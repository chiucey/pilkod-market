#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Document Pro 测试用例
"""

import unittest
import sys
import os
import tempfile
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from main import (
    clean_text, split_paragraphs, extract_keywords,
    extract_title, generate_summary, detect_document_type,
    parse_txt, run
)


class TestDocumentPro(unittest.TestCase):
    """Document Pro 核心功能测试"""

    def test_clean_text(self):
        """测试文本清洗功能"""
        text = "  这是  测试  \n\n 文本  "
        result = clean_text(text)
        self.assertEqual(result, "这是 测试 文本")

    def test_clean_text_empty(self):
        """测试空文本处理"""
        result = clean_text("")
        self.assertEqual(result, "")

    def test_split_paragraphs(self):
        """测试智能分段"""
        text = "第一段内容。\n\n第二段较长内容，这里会继续扩展以满足分段阈值。"
        paras = split_paragraphs(text)
        self.assertGreaterEqual(len(paras), 1)

    def test_split_paragraphs_empty(self):
        """测试空文本分段"""
        paras = split_paragraphs("")
        self.assertEqual(paras, [])

    def test_extract_keywords_chinese(self):
        """测试中文关键词提取"""
        text = "人工智能 大模型 文档处理 智能总结 关键词提取 人工智能技术"
        keywords = extract_keywords(text)
        self.assertIn("人工智能", keywords)
        self.assertIn("文档处理", keywords)

    def test_extract_keywords_english(self):
        """测试英文关键词提取"""
        text = "Document processing is a key technology. Document analysis is important."
        keywords = extract_keywords(text)
        self.assertIn("document", keywords)

    def test_extract_title(self):
        """测试标题提取"""
        text = "这是文档标题\n\n这是正文内容"
        title = extract_title(text)
        self.assertEqual(title, "这是文档标题")

    def test_extract_title_empty(self):
        """测试空文档标题"""
        title = extract_title("")
        self.assertEqual(title, "未识别标题")

    def test_generate_summary(self):
        """测试摘要生成"""
        paragraphs = ["第一段内容。", "第二段内容。", "第三段内容。"]
        summary = generate_summary(paragraphs, max_length=50)
        self.assertIsInstance(summary, str)
        self.assertLessEqual(len(summary), 55)  # 包含省略号

    def test_generate_summary_empty(self):
        """测试空摘要生成"""
        summary = generate_summary([], max_length=100)
        self.assertEqual(summary, "")

    def test_detect_document_type(self):
        """测试文档类型检测"""
        self.assertEqual(detect_document_type("test.pdf"), "pdf")
        self.assertEqual(detect_document_type("test.docx"), "docx")
        self.assertEqual(detect_document_type("test.pptx"), "pptx")
        self.assertEqual(detect_document_type("test.txt"), "txt")
        self.assertEqual(detect_document_type("test.md"), "markdown")
        self.assertEqual(detect_document_type("test.xyz"), "unknown")

    def test_run_with_content(self):
        """测试内容输入处理"""
        res = run({
            "content": "这是一篇测试文档，用于验证Document Pro处理能力。文档包含一些关键信息和重要内容。",
            "mode": "summary"
        })
        self.assertEqual(res["status"], "success")
        self.assertIn("summary", res["data"])
        self.assertIn("keywords", res["data"])

    def test_run_empty_content(self):
        """测试空内容处理"""
        res = run({"content": ""})
        self.assertEqual(res["status"], "error")

    def test_run_no_input(self):
        """测试无输入处理"""
        res = run({})
        self.assertEqual(res["status"], "error")

    def test_run_file_not_exist(self):
        """测试文件不存在"""
        res = run({"file_path": "/nonexistent/file.pdf"})
        self.assertEqual(res["status"], "error")

    def test_run_extract_mode(self):
        """测试提取模式"""
        res = run({
            "content": "人工智能技术发展迅速，机器学习和深度学习是核心技术。",
            "mode": "extract"
        })
        self.assertEqual(res["status"], "success")
        self.assertIn("keywords", res["data"])
        self.assertIn("paragraphs", res["data"])

    def test_run_full_mode(self):
        """测试完整模式"""
        res = run({
            "content": "文档处理是重要功能。",
            "mode": "full"
        })
        self.assertEqual(res["status"], "success")
        data = res["data"]
        self.assertIn("summary", data)
        self.assertIn("keywords", data)
        self.assertIn("paragraphs", data)
        self.assertIn("title", data)


class TestTextFileProcessing(unittest.TestCase):
    """文本文件处理测试"""

    def test_parse_txt_utf8(self):
        """测试 UTF-8 文本解析"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("测试内容\n第二行内容")
            temp_path = f.name

        try:
            result = parse_txt(temp_path)
            self.assertTrue(result['success'])
            self.assertIn("测试内容", result['text'])
        finally:
            os.unlink(temp_path)

    def test_parse_txt_with_chinese(self):
        """测试中文文本解析"""
        content = "这是中文内容\n包含多行文字"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name

        try:
            result = parse_txt(temp_path)
            self.assertTrue(result['success'])
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
