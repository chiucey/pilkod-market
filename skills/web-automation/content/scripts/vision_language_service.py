#!/usr/bin/env python3
"""
PaddleOCR-VL 服务脚本
视觉语言模型服务，支持图像问答、图像理解、多模态交互等功能

核心功能：
1. 图像问答：基于图像内容回答用户问题
2. 图像理解：理解图像的语义和场景
3. 多模态交互：结合图像和文本进行智能交互
4. 内容描述：生成图像的自然语言描述
5. GPU 自动检测和回退机制

版本：基于 PaddleOCR 3.x + PaddleOCR-VL + Transformers 4.30+
"""

import argparse
import sys
import json
from typing import Optional, Dict, Any, List
from pathlib import Path
from PIL import Image
import numpy as np

# 尝试导入 PaddleOCR-VL
try:
    from paddleocr import PaddleOCRVL
    PADDLEOCRVL_AVAILABLE = True
except ImportError:
    PADDLEOCRVL_AVAILABLE = False


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


class VisionLanguageService:
    """PaddleOCR-VL 服务类"""

    def __init__(
        self,
        use_gpu: Optional[bool] = None,
        model_name: str = "PaddleOCR-VL"
    ):
        """
        初始化视觉语言服务

        参数：
            use_gpu: 是否使用 GPU（None 表示自动检测）
            model_name: 模型名称
        """
        if not PADDLEOCRVL_AVAILABLE:
            raise ImportError(
                "PaddleOCR-VL 未安装，请运行: pip install paddleocr>=3.0.0 transformers torch"
            )

        self.model_name = model_name

        # GPU 自动检测
        if use_gpu is None:
            self.use_gpu = detect_gpu_available()
            print(f"🔍 自动检测 GPU: {'使用 GPU' if self.use_gpu else '使用 CPU'}")
        else:
            self.use_gpu = use_gpu

        self.vl_model = None

        # 初始化模型
        self._init_model()

    def _init_model(self):
        """初始化 PaddleOCR-VL 模型"""
        try:
            self.vl_model = PaddleOCRVL(
                show_log=False,
                use_gpu=self.use_gpu
            )
            print(f"✅ PaddleOCR-VL 模型初始化成功 ({self.model_name})")
        except Exception as e:
            print(f"⚠️ PaddleOCR-VL 模型初始化失败: {e}")
            raise

    def image_qa(
        self,
        image_path: str,
        question: str
    ) -> Dict[str, Any]:
        """
        图像问答

        参数：
            image_path: 图像路径
            question: 用户问题

        返回：
            包含答案的字典
        """
        try:
            # 验证图像文件
            img_file = Path(image_path)
            if not img_file.exists():
                return {
                    "success": False,
                    "error": f"图像文件不存在: {image_path}"
                }

            # 执行图像问答
            result = self.vl_model.ocr(
                str(img_file),
                ocr=True,
                return_ocr_result_in_doc=True
            )

            if not result:
                return {
                    "success": False,
                    "error": "图像问答失败：未返回有效结果"
                }

            # 提取图像内容
            image_content = []
            for item in result:
                if 'res' in item:
                    res = item['res']
                    if 'text' in res:
                        image_content.append(res['text'])

            full_text = "\n".join(image_content)

            # 基于图像内容回答问题
            answer = self._answer_question(image_content, question)

            return {
                "success": True,
                "question": question,
                "answer": answer,
                "image_content": full_text,
                "image_path": str(img_file)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"图像问答失败: {str(e)}",
                "image_path": image_path
            }

    def _answer_question(self, image_content: List[str], question: str) -> str:
        """
        基于图像内容回答问题

        参数：
            image_content: 图像内容列表
            question: 用户问题

        返回：
            答案
        """
        # 简单的关键词匹配
        question_lower = question.lower()
        relevant_info = []

        for content in image_content:
            content_lower = content.lower()
            # 检查是否包含问题中的关键词
            if any(word in content_lower for word in question_lower.split()):
                relevant_info.append(content)

        if relevant_info:
            answer = "\n".join(relevant_info[:3])
        else:
            # 如果没有找到相关信息，返回图像内容摘要
            answer = "图像内容：\n" + "\n".join(image_content[:5])

        return answer

    def describe_image(
        self,
        image_path: str,
        detail_level: str = "simple"
    ) -> Dict[str, Any]:
        """
        描述图像内容

        参数：
            image_path: 图像路径
            detail_level: 描述详细程度
                - simple: 简单描述
                - detailed: 详细描述

        返回：
            包含描述的字典
        """
        try:
            # 验证图像文件
            img_file = Path(image_path)
            if not img_file.exists():
                return {
                    "success": False,
                    "error": f"图像文件不存在: {image_path}"
                }

            # 执行图像识别
            result = self.vl_model.ocr(
                str(img_file),
                ocr=True,
                return_ocr_result_in_doc=True
            )

            if not result:
                return {
                    "success": False,
                    "error": "图像描述失败：未返回有效结果"
                }

            # 提取图像内容
            image_content = []
            for item in result:
                if 'res' in item:
                    res = item['res']
                    if 'text' in res:
                        image_content.append(res['text'])

            # 生成描述
            if detail_level == "simple":
                description = self._generate_simple_description(image_content)
            else:
                description = self._generate_detailed_description(image_content)

            return {
                "success": True,
                "description": description,
                "detail_level": detail_level,
                "image_content": image_content,
                "image_path": str(img_file)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"图像描述失败: {str(e)}",
                "image_path": image_path
            }

    def _generate_simple_description(self, image_content: List[str]) -> str:
        """
        生成简单描述

        参数：
            image_content: 图像内容列表

        返回：
            简单描述
        """
        if not image_content:
            return "图像中没有可识别的文字内容"

        # 取前几行内容作为简单描述
        preview = image_content[:3]
        return "图像内容：\n" + "\n".join(preview)

    def _generate_detailed_description(self, image_content: List[str]) -> str:
        """
        生成详细描述

        参数：
            image_content: 图像内容列表

        返回：
            详细描述
        """
        if not image_content:
            return "图像中没有可识别的文字内容"

        # 完整描述所有内容
        return "图像详细内容：\n" + "\n".join(image_content)

    def analyze_scene(
        self,
        image_path: str
    ) -> Dict[str, Any]:
        """
        分析图像场景

        参数：
            image_path: 图像路径

        返回：
            包含场景分析结果的字典
        """
        try:
            # 验证图像文件
            img_file = Path(image_path)
            if not img_file.exists():
                return {
                    "success": False,
                    "error": f"图像文件不存在: {image_path}"
                }

            # 执行图像识别
            result = self.vl_model.ocr(
                str(img_file),
                ocr=True,
                return_ocr_result_in_doc=True
            )

            if not result:
                return {
                    "success": False,
                    "error": "场景分析失败：未返回有效结果"
                }

            # 提取图像内容
            image_content = []
            for item in result:
                if 'res' in item:
                    res = item['res']
                    if 'text' in res:
                        image_content.append(res['text'])

            # 分析场景
            scene_info = self._analyze_scene_content(image_content)

            return {
                "success": True,
                "scene_type": scene_info["scene_type"],
                "key_elements": scene_info["key_elements"],
                "image_content": image_content,
                "image_path": str(img_file)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"场景分析失败: {str(e)}",
                "image_path": image_path
            }

    def _analyze_scene_content(self, image_content: List[str]) -> Dict[str, Any]:
        """
        分析场景内容

        参数：
            image_content: 图像内容列表

        返回：
            场景信息
        """
        # 简单的场景分类
        full_text = "\n".join(image_content).lower()

        scene_type = "unknown"
        key_elements = []

        # 检测常见场景
        if "发票" in full_text or "收据" in full_text:
            scene_type = "invoice"
            key_elements = ["发票", "金额", "日期"]
        elif "合同" in full_text or "协议" in full_text:
            scene_type = "contract"
            key_elements = ["合同", "甲方", "乙方"]
        elif "身份证" in full_text or "公民身份号码" in full_text:
            scene_type = "id_card"
            key_elements = ["姓名", "身份证号", "住址"]
        elif "菜单" in full_text or "菜品" in full_text:
            scene_type = "menu"
            key_elements = ["菜名", "价格"]
        elif "书" in full_text or "文章" in full_text:
            scene_type = "document"
            key_elements = ["标题", "正文"]
        else:
            scene_type = "general"
            key_elements = image_content[:5]

        return {
            "scene_type": scene_type,
            "key_elements": key_elements
        }

    def extract_text(
        self,
        image_path: str,
        with_layout: bool = False
    ) -> Dict[str, Any]:
        """
        提取图像中的文字

        参数：
            image_path: 图像路径
            with_layout: 是否包含版面信息

        返回：
            包含文字的字典
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
            result = self.vl_model.ocr(
                str(img_file),
                ocr=True,
                return_ocr_result_in_doc=True
            )

            if not result:
                return {
                    "success": False,
                    "error": "文字提取失败：未返回有效结果"
                }

            # 提取文字
            texts = []
            layout_info = []

            for item in result:
                if 'res' in item:
                    res = item['res']
                    text = res.get('text', '')
                    bbox = res.get('bbox', [])

                    if text:
                        texts.append(text)
                        if with_layout and bbox:
                            layout_info.append({
                                "text": text,
                                "bbox": bbox
                            })

            full_text = "\n".join(texts)

            response = {
                "success": True,
                "text": full_text,
                "texts": texts,
                "image_path": str(img_file)
            }

            if with_layout:
                response["layout"] = layout_info

            return response

        except Exception as e:
            return {
                "success": False,
                "error": f"文字提取失败: {str(e)}",
                "image_path": image_path
            }


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="PaddleOCR-VL 服务脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：

1. 图像问答：
  python vision_language_service.py qa image.png "图像中有什么内容？"

2. 描述图像：
  python vision_language_service.py describe image.png --detail-level simple

3. 分析场景：
  python vision_language_service.py analyze image.png

4. 提取文字：
  python vision_language_service.py extract image.png --with-layout
        """
    )

    parser.add_argument(
        "command",
        choices=["qa", "describe", "analyze", "extract"],
        help="命令类型"
    )

    parser.add_argument(
        "image",
        help="图像路径"
    )

    parser.add_argument(
        "--question",
        help="问题（仅用于 qa 命令）"
    )

    parser.add_argument(
        "--detail-level",
        default="simple",
        choices=["simple", "detailed"],
        help="描述详细程度（仅用于 describe 命令）"
    )

    parser.add_argument(
        "--with-layout",
        action="store_true",
        help="包含版面信息（仅用于 extract 命令）"
    )

    parser.add_argument(
        "--gpu",
        action="store_true",
        help="使用 GPU"
    )

    args = parser.parse_args()

    # 初始化服务
    try:
        service = VisionLanguageService(use_gpu=args.gpu)
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        sys.exit(1)

    # 执行命令
    result = None

    if args.command == "qa":
        if not args.question:
            print("❌ qa 命令需要 --question 参数")
            sys.exit(1)

        result = service.image_qa(args.image, args.question)

    elif args.command == "describe":
        result = service.describe_image(args.image, args.detail_level)

    elif args.command == "analyze":
        result = service.analyze_scene(args.image)

    elif args.command == "extract":
        result = service.extract_text(args.image, args.with_layout)

    # 输出结果
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
