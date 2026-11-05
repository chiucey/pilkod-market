"""
面板生成模块
生成漫画面板，包含角色、场景和对话
"""

from typing import Tuple, Optional, List, Dict
from PIL import Image, ImageDraw, ImageFont
import math

from .parser import Scene, Dialogue, ScriptInfo
from .character import CharacterManager
from .scene import SceneGenerator
from .dialogue import DialogueBubble


class PanelGenerator:
    """漫画面板生成器"""

    # 布局模板
    LAYOUTS = {
        "1x1": [(1, 1)],
        "2x1": [(2, 1)],
        "2x2": [(2, 2)],
        "3x2": [(3, 2)],
        "1x2": [(1, 2)],
        "3x1": [(3, 1)]
    }

    def __init__(self, width: int = 1200, height: int = 900,
                 style: str = "comic"):
        """
        初始化面板生成器

        Args:
            width: 面板宽度
            height: 面板高度
            style: 画风
        """
        self.width = width
        self.height = height
        self.style = style

        # 初始化组件
        self.character_manager = CharacterManager(base_size=150)
        self.scene_generator = SceneGenerator(width=width, height=height)
        self.dialogue_generator = DialogueBubble(default_style=style)

        # 面板边距
        self.margin = 20
        self.panel_gap = 10

    def generate_panel(self, scene: Scene, script_info: ScriptInfo,
                      layout: str = "1x1") -> Image.Image:
        """
        生成单个漫画面板

        Args:
            scene: 场景对象
            script_info: 剧本信息
            layout: 面板布局

        Returns:
            PIL Image对象
        """
        # 获取布局
        grid = self.LAYOUTS.get(layout, [(1, 1)])
        rows, cols = grid[0]

        # 计算每个小面板的尺寸
        panel_width = (self.width - self.margin * 2 - self.panel_gap * (cols - 1)) // cols
        panel_height = (self.height - self.margin * 2 - self.panel_gap * (rows - 1)) // rows

        # 创建面板图像
        panel = Image.new('RGB', (self.width, self.height), (255, 255, 255))
        draw = ImageDraw.Draw(panel)

        # 生成背景
        background = self.scene_generator.generate_scene(scene, self.style)
        panel.paste(background, (0, 0))

        # 准备对话列表
        dialogues = scene.dialogues

        # 放置角色和对话
        if len(dialogues) == 0:
            # 没有对话，只显示场景
            self._draw_scene_title(draw, scene.title, panel_width // 2)

        elif len(dialogues) == 1:
            # 单个对话
            self._draw_single_dialogue(panel, dialogues[0], script_info)

        elif len(dialogues) == 2:
            # 两个角色对话
            self._draw_double_dialogue(panel, dialogues, script_info)

        else:
            # 多个对话，使用多面板布局
            self._draw_multi_dialogue(panel, dialogues, script_info, layout)

        # 绘制场景标题
        self._draw_scene_title(draw, scene.title, self.margin)

        # 绘制边框
        self._draw_panel_border(draw)

        return panel

    def _draw_single_dialogue(self, panel: Image.Image, dialogue: Dialogue,
                            script_info: ScriptInfo) -> None:
        """绘制单个对话面板"""
        # 获取角色图像
        char_img = self.character_manager.get_character_image(
            dialogue.character, dialogue.emotion
        )

        if char_img is None:
            # 如果没有角色图像，创建一个占位符
            char_img = self._create_character_placeholder(
                dialogue.character,
                script_info.get_character_color(dialogue.character)
            )

        # 调整角色图像大小
        char_size = self.height // 2
        char_img = char_img.resize((char_size, char_size), Image.Resampling.LANCZOS)

        # 放置角色（居中偏左）
        char_x = (self.width - char_size) // 2
        char_y = (self.height - char_size) // 2 - 50
        panel.paste(char_img, (char_x, char_y), char_img)

        # 创建对话气泡
        bubble, _ = self.dialogue_generator.create_bubble(
            dialogue.content,
            (char_x + char_size // 2, char_y + char_size // 2),
            direction="right",
            max_width=350,
            font_size=24
        )

        # 放置气泡
        bubble_x = char_x + char_size + 20
        bubble_y = char_y + char_size // 4
        panel.paste(bubble, (bubble_x, bubble_y), bubble)

    def _draw_double_dialogue(self, panel: Image.Image,
                            dialogues: List[Dialogue],
                            script_info: ScriptInfo) -> None:
        """绘制双人对话面板"""
        # 左侧角色
        char1_img = self.character_manager.get_character_image(
            dialogues[0].character, dialogues[0].emotion
        )
        if char1_img is None:
            char1_color = self._get_character_color(script_info, dialogues[0].character)
            char1_img = self._create_character_placeholder(
                dialogues[0].character,
                char1_color
            )

        # 右侧角色
        char2_img = self.character_manager.get_character_image(
            dialogues[1].character, dialogues[1].emotion
        )
        if char2_img is None:
            char2_color = self._get_character_color(script_info, dialogues[1].character)
            char2_img = self._create_character_placeholder(
                dialogues[1].character,
                char2_color
            )

        # 调整大小
        char_size = self.height // 3
        char1_img = char1_img.resize((char_size, char_size), Image.Resampling.LANCZOS)
        char2_img = char2_img.resize((char_size, char_size), Image.Resampling.LANCZOS)

        # 放置角色
        panel.paste(char1_img, (self.margin + 50, self.height // 2 - char_size // 2), char1_img)
        panel.paste(char2_img, (self.width - char_size - self.margin - 50, self.height // 2 - char_size // 2), char2_img)

        # 创建对话气泡
        bubble1, _ = self.dialogue_generator.create_bubble(
            dialogues[0].content,
            (self.margin + 150, self.height // 2),
            direction="left",
            max_width=300,
            font_size=20
        )
        bubble2, _ = self.dialogue_generator.create_bubble(
            dialogues[1].content,
            (self.width - self.margin - 150, self.height // 2),
            direction="right",
            max_width=300,
            font_size=20
        )

        # 放置气泡
        panel.paste(bubble1, (self.margin, self.margin + 50), bubble1)
        panel.paste(bubble2, (self.width - bubble2.size[0] - self.margin, self.margin + 50), bubble2)

    def _draw_multi_dialogue(self, panel: Image.Image,
                            dialogues: List[Dialogue],
                            script_info: ScriptInfo,
                            layout: str) -> None:
        """绘制多人对话面板（多格布局）"""
        grid = self.LAYOUTS.get(layout, [(2, 2)])
        rows, cols = grid[0]

        # 计算每个小格尺寸
        cell_width = (self.width - self.margin * 2 - self.panel_gap * (cols - 1)) // cols
        cell_height = (self.height - self.margin * 2 - self.panel_gap * (rows - 1)) // rows

        # 为每个对话创建小面板
        for i, dialogue in enumerate(dialogues[:rows * cols]):
            row = i // cols
            col = i % cols

            # 计算位置
            x = self.margin + col * (cell_width + self.panel_gap)
            y = self.margin + row * (cell_height + self.panel_gap)

            # 创建小面板背景
            cell_panel = Image.new('RGB', (cell_width, cell_height), (240, 240, 240))
            cell_draw = ImageDraw.Draw(cell_panel)

            # 绘制边框
            cell_draw.rectangle([0, 0, cell_width - 1, cell_height - 1],
                               outline=(100, 100, 100), width=2)

            # 获取角色图像
            char_img = self.character_manager.get_character_image(
                dialogue.character, dialogue.emotion
            )
            if char_img is None:
                # 从script_info获取角色颜色
                char_color = self._get_character_color(script_info, dialogue.character)
                char_img = self._create_character_placeholder(
                    dialogue.character,
                    char_color
                )

            # 调整大小并放置
            img_size = min(cell_width, cell_height) // 2
            char_img = char_img.resize((img_size, img_size), Image.Resampling.LANCZOS)

            char_x = (cell_width - img_size) // 2
            char_y = cell_height // 3
            cell_panel.paste(char_img, (char_x, char_y), char_img)

            # 添加对话气泡
            bubble, _ = self.dialogue_generator.create_bubble(
                dialogue.content,
                (cell_width // 2, cell_height // 2),
                direction="down",
                max_width=cell_width - 20,
                font_size=14
            )

            # 缩小气泡
            bubble_scale = min(1, (cell_width - 30) / bubble.size[0])
            if bubble_scale < 1:
                new_size = (int(bubble.size[0] * bubble_scale),
                          int(bubble.size[1] * bubble_scale))
                bubble = bubble.resize(new_size, Image.Resampling.LANCZOS)

            bubble_y = cell_height - bubble.size[1] - 10
            cell_panel.paste(bubble, ((cell_width - bubble.size[0]) // 2, bubble_y), bubble)

            # 将小面板粘贴到主面板
            panel.paste(cell_panel, (x, y))

    def _get_character_color(self, script_info, character_name: str) -> Tuple[int, int, int]:
        """从剧本信息获取角色颜色"""
        for char in script_info.characters:
            if char.name == character_name:
                return char.color
        return (128, 128, 128)  # 默认灰色

    def _create_character_placeholder(self, name: str,
                                      color: Tuple[int, int, int]) -> Image.Image:
        """创建角色占位符"""
        size = 150
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 绘制圆形背景
        margin = 10
        draw.ellipse([margin, margin, size - margin, size - margin],
                    fill=color)

        # 绘制名字首字母
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
        except:
            font = ImageFont.load_default()

        initial = name[0] if name else "?"
        bbox = draw.textbbox((0, 0), initial, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        text_x = (size - text_width) // 2
        text_y = (size - text_height) // 2
        draw.text((text_x, text_y), initial, fill=(255, 255, 255), font=font)

        return img

    def _draw_scene_title(self, draw: ImageDraw.ImageDraw, title: str,
                         x: int) -> None:
        """绘制场景标题"""
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        except:
            font = ImageFont.load_default()

        # 绘制半透明背景
        bbox = draw.textbbox((x, 10), title, font=font)
        padding = 5
        bg_box = (bbox[0] - padding, bbox[1] - padding,
                 bbox[2] + padding, bbox[3] + padding)

        # 简化处理，直接绘制文本
        draw.text((x, 10), title, fill=(50, 50, 50), font=font)

    def _draw_panel_border(self, draw: ImageDraw.ImageDraw) -> None:
        """绘制面板边框"""
        draw.rectangle([0, 0, self.width - 1, self.height - 1],
                      outline=(0, 0, 0), width=4)

    def generate_comic_page(self, scenes: List[Scene],
                           script_info: ScriptInfo,
                           layout: str = "2x2") -> Image.Image:
        """
        生成漫画页面（包含多个场景）

        Args:
            scenes: 场景列表
            script_info: 剧本信息
            layout: 页面布局

        Returns:
            PIL Image对象
        """
        grid = self.LAYOUTS.get(layout, [(2, 2)])
        rows, cols = grid[0]

        # 计算每个面板尺寸
        panel_width = (self.width - self.margin * 2 - self.panel_gap * (cols - 1)) // cols
        panel_height = (self.height - self.margin * 2 - self.panel_gap * (rows - 1)) // rows

        # 创建页面
        page = Image.new('RGB', (self.width, self.height), (255, 255, 255))
        draw = ImageDraw.Draw(page)

        # 绘制标题栏
        self._draw_page_title(draw, script_info.title)

        # 为每个场景生成面板
        scene_index = 0
        for row in range(rows):
            for col in range(cols):
                if scene_index >= len(scenes):
                    break

                # 计算位置
                x = self.margin + col * (panel_width + self.panel_gap)
                y = self.margin + 40 + row * (panel_height + self.panel_gap)

                # 生成面板
                panel = self.generate_panel(
                    scenes[scene_index],
                    script_info,
                    "1x1"
                )

                # 调整大小并放置
                panel = panel.resize((panel_width, panel_height), Image.Resampling.LANCZOS)
                page.paste(panel, (x, y))

                scene_index += 1

        # 绘制页面边框
        draw.rectangle([0, 0, self.width - 1, self.height - 1],
                      outline=(0, 0, 0), width=3)

        return page

    def _draw_page_title(self, draw: ImageDraw.ImageDraw, title: str) -> None:
        """绘制页面标题"""
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        except:
            font = ImageFont.load_default()

        # 计算标题位置
        bbox = draw.textbbox((0, 10), title, font=font)
        title_width = bbox[2] - bbox[0]
        x = (self.width - title_width) // 2

        # 绘制标题
        draw.text((x, 10), title, fill=(0, 0, 0), font=font)


def create_comic_strip(panels: List[Image.Image],
                       direction: str = "horizontal") -> Image.Image:
    """
    创建漫画条（将多个面板拼接）

    Args:
        panels: 面板图像列表
        direction: 拼接方向

    Returns:
        拼接后的图像
    """
    if not panels:
        return Image.new('RGB', (100, 100), (255, 255, 255))

    if direction == "horizontal":
        # 水平拼接
        total_width = sum(p.width for p in panels)
        max_height = max(p.height for p in panels)

        result = Image.new('RGB', (total_width, max_height), (255, 255, 255))

        x = 0
        for panel in panels:
            result.paste(panel, (x, 0))
            x += panel.width
    else:
        # 垂直拼接
        max_width = max(p.width for p in panels)
        total_height = sum(p.height for p in panels)

        result = Image.new('RGB', (max_width, total_height), (255, 255, 255))

        y = 0
        for panel in panels:
            result.paste(panel, (0, y))
            y += panel.height

    return result
