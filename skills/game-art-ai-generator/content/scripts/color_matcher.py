"""
Game Art AI Generator - Color Matcher
游戏美术AI生成器 - 色彩匹配模块

基于游戏类型和主题关键词自动生成适配的色彩方案
"""

import logging
import random
from typing import Dict, Optional, Any, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import colorsys

# 配置日志
logger = logging.getLogger('ColorMatcher')


class GameType(Enum):
    """游戏类型"""
    RELAXING = "relaxing"           # 解压闯关类
    BREEDING = "breeding"            # 合成养成类
    SKILL = "skill"                  # 敏捷挑战类
    COMPETITIVE = "competitive"      # 趣味竞技类
    IDLE = "idle"                   # 放置收集类


class ColorMood(Enum):
    """色彩情绪"""
    SOFT = "soft"                   # 柔和
    VIBRANT = "vibrant"             # 鲜明
    DARK = "dark"                   # 深沉
    BRIGHT = "bright"               # 明亮
    PASTEL = "pastel"               # 马卡龙
    NEON = "neon"                   # 霓虹


@dataclass
class ColorScheme:
    """色彩方案"""
    primary: str = "#4A90D9"         # 主色
    secondary: str = "#7B68EE"      # 辅助色
    accent: str = "#FFD700"          # 点缀色
    background: str = "#1A1A2E"     # 背景色
    text: str = "#FFFFFF"            # 文字色
    gradient_start: str = "#4A90D9"  # 渐变起始
    gradient_end: str = "#7B68EE"    # 渐变终止

    # 额外配色
    success: str = "#4CAF50"        # 成功色
    warning: str = "#FF9800"         # 警告色
    error: str = "#F44336"          # 错误色

    # 情绪标签
    mood: str = "vibrant"

    def to_dict(self) -> Dict[str, str]:
        """转换为字典"""
        return {
            "primary": self.primary,
            "secondary": self.secondary,
            "accent": self.accent,
            "background": self.background,
            "text": self.text,
            "gradient": f"linear-gradient(135deg, {self.gradient_start}, {self.gradient_end})",
            "success": self.success,
            "warning": self.warning,
            "error": self.error,
            "mood": self.mood
        }

    def to_css_variables(self) -> str:
        """生成CSS变量"""
        return f"""
:root {{
    --color-primary: {self.primary};
    --color-secondary: {self.secondary};
    --color-accent: {self.accent};
    --color-background: {self.background};
    --color-text: {self.text};
    --color-gradient-start: {self.gradient_start};
    --color-gradient-end: {self.gradient_end};
    --color-success: {self.success};
    --color-warning: {self.warning};
    --color-error: {self.error};
}}
"""


