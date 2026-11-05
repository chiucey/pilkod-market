#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终版政府人事任免信息爬虫 v5
修复免职提取问题
"""

import re
import csv
from datetime import datetime
from typing import List, Dict
import requests
from bs4 import BeautifulSoup


class FinalGovScraperV5:
    """最终版爬虫 - 完整提取任命和免职"""

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }

    def get_recent_urls(self) -> List[Dict]:
        """获取近期任免公报URL"""
        return [
            {'title': '国务院任免人员 (2026年3月)', 'url': 'https://www.gov.cn/gongbao/2026/issue_12606/202603/content_7061748.html'},
            {'title': '国务院任免人员 (2026年2月28日)', 'url': 'https://www.gov.cn/gongbao/2026/issue_12586/202602/content_7059932.html'},
            {'title': '国务院任免人员 (2026年2月20日)', 'url': 'https://www.gov.cn/gongbao/2026/issue_12566/202602/content_7057932.html'},
            {'title': '国务院任免人员 (2026年2月10日)', 'url': 'https://www.gov.cn/gongbao/2026/issue_12546/202602/content_7057446.html'},
            {'title': '国务院任免人员 (2026年1月30日)', 'url': 'https://www.gov.cn/gongbao/2026/issue_12526/202601/content_7056482.html'},
        ]

    def parse_article(self, url: str) -> List[Dict]:
        """解析任免文章"""
        try:
            response = requests.get(url, headers=self.HEADERS, timeout=30)
            response.encoding = 'utf-8'
            html = response.text

            soup = BeautifulSoup(html, 'html.parser')
            content = soup.find('div', class_='article')
            if not content:
                content = soup.find('div', class_=re.compile('TRS_Editor'))
            if not content:
                content = soup.find('div', id='zoom')

            if not content:
                return []

            text = content.get_text(separator='\n', strip=True)
            records = self._extract_records(text, url)
            return records

        except Exception as e:
            print(f"[错误] 解析失败 {url}: {e}")
            return []

    def _extract_records(self, text: str, source_url: str) -> List[Dict]:
        """从文本提取任免记录 - 完整版"""
        records = []

        # 先清理文本，去除多余换行
        text = text.replace('\n', '').replace('\r', '')

        # 找到所有日期
        date_pattern = r'(\d{4})年(\d{1,2})月(\d{1,2})日'
        dates = list(re.finditer(date_pattern, text))

        # 为每个日期范围提取内容
        for i, date_match in enumerate(dates):
            current_date = f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"

            # 确定当前日期段的文本范围
            start = date_match.end()
            if i + 1 < len(dates):
                end = dates[i + 1].start()
            else:
                end = len(text)

            segment = text[start:end]

            # 在当前段落中提取任命和免职
            # 任命模式: 任命XXX为YYY
            renming_pattern = r'任命([^，,。；;]+)为([^，,。；;]+?)(?=[，,；;]|$)'
            for m in re.finditer(renming_pattern, segment):
                name = m.group(1).strip()
                position = m.group(2).strip()
                # 清理职务中的多余内容
                position = re.sub(r'的?(?:职务|)$', '', position)
                if name and len(name) >= 2 and len(name) <= 10 and position:
                    records.append({
                        'name': name,
                        'position': position,
                        'action': '任命',
                        'date': current_date,
                        'doc_no': '',
                        'source_url': source_url
                    })

            # 免职模式: 免去XXX的YYY职务
            mianzhi_pattern = r'免去([^，,。；;]+?)(?:的|)([^，,。；;]+?)(?:职务|)(?=[，,；;]|$)'
            for m in re.finditer(mianzhi_pattern, segment):
                name = m.group(1).strip()
                position = m.group(2).strip()
                if name and len(name) >= 2 and len(name) <= 10 and position:
                    records.append({
                        'name': name,
                        'position': position,
                        'action': '免去',
                        'date': current_date,
                        'doc_no': '',
                        'source_url': source_url
                    })

        return records

    def scrape(self) -> List[Dict]:
        """执行爬取"""
        print("[爬虫] 开始爬取国务院公报任免信息...")

        all_records = []
        urls = self.get_recent_urls()

        for item in urls:
            print(f"[爬虫] 正在解析: {item['title']}")
            records = self.parse_article(item['url'])
            print(f"[爬虫] 提取到 {len(records)} 条记录")
            all_records.extend(records)

        # 去重
        unique = []
        seen = set()
        for r in all_records:
            key = (r['name'], r['action'], r['position'], r['date'])
            if key not in seen:
                seen.add(key)
                unique.append(r)

        print(f"[爬虫] 共提取 {len(unique)} 条去重后记录")
        return unique


def main():
    """主函数"""
    scraper = FinalGovScraperV5()
    records = scraper.scrape()

    print("\n" + "=" * 80)
    print("提取结果:")
    print("=" * 80)

    # 按日期排序
    records.sort(key=lambda x: (x['date'], x['action']))

    for r in records:
        print(f"{r['date']} | {r['action']:4s} | {r['name']:12s} | {r['position']}")

    print(f"\n共 {len(records)} 条记录")

    # 保存到CSV
    if records:
        with open('data/appointments.csv', 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'name', 'position', 'action', 'date', 'doc_no', 'source', 'source_url', 'crawl_time', 'batch_id', 'import_method'])
            writer.writeheader()

            for i, r in enumerate(records, 1):
                writer.writerow({
                    'id': f'GOV{i:06d}',
                    'name': r['name'],
                    'position': r['position'],
                    'action': r['action'],
                    'date': r['date'],
                    'doc_no': r.get('doc_no', ''),
                    'source': 'gov.cn',
                    'source_url': r.get('source_url', ''),
                    'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'batch_id': f'B{datetime.now().strftime("%Y%m%d")}01',
                    'import_method': 'scrape'
                })

        print(f"\n已保存到 data/appointments.csv")


if __name__ == '__main__':
    main()
