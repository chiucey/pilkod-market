"""
Game Art AI Generator - UI Generator
游戏美术AI生成器 - UI组件生成模块

统一化生成游戏UI控件（按钮、进度条、弹窗等）
"""

import os
import logging
from typing import Dict, Optional, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# 配置日志
logger = logging.getLogger('UIGenerator')


class UIComponentType(Enum):
    """UI组件类型"""
    BUTTON = "button"
    PROGRESS_BAR = "progress_bar"
    POPUP = "popup"
    COIN_ICON = "coin_icon"
    NAVBAR = "navbar"
    LEVEL_INDICATOR = "level_indicator"
    TAB_BAR = "tab_bar"
    CARD = "card"


@dataclass
class UIComponent:
    """UI组件"""
    component_type: UIComponentType
    name: str
    width: int
    height: int
    file_path: str
    states: List[str] = None  # normal, hover, pressed, disabled
    metadata: Dict = None

    def __post_init__(self):
        if self.states is None:
            self.states = ["normal"]
        if self.metadata is None:
            self.metadata = {}


@dataclass
class UITheme:
    """UI主题配置"""
    corner_radius: int = 8
    shadow_offset: int = 2
    shadow_blur: int = 4
    shadow_color: str = "#00000040"
    border_width: int = 0
    border_color: str = "#FFFFFF00"
    padding: int = 12
    font_size: int = 24
    font_color: str = "#FFFFFF"


