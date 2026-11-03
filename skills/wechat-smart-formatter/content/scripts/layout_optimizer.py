#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号配图 - 布局优化与文章格式化模块
智能分析文章结构，优化图文布局，支持自定义Logo嵌入
Author: MiniMax Agent
Version: 1.0.0
"""

import os
import re
import json
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ColorScheme(Enum):
    """配色方案枚举"""
    BUSINESS = "business"       # 经典商务 - 专业稳重
    WARM = "warm"               # 温暖人文 - 情感共鸣
    NATURE = "nature"           # 清新自然 - 森系风格
    MINIMAL = "minimal"         # 极简黑白 - 纯粹专业
    ENERGETIC = "energetic"     # 活力橙黄 - 温暖活力
    VINTAGE = "vintage"         # 文艺复古 - 咖啡书香


@dataclass
class ArticleContent:
    """文章内容结构"""
    title: str
    subtitle: Optional[str] = None
    author: Optional[str] = None
    paragraphs: List[str] = None
    headings: List[Dict] = None  # [{level: int, text: str}]
    images: List[Dict] = None    # [{src: str, caption: str, position: int}]
    quotes: List[str] = None
    code_blocks: List[Dict] = None

    def __post_init__(self):
        if self.paragraphs is None:
            self.paragraphs = []
        if self.headings is None:
            self.headings = []
        if self.images is None:
            self.images = []
        if self.quotes is None:
            self.quotes = []
        if self.code_blocks is None:
            self.code_blocks = []


@dataclass
class LayoutConfig:
    """布局配置"""
    color_scheme: ColorScheme = ColorScheme.BUSINESS
    logo_path: Optional[str] = None
    logo_position: str = "bottom-right"  # top-right, bottom-left, bottom-right
    logo_opacity: float = 0.85
    cover_image: Optional[str] = None
    author_info: Optional[str] = None
    show_qr_code: bool = False


class ArticleParser:
    """文章解析器 - 将文本解析为结构化内容"""

    @staticmethod
    def parse_text(text: str) -> ArticleContent:
        """
        解析文本为文章结构

        Args:
            text: 原始文本

        Returns:
            ArticleContent对象
        """
        lines = text.strip().split('\n')

        content = ArticleContent(
            title="",
            paragraphs=[],
            headings=[],
            images=[],
            quotes=[],
            code_blocks=[]
        )

        current_paragraph = []
        in_code_block = False
        code_content = []
        code_lang = ""

        for line in lines:
            stripped = line.strip()

            # 空行处理
            if not stripped:
                if current_paragraph:
                    content.paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = []
                continue

            # 代码块
            if stripped.startswith('```'):
                if not in_code_block:
                    in_code_block = True
                    code_lang = stripped[3:].strip()
                    code_content = []
                else:
                    in_code_block = False
                    content.code_blocks.append({
                        "language": code_lang,
                        "content": '\n'.join(code_content)
                    })
                    code_content = []
                continue

            if in_code_block:
                code_content.append(line)
                continue

            # 标题检测
            if stripped.startswith('#'):
                # 先保存当前段落
                if current_paragraph:
                    content.paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = []

                level = len(stripped) - len(stripped.lstrip('#'))
                heading_text = stripped.lstrip('#').strip()

                if level == 1 and not content.title:
                    content.title = heading_text
                else:
                    content.headings.append({
                        "level": level,
                        "text": heading_text
                    })
                continue

            # 引用块
            if stripped.startswith('>'):
                if current_paragraph:
                    content.paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = []
                quote_text = stripped.lstrip('>').strip()
                content.quotes.append(quote_text)
                continue

            # 图片
            img_match = re.match(r'!\[(.*?)\]\((.*?)\)', stripped)
            if img_match:
                if current_paragraph:
                    content.paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = []
                caption, src = img_match.groups()
                content.images.append({
                    "src": src,
                    "caption": caption,
                    "position": len(content.paragraphs)
                })
                continue

            # 普通段落
            current_paragraph.append(stripped)

        # 处理最后一段
        if current_paragraph:
            content.paragraphs.append(' '.join(current_paragraph))

        return content


class LayoutOptimizer:
    """布局优化器 - 智能安排图文比例和位置"""

    # 微信公众号推荐尺寸
    WECHAT_WIDTH = 900  # 推荐宽度
    COVER_HEIGHT_RATIO = 0.42  # 封面图高度比例 (383/900)
    INLINE_IMAGE_RATIO = 0.67  # 文内图推荐比例 (600/900)

    @staticmethod
    def calculate_image_layout(
        image_count: int,
        total_paragraphs: int
    ) -> List[Dict]:
        """
        计算图片布局策略

        Args:
            image_count: 图片数量
            total_paragraphs: 段落数量

        Returns:
            布局方案列表
        """
        if image_count == 0:
            return []

        layouts = []

        # 单图布局：居中展示
        if image_count == 1:
            return [{
                "type": "single-center",
                "position": "center",
                "caption": True
            }]

        # 双图布局：左右分栏
        if image_count == 2:
            return [
                {"type": "left-right", "position": 0},
                {"type": "left-right", "position": 1}
            ]

        # 多图布局：网格或瀑布流
        if image_count <= 4:
            return [
                {"type": "grid", "columns": 2, "position": i}
                for i in range(image_count)
            ]

        # 大于4张图：使用混合布局
        layouts = [
            {"type": "full-width", "position": 0}
        ]
        remaining = image_count - 1
        if remaining >= 2:
            layouts.extend([
                {"type": "grid", "columns": 2, "position": i + 1}
                for i in range(remaining)
            ])

        return layouts

    @staticmethod
    def determine_optimal_positions(
        image_count: int,
        total_paragraphs: int
    ) -> List[int]:
        """
        确定图片最佳插入位置

        Args:
            image_count: 图片数量
            total_paragraphs: 段落数量

        Returns:
            插入位置列表
        """
        if image_count == 0 or total_paragraphs == 0:
            return []

        # 根据段落数均分图片
        positions = []
        step = total_paragraphs / (image_count + 1)

        for i in range(image_count):
            position = int(step * (i + 1))
            positions.append(min(position, total_paragraphs - 1))

        return positions


class HTMLGenerator:
    """HTML生成器 - 生成微信公众号兼容的HTML"""

    # 基础CSS模板
    BASE_CSS = """
    .wechat-article {
        font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
        font-size: 15px;
        line-height: 1.9;
        color: #2D3436;
        max-width: 100%;
        margin: 0 auto;
        padding: 15px;
    }
    """

    @staticmethod
    def generate_article_html(
        content: ArticleContent,
        config: LayoutConfig,
        images: List[Dict] = None
    ) -> str:
        """
        生成文章HTML

        Args:
            content: 文章内容
            config: 布局配置
            images: 图片数据 [{url, local_path, caption, layout}]

        Returns:
            HTML字符串
        """
        images = images or []
        image_index = 0

        html_parts = []

        # 开始文章容器
        scheme_class = f"scheme-{config.color_scheme.value}"
        html_parts.append(f'<div class="wechat-article {scheme_class}">')

        # 封面图
        if config.cover_image:
            html_parts.append(HTMLGenerator._generate_cover(
                config.cover_image,
                config.logo_path,
                config.logo_position,
                config.logo_opacity
            ))

        # 标题
        if content.title:
            html_parts.append(f'<h1 class="article-title">{content.title}</h1>')

        # 副标题
        if content.subtitle:
            html_parts.append(f'<p class="article-subtitle">{content.subtitle}</p>')

        # 正文
        html_parts.append('<div class="article-body">')

        for i, para in enumerate(content.paragraphs):
            # 检查是否有图片插入点
            positions = LayoutOptimizer.determine_optimal_positions(
                len(images), len(content.paragraphs)
            )

            # 插入图片
            while image_index < len(images) and positions and i == positions[image_index]:
                img = images[image_index]
                html_parts.append(HTMLGenerator._generate_image_figure(img))
                image_index += 1

            # 段落
            html_parts.append(f'<p>{para}</p>')

        # 处理剩余图片
        while image_index < len(images):
            html_parts.append(HTMLGenerator._generate_image_figure(images[image_index]))
            image_index += 1

        # 引用块
        for quote in content.quotes:
            html_parts.append(f'<blockquote><p>{quote}</p></blockquote>')

        # 代码块
        for code in content.code_blocks:
            html_parts.append(HTMLGenerator._generate_code_block(code))

        html_parts.append('</div>')  # article-body

        # 底部签名
        if config.author_info:
            html_parts.append(HTMLGenerator._generate_footer(config.author_info))

        html_parts.append('</div>')  # wechat-article

        return '\n'.join(html_parts)

    @staticmethod
    def _generate_cover(
        cover_url: str,
        logo_path: Optional[str] = None,
        logo_position: str = "bottom-right",
        logo_opacity: float = 0.85
    ) -> str:
        """生成封面HTML"""
        parts = [
            '<figure class="cover-image-container">',
            f'<img class="cover-image" src="{cover_url}" alt="封面图">'
        ]

        if logo_path:
            parts.append(
                f'<img class="logo-overlay position-{logo_position}" '
                f'src="{logo_path}" '
                f'style="opacity: {logo_opacity};" '
                f'alt="Logo">'
            )

        parts.append('</figure>')
        return '\n'.join(parts)

    @staticmethod
    def _generate_image_figure(image: Dict) -> str:
        """生成图片figure HTML"""
        layout_class = image.get('layout', 'center')
        caption = image.get('caption', '')

        parts = [
            f'<figure class="layout-{layout_class}">',
            f'<img src="{image["url"]}" alt="{caption}">'
        ]

        if caption:
            parts.append(f'<figcaption>{caption}</figcaption>')

        parts.append('</figure>')

        return '\n'.join(parts)

    @staticmethod
    def _generate_code_block(code: Dict) -> str:
        """生成代码块HTML"""
        lang = code.get('language', '')
        content = code.get('content', '')

        return (
            f'<pre><code class="language-{lang}">'
            f'{content}'
            f'</code></pre>'
        )

    @staticmethod
    def _generate_footer(author_info: str) -> str:
        """生成底部签名HTML"""
        return f'''
        <footer class="article-footer">
            <div class="author-info">{author_info}</div>
        </footer>
        '''


class WeChatArticleFormatter:
    """微信公众号文章格式化器 - 主控制器"""

    def __init__(self, config: Optional[Dict] = None):
        """
        初始化格式化器

        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.parser = ArticleParser()
        self.layout_optimizer = LayoutOptimizer()
        self.html_generator = HTMLGenerator()

        # 加载配色方案
        color_scheme = self.config.get('color_scheme', 'business')
        try:
            self.default_scheme = ColorScheme(color_scheme)
        except ValueError:
            self.default_scheme = ColorScheme.BUSINESS

    def format_article(
        self,
        text: str,
        images: List[Dict] = None,
        custom_config: Optional[LayoutConfig] = None
    ) -> Dict:
        """
        格式化文章

        Args:
            text: 文章文本
            images: 图片列表
            custom_config: 自定义配置

        Returns:
            {
                "html": str,          # 生成的HTML
                "content": ArticleContent,
                "layout_info": Dict,  # 布局信息
                "message": str        # 提示信息
            }
        """
        try:
            # 解析文章
            content = self.parser.parse_text(text)

            if not content.title:
                # 尝试从第一行提取标题
                lines = text.strip().split('\n')
                if lines:
                    content.title = lines[0][:50]
                    if len(lines) > 1:
                        content.paragraphs.insert(0, lines[1])

            # 创建布局配置
            config = custom_config or LayoutConfig(
                color_scheme=self.default_scheme,
                logo_path=self.config.get('logo_path'),
                author_info=self.config.get('author_info')
            )

            # 计算图片布局
            layout_info = {
                "image_count": len(images) if images else 0,
                "paragraph_count": len(content.paragraphs),
                "layout_strategy": self.layout_optimizer.calculate_image_layout(
                    len(images) if images else 0,
                    len(content.paragraphs)
                ),
                "insertion_points": self.layout_optimizer.determine_optimal_positions(
                    len(images) if images else 0,
                    len(content.paragraphs)
                )
            }

            # 生成HTML
            html = self.html_generator.generate_article_html(
                content,
                config,
                images
            )

            return {
                "success": True,
                "html": html,
                "content": content,
                "layout_info": layout_info,
                "message": "文章格式化成功"
            }

        except Exception as e:
            logger.error(f"格式化失败: {e}")
            return {
                "success": False,
                "html": "",
                "content": None,
                "layout_info": {},
                "message": f"格式化失败: {str(e)}"
            }

    def auto_detect_color_scheme(self, text: str) -> ColorScheme:
        """
        根据文章内容自动检测配色方案

        Args:
            text: 文章文本

        Returns:
            推荐的配色方案
        """
        text_lower = text.lower()

        # 温暖人文关键词
        warm_keywords = ['情感', '生活', '随笔', '回忆', '心情', '感悟', '温暖', '爱情', '亲情', '友情']
        if any(kw in text_lower for kw in warm_keywords):
            return ColorScheme.WARM

        # 自然关键词
        nature_keywords = ['自然', '旅行', '风景', '环保', '生态', '户外', '森林', '山水', '天空', '大海']
        if any(kw in text_lower for kw in nature_keywords):
            return ColorScheme.NATURE

        # 活力关键词
        energetic_keywords = ['活动', '促销', '优惠', '福利', '抽奖', '庆祝', '节日', '派对']
        if any(kw in text_lower for kw in energetic_keywords):
            return ColorScheme.ENERGETIC

        # 文艺关键词
        vintage_keywords = ['书评', '影评', '文艺', '复古', '经典', '文学', '艺术', '咖啡']
        if any(kw in text_lower for kw in vintage_keywords):
            return ColorScheme.VINTAGE

        # 科技/评测类使用极简黑白
        tech_keywords = ['评测', '技术', '教程', '代码', '分析', '对比', '专业']
        if any(kw in text_lower for kw in tech_keywords):
            return ColorScheme.MINIMAL

        # 默认商务
        return ColorScheme.BUSINESS


# 演示和测试
if __name__ == "__main__":
    # 测试代码
    formatter = WeChatArticleFormatter()

    test_text = """
# 微信文章测试

这是一个测试文章。

## 第一部分

这里是正文内容。

> 这是一个引用块

### 子标题

更多内容...

```

def hello():
    print("Hello World!")

```
"""

    result = formatter.format_article(test_text)
    print(f"格式化结果: {result['message']}")
    print(f"布局信息: {json.dumps(result['layout_info'], indent=2)}")
    print(f"HTML长度: {len(result['html'])} 字符")
