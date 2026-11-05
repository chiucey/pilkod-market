#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号配图 - 主文章生成器
整合所有模块，提供一站式公众号文章排版配图服务
Author: MiniMax Agent
Version: 1.0.0

功能说明：
1. 智能配图系统
   - 优先搜索 Unsplash/Pexels 版权免费图片
   - 自动使用 AI 生成图片
   - 支持本地 Stable Diffusion 接口
   - 智能去水印处理

2. 高级排版系统
   - 6种高级配色方案（拒绝蓝紫配色）
   - 自动适配文章内容风格
   - 支持 Logo 嵌入
   - 智能图文混排

3. 输出格式
   - HTML 代码（可直接粘贴到公众号编辑器）
   - Markdown 源文件备份
"""

import os
import sys
import json
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from image_search import ImageSearcher, extract_keywords_from_text
from watermark_removal import SmartWatermarkCleaner
from ai_image_generator import SmartImageGenerator
from layout_optimizer import (
    WeChatArticleFormatter,
    LayoutConfig,
    ColorScheme,
    ArticleContent
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class GenerationConfig:
    """生成配置"""
    # 图片搜索配置
    search_provider: str = "auto"  # unsplash / pexels / auto
    search_count: int = 10
    exclude_watermarked: bool = True

    # AI生图配置
    ai_generation_enabled: bool = True
    preferred_ai_method: str = "minimax"  # minimax / local_sd / auto

    # 本地SD配置
    local_sd_enabled: bool = False
    local_sd_url: str = "http://localhost:7860"
    local_sd_model: str = "AnythingV5"

    # 水印处理
    watermark_removal_enabled: bool = True
    watermark_strength: str = "medium"  # low / medium / high

    # 排版配置
    color_scheme: str = "auto"  # auto / business / warm / nature / minimal / energetic / vintage
    logo_path: Optional[str] = None
    logo_position: str = "bottom-right"  # top-right / bottom-left / bottom-right
    author_info: Optional[str] = None

    # 输出配置
    output_format: str = "html"  # html / markdown / both
    css_inline: bool = True


class WeChatArticleGenerator:
    """微信公众号文章生成器 - 主控制器"""

    def __init__(self, config: Optional[GenerationConfig] = None):
        """
        初始化生成器

        Args:
            config: 生成配置
        """
        self.config = config or GenerationConfig()

        # 初始化各模块
        self.image_searcher = ImageSearcher()
        self.watermark_cleaner = SmartWatermarkCleaner()
        self.ai_generator = SmartImageGenerator(self._get_ai_config())
        self.article_formatter = WeChatArticleFormatter(self._get_formatter_config())

    def _get_ai_config(self) -> Dict:
        """获取AI生图配置"""
        return {
            "minimax_api_key": os.getenv("MINIMAX_API_KEY"),
            "local_sd_url": self.config.local_sd_url if self.config.local_sd_enabled else None,
            "local_sd_model": self.config.local_sd_model
        }

    def _get_formatter_config(self) -> Dict:
        """获取格式化器配置"""
        return {
            "color_scheme": self.config.color_scheme,
            "logo_path": self.config.logo_path,
            "author_info": self.config.author_info
        }

    def generate_article(
        self,
        text: str,
        title: Optional[str] = None,
        custom_config: Optional[GenerationConfig] = None
    ) -> Dict:
        """
        生成完整文章

        Args:
            text: 文章文本内容
            title: 文章标题（可选，自动从内容提取）
            custom_config: 自定义配置

        Returns:
            {
                "success": bool,
                "html": str,           # 生成的HTML代码
                "markdown": str,       # Markdown源文件
                "images": List[Dict],  # 使用的图片信息
                "message": str,        # 提示信息
                "stats": Dict          # 统计信息
            }
        """
        config = custom_config or self.config
        result = {
            "success": False,
            "html": "",
            "markdown": text,
            "images": [],
            "message": "",
            "stats": {}
        }

        try:
            # 步骤1：内容分析
            logger.info("步骤1：分析文章内容...")
            keywords = extract_keywords_from_text(text, max_keywords=5)
            article_title = title or keywords[0] if keywords else "未命名文章"

            # 自动检测配色方案
            if config.color_scheme == "auto":
                detected_scheme = self.article_formatter.auto_detect_color_scheme(text)
                color_scheme_name = detected_scheme.value
                logger.info(f"自动检测配色方案：{color_scheme_name}")
            else:
                color_scheme_name = config.color_scheme

            # 步骤2：图片处理
            logger.info("步骤2：搜索和生成配图...")
            images = self._process_images(keywords, article_title, config)

            # 步骤3：格式化文章
            logger.info("步骤3：生成排版HTML...")

            layout_config = LayoutConfig(
                color_scheme=ColorScheme(color_scheme_name),
                logo_path=config.logo_path,
                logo_position=config.logo_position,
                cover_image=images[0]["url"] if images else None,
                author_info=config.author_info
            )

            format_result = self.article_formatter.format_article(
                text,
                images=images[1:] if len(images) > 1 else [],  # 封面用第一张
                custom_config=layout_config
            )

            if not format_result["success"]:
                return {
                    **result,
                    "message": f"格式化失败：{format_result['message']}"
                }

            # 步骤4：生成最终HTML
            final_html = self._wrap_html(format_result["html"], color_scheme_name)

            result = {
                "success": True,
                "html": final_html,
                "markdown": self._generate_markdown(text, images),
                "images": images,
                "message": "文章生成成功！可直接粘贴HTML到公众号编辑器",
                "stats": {
                    "image_count": len(images),
                    "keywords": keywords,
                    "color_scheme": color_scheme_name,
                    "paragraph_count": format_result["layout_info"].get("paragraph_count", 0),
                    "layout_strategy": format_result["layout_info"].get("layout_strategy", [])
                }
            }

            logger.info(f"生成完成：{len(images)}张图片，{color_scheme_name}配色")

        except Exception as e:
            logger.error(f"生成失败：{e}")
            result["message"] = f"生成失败：{str(e)}"

        return result

    def _process_images(
        self,
        keywords: List[str],
        title: str,
        config: GenerationConfig
    ) -> List[Dict]:
        """
        处理图片：搜索、去水印、生成

        Args:
            keywords: 关键词列表
            title: 文章标题
            config: 配置

        Returns:
            处理后的图片列表
        """
        processed_images = []

        # 策略：生成 3-5 张图片
        target_count = min(max(3, len(keywords)), 5)

        # 构建搜索关键词
        search_keywords_list = []
        for i in range(target_count):
            if i < len(keywords):
                search_keywords_list.append(keywords)
            else:
                search_keywords_list.append(keywords[:2])

        # 步骤2.1：搜索版权图片
        logger.info("搜索版权免费图片...")
        search_results = []

        try:
            search_results = self.image_searcher.search_images(
                keywords=keywords,
                count=target_count * 2,  # 多搜一些备选
                orientation="landscape",
                exclude_watermarked=config.exclude_watermarked
            )
            logger.info(f"搜索到 {len(search_results)} 张图片")
        except Exception as e:
            logger.warning(f"图片搜索失败：{e}")

        # 步骤2.2：处理搜索到的图片
        for i, img in enumerate(search_results[:target_count]):
            image_info = {
                "url": img["url"],
                "source": img.get("source", "unknown"),
                "photographer": img.get("photographer", ""),
                "license": img.get("license", ""),
                "caption": f"配图{i+1}",
                "layout": "center",
                "watermark_status": "clean"
            }

            # 如果配置了去水印且检测到水印
            if config.watermark_removal_enabled and img.get("is_watermarked", False):
                image_info["watermark_status"] = "needs_removal"

            processed_images.append(image_info)

        # 步骤2.3：如果图片不够，用AI生成
        if len(processed_images) < target_count and config.ai_generation_enabled:
            remaining = target_count - len(processed_images)
            logger.info(f"使用AI生成 {remaining} 张图片...")

            for i in range(remaining):
                try:
                    prompt = self._build_image_prompt(
                        title,
                        keywords,
                        i,
                        len(processed_images)
                    )

                    # 使用AI生成
                    gen_result = self.ai_generator.generate_image(
                        prompt=prompt,
                        preferred_method=config.preferred_ai_method
                    )

                    if gen_result["success"]:
                        processed_images.append({
                            "url": gen_result["image_path"],
                            "source": "ai_generated",
                            "prompt": prompt,
                            "caption": f"AI生成配图{i+1}",
                            "layout": "center",
                            "watermark_status": "clean"
                        })
                        logger.info(f"AI生成成功：{prompt[:50]}...")

                except Exception as e:
                    logger.warning(f"AI生成失败：{e}")

        return processed_images

    def _build_image_prompt(
        self,
        title: str,
        keywords: List[str],
        index: int,
        existing_count: int
    ) -> str:
        """构建图片生成提示词"""
        keyword_str = ", ".join(keywords[:3])

        # 根据位置生成不同类型的图片
        if index == 0:
            # 封面图：大气、主题明确
            prompt = f"{title}, {keyword_str}, clean composition, atmospheric, professional photography, suitable for cover"
        elif index < existing_count + 2:
            # 文内配图：与内容相关
            prompt = f"{keywords[index % len(keywords)]}, {keyword_str}, editorial illustration, balanced composition"
        else:
            # 补充配图：多样化
            prompt = f"{keyword_str}, abstract concept, minimalist, modern design"

        return prompt

    def _wrap_html(self, content_html: str, color_scheme: str) -> str:
        """包装HTML，添加样式"""
        css = self._get_inline_css(color_scheme)

        return f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>微信公众号文章</title>
    <style>
{css}
    </style>
</head>
<body>
{content_html}
</body>
</html>
'''

    def _get_inline_css(self, color_scheme: str) -> str:
        """获取内联CSS"""
        # 读取CSS文件
        css_path = os.path.join(
            os.path.dirname(__file__),
            "../styles/article-templates.css"
        )

        if os.path.exists(css_path):
            with open(css_path, "r", encoding="utf-8") as f:
                return f.read()

        # 内联基础CSS
        return self._get_minimal_css()

    def _get_minimal_css(self) -> str:
        """获取最小CSS（备用）"""
        return """
