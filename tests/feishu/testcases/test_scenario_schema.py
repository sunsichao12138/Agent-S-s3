import unittest

from gui_agents.feishu.testcases.scenario_schema import (
    build_testcase,
    validate_testcase,
)


class TestScenarioSchema(unittest.TestCase):
    def test_build_testcase_normalizes_step_ids_and_defaults(self) -> None:
        testcase = build_testcase(
            product="im",
            title="在测试群发送消息并验证发送成功",
            steps=[
                {"action": "open_chat", "target": "测试群"},
                {"action": "type_message", "payload": {"text": "你好"}},
                {"action": "send_message"},
            ],
        )

        self.assertEqual(testcase["steps"][0]["step_id"], "step_1")
        self.assertEqual(testcase["steps"][1]["step_id"], "step_2")
        self.assertEqual(testcase["preconditions"], ["飞书桌面端已登录"])
        self.assertIn("message_sent", testcase["assertions"])

    def test_build_testcase_rejects_unknown_action(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid action"):
            build_testcase(
                product="im",
                title="在测试群发送消息并验证发送成功",
                steps=[
                    {"action": "open_chat", "target": "测试群"},
                    {"action": "send_mesage"},
                ],
            )

    def test_build_testcase_rejects_empty_steps(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least one step"):
            build_testcase(
                product="im",
                title="空步骤用例",
                steps=[],
            )

    def test_validate_testcase_rejects_empty_steps(self) -> None:
        testcase = {
            "id": "tc_im_empty",
            "product": "im",
            "title": "空步骤用例",
            "preconditions": ["飞书桌面端已登录"],
            "steps": [],
            "assertions": [],
        }

        with self.assertRaisesRegex(ValueError, "at least one step"):
            validate_testcase(testcase)


if __name__ == "__main__":
    unittest.main()
