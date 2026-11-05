"""
Game Art AI Generator - Main Controller
游戏美术AI生成器 - 主协调脚本

整合所有模块，提供完整的游戏美术素材自动生成服务
"""

import os
import sys
import json
import logging
from typing import Dict, Optional, Any, List, Callable
from pathlib import Path
from dataclasses import dataclass

from image_generator import AIImageGenerator, GenerationConfig
from pixel_art import PixelArtGenerator, PixelStyle
from color_matcher import ColorMatcher, ColorScheme, GameType
from ui_generator import UIGenerator
from sound_generator import SoundMatcher
from asset_packer import AssetPacker
from sync_manager import SyncManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('GameArtGenerator')


@dataclass
class GameArtRequest:
    """游戏美术请求"""
    game_type: str  # 解压闯关/合成养成/敏捷挑战/趣味竞技/放置收集
    theme_keywords: str  # 主题关键词
    art_style: str = "pixel"  # 像素/扁平/卡通
    color_preference: str = None  # 自定义色彩偏好
    icon_size: str = "512x512"
    pixel_style: str = "retro"  # 复古/Q版/简约
    generate_sound: bool = True


@dataclass
class GameArtResult:
    """游戏美术生成结果"""
    success: bool
    package_path: str = ""
    color_scheme: Dict = None
    assets_summary: Dict = None
    error_message: str = ""
    pipeline_config: Dict = None

    def __post_init__(self):
        if self.color_scheme is None:
            self.color_scheme = {}
        if self.assets_summary is None:
            self.assets_summary = {}


