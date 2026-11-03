# -*- coding: utf-8 -*-
"""
每日新闻早报生成器 - 模块包
Daily News Brief Generator - Modules Package
"""

from .config_loader import ConfigLoader
from .news_fetcher import NewsFetcher, NewsItem
from .news_formatter import NewsFormatter

__all__ = [
    'ConfigLoader',
    'NewsFetcher',
    'NewsItem',
    'NewsFormatter'
]

__version__ = '1.0.0'
__author__ = 'MiniMax Agent'
