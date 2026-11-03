#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日新闻早报生成器 - 主程序入口
Daily News Brief Generator - Main Entry Point

功能：自动收集、整理并生成格式化的每日新闻早报
"""

import argparse
import sys
import os
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.config_loader import ConfigLoader
from modules.news_fetcher import NewsFetcher
from modules.news_formatter import NewsFormatter


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='每日新闻早报生成器 - 自动生成格式化新闻早报',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  python main.py                      # 生成Markdown格式早报
  python main.py --format html        # 生成HTML格式早报
  python main.py --output my_brief.md # 保存到指定文件
  python main.py --config custom.yaml # 使用自定义配置文件
  python main.py --no-weather         # 不包含天气信息
  python main.py --no-quote           # 不包含今日名言
        '''
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['markdown', 'html', 'text'],
        default='markdown',
        help='输出格式 (默认: markdown)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='输出文件路径 (默认: 输出到标准输出)'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        default=None,
        help='配置文件路径 (默认: config/settings.yaml)'
    )
    
    parser.add_argument(
        '--no-weather',
        action='store_true',
        help='不包含天气信息'
    )
    
    parser.add_argument(
        '--no-quote',
        action='store_true',
        help='不包含今日名言'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细输出'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    return parser.parse_args()


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 显示版本和启动信息
    if args.verbose:
        print(f"每日新闻早报生成器 v1.0.0")
        print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
    
    try:
        # 加载配置
        config_path = args.config or 'config/settings.yaml'
        config_loader = ConfigLoader(config_path)
        config = config_loader.load()
        
        if args.verbose:
            print(f"配置文件: {config_path}")
            print(f"新闻源数量: {len(config.get('news_sources', []))}")
            print("-" * 50)
        
        # 创建新闻获取器
        fetcher = NewsFetcher(config)
        
        if args.verbose:
            print("正在获取新闻...")
        
        # 获取新闻
        news_data = fetcher.get_today_news()
        
        if args.verbose:
            print(f"获取到 {sum(len(v) for v in news_data.values())} 条新闻")
            print("-" * 50)
        
        # 创建格式化器
        formatter = NewsFormatter(config)
        
        # 设置选项
        options = {
            'format': args.format,
            'include_weather': not args.no_weather,
            'include_quote': not args.no_quote,
            'verbose': args.verbose
        }
        
        # 格式化输出
        report = formatter.format(news_data, **options)
        
        # 输出结果
        if args.output:
            # 保存到文件
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report, encoding='utf-8')
            print(f"早报已保存到: {args.output}")
        else:
            # 输出到标准输出
            print(report)
        
        if args.verbose:
            print("-" * 50)
            print("生成完成!")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"错误: 找不到配置文件 - {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"错误: 生成早报失败 - {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
