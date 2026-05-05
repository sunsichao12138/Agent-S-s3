"""Explicit workflow selection for Track A supported scenarios."""

from __future__ import annotations

from gui_agents.feishu.contracts import FeishuState, TestCase, WorkflowPlan


def _failure_plan(reason: str) -> WorkflowPlan:
    return WorkflowPlan(
        workflow=None,
        reason=reason,
        workflow_params={},
        entry_assertions=[],
        preconditions=[],
        failure_type="precondition",
        failure_reason=reason,
    )


def select_workflow(
    testcase: TestCase, state: FeishuState | None = None
) -> WorkflowPlan:
    steps = testcase.get("steps", [])
    actions = [step["action"] for step in steps]

    if testcase["product"] == "im" and actions == [
        "open_chat",
        "type_message",
        "send_message",
    ]:
        chat_name = steps[0].get("target")
        payload = steps[1].get("payload") or {}
        message_text = payload.get("text")

        if not chat_name or not message_text:
            return _failure_plan(
                "send_message workflow requires chat_name and message_text"
            )

        return WorkflowPlan(
            workflow="send_message",
            reason="matched product=im and action intent=send_message",
            workflow_params={
                "chat_name": chat_name,
                "message_text": message_text,
            },
            entry_assertions=["chat_title_matched"],
            preconditions=[],
            failure_type=None,
            failure_reason=None,
        )

    return _failure_plan("no supported workflow matched testcase steps")

