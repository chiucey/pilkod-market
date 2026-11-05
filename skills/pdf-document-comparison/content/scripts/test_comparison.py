#!/usr/bin/env python3
"""
校对脚本测试套件
"""

import unittest
import sys
import os

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from compare_documents import (
    normalize_text,
    is_numeric_difference,
    detect_digit_error,
    DocumentComparator,
    generate_markdown_report
)


class TestNormalizeText(unittest.TestCase):
    """测试文本规范化"""

    def test_remove_multiple_spaces(self):
        """测试移除多余空格"""
        text = "这   是   一个   测试"
        result = normalize_text(text)
        self.assertEqual(result, "这 是 一个 测试")

    def test_normalize_line_breaks(self):
        """测试规范化换行符"""
        text = "第一行\r\n第二行\r第三行\n第四行"
        result = normalize_text(text)
        self.assertNotIn('\r', result)

    def test_normalize_quotes(self):
        """测试规范化引号"""
        text = '他说"你好"'
        result = normalize_text(text)
        self.assertIn('"', result)


class TestNumericDetection(unittest.TestCase):
    """测试数字差异检测"""

    def test_detect_different_numbers(self):
        """测试检测不同数字"""
        self.assertTrue(is_numeric_difference("123", "456"))
        self.assertTrue(is_numeric_difference("12.34", "12.35"))

    def test_detect_same_numbers(self):
        """测试相同数字"""
        self.assertFalse(is_numeric_difference("123", "123"))
        self.assertFalse(is_numeric_difference("12.34", "12.34"))


class TestDigitError(unittest.TestCase):
    """测试小数点错误检测"""

    def test_decimal_point_error(self):
        """测试小数点位置错误"""
        self.assertTrue(detect_digit_error("1.234", "12.34"))
        self.assertTrue(detect_digit_error("100.00", "1000.00"))


class TestDocumentComparator(unittest.TestCase):
    """测试文档比对器"""

    def setUp(self):
        self.comparator = DocumentComparator(chunk_size=500)

    def test_identical_texts(self):
        """测试完全相同的文本"""
        text = "这是完全相同的内容。"
        diffs, identical = self.comparator.compare_texts(text, text)
        self.assertEqual(len(diffs), 0)

    def test_text_difference(self):
        """测试文字差异"""
        original = "这是原文内容"
        parsed = "这是解析后内容"
        diffs, identical = self.comparator.compare_texts(original, parsed)
        self.assertGreater(len(diffs), 0)

    def test_missing_content(self):
        """测试遗漏内容"""
        original = "第一段\n\n第二段\n\n第三段"
        parsed = "第一段\n\n第三段"
        diffs, identical = self.comparator.compare_texts(original, parsed)
        # 应该检测到遗漏
        self.assertGreater(len(diffs), 0)

    def test_extra_content(self):
        """测试多余内容"""
        original = "第一段\n\n第三段"
        parsed = "第一段\n\n第二段\n\n第三段"
        diffs, identical = self.comparator.compare_texts(original, parsed)
        # 应该检测到多余
        self.assertGreater(len(diffs), 0)

    def test_large_text_chunking(self):
        """测试大文本分块"""
        # 创建一个超过分块大小的文本
        text = "段落内容。" * 200  # 约2400字符
        chunks = self.comparator.chunk_text(text)
        self.assertGreater(len(chunks), 1)


class TestReportGeneration(unittest.TestCase):
    """测试报告生成"""

    def test_report_with_differences(self):
        """测试有差异的报告"""
        differences = [
            {
                'type': '文字错误',
                'position': '第1页',
                'original': '原文',
                'parsed': '解析',
                'description': '字符差异'
            }
        ]
        report = generate_markdown_report(differences, ['无差异段落'])
        self.assertIn('差异详情', report)
        self.assertIn('文字错误', report)

    def test_report_without_differences(self):
        """测试无差异的报告"""
        report = generate_markdown_report([], ['无差异段落'])
        self.assertIn('无差异', report)


def run_tests():
    """运行所有测试"""
    unittest.main(module=__name__, verbosity=2, exit=False)


if __name__ == "__main__":
    run_tests()
