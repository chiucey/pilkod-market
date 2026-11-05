#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

url = 'https://www.gov.cn/gongbao/2026/issue_12606/202603/content_7061748.html'
resp = requests.get(url, headers=headers, timeout=30)

soup = BeautifulSoup(resp.text, 'html.parser')

# 查找文章内容
content = soup.find('div', class_=re.compile('TRS_Editor'))
if not content:
    content = soup.find('div', id='zoom')

text = content.get_text() if content else ''

print('=== 提取的文本 ===')
print(text)
print()

# 按日期分段
lines = text.split('\n')
records = []

current_date = ''
for line in lines:
    line = line.strip()
    if not line:
        continue

    # 检查日期
    date_match = re.match(r'(\d{4})年(\d{1,2})月(\d{1,2})日', line)
    if date_match:
        current_date = f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"
        continue

    # 处理任命
    if '任命' in line:
        # 分割可能有多个
        parts = re.split(r'[;；]', line)
        for part in parts:
            part = part.strip()
            matches = re.findall(r'任命(.+?)为(.+?)[。;；]?', part)
            for m in matches:
                name = m[0].strip()
                position = m[1].strip()
                records.append({
                    'name': name,
                    'position': position,
                    'action': '任命',
                    'date': current_date
                })

    # 处理免职
    if '免去' in line:
        parts = re.split(r'[;；]', line)
        for part in parts:
            part = part.strip()
            matches = re.findall(r'免去(.+?)(?:的|)(.+?)(?:职务|)[。;；]?', part)
            for m in matches:
                name = m[0].strip()
                position = m[1].strip()
                records.append({
                    'name': name,
                    'position': position,
                    'action': '免去',
                    'date': current_date
                })

print('=== 提取的记录 ===')
for r in records:
    print(f"  {r['date']} | {r['action']} | {r['name']} | {r['position']}")

print(f"\n共提取 {len(records)} 条记录")
