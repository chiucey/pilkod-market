#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量抓取示例
从文件读取多个文章链接，批量抓取
"""

import sys
import os
import time
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from fetch_article import WechatArticleFetcher


def read_urls_from_file(file_path):
    """从文件读取URL列表"""
    with open(file_path, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip() and line.startswith('http')]
    return urls


def main():
    # URL列表文件
    url_file = "urls.txt"  # 每行一个URL
    
    if not os.path.exists(url_file):
        print(f"URL文件不存在: {url_file}")
        print("请创建 urls.txt 文件，每行一个微信文章链接")
        return
    
    urls = read_urls_from_file(url_file)
    print(f"共 {len(urls)} 个链接待处理\n")
    
    # 创建抓取器
    fetcher = WechatArticleFetcher(
        output_dir='./output',
        enable_ocr=True,
        headless=True  # 无头模式，批量处理更快
    )
    
    # 批量处理
    results = []
    for i, url in enumerate(urls, 1):
        print(f"\n{'='*60}")
        print(f"处理第 {i}/{len(urls)} 个链接")
        print(f"{'='*60}")
        
        try:
            # 抓取文章
            article_data = fetcher.fetch(url)
            
            # 生成Word文档
            output_path = fetcher.generate_docx(article_data)
            
            results.append({
                'url': url,
                'title': article_data['title'],
                'status': 'success',
                'output': output_path
            })
            
            print(f"✓ 成功: {article_data['title']}")
            
        except Exception as e:
            print(f"✗ 失败: {e}")
            results.append({
                'url': url,
                'title': '',
                'status': 'failed',
                'error': str(e)
            })
        
        # 间隔等待
        if i < len(urls):
            print(f"\n等待5秒后处理下一个...")
            time.sleep(5)
    
    # 汇总
    print("\n" + "="*60)
    print("批量处理完成")
    print("="*60)
    
    success_count = sum(1 for r in results if r['status'] == 'success')
    print(f"\n成功: {success_count}/{len(urls)}")
    
    # 保存结果
    import json
    with open('./output/batch_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("结果已保存到: ./output/batch_results.json")


if __name__ == '__main__':
    main()
