#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号配图 - 图片搜索模块
支持 Unsplash 和 Pexels 版权免费图片搜索
Author: MiniMax Agent
Version: 1.0.0
"""

import requests
import json
import os
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlencode
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageSearcher:
    """图片搜索引擎 - 支持多源搜索"""

    def __init__(
        self,
        unsplash_api_key: Optional[str] = None,
        pexels_api_key: Optional[str] = None
    ):
        """
        初始化图片搜索引擎

        Args:
            unsplash_api_key: Unsplash API密钥
            pexels_api_key: Pexels API密钥
        """
        self.unsplash_api_key = unsplash_api_key or os.getenv("UNSPLASH_API_KEY")
        self.pexels_api_key = pexels_api_key or os.getenv("PEXELS_API_KEY")

        self.search_sources = []
        if self.unsplash_api_key:
            self.search_sources.append("unsplash")
        if self.pexels_api_key:
            self.search_sources.append("pexels")

        if not self.search_sources:
            logger.warning("未配置任何图片搜索API，将使用演示模式")

    def search_images(
        self,
        keywords: List[str],
        count: int = 10,
        orientation: str = "landscape",
        exclude_watermarked: bool = True
    ) -> List[Dict]:
        """
        搜索版权免费图片

        Args:
            keywords: 搜索关键词列表
            count: 返回图片数量
            orientation: 图片方向 (landscape/portrait/squarish)
            exclude_watermarked: 是否排除有水印图片

        Returns:
            图片信息列表
        """
        # 组合搜索关键词
        search_query = " ".join(keywords)
        if exclude_watermarked:
            search_query += " no watermark"

        all_results = []

        # 按优先级搜索
        for source in self.search_sources:
            try:
                if source == "unsplash":
                    results = self._search_unsplash(search_query, count, orientation)
                elif source == "pexels":
                    results = self._search_pexels(search_query, count, orientation)
                else:
                    results = []

                # 标记来源并添加到结果
                for img in results:
                    img["source"] = source
                    all_results.append(img)

            except Exception as e:
                logger.error(f"{source} 搜索失败: {e}")

        # 如果没有API结果，返回演示数据
        if not all_results:
            logger.info("使用演示模式返回示例图片")
            all_results = self._get_demo_results(search_query)

        # 去重（基于URL）
        seen_urls = set()
        unique_results = []
        for img in all_results:
            if img["url"] not in seen_urls:
                seen_urls.add(img["url"])
                unique_results.append(img)

        return unique_results[:count]

    def _search_unsplash(
        self,
        query: str,
        count: int,
        orientation: str
    ) -> List[Dict]:
        """搜索 Unsplash 图片"""
        url = "https://api.unsplash.com/search/photos"
        headers = {
            "Authorization": f"Client-ID {self.unsplash_api_key}"
        }
        params = {
            "query": query,
            "per_page": count,
            "orientation": orientation
        }

        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []
        for photo in data.get("results", []):
            results.append({
                "id": photo.get("id"),
                "url": photo["urls"]["regular"],
                "thumb_url": photo["urls"]["thumb"],
                "download_url": photo["links"]["download_location"],
                "width": photo["width"],
                "height": photo["height"],
                "description": photo.get("description") or photo.get("alt_description", ""),
                "photographer": photo["user"]["name"],
                "photographer_url": photo["user"]["links"]["html"],
                "is_watermarked": False,  # Unsplash图片无水印
                "license": "Unsplash License"
            })

        logger.info(f"Unsplash 返回 {len(results)} 张图片")
        return results

    def _search_pexels(
        self,
        query: str,
        count: int,
        orientation: str
    ) -> List[Dict]:
        """搜索 Pexels 图片"""
        url = "https://api.pexels.com/v1/search"
        headers = {
            "Authorization": self.pexels_api_key
        }
        params = {
            "query": query,
            "per_page": count,
            "orientation": orientation
        }

        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []
        for photo in data.get("photos", []):
            results.append({
                "id": str(photo.get("id")),
                "url": photo["src"]["large"],
                "thumb_url": photo["src"]["tiny"],
                "download_url": photo["src"]["original"],
                "width": photo["width"],
                "height": photo["height"],
                "description": photo.get("alt", ""),
                "photographer": photo["photographer"],
                "photographer_url": photo["photographer_url"],
                "is_watermarked": False,  # Pexels图片无水印
                "license": "Pexels License"
            })

        logger.info(f"Pexels 返回 {len(results)} 张图片")
        return results

    def _get_demo_results(self, query: str) -> List[Dict]:
        """返回演示数据"""
        return [
            {
                "id": "demo_1",
                "url": f"https://source.unsplash.com/featured/900x600?{query}",
                "thumb_url": f"https://source.unsplash.com/featured/300x200?{query}",
                "width": 900,
                "height": 600,
                "description": f"关于 {query} 的演示图片",
                "photographer": "Demo User",
                "photographer_url": "#",
                "is_watermarked": False,
                "license": "Demo License",
                "source": "demo"
            }
        ]

    def download_image(self, url: str, save_path: str) -> bool:
        """
        下载图片到本地

        Args:
            url: 图片URL
            save_path: 保存路径

        Returns:
            是否下载成功
        """
        try:
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()

            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"图片已保存: {save_path}")
            return True

        except Exception as e:
            logger.error(f"图片下载失败: {e}")
            return False


class ImageAnalyzer:
    """图片分析器 - 检测水印和图片质量"""

    @staticmethod
    def check_watermark(image_path: str) -> Dict:
        """
        检测图片是否有水印

        Args:
            image_path: 图片路径

        Returns:
            检测结果 {
                "has_watermark": bool,
                "confidence": float,
                "watermark_location": str,
                "suggested_action": str
            }
        """
        try:
            import cv2
            import numpy as np

            # 读取图片
            img = cv2.imread(image_path)
            if img is None:
                return {
                    "has_watermark": False,
                    "confidence": 0.0,
                    "watermark_location": "unknown",
                    "suggested_action": "skip"
                }

            # 转换为灰度图
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # 边缘检测
            edges = cv2.Canny(gray, 50, 150)

            # 查找轮廓
            contours, _ = cv2.findContours(
                edges,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )

            # 分析可疑区域
            suspicious_regions = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100 and area < img.shape[0] * img.shape[1] * 0.1:
                    x, y, w, h = cv2.boundingRect(contour)
                    suspicious_regions.append({
                        "location": "bottom-right" if y > img.shape[0] * 0.7 else "other",
                        "area": area,
                        "bbox": (x, y, w, h)
                    })

            # 检测半透明白色区域（水印特征）
            lower_white = np.array([200, 200, 200])
            upper_white = np.array([255, 255, 255])
            white_mask = cv2.inRange(img, lower_white, upper_white)

            white_ratio = np.sum(white_mask > 0) / white_mask.size

            has_watermark = (
                len(suspicious_regions) > 0 or
                white_ratio > 0.05
            )

            return {
                "has_watermark": has_watermark,
                "confidence": 0.8 if has_watermark else 0.3,
                "watermark_location": (
                    suspicious_regions[0]["location"]
                    if suspicious_regions else "unknown"
                ),
                "suggested_action": "remove" if has_watermark else "use_directly"
            }

        except ImportError:
            logger.warning("OpenCV未安装，使用基础水印检测")
            return {
                "has_watermark": False,
                "confidence": 0.0,
                "watermark_location": "unknown",
                "suggested_action": "manual_check"
            }

    @staticmethod
    def analyze_image_quality(image_path: str) -> Dict:
        """
        分析图片质量

        Args:
            image_path: 图片路径

        Returns:
            质量分析结果
        """
        try:
            from PIL import Image
            import math

            img = Image.open(image_path)
            width, height = img.size

            # 检查分辨率
            resolution_score = 1.0
            if width < 600 or height < 400:
                resolution_score = 0.5
            elif width < 900 or height < 600:
                resolution_score = 0.8

            # 检查宽高比
            aspect_ratio = width / height
            aspect_score = 1.0
            if 0.8 <= aspect_ratio <= 1.2:
                aspect_type = "square"
            elif 1.2 <= aspect_ratio <= 1.8:
                aspect_type = "landscape"
            else:
                aspect_type = "portrait"

            return {
                "width": width,
                "height": height,
                "aspect_ratio": round(aspect_ratio, 2),
                "aspect_type": aspect_type,
                "resolution_score": resolution_score,
                "suitable_for_wechat": width >= 900 and resolution_score >= 0.8,
                "format": img.format,
                "mode": img.mode
            }

        except ImportError:
            return {
                "suitable_for_wechat": True,
                "error": "PIL未安装，无法完整分析"
            }


def extract_keywords_from_text(text: str, max_keywords: int = 5) -> List[str]:
    """
    从文章中提取关键词用于图片搜索

    Args:
        text: 文章文本
        max_keywords: 最大关键词数量

    Returns:
        关键词列表
    """
    # 简单实现：去除停用词后取名词
    stop_words = {
        "的", "了", "在", "是", "我", "有", "和", "就", "不", "人",
        "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去",
        "你", "会", "着", "没有", "看", "好", "自己", "这", "那"
    }

    # 简单分词（按空格和标点）
    import re
    words = re.findall(r'[\w]+', text)

    # 过滤停用词和短词
    keywords = [
        w for w in words
        if w not in stop_words and len(w) >= 2
    ]

    # 统计词频
    from collections import Counter
    word_freq = Counter(keywords)

    # 返回高频词
    return [word for word, _ in word_freq.most_common(max_keywords)]


# 示例用法
if __name__ == "__main__":
    # 测试代码
    searcher = ImageSearcher()

    # 测试搜索
    keywords = ["technology", "business", "modern"]
    results = searcher.search_images(keywords, count=5)

    print(f"找到 {len(results)} 张图片:")
    for i, img in enumerate(results):
        print(f"{i+1}. {img['url']}")
