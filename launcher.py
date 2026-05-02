import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import threading
import pyautogui
import queue
import sys
import os
import re
import json

ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m')

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
CLI_APP = os.path.join(PROJECT_DIR, "gui_agents", "s3", "cli_app.py")
CONFIG_FILE = os.path.join(PROJECT_DIR, "config.json")

DEFAULT_CONFIG = {
    "model_api_key":  "",
    "model_id":       "",
    "model_url":      "https://ark.cn-beijing.volces.com/api/v3",
    "ground_api_key": "",
    "ground_model":   "bytedance/ui-tars-1.5-7b",
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            return {**DEFAULT_CONFIG, **saved}
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(cfg: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


class Launcher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Agent S 启动器")
        self.root.resizable(True, True)
        self.process = None
        self.output_queue = queue.Queue()
        self.agent_ready = False
        self.cfg = load_config()

        self._build_ui()
        self._auto_detect_resolution()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ─── UI ───────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # ── 顶部：配置区 ──
        cfg = ttk.LabelFrame(self.root, text="配置", padding=8)
        cfg.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        cfg.columnconfigure(1, weight=1)

        # 主模型
        ttk.Label(cfg, text="豆包 API Key").grid(row=0, column=0, sticky="w", pady=2)
        self.v_model_key = tk.StringVar(value=self.cfg["model_api_key"])
        ttk.Entry(cfg, textvariable=self.v_model_key, show="*", width=50).grid(row=0, column=1, sticky="ew", padx=(8, 0))

        ttk.Label(cfg, text="豆包 Endpoint ID").grid(row=1, column=0, sticky="w", pady=2)
        self.v_model_id = tk.StringVar(value=self.cfg["model_id"])
        ttk.Entry(cfg, textvariable=self.v_model_id, width=50).grid(row=1, column=1, sticky="ew", padx=(8, 0))

        # 定位模型
        ttk.Label(cfg, text="OpenRouter API Key").grid(row=2, column=0, sticky="w", pady=2)
        self.v_ground_key = tk.StringVar(value=self.cfg["ground_api_key"])
        ttk.Entry(cfg, textvariable=self.v_ground_key, show="*", width=50).grid(row=2, column=1, sticky="ew", padx=(8, 0))

        # 分辨率
        ttk.Label(cfg, text="定位分辨率").grid(row=3, column=0, sticky="w", pady=2)
        res_frame = ttk.Frame(cfg)
        res_frame.grid(row=3, column=1, sticky="w", padx=(8, 0))
        self.v_gw = tk.StringVar()
        self.v_gh = tk.StringVar()
        ttk.Entry(res_frame, textvariable=self.v_gw, width=6).pack(side="left")
        ttk.Label(res_frame, text=" x ").pack(side="left")
        ttk.Entry(res_frame, textvariable=self.v_gh, width=6).pack(side="left")
        self.v_screen_info = tk.StringVar()
        ttk.Label(res_frame, textvariable=self.v_screen_info, foreground="gray").pack(side="left", padx=(10, 0))

        # 启动按钮
        btn_frame = ttk.Frame(cfg)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(8, 0))
        self.btn_start = ttk.Button(btn_frame, text="▶  启动 Agent", command=self._start_agent, width=20)
        self.btn_start.pack(side="left", padx=4)
        self.btn_stop = ttk.Button(btn_frame, text="■  停止", command=self._stop_agent, width=10, state="disabled")
        self.btn_stop.pack(side="left", padx=4)
        ttk.Button(btn_frame, text="💾 保存配置", command=self._save_config, width=12).pack(side="left", padx=4)
        self.v_status = tk.StringVar(value="未启动")
        ttk.Label(btn_frame, textvariable=self.v_status, foreground="gray").pack(side="left", padx=12)

        # ── 中部：日志区 ──
        log_frame = ttk.LabelFrame(self.root, text="运行日志", padding=4)
        log_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=8)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log = scrolledtext.ScrolledText(log_frame, wrap="word", height=18,
                                             font=("Consolas", 9), state="disabled",
                                             bg="#1e1e1e", fg="#d4d4d4",
                                             insertbackground="white")
        self.log.grid(row=0, column=0, sticky="nsew")

        # 颜色标签
        self.log.tag_config("info",    foreground="#9cdcfe")
        self.log.tag_config("action",  foreground="#4ec9b0")
        self.log.tag_config("warn",    foreground="#ce9178")
        self.log.tag_config("query",   foreground="#dcdcaa")
        self.log.tag_config("success", foreground="#6a9955")
        self.log.tag_config("normal",  foreground="#d4d4d4")

        # ── 底部：指令输入区 ──
        input_frame = ttk.LabelFrame(self.root, text="任务指令", padding=6)
        input_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)

        self.v_query = tk.StringVar()
        self.entry_query = ttk.Entry(input_frame, textvariable=self.v_query, font=("Microsoft YaHei", 11))
        self.entry_query.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.entry_query.bind("<Return>", lambda e: self._send_query())
        self.entry_query.configure(state="disabled")

        self.btn_send = ttk.Button(input_frame, text="发送", command=self._send_query, width=10, state="disabled")
        self.btn_send.grid(row=0, column=1)

        # 最小尺寸
        self.root.update_idletasks()
        self.root.minsize(640, 560)

    # ─── 分辨率自动检测 ───────────────────────────────────────────────────────

    def _auto_detect_resolution(self):
        sw, sh = pyautogui.size()
        max_dim = 1920
        scale = min(max_dim / sw, max_dim / sh, 1.0)
        gw = int(sw * scale)
        gh = int(sh * scale)
        self.v_gw.set(str(gw))
        self.v_gh.set(str(gh))
        self.v_screen_info.set(f"（屏幕 {sw}×{sh}，自动缩放）")

    # ─── 启动 / 停止 ──────────────────────────────────────────────────────────

    def _start_agent(self):
        if self.process and self.process.poll() is None:
            return

        self.agent_ready = False
        self._log("正在启动 Agent S...\n", "info")

        env = os.environ.copy()
        env["PYTHONPATH"] = PROJECT_DIR
        env["PYTHONIOENCODING"] = "utf-8"

        cmd = [
            sys.executable, CLI_APP,
            "--provider", "openai",
            "--model", self.v_model_id.get().strip(),
            "--model_url", DEFAULT_CONFIG["model_url"],
            "--model_api_key", self.v_model_key.get().strip(),
            "--ground_provider", "open_router",
            "--ground_url", "https://openrouter.ai/api/v1",
            "--ground_api_key", self.v_ground_key.get().strip(),
            "--ground_model", DEFAULT_CONFIG["ground_model"],
            "--grounding_width", self.v_gw.get().strip(),
            "--grounding_height", self.v_gh.get().strip(),
        ]

        self.process = subprocess.Popen(
            cmd, env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace",
            bufsize=1,
        )

        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.v_status.set("运行中...")

        threading.Thread(target=self._read_output, daemon=True).start()
        self.root.after(100, self._poll_output)

    def _stop_agent(self):
        if self.process:
            try:
                self.process.terminate()
            except Exception:
                pass
        self._set_stopped()

    def _set_stopped(self):
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.btn_send.configure(state="disabled")
        self.entry_query.configure(state="disabled")
        self.v_status.set("已停止")
        self._log("\n─── Agent 已停止 ───\n", "warn")

    # ─── 输出读取 ─────────────────────────────────────────────────────────────

    def _read_output(self):
        buf = ""
        while True:
            ch = self.process.stdout.read(1)
            if not ch:
                if buf:
                    self.output_queue.put(buf)
                self.output_queue.put(None)
                break
            buf += ch
            # 遇到换行或出现 "Query: " 提示时推送
            if ch == "\n" or buf.endswith("Query: ") or buf.endswith("(y/n): "):
                self.output_queue.put(buf)
                buf = ""

    def _poll_output(self):
        try:
            while True:
                line = self.output_queue.get_nowait()
                if line is None:
                    self._set_stopped()
                    return
                self._handle_line(line)
        except queue.Empty:
            pass
        self.root.after(100, self._poll_output)

    def _handle_line(self, line: str):
        line = ANSI_ESCAPE.sub("", line)
        line_strip = line.strip()

        # 识别 "Query:" 提示，激活输入框
        if line_strip.startswith("Query:"):
            if not self.agent_ready:
                self.agent_ready = True
                self._log("✅ Agent 就绪，请在下方输入任务\n", "success")
                self.btn_send.configure(state="normal")
                self.entry_query.configure(state="normal")
                self.entry_query.focus()
            return

        # 自动回复"继续查询"提示
        if "Would you like to provide another query" in line:
            self._write_stdin("y\n")
            return

        # 着色
        if "PLAN:" in line or "Step" in line:
            tag = "action"
        elif "ERROR" in line or "Error" in line or "Traceback" in line:
            tag = "warn"
        elif "REFLECTION" in line or "Response success" in line:
            tag = "info"
        elif "EXECUTING CODE" in line:
            tag = "query"
        else:
            tag = "normal"

        self._log(line, tag)

    # ─── 发送指令 ─────────────────────────────────────────────────────────────

    def _send_query(self):
        query = self.v_query.get().strip()
        if not query or not self.agent_ready:
            return
        self._log(f"\n▶ 指令：{query}\n", "query")
        self._write_stdin(query + "\n")
        self.v_query.set("")
        self.btn_send.configure(state="disabled")
        self.entry_query.configure(state="disabled")
        self.agent_ready = False

    def _write_stdin(self, text: str):
        if self.process and self.process.poll() is None:
            try:
                self.process.stdin.write(text)
                self.process.stdin.flush()
            except Exception:
                pass

    # ─── 日志写入 ─────────────────────────────────────────────────────────────

    def _log(self, text: str, tag: str = "normal"):
        self.log.configure(state="normal")
        self.log.insert("end", text, tag)
        self.log.see("end")
        self.log.configure(state="disabled")

    # ─── 关闭 ─────────────────────────────────────────────────────────────────

    def _save_config(self):
        save_config({
            "model_api_key":  self.v_model_key.get().strip(),
            "model_id":       self.v_model_id.get().strip(),
            "model_url":      DEFAULT_CONFIG["model_url"],
            "ground_api_key": self.v_ground_key.get().strip(),
            "ground_model":   DEFAULT_CONFIG["ground_model"],
        })
        self.v_status.set("配置已保存 ✓")

    def _on_close(self):
        self._stop_agent()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    Launcher().run()
