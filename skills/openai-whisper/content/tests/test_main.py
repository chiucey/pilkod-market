import unittest
import sys
import os

# 将 src 目录加入 Python 路径，适配 Minimax 运行环境
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from main import run


class TestWhisperSkill(unittest.TestCase):
    """Whisper 技能单元测试用例"""

    def test_missing_audio_path(self):
        """测试未传入音频路径的场景"""
        result = run({})
        self.assertEqual(result["status"], "error")
        self.assertIn("请提供音频文件的完整路径", result["message_for_user"])

    def test_nonexistent_audio_file(self):
        """测试音频文件不存在的场景"""
        test_input = {"audio_path": "/nonexistent/test_audio.mp3"}
        result = run(test_input)
        self.assertEqual(result["status"], "error")
        self.assertIn("音频文件不存在", result["message_for_user"])

    def test_invalid_audio_path_is_dir(self):
        """测试传入的路径是文件夹而非文件的场景"""
        test_input = {"audio_path": os.path.dirname(__file__)}
        result = run(test_input)
        self.assertEqual(result["status"], "error")
        self.assertIn("不是一个有效的文件", result["message_for_user"])


if __name__ == "__main__":
    unittest.main()
