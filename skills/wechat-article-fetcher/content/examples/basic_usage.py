#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基本用法示例
"""

import sys
import os

# 添加scripts目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from fetch_article import WechatArticleFetcher


def main():
    # 创建抓取器
    fetcher = WechatArticleFetcher(
        output_dir='./output',
        enable_ocr=True,
        max_comments=10,
        headless=False  # 显示浏览器窗口
    )
    
    # 文章链接
    article_url = "https://mp.weixin.qq.com/s/xxxxxx"
    
    # 抓取文章
    print("开始抓取文章...")
    article_data = fetcher.fetch(article_url)
    
    # 生成Word文档
    print("\n生成Word文档...")
    output_path = fetcher.generate_docx(article_data)
    
    print(f"\n完成！文档已保存到: {output_path}")


if __name__ == '__main__':
    main()
