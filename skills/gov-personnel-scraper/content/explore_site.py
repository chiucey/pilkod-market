#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深入分析国务院网站结构
"""

import requests
from bs4 import BeautifulSoup
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

def explore_homepage():
    """探索首页结构"""
    print("=" * 70)
    print("探索首页结构")
    print("=" * 70)

    url = "https://www.gov.cn/"
    response = requests.get(url, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 查找所有导航菜单
    nav = soup.find('nav') or soup.find('div', class_=re.compile('nav|menu'))
    if nav:
        print("找到导航区域")
        links = nav.find_all('a', href=True)
        for a in links[:20]:
            print(f"  {a.get_text(strip=True)[:30]:30s} -> {a.get('href')[:50]}")

    # 查找搜索框
    search_inputs = soup.find_all(['input', 'form'])
    print("\n搜索相关元素:")
    for elem in search_inputs:
        if 'search' in str(elem).lower() or 'input' in elem.name:
            print(f"  {elem}")

    # 查找主内容区域的链接
    main = soup.find('main') or soup.find('div', id='main') or soup.find('div', class_=re.compile('main|content'))
    if main:
        print("\n主内容区域链接:")
        links = main.find_all('a', href=True)
        for a in links[:30]:
            href = a.get('href', '')
            text = a.get_text(strip=True)[:40]
            if href.startswith('http') or href.startswith('/'):
                print(f"  {text:40s} -> {href[:60]}")

def explore_search_urls():
    """测试多种搜索URL"""
    print("\n" + "=" * 70)
    print("测试多种搜索URL")
    print("=" * 70)

    # 尝试不同的搜索URL格式
    urls = [
        # 政策文件库
        "https://sousuo.www.gov.cn/zcwjk/policyDocumentLibrary?q=%E4%BB%BB%E5%85%8D&t=zhengcelibrary",
        # 全站搜索
        "https://sousuo.www.gov.cn/s.htm?type=site&searchword=%E4%BB%BB%E5%85%8D",
        # 政务搜索
        "https://sousuo.www.gov.cn/s.htm?q=%E4%BB%BB%E5%85%8D&t=govall",
        # 政府网首页搜索跳转
        "https://www.gov.cn/",
    ]

    for url in urls:
        print(f"\n测试: {url[:80]}")
        try:
            response = requests.get(url, headers=HEADERS, timeout=30, allow_redirects=True)
            print(f"  状态: {response.status_code}, 最终URL: {response.url[:60]}")

            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('title')
            if title:
                print(f"  标题: {title.get_text(strip=True)[:60]}")

            # 保存页面
            filename = f"/workspace/temp-skills/gov-personnel-scraper/data/page_{hash(url)}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"  已保存: {filename}")

        except Exception as e:
            print(f"  错误: {e}")

def find_renmian_pages():
    """查找可能的任免信息页面"""
    print("\n" + "=" * 70)
    print("查找任免信息相关页面")
    print("=" * 70)

    # 从首页获取所有链接，然后逐个检查
    url = "https://www.gov.cn/"
    response = requests.get(url, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 收集所有内链
    all_links = soup.find_all('a', href=True)
    internal_links = []

    for a in all_links:
        href = a.get('href', '')
        if href.startswith('/') or 'gov.cn' in href:
            full_url = href if href.startswith('http') else f"https://www.gov.cn{href}"
            internal_links.append((a.get_text(strip=True), full_url))

    # 去重
    seen = set()
    unique_links = []
    for text, link in internal_links:
        if link not in seen:
            seen.add(link)
            unique_links.append((text, link))

    print(f"找到 {len(unique_links)} 个内部链接")

    # 检查哪些页面可能包含任免信息
    possible_pages = []
    for text, link in unique_links:
        keywords = ['renmian', 'renmian', 'zhengce', 'xinwen', '，领导', '任命', '干部']
        if any(kw in link.lower() or kw in text for kw in keywords):
            possible_pages.append((text, link))

    print(f"\n可能相关的页面 ({len(possible_pages)}):")
    for text, link in possible_pages[:20]:
        print(f"  {text[:40]:40s} -> {link[:70]}")

    return possible_pages

def explore_policy_pages():
    """探索政策文件页面"""
    print("\n" + "=" * 70)
    print("探索政策文件页面")
    print("=" * 70)

    urls_to_try = [
        "https://www.gov.cn/zhengce/index.htm",
        "https://www.gov.cn/zhengce/xxgk.htm",
        "https://sousuo.www.gov.cn/zcwjk/policyDocumentLibrary?t=zhengcelibrary&q=",
    ]

    for url in urls_to_try:
        print(f"\n探索: {url[:70]}")
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.find('title')
                print(f"  标题: {title.get_text(strip=True)[:60] if title else '无'}")

                # 查找文章列表
                articles = soup.select('a[href*="content"]')
                print(f"  内容链接数: {len(articles)}")

                # 查找表格
                tables = soup.find_all('table')
                print(f"  表格数: {len(tables)}")

                if tables:
                    for table in tables[:2]:
                        rows = table.find_all('tr')
                        print(f"    表格行数: {len(rows)}")
                        for row in rows[:3]:
                            cells = row.find_all(['td', 'th'])
                            print(f"      行: {[c.get_text(strip=True)[:20] for c in cells]}")

        except Exception as e:
            print(f"  错误: {e}")

def test_api():
    """测试可能的API接口"""
    print("\n" + "=" * 70)
    print("测试API接口")
    print("=" * 70)

    # 尝试JSON API
    api_urls = [
        "https://sousuo.www.gov.cn/api/public/search?q=%E4%BB%BB%E5%85%8D&t=site&page=1",
        "https://www.gov.cn/api/search?q=%E4%BB%BB%E5%85%8D",
    ]

    for url in api_urls:
        print(f"\n测试: {url[:70]}")
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            print(f"  状态: {response.status_code}")
            if 'json' in response.headers.get('Content-Type', ''):
                print(f"  JSON响应: {response.text[:200]}")
        except Exception as e:
            print(f"  错误: {e}")

def simulate_search():
    """模拟网站搜索行为"""
    print("\n" + "=" * 70)
    print("模拟网站搜索")
    print("=" * 70)

    # 国务院搜索的常见URL格式
    base_url = "https://sousuo.www.gov.cn/s.htm"

    # 尝试带搜索参数的请求
    params_list = [
        {"q": "任免", "type": "site"},
        {"searchword": "任免", "t": "govall"},
        {"q": "任免", "t": "zhengcelibrary"},
    ]

    for params in params_list:
        print(f"\n尝试参数: {params}")
        try:
            response = requests.get(base_url, params=params, headers=HEADERS, timeout=30, allow_redirects=True)
            print(f"  URL: {response.url[:100]}")
            print(f"  状态: {response.status_code}")

            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('title')
            print(f"  标题: {title.get_text(strip=True)[:60] if title else '无'}")

            # 查找搜索结果
            results = soup.select('.result, .news, .article, li')
            print(f"  结果项: {len(results)}")

        except Exception as e:
            print(f"  错误: {e}")

if __name__ == '__main__':
    explore_homepage()
    explore_search_urls()
    find_renmian_pages()
    explore_policy_pages()
    test_api()
    simulate_search()

    print("\n" + "=" * 70)
    print("探索完成")
    print("=" * 70)
