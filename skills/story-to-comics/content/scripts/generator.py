"""
漫画生成器
主模块，整合所有组件生成漫画
"""

import os
import json
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from .parser import ScriptParser, ScriptInfo, parse_script_file
from .character import CharacterManager
from .scene import SceneGenerator
from .dialogue import DialogueBubble
from .panel import PanelGenerator


class ComicGenerator:
    """漫画生成器主类"""

    # 支持的输出格式
    OUTPUT_FORMATS = ["png", "jpg", "pdf"]

    # 画风选项
    STYLES = ["simple", "traditional", "cartoon"]

    # 布局选项
    LAYOUTS = ["1x1", "2x1", "2x2", "3x2", "1x2", "3x1"]

    def __init__(self, style: str = "simple", width: int = 1200, height: int = 900):
        """
        初始化漫画生成器

        Args:
            style: 画风 (simple/traditional/cartoon)
            width: 输出宽度
            height: 输出高度
        """
        self.style = style if style in self.STYLES else "simple"
        self.width = width
        self.height = height

        # 初始化组件
        self.parser = ScriptParser()
        self.character_manager = CharacterManager(base_size=150)
        self.scene_generator = SceneGenerator(width=width, height=height)
        self.dialogue_generator = DialogueBubble(default_style=style)
        self.panel_generator = PanelGenerator(
            width=width,
            height=height,
            style=style
        )

        # 解析结果
        self.script_info: Optional[ScriptInfo] = None

    def parse_script(self, script_text: str) -> ScriptInfo:
        """
        解析剧本文本

        Args:
            script_text: 剧本文本内容

        Returns:
            ScriptInfo: 解析后的剧本信息
        """
        self.script_info = self.parser.parse(script_text)

        # 注册所有角色
        for character in self.script_info.characters:
            self.character_manager.register_character(character)

        return self.script_info

    def parse_script_file(self, file_path: str) -> ScriptInfo:
        """
        解析剧本文件

        Args:
            file_path: 剧本文件路径

        Returns:
            ScriptInfo: 解析后的剧本信息
        """
        self.script_info = parse_script_file(file_path)

        # 注册所有角色
        for character in self.script_info.characters:
            self.character_manager.register_character(character)

        return self.script_info

    def generate(self, script_info: Optional[ScriptInfo] = None,
                output_dir: str = "output",
                format: str = "png",
                layout: str = "2x2",
                pages_per_row: int = 2) -> Dict[str, any]:
        """
        生成漫画

        Args:
            script_info: 剧本信息（可选，如果不提供则使用已解析的剧本）
            output_dir: 输出目录
            format: 输出格式 (png/jpg/pdf)
            layout: 面板布局
            pages_per_row: 每页场景数

        Returns:
            生成结果字典
        """
        # 确定剧本信息
        if script_info is None:
            if self.script_info is None:
                raise ValueError("没有可用的剧本信息，请先解析剧本")
            script_info = self.script_info

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 生成结果
        results = {
            "title": script_info.title,
            "scenes": [],
            "panels": [],
            "pages": [],
            "output_dir": output_dir
        }

        # 生成每个场景的面板
        for scene in script_info.scenes:
            # 生成单场景面板
            panel = self.panel_generator.generate_panel(
                scene,
                script_info,
                layout="1x1"
            )

            # 保存面板（只使用编号避免文件名包含中文）
            scene_name = f"scene_{scene.number:02d}"
            panel_path = os.path.join(output_dir, f"{scene_name}.{format}")
            panel.save(panel_path, quality=95)

            results["panels"].append({
                "scene": scene.number,
                "title": scene.title,
                "path": panel_path
            })

        # 生成分页漫画
        scenes_per_page = pages_per_row * pages_per_row
        num_pages = (len(script_info.scenes) + scenes_per_page - 1) // scenes_per_page

        for page_num in range(num_pages):
            start_idx = page_num * scenes_per_page
            end_idx = min(start_idx + scenes_per_page, len(script_info.scenes))
            page_scenes = script_info.scenes[start_idx:end_idx]

            # 生成分页
            page = self.panel_generator.generate_comic_page(
                page_scenes,
                script_info,
                layout=f"{pages_per_row}x{pages_per_row}"
            )

            # 保存页面
            page_path = os.path.join(output_dir, f"page_{page_num + 1:02d}.{format}")
            page.save(page_path, quality=95)

            results["pages"].append({
                "page": page_num + 1,
                "scenes": [s.number for s in page_scenes],
                "path": page_path
            })

        # 生成封面
        if script_info.scenes:
            cover = self._generate_cover(script_info)
            cover_path = os.path.join(output_dir, f"cover.{format}")
            cover.save(cover_path, quality=95)
            results["cover"] = cover_path

        return results

    def generate_single_panel(self, scene, layout: str = "1x1") -> Image.Image:
        """
        生成单个面板

        Args:
            scene: 场景对象
            layout: 布局

        Returns:
            PIL Image对象
        """
        if self.script_info is None:
            raise ValueError("没有可用的剧本信息")

        return self.panel_generator.generate_panel(scene, self.script_info, layout)

    def generate_preview(self, script_text: str,
                        max_scenes: int = 4) -> List[Image.Image]:
        """
        生成预览图像

        Args:
            script_text: 剧本文本
            max_scenes: 最大场景数

        Returns:
            预览图像列表
        """
        # 解析剧本
        script_info = self.parse_script(script_text)

        # 生成预览面板
        previews = []
        for i, scene in enumerate(script_info.scenes[:max_scenes]):
            panel = self.panel_generator.generate_panel(
                scene,
                script_info,
                layout="1x1"
            )
            previews.append(panel)

        return previews

    def _generate_cover(self, script_info: ScriptInfo) -> Image.Image:
        """
        生成封面

        Args:
            script_info: 剧本信息

        Returns:
            封面图像
        """
        # 创建封面背景
        cover = Image.new('RGB', (self.width, self.height), (45, 45, 65))
        draw = ImageDraw.Draw(cover)

        # 添加装饰元素
        self._draw_cover_decoration(draw)

        # 绘制标题
        self._draw_cover_title(draw, script_info.title)

        # 绘制副标题
        self._draw_cover_subtitle(draw, script_info)

        # 绘制角色
        self._draw_cover_characters(draw, script_info)

        return cover

    def _draw_cover_decoration(self, draw: ImageDraw.ImageDraw) -> None:
        """绘制封面装饰"""
        # 添加渐变效果
        for y in range(self.height):
            ratio = y / self.height
            r = int(45 * (1 - ratio) + 70 * ratio)
            g = int(45 * (1 - ratio) + 70 * ratio)
            b = int(65 * (1 - ratio) + 120 * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))

        # 添加装饰线条
        line_color = (255, 255, 255, 50)
        for i in range(5):
            y = self.height // 6 * (i + 1)
            draw.line([(0, y), (self.width, y)], fill=(255, 255, 255, 30), width=1)

    def _draw_cover_title(self, draw: ImageDraw.ImageDraw, title: str) -> None:
        """绘制封面标题"""
        try:
            title_font_size = 72
            title_font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                title_font_size
            )
        except:
            title_font = ImageFont.load_default()

        # 计算标题位置
        bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = bbox[2] - bbox[0]
        title_height = bbox[3] - bbox[1]

        x = (self.width - title_width) // 2
        y = self.height // 3

        # 绘制阴影
        draw.text((x + 3, y + 3), title, fill=(0, 0, 0), font=title_font)

        # 绘制标题
        draw.text((x, y), title, fill=(255, 255, 255), font=title_font)

    def _draw_cover_subtitle(self, draw: ImageDraw.ImageDraw,
                           script_info: ScriptInfo) -> None:
        """绘制封面副标题"""
        try:
            subtitle_font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                24
            )
        except:
            subtitle_font = ImageFont.load_default()

        # 副标题内容
        subtitle_lines = [
            f"时长：{script_info.duration}" if script_info.duration else "",
            f"场景：{script_info.location}" if script_info.location else "",
            f"共 {len(script_info.scenes)} 个场景"
        ]

        subtitle_text = " | ".join([l for l in subtitle_lines if l])

        # 计算位置
        bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
        x = (self.width - (bbox[2] - bbox[0])) // 2
        y = self.height // 3 + 100

        draw.text((x, y), subtitle_text, fill=(200, 200, 200), font=subtitle_font)

    def _draw_cover_characters(self, draw: ImageDraw.ImageDraw,
                              script_info: ScriptInfo) -> None:
        """绘制封面角色"""
        num_chars = min(len(script_info.characters), 4)

        if num_chars == 0:
            return

        # 计算角色图标布局
        icon_size = 100
        spacing = 30
        total_width = num_chars * icon_size + (num_chars - 1) * spacing
        start_x = (self.width - total_width) // 2
        y = self.height - 150

        for i, char in enumerate(script_info.characters[:num_chars]):
            x = start_x + i * (icon_size + spacing)

            # 绘制圆形背景
            draw.ellipse(
                [x, y, x + icon_size, y + icon_size],
                fill=char.color
            )

            # 绘制名字
            try:
                name_font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    16
                )
            except:
                name_font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), char.name, font=name_font)
            name_width = bbox[2] - bbox[0]
            draw.text((x + (icon_size - name_width) // 2, y + icon_size + 5),
                     char.name, fill=(255, 255, 255), font=name_font)

    def save_config(self, config_path: str) -> None:
        """
        保存配置到文件

        Args:
            config_path: 配置文件路径
        """
        config = {
            "style": self.style,
            "width": self.width,
            "height": self.height,
            "script_info": None
        }

        if self.script_info:
            config["script_info"] = {
                "title": self.script_info.title,
                "duration": self.script_info.duration,
                "location": self.script_info.location,
                "num_characters": len(self.script_info.characters),
                "num_scenes": len(self.script_info.scenes)
            }

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    @classmethod
    def from_config(cls, config_path: str) -> 'ComicGenerator':
        """
        从配置文件加载生成器

        Args:
            config_path: 配置文件路径

        Returns:
            ComicGenerator实例
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        generator = cls(
            style=config.get("style", "simple"),
            width=config.get("width", 1200),
            height=config.get("height", 900)
        )

        return generator


def generate_comics_from_script(script_text: str,
                                output_dir: str = "output",
                                style: str = "simple",
                                format: str = "png") -> Dict[str, any]:
    """
    从剧本文本生成漫画的便捷函数

    Args:
        script_text: 剧本文本
        output_dir: 输出目录
        style: 画风
        format: 输出格式

    Returns:
        生成结果
    """
    generator = ComicGenerator(style=style)
    script_info = generator.parse_script(script_text)
    return generator.generate(
        script_info=script_info,
        output_dir=output_dir,
        format=format
    )


def generate_comics_from_file(script_path: str,
                             output_dir: str = "output",
                             style: str = "simple",
                             format: str = "png") -> Dict[str, any]:
    """
    从剧本文件生成漫画的便捷函数

    Args:
        script_path: 剧本文件路径
        output_dir: 输出目录
        style: 画风
        format: 输出格式

    Returns:
        生成结果
    """
    generator = ComicGenerator(style=style)
    script_info = generator.parse_script_file(script_path)
    return generator.generate(
        script_info=script_info,
        output_dir=output_dir,
        format=format
    )
