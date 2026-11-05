#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号配图 - AI图片生成模块
支持 MiniMax API 和本地 Stable Diffusion
Author: MiniMax Agent
Version: 1.0.0
"""

import os
import json
import base64
import logging
from typing import Optional, Dict, List
from pathlib import Path
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MiniMaxImageGenerator:
    """MiniMax 图片生成器"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 MiniMax 图片生成器

        Args:
            api_key: MiniMax API 密钥
        """
        self.api_key = api_key or os.getenv("MINIMAX_API_KEY")
        self.api_url = "https://api.minimax.chat/v1/image_generation"
        self.model = "image-01"

        if not self.api_key:
            logger.warning("未设置 MINIMAX_API_KEY 环境变量")

    def generate_image(
        self,
        prompt: str,
        output_path: Optional[str] = None,
        style: str = "photorealistic",
        aspect_ratio: str = "16:9",
        quality: str = "standard"
    ) -> Dict:
        """
        生成图片

        Args:
            prompt: 图片描述提示词
            output_path: 输出路径
            style: 风格 (photorealistic/illustration/flat/artistic)
            aspect_ratio: 宽高比 (1:1/16:9/9:16/4:3/3:2)
            quality: 质量 (standard/high)

        Returns:
            生成结果 {
                "success": bool,
                "image_path": str,
                "prompt": str,
                "message": str
            }
        """
        if not self.api_key:
            return {
                "success": False,
                "image_path": None,
                "prompt": prompt,
                "message": "未配置 API 密钥"
            }

        try:
            import requests

            # 构建请求
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "prompt": self._build_prompt(prompt, style),
                "aspect_ratio": aspect_ratio,
                "response_format": "base64"
            }

            # 发送请求
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code != 200:
                return {
                    "success": False,
                    "image_path": None,
                    "prompt": prompt,
                    "message": f"API 错误: {response.status_code} - {response.text}"
                }

            # 解析响应
            data = response.json()
            image_data = data.get("data", [{}])[0].get("b64_json")

            if not image_data:
                return {
                    "success": False,
                    "image_path": None,
                    "prompt": prompt,
                    "message": "API 返回数据格式错误"
                }

            # 解码并保存图片
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"generated_image_{timestamp}.png"

            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

            image_bytes = base64.b64decode(image_data)
            with open(output_path, "wb") as f:
                f.write(image_bytes)

            logger.info(f"图片已生成: {output_path}")

            return {
                "success": True,
                "image_path": output_path,
                "prompt": prompt,
                "style": style,
                "message": "图片生成成功"
            }

        except ImportError:
            return {
                "success": False,
                "image_path": None,
                "prompt": prompt,
                "message": "requests 库未安装"
            }
        except Exception as e:
            logger.error(f"图片生成失败: {e}")
            return {
                "success": False,
                "image_path": None,
                "prompt": prompt,
                "message": str(e)
            }

    def _build_prompt(self, base_prompt: str, style: str) -> str:
        """构建完整提示词"""
        style_prefixes = {
            "photorealistic": "Photorealistic photograph, professional quality, natural lighting, ",
            "illustration": "Digital illustration, detailed, vibrant colors, ",
            "flat": "Flat design illustration, minimal, clean, modern style, ",
            "artistic": "Artistic painting, expressive, dramatic lighting, ",
            "editorial": "Editorial illustration, magazine quality, sophisticated, "
        }

        prefix = style_prefixes.get(style, "")

        # 添加通用后缀确保质量
        suffix = ", high resolution, 4K, detailed, no text, no watermark"

        return prefix + base_prompt + suffix


class LocalStableDiffusionGenerator:
    """本地 Stable Diffusion 图片生成器"""

    def __init__(
        self,
        api_url: str = "http://localhost:7860",
        model: str = "AnythingV5"
    ):
        """
        初始化本地 SD 生成器

        Args:
            api_url: SD API 地址
            model: 使用的模型名称
        """
        self.api_url = api_url.rstrip("/")
        self.model = model
        self.txt2img_endpoint = f"{self.api_url}/sdapi/v1/txt2img"
        self.sd_models_endpoint = f"{self.api_url}/sdapi/v1/sd-models"

    def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        output_path: Optional[str] = None,
        steps: int = 30,
        cfg_scale: float = 7.0,
        width: int = 768,
        height: int = 512,
        seed: Optional[int] = None
    ) -> Dict:
        """
        使用本地 SD 生成图片

        Args:
            prompt: 正向提示词
            negative_prompt: 负向提示词
            output_path: 输出路径
            steps: 采样步数
            cfg_scale: CFG 强度
            width: 图片宽度
            height: 图片高度
            seed: 随机种子

        Returns:
            生成结果
        """
        try:
            import requests

            # 默认负向提示词
            if negative_prompt is None:
                negative_prompt = (
                    "low quality, worst quality, blurry, "
                    "ugly, deformed, watermark, text, signature"
                )

            payload = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "steps": steps,
                "cfg_scale": cfg_scale,
                "width": width,
                "height": height,
                "seed": seed if seed else -1,
                "batch_size": 1
            }

            response = requests.post(
                self.txt2img_endpoint,
                json=payload,
                timeout=120
            )

            if response.status_code != 200:
                return {
                    "success": False,
                    "image_path": None,
                    "prompt": prompt,
                    "message": f"SD API 错误: {response.status_code}"
                }

            data = response.json()
            images = data.get("images", [])

            if not images:
                return {
                    "success": False,
                    "image_path": None,
                    "prompt": prompt,
                    "message": "未生成图片"
                }

            # 保存图片
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"sd_generated_{timestamp}.png"

            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

            image_data = images[0]
            if "," in image_data:
                image_data = image_data.split(",", 1)[1]

            image_bytes = base64.b64decode(image_data)
            with open(output_path, "wb") as f:
                f.write(image_bytes)

            return {
                "success": True,
                "image_path": output_path,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "seed": data.get("parameters", {}).get("seed", -1),
                "message": "图片生成成功"
            }

        except ImportError:
            return {
                "success": False,
                "image_path": None,
                "prompt": prompt,
                "message": "requests 库未安装"
            }
        except Exception as e:
            return {
                "success": False,
                "image_path": None,
                "prompt": prompt,
                "message": str(e)
            }

    def check_connection(self) -> bool:
        """检查 SD 服务是否可用"""
        try:
            import requests
            response = requests.get(
                f"{self.api_url}/sdapi/v1/ping",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False


class SmartImageGenerator:
    """智能图片生成器 - 自动选择最佳方案"""

    def __init__(self, config: Optional[Dict] = None):
        """
        初始化智能生成器

        Args:
            config: 配置字典
        """
        self.config = config or {}

        # 初始化各生成器
        self.minimax = MiniMaxImageGenerator(
            api_key=self.config.get("minimax_api_key")
        )

        self.local_sd = LocalStableDiffusionGenerator(
            api_url=self.config.get("local_sd_url", "http://localhost:7860"),
            model=self.config.get("local_sd_model", "AnythingV5")
        )

        # 优先级
        self.generation_order = ["minimax", "local_sd"]
        if not self.config.get("minimax_api_key"):
            self.generation_order = ["local_sd"]

    def generate_image(
        self,
        prompt: str,
        output_path: Optional[str] = None,
        preferred_method: Optional[str] = None
    ) -> Dict:
        """
        智能生成图片

        Args:
            prompt: 图片描述
            output_path: 输出路径
            preferred_method: 偏好方法 ("minimax"/"local_sd"/"auto")

        Returns:
            生成结果
        """
        # 如果指定了方法，只用该方法
        if preferred_method and preferred_method != "auto":
            return self._generate_with_method(
                preferred_method, prompt, output_path
            )

        # 按优先级尝试
        for method in self.generation_order:
            result = self._generate_with_method(method, prompt, output_path)
            if result["success"]:
                return result

        # 所有方法都失败
        return {
            "success": False,
            "image_path": None,
            "prompt": prompt,
            "message": "所有图片生成方法均失败"
        }

    def _generate_with_method(
        self,
        method: str,
        prompt: str,
        output_path: Optional[str]
    ) -> Dict:
        """使用指定方法生成图片"""
        if method == "minimax":
            return self.minimax.generate_image(prompt, output_path)
        elif method == "local_sd":
            return self.local_sd.generate_image(prompt, output_path)
        else:
            return {
                "success": False,
                "image_path": None,
                "prompt": prompt,
                "message": f"未知方法: {method}"
            }

    def generate_article_cover(
        self,
        article_title: str,
        article_keywords: List[str],
        style: str = "photorealistic",
        output_path: Optional[str] = None
    ) -> Dict:
        """
        为文章生成封面图

        Args:
            article_title: 文章标题
            article_keywords: 文章关键词
            style: 风格
            output_path: 输出路径

        Returns:
            生成结果
        """
        # 构建封面提示词
        keyword_str = ", ".join(article_keywords[:3])

        cover_prompt = (
            f"{article_title}, {keyword_str}, "
            f"clean composition, {style}, "
            f"professional photography style, "
            f"suitable for article cover, "
            f"no text, no watermark, high quality"
        )

        return self.generate_image(
            prompt=cover_prompt,
            output_path=output_path
        )


# 工具函数
def load_config(config_path: str = "config.json") -> Dict:
    """加载配置文件"""
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(config: Dict, config_path: str = "config.json"):
    """保存配置文件"""
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


# 命令行接口
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI图片生成工具")
    parser.add_argument("prompt", help="图片描述提示词")
    parser.add_argument("-o", "--output", help="输出路径")
    parser.add_argument("-m", "--method",
                       choices=["minimax", "local_sd", "auto"],
                       default="auto",
                       help="生成方法")
    parser.add_argument("-s", "--style",
                       default="photorealistic",
                       help="图片风格")

    args = parser.parse_args()

    generator = SmartImageGenerator()
    result = generator.generate_image(
        prompt=args.prompt,
        output_path=args.output,
        preferred_method=args.method
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))
