import unittest

from gui_agents.feishu.testcases.nl_parser import parse_instruction


class TestNLParser(unittest.TestCase):
    def test_parse_send_message_instruction(self) -> None:
        testcase = parse_instruction('在"测试群"发送"Hello World"并验证发送成功')

        self.assertEqual(testcase["product"], "im")
        self.assertEqual(testcase["steps"][0]["action"], "open_chat")
        self.assertEqual(testcase["steps"][0]["target"], "测试群")
        self.assertEqual(
            testcase["steps"][1]["payload"],
            {"text": "Hello World"},
        )
        self.assertEqual(testcase["steps"][2]["action"], "send_message")
        self.assertIn("message_sent", testcase["assertions"])

    def test_parse_empty_instruction_raises_value_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "instruction cannot be empty"):
            parse_instruction("   ")


if __name__ == "__main__":
    unittest.main()
