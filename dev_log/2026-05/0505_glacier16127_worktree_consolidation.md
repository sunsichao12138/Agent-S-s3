# Worktree 合并与开发基线重建 — 2026-05-05

作者：glacier16127

## 背景

此前因跨仓库同步需求，同时维护了两个 git worktree：
- `Agent-S-s3-master`（主工作树，`feat/reflection-optimize`）
- `Agent-S-s3-master-sync`（关联工作树，`feat/docs-integration`）

两个仓库 git 历史独立（无共同祖先），导致分支管理碎片化。本次合并确定以 sync 侧为唯一开发基线，清理 worktree 结构，建立统一开发分支。

---

## 变更清单

| 文件 / 操作 | 说明 |
|-------------|------|
| `git worktree list` | 确认两个 worktree：s3-master（主树） + s3-master-sync（关联树） |
| `git merge-base` | 验证两个分支无共同祖先，确认历史独立 |
| `git worktree remove` | 尝试移除主工作树失败（不适用于 main working tree） |
| `git checkout -b feat/TrackA-B ec895ea` | 从 sync 侧最新提交建立新开发分支 |
| `dev_log/2026-05/0505_glacier16127_worktree_consolidation.md` | 本日志 |
| `dev_log/INDEX.md` | 更新索引 |

---

## 关键决策

### 1. 以 Agent-S-s3-master-sync 为唯一开发基线
**决策**：保留 sync worktree 作为唯一活跃开发目录，放弃非 sync 侧。
**理由**：sync 侧 (`feat/docs-integration`) 包含 24 个提交，覆盖 launcher、grounding、reasoning、Windows 飞书支持等完整功能链；非 sync 侧仅 10 个提交且以文档为主。sync 侧是目标仓库，功能更完整。

### 2. 新切分支而非沿用 feat/docs-integration
**决策**：从 `ec895ea` 切出 `feat/TrackA-B` 作为长期开发分支，`feat/docs-integration` 保留为历史快照。
**理由**：`feat/docs-integration` 的职责是跨仓库迁移，任务已结束。新功能开发应从干净基线开始，避免分支名语义误导。

### 3. 主工作树不强行删除
**决策**：主工作树 `Agent-S-s3-master` 无法通过 `git worktree remove` 删除，保留目录不动。
**理由**：Git 限制 main working tree 不可通过 worktree 子命令移除。手动删除目录不会影响 sync 侧开发，无阻塞风险。

---

## 验证

- [x] `feat/TrackA-B` 分支创建成功，HEAD 指向 `ec895ea`
- [x] `git worktree list` 确认 sync worktree 分支已切换为 `feat/TrackA-B`
- [x] 旧分支 `feat/docs-integration`、`feat/reflection-optimize` 均保留可回溯

---

## 风险 & 后续

- 非 sync 侧 `feat/reflection-optimize` 的 reflection frequency control 逻辑尚未迁移到 sync 侧，需后续 cherry-pick
- 两个仓库历史无法 merge（无共同祖先），任何跨仓库代码合并都只能通过 cherry-pick 或手动移植
- 后续开发均在 `feat/TrackA-B` 上进行