class ColorMatcher:
    """色彩匹配器"""

    # 游戏类型对应的色彩情绪
    GAME_TYPE_MOODS = {
        GameType.RELAXING: ColorMood.SOFT,
        GameType.BREEDING: ColorMood.PASTEL,
        GameType.SKILL: ColorMood.VIBRANT,
        GameType.COMPETITIVE: ColorMood.NEON,
        GameType.IDLE: ColorMood.BRIGHT
    }

    # 主题关键词映射
    THEME_KEYWORDS = {
        # 太空/科技
        "太空": {"primary_h": 220, "saturation": 0.7, "brightness": 0.6},
        "科技": {"primary_h": 200, "saturation": 0.8, "brightness": 0.5},
        "未来": {"primary_h": 260, "saturation": 0.9, "brightness": 0.7},

        # 自然/清新
        "自然": {"primary_h": 120, "saturation": 0.6, "brightness": 0.5},
        "森林": {"primary_h": 130, "saturation": 0.5, "brightness": 0.4},
        "海洋": {"primary_h": 190, "saturation": 0.7, "brightness": 0.6},
        "天空": {"primary_h": 200, "saturation": 0.6, "brightness": 0.8},

        # 食物/生活
        "美食": {"primary_h": 30, "saturation": 0.8, "brightness": 0.6},
        "甜品": {"primary_h": 340, "saturation": 0.7, "brightness": 0.7},
        "咖啡": {"primary_h": 25, "saturation": 0.5, "brightness": 0.4},

        # 节日/喜庆
        "圣诞": {"primary_h": 0, "saturation": 0.7, "brightness": 0.5},
        "万圣": {"primary_h": 270, "saturation": 0.8, "brightness": 0.4},
        "春节": {"primary_h": 30, "saturation": 0.9, "brightness": 0.6},

        # 卡通/可爱
        "可爱": {"primary_h": 320, "saturation": 0.6, "brightness": 0.7},
        "卡通": {"primary_h": 200, "saturation": 0.7, "brightness": 0.7},
        "Q版": {"primary_h": 280, "saturation": 0.6, "brightness": 0.75},

        # 复古/经典
        "复古": {"primary_h": 30, "saturation": 0.6, "brightness": 0.5},
        "像素": {"primary_h": 180, "saturation": 0.7, "brightness": 0.55},
        "游戏": {"primary_h": 270, "saturation": 0.8, "brightness": 0.6},

        # 暗黑/神秘
        "暗黑": {"primary_h": 260, "saturation": 0.5, "brightness": 0.25},
        "神秘": {"primary_h": 280, "saturation": 0.6, "brightness": 0.3},
        "恐怖": {"primary_h": 0, "saturation": 0.4, "brightness": 0.2}
    }

    # 情绪色彩配置
    MOOD_CONFIGS = {
        ColorMood.SOFT: {
            "saturation_range": (0.4, 0.6),
            "brightness_range": (0.6, 0.8),
            "contrast": 0.3
        },
        ColorMood.VIBRANT: {
            "saturation_range": (0.7, 0.9),
            "brightness_range": (0.5, 0.7),
            "contrast": 0.6
        },
        ColorMood.DARK: {
            "saturation_range": (0.4, 0.7),
            "brightness_range": (0.15, 0.35),
            "contrast": 0.8
        },
        ColorMood.BRIGHT: {
            "saturation_range": (0.6, 0.8),
            "brightness_range": (0.7, 0.9),
            "contrast": 0.5
        },
        ColorMood.PASTEL: {
            "saturation_range": (0.3, 0.5),
            "brightness_range": (0.75, 0.9),
            "contrast": 0.25
        },
        ColorMood.NEON: {
            "saturation_range": (0.9, 1.0),
            "brightness_range": (0.7, 0.95),
            "contrast": 0.7
        }
    }

    def __init__(self):
        """初始化色彩匹配器"""
        pass

    def generate_color_scheme(
        self,
        game_type: GameType = None,
        theme_keywords: str = "",
        custom_preference: str = None
    ) -> ColorScheme:
        """
        生成色彩方案

        Args:
            game_type: 游戏类型
            theme_keywords: 主题关键词（空格分隔）
            custom_preference: 自定义色彩偏好

        Returns:
            ColorScheme
        """
        logger.info(f"[ColorMatcher] Generating scheme for: {theme_keywords}")

        # 确定色彩情绪
        mood = self._determine_mood(game_type, theme_keywords)

        # 从关键词提取色调
        hue_offset = self._extract_hue_from_keywords(theme_keywords)

        # 获取情绪配置
        mood_config = self.MOOD_CONFIGS.get(mood, self.MOOD_CONFIGS[ColorMood.VIBRANT])

        # 生成配色
        scheme = self._create_scheme(
            base_hue=hue_offset,
            mood=mood,
            mood_config=mood_config
        )

        # 应用自定义偏好
        if custom_preference:
            scheme = self._apply_custom_preference(scheme, custom_preference)

        logger.info(f"[ColorMatcher] Generated {scheme.mood} scheme")
        return scheme

    def _determine_mood(
        self,
        game_type: GameType,
        theme_keywords: str
    ) -> ColorMood:
        """确定色彩情绪"""
        # 优先从关键词判断
        keywords_lower = theme_keywords.lower()

        # 检查关键词中的情绪暗示
        mood_keywords = {
            "soft": ColorMood.SOFT,
            "bright": ColorMood.BRIGHT,
            "dark": ColorMood.DARK,
            "neon": ColorMood.NEON,
            "pastel": ColorMood.PASTEL,
            "vibrant": ColorMood.VIBRANT
        }

        for kw, mood in mood_keywords.items():
            if kw in keywords_lower:
                return mood

        # 检查特定主题
        if any(kw in keywords_lower for kw in ["暗黑", "dark", "恐怖", "恐怖"]):
            return ColorMood.DARK
        if any(kw in keywords_lower for kw in ["可爱", "cute", "治愈", "卡哇伊"]):
            return ColorMood.PASTEL
        if any(kw in keywords_lower for kw in ["霓虹", "neon", "赛博", "cyber"]):
            return ColorMood.NEON

        # 从游戏类型推断
        if game_type:
            return self.GAME_TYPE_MOODS.get(game_type, ColorMood.VIBRANT)

        return ColorMood.VIBRANT

    def _extract_hue_from_keywords(self, keywords: str) -> float:
        """从关键词提取色调"""
        hue_sum = 0
        hue_count = 0

        keywords_lower = keywords.lower()

        for keyword, config in self.THEME_KEYWORDS.items():
            if keyword.lower() in keywords_lower:
                hue_sum += config["primary_h"]
                hue_count += 1

        if hue_count > 0:
            return hue_sum / hue_count

        # 默认色调（蓝紫色）
        return 220

    def _create_scheme(
        self,
        base_hue: float,
        mood: ColorMood,
        mood_config: Dict
    ) -> ColorScheme:
        """创建色彩方案"""
        sat_range = mood_config["saturation_range"]
        bri_range = mood_config["brightness_range"]

        # 生成主色
        primary = self._generate_color(
            hue=base_hue,
            saturation=random.uniform(*sat_range),
            brightness=random.uniform(bri_range[0], bri_range[1])
        )

        # 生成辅助色（主色+30度）
        secondary = self._generate_color(
            hue=(base_hue + 30) % 360,
            saturation=random.uniform(*sat_range),
            brightness=random.uniform(bri_range[0], bri_range[1])
        )

        # 生成点缀色（主色互补）
        accent = self._generate_color(
            hue=(base_hue + 180) % 360,
            saturation=random.uniform(sat_range[0], min(sat_range[1] + 0.1, 1.0)),
            brightness=random.uniform(bri_range[0] + 0.1, min(bri_range[1] + 0.1, 1.0))
        )

        # 生成背景色
        background = self._generate_color(
            hue=base_hue,
            saturation=random.uniform(0.1, 0.3),
            brightness=random.uniform(0.1, 0.25) if mood == ColorMood.DARK else random.uniform(0.9, 0.98)
        )

        # 生成文字色
        text = "#FFFFFF" if random.uniform(0, 1) > 0.5 else "#1A1A2E"

        # 生成渐变色
        gradient_start = primary
        gradient_end = secondary

        # 生成状态色
        success = self._generate_color(hue=120, saturation=0.7, brightness=0.5)
        warning = self._generate_color(hue=30, saturation=0.8, brightness=0.6)
        error = self._generate_color(hue=0, saturation=0.8, brightness=0.5)

        return ColorScheme(
            primary=primary,
            secondary=secondary,
            accent=accent,
            background=background,
            text=text,
            gradient_start=gradient_start,
            gradient_end=gradient_end,
            success=success,
            warning=warning,
            error=error,
            mood=mood.value
        )

    def _generate_color(self, hue: float, saturation: float, brightness: float) -> str:
        """生成十六进制颜色"""
        # 限制范围
        hue = hue % 360
        saturation = max(0, min(1, saturation))
        brightness = max(0, min(1, brightness))

        # HSV转RGB
        r, g, b = colorsys.hsv_to_rgb(hue / 360, saturation, brightness)

        # 转换回十六进制
        return f"#{int(r * 255):02X}{int(g * 255):02X}{int(b * 255):02X}"

    def _apply_custom_preference(
        self,
        scheme: ColorScheme,
        preference: str
    ) -> ColorScheme:
        """应用自定义偏好"""
        pref_lower = preference.lower()

        # 简化处理
        if "warm" in pref_lower:
            # 暖色调
            pass  # 保持当前配色
        elif "cool" in pref_lower:
            # 冷色调
            pass

        return scheme

    def adjust_for_tiktok(self, scheme: ColorScheme) -> ColorScheme:
        """
        调整配色以适配TikTok平台

        TikTok用户偏好高对比度、高饱和度的内容
        """
        logger.info("[ColorMatcher] Adjusting for TikTok platform")

        # TikTok偏好增强
        scheme.secondary = scheme.accent  # 增强辅助色
        scheme.accent = "#FF0050"  # TikTok标志红色

        return scheme

    def generate_gradient_palette(
        self,
        scheme: ColorScheme,
        steps: int = 5
    ) -> List[str]:
        """生成渐变色阶"""
        colors = []

        # 解析主色和辅助色
        start = self._hex_to_hsv(scheme.gradient_start)
        end = self._hex_to_hsv(scheme.gradient_end)

        for i in range(steps):
            t = i / (steps - 1)
            h = start[0] + (end[0] - start[0]) * t
            s = start[1] + (end[1] - start[1]) * t
            v = start[2] + (end[2] - start[2]) * t

            colors.append(self._generate_color(h, s, v))

        return colors

    def _hex_to_hsv(self, hex_color: str) -> Tuple[float, float, float]:
        """十六进制转HSV"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255
        g = int(hex_color[2:4], 16) / 255
        b = int(hex_color[4:6], 16) / 255

        return colorsys.rgb_to_hsv(r, g, b)

    def generate_palette_preview(
        self,
        scheme: ColorScheme,
        output_path: str
    ) -> str:
        """生成调色板预览图"""
        try:
            from PIL import Image, ImageDraw

            width = 800
            height = 200
            img = Image.new('RGB', (width, height))
            draw = ImageDraw.Draw(img)

            colors = [
                scheme.primary,
                scheme.secondary,
                scheme.accent,
                scheme.background,
                scheme.text
            ]

            block_width = width // len(colors)

            for i, color in enumerate(colors):
                x = i * block_width
                draw.rectangle([x, 0, x + block_width, height], fill=color)

            img.save(output_path)
            return output_path

        except ImportError:
            logger.warning("PIL not available, skipping palette preview")
            return ""


def main():
    """主函数测试"""
    print("=" * 60)
    print("Color Matcher Test")
    print("色彩匹配器测试")
    print("=" * 60)
    print()

    matcher = ColorMatcher()

    # 测试生成
    scheme = matcher.generate_color_scheme(
        game_type=GameType.RELAXING,
        theme_keywords="像素 太空 闯关 可爱 外星人",
        custom_preference=None
    )

    print(f"Primary: {scheme.primary}")
    print(f"Secondary: {scheme.secondary}")
    print(f"Accent: {scheme.accent}")
    print(f"Background: {scheme.background}")
    print(f"Mood: {scheme.mood}")
    print()
    print(scheme.to_css_variables())


if __name__ == "__main__":
    main()
