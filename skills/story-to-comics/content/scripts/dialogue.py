"""
对话气泡模块
生成漫画对话气泡
"""

from typing import Tuple, Optional, List
from PIL import Image, ImageDraw, ImageFont
import textwrap


class DialogueBubble:
    """对话气泡生成器"""

    # 气泡样式
    STYLES = {
        "simple": {
            "fill": (255, 255, 255),
            "outline": (0, 0, 0),
            "tail_style": "triangle"
        },
        "comic": {
            "fill": (255, 255, 240),
            "outline": (0, 0, 0),
            "tail_style": "rounded"
        },
        "cartoon": {
            "fill": (255, 255, 255),
            "outline": (50, 50, 50),
            "tail_style": "star"
        }
    }

    def __init__(self, default_style: str = "comic"):
        """
        初始化对话气泡生成器

        Args:
            default_style: 默认气泡样式
        """
        self.default_style = default_style
        self.font_cache = {}

    def create_bubble(self, text: str, position: Tuple[int, int],
                     direction: str = "left",
                     style: Optional[str] = None,
                     max_width: int = 300,
                     font_size: int = 20) -> Tuple[Image.Image, Tuple[int, int]]:
        """
        创建对话气泡

        Args:
            text: 对话文本
            position: 气泡位置（尾部指向位置）
            direction: 气泡方向（left/right/up/down）
            style: 气泡样式
            max_width: 最大宽度
            font_size: 字体大小

        Returns:
            (气泡图像, 气泡实际位置)
        """
        style = style or self.default_style
        style_config = self.STYLES.get(style, self.STYLES["simple"])

        # 计算文本尺寸
        lines = self._wrap_text(text, max_width - 40, font_size)
        line_height = font_size + 8
        padding = 20

        text_width = max_width - padding * 2
        text_height = len(lines) * line_height

        # 气泡尺寸
        bubble_width = min(max_width, text_width + padding * 2)
        bubble_height = text_height + padding * 2

        # 确保气泡不会太小
        bubble_width = max(bubble_width, 80)
        bubble_height = max(bubble_height, 40)

        # 创建气泡图像
        bubble = Image.new('RGBA', (bubble_width, bubble_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(bubble)

        # 绘制气泡主体
        self._draw_bubble_shape(draw, (0, 0, bubble_width, bubble_height),
                               style_config, direction, position)

        # 绘制文本
        self._draw_text(draw, lines, (padding, padding), font_size)

        return bubble, (bubble_width, bubble_height)

    def _wrap_text(self, text: str, max_width: int, font_size: int) -> List[str]:
        """
        包装文本到多行

        Args:
            text: 原始文本
            max_width: 最大宽度
            font_size: 字体大小

        Returns:
            包装后的文本行列表
        """
        # 估算每行字符数（根据字体大小调整）
        chars_per_line = max_width // (font_size // 2)

        # 使用textwrap包装
        wrapped = textwrap.wrap(text, width=chars_per_line)

        # 如果包装后只有一行，再按逗号和句号分割
        if len(wrapped) == 1 and len(text) > chars_per_line:
            # 按标点分割
            segments = []
            current = ""
            for char in text:
                current += char
                if char in "，。、；：！？""''":
                    if len(current) > chars_per_line // 2:
                        segments.append(current)
                        current = ""
            if current:
                segments.append(current)
            if segments:
                wrapped = segments

        return wrapped if wrapped else [text]

    def _draw_bubble_shape(self, draw: ImageDraw.ImageDraw,
                          bbox: Tuple[int, int, int, int],
                          style_config: dict,
                          direction: str,
                          target_pos: Tuple[int, int]) -> None:
        """
        绘制气泡形状

        Args:
            draw: 绘图对象
            bbox: 边界框
            style_config: 样式配置
            direction: 方向
            target_pos: 目标位置（用于绘制尾部）
        """
        x1, y1, x2, y2 = bbox
        fill_color = style_config["fill"]
        outline_color = style_config["outline"]
        tail_style = style_config["tail_style"]

        # 绘制圆角矩形主体
        corner_radius = 15

        # 简化处理：使用普通矩形
        draw.rectangle([x1, y1, x2, y2], fill=fill_color, outline=outline_color, width=3)

        # 绘制尾部
        if direction == "left":
            # 尾部在左边
            tail_points = [
                (x1, y1 + (y2 - y1) // 2),
                (x1 - 20, y1 + (y2 - y1) // 2 - 10),
                (x1, y1 + (y2 - y1) // 2 + 10)
            ]
        elif direction == "right":
            # 尾部在右边
            tail_points = [
                (x2, y1 + (y2 - y1) // 2),
                (x2 + 20, y1 + (y2 - y1) // 2 - 10),
                (x2, y1 + (y2 - y1) // 2 + 10)
            ]
        elif direction == "up":
            # 尾部在上边
            tail_points = [
                (x1 + (x2 - x1) // 2, y1),
                (x1 + (x2 - x1) // 2 - 10, y1 - 20),
                (x1 + (x2 - x1) // 2 + 10, y1 - 20)
            ]
        else:  # down
            # 尾部在下边
            tail_points = [
                (x1 + (x2 - x1) // 2, y2),
                (x1 + (x2 - x1) // 2 - 10, y2 + 20),
                (x1 + (x2 - x1) // 2 + 10, y2 + 20)
            ]

        # 绘制尾部
        if len(tail_points) >= 3:
            draw.polygon(tail_points, fill=fill_color, outline=outline_color)

    def _draw_text(self, draw: ImageDraw.ImageDraw, lines: List[str],
                  position: Tuple[int, int], font_size: int) -> None:
        """
        绘制文本

        Args:
            draw: 绘图对象
            lines: 文本行列表
            position: 位置
            font_size: 字体大小
        """
        x, y = position
        line_height = font_size + 8

        # 尝试加载字体
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", font_size)
            except:
                font = ImageFont.load_default()

        # 绘制每行文本
        for i, line in enumerate(lines):
            draw.text((x, y + i * line_height), line, fill=(0, 0, 0), font=font)

    def create_thought_bubble(self, text: str, position: Tuple[int, int],
                             max_width: int = 250,
                             font_size: int = 18) -> Image.Image:
        """
        创建思考气泡（云朵形状）

        Args:
            text: 思考内容
            position: 位置
            max_width: 最大宽度
            font_size: 字体大小

        Returns:
            思考气泡图像
        """
        lines = self._wrap_text(text, max_width - 40, font_size)
        line_height = font_size + 6
        padding = 15

        bubble_width = max_width
        bubble_height = len(lines) * line_height + padding * 2

        # 创建气泡图像
        bubble = Image.new('RGBA', (bubble_width, bubble_height + 30), (0, 0, 0, 0))
        draw = ImageDraw.Draw(bubble)

        # 绘制云朵形状
        cloud_center_y = bubble_height // 2

        # 使用多个重叠的圆形创建云朵效果
        fill_color = (255, 255, 255)
        outline_color = (100, 100, 100)

        # 主气泡
        draw.ellipse([0, 0, bubble_width - 20, bubble_height],
                    fill=fill_color, outline=outline_color, width=2)

        # 小圆点（表示思考）
        for i, (ox, oy, r) in enumerate([
            (-10, bubble_height + 5, 8),
            (10, bubble_height + 18, 12),
            (-5, bubble_height + 25, 6)
        ]):
            draw.ellipse([ox - r, oy - r, ox + r, oy + r],
                        fill=fill_color, outline=outline_color, width=2)

        # 绘制文本
        self._draw_text(draw, lines, (padding, padding), font_size)

        return bubble

    def create_narration_box(self, text: str, width: int = 400,
                            font_size: int = 16) -> Image.Image:
        """
        创建叙述框

        Args:
            text: 叙述文本
            width: 宽度
            font_size: 字体大小

        Returns:
            叙述框图像
        """
        lines = self._wrap_text(text, width - 30, font_size)
        line_height = font_size + 6
        padding = 15

        box_height = len(lines) * line_height + padding * 2

        # 创建图像
        box = Image.new('RGBA', (width, box_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(box)

        # 绘制矩形框
        draw.rectangle([0, 0, width - 1, box_height - 1],
                      outline=(50, 50, 50), width=2)

        # 绘制文本
        self._draw_text(draw, lines, (padding, padding), font_size)

        return box

    def apply_bubble_effect(self, bubble: Image.Image, effect: str) -> Image.Image:
        """
        应用气泡效果

        Args:
            bubble: 气泡图像
            effect: 效果类型（shadow/glow/round）

        Returns:
            处理后的气泡图像
        """
        if effect == "shadow":
            # 添加阴影
            shadow = Image.new('RGBA', bubble.size, (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow)

            # 简单阴影偏移
            offset = 5
            shadow_draw.rectangle(
                [offset, offset, bubble.size[0] + offset, bubble.size[1] + offset],
                fill=(0, 0, 0, 50)
            )

            result = Image.new('RGBA', bubble.size, (0, 0, 0, 0))
            result.paste(shadow, (0, 0))
            result.paste(bubble, (0, 0), bubble)
            return result

        elif effect == "glow":
            # 添加发光效果
            from PIL import ImageEnhance

            # 高斯模糊模拟发光
            glow = bubble.filter(ImageEnhance.Blur(5).enhance(2))
            result = Image.composite(glow, bubble, bubble)
            return result

        return bubble


def create_dialogue_sequence(dialogues: List[dict],
                            start_pos: Tuple[int, int],
                            direction: str = "alternating",
                            spacing: int = 80) -> List[Tuple[Image.Image, Tuple[int, int]]]:
    """
    创建对话序列

    Args:
        dialogues: 对话列表，每个元素为 (角色名, 对话内容)
        start_pos: 起始位置
        direction: 方向（alternating/left/right）
        spacing: 垂直间距

    Returns:
        气泡列表
    """
    generator = DialogueBubble()
    bubbles = []

    current_pos = start_pos

    for i, (character, content) in enumerate(dialogues):
        # 确定方向
        if direction == "alternating":
            bubble_dir = "left" if i % 2 == 0 else "right"
        else:
            bubble_dir = direction

        bubble, size = generator.create_bubble(
            content,
            current_pos,
            direction=bubble_dir,
            max_width=280
        )

        bubbles.append((bubble, current_pos))

        # 更新位置
        current_pos = (current_pos[0], current_pos[1] + size[1] + spacing)

    return bubbles
