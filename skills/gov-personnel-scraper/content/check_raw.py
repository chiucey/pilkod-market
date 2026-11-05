#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0'}
url = 'https://www.gov.cn/gongbao/2026/issue_12606/202603/content_7061748.html'
resp = requests.get(url, headers=headers, timeout=30)
resp.encoding = 'utf-8'

soup = BeautifulSoup(resp.text, 'html.parser')
content = soup.find('div', class_='article')
text = content.get_text() if content else ''

# 保存到文件
with open('data/raw_content.txt', 'w', encoding='utf-8') as f:
    f.write(text)

print("原始内容:")
print(text)
print()
print("="*50)
print("分析每句话:")

import re
sentences = text.split('。')
for i, s in enumerate(sentences):
    s = s.strip()
    if s:
        print(f"{i}: {s}")
        if '免去' in s:
            print("  -> 包含免去")
        if '任命' in s:
            print("  -> 包含任命")
