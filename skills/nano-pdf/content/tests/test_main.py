import unittest
import sys
import os
import tempfile
from pathlib import Path

# 导入主模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from main import run, NanoPDF


class TestNanoPDF(unittest.TestCase):
    def setUp(self):
        """创建临时测试文件"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_pdf = os.path.join(self.temp_dir, "test.pdf")

        # 创建空白测试PDF
        from pypdf import PdfWriter
        writer = PdfWriter()
        writer.add_blank_page(width=595, height=842)
        with open(self.test_pdf, "wb") as f:
            writer.write(f)

    def tearDown(self):
        """清理临时文件"""
        if os.path.exists(self.test_pdf):
            os.remove(self.test_pdf)
        os.rmdir(self.temp_dir)

    def test_extract_metadata(self):
        """测试元数据提取"""
        res = run({
            "action": "metadata",
            "file_path": self.test_pdf
        })
        self.assertEqual(res["status"], "success")
        self.assertIn("metadata", res["data"])

    def test_extract_text(self):
        """测试文本提取"""
        res = run({
            "action": "text",
            "file_path": self.test_pdf
        })
        self.assertEqual(res["status"], "success")

    def test_extract_pages(self):
        """测试页面提取"""
        out = os.path.join(self.temp_dir, "extracted.pdf")
        res = run({
            "action": "extract_pages",
            "file_path": self.test_pdf,
            "output_path": out,
            "start_page": 1
        })
        self.assertEqual(res["status"], "success")
        if os.path.exists(out):
            os.remove(out)

    def test_invalid_action(self):
        """测试无效操作"""
        res = run({"action": "invalid"})
        self.assertEqual(res["status"], "error")


if __name__ == "__main__":
    unittest.main()