.wechat-article {
    font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    font-size: 15px;
    line-height: 1.9;
    color: #2D3436;
    max-width: 100%;
    margin: 0 auto;
    padding: 15px;
}
.article-title {
    font-size: 24px;
    font-weight: bold;
    text-align: center;
    margin: 1em 0;
    color: #2D3436;
}
.article-body p {
    text-indent: 2em;
    margin: 0.8em 0;
}
.article-body figure {
    margin: 1.5em 0;
    text-align: center;
}
.article-body figure img {
    max-width: 100%;
    border-radius: 4px;
}
.article-body blockquote {
    background: #F8F9FA;
    border-left: 4px solid #B85C38;
    padding: 1em;
    margin: 1em 0;
}
.article-body pre {
    background: #2D3436;
    color: #DFE6E9;
    padding: 1em;
    border-radius: 6px;
    overflow-x: auto;
}
"""

    def _generate_markdown(self, text: str, images: List[Dict]) -> str:
        """生成带图片引用的Markdown"""
        md_lines = [text]

        # 添加图片引用
        if images:
            md_lines.append("\n\n---\n\n**配图说明：**\n")
            for i, img in enumerate(images):
                caption = img.get("caption", f"配图{i+1}")
                source = img.get("source", "unknown")
                md_lines.append(f"- {caption}（来源：{source}）")

        return "\n".join(md_lines)


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="微信公众号智能排版配图工具"
    )
    parser.add_argument("input", help="输入文件路径或文章文本")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("-t", "--title", help="文章标题")
    parser.add_argument("-c", "--color-scheme",
                       choices=["auto", "business", "warm", "nature", "minimal", "energetic", "vintage"],
                       default="auto",
                       help="配色方案")
    parser.add_argument("--logo", help="Logo文件路径")
    parser.add_argument("--logo-position",
                       choices=["top-right", "bottom-left", "bottom-right"],
                       default="bottom-right",
                       help="Logo位置")
    parser.add_argument("--no-ai", action="store_true", help="禁用AI生图")
    parser.add_argument("--no-watermark-removal", action="store_true", help="禁用去水印")

    args = parser.parse_args()

    # 读取输入
    if os.path.exists(args.input):
        with open(args.input, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = args.input

    # 创建配置
    config = GenerationConfig(
        color_scheme=args.color_scheme,
        logo_path=args.logo,
        logo_position=args.logo_position,
        ai_generation_enabled=not args.no_ai,
        watermark_removal_enabled=not args.no_watermark_removal
    )

    # 生成文章
    generator = WeChatArticleGenerator(config)
    result = generator.generate_article(text, title=args.title)

    # 输出结果
    if result["success"]:
        print(f"\n{'='*50}")
        print("✅ 生成成功！")
        print(f"{'='*50}")
        print(f"\n📊 统计信息：")
        print(f"   - 配图数量：{result['stats']['image_count']}")
        print(f"   - 配色方案：{result['stats']['color_scheme']}")
        print(f"   - 关键词：{', '.join(result['stats']['keywords'])}")

        print(f"\n📝 提示：")
        print(f"   {result['message']}")

        # 保存结果
        if args.output:
            output_path = args.output
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result["html"])
            print(f"\n💾 HTML已保存到：{output_path}")

            # 保存Markdown
            md_path = output_path.replace(".html", ".md")
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(result["markdown"])
            print(f"💾 Markdown已保存到：{md_path}")
        else:
            print(f"\n📄 HTML预览（前500字符）：")
            print(result["html"][:500] + "...")

    else:
        print(f"\n❌ 生成失败：{result['message']}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
