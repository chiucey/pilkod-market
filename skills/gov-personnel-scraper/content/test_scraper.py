#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试国务院网站爬取功能
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time

# 配置
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

def test_homepage():
    """测试首页"""
    print("=" * 60)
    print("测试1: 访问国务院首页")
    print("=" * 60)

    url = "https://www.gov.cn/"
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        print(f"状态码: {response.status_code}")
        print(f"内容长度: {len(response.text)} 字符")

        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找搜索框
        search_form = soup.find('form', {'class': 'search'})
        if search_form:
            print("找到搜索表单")
            inputs = search_form.find_all('input')
            for inp in inputs:
                print(f"  - input: name={inp.get('name')}, type={inp.get('type')}, placeholder={inp.get('placeholder')}")

        # 查找导航链接
        nav_links = soup.find_all('a', href=True)
        gov_links = [a for a in nav_links if 'zhengce' in a.get('href', '').lower() or 'renmian' in a.get('href', '').lower()]
        print(f"\n找到 {len(gov_links)} 个相关链接:")
        for link in gov_links[:10]:
            print(f"  - {link.get_text(strip=True)}: {link.get('href')}")

    except Exception as e:
        print(f"错误: {e}")

def test_search_page():
    """测试搜索页面"""
    print("\n" + "=" * 60)
    print("测试2: 访问搜索页面")
    print("=" * 60)

    # 尝试不同的搜索URL
    search_urls = [
        "https://sousuo.www.gov.cn/s.htm?type=site&searchword=%E4%BB%BB%E5%85%8D",
        "https://www.gov.cn/search/site/?searchword=%E4%BB%BB%E5%85%8D",
        "https://sousuo.www.gov.cn/sztb/?searchword=%E4%BB%BB%E5%85%8D&t=govall",
    ]

    for url in search_urls:
        print(f"\n尝试: {url[:80]}...")
        try:
            response = requests.get(url, headers=HEADERS, timeout=30, allow_redirects=True)
            print(f"  状态码: {response.status_code}")
            print(f"  最终URL: {response.url[:100]}")
            print(f"  内容长度: {len(response.text)} 字符")

            if "不存在" in response.text or "404" in response.text:
                print("  ⚠️ 页面不存在")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')

            # 分析页面结构
            title = soup.find('title')
            print(f"  标题: {title.get_text(strip=True) if title else '无'}")

            # 查找搜索结果列表
            result_items = soup.select('.result, .news, .list li, .searchResult')
            print(f"  找到 {len(result_items)} 个可能的结果容器")

            # 查找包含任免的链接
            renmian_links = soup.find_all('a', href=True)
            renmian_links = [a for a in renmian_links if '任免' in a.get_text() or '任命' in a.get_text()]
            print(f"  包含'任免'/'任命'的链接: {len(renmian_links)}")

            for link in renmian_links[:5]:
                print(f"    - {link.get_text(strip=True)[:50]}: {link.get('href')[:60]}")

            break  # 找到有效的就停止

        except Exception as e:
            print(f"  错误: {e}")

def test_policy_pages():
    """测试政府信息公开页面"""
    print("\n" + "=" * 60)
    print("测试3: 测试政府信息公开页面")
    print("=" * 60)

    # 尝试多个可能的任免信息页面
    urls = [
        "https://www.gov.cn/zhengce/xxgk/index.htm",
        "https://www.gov.cn/zhengce/renmr/index.htm",
        "https://www.gov.cn/zwgk/renmr/index.htm",
    ]

    for url in urls:
        print(f"\n尝试: {url}")
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            print(f"  状态码: {response.status_code}")

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # 查找表格（政府文件通常用表格展示）
                tables = soup.find_all('table')
                print(f"  找到 {len(tables)} 个表格")

                # 查找文章列表
                articles = soup.select('tr, li.article, .article, .news')
                print(f"  找到 {len(articles)} 个可能的内容项")

                # 查找包含任免的标题
                titles = soup.find_all(['a', 'span', 'h2', 'h3'])
                renmian_titles = [t for t in titles if '任免' in t.get_text() or '任命' in t.get_text()]
                print(f"  包含任免/任命的内容: {len(renmian_titles)}")

                for t in renmian_titles[:3]:
                    print(f"    - {t.get_text(strip=True)[:60]}")

        except Exception as e:
            print(f"  错误: {e}")

def test_direct_article():
    """测试直接访问文章"""
    print("\n" + "=" * 60)
    print("测试4: 尝试找到任免相关文章")
    print("=" * 60)

    # 尝试搜索最近的可能包含任免信息的页面
    search_url = "https://sousuo.www.gov.cn/s.htm"
    params = {
        'type': 'site',
        'searchword': '任免',
        't': 'govall'
    }

    try:
        response = requests.get(search_url, params=params, headers=HEADERS, timeout=30)
        print(f"搜索URL: {response.url}")
        print(f"状态码: {response.status_code}")
        print(f"内容长度: {len(response.text)} 字符")

        soup = BeautifulSoup(response.text, 'html.parser')

        # 保存页面用于分析
        with open('/workspace/temp-skills/gov-personnel-scraper/data/search_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("页面已保存到 data/search_page.html")

        # 查找所有链接
        all_links = soup.find_all('a', href=True)
        print(f"\n总共找到 {len(all_links)} 个链接")

        # 筛选包含任免的
        renmian = [a for a in all_links if '任免' in a.get_text() or '任命' in a.get_text()]
        print(f"包含'任免'/'任命': {len(renmian)}")

        for link in renmian[:10]:
            href = link.get('href', '')
            text = link.get_text(strip=True)[:60]
            print(f"  - {text}")
            print(f"    {href}")

    except Exception as e:
        print(f"错误: {e}")

def analyze_search_result_page():
    """分析搜索结果页面结构"""
    print("\n" + "=" * 60)
    print("测试5: 分析国务院搜索结果页面结构")
    print("=" * 60)

    # 尝试不同的搜索接口
    urls_to_try = [
        "https://sousuo.www.gov.cn/s.htm?type=site&searchword=%E4%BB%BB%E5%85%8D&t=govall&page=1",
        "https://www.gov.cn/zhengce/renmr/index.htm",
    ]

    for url in urls_to_try:
        try:
            print(f"\n分析: {url[:80]}...")
            response = requests.get(url, headers=HEADERS, timeout=30)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # 查找可能的列表容器
                containers = [
                    ('.list', soup),
                    ('.news-list', soup),
                    ('.result-list', soup),
                    ('ul', soup),
                    ('table', soup),
                    ('#results', soup),
                    ('.searchResults', soup),
                ]

                for selector, elem in containers:
                    items = elem.select(selector)
                    if items and len(items) > 3:
                        print(f"\n  找到列表: {selector} ({len(items)} 项)")
                        # 分析第一个项的结构
                        first = items[0]
                        links = first.find_all('a', href=True)
                        text_content = first.get_text()[:100]
                        print(f"    文本预览: {text_content}")
                        print(f"    链接数: {len(links)}")

        except Exception as e:
            print(f"错误: {e}")

if __name__ == '__main__':
    print("开始测试国务院网站爬取功能...")
    print()

    test_homepage()
    test_search_page()
    test_policy_pages()
    test_direct_article()
    analyze_search_result_page()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
