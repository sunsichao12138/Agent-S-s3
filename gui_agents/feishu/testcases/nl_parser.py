"""Rule-based parser for natural-language Feishu test instructions."""

from __future__ import annotations

import re

from gui_agents.feishu.contracts import TestCase
from gui_agents.feishu.testcases.scenario_schema import build_testcase


QUOTED_TEXT_PATTERN = re.compile(r"""["'“”‘’]([^"'“”‘’]+)["'“”‘’]""")


def _extract_quoted_texts(instruction: str) -> list[str]:
    return [match.strip() for match in QUOTED_TEXT_PATTERN.findall(instruction)]


def _detect_product(instruction: str) -> str:
    # Current milestone supports IM only; Docs/Calendar will be added later.
    return "im"


def _extract_chat_name(instruction: str, quoted_texts: list[str]) -> str:
    if len(quoted_texts) >= 2:
        return quoted_texts[0]

    # Current milestone supports a single chat target only. Expressions such as
    # "在测试群和产品群发送消息" are not disambiguated yet and will need a richer
    # parser once multi-target workflows are introduced.
    match = re.search(r"(?:在|向|给)(.+?)(?:发送|发|回复)", instruction)
    if match:
        return match.group(1).strip(" 的里中到给向在")

    return "测试群"


def _extract_message_text(instruction: str, quoted_texts: list[str]) -> str:
    if len(quoted_texts) >= 2:
        return quoted_texts[1]

    if len(quoted_texts) == 1 and any(
        keyword in instruction for keyword in ("发送", "发消息", "回复")
    ):
        return quoted_texts[0]

    match = re.search(r"(?:发送|回复|发)(.+?)(?:并|，|。|$)", instruction)
    if match:
        return match.group(1).strip("消息内容为:： ")

    return "Hello World"


def parse_instruction(instruction: str) -> TestCase:
    normalized = instruction.strip()
    if not normalized:
        raise ValueError("instruction cannot be empty")

    product = _detect_product(normalized)
    quoted_texts = _extract_quoted_texts(normalized)
    chat_name = _extract_chat_name(normalized, quoted_texts)
    message_text = _extract_message_text(normalized, quoted_texts)

    title = f"在{chat_name}发送消息并验证发送成功"

    return build_testcase(
        product=product,
        title=title,
        steps=[
            {
                "action": "open_chat",
                "target": chat_name,
                "payload": None,
                "assertion": "chat_title_matched",
            },
            {
                "action": "type_message",
                "target": "message_input",
                "payload": {"text": message_text},
                "assertion": "message_input_contains_text",
            },
            {
                "action": "send_message",
                "target": "send_button",
                "payload": None,
                "assertion": "message_sent",
            },
        ],
    )
