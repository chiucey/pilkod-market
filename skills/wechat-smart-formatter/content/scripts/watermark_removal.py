#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号配图 - 水印去除模块
智能识别并去除图片水印
Author: MiniMax Agent
Version: 1.0.0
"""

import os
import sys
import logging
from typing import Optional, Tuple, List, Dict
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WatermarkRemover:
    """智能水印去除器"""

    def __init__(self, method: str = "auto"):
        """
        初始化水印去除器

        Args:
            method: 去除方法 ("auto", "inpaint", "crop", "blend")
        """
        self.method = method
        self.opencv_available = False
        self.pil_available = False

        # 检查依赖
        try:
            import cv2
            import numpy as np
            self.cv2 = cv2
            self.np = np
            self.opencv_available = True
        except ImportError:
            logger.warning("OpenCV未安装，高级水印去除功能不可用")

    def remove_watermark(
        self,
        image_path: str,
        output_path: Optional[str] = None,
        strength: str = "medium"
    ) -> Tuple[bool, Optional[str]]:
        """
        去除图片水印

        Args:
            image_path: 输入图片路径
            output_path: 输出图片路径（可选）
            strength: 去除强度 ("low", "medium", "high")

        Returns:
            (是否成功, 输出路径或错误信息)
        """
        if not self.opencv_available:
            return False, "OpenCV未安装，无法去除水印"

        if not os.path.exists(image_path):
            return False, f"图片不存在: {image_path}"

        # 确定输出路径
        if output_path is None:
            path = Path(image_path)
            output_path = str(path.parent / f"{path.stem}_nowm{path.suffix}")

        try:
            # 读取图片
            img = self.cv2.imread(image_path)
            if img is None:
                return False, "无法读取图片"

            # 检测水印位置
            watermark_info = self._detect_watermark(img)

            if not watermark_info["detected"]:
                logger.info("未检测到明显水印，直接复制原图")
                self.cv2.imwrite(output_path, img)
                return True, output_path

            # 根据水印位置选择去除方法
            location = watermark_info["location"]

            if location == "bottom-right":
                result = self._remove_corner_watermark(img, output_path, strength)
            elif location == "bottom-center":
                result = self._remove_bottom_watermark(img, output_path, strength)
            elif location == "corners":
                result = self._remove_corner_watermarks(img, output_path, strength)
            else:
                result = self._inpaint_watermark(img, watermark_info, output_path)

            return True, result

        except Exception as e:
            logger.error(f"水印去除失败: {e}")
            return False, str(e)

    def _detect_watermark(self, img) -> Dict:
        """
        检测水印位置和类型

        Args:
            img: OpenCV图片对象

        Returns:
            检测结果字典
        """
        h, w = img.shape[:2]

        # 转换为灰度图
        gray = self.cv2.cvtColor(img, self.cv2.COLOR_BGR2GRAY)

        # 边缘检测
        edges = self.cv2.Canny(gray, 50, 150)

        # 膨胀以连接相关边缘
        kernel = self.cv2.getStructuringElement(self.cv2.MORPH_RECT, (5, 5))
        dilated = self.cv2.dilate(edges, kernel, iterations=2)

        # 查找轮廓
        contours, _ = self.cv2.findContours(
            dilated,
            self.cv2.RETR_EXTERNAL,
            self.cv2.CHAIN_APPROX_SIMPLE
        )

        # 分析右下角区域（水印常见位置）
        bottom_right_region = img[int(h*0.85):, int(w*0.7):]
        bottom_center_region = img[int(h*0.9):, int(w*0.2):int(w*0.8)]

        # 检测半透明白色/灰色区域
        white_mask = self._detect_transparent_text(img)

        # 综合判断
        location = "none"
        confidence = 0.0

        # 右下角水印特征
        if self._has_watermark_pattern(bottom_right_region):
            location = "bottom-right"
            confidence = 0.85
        # 底部居中水印
        elif self._has_watermark_pattern(bottom_center_region):
            location = "bottom-center"
            confidence = 0.80
        # 多角水印
        elif white_mask["corners_ratio"] > 0.1:
            location = "corners"
            confidence = 0.75
        # 全局检测
        elif white_mask["overall_ratio"] > 0.03:
            location = "scattered"
            confidence = 0.60

        return {
            "detected": confidence > 0.5,
            "location": location,
            "confidence": confidence,
            "mask": white_mask
        }

    def _detect_transparent_text(self, img) -> Dict:
        """检测半透明文字区域"""
        h, w = img.shape[:2]

        # 检测浅色文字
        lower = self.np.array([180, 180, 180])
        upper = self.np.array([255, 255, 255])
        mask = self.cv2.inRange(img, lower, upper)

        # 计算各区域占比
        total_pixels = h * w
        white_pixels = self.np.sum(mask > 0)

        # 检查角落
        corner_regions = [
            mask[0:int(h*0.2), 0:int(w*0.2)],  # 左上
            mask[0:int(h*0.2), int(w*0.8):],  # 右上
            mask[int(h*0.8):, 0:int(w*0.2)],  # 左下
            mask[int(h*0.8):, int(w*0.8):],  # 右下
        ]

        corner_ratios = [self.np.sum(r > 0) / (r.shape[0] * r.shape[1] + 1)
                        for r in corner_regions]

        return {
            "overall_ratio": white_pixels / total_pixels,
            "corners_ratio": max(corner_ratios) if corner_ratios else 0,
            "mask": mask
        }

    def _has_watermark_pattern(self, region) -> bool:
        """检测是否是水印模式"""
        if region.size == 0:
            return False

        gray = self.cv2.cvtColor(region, self.cv2.COLOR_BGR2GRAY)

        # 检查是否有文字特征（高对比度边缘）
        edges = self.cv2.Canny(gray, 30, 100)
        edge_density = self.np.sum(edges > 0) / edges.size

        return edge_density > 0.05

    def _remove_corner_watermark(
        self,
        img,
        output_path: str,
        strength: str
    ) -> str:
        """去除右下角水印"""
        h, w = img.shape[:2]

        # 定义水印区域（右下角）
        padding = 20
        watermark_h = int(h * 0.15)
        watermark_w = int(w * 0.35)

        y_start = h - watermark_h - padding
        y_end = h - padding
        x_start = w - watermark_w - padding
        x_end = w - padding

        # 复制邻近区域进行填充
        source_region = img[y_start:y_end, x_start-50:x_start+10].copy()
        source_resized = self.cv2.resize(
            source_region,
            (watermark_w, watermark_h),
            interpolation=self.cv2.INTER_CUBIC
        )

        # 模糊处理以消除水印痕迹
        if strength == "high":
            source_resized = self.cv2.GaussianBlur(
                source_resized, (7, 7), 2
            )
        elif strength == "medium":
            source_resized = self.cv2.GaussianBlur(
                source_resized, (5, 5), 1
            )

        # 应用修复
        img[y_start:y_end, x_start:x_end] = source_resized

        # 保存结果
        self.cv2.imwrite(output_path, img)
        logger.info(f"水印已去除: {output_path}")

        return output_path

    def _remove_bottom_watermark(
        self,
        img,
        output_path: str,
        strength: str
    ) -> str:
        """去除底部居中水印"""
        h, w = img.shape[:2]

        # 定义水印区域
        padding = 10
        watermark_h = int(h * 0.08)

        y_start = h - watermark_h - padding
        y_end = h - padding

        # 使用渐变填充
        for i in range(3):  # BGR三个通道
            channel = img[y_start:y_end, :, i]

            # 创建渐变蒙版
            gradient = self.np.linspace(0, 255, watermark_h).astype(
                channel.dtype
            )
            gradient_mask = self.np.tile(
                gradient.reshape(-1, 1), (1, w)
            )

            # 混合
            blended = self.cv2.addWeighted(
                channel, 0.3,
                gradient_mask.astype(channel.dtype), 0.7, 0
            )

            img[y_start:y_end, :, i] = blended

        # 高斯模糊进一步处理
        img[y_start:y_end] = self.cv2.GaussianBlur(
            img[y_start:y_end], (3, 3), 0.5
        )

        self.cv2.imwrite(output_path, img)
        logger.info(f"底部水印已去除: {output_path}")

        return output_path

    def _remove_corner_watermarks(
        self,
        img,
        output_path: str,
        strength: str
    ) -> str:
        """去除四角水印"""
        h, w = img.shape[:2]

        corners = [
            (0, 0, int(w*0.15), int(h*0.1)),      # 左上
            (w-int(w*0.15), 0, w, int(h*0.1)),    # 右上
            (0, h-int(h*0.1), int(w*0.15), h),    # 左下
            (w-int(w*0.15), h-int(h*0.1), w, h),  # 右下
        ]

        for x1, y1, x2, y2 in corners:
            region = img[y1:y2, x1:x2]
            if region.size == 0:
                continue

            # 使用模糊和颜色调整
            blurred = self.cv2.GaussianBlur(region, (5, 5), 1)
            img[y1:y2, x1:x2] = blurred

        self.cv2.imwrite(output_path, img)
        return output_path

    def _inpaint_watermark(
        self,
        img,
        watermark_info: Dict,
        output_path: str
    ) -> str:
        """使用inpainting算法去除水印"""
        # 创建水印蒙版
        mask = watermark_info.get("mask", {}).get("mask")

        if mask is not None:
            # 使用Telea inpainting算法
            result = self.cv2.inpaint(
                img, mask, 3, self.cv2.INPAINT_TELEA
            )
            self.cv2.imwrite(output_path, result)
            return output_path

        # 如果无法创建蒙版，使用模糊
        h, w = img.shape[:2]
        center_region = img[int(h*0.8):, int(w*0.2):int(w*0.8)]
        blurred = self.cv2.GaussianBlur(center_region, (7, 7), 3)
        img[int(h*0.8):, int(w*0.2):int(w*0.8)] = blurred

        self.cv2.imwrite(output_path, img)
        return output_path


class SmartWatermarkCleaner:
    """智能水印清洁器 - 一站式处理"""

    def __init__(self):
        self.remover = WatermarkRemover()

    def process_image(
        self,
        image_path: str,
        auto_detect: bool = True,
        preserve_quality: bool = True
    ) -> Dict:
        """
        智能处理图片

        Args:
            image_path: 图片路径
            auto_detect: 是否自动检测水印
            preserve_quality: 是否保持原图质量

        Returns:
            处理结果 {
                "success": bool,
                "output_path": str,
                "watermark_removed": bool,
                "quality_preserved": bool,
                "message": str
            }
        """
        output_path = image_path.replace(
            ".", "_cleaned.", 1
        )

        if not auto_detect:
            # 直接去除
            success, result = self.remover.remove_watermark(
                image_path, output_path
            )
            return {
                "success": success,
                "output_path": result if success else None,
                "watermark_removed": success,
                "quality_preserved": False,
                "message": "水印已处理" if success else f"处理失败: {result}"
            }

        # 先检测
        img = self.remover.cv2.imread(image_path)
        if img is None:
            return {
                "success": False,
                "output_path": None,
                "watermark_removed": False,
                "quality_preserved": False,
                "message": "无法读取图片"
            }

        detection = self.remover._detect_watermark(img)

        if not detection["detected"]:
            # 无水印，直接复制
            self.remover.cv2.imwrite(output_path, img)
            return {
                "success": True,
                "output_path": output_path,
                "watermark_removed": False,
                "quality_preserved": True,
                "message": "未检测到水印，原图已保存"
            }

        # 有水印，去除
        success, result = self.remover.remove_watermark(
            image_path, output_path
        )

        return {
            "success": success,
            "output_path": result if success else None,
            "watermark_removed": success,
            "quality_preserved": False,
            "message": f"水印已去除" if success else f"处理失败: {result}"
        }


# 命令行接口
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="智能水印去除工具")
    parser.add_argument("image_path", help="图片路径")
    parser.add_argument("-o", "--output", help="输出路径")
    parser.add_argument("-m", "--method", default="auto",
                       choices=["auto", "inpaint", "crop", "blend"],
                       help="去除方法")
    parser.add_argument("-s", "--strength", default="medium",
                       choices=["low", "medium", "high"],
                       help="处理强度")

    args = parser.parse_args()

    cleaner = SmartWatermarkCleaner()
    result = cleaner.process_image(
        args.image_path,
        output_path=args.output
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))
