"""
Game Art AI Generator - Pixel Art Generator
游戏美术AI生成器 - 像素艺术生成模块

支持多种像素风格，自动调整像素密度和线条粗细
"""

import os
import logging
from typing import Dict, Optional, Any, Tuple, List
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

# 配置日志
logger = logging.getLogger('PixelArtGenerator')


class PixelStyle(Enum):
    """像素风格"""
    RETRO = "retro"           # 复古像素（16/32位）
    CUTE = "cute"            # Q版像素（可爱圆润）
    MINIMAL = "minimal"       # 简约像素（扁平简洁）


@dataclass
class PixelConfig:
    """像素艺术配置"""
    style: PixelStyle = PixelStyle.RETRO
    pixel_size: int = 4       # 像素大小（1-16）
    line_weight: int = 1      # 线条粗细
    color_reduction: int = 32  # 颜色数量
    sharpness: float = 1.5     # 锐度增强
    dithering: bool = False    # 抖动


@dataclass
class PixelArtResult:
    """像素艺术处理结果"""
    success: bool
    input_path: str = ""
    output_path: str = ""
    config: PixelConfig = None
    metadata: Dict = None


class PixelArtGenerator:
    """像素艺术生成器"""

    # 风格预设
    STYLE_PRESETS = {
        PixelStyle.RETRO: {
            "pixel_size": 4,
            "line_weight": 2,
            "color_reduction": 32,
            "sharpness": 1.8,
            "dithering": True
        },
        PixelStyle.CUTE: {
            "pixel_size": 3,
            "line_weight": 1,
            "color_reduction": 48,
            "sharpness": 1.2,
            "dithering": False
        },
        PixelStyle.MINIMAL: {
            "pixel_size": 2,
            "line_weight": 1,
            "color_reduction": 16,
            "sharpness": 1.0,
            "dithering": False
        }
    }

    def __init__(self):
        """初始化像素艺术生成器"""
        pass

    def apply_style(
        self,
        input_path: str,
        output_path: str,
        style: PixelStyle = PixelStyle.RETRO,
        custom_config: Dict = None
    ) -> PixelArtResult:
        """
        应用像素风格到图像

        Args:
            input_path: 输入图像路径
            output_path: 输出路径
            style: 像素风格
            custom_config: 自定义配置

        Returns:
            PixelArtResult
        """
        logger.info(f"[PixelArt] Applying {style.value} style to {input_path}")

        try:
            # 加载图像
            img = Image.open(input_path).convert("RGBA")

            # 获取配置
            config = self._get_config(style, custom_config)

            # 处理图像
            pixelated = self._create_pixel_art(img, config)

            # 锐化
            sharpened = self._sharpen_image(pixelated, config.sharpness)

            # 修复锯齿
            cleaned = self._clean_edges(sharpened)

            # 保存
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            cleaned.save(output_path, "PNG")

            return PixelArtResult(
                success=True,
                input_path=input_path,
                output_path=output_path,
                config=config,
                metadata={
                    "style": style.value,
                    "original_size": img.size,
                    "pixel_size": config.pixel_size
                }
            )

        except Exception as e:
            logger.error(f"[PixelArt] Processing failed: {e}")
            return PixelArtResult(success=False, input_path=input_path)

    def _get_config(self, style: PixelStyle, custom_config: Dict = None) -> PixelConfig:
        """获取配置"""
        preset = self.STYLE_PRESETS.get(style, self.STYLE_PRESETS[PixelStyle.RETRO])

        if custom_config:
            preset.update(custom_config)

        return PixelConfig(
            style=style,
            pixel_size=preset["pixel_size"],
            line_weight=preset["line_weight"],
            color_reduction=preset["color_reduction"],
            sharpness=preset["sharpness"],
            dithering=preset["dithering"]
        )

    def _create_pixel_art(self, img: Image.Image, config: PixelConfig) -> Image.Image:
        """创建像素化图像"""
        # 缩小图像
        w, h = img.size
        new_w = w // config.pixel_size
        new_h = h // config.pixel_size

        # 使用最近邻缩放（保持像素感）
        small = img.resize((new_w, new_h), Image.Resampling.NEAREST)

        # 颜色量化
        quantized = self._quantize_colors(small, config.color_reduction, config.dithering)

        # 放大回原尺寸
        pixelated = quantized.resize((w, h), Image.Resampling.NEAREST)

        return pixelated

    def _quantize_colors(
        self,
        img: Image.Image,
        num_colors: int,
        dithering: bool = False
    ) -> Image.Image:
        """颜色量化"""
        # 使用调色板模式量化
        quantized = img.quantize(colors=num_colors, method=2)

        if dithering:
            # 应用抖动
            return img.convert("RGB").convert("P", dither=Image.Dither.FLOYDSTEINBERG)
        else:
            return quantized

    def _sharpen_image(self, img: Image.Image, factor: float) -> Image.Image:
        """锐化图像"""
        if factor <= 1.0:
            return img

        enhancer = ImageFilter.UnsharpMask(
            radius=1,
            percent=int(factor * 50),
            threshold=3
        )
        return img.filter(enhancer)

    def _clean_edges(self, img: Image.Image) -> Image.Image:
        """清理边缘锯齿"""
        # 创建边缘平滑版本
        smoothed = img.filter(ImageFilter.SMOOTH)

        # 边缘检测
        edge = img.filter(ImageFilter.FIND_EDGES)

        # 合并（保持主体锐利，边缘平滑）
        return Image.composite(img, smoothed, edge.point(lambda x: 128 if x > 0 else 0))

    def generate_from_prompt(
        self,
        prompt: str,
        output_path: str,
        style: PixelStyle = PixelStyle.RETRO,
        size: Tuple[int, int] = (512, 512),
        ai_generator=None
    ) -> PixelArtResult:
        """
        从提示词直接生成像素艺术

        Args:
            prompt: 生成提示词
            output_path: 输出路径
            style: 像素风格
            size: 图像尺寸
            ai_generator: AI图像生成器实例

        Returns:
            PixelArtResult
        """
        logger.info(f"[PixelArt] Generating from prompt: {prompt}")

        if not ai_generator:
            raise ValueError("AI image generator is required for prompt-based generation")

        # 添加像素风格关键词
        style_keywords = {
            PixelStyle.RETRO: "retro pixel art, 16-bit style, sharp pixels",
            PixelStyle.CUTE: "cute pixel art, kawaii style, adorable",
            PixelStyle.MINIMAL: "minimal pixel art, flat, simple"
        }

        enhanced_prompt = f"{prompt}, {style_keywords.get(style, '')}"

        # 使用AI生成
        from image_generator import GenerationConfig
        config = GenerationConfig(
            width=size[0],
            height=size[1],
            style=style.value
        )

        result = ai_generator.generate("prop", enhanced_prompt, config)

        if not result.success:
            return PixelArtResult(success=False)

        # 下载并处理
        image_data = ai_generator._download_image(result.image_url)
        if not image_data:
            return PixelArtResult(success=False)

        # 保存临时文件
        temp_path = output_path + ".temp.png"
        with open(temp_path, 'wb') as f:
            f.write(image_data)

        # 应用像素风格
        final_result = self.apply_style(temp_path, output_path, style)

        # 删除临时文件
        Path(temp_path).unlink(missing_ok=True)

        return final_result

    def batch_process(
        self,
        input_dir: str,
        output_dir: str,
        style: PixelStyle = PixelStyle.RETRO,
        file_patterns: List[str] = None
    ) -> List[PixelArtResult]:
        """
        批量处理像素艺术

        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            style: 像素风格
            file_patterns: 文件匹配模式

        Returns:
            结果列表
        """
        if file_patterns is None:
            file_patterns = ["*.png", "*.jpg", "*.jpeg"]

        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        results = []

        for pattern in file_patterns:
            for file in input_path.glob(pattern):
                rel_path = file.relative_to(input_path)
                out_file = output_path / rel_path.with_suffix(".png")

                result = self.apply_style(
                    str(file),
                    str(out_file),
                    style
                )
                results.append(result)

        return results

    def create_animation_frames(
        self,
        base_image_path: str,
        output_dir: str,
        frame_count: int = 4,
        animation_type: str = "idle",
        style: PixelStyle = PixelStyle.RETRO
    ) -> List[str]:
        """
        创建动画帧

        Args:
            base_image_path: 基础图像路径
            output_dir: 输出目录
            frame_count: 帧数
            animation_type: 动画类型(idle/move/attack/reward)
            style: 像素风格

        Returns:
            帧文件路径列表
        """
        logger.info(f"[PixelArt] Creating {frame_count} animation frames")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        frames = []

        # 动画偏移配置
        animation_configs = {
            "idle": {"offset_y": [0, -2, 0, -2], "scale": [1, 1.02, 1, 1.02]},
            "move": {"offset_x": [0, 2, 0, -2], "offset_y": [0, 0, 0, 0]},
            "attack": {"offset_y": [0, -4, 0, -2], "scale": [1, 1.1, 1, 1.05]},
            "reward": {"offset_y": [0, -6, 0, -3], "scale": [1, 1.2, 1.1, 1]}
        }

        config = animation_configs.get(animation_type, animation_configs["idle"])

        # 加载基础图像
        base_img = Image.open(base_image_path).convert("RGBA")

        for i in range(frame_count):
            frame = base_img.copy()

            # 应用动画变换
            if "offset_x" in config:
                offset_x = config["offset_x"][i]
                offset_y = config["offset_y"][i]
                frame = self._translate_image(frame, offset_x, offset_y)

            if "scale" in config:
                scale = config["scale"][i]
                if scale != 1:
                    frame = self._scale_image(frame, scale)

            # 保存帧
            frame_path = output_path / f"frame_{animation_type}_{i:02d}.png"
            frame.save(frame_path, "PNG")
            frames.append(str(frame_path))

        return frames

    def _translate_image(self, img: Image.Image, dx: int, dy: int) -> Image.Image:
        """图像平移"""
        return Image.transform(
            img,
            img.size,
            Image.Transform.AFFINE,
            (1, 0, dx, 0, 1, dy),
            Image.Resampling.NEAREST
        )

    def _scale_image(self, img: Image.Image, scale: float) -> Image.Image:
        """图像缩放"""
        w, h = img.size
        new_w = int(w * scale)
        new_h = int(h * scale)

        scaled = img.resize((new_w, new_h), Image.Resampling.NEAREST)

        # 居中裁剪回原尺寸
        left = (new_w - w) // 2
        top = (new_h - h) // 2
        return scaled.crop((left, top, left + w, top + h))


def main():
    """主函数测试"""
    print("=" * 60)
    print("Pixel Art Generator Test")
    print("像素艺术生成器测试")
    print("=" * 60)
    print()

    print("使用示例:")
    print("""
    from pixel_art import PixelArtGenerator, PixelStyle, PixelConfig

    # 初始化
    generator = PixelArtGenerator()

    # 应用像素风格
    result = generator.apply_style(
        input_path="input.png",
        output_path="output_pixel.png",
        style=PixelStyle.RETRO
    )

    if result.success:
        print(f"Generated: {result.output_path}")

    # 创建动画帧
    frames = generator.create_animation_frames(
        base_image_path="character.png",
        output_dir="./frames",
        frame_count=4,
        animation_type="idle"
    )
    """)


if __name__ == "__main__":
    main()
