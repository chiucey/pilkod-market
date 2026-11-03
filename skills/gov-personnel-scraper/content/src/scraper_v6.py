#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终版政府人事任免信息爬虫 v6
简化正则，提高提取准确性
"""

import re
import csv
from datetime import datetime
from typing import List, Dict
import requests
from bs4 import BeautifulSoup


class FinalGovScraperV6:
    """最终版爬虫 - 简化正则"""

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
        """从文本提取任免记录 - 简化版"""
        records = []

        # 合并换行
        text = text.replace('\n', '').replace('\r', '')

        # 找出所有日期
        dates = re.findall(r'(\d{4})年(\d{1,2})月(\d{1,2})日', text)

        for year, month, day in dates:
            current_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

            # 找这个日期之后、下一个日期之前的内容
            pattern = rf'{year}年{month}月{day}日(.+?)(?=\d{{4}}年\d{{1,2}}月\d{{1,2}}日|$)'
            match = re.search(pattern, text)
            if not match:
                continue

            segment = match.group(1)

            # 简化：直接用句号分割，每句话单独处理
            sentences = segment.split('。')

            for sent in sentences:
                sent = sent.strip()
                if not sent:
                    continue

                # 处理任命：找"任命"和"为"
                if '任命' in sent and '为' in sent:
                    # 提取"任命"后面的部分
                    renming_part = sent.split('任命')[-1]
                    # 提取"为"前面的姓名和后面的职务
                    if '为' in renming_part:
                        parts = renming_part.split('为', 1)
                        name = parts[0].strip()
                        position = parts[1].strip() if len(parts) > 1 else ''
                        # 清理职务
                        position = re.sub(r'[，,；;]', '', position)
                        position = position.strip('职务').strip()

                        if name and 2 <= len(name) <= 10 and position:
                            records.append({
                                'name': name,
                                'position': position,
                                'action': '任命',
                                'date': current_date,
                                'doc_no': '',
                                'source_url': source_url
                            })

                # 处理免职：找"免去"和"的"
                if '免去' in sent:
                    # 提取"免去"后面的部分
                    mianzhi_part = sent.split('免去')[-1]
                    # 格式：XXX的YYY
                    if '的' in mianzhi_part:
                        parts = mianzhi_part.split('的', 1)
                        name = parts[0].strip()
                        position = parts[1].strip() if len(parts) > 1 else ''
                        # 清理职务
                        position = position.strip('职务').strip()
                        position = re.sub(r'[，,；;]', '', position)

                        if name and 2 <= len(name) <= 10 and position:
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
    scraper = FinalGovScraperV6()
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
