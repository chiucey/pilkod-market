#!/usr/bin/env python3
"""
测试验证脚本和打包脚本
"""

import sys
import os
import unittest

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from verify_website import verify_website, extract_domain, check_domain_suspicious


class TestVerifyWebsite(unittest.TestCase):
    """测试网站验证功能"""

    def test_extract_domain(self):
        """测试域名提取"""
        test_cases = [
            ("https://nodejs.org", "nodejs.org"),
            ("https://www.python.org/downloads/", "www.python.org"),
            ("http://example.com/path", "example.com"),
            ("not-a-url", None),
        ]

        for url, expected in test_cases:
            result = extract_domain(url)
            self.assertEqual(result, expected, f"URL: {url}")

    def test_check_domain_suspicious(self):
        """测试可疑域名检测"""
        suspicious_domains = [
            "software-download.com",
            "app-free.net",
            "nodejs.tk",
            "python.ml",
        ]

        for domain in suspicious_domains:
            is_suspicious, reason = check_domain_suspicious(domain)
            self.assertTrue(is_suspicious, f"域名应被标记为可疑: {domain}")

    def test_verify_official_website(self):
        """测试官方域名验证"""
        # 高可信度官方域名
        result = verify_website("https://nodejs.org", "nodejs")
        self.assertTrue(result['is_official'])
        self.assertGreater(result['confidence'], 60)
        self.assertTrue(any('HTTPS' in r for r in result['reasons']))

    def test_verify_suspicious_website(self):
        """测试可疑域名验证"""
        result = verify_website("https://nodejs-download.tk", "nodejs")
        self.assertFalse(result['is_official'])
        self.assertLess(result['confidence'], 50)
        self.assertTrue(len(result['warnings']) > 0)


class TestPackageScript(unittest.TestCase):
    """测试打包脚本结构验证"""

    def test_meta_json_structure(self):
        """测试 _meta.json 结构"""
        meta_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '_meta.json')
        if os.path.exists(meta_path):
            import json
            with open(meta_path, 'r') as f:
                meta = json.load(f)
            self.assertIn('id', meta)
            self.assertIn('version', meta)


if __name__ == '__main__':
    print("运行测试...")
    unittest.main(verbosity=2)