class UIGenerator:
    """UI组件生成器"""

    # 组件尺寸规格
    SIZE_SPECS = {
        UIComponentType.BUTTON: {
            "small": (80, 40),
            "medium": (120, 50),
            "large": (160, 60),
            "xlarge": (200, 70)
        },
        UIComponentType.PROGRESS_BAR: {
            "small": (100, 16),
            "medium": (200, 24),
            "large": (300, 32)
        },
        UIComponentType.COIN_ICON: {
            "small": (24, 24),
            "medium": (32, 32),
            "large": (48, 48)
        },
        UIComponentType.POPUP: {
            "small": (280, 200),
            "medium": (360, 280),
            "large": (450, 350)
        }
    }

    def __init__(
        self,
        color_scheme: Dict = None,
        theme: UITheme = None
    ):
        """
        初始化UI生成器

        Args:
            color_scheme: 色彩方案
            theme: UI主题配置
        """
        self.color_scheme = color_scheme or {}
        self.theme = theme or UITheme()

        # 默认色彩
        self.primary = self.color_scheme.get("primary", "#4A90D9")
        self.secondary = self.color_scheme.get("secondary", "#7B68EE")
        self.accent = self.color_scheme.get("accent", "#FFD700")
        self.background = self.color_scheme.get("background", "#1A1A2E")
        self.text = self.color_scheme.get("text", "#FFFFFF")

    def set_color_scheme(self, color_scheme: Dict):
        """设置色彩方案"""
        self.color_scheme = color_scheme
        self.primary = color_scheme.get("primary", self.primary)
        self.secondary = color_scheme.get("secondary", self.secondary)
        self.accent = color_scheme.get("accent", self.accent)
        self.background = color_scheme.get("background", self.background)
        self.text = color_scheme.get("text", self.text)

    def generate_button(
        self,
        name: str,
        output_dir: str,
        size: str = "medium",
        states: List[str] = None
    ) -> List[UIComponent]:
        """
        生成按钮组件

        Args:
            name: 按钮名称
            output_dir: 输出目录
            size: 尺寸(small/medium/large/xlarge)
            states: 状态列表(normal/hover/pressed/disabled)

        Returns:
            UIComponent列表
        """
        if states is None:
            states = ["normal", "hover", "pressed", "disabled"]

        logger.info(f"[UIGenerator] Generating button: {name}")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        components = []
        button_sizes = self.SIZE_SPECS[UIComponentType.BUTTON]
        width, height = button_sizes.get(size, button_sizes["medium"])

        for state in states:
            img = self._create_button_image(width, height, state)

            filename = f"btn_{name}_{state}.png"
            filepath = output_path / filename
            img.save(filepath, "PNG")

            components.append(UIComponent(
                component_type=UIComponentType.BUTTON,
                name=name,
                width=width,
                height=height,
                file_path=str(filepath),
                states=[state],
                metadata={"state": state, "size": size}
            ))

        return components

    def _create_button_image(
        self,
        width: int,
        height: int,
        state: str
    ) -> Image.Image:
        """创建按钮图像"""
        # 状态对应的颜色和效果
        state_configs = {
            "normal": {
                "bg_color": self.primary,
                "scale": 1.0,
                "offset": 0
            },
            "hover": {
                "bg_color": self._lighten_color(self.primary, 0.15),
                "scale": 1.02,
                "offset": 0
            },
            "pressed": {
                "bg_color": self._darken_color(self.primary, 0.15),
                "scale": 0.98,
                "offset": 2
            },
            "disabled": {
                "bg_color": self._darken_color(self.primary, 0.4),
                "scale": 1.0,
                "offset": 0
            }
        }

        config = state_configs.get(state, state_configs["normal"])

        # 创建图像
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 绘制圆角矩形
        radius = self.theme.corner_radius
        bg_color = self._hex_to_rgba(config["bg_color"], 255)

        # 主按钮
        self._rounded_rectangle(
            draw,
            (0, config["offset"], width, height + config["offset"]),
            bg_color,
            radius
        )

        # 添加高光
        highlight_color = self._hex_to_rgba("#FFFFFF", 30)
        self._rounded_rectangle(
            draw,
            (4, config["offset"] + 2, width - 4, height // 2 + config["offset"]),
            highlight_color,
            radius - 2
        )

        return img

    def generate_progress_bar(
        self,
        name: str,
        output_dir: str,
        size: str = "medium",
        style: str = "horizontal"
    ) -> List[UIComponent]:
        """生成进度条组件"""
        logger.info(f"[UIGenerator] Generating progress bar: {name}")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        components = []
        bar_sizes = self.SIZE_SPECS[UIComponentType.PROGRESS_BAR]
        width, height = bar_sizes.get(size, bar_sizes["medium"])

        # 背景条
        bg_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        bg_draw = ImageDraw.Draw(bg_img)
        bg_color = self._hex_to_rgba(self._darken_color(self.background, 0.3), 200)
        self._rounded_rectangle(bg_draw, (0, 0, width, height), bg_color, height // 2)
        bg_filepath = output_path / f"progress_{name}_bg.png"
        bg_img.save(bg_filepath, "PNG")

        components.append(UIComponent(
            component_type=UIComponentType.PROGRESS_BAR,
            name=f"{name}_bg",
            width=width,
            height=height,
            file_path=str(bg_filepath),
            metadata={"part": "background", "style": style}
        ))

        # 前景填充（默认50%）
        fill_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        fill_draw = ImageDraw.Draw(fill_img)
        fill_color = self._hex_to_rgba(self.accent, 255)
        fill_width = width // 2
        self._rounded_rectangle(fill_draw, (0, 0, fill_width, height), fill_color, height // 2)
        fill_filepath = output_path / f"progress_{name}_fill.png"
        fill_img.save(fill_filepath, "PNG")

        components.append(UIComponent(
            component_type=UIComponentType.PROGRESS_BAR,
            name=f"{name}_fill",
            width=width,
            height=height,
            file_path=str(fill_filepath),
            metadata={"part": "fill", "style": style}
        ))

        return components

    def generate_popup(
        self,
        name: str,
        output_dir: str,
        size: str = "medium",
        popup_type: str = "info"
    ) -> UIComponent:
        """生成弹窗组件"""
        logger.info(f"[UIGenerator] Generating popup: {name}")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        popup_sizes = self.SIZE_SPECS[UIComponentType.POPUP]
        width, height = popup_sizes.get(size, popup_sizes["medium"])

        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 弹窗背景
        bg_color = self._hex_to_rgba(self.background, 240)
        self._rounded_rectangle(draw, (0, 0, width, height), bg_color, 16)

        # 边框
        border_color = self._hex_to_rgba(self.primary, 200)
        self._rounded_rectangle_outline(draw, (0, 0, width, height), border_color, 16, 2)

        # 顶部装饰条
        top_color = self._hex_to_rgba(self.primary, 255)
        self._rounded_rectangle(draw, (0, 0, width, 40), top_color, 16)
        draw.rectangle([0, 20, width, 40], fill=top_color)  # 覆盖底部圆角

        filename = f"popup_{name}_{popup_type}.png"
        filepath = output_path / filename
        img.save(filepath, "PNG")

        return UIComponent(
            component_type=UIComponentType.POPUP,
            name=name,
            width=width,
            height=height,
            file_path=str(filepath),
            metadata={"popup_type": popup_type, "size": size}
        )

    def generate_coin_icon(
        self,
        name: str,
        output_dir: str,
        size: str = "medium"
    ) -> UIComponent:
        """生成金币图标"""
        logger.info(f"[UIGenerator] Generating coin icon: {name}")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        coin_sizes = self.SIZE_SPECS[UIComponentType.COIN_ICON]
        size_tuple = coin_sizes.get(size, coin_sizes["medium"])
        width = height = size_tuple[0]

        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 金币圆形
        coin_color = self._hex_to_rgba(self.accent, 255)
        draw.ellipse([0, 0, width - 1, height - 1], fill=coin_color)

        # 内圈
        inner_color = self._hex_to_rgba(self._lighten_color(self.accent, 0.2), 255)
        margin = width // 6
        draw.ellipse([margin, margin, width - margin - 1, height - margin - 1], fill=inner_color)

        # 高光
        highlight_color = self._hex_to_rgba("#FFFFFF", 100)
        draw.ellipse([margin, margin, width // 2, height // 2], fill=highlight_color)

        filename = f"coin_{name}.png"
        filepath = output_path / filename
        img.save(filepath, "PNG")

        return UIComponent(
            component_type=UIComponentType.COIN_ICON,
            name=name,
            width=width,
            height=height,
            file_path=str(filepath),
            metadata={"coin_type": name}
        )

    def generate_navbar(
        self,
        name: str,
        output_dir: str,
        width: int = 400,
        height: int = 60
    ) -> UIComponent:
        """生成导航栏"""
        logger.info(f"[UIGenerator] Generating navbar: {name}")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 背景
        bg_color = self._hex_to_rgba(self.background, 230)
        draw.rectangle([0, 0, width, height], fill=bg_color)

        # 顶部边框
        border_color = self._hex_to_rgba(self.primary, 150)
        draw.rectangle([0, 0, width, 2], fill=border_color)

        filename = f"navbar_{name}.png"
        filepath = output_path / filename
        img.save(filepath, "PNG")

        return UIComponent(
            component_type=UIComponentType.NAVBAR,
            name=name,
            width=width,
            height=height,
            file_path=str(filepath)
        )

    def generate_level_indicator(
        self,
        name: str,
        output_dir: str,
        levels: int = 10
    ) -> List[UIComponent]:
        """生成关卡指示器"""
        logger.info(f"[UIGenerator] Generating level indicator: {name}")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        components = []
        icon_size = 32
        spacing = 8

        for i in range(levels):
            img = Image.new("RGBA", (icon_size, icon_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # 圆形背景
            bg_color = self._hex_to_rgba(self._darken_color(self.primary, 0.3), 255)
            draw.ellipse([0, 0, icon_size - 1, icon_size - 1], fill=bg_color)

            # 数字
            center = icon_size // 2
            text_color = self._hex_to_rgba(self.text, 255)
            draw.text((center, center), str(i + 1), fill=text_color)

            filename = f"level_{name}_{i+1:02d}.png"
            filepath = output_path / filename
            img.save(filepath, "PNG")

            components.append(UIComponent(
                component_type=UIComponentType.LEVEL_INDICATOR,
                name=f"{name}_{i+1}",
                width=icon_size,
                height=icon_size,
                file_path=str(filepath),
                metadata={"level": i + 1, "total": levels}
            ))

        return components

    def generate_full_ui_set(
        self,
        game_name: str,
        output_dir: str
    ) -> Dict[str, List[UIComponent]]:
        """
        生成完整UI组件集

        Args:
            game_name: 游戏名称
            output_dir: 输出目录

        Returns:
            组件字典
        """
        logger.info(f"[UIGenerator] Generating full UI set for: {game_name}")

        components = {}

        # 按钮
        components["buttons"] = self.generate_button(
            game_name, output_dir, size="medium"
        )

        # 进度条
        components["progress_bars"] = self.generate_progress_bar(
            game_name, output_dir, size="medium"
        )

        # 弹窗
        components["popups"] = [
            self.generate_popup(f"{game_name}_confirm", output_dir, popup_type="confirm"),
            self.generate_popup(f"{game_name}_reward", output_dir, popup_type="reward")
        ]

        # 金币图标
        components["coins"] = [self.generate_coin_icon(game_name, output_dir)]

        # 导航栏
        components["navbar"] = [self.generate_navbar(game_name, output_dir)]

        # 关卡指示器
        components["level_indicators"] = self.generate_level_indicator(
            game_name, output_dir, levels=5
        )

        return components

    # ========== 辅助方法 ==========

    def _rounded_rectangle(
        self,
        draw: ImageDraw.Draw,
        coords: Tuple[int, int, int, int],
        fill: Tuple,
        radius: int
    ):
        """绘制圆角矩形"""
        x1, y1, x2, y2 = coords

        # 主体矩形
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)

        # 四个角
        draw.pieslice([x1, y1, x1 + radius * 2, y1 + radius * 2],
                       180, 270, fill=fill)
        draw.pieslice([x2 - radius * 2, y1, x2, y1 + radius * 2],
                       270, 360, fill=fill)
        draw.pieslice([x1, y2 - radius * 2, x1 + radius * 2, y2],
                       90, 180, fill=fill)
        draw.pieslice([x2 - radius * 2, y2 - radius * 2, x2, y2],
                       0, 90, fill=fill)

    def _rounded_rectangle_outline(
        self,
        draw: ImageDraw.Draw,
        coords: Tuple[int, int, int, int],
        outline: Tuple,
        radius: int,
        width: int = 1
    ):
        """绘制圆角矩形边框"""
        x1, y1, x2, y2 = coords

        # 上边
        draw.arc([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=outline, width=width)
        draw.line([x1 + radius, y1, x2 - radius, y1], fill=outline, width=width)

        # 右边
        draw.arc([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, fill=outline, width=width)
        draw.line([x2, y1 + radius, x2, y2 - radius], fill=outline, width=width)

        # 下边
        draw.arc([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=outline, width=width)
        draw.line([x2 - radius, y2, x1 + radius, y2], fill=outline, width=width)

        # 左边
        draw.arc([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=outline, width=width)
        draw.line([x1, y2 - radius, x1, y1 + radius], fill=outline, width=width)

    def _hex_to_rgba(self, hex_color: str, alpha: int) -> Tuple:
        """十六进制转RGBA"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b, alpha)

    def _lighten_color(self, hex_color: str, amount: float) -> str:
        """提亮颜色"""
        r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
        r = min(255, int(r + (255 - r) * amount))
        g = min(255, int(g + (255 - g) * amount))
        b = min(255, int(b + (255 - b) * amount))
        return f"#{r:02X}{g:02X}{b:02X}"

    def _darken_color(self, hex_color: str, amount: float) -> str:
        """加深颜色"""
        r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
        r = max(0, int(r * (1 - amount)))
        g = max(0, int(g * (1 - amount)))
        b = max(0, int(b * (1 - amount)))
        return f"#{r:02X}{g:02X}{b:02X}"


def main():
    """测试"""
    print("=" * 60)
    print("UI Generator Test")
    print("UI组件生成器测试")
    print("=" * 60)

    generator = UIGenerator({
        "primary": "#4A90D9",
        "secondary": "#7B68EE",
        "accent": "#FFD700",
        "background": "#1A1A2E",
        "text": "#FFFFFF"
    })

    components = generator.generate_full_ui_set("test_game", "./output")
    print(f"Generated {sum(len(v) for v in components.values())} UI components")


if __name__ == "__main__":
    main()