class GameArtGenerator:
    """游戏美术AI生成器主类"""

    # 游戏类型映射
    GAME_TYPE_MAP = {
        "解压闯关": GameType.RELAXING,
        "合成养成": GameType.BREEDING,
        "敏捷挑战": GameType.SKILL,
        "趣味竞技": GameType.COMPETITIVE,
        "放置收集": GameType.IDLE
    }

    # 像素风格映射
    PIXEL_STYLE_MAP = {
        "复古": PixelStyle.RETRO,
        "Q版": PixelStyle.CUTE,
        "简约": PixelStyle.MINIMAL,
        "retro": PixelStyle.RETRO,
        "cute": PixelStyle.CUTE,
        "minimal": PixelStyle.MINIMAL
    }

    def __init__(
        self,
        output_dir: str = "./generated",
        workspace_dir: str = "./workspace",
        midjourney_key: str = None,
        stable_diffusion_key: str = None
    ):
        """
        初始化游戏美术生成器

        Args:
            output_dir: 素材输出目录
            workspace_dir: 工作区目录
            midjourney_key: Midjourney API密钥
            stable_diffusion_key: Stable Diffusion API密钥
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

        # 初始化各模块
        self.image_generator = None
        if midjourney_key or stable_diffusion_key:
            self.image_generator = AIImageGenerator(
                midjourney_key=midjourney_key,
                stable_diffusion_key=stable_diffusion_key
            )

        self.pixel_generator = PixelArtGenerator()
        self.color_matcher = ColorMatcher()
        self.ui_generator = None  # 延迟初始化
        self.sound_generator = None  # 延迟初始化
        self.asset_packer = AssetPacker(str(self.output_dir))
        self.sync_manager = SyncManager(workspace_dir=str(self.workspace_dir))

        # 状态
        self._current_request: GameArtRequest = None
        self._generated_assets: Dict[str, List[str]] = {}

    def generate(
        self,
        request: GameArtRequest,
        on_progress: Callable[[str, float, Dict], None] = None
    ) -> GameArtResult:
        """
        生成游戏美术素材包

        Args:
            request: 生成请求
            on_progress: 进度回调(step, progress, details)

        Returns:
            GameArtResult
        """
        self._current_request = request
        self._generated_assets = {}

        logger.info(f"[Generator] Starting generation for: {request.theme_keywords}")

        def progress(step: str, pct: float, details: Dict = None):
            logger.info(f"[{step}] {pct:.1f}%")
            if on_progress:
                on_progress(step, pct, details or {})

        try:
            # Step 1: 色彩方案生成
            progress("Color Scheme", 5.0)
            color_scheme = self._generate_color_scheme(request)
            self._generated_assets["color_scheme"] = color_scheme.to_dict()

            # Step 2: UI组件生成
            progress("UI Components", 10.0)
            ui_assets = self._generate_ui_components(request, color_scheme)
            self._generated_assets["ui"] = ui_assets

            # Step 3: 游戏元素生成（如果AI生成器可用）
            progress("Game Elements", 30.0)
            element_assets = self._generate_game_elements(request, color_scheme)
            self._generated_assets.update(element_assets)

            # Step 4: 音效匹配（生成元数据）
            if request.generate_sound:
                progress("Sound Assets", 80.0)
                sound_assets = self._generate_sound_metadata(request)
                self._generated_assets["sound"] = sound_assets

            # Step 5: 素材打包
            progress("Packaging", 90.0)
            package_result = self._create_asset_package(request)

            # Step 6: 准备流水线配置
            progress("Pipeline Config", 95.0)
            pipeline_config = self.sync_manager.generate_pipeline_script()

            progress("Complete", 100.0)

            return GameArtResult(
                success=True,
                package_path=package_result.package_path,
                color_scheme=color_scheme.to_dict(),
                assets_summary=self._generate_summary(),
                pipeline_config=pipeline_config
            )

        except Exception as e:
            logger.error(f"[Generator] Generation failed: {e}")
            return GameArtResult(
                success=False,
                error_message=str(e)
            )

    def _generate_color_scheme(self, request: GameArtRequest) -> ColorScheme:
        """生成色彩方案"""
        # 获取游戏类型
        game_type = self.GAME_TYPE_MAP.get(request.game_type)

        # 生成配色
        color_scheme = self.color_matcher.generate_color_scheme(
            game_type=game_type,
            theme_keywords=request.theme_keywords,
            custom_preference=request.color_preference
        )

        # TikTok适配调整
        color_scheme = self.color_matcher.adjust_for_tiktok(color_scheme)

        logger.info(f"[Generator] Color scheme: {color_scheme.mood}")
        return color_scheme

    def _generate_ui_components(
        self,
        request: GameArtRequest,
        color_scheme: ColorScheme
    ) -> List[str]:
        """生成UI组件"""
        if self.ui_generator is None:
            self.ui_generator = UIGenerator(color_scheme.to_dict())

        # 设置色彩
        self.ui_generator.set_color_scheme(color_scheme.to_dict())

        # 生成完整UI集
        game_name = request.theme_keywords.replace(" ", "_")[:20]
        ui_dir = self.output_dir / "ui"
        ui_dir.mkdir(parents=True, exist_ok=True)

        components = self.ui_generator.generate_full_ui_set(game_name, str(ui_dir))

        # 收集生成的文件
        files = []
        for category, comp_list in components.items():
            for comp in comp_list:
                files.append(comp.file_path)

        return files

    def _generate_game_elements(
        self,
        request: GameArtRequest,
        color_scheme: ColorScheme
    ) -> Dict[str, List[str]]:
        """生成游戏元素"""
        assets = {}

        if self.image_generator is None:
            logger.warning("[Generator] No AI image generator, skipping element generation")
            return assets

        # 确定像素风格
        pixel_style = self.PIXEL_STYLE_MAP.get(request.pixel_style, PixelStyle.RETRO)

        # 生成图标
        icons_dir = self.output_dir / "icons"
        icons_dir.mkdir(parents=True, exist_ok=True)
        icon_files = self._generate_icons(request, icons_dir, pixel_style)
        assets["icons"] = icon_files

        # 生成角色
        chars_dir = self.output_dir / "characters"
        chars_dir.mkdir(parents=True, exist_ok=True)
        char_files = self._generate_characters(request, chars_dir, pixel_style)
        assets["characters"] = char_files

        # 生成道具
        props_dir = self.output_dir / "props"
        props_dir.mkdir(parents=True, exist_ok=True)
        prop_files = self._generate_props(request, props_dir, pixel_style)
        assets["props"] = prop_files

        # 生成背景
        bg_dir = self.output_dir / "backgrounds"
        bg_dir.mkdir(parents=True, exist_ok=True)
        bg_files = self._generate_backgrounds(request, bg_dir, pixel_style)
        assets["backgrounds"] = bg_files

        return assets

    def _generate_icons(
        self,
        request: GameArtRequest,
        output_dir: Path,
        pixel_style: PixelStyle
    ) -> List[str]:
        """生成游戏图标"""
        files = []

        prompts = [
            f"{request.theme_keywords} game icon, logo, centered, transparent background",
            f"{request.theme_keywords} app icon, simple design, clean, high contrast",
            f"{request.theme_keywords} game logo, stylized, memorable"
        ]

        for i, prompt in enumerate(prompts):
            try:
                result = self.image_generator.generate(
                    asset_type="icon",
                    prompt=prompt,
                    config=GenerationConfig(
                        width=512,
                        height=512,
                        style=request.art_style
                    )
                )

                if result.success:
                    # 下载并处理像素风格
                    if result.image_url:
                        image_data = self.image_generator._download_image(result.image_url)
                        if image_data:
                            temp_path = output_dir / f"icon_temp_{i}.png"
                            with open(temp_path, 'wb') as f:
                                f.write(image_data)

                            # 应用像素风格
                            final_path = output_dir / f"icon_{i+1}.png"
                            self.pixel_generator.apply_style(
                                str(temp_path),
                                str(final_path),
                                pixel_style
                            )
                            files.append(str(final_path))

                            # 删除临时文件
                            temp_path.unlink(missing_ok=True)

            except Exception as e:
                logger.warning(f"[Generator] Icon {i} generation failed: {e}")

        return files

    def _generate_characters(
        self,
        request: GameArtRequest,
        output_dir: Path,
        pixel_style: PixelStyle
    ) -> List[str]:
        """生成角色"""
        files = []

        prompts = [
            f"{request.theme_keywords} main character, cute, pixel art style",
            f"{request.theme_keywords} NPC character, friendly, pixel art"
        ]

        for i, prompt in enumerate(prompts):
            try:
                result = self.image_generator.generate(
                    asset_type="character",
                    prompt=prompt,
                    config=GenerationConfig(
                        width=256,
                        height=256,
                        style=request.art_style
                    )
                )

                if result.success and result.image_url:
                    # 下载图像
                    image_data = self.image_generator._download_image(result.image_url)
                    if image_data:
                        char_path = output_dir / f"char_{i}_temp.png"
                        with open(char_path, 'wb') as f:
                            f.write(image_data)

                        # 应用像素风格
                        final_path = output_dir / f"char_{i}.png"
                        self.pixel_generator.apply_style(
                            str(char_path),
                            str(final_path),
                            pixel_style
                        )
                        files.append(str(final_path))

                        # 生成动画帧
                        frames_dir = output_dir.parent / "animations"
                        frames_dir.mkdir(exist_ok=True)
                        self.pixel_generator.create_animation_frames(
                            str(final_path),
                            str(frames_dir),
                            frame_count=4,
                            animation_type="idle",
                            style=pixel_style
                        )

                        char_path.unlink(missing_ok=True)

            except Exception as e:
                logger.warning(f"[Generator] Character {i} generation failed: {e}")

        return files

    def _generate_props(
        self,
        request: GameArtRequest,
        output_dir: Path,
        pixel_style: PixelStyle
    ) -> List[str]:
        """生成道具"""
        files = []

        prop_prompts = [
            f"{request.theme_keywords} gold coin, collectible, shiny",
            f"{request.theme_keywords} power up item, glowing",
            f"{request.theme_keywords} obstacle object, game asset",
            f"{request.theme_keywords} reward chest, treasure",
            f"{request.theme_keywords} special item, rare"
        ]

        for i, prompt in enumerate(prop_prompts):
            try:
                result = self.image_generator.generate(
                    asset_type="prop",
                    prompt=prompt,
                    config=GenerationConfig(
                        width=128,
                        height=128,
                        style=request.art_style
                    )
                )

                if result.success and result.image_url:
                    image_data = self.image_generator._download_image(result.image_url)
                    if image_data:
                        temp_path = output_dir / f"prop_{i}_temp.png"
                        with open(temp_path, 'wb') as f:
                            f.write(image_data)

                        final_path = output_dir / f"prop_{i+1}.png"
                        self.pixel_generator.apply_style(
                            str(temp_path),
                            str(final_path),
                            pixel_style
                        )
                        files.append(str(final_path))
                        temp_path.unlink(missing_ok=True)

            except Exception as e:
                logger.warning(f"[Generator] Prop {i} generation failed: {e}")

        return files

    def _generate_backgrounds(
        self,
        request: GameArtRequest,
        output_dir: Path,
        pixel_style: PixelStyle
    ) -> List[str]:
        """生成背景"""
        files = []

        bg_prompts = [
            f"{request.theme_keywords} game background, main menu, parallax layers",
            f"{request.theme_keywords} level background, game scenery, detailed",
            f"{request.theme_keywords} sky background, seamless, tileable"
        ]

        for i, prompt in enumerate(bg_prompts):
            try:
                result = self.image_generator.generate(
                    asset_type="background",
                    prompt=prompt,
                    config=GenerationConfig(
                        width=800,
                        height=600,
                        style="flat"  # 背景用扁平风格更合适
                    )
                )

                if result.success and result.image_url:
                    image_data = self.image_generator._download_image(result.image_url)
                    if image_data:
                        bg_path = output_dir / f"bg_{i+1}.png"
                        with open(bg_path, 'wb') as f:
                            f.write(image_data)
                        files.append(str(bg_path))

            except Exception as e:
                logger.warning(f"[Generator] Background {i} generation failed: {e}")

        return files

    def _generate_sound_metadata(self, request: GameArtRequest) -> Dict:
        """生成音效元数据"""
        # 初始化音效生成器
        self.sound_generator = SoundMatcher(
            theme_keywords=request.theme_keywords,
            game_type=request.game_type,
            output_dir=str(self.output_dir / "audio")
        )

        # 保存音效元数据
        sound_dir = self.output_dir / "audio"
        sound_dir.mkdir(parents=True, exist_ok=True)
        metadata_path = self.sound_generator.save_metadata(
            str(sound_dir / "sound_metadata.json")
        )

        return {
            "metadata_path": metadata_path,
            "manifest": self.sound_generator.create_sound_manifest()
        }

    def _create_asset_package(self, request: GameArtRequest):
        """创建素材包"""
        package_name = f"{request.theme_keywords.replace(' ', '_')[:15]}_assets"

        # 设置素材包路径到同步管理器
        self.sync_manager.set_asset_package(str(self.output_dir))

        # 打包
        result = self.asset_packer.create_package(
            package_name=package_name,
            source_dir=str(self.output_dir),
            game_info={
                "name": request.theme_keywords,
                "type": request.game_type,
                "theme": request.theme_keywords,
                "style": request.art_style
            }
        )

        logger.info(f"[Generator] Package created: {result.package_path}")
        return result

    def _generate_summary(self) -> Dict:
        """生成素材摘要"""
        summary = {}

        for category, files in self._generated_assets.items():
            if isinstance(files, list):
                summary[category] = {
                    "count": len(files),
                    "files": [Path(f).name for f in files if f]
                }
            else:
                summary[category] = files

        return summary

    def sync_to_c3p(self, c3p_project_path: str) -> Dict:
        """同步素材到C3P项目"""
        result = self.sync_manager.sync_to_c3p(
            package_path=self.output_dir / f"{self._current_request.theme_keywords[:15]}_assets.zip",
            c3p_project_path=c3p_project_path
        )
        return {"success": result.success, "message": result.message}

    def prepare_tiktok_publish(self, game_title: str = None) -> Dict:
        """准备TikTok发布"""
        return self.sync_manager.prepare_for_tiktok(
            asset_package_path=self.output_dir / f"{self._current_request.theme_keywords[:15]}_assets.zip",
            game_title=game_title or self._current_request.theme_keywords
        )


def main():
    """测试"""
    print("=" * 60)
    print("Game Art AI Generator")
    print("游戏美术AI生成器")
    print("=" * 60)
    print()

    generator = GameArtGenerator()

    # 示例请求
    request = GameArtRequest(
        game_type="敏捷挑战",
        theme_keywords="复古像素 太空闯关 可爱外星人",
        art_style="pixel",
        pixel_style="复古",
        generate_sound=True
    )

    # 生成（需要API密钥才能完整运行）
    # result = generator.generate(request)

    print("使用示例:")
    print("""
    from main import GameArtGenerator, GameArtRequest

    # 初始化
    generator = GameArtGenerator(
        midjourney_key="your_mj_key",
        stable_diffusion_key="your_sd_key"
    )

    # 创建请求
    request = GameArtRequest(
        game_type="敏捷挑战",
        theme_keywords="复古像素 太空闯关 可爱外星人",
        art_style="pixel",
        pixel_style="复古"
    )

    # 生成素材
    result = generator.generate(request, on_progress=lambda step, pct, details:
        print(f"[{step}] {pct:.1f}%")
    )

    if result.success:
        print(f"素材包: {result.package_path}")

        # 同步到C3P
        generator.sync_to_c3p("path/to/project.c3p")

        # 准备TikTok发布
        config = generator.prepare_tiktok_publish("My Space Game")
    """)


if __name__ == "__main__":
    main()
