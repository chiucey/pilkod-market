"""
Game Art AI Generator - Image Generator
游戏美术AI生成器 - AI图像生成模块

支持Midjourney API、Stable Diffusion API自动切换调用
"""

import os
import time
import logging
import hashlib
from typing import Dict, Optional, Any, List, Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import base64
import json

import requests

# 配置日志
logger = logging.getLogger('ImageGenerator')


class ImageProvider(Enum):
    """图像生成提供商"""
    MIDJOURNEY = "midjourney"
    STABLE_DIFFUSION = "stable_diffusion"


@dataclass
class GenerationConfig:
    """生成配置"""
    width: int = 512
    height: int = 512
    style: str = "pixel"
    quality: str = "standard"
    seed: Optional[int] = None


@dataclass
class GenerationResult:
    """生成结果"""
    success: bool
    image_path: str = ""
    image_url: str = ""
    prompt: str = ""
    provider: str = ""
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ImageGeneratorError(Exception):
    """图像生成错误"""
    pass


class BaseImageGenerator:
    """图像生成器基类"""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate(self, prompt: str, config: GenerationConfig) -> GenerationResult:
        raise NotImplementedError


class MidjourneyGenerator(BaseImageGenerator):
    """Midjourney图像生成器"""

    ENDPOINT = "https://api.midjourney.com/v1/imagine"

    STYLE_PRESETS = {
        "pixel": "--style pixel-art --pixel",
        "retro": "--style retro-16bit --vibrant",
        "cute": "--style kawaii --cute --pastel",
        "flat": "--style flat-design --minimal",
        "cartoon": "--style cartoon --expressive"
    }

    def __init__(self, api_key: str, webhook_url: str = None):
        super().__init__(api_key)
        self.webhook_url = webhook_url

    def generate(self, prompt: str, config: GenerationConfig) -> GenerationResult:
        """生成图像"""
        logger.info(f"[Midjourney] Generating: {prompt[:50]}...")

        # 添加风格后缀
        style_suffix = self.STYLE_PRESETS.get(config.style, "")
        full_prompt = f"{prompt} {style_suffix}".strip()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "prompt": full_prompt,
            "width": config.width,
            "height": config.height,
            "quality": config.quality,
            " webhook_url": self.webhook_url
        }

        if config.seed:
            payload["seed"] = config.seed

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.ENDPOINT,
                    headers=headers,
                    json=payload,
                    timeout=60
                )

                if response.status_code == 200:
                    data = response.json()
                    image_url = data.get("image_url", "")
                    return GenerationResult(
                        success=True,
                        image_url=image_url,
                        prompt=full_prompt,
                        provider="midjourney",
                        metadata=data
                    )
                elif response.status_code == 429:
                    logger.warning(f"[Midjourney] Rate limited, retrying in 30s...")
                    time.sleep(30)
                else:
                    raise ImageGeneratorError(f"API error: {response.status_code}")

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    logger.warning(f"[Midjourney] Request failed, retrying: {e}")
                    time.sleep(5)
                else:
                    raise ImageGeneratorError(f"Midjourney generation failed: {e}")

        return GenerationResult(success=False, prompt=prompt)


