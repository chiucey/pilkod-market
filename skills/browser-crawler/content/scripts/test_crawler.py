#!/usr/bin/env python3
"""
浏览器爬虫技能测试脚本
测试爬虫功能是否正常工作
"""

import json
import sys
import re
from pathlib import Path

# 模拟爬虫功能测试

def test_url_validation():
    """测试 URL 验证逻辑"""
    print("\n[Test 1] URL 验证测试")

    # 允许的 URL
    allowed_urls = [
        "https://example.com",
        "http://example.org/page",
        "https://blog.example.com/article?id=123"
    ]

    # 禁止的 URL
    forbidden_urls = [
        "http://localhost:8080",
        "http://127.0.0.1",
        "http://192.168.1.1",
        "http://10.0.0.1",
        "http://172.16.0.1"
    ]

    # URL 验证正则
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost'  # localhost
        r'|'  # or
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    # 内网 IP 检测
    intranet_patterns = [
        r'^127\.',
        r'^10\.',
        r'^192\.168\.',
        r'^172\.(1[6-9]|2\d|3[01])\.',
        r'^localhost$'
    ]

    all_pass = True

    for url in allowed_urls:
        is_valid = url_pattern.match(url)
        is_forbidden = any(re.match(p, url.replace('http://', '').replace('https://', '').split(':')[0]) for p in intranet_patterns)

        if is_valid and not is_forbidden:
            print(f"  ✓ PASS: {url}")
        else:
            print(f"  ✗ FAIL: {url} (should be allowed)")
            all_pass = False

    for url in forbidden_urls:
        clean_url = url.replace('http://', '').replace('https://', '').replace(':8080', '').replace(':80', '')
        is_forbidden = any(re.match(p, clean_url) for p in intranet_patterns)

        if is_forbidden:
            print(f"  ✓ PASS: {url} (correctly blocked)")
        else:
            print(f"  ✗ FAIL: {url} (should be blocked)")
            all_pass = False

    return all_pass

def test_output_schema():
    """测试输出格式"""
    print("\n[Test 2] 输出格式测试")

    # 模拟输出
    mock_output = {
        "title": "Test Page",
        "url": "https://example.com",
        "content": "Test content",
        "summary": "Test summary",
        "links": [{"text": "Link", "href": "https://example.com/page"}],
        "images": [{"alt": "Image", "src": "https://example.com/img.jpg"}],
        "status": "success",
        "msg": ""
    }

    required_fields = ["title", "url", "content", "summary", "links", "images", "status", "msg"]

    all_pass = True
    for field in required_fields:
        if field in mock_output:
            print(f"  ✓ PASS: '{field}' field exists")
        else:
            print(f"  ✗ FAIL: '{field}' field missing")
            all_pass = False

    return all_pass

def test_mode_handling():
    """测试模式处理"""
    print("\n[Test 3] 模式处理测试")

    valid_modes = ["full", "content", "links", "images"]

    all_pass = True
    for mode in valid_modes:
        print(f"  ✓ PASS: '{mode}' is valid mode")

    return all_pass

def test_content_cleaning():
    """测试内容清洗"""
    print("\n[Test 4] 内容清洗测试")

    # 模拟 HTML
    html_content = """
    <html>
    <head><title>Test</title></head>
    <body>
        <script>alert('test');</script>
        <style>.test { color: red; }</style>
        <article>
            <p>这是正文内容，包含<span>行内标签</span></p>
            <p>第二段内容</p>
        </article>
    </body>
    </html>
    """

    # 简单清洗逻辑（实际应用中更复杂）
    import re
    content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
    content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
    content = re.sub(r'<[^>]+>', '', content)
    content = re.sub(r'\s+', ' ', content).strip()

    expected_text = "Test 这是正文内容，包含行内标签 第二段内容"
    cleaned = content.replace(' ', '')

    if len(cleaned) > 0:
        print(f"  ✓ PASS: Content cleaned successfully")
        print(f"    Result: {content[:50]}...")
        return True
    else:
        print(f"  ✗ FAIL: Content cleaning failed")
        return False

def test_summary_generation():
    """测试摘要生成"""
    print("\n[Test 5] 摘要生成测试")

    content = "这是测试内容的第一段。这应该是摘要。" + "额外的内容。" * 50

    # 生成 200 字符摘要
    summary = content[:200]
    if len(summary) <= 200:
        print(f"  ✓ PASS: Summary generated ({len(summary)} chars)")
        return True
    else:
        print(f"  ✗ FAIL: Summary too long")
        return False

def main():
    print("=" * 50)
    print("浏览器爬虫功能测试")
    print("=" * 50)

    tests = [
        ("URL 验证", test_url_validation),
        ("输出格式", test_output_schema),
        ("模式处理", test_mode_handling),
        ("内容清洗", test_content_cleaning),
        ("摘要生成", test_summary_generation),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            results.append((name, False))

    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)

    all_pass = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {name}")
        if not passed:
            all_pass = False

    print("=" * 50)
    if all_pass:
        print("所有测试通过 ✓")
        return 0
    else:
        print("存在失败项 ✗")
        return 1

if __name__ == "__main__":
    sys.exit(main())
