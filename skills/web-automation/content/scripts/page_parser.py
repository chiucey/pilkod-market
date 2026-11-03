#!/usr/bin/env python3
"""
PaddleStructure 页面解析脚本
用于复杂界面的布局分析、元素检测和语义理解

核心功能：
1. 版面分析（Layout Analysis）：使用 PaddleStructure 识别页面区域
2. 元素检测（Element Detection）：检测交互元素（按钮、链接、输入框等）
3. 语义理解（Semantic Understanding）：理解页面内容的语义关系
4. 结构化提取：将非结构化页面转换为结构化数据
5. GPU 自动检测和回退机制

版本：基于 PaddleOCR 3.x + PaddleStructure + PaddlePaddle 2.6.0
"""

import sys
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# 尝试导入 PaddleOCR
try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False

# 尝试导入 PaddleStructure（版面分析）
try:
    from paddlestructure import PaddleStructure
    PADDLESTRUCTURE_AVAILABLE = True
except ImportError:
    PADDLESTRUCTURE_AVAILABLE = False


def detect_gpu_available() -> bool:
    """
    检测 GPU 是否可用

    返回：
        GPU 是否可用
    """
    try:
        import paddle
        return paddle.is_compiled_with_cuda() and paddle.device.cuda.device_count() > 0
    except Exception:
        return False


