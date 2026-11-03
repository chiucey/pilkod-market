#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进版政府人事任免信息爬虫
适配新版gov.cn网站结构
"""

import re
import json
import csv
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import requests
from bs4 import BeautifulSoup


class ImprovedGovScraper:
    """改进版政府网站爬虫"""

    # 政策文件库搜索URL
    SEARCH_URL = "https://sousuo.www.gov.cn/zcwjk/policyDocumentLibrary"
    GONGBAO_BASE = "https://www.gov.cn/gongbao"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    def __init__(self, timeout: int = 30):
        self.session = requests.Session()
        self.timeout = timeout

    def search_gongbao_renmian(self, max_pages: int = 3) -> List[Dict]:
        """
        搜索国务院公报中的任免人员信息

        Args:
            max_pages: 最大搜索页数

        Returns:
            搜索结果列表
        """
        results = []

        for page in range(1, max_pages + 1):
            try:
                params = {
                    "q": "任免",
                    "t": "zhengcelibrary",
                    "page": page
                }

                print(f"[爬虫] 正在搜索第 {page} 页...")

                response = self.session.get(
                    self.SEARCH_URL,
                    params=params,
                    headers=self.HEADERS,
                    timeout=self.timeout
                )

                if response.status_code != 200:
                    print(f"[爬虫] 搜索请求失败: {response.status_code}")
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')

                # 查找搜索结果列表
                # 国务院公报的任免人员页面特征
                items = soup.select('.result, .news, .list li, tr, .article')

                for item in items:
                    # 查找标题和链接
                    link = item.find('a', href=True)
                    if not link:
                        continue

                    title = link.get_text(strip=True)

                    # 只关注"任免人员"相关
                    if '任免人员' not in title:
                        continue

                    href = link.get('href', '')
                    if not href:
                        continue

                    # 获取日期
                    date_elem = item.find(['span', 'td', 'p'], class_=re.compile('date|time'))
                    date_str = date_elem.get_text(strip=True) if date_elem else ''

                    # 尝试从URL或标题中提取日期
                    date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', title)
                    if date_match:
                        date_str = f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"

                    results.append({
                        'title': title,
                        'url': href if href.startswith('http') else f"https://www.gov.cn{href}",
                        'date': date_str
                    })

                time.sleep(1)

            except Exception as e:
                print(f"[爬虫] 第 {page} 页搜索出错: {e}")
                continue

        return results

    def parse_gongbao_article(self, url: str) -> List[Dict]:
        """
        解析国务院公报任免文章

        Args:
            url: 文章URL

        Returns:
            提取的人事信息列表
        """
        try:
            response = self.session.get(
                url,
                headers=self.HEADERS,
                timeout=self.timeout
            )

            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, 'html.parser')

            # 获取文章正文
            content = soup.find('div', class_=re.compile('content|article|TRS_Editor'))
            if not content:
                content = soup.find('body')

            if not content:
                return []

            text = content.get_text(separator='\n', strip=True)

            # 提取任免信息
            records = self._extract_renmian_from_text(text, url)

            time.sleep(1)
            return records

        except Exception as e:
            print(f"[爬虫] 解析文章失败 {url}: {e}")
            return []

    def _extract_renmian_from_text(self, text: str, source_url: str) -> List[Dict]:
        """
        从文本中提取任免信息

        格式示例：
        2026年2月10日
        任命孙志禹为水利部副部长。
        任命何飚为国家广播电视总局副局长。
        """
        records = []

        # 按日期分段
        date_pattern = r'(\d{4})年(\d{1,2})月(\d{1,2})日'
        date_sections = re.split(date_pattern, text)

        current_date = ''
        current_text = ''

        for i, section in enumerate(date_sections):
            # 检查是否是日期部分
            date_match = re.match(r'(\d{4})年(\d{1,2})月(\d{1,2})日', section)
            if date_match:
                current_date = f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"
                continue

            # 处理任命/免职文本
            if current_date and section.strip():
                lines = section.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line or len(line) < 5:
                        continue

                    # 解析任命
                    if '任命' in line and '为' in line:
                        record = self._parse_renming(line, current_date, source_url)
                        if record:
                            records.extend(record)

                    # 解析免职
                    if '免去' in line and '的' in line:
                        record = self._parse_mianzhi(line, current_date, source_url)
                        if record:
                            records.extend(record)

        return records

    def _parse_renming(self, line: str, date: str, source_url: str) -> List[Dict]:
        """解析任命信息"""
        records = []

        # 格式: 任命XXX为YYY
        patterns = [
            r'任命(.+?)为(.+?)[。；]',
            r'任命(.+?)为(.+)$',
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, line)
            for match in matches:
                name = match.group(1).strip()
                position = match.group(2).strip()

                # 清理职务
                position = re.sub(r'[。；，,]', '', position)

                if self._is_valid_name(name) and position:
                    records.append({
                        'name': name,
                        'position': position,
                        'action': '任命',
                        'date': date,
                        'doc_no': '',
                        'source_url': source_url
                    })

        return records

    def _parse_mianzhi(self, line: str, date: str, source_url: str) -> List[Dict]:
        """解析免职信息"""
        records = []

        # 格式: 免去XXX的YYY职务
        patterns = [
            r'免去(.+?)的(.+?)(?:职务|)$',
            r'免去(.+?)(?:的|)(.+?)(?:职务|)[。；]',
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, line)
            for match in matches:
                name = match.group(1).strip()
                position = match.group(2).strip()

                # 清理
                position = re.sub(r'[。；，,]', '', position)

                if self._is_valid_name(name):
                    records.append({
                        'name': name,
                        'position': position,
                        'action': '免去',
                        'date': date,
                        'doc_no': '',
                        'source_url': source_url
                    })

        return records

    def _is_valid_name(self, name: str) -> bool:
        """验证是否为有效姓名"""
        if not name or len(name) < 2 or len(name) > 6:
            return False

        # 检查是否包含姓名常用字
        name_chars = set(name)
        common_chars = set('赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳酆鲍史唐费廉岑薛雷贺倪汤滕殷罗毕郝邬安常乐于时傅皮卡齐康余元卜顾孟平黄')

        # 至少包含一个常见姓氏
        has_surname = any(c in common_chars for c in name_chars)

        # 排除常见非姓名词
        exclude_words = ['会议', '通知', '决定', '文件', '规定', '条例', '办法', '主任', '副主任', '部长', '副部长']
        has_exclude = any(word in name for word in exclude_words)

        return has_surname and not has_exclude

    def scrape(self, state_file: str, last_24h_only: bool = True) -> List[Dict]:
        """
        执行爬取任务

        Args:
            state_file: 状态文件路径
            last_24h_only: 是否只抓取最近24小时数据

        Returns:
            爬取到的人事信息列表
        """
        print("[爬虫] 开始爬取国务院公报任免信息...")

        # 搜索任免公报
        search_results = self.search_gongbao_renmian(max_pages=3)
        print(f"[爬虫] 找到 {len(search_results)} 条搜索结果")

        all_records = []

        for result in search_results:
            print(f"[爬虫] 正在解析: {result['title']}")
            records = self.parse_gongbao_article(result['url'])

            # 过滤日期
            result_date = result.get('date', '')
            if result_date:
                for record in records:
                    record['date'] = result_date

            print(f"[爬虫] 从 {result['title']} 提取到 {len(records)} 条记录")
            all_records.extend(records)

        print(f"[爬虫] 共提取 {len(all_records)} 条人事任免信息")
        return all_records


def test_improved_scraper():
    """测试改进版爬虫"""
    scraper = ImprovedGovScraper()

    # 测试搜索
    results = scraper.search_gongbao_renmian(max_pages=1)
    print(f"\n搜索结果: {len(results)} 条")

    for r in results:
        print(f"  - {r['title']}: {r['date']}")

    # 测试解析
    if results:
        url = results[0]['url']
        print(f"\n正在解析: {url}")
        records = scraper.parse_gongbao_article(url)

        print(f"提取记录: {len(records)} 条")
        for rec in records:
            print(f"  - {rec['name']}: {rec['action']} {rec['position']} ({rec['date']})")


if __name__ == '__main__':
    test_improved_scraper()
