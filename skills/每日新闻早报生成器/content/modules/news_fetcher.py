# -*- coding: utf-8 -*-
"""
新闻获取模块
News Fetcher Module

负责从各种新闻源获取新闻内容
"""

import feedparser
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import time
import random


class NewsItem:
    """新闻条目类"""
    
    def __init__(self, title: str, link: str, description: str = '', 
                 pubdate: Optional[datetime] = None, source: str = '',
                 category: str = 'general'):
        """
        初始化新闻条目
        
        Args:
            title: 标题
            link: 链接
            description: 描述
            pubdate: 发布日期
            source: 来源
            category: 分类
        """
        self.title = title
        self.link = link
        self.description = description
        self.pubdate = pubdate
        self.source = source
        self.category = category
    
    def __repr__(self):
        return f"NewsItem(title='{self.title[:30]}...', source='{self.source}')"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'title': self.title,
            'link': self.link,
            'description': self.description,
            'pubdate': self.pubdate.isoformat() if self.pubdate else None,
            'source': self.source,
            'category': self.category
        }


class NewsFetcher:
    """新闻获取器类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化新闻获取器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.news_sources = config.get('news_sources', [])
        self.max_news_per_category = config.get('output', {}).get('max_news_per_category', 10)
        
        # 设置请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_today_news(self) -> Dict[str, List[NewsItem]]:
        """
        获取今日新闻
        
        Returns:
            按分类组织的新闻字典
        """
        all_news = []
        
        # 获取所有新闻源的新闻
        for source in self.news_sources:
            if not source.get('enabled', True):
                continue
            
            try:
                news_items = self._fetch_from_source(source)
                all_news.extend(news_items)
                
                # 添加延迟，避免请求过快
                time.sleep(random.uniform(0.5, 1.5))
                
            except Exception as e:
                print(f"从 {source['name']} 获取新闻失败: {e}", file=__import__('sys').stderr)
                continue
        
        # 按分类组织新闻
        categorized_news = self._categorize_news(all_news)
        
        return categorized_news
    
    def _fetch_from_source(self, source: Dict) -> List[NewsItem]:
        """
        从单个新闻源获取新闻
        
        Args:
            source: 新闻源配置
            
        Returns:
            新闻条目列表
        """
        url = source.get('url', '')
        name = source.get('name', 'Unknown')
        category = source.get('category', 'general')
        
        # 使用feedparser解析RSS
        feed = feedparser.parse(url)
        
        news_items = []
        for entry in feed.entries[:self.max_news_per_category]:
            # 解析发布日期
            pubdate = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pubdate = datetime(*entry.published_parsed[:6])
            
            # 清理描述
            description = self._clean_html(getattr(entry, 'summary', ''))
            
            news_item = NewsItem(
                title=entry.title,
                link=entry.link,
                description=description,
                pubdate=pubdate,
                source=name,
                category=category
            )
            news_items.append(news_item)
        
        return news_items
    
    def _clean_html(self, html: str) -> str:
        """
        清理HTML标签
        
        Args:
            html: HTML字符串
            
        Returns:
            清理后的文本
        """
        if not html:
            return ''
        
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        
        # 移除多余空白
        text = ' '.join(text.split())
        
        # 限制长度
        if len(text) > 200:
            text = text[:200] + '...'
        
        return text
    
    def _categorize_news(self, news: List[NewsItem]) -> Dict[str, List[NewsItem]]:
        """
        将新闻分类
        
        Args:
            news: 新闻列表
            
        Returns:
            按分类组织的新闻字典
        """
        categories = {
            'domestic': [],      # 国内新闻
            'international': [], # 国际新闻
            'finance': [],       # 财经新闻
            'technology': [],    # 科技新闻
            'sports': [],        # 体育新闻
            'entertainment': [], # 娱乐新闻
            'general': []        # 通用分类
        }
        
        # 按发布日期排序
        news.sort(key=lambda x: x.pubdate or datetime.min, reverse=True)
        
        # 分类
        for item in news:
            category = item.category.lower()
            if category in categories:
                categories[category].append(item)
            else:
                categories['general'].append(item)
        
        # 限制每个分类的新闻数量
        for cat in categories:
            categories[cat] = categories[cat][:self.max_news_per_category]
        
        return categories
    
    def fetch_with_requests(self, url: str) -> Optional[str]:
        """
        使用requests获取网页内容
        
        Args:
            url: 网页URL
            
        Returns:
            网页内容
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"请求失败: {e}", file=__import__('sys').stderr)
            return None