class StableDiffusionGenerator(BaseImageGenerator):
    """Stable Diffusion图像生成器"""

    ENDPOINT = "https://api.stability.ai/v1/generation/{engine}/text-to-image"

    ENGINES = {
        "512": "stable-diffusion-xl-1024-v1-0",
        "1024": "stable-diffusion-xl-1024-v1-0"
    }

    STYLE_GUIDANCE = {
        "pixel": 12,
        "retro": 10,
        "cute": 11,
        "flat": 7,
        "cartoon": 9
    }

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.engine = self.ENGINES["512"]

    def generate(self, prompt: str, config: GenerationConfig) -> GenerationResult:
        """生成图像"""
        logger.info(f"[Stable Diffusion] Generating: {prompt[:50]}...")

        # 添加质量增强词
        quality_boosters = {
            "pixel": "pixel art, 8-bit style, sharp pixels, crisp edges, game asset",
            "retro": "retro game, 16-bit, vibrant colors, nostalgic",
            "cute": "kawaii, cute, pastel colors, adorable",
            "flat": "flat design, minimal, clean, vector style",
            "cartoon": "cartoon style, expressive, vibrant"
        }

        enhanced_prompt = f"{prompt}, {quality_boosters.get(config.style, '')}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "text_prompts": [
                {"text": enhanced_prompt, "weight": 1}
            ],
            "cfg_scale": self.STYLE_GUIDANCE.get(config.style, 7),
            "height": config.height,
            "width": config.width,
            "samples": 1,
            "steps": 30
        }

        if config.seed:
            payload["seed"] = config.seed

        max_retries = 3
        for attempt in range(max_retries):
            try:
                url = self.ENDPOINT.format(engine=self.engine)
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=120
                )

                if response.status_code == 200:
                    data = response.json()
                    # 从base64提取图像
                    if "artifacts" in data and len(data["artifacts"]) > 0:
                        image_base64 = data["artifacts"][0]["base64"]
                        return GenerationResult(
                            success=True,
                            image_url=f"data:image/png;base64,{image_base64}",
                            prompt=enhanced_prompt,
                            provider="stable_diffusion",
                            metadata=data
                        )
                elif response.status_code == 429:
                    logger.warning(f"[SD] Rate limited, retrying in 30s...")
                    time.sleep(30)
                else:
                    raise ImageGeneratorError(f"API error: {response.status_code}")

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    logger.warning(f"[SD] Request failed, retrying: {e}")
                    time.sleep(5)
                else:
                    raise ImageGeneratorError(f"Stable Diffusion generation failed: {e}")

        return GenerationResult(success=False, prompt=prompt)


