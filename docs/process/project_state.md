# Project State

Last updated: 2026-05-05

## Goal

Build a Windows-first, Feishu desktop GUI agent on top of `Agent-S`, with the current milestone biased toward a stable `vision-first` baseline instead of a UIA-first rollout.

## Current baseline

The default runtime entry currently checked is:

```python
from gui_agents.s3.agents.grounding import OSWorldACI
```

Source of truth:

- `gui_agents/s3/cli_app.py`
- `gui_agents/s3/agents/grounding.py`

Current baseline implications:

- Default runtime path is `vision-first`
- Default runtime path does not assume `WindowsFeishuACI`
- Default runtime path does not assume Feishu-specific UIA helpers are available
- Accessibility / UIA routes are not part of the default execution chain for the current milestone

## Feishu-specific compatibility code

The repository still contains a Feishu / Windows compatibility branch:

- `gui_agents/s3/agents/grounding_feishu.py`
- `gui_agents/s3/agents/_feishu_exec.py`

These files provide optional helper methods such as:

- `feishu_focus()`
- `feishu_click(...)`
- `feishu_type(...)`
- `feishu_doc_click(...)`
- `feishu_doc_type(...)`

Current status:

- This branch is retained in-repo
- This branch is not the default entry contract
- It only becomes active if an entrypoint explicitly imports `WindowsFeishuACI as OSWorldACI`
- Documentation must not describe it as already wired into the stock CLI unless that import has been restored in the entrypoint

## Locator status

Current milestone status:

- `VisionLocator`: current default route
- `AccessibilityLocator`: contract placeholder only
- `HybridLocator`: contract placeholder only

Reason:

- Windows + Feishu desktop + browser mixed interactions still carry compatibility risk on accessibility/UIA-heavy paths
- The current priority is to keep the default chain runnable before re-enabling alternate locator paths

## Documentation alignment

As of 2026-05-05, the intended documentation position is:

- `spec` and `interfaces` may keep Accessibility / Hybrid as future interfaces
- `process` documents must clearly distinguish default runtime path from optional compatibility branches
- `interface_compatibility.md` must not claim that `cli_app.py` already auto-switches to `WindowsFeishuACI`

## Known drift to resolve separately

The codebase still has a drift between runtime prompt guidance and default entry wiring:

- `gui_agents/s3/memory/procedural_memory.py` still contains Feishu-specific helper guidance
- The default `cli_app.py` entry does not currently guarantee those helper methods exist

This should be handled in a dedicated follow-up track:

1. Either restore the Feishu-specific runtime path end-to-end
2. Or remove / downgrade the prompt instructions that assume `feishu_*` methods

Until then, treat `procedural_memory.py` guidance about `feishu_*` methods as ahead of the default runtime wiring.

## Historical material

Detailed session-level notes, bug timelines, and one-off validation evidence should be read from:

- `docs/archive/feishu_decisions_log.md`
- `docs/archive/feishu_test_log_2026-05-03.md`

They are historical evidence, not the current default runtime contract.
