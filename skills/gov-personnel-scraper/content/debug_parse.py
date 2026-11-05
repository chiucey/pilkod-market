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

print(f'状态: {resp.status_code}')
print(f'编码: {resp.encoding}')
print(f'内容长度: {len(resp.text)}')

soup = BeautifulSoup(resp.text, 'html.parser')

# 尝试所有可能的内容容器
selectors = [
    ('div', 'TRS_Editor'),
    ('div', 'zoom'),
    ('div', 'article'),
    ('div', 'content'),
    ('td', 'bzw'),
]

for tag, cls in selectors:
    elem = soup.find(tag, class_=cls)
    if elem:
        text = elem.get_text()
        print(f'\n找到 {tag}.{cls}: {len(text)} 字符')
        print(f'前200字符: {text[:200]}')
        break
else:
    # 尝试body
    body = soup.find('body')
    if body:
        # 保存到文件
        with open('debug_page.html', 'w', encoding='utf-8') as f:
            f.write(resp.text)
        print('已保存页面到 debug_page.html')

        # 查找所有div
        divs = soup.find_all('div')
        print(f'页面共有 {len(divs)} 个div')

        # 查找包含任免的div
        for div in divs:
            text = div.get_text()
            if '任命' in text or '免去' in text:
                print(f'\n找到包含任免的div:')
                print(text[:500])
                break