class AIImageGenerator:
    """AI图像生成器（双API自动切换）"""

    # 素材类型对应的最优API
    ASSET_TO_PROVIDER = {
        "icon": "midjourney",           # 图标用MJ更精美
        "character": "midjourney",      # 角色用MJ效果更好
        "background": "stable_diffusion",  # 背景用SD效率高
        "ui": "stable_diffusion",       # UI组件SD足够
        "prop": "midjourney",           # 道具用MJ更精细
        "default": "midjourney"
    }

    def __init__(
        self,
        midjourney_key: str = None,
        stable_diffusion_key: str = None,
        webhook_url: str = None
    ):
        """
        初始化生成器

        Args:
            midjourney_key: Midjourney API密钥
            stable_diffusion_key: Stable Diffusion API密钥
            webhook_url: Midjourney回调URL
        """
        self.mj_generator = None
        self.sd_generator = None

        if midjourney_key:
            self.mj_generator = MidjourneyGenerator(midjourney_key, webhook_url)

        if stable_diffusion_key:
            self.sd_generator = StableDiffusionGenerator(stable_diffusion_key)

        if not self.mj_generator and not self.sd_generator:
            raise ImageGeneratorError("At least one API key is required")

    def generate(
        self,
        asset_type: str,
        prompt: str,
        config: GenerationConfig = None,
        force_provider: str = None
    ) -> GenerationResult:
        """
        生成图像（自动选择最优API）

        Args:
            asset_type: 素材类型(icon/character/background/ui/prop)
            prompt: 生成提示词
            config: 生成配置
            force_provider: 强制使用的提供商

        Returns:
            GenerationResult
        """
        if config is None:
            config = GenerationConfig()

        # 选择提供商
        if force_provider == "midjourney":
            provider = ImageProvider.MIDJOURNEY
        elif force_provider == "stable_diffusion":
            provider = ImageProvider.STABLE_DIFFUSION
        else:
            # 根据素材类型自动选择
            provider_name = self.ASSET_TO_PROVIDER.get(asset_type, "default")
            provider = ImageProvider.MIDJOURNEY if provider_name == "midjourney" else ImageProvider.STABLE_DIFFUSION

        # 尝试主提供商
        result = self._try_generate(provider, prompt, config)

        # 如果失败，尝试备用提供商
        if not result.success:
            alt_provider = (
                ImageProvider.STABLE_DIFFUSION
                if provider == ImageProvider.MIDJOURNEY
                else ImageProvider.MIDJOURNEY
            )
            logger.info(f"[Generator] Primary provider failed, trying backup...")
            result = self._try_generate(alt_provider, prompt, config)

        return result

    def _try_generate(
        self,
        provider: ImageProvider,
        prompt: str,
        config: GenerationConfig
    ) -> GenerationResult:
        """尝试使用指定提供商生成"""
        if provider == ImageProvider.MIDJOURNEY:
            if not self.mj_generator:
                return GenerationResult(success=False, prompt=prompt)
            return self.mj_generator.generate(prompt, config)
        else:
            if not self.sd_generator:
                return GenerationResult(success=False, prompt=prompt)
            return self.sd_generator.generate(prompt, config)

    def generate_batch(
        self,
        asset_list: List[Dict[str, str]],
        output_dir: str,
        on_progress: Callable[[int, int, GenerationResult], None] = None
    ) -> List[GenerationResult]:
        """
        批量生成图像

        Args:
            asset_list: 素材列表 [{"type": "icon", "prompt": "..."}, ...]
            output_dir: 输出目录
            on_progress: 进度回调

        Returns:
            结果列表
        """
        results = []
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        for i, asset in enumerate(asset_list):
            asset_type = asset.get("type", "default")
            prompt = asset.get("prompt", "")
            filename = asset.get("filename", f"{asset_type}_{i}.png")

            config = GenerationConfig(
                width=asset.get("width", 512),
                height=asset.get("height", 512),
                style=asset.get("style", "pixel")
            )

            result = self.generate(asset_type, prompt, config)

            # 保存图像
            if result.success and result.image_url:
                image_data = self._download_image(result.image_url)
                if image_data:
                    filepath = output_path / filename
                    with open(filepath, 'wb') as f:
                        f.write(image_data)
                    result.image_path = str(filepath)

            results.append(result)

            if on_progress:
                on_progress(i + 1, len(asset_list), result)

            # 避免API限流
            if i < len(asset_list) - 1:
                time.sleep(2)

        return results

    def _download_image(self, image_url: str) -> Optional[bytes]:
        """下载图像"""
        try:
            if image_url.startswith("data:"):
                # base64编码的图像
                base64_data = image_url.split(",")[1]
                return base64.b64decode(base64_data)
            else:
                response = requests.get(image_url, timeout=30)
                if response.status_code == 200:
                    return response.content
        except Exception as e:
            logger.error(f"Image download failed: {e}")

        return None

    def is_available(self, provider: str = None) -> Dict[str, bool]:
        """检查API可用性"""
        result = {
            "midjourney": self.mj_generator is not None,
            "stable_diffusion": self.sd_generator is not None
        }

        if provider:
            return result.get(provider, False)

        return result


def main():
    """主函数测试"""
    print("=" * 60)
    print("AI Image Generator Test")
    print("AI图像生成器测试")
    print("=" * 60)
    print()

    print("使用示例:")
    print("""
    from image_generator import AIImageGenerator, GenerationConfig

    # 初始化（需要至少一个API密钥）
    generator = AIImageGenerator(
        midjourney_key="your_mj_key",
        stable_diffusion_key="your_sd_key"
    )

    # 生成单个图像
    config = GenerationConfig(
        width=512,
        height=512,
        style="pixel"
    )

    result = generator.generate(
        asset_type="icon",
        prompt="cute space alien character pixel art",
        config=config
    )

    if result.success:
        print(f"Generated: {result.image_path}")
        print(f"Provider: {result.provider}")
    """)


if __name__ == "__main__":
    main()
