import unittest

from gui_agents.feishu.planner.task_planner import plan_testcase
from gui_agents.feishu.testcases.scenario_schema import build_testcase


class TestTaskPlanner(unittest.TestCase):
    def test_plan_supported_send_message_workflow(self) -> None:
        testcase = build_testcase(
            product="im",
            title="在测试群发送消息并验证发送成功",
            steps=[
                {
                    "action": "open_chat",
                    "target": "测试群",
                    "assertion": "chat_title_matched",
                },
                {
                    "action": "type_message",
                    "target": "message_input",
                    "payload": {"text": "Hello World"},
                    "assertion": "message_input_contains_text",
                },
                {
                    "action": "send_message",
                    "target": "send_button",
                    "assertion": "message_sent",
                },
            ],
        )

        plan = plan_testcase(testcase)

        self.assertEqual(plan["workflow"], "send_message")
        self.assertEqual(plan["workflow_params"]["chat_name"], "测试群")
        self.assertEqual(plan["workflow_params"]["message_text"], "Hello World")
        self.assertEqual(plan["entry_assertions"], ["chat_title_matched"])
        self.assertEqual(plan["preconditions"], ["飞书桌面端已登录"])
        self.assertIsNone(plan["failure_type"])
        self.assertIsNone(plan["failure_reason"])
        self.assertNotIn("fallback", plan)

    def test_plan_returns_structured_failure_for_unsupported_steps(self) -> None:
        testcase = build_testcase(
            product="im",
            title="在测试群只打开聊天窗口",
            steps=[
                {"action": "open_chat", "target": "测试群"},
            ],
            assertions=["chat_title_matched"],
        )

        plan = plan_testcase(testcase)

        self.assertIsNone(plan["workflow"])
        self.assertEqual(plan["failure_type"], "precondition")
        self.assertIn("no supported workflow", plan["failure_reason"])
        self.assertEqual(plan["preconditions"], ["飞书桌面端已登录"])


if __name__ == "__main__":
    unittest.main()
