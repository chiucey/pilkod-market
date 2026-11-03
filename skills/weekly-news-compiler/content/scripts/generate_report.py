#!/usr/bin/env python3
"""
Weekly News Report Generator
Generates an HTML news report from collected news data
"""
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

class NewsReportGenerator:
    """Generate weekly news HTML report"""

    def __init__(self, template_path: str = None):
        self.template_path = template_path or "assets/report_template.html"
        self.section_icons = {
            "国内外热点": "🌍",
            "宏观经济": "📈",
            "金融": "💰",
            "股市": "📊",
            "楼市": "🏠",
            "产业": "🏭"
        }

    def load_template(self) -> str:
        """Load HTML template"""
        template_file = Path(__file__).parent.parent / self.template_path
        if template_file.exists():
            return template_file.read_text(encoding="utf-8")
        return self._get_default_template()

    def _get_default_template(self) -> str:
        """Get default template if file not found"""
        return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{{title}}</title>
    <style>{{css}}</style>
</head>
<body>{{content}}</body>
</html>'''

    def load_news_data(self, data_path: str) -> List[Dict[str, Any]]:
        """Load news data from JSON file"""
        data_file = Path(data_path)
        if data_file.exists():
            return json.loads(data_file.read_text(encoding="utf-8"))
        return []

    def generate_report(self, news_data: List[Dict[str, Any]], output_path: str = None) -> str:
        """Generate HTML report from news data"""
        template = self.load_template()

        # Calculate date range (last 7 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        date_range = f"{start_date.strftime('%Y年%m月%d日')} - {end_date.strftime('%Y年%m月%d日')}"

        # Group news by category
        categories = self._group_by_category(news_data)

        # Build content
        content = self._build_content(categories)

        # Build navigation
        navigation = self._build_navigation(categories)

        # Build summary stats
        summary_stats = self._build_summary_stats(categories)

        # Count unique sources
        sources = set()
        for news in news_data:
            if 'source' in news:
                sources.add(news['source'])

        # Replace placeholders
        html = template.replace('{{title}}', '每周资讯整合报告')
        html = html.replace('{{subtitle}}', '全方位资讯聚合 · 决策参考')
        html = html.replace('{{date_range}}', date_range)
        html = html.replace('{{total_count}}', str(len(news_data)))
        html = html.replace('{{source_count}}', str(len(sources)))
        html = html.replace('{{navigation}}', navigation)
        html = html.replace('{{summary_stats}}', summary_stats)
        html = html.replace('{{content}}', content)
        html = html.replace('{{generate_time}}', datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'))
        html = html.replace('{{sources}}', '、'.join(list(sources)[:5]) + ('等' if len(sources) > 5 else ''))

        # Save if output path provided
        if output_path:
            Path(output_path).write_text(html, encoding="utf-8")

        return html

    def _group_by_category(self, news_data: List[Dict]) -> Dict[str, Any]:
        """Group news by category and subsection"""
        categories = {}

        category_order = [
            ("国内外热点", None),
            ("宏观经济", "国际层面"),
            ("宏观经济", "国内层面"),
            ("宏观经济", "地方层面"),
            ("金融", None),
            ("股市", None),
            ("楼市", None),
            ("产业", "车辆设备"),
            ("产业", "新质生产力"),
            ("产业", "热门产业"),
        ]

        for main_cat, sub_cat in category_order:
            key = f"{main_cat}_{sub_cat}" if sub_cat else main_cat
            categories[key] = {
                "main": main_cat,
                "sub": sub_cat,
                "news": []
            }

        for news in news_data:
            main = news.get('category', '其他')
            sub = news.get('subsection', None)
            key = f"{main}_{sub}" if sub else main

            if key in categories:
                categories[key]['news'].append(news)
            else:
                # Fallback to main category
                if main in [c[0] for c in category_order]:
                    categories[main]['news'].append(news)

        return categories

    def _build_navigation(self, categories: Dict) -> str:
        """Build navigation HTML"""
        nav_items = []
        section_num = 1

        for key, data in categories.items():
            if data['news']:
                title = data['sub'] if data['sub'] else data['main']
                nav_items.append(
                    f'<a href="#section-{section_num}" class="nav-item">'
                    f'<span class="num">{section_num}</span>{title}'
                    f'</a>'
                )
                section_num += 1

        return '\n'.join(nav_items)

    def _build_summary_stats(self, categories: Dict) -> str:
        """Build summary statistics HTML"""
        stats = []
        for key, data in categories.items():
            if data['news']:
                title = data['sub'] if data['sub'] else data['main']
                icon = self.section_icons.get(data['main'], '📋')
                stats.append(
                    f'<div class="summary-stat">'
                    f'<div class="number">{len(data["news"])}</div>'
                    f'<div class="text">{icon} {title}</div>'
                    f'</div>'
                )
        return '\n'.join(stats)

    def _build_content(self, categories: Dict) -> str:
        """Build main content HTML"""
        sections = []
        section_num = 1

        for key, data in categories.items():
            if not data['news']:
                continue

            icon = self.section_icons.get(data['main'], '📋')

            if data['sub']:
                # Subsection within a section
                if sections:
                    # Add to last section
                    sections[-1] = sections[-1][:-6] + self._build_subsection(data, section_num, icon) + '\n        </div>\n    </div>'
            else:
                # Main section
                section_html = self._build_section(data, section_num, icon)
                sections.append(section_html)
                section_num += 1

        return '\n'.join(sections)

    def _build_section(self, data: Dict, num: int, icon: str) -> str:
        """Build section HTML"""
        news_items = self._build_news_items(data['news'])

        return f'''
        <section class="section" id="section-{num}">
            <div class="section-header">
                <h2><span class="icon">{icon}</span>{data['main']}</h2>
                <span class="news-count">{len(data['news'])} 条</span>
            </div>
            <div class="subsection">
                <div class="subsection-header">📋 {data['main']}要闻</div>
                <div class="news-list">
                    {news_items}
                </div>
            </div>
        </section>'''

    def _build_subsection(self, data: Dict, num: int, icon: str) -> str:
        """Build subsection HTML (appended to existing section)"""
        news_items = self._build_news_items(data['news'])

        return f'''
                <div class="subsection-header">📋 {data['sub']}</div>
                <div class="news-list">
                    {news_items}
                </div>
            </div>'''

    def _build_news_items(self, news_list: List[Dict]) -> str:
        """Build news items HTML"""
        items = []
        for news in news_list:
            title = news.get('title', '无标题')
            summary = news.get('summary', '')
            source = news.get('source', '未知来源')
            time = news.get('publishTime', '')
            impact = news.get('impact', '中性')
            url = news.get('url', '#')

            impact_class = 'bullish' if impact in ['利好', '利好'] else ('bearish' if impact in ['利空', '利空'] else 'neutral')
            impact_text = '📈 利好' if impact in ['利好'] else ('📉 利空' if impact in ['利空'] else '➡️ 中性')

            item = f'''
                    <div class="news-item">
                        <div class="news-content">
                            <h3 class="news-title"><a href="{url}" target="_blank">{title}</a></h3>
                            <p class="news-summary">{summary}</p>
                            <div class="news-meta">
                                <span class="meta-tag time">🕐 {time}</span>
                                <span class="meta-tag source">📰 {source}</span>
                                <span class="meta-tag impact {impact_class}">{impact_text}</span>
                            </div>
                        </div>
                    </div>'''
            items.append(item)

        return '\n'.join(items)


def main():
    """Main entry point for testing"""
    generator = NewsReportGenerator()

    # Sample data for testing
    sample_news = [
        {
            "title": "中美经贸高层举行视频通话",
            "summary": "双方就经贸问题深入交换意见，达成多项共识",
            "source": "新华社",
            "publishTime": "2024-04-13",
            "impact": "利好",
            "category": "国内外热点",
            "url": "#"
        },
        {
            "title": "央行宣布降准0.25个百分点",
            "summary": "释放长期资金约5000亿元，支持实体经济发展",
            "source": "中国人民银行",
            "publishTime": "2024-04-12",
            "impact": "利好",
            "category": "金融",
            "url": "#"
        },
        {
            "title": "A股三大指数集体上涨",
            "summary": "沪指涨1.5%，深成指涨2%，创业板指涨3%",
            "source": "证券时报",
            "publishTime": "2024-04-13",
            "impact": "利好",
            "category": "股市",
            "url": "#"
        },
    ]

    html = generator.generate_report(sample_news)

    # Save to file
    output_path = Path(__file__).parent.parent / "test_report.html"
    output_path.write_text(html, encoding="utf-8")
    print(f"Report generated: {output_path}")


if __name__ == "__main__":
    main()
