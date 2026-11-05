# -*- coding: utf-8 -*-
"""
新闻格式化模块
News Formatter Module

负责将新闻内容格式化为各种输出格式
"""

from datetime import datetime, date
from typing import Dict, List, Any, Optional
from modules.news_fetcher import NewsItem


class NewsFormatter:
    """新闻格式化器类"""
    
    # 分类名称映射
    CATEGORY_NAMES = {
        'domestic': '国内新闻',
        'international': '国际新闻',
        'finance': '财经新闻',
        'technology': '科技新闻',
        'sports': '体育新闻',
        'entertainment': '娱乐新闻',
        'general': '综合新闻'
    }
    
    # 历史上的今天数据（示例）
    HISTORY_EVENTS = [
        "1926年 - 日本漫画《铁臂阿童木》作者手冢治虫出生",
        "2003年 - 世界卫生组织宣布非典病原体为新型冠状病毒",
        "1969年 - 美国阿波罗11号宇宙飞船发射升空",
        "1990年 - - 中国与沙特阿拉伯建交",
        "2012年 - 伦敦奥运会开幕",
    ]
    
    # 今日名言（示例）
    QUOTES = [
        "人生苦短，及时行乐。—— 莎士比亚",
        "知识就是力量。—— 培根",
        "我思故我在。—— 笛卡尔",
        "生活不是等待风暴过去，而是学会在雨中跳舞。",
        "成功是1%的灵感加上99%的汗水。—— 爱迪生"
    ]
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化格式化器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.output_config = config.get('output', {})
    
    def format(self, news_data: Dict[str, List[NewsItem]], **kwargs) -> str:
        """
        格式化新闻数据
        
        Args:
            news_data: 新闻数据字典
            **kwargs: 格式化选项
            
        Returns:
            格式化后的字符串
        """
        format_type = kwargs.get('format', self.output_config.get('format', 'markdown'))
        
        if format_type == 'html':
            return self._format_html(news_data, **kwargs)
        elif format_type == 'text':
            return self._format_text(news_data, **kwargs)
        else:
            return self._format_markdown(news_data, **kwargs)
    
    def _format_markdown(self, news_data: Dict[str, List[NewsItem]], **kwargs) -> str:
        """
        格式化为Markdown
        
        Args:
            news_data: 新闻数据字典
            **kwargs: 格式化选项
            
        Returns:
            Markdown格式字符串
        """
        lines = []
        
        # 标题
        today = datetime.now()
        lines.append(f"# 每日新闻早报")
        lines.append(f"\n**{today.strftime('%Y年%m月%d日')} {self._get_weekday(today)}**\n")
        lines.append("-" * 60)
        
        # 天气信息
        if kwargs.get('include_weather', True) and self.output_config.get('include_weather', True):
            lines.extend(self._get_weather_section())
            lines.append("")
        
        # 今日要闻
        lines.extend(self._get_headlines_section(news_data))
        lines.append("")
        
        # 分类新闻
        lines.extend(self._get_categories_section(news_data))
        
        # 历史上的今天
        if kwargs.get('include_history', True) and self.output_config.get('include_history', True):
            lines.extend(self._get_history_section())
            lines.append("")
        
        # 今日名言
        if kwargs.get('include_quote', True) and self.output_config.get('include_quote', True):
            lines.extend(self._get_quote_section())
        
        # 页脚
        lines.append("")
        lines.append("---")
        lines.append(f"\n*本早报由每日新闻早报生成器自动生成 | 更新时间: {datetime.now().strftime('%H:%M:%S')}*")
        
        return '\n'.join(lines)
    
    def _format_html(self, news_data: Dict[str, List[NewsItem]], **kwargs) -> str:
        """
        格式化为HTML
        
        Args:
            news_data: 新闻数据字典
            **kwargs: 格式化选项
            
        Returns:
            HTML格式字符串
        """
        lines = []
        
        # HTML头部
        today = datetime.now()
        lines.append('<!DOCTYPE html>')
        lines.append('<html lang="zh-CN">')
        lines.append('<head>')
        lines.append('    <meta charset="UTF-8">')
        lines.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
        lines.append(f'    <title>每日新闻早报 - {today.strftime("%Y年%m月%d日")}</title>')
        lines.append('    <style>')
        lines.append('        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }')
        lines.append('        h1 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }')
        lines.append('        .date { color: #666; font-size: 14px; }')
        lines.append('        h2 { color: #007bff; margin-top: 30px; }')
        lines.append('        .news-item { margin-bottom: 15px; padding: 10px; background: #f8f9fa; border-radius: 5px; }')
        lines.append('        .news-title { font-weight: bold; color: #333; }')
        lines.append('        .news-desc { color: #666; font-size: 14px; margin-top: 5px; }')
        lines.append('        .news-source { color: #999; font-size: 12px; }')
        lines.append('        .weather { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; border-radius: 10px; margin: 20px 0; }')
        lines.append('        .quote { font-style: italic; color: #555; border-left: 4px solid #007bff; padding-left: 15px; margin: 20px 0; }')
        lines.append('        .history { background: #fff3cd; padding: 15px; border-radius: 5px; }')
        lines.append('        .footer { text-align: center; color: #999; font-size: 12px; margin-top: 30px; }')
        lines.append('        a { color: #007bff; text-decoration: none; }')
        lines.append('        a:hover { text-decoration: underline; }')
        lines.append('    </style>')
        lines.append('</head>')
        lines.append('<body>')
        
        # 标题
        lines.append(f'    <h1>每日新闻早报</h1>')
        lines.append(f'    <p class="date">{today.strftime("%Y年%m月%d日")} {self._get_weekday(today)}</p>')
        
        # 天气信息
        if kwargs.get('include_weather', True) and self.output_config.get('include_weather', True):
            lines.extend(self._get_weather_html())
        
        # 今日要闻
        lines.extend(self._get_headlines_html(news_data))
        
        # 分类新闻
        lines.extend(self._get_categories_html(news_data))
        
        # 历史上的今天
        if kwargs.get('include_history', True) and self.output_config.get('include_history', True):
            lines.extend(self._get_history_html())
        
        # 今日名言
        if kwargs.get('include_quote', True) and self.output_config.get('include_quote', True):
            lines.extend(self._get_quote_html())
        
        # 页脚
        lines.append('    <div class="footer">')
        lines.append(f'        <p>本早报由每日新闻早报生成器自动生成 | 更新时间: {datetime.now().strftime("%H:%M:%S")}</p>')
        lines.append('    </div>')
        lines.append('</body>')
        lines.append('</html>')
        
        return '\n'.join(lines)
    
    def _format_text(self, news_data: Dict[str, List[NewsItem]], **kwargs) -> str:
        """
        格式化为纯文本
        
        Args:
            news_data: 新闻数据字典
            **kwargs: 格式化选项
            
        Returns:
            纯文本格式字符串
        """
        lines = []
        
        # 标题
        today = datetime.now()
        lines.append("=" * 60)
        lines.append("              每 日 新 闻 早 报")
        lines.append("=" * 60)
        lines.append(f"\n{today.strftime('%Y年%m月%d日')} {self._get_weekday(today)}")
        lines.append("")
        
        # 天气信息
        if kwargs.get('include_weather', True) and self.output_config.get('include_weather', True):
            lines.extend(self._get_weather_text())
            lines.append("")
        
        # 今日要闻
        lines.extend(self._get_headlines_text(news_data))
        lines.append("")
        
        # 分类新闻
        lines.extend(self._get_categories_text(news_data))
        
        # 历史上的今天
        if kwargs.get('include_history', True) and self.output_config.get('include_history', True):
            lines.extend(self._get_history_text())
            lines.append("")
        
        # 今日名言
        if kwargs.get('include_quote', True) and self.output_config.get('include_quote', True):
            lines.extend(self._get_quote_text())
        
        # 页脚
        lines.append("")
        lines.append("=" * 60)
        lines.append(f"本早报由每日新闻早报生成器自动生成 | 更新时间: {datetime.now().strftime('%H:%M:%S')}")
        
        return '\n'.join(lines)
    
    def _get_weekday(self, dt: datetime) -> str:
        """获取星期几"""
        weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        return weekdays[dt.weekday()]
    
    def _get_weather_section(self) -> List[str]:
        """获取天气信息（Markdown）"""
        return [
            "## 今日天气",
            "",
            "多云转晴，16-24°C，适宜出行",
            "",
            "> 温馨提示：今日气温适宜，早晚温差较大，请注意增减衣物"
        ]
    
    def _get_weather_html(self) -> List[str]:
        """获取天气信息（HTML）"""
        return [
            '    <div class="weather">',
            '        <h3>今日天气</h3>',
            '        <p>多云转晴，16-24°C，适宜出行</p>',
            '        <p><em>温馨提示：今日气温适宜，早晚温差较大，请注意增减衣物</em></p>',
            '    </div>'
        ]
    
    def _get_weather_text(self) -> List[str]:
        """获取天气信息（纯文本）"""
        return [
            "【今日天气】",
            "多云转晴，16-24°C，适宜出行",
            "温馨提示：今日气温适宜，早晚温差较大，请注意增减衣物"
        ]
    
    def _get_headlines_section(self, news_data: Dict[str, List[NewsItem]]) -> List[str]:
        """获取今日要闻（Markdown）"""
        lines = ["## 今日要闻", ""]
        
        # 从各个分类中选取重要新闻
        headlines = []
        for category, items in news_data.items():
            headlines.extend(items[:2])  # 每个分类取2条
        
        # 取前5条作为要闻
        headlines = headlines[:5]
        
        for i, item in enumerate(headlines, 1):
            lines.append(f"{i}. **{item.title}**")
            if item.description:
                lines.append(f"   {item.description}")
            lines.append(f"   来源：{item.source}")
            lines.append("")
        
        return lines
    
    def _get_headlines_html(self, news_data: Dict[str, List[NewsItem]]) -> List[str]:
        """获取今日要闻（HTML）"""
        lines = ['    <h2>今日要闻</h2>']
        
        headlines = []
        for category, items in news_data.items():
            headlines.extend(items[:2])
        headlines = headlines[:5]
        
        for i, item in enumerate(headlines, 1):
            lines.append(f'    <div class="news-item">')
            lines.append(f'        <div class="news-title">{i}. <a href="{item.link}" target="_blank">{item.title}</a></div>')
            if item.description:
                lines.append(f'        <div class="news-desc">{item.description}</div>')
            lines.append(f'        <div class="news-source">来源：{item.source}</div>')
            lines.append('    </div>')
        
        return lines
    
    def _get_headlines_text(self, news_data: Dict[str, List[NewsItem]]) -> List[str]:
        """获取今日要闻（纯文本）"""
        lines = ["【今日要闻】", ""]
        
        headlines = []
        for category, items in news_data.items():
            headlines.extend(items[:2])
        headlines = headlines[:5]
        
        for i, item in enumerate(headlines, 1):
            lines.append(f"{i}. {item.title}")
            if item.description:
                lines.append(f"   {item.description}")
            lines.append(f"   来源：{item.source}")
            lines.append("")
        
        return lines
    
    def _get_categories_section(self, news_data: Dict[str, List[NewsItem]]) -> List[str]:
        """获取分类新闻（Markdown）"""
        lines = ["## 分类新闻", ""]
        
        for category, items in news_data.items():
            if not items:
                continue
            
            category_name = self.CATEGORY_NAMES.get(category, category)
            lines.append(f"### {category_name}")
            lines.append("")
            
            for item in items[:5]:
                lines.append(f"- [{item.title}]({item.link})")
                if item.description:
                    lines.append(f"  {item.description}")
                lines.append("")
            
            lines.append("")
        
        return lines
    
    def _get_categories_html(self, news_data: Dict[str, List[NewsItem]]) -> List[str]:
        """获取分类新闻（HTML）"""
        lines = ['    <h2>分类新闻</h2>']
        
        for category, items in news_data.items():
            if not items:
                continue
            
            category_name = self.CATEGORY_NAMES.get(category, category)
            lines.append(f'    <h3>{category_name}</h3>')
            
            for item in items[:5]:
                lines.append('    <div class="news-item">')
                lines.append(f'        <div class="news-title"><a href="{item.link}" target="_blank">{item.title}</a></div>')
                if item.description:
                    lines.append(f'        <div class="news-desc">{item.description}</div>')
                lines.append('    </div>')
        
        return lines
    
    def _get_categories_text(self, news_data: Dict[str, List[NewsItem]]) -> List[str]:
        """获取分类新闻（纯文本）"""
        lines = ["【分类新闻】", ""]
        
        for category, items in news_data.items():
            if not items:
                continue
            
            category_name = self.CATEGORY_NAMES.get(category, category)
            lines.append(f"--- {category_name} ---")
            
            for i, item in enumerate(items[:5], 1):
                lines.append(f"{i}. {item.title}")
                if item.description:
                    lines.append(f"   {item.description}")
                lines.append("")
            
            lines.append("")
        
        return lines
    
    def _get_history_section(self) -> List[str]:
        """获取历史上的今天（Markdown）"""
        lines = ["## 历史上的今天", ""]
        for event in self.HISTORY_EVENTS[:3]:
            lines.append(f"- {event}")
        lines.append("")
        return lines
    
    def _get_history_html(self) -> List[str]:
        """获取历史上的今天（HTML）"""
        lines = ['    <h2>历史上的今天</h2>']
        lines.append('    <div class="history">')
        for event in self.HISTORY_EVENTS[:3]:
            lines.append(f'        <p>{event}</p>')
        lines.append('    </div>')
        return lines
    
    def _get_history_text(self) -> List[str]:
        """获取历史上的今天（纯文本）"""
        lines = ["【历史上的今天】"]
        for event in self.HISTORY_EVENTS[:3]:
            lines.append(f"- {event}")
        lines.append("")
        return lines
    
    def _get_quote_section(self) -> List[str]:
        """获取今日名言（Markdown）"""
        quote = self.QUOTES[datetime.now().day % len(self.QUOTES)]
        return [
            "## 今日名言",
            "",
            f"> {quote}",
            ""
        ]
    
    def _get_quote_html(self) -> List[str]:
        """获取今日名言（HTML）"""
        quote = self.QUOTES[datetime.now().day % len(self.QUOTES)]
        return [
            '    <h2>今日名言</h2>',
            f'    <div class="quote"><p>{quote}</p></div>'
        ]
    
    def _get_quote_text(self) -> List[str]:
        """获取今日名言（纯文本）"""
        quote = self.QUOTES[datetime.now().day % len(self.QUOTES)]
        return [
            "【今日名言】",
            f'"{quote}"'
        ]