class PageParser:
    """PaddleStructure 页面解析器"""

    def __init__(self, use_gpu: Optional[bool] = None):
        """
        初始化页面解析器

        参数：
            use_gpu: 是否使用 GPU（None 表示自动检测）
        """
        if not PADDLEOCR_AVAILABLE:
            raise ImportError(
                "PaddleOCR 未安装，请运行: pip install paddleocr paddlepaddle"
            )

        # GPU 自动检测
        if use_gpu is None:
            self.use_gpu = detect_gpu_available()
            print(f"🔍 自动检测 GPU: {'使用 GPU' if self.use_gpu else '使用 CPU'}")
        else:
            self.use_gpu = use_gpu

        self.ocr = None
        self.layout_engine = None

        # 初始化 OCR
        self._init_ocr()

        # 初始化版面分析引擎
        if PADDLESTRUCTURE_AVAILABLE:
            self._init_layout_engine()

    def _init_ocr(self):
        """初始化 PaddleOCR 实例"""
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang='ch',
            use_gpu=self.use_gpu,
            show_log=False
        )

    def _init_layout_engine(self):
        """初始化 PaddleStructure 版面分析引擎"""
        try:
            self.layout_engine = PaddleStructure(
                show_log=False,
                image_orientation=True,
                layout=True,  # 启用版面分析
                table=True,   # 同时支持表格
                ocr=True,
                structure_version='PP-StructureV3'  # 升级到 V3 版本
            )
            print("✅ PaddleStructure 版面分析引擎初始化成功")
        except Exception as e:
            print(f"⚠️ PaddleStructure 版面分析引擎初始化失败: {e}")
            self.layout_engine = None

    def recognize_text(self, image_path: str) -> List[Dict[str, Any]]:
        """
        识别图像中的文字（带坐标）

        参数：
            image_path: 图像路径

        返回：
            识别结果列表
        """
        try:
            img_file = Path(image_path)
            if not img_file.exists():
                return []

            result = self.ocr.ocr(str(img_file), cls=True)

            if not result or result[0] is None:
                return []

            texts = []
            for line in result[0]:
                box = line[0]
                text_info = line[1]
                text = text_info[0]
                confidence = text_info[1]

                x_coords = [point[0] for point in box]
                y_coords = [point[1] for point in box]
                bbox = {
                    "x_min": min(x_coords),
                    "y_min": min(y_coords),
                    "x_max": max(x_coords),
                    "y_max": max(y_coords)
                }

                texts.append({
                    "text": text,
                    "box": box,
                    "bbox": bbox,
                    "confidence": confidence
                })

            return texts

        except Exception as e:
            print(f"❌ 识别失败: {e}")
            return []

    def analyze_layout(
        self,
        image_path: str
    ) -> Dict[str, Any]:
        """
        分析页面布局（使用 PaddleStructure）

        参数：
            image_path: 图像路径

        返回：
            版面分析结果
        """
        if not PADDLESTRUCTURE_AVAILABLE:
            return {
                "success": False,
                "error": "PaddleStructure 未安装，请运行: pip install paddlestructure"
            }

        if not self.layout_engine:
            return {
                "success": False,
                "error": "版面分析引擎未初始化"
            }

        try:
            # 验证图像文件
            img_file = Path(image_path)
            if not img_file.exists():
                return {
                    "success": False,
                    "error": f"图像文件不存在: {image_path}"
                }

            # 使用 PaddleStructure 进行版面分析
            result = self.layout_engine(str(img_file))

            if not result or not isinstance(result, list):
                return {
                    "success": False,
                    "error": "版面分析失败：未返回有效结果",
                    "image_path": str(img_file)
                }

            # 解析版面分析结果
            regions = []
            for item in result:
                if 'res' in item:
                    res = item['res']

                    # 提取版面信息
                    layout_type = res.get('type', 'unknown')
                    bbox = res.get('bbox', [])
                    text = res.get('text', '')
                    confidence = res.get('score', 0.0)

                    if bbox:
                        regions.append({
                            "type": layout_type,
                            "text": text,
                            "bbox": bbox,
                            "confidence": confidence
                        })

            if not regions:
                return {
                    "success": False,
                    "error": "未检测到版面区域",
                    "image_path": str(img_file)
                }

            # 按类型分组
            regions_by_type = {}
            for region in regions:
                region_type = region["type"]
                if region_type not in regions_by_type:
                    regions_by_type[region_type] = []
                regions_by_type[region_type].append(region)

            return {
                "success": True,
                "regions": regions,
                "regions_by_type": regions_by_type,
                "region_count": len(regions),
                "region_types": list(regions_by_type.keys()),
                "image_path": str(img_file)
            }

        except Exception as e:
            import traceback
            return {
                "success": False,
                "error": f"版面分析失败: {str(e)}\n{traceback.format_exc()}",
                "image_path": image_path
            }

    def detect_elements(
        self,
        image_path: str,
        element_types: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        检测页面元素（基于版面分析结果）

        参数：
            image_path: 图像路径
            element_types: 元素类型列表

        返回：
            检测到的元素
        """
        # 先进行版面分析
        layout_result = self.analyze_layout(image_path)

        if not layout_result["success"]:
            # 如果版面分析失败，回退到基础 OCR
            texts = self.recognize_text(image_path)
            elements = []
            for item in texts:
                text = item["text"]
                bbox = item["bbox"]
                element_type = self._classify_element(text, bbox)
                elements.append({
                    "type": element_type,
                    "text": text,
                    "bbox": bbox,
                    "box": item["box"],
                    "confidence": item["confidence"]
                })
            return elements

        # 从版面分析结果中提取元素
        elements = []
        for region in layout_result["regions"]:
            region_type = region["type"]
            text = region["text"]
            bbox = region["bbox"]
            confidence = region["confidence"]

            # 根据版面类型映射到元素类型
            element_type = self._map_layout_to_element(region_type)

            if element_types is None or element_type in element_types:
                elements.append({
                    "type": element_type,
                    "text": text,
                    "bbox": bbox,
                    "confidence": confidence
                })

        return elements

    def _map_layout_to_element(self, layout_type: str) -> str:
        """
        将版面类型映射到元素类型

        参数：
            layout_type: 版面类型

        返回：
            元素类型
        """
        mapping = {
            "title": "heading",
            "text": "text",
            "header": "header",
            "footer": "footer",
            "table": "table",
            "figure": "image",
            "list": "list",
            "formula": "formula"
        }

        return mapping.get(layout_type, "text")

    def _classify_element(
        self,
        text: str,
        bbox: Dict[str, float]
    ) -> str:
        """
        分类元素类型（基于文本和位置）

        参数：
            text: 文字内容
            bbox: 边界框

        返回：
            元素类型
        """
        text_lower = text.lower().strip()

        if any(keyword in text_lower for keyword in [
            "button", "click", "点击", "确定", "取消", "提交"
        ]):
            return "button"

        if any(keyword in text_lower for keyword in [
            "http", "www", ".com", ".org", ".net"
        ]):
            return "link"

        if any(keyword in text_lower for keyword in [
            "input", "用户名", "密码", "email"
        ]):
            return "input"

        if bbox["y_min"] < 100 and len(text) < 20:
            return "heading"

        return "text"

    def extract_structure(
        self,
        image_path: str
    ) -> Dict[str, Any]:
        """
        提取页面结构（基于版面分析）

        参数：
            image_path: 图像路径

        返回：
            页面结构
        """
        layout = self.analyze_layout(image_path)
        elements = self.detect_elements(image_path)

        if not layout["success"]:
            return {
                "success": False,
                "error": layout.get("error", "Unknown error")
            }

        # 构建结构化数据
        structure = {
            "regions": layout["regions_by_type"],
            "elements": elements,
            "metadata": {
                "region_count": layout["region_count"],
                "region_types": layout["region_types"]
            }
        }

        return {
            "success": True,
            "structure": structure,
            "image_path": image_path
        }

    def visualize_layout(
        self,
        image_path: str,
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        可视化页面布局

        参数：
            image_path: 图像路径
            output_path: 输出路径

        返回：
            输出图像路径
        """
        try:
            image = Image.open(image_path).convert("RGB")
            draw = ImageDraw.Draw(image)

            layout = self.analyze_layout(image_path)

            if not layout["success"]:
                return None

            # 为不同类型的区域使用不同颜色
            colors = {
                "title": "red",
                "text": "green",
                "header": "blue",
                "footer": "purple",
                "table": "orange",
                "figure": "cyan"
            }

            for region in layout["regions"]:
                region_type = region["type"]
                bbox = region["bbox"]
                text = region["text"]

                # 转换坐标
                x_min, y_min, x_max, y_max = bbox

                color = colors.get(region_type, "black")
                draw.rectangle([x_min, y_min, x_max, y_max], outline=color, width=2)
                draw.text((x_min, y_min), f"{region_type}: {text[:20]}", fill=color)

            if output_path is None:
                img_file = Path(image_path)
                output_path = str(img_file.parent / f"{img_file.stem}_layout{img_file.suffix}")

            image.save(output_path)
            print(f"✅ 布局可视化已保存: {output_path}")

            return output_path

        except Exception as e:
            print(f"❌ 可视化失败: {e}")
            return None

    def export_json(
        self,
        image_path: str,
        output_path: str,
        export_type: str = "full"
    ) -> bool:
        """
        导出 JSON 格式结果

        参数：
            image_path: 图像路径
            output_path: 输出路径
            export_type: 导出类型

        返回：
            是否成功
        """
        try:
            if export_type == "layout":
                result = self.analyze_layout(image_path)
            elif export_type == "elements":
                result = {
                    "success": True,
                    "elements": self.detect_elements(image_path)
                }
            elif export_type == "structure":
                result = self.extract_structure(image_path)
            else:
                result = {
                    "layout": self.analyze_layout(image_path),
                    "elements": self.detect_elements(image_path),
                    "structure": self.extract_structure(image_path)
                }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            print(f"✅ JSON 已导出: {output_path}")
            return True

        except Exception as e:
            print(f"❌ 导出失败: {e}")
            return False


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="PaddleStructure 页面解析器",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("image_path", help="图像文件路径")
    parser.add_argument("--use-gpu", action="store_true", help="使用 GPU")
    parser.add_argument("--output", help="输出文件路径（JSON 格式）")
    parser.add_argument("--type", default="full", choices=["full", "layout", "elements", "structure"], help="导出类型")
    parser.add_argument("--visualize", action="store_true", help="可视化布局")

    args = parser.parse_args()

    try:
        parser = PageParser(use_gpu=args.use_gpu)

        if args.output:
            parser.export_json(args.image_path, args.output, args.type)
        else:
            if args.type == "layout":
                result = parser.analyze_layout(args.image_path)
            elif args.type == "elements":
                result = {
                    "success": True,
                    "elements": parser.detect_elements(args.image_path)
                }
            elif args.type == "structure":
                result = parser.extract_structure(args.image_path)
            else:
                result = {
                    "layout": parser.analyze_layout(args.image_path),
                    "elements": parser.detect_elements(args.image_path),
                    "structure": parser.extract_structure(args.image_path)
                }

            print(json.dumps(result, ensure_ascii=False, indent=2))

        if args.visualize:
            parser.visualize_layout(args.image_path)

    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
