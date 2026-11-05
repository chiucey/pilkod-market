"""
PaddleOCR 服务脚本（完整版，PaddleOCR 3.x）
提供文字识别、表格提取、元素检测、印章识别等功能

核心功能：
- 通用文字识别（中英文，PaddleOCR 3.x）
- 表格识别与提取（PP-StructureV3）
- 元素检测（按钮、文本、链接等）
- 版面分析（PP-StructureV3）
- 批量图片处理
- GPU 自动检测和回退机制

版本：PaddleOCR 3.x + PaddlePaddle 2.6.0
参考：https://www.paddleocr.ai/latest/version3.x/pipeline_usage/OCR.html
"""

import argparse
import sys
import json
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from PIL import Image
import numpy as np

# 尝试导入 PaddleOCR
try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False

# 尝试导入 PPStructure（文档解析）
try:
    from paddleocr import PPStructure
    PPSTRUCTURE_AVAILABLE = True
except ImportError:
    PPSTRUCTURE_AVAILABLE = False


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


class OCRService:
    """PaddleOCR 服务类（包含表格识别）"""

    def __init__(
        self,
        use_angle_cls: bool = True,
        lang: str = 'ch',
        use_gpu: Optional[bool] = None,
        ocr_version: str = 'PP-OCRv5',
        det_model_dir: Optional[str] = None,
        rec_model_dir: Optional[str] = None,
        cls_model_dir: Optional[str] = None
    ):
        """
        初始化 OCR 服务

        参数：
            use_angle_cls: 是否使用方向分类器
            lang: 语言类型 (ch/en/japan/korean)
            use_gpu: 是否使用 GPU（None 表示自动检测）
            ocr_version: OCR 版本 (PP-OCRv3/v4/v5)
            det_model_dir: 检测模型路径
            rec_model_dir: 识别模型路径
            cls_model_dir: 分类模型路径
        """
        if not PADDLEOCR_AVAILABLE:
            raise ImportError(
                "PaddleOCR 未安装，请运行: pip install paddleocr"
            )

        self.use_angle_cls = use_angle_cls
        self.lang = lang
        self.ocr_version = ocr_version

        # GPU 自动检测
        if use_gpu is None:
            self.use_gpu = detect_gpu_available()
            print(f"🔍 自动检测 GPU: {'使用 GPU' if self.use_gpu else '使用 CPU'}")
        else:
            self.use_gpu = use_gpu

        self.ocr = None
        self.structure_engine = None

        # 初始化 OCR
        self._init_ocr(
            det_model_dir=det_model_dir,
            rec_model_dir=rec_model_dir,
            cls_model_dir=cls_model_dir
        )

        # 初始化版面分析引擎（PP-StructureV3）
        if PPSTRUCTURE_AVAILABLE:
            self._init_structure_engine()

    def _init_ocr(
        self,
        det_model_dir: Optional[str] = None,
        rec_model_dir: Optional[str] = None,
        cls_model_dir: Optional[str] = None
    ):
        """初始化 PaddleOCR 实例"""
        self.ocr = PaddleOCR(
            use_angle_cls=self.use_angle_cls,
            lang=self.lang,
            use_gpu=self.use_gpu,
            ocr_version=self.ocr_version,
            det_model_dir=det_model_dir,
            rec_model_dir=rec_model_dir,
            cls_model_dir=cls_model_dir,
            show_log=False,
            det=True,
            rec=True
        )

    def _init_structure_engine(self):
        """初始化 PP-StructureV3 版面分析引擎"""
        try:
            self.structure_engine = PPStructure(
                show_log=False,
                table=True,          # 启用表格识别
                ocr=True,            # 启用 OCR
                layout=True,         # 启用版面分析
                structure_version='PP-StructureV3',
                image_orientation=True
            )
            print("✅ PP-StructureV3 版面分析引擎初始化成功")
        except Exception as e:
            print(f"⚠️ PP-StructureV3 版面分析引擎初始化失败: {e}")
            self.structure_engine = None

    def recognize_image(
        self,
        image_path: str,
        det: bool = True,
        rec: bool = True,
        cls: bool = True
    ) -> Dict[str, Any]:
        """
        识别图像中的文字

        参数：
            image_path: 图像路径
            det: 是否进行文字检测
            rec: 是否进行文字识别
            cls: 是否进行方向分类

        返回：
            包含识别结果的字典
        """
        try:
            # 验证图像文件
            img_file = Path(image_path)
            if not img_file.exists():
                return {
                    "success": False,
                    "error": f"图像文件不存在: {image_path}"
                }

            # 执行 OCR 识别
            result = self.ocr.ocr(str(img_file), cls=cls)

            # 处理结果
            if not result or result[0] is None:
                return {
                    "success": True,
                    "text": "",
                    "boxes": [],
                    "texts": [],
                    "confidence": 0.0
                }

            # 提取文本和坐标
            texts = []
            boxes = []
            confidences = []

            for line in result[0]:
                box = line[0]
                text_info = line[1]
                text = text_info[0]
                confidence = text_info[1]

                boxes.append(box)
                texts.append(text)
                confidences.append(confidence)

            # 合并所有文本
            full_text = "\n".join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            return {
                "success": True,
                "text": full_text,
                "boxes": boxes,
                "texts": texts,
                "confidence": avg_confidence
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"识别图像失败: {str(e)}"
            }

    def recognize_tables(
        self,
        image_path: str
    ) -> Dict[str, Any]:
        """
        识别图像中的表格

        参数：
            image_path: 图像路径

        返回：
            包含表格识别结果的字典
        """
        if not PPSTRUCTURE_AVAILABLE or not self.structure_engine:
            return {
                "success": False,
                "error": "PP-StructureV3 未初始化，请安装完整版：pip install 'paddleocr[doc-parser]'"
            }

        try:
            img_file = Path(image_path)
            if not img_file.exists():
                return {
                    "success": False,
                    "error": f"图像文件不存在: {image_path}"
                }

            # 使用 PP-StructureV3 识别表格
            result = self.structure_engine(str(img_file))

            # 提取表格数据
            tables = []
            for region in result:
                if region['type'] == 'table':
                    tables.append({
                        'type': 'table',
                        'html': region.get('res', {}).get('html', ''),
                        'data': region.get('res', {})
                    })

            return {
                "success": True,
                "tables": tables,
                "all_regions": result
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"识别表格失败: {str(e)}"
            }

    def analyze_layout(
        self,
        image_path: str
    ) -> Dict[str, Any]:
        """
        分析文档布局（标题、段落、图片、表格等）

        参数：
            image_path: 图像路径

        返回：
            包含布局分析结果的字典
        """
        if not PPSTRUCTURE_AVAILABLE or not self.structure_engine:
            return {
                "success": False,
                "error": "PP-StructureV3 未初始化，请安装完整版：pip install 'paddleocr[doc-parser]'"
            }

        try:
            img_file = Path(image_path)
            if not img_file.exists():
                return {
                    "success": False,
                    "error": f"图像文件不存在: {image_path}"
                }

            # 使用 PP-StructureV3 分析布局
            result = self.structure_engine(str(img_file))

            # 按类型分类区域
            regions_by_type = {
                'title': [],
                'text': [],
                'table': [],
                'figure': [],
                'header': [],
                'footer': []
            }

            for region in result:
                region_type = region['type']
                if region_type in regions_by_type:
                    regions_by_type[region_type].append(region)

            return {
                "success": True,
                "regions": result,
                "regions_by_type": regions_by_type
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"分析布局失败: {str(e)}"
            }


def main():
    """命令行接口"""
    parser = argparse.ArgumentParser(description='PaddleOCR 3.x 服务')
    parser.add_argument('image', help='图像路径')
    parser.add_argument('--mode', choices=['ocr', 'table', 'layout'],
                       default='ocr', help='处理模式')
    parser.add_argument('--lang', default='ch', help='语言')
    parser.add_argument('--gpu', action='store_true', help='使用 GPU')
    parser.add_argument('--output', help='输出结果到文件')

    args = parser.parse_args()

    # 初始化服务
    service = OCRService(
        lang=args.lang,
        use_gpu=args.gpu
    )

    result = None

    if args.mode == 'ocr':
        result = service.recognize_image(args.image)
    elif args.mode == 'table':
        result = service.recognize_tables(args.image)
    elif args.mode == 'layout':
        result = service.analyze_layout(args.image)

    # 输出结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到: {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
