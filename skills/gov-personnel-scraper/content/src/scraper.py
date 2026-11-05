#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
政府人事任免信息爬虫核心模块
"""

import re
import json
import csv
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup


class GovScraper:
    """中国政府网人事任免信息爬虫"""

    BASE_URL = "https://www.gov.cn"
    SEARCH_URL = "https://www.gov.cn/search/site/"

    # 搜索配置
    SEARCH_PARAMS = {
        "keywords": "任免",
        "searchScope": "dealInfo",
        "siteId": "1"
    }

    # 请求头
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    def __init__(self, timeout: int = 30):
        self.session = requests.Session()
        self.timeout = timeout
        self.last_crawl_time = None

    def get_last_crawl_time(self, state_file: str) -> Optional[datetime]:
        """获取上次爬取时间"""
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
                last_time = state.get('last_crawl_time')
                if last_time:
                    return datetime.fromisoformat(last_time)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return None

    def search_renmian(self, max_pages: int = 5) -> List[Dict]:
        """
        搜索任免相关信息

        Args:
            max_pages: 最大搜索页数

        Returns:
            搜索结果列表
        """
        results = []

        for page in range(1, max_pages + 1):
            try:
                params = self.SEARCH_PARAMS.copy()
                params['page'] = page

                print(f"[爬虫] 正在搜索第 {page} 页...")

                response = self.session.get(
                    self.SEARCH_URL,
                    params=params,
                    headers=self.HEADERS,
                    timeout=self.timeout
                )

                if response.status_code != 200:
                    print(f"[爬虫] 页面请求失败: {response.status_code}")
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')

                # 查找搜索结果列表
                result_items = soup.select('.list .news, .searchResult .result, .news-list li, .result-list li')

                if not result_items:
                    # 备选选择器
                    result_items = soup.select('.m-list li, .news-list li, .search-list li')

                for item in result_items:
                    link_tag = item.find('a')
                    if not link_tag:
                        continue

                    title = link_tag.get_text(strip=True)
                    url = link_tag.get('href', '')

                    # 过滤任免相关内容
                    if '任免' not in title and '任命' not in title and '免去' not in title:
                        continue

                    # 获取摘要和时间
                    summary = item.find('p', class_='info') or item.find('.summary') or item.find('p')
                    date_tag = item.find('span', class_='date') or item.find('.time')

                    results.append({
                        'title': title,
                        'url': url if url.startswith('http') else urljoin(self.BASE_URL, url),
                        'summary': summary.get_text(strip=True) if summary else '',
                        'date': date_tag.get_text(strip=True) if date_tag else ''
                    })

                time.sleep(2)  # 礼貌性延迟

            except Exception as e:
                print(f"[爬虫] 第 {page} 页抓取出错: {e}")
                continue

        return results

    def parse_article(self, url: str) -> List[Dict]:
        """
        解析文章详情页，提取人事任免信息

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

            # 获取文章内容
            content = soup.find('div', class_='article-content') or \
                      soup.find('div', class_='TRS_Editor') or \
                      soup.find('div', id='zoom')

            if not content:
                content = soup.find('body')

            if not content:
                return []

            text = content.get_text(separator='\n', strip=True)

            # 提取信息
            info = self._extract_info(text, url)

            time.sleep(1)
            return info

        except Exception as e:
            print(f"[爬虫] 解析文章失败 {url}: {e}")
            return []

    def _extract_info(self, text: str, source_url: str) -> List[Dict]:
        """从文本中提取人事任免信息"""
        records = []

        # 获取文号
        doc_no = self._extract_doc_no(text)

        # 获取日期
        date = self._extract_date(text)

        # 提取任命信息
        appointment_patterns = [
            r'任命(.+?)(?:为|担任)(.+?)(?=\n|，|。|$)',
            r'(.+?)(?:被任命|任命|担任)(.+?)(?=\n|，|。|$)',
            r'决定任命(.+?)为(.+?)(?=\n|，|。|$)',
        ]

        for pattern in appointment_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                name = match.group(1).strip()
                position = match.group(2).strip()
                if self._is_valid_name(name):
                    records.append({
                        'name': name,
                        'position': position,
                        'action': '任命',
                        'doc_no': doc_no,
                        'date': date,
                        'source_url': source_url
                    })

        # 提取免职信息
        removal_patterns = [
            r'免去(.+?)(?:的职务|)(?=\n|，|。|$)',
            r'(.+?)(?:被免去|免去|免职|)(?:其|的|)(.+?)(?:职务|)(?=\n|，|。|$)',
            r'决定免去(.+?)(?:的职务|)(?=\n|，|。|$)',
        ]

        for pattern in removal_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                if '免去' in pattern:
                    name = match.group(1).strip()
                else:
                    name = match.group(1).strip()
                if self._is_valid_name(name):
                    records.append({
                        'name': name,
                        'position': '',
                        'action': '免去',
                        'doc_no': doc_no,
                        'date': date,
                        'source_url': source_url
                    })

        # 去除重复
        seen = set()
        unique_records = []
        for record in records:
            key = (record['name'], record['action'], record['doc_no'])
            if key not in seen:
                seen.add(key)
                unique_records.append(record)

        return unique_records

    def _extract_doc_no(self, text: str) -> str:
        """提取文号"""
        patterns = [
            r'〔(\d{4})〕\s*第?\s*\d+号',
            r'\((\d{4})\)\s*第?\s*\d+号',
            r'国人部发〔(\d{4})〕\d+号',
            r'中组部发〔(\d{4})〕\d+号',
            r'人社保部发〔(\d{4})〕\d+号',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)

        return ''

    def _extract_date(self, text: str) -> str:
        """提取日期"""
        patterns = [
            r'(\d{4})年\d{1,2}月\d{1,2}日',
            r'(\d{4})-(\d{2})-(\d{2})',
            r'(\d{4})/(\d{2})/(\d{2})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                if '年' in pattern:
                    return f"{match.group(1)}-{match.group(2).zfill(2)}-{match.group(3).zfill(2)}"
                else:
                    return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"

        return datetime.now().strftime('%Y-%m-%d')

    def _is_valid_name(self, name: str) -> bool:
        """验证是否为有效姓名"""
        if not name or len(name) < 2 or len(name) > 6:
            return False

        # 排除常见非姓名词汇
        exclude_words = ['会议', '通知', '决定', '文件', '规定', '条例', '办法']
        for word in exclude_words:
            if word in name:
                return False

        # 检查是否包含姓名常用字
        valid_chars = set('赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳酆鲍史唐费廉岑薛雷贺倪汤滕殷罗毕郝邬安常乐于时傅皮卡齐康余元卜顾孟平黄和穆萧尹姚邵堪汪祁毛禹狄米贝明臧计伏成戴谈宋茅庞熊纪舒屈项祝董梁杜阮蓝闽席季麻强贾路娄危江童颜郭梅盛林刁钟徐邱骆高夏蔡田樊胡凌霍虞万支柯咎管卢莫经房裘干解应宗丁宣贲邓郁单杭洪包诸左石崔吉钮龚程嵇邢滑裴陆荣翁荀羊於惠甄麴加封芮羿储靳汲邴糜松井段富巫乌焦巴弓牧隗山谷车侯宓蓬全郗班仰秋仲伊宫宁仇栾暴甘钭厉戌慕连茹习宦艾鱼容向古吉绣讯庚巫刻宗丙')
        return all(c in valid_chars or not c.isdigit() for c in name)

    def scrape(self, state_file: str, last_24h_only: bool = True) -> List[Dict]:
        """
        执行爬取任务

        Args:
            state_file: 状态文件路径
            last_24h_only: 是否只抓取最近24小时数据

        Returns:
            爬取到的人事信息列表
        """
        print("[爬虫] 开始爬取任务...")

        # 获取上次爬取时间
        last_crawl = self.get_last_crawl_time(state_file)
        cutoff_time = datetime.now() - timedelta(hours=24) if last_24h_only else None

        if last_crawl and cutoff_time:
            if last_crawl > cutoff_time:
                cutoff_time = last_crawl
            print(f"[爬虫] 增量模式：将抓取 {cutoff_time.strftime('%Y-%m-%d %H:%M:%S')} 之后的新数据")
        else:
            print(f"[爬虫] 全量模式：将抓取最近24小时的数据")

        # 搜索任免信息
        search_results = self.search_renmian(max_pages=5)
        print(f"[爬虫] 找到 {len(search_results)} 条搜索结果")

        all_records = []

        for result in search_results:
            # 检查时间过滤
            result_date_str = result.get('date', '')
            if result_date_str and cutoff_time:
                try:
                    # 尝试解析日期
                    date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', result_date_str)
                    if date_match:
                        result_date = datetime(
                            int(date_match.group(1)),
                            int(date_match.group(2)),
                            int(date_match.group(3))
                        )
                        if result_date < cutoff_time:
                            continue
                except:
                    pass

            # 解析详情
            records = self.parse_article(result['url'])
            print(f"[爬虫] 从 {result['title']} 提取到 {len(records)} 条记录")
            all_records.extend(records)

        print(f"[爬虫] 共提取 {len(all_records)} 条人事任免信息")
        return all_records


def test_scraper():
    """测试爬虫"""
    scraper = GovScraper()

    # 测试搜索功能
    results = scraper.search_renmian(max_pages=1)
    print(f"搜索结果: {len(results)} 条")

    for r in results[:3]:
        print(f"  - {r['title']}: {r['url']}")


if __name__ == '__main__':
    test_scraper()
