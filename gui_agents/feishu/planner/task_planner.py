"""Track A planner wrapper that normalizes workflow selection output."""

from __future__ import annotations

from gui_agents.feishu.contracts import FeishuState, TestCase, WorkflowPlan
from gui_agents.feishu.testcases.scenario_schema import validate_testcase
from .workflow_selector import select_workflow


def plan_testcase(testcase: TestCase, state: FeishuState | None = None) -> WorkflowPlan:
    validate_testcase(testcase)
    plan = select_workflow(testcase, state=state)
    plan["preconditions"] = list(testcase.get("preconditions", []))
    return plan
