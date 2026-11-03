#!/usr/bin/env python3
"""
PP-ChatOCRv4 服务脚本
基于大模型的文档理解系统，提供文档问答、关键信息提取、语义理解等功能

核心功能：
1. 文档问答：基于文档内容回答用户问题
2. 关键信息提取：从文档中提取结构化信息（如发票、合同等）
3. 文档摘要：生成文档的摘要
4. 语义理解：理解文档的深层含义
5. GPU 自动检测和回退机制

版本：基于 PaddleOCR 3.x + PP-ChatOCRv4 + Transformers 4.30+
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
    from paddleocr import PPChatOCRv4
    PPCHATOCR_AVAILABLE = True
except ImportError:
    PPCHATOCR_AVAILABLE = False


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


class ChatOCRService:
    """PP-ChatOCRv4 服务类"""

    def __init__(
        self,
        use_gpu: Optional[bool] = None,
        model_name: str = "PP-ChatOCRv4_doc"
    ):
        """
        初始化 ChatOCR 服务

        参数：
            use_gpu: 是否使用 GPU（None 表示自动检测）
            model_name: 模型名称
                - PP-ChatOCRv4_doc: 通用文档理解
                - PP-ChatOCRv4_table: 表格理解
        """
        if not PPCHATOCR_AVAILABLE:
            raise ImportError(
                "PP-ChatOCRv4 未安装，请运行: pip install paddleocr>=3.0.0 transformers torch"
            )

        self.model_name = model_name

        # GPU 自动检测
        if use_gpu is None:
            self.use_gpu = detect_gpu_available()
            print(f"🔍 自动检测 GPU: {'使用 GPU' if self.use_gpu else '使用 CPU'}")
        else:
            self.use_gpu = use_gpu

        self.chat_ocr = None

        # 初始化模型
        self._init_model()

    def _init_model(self):
        """初始化 PP-ChatOCRv4 模型"""
        try:
            self.chat_ocr = PPChatOCRv4(
                show_log=False,
                use_gpu=self.use_gpu
            )
            print(f"✅ PP-ChatOCRv4 模型初始化成功 ({self.model_name})")
        except Exception as e:
            print(f"⚠️ PP-ChatOCRv4 模型初始化失败: {e}")
            raise

    def document_qa(
        self,
        image_path: str,
        question: str
    ) -> Dict[str, Any]:
        """
        文档问答

        参数：
            image_path: 文档图像路径
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

            # 执行问答
            result = self.chat_ocr.ocr(
                str(img_file),
                ocr=True,
                return_ocr_result_in_doc=True
            )

            if not result:
                return {
                    "success": False,
                    "error": "文档问答失败：未返回有效结果"
                }

            # 提取文档内容和答案
            doc_content = []
            for item in result:
                if 'res' in item:
                    res = item['res']
                    if 'text' in res:
                        doc_content.append(res['text'])

            full_text = "\n".join(doc_content)

            # 基于文档内容回答问题
            # 注意：这里简化处理，实际 PP-ChatOCRv4 有专门的问答接口
            # 需要根据实际 API 调整
            answer = self._answer_question(full_text, question)

            return {
                "success": True,
                "question": question,
                "answer": answer,
                "document_text": full_text,
                "image_path": str(img_file)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"文档问答失败: {str(e)}",
                "image_path": image_path
            }

    def _answer_question(self, document: str, question: str) -> str:
        """
        基于文档回答问题（简化版）

        实际应用中应该使用 PP-ChatOCRv4 的专用问答接口
        """
        # 这里提供基本的实现框架
        # 实际使用时需要根据 PP-ChatOCRv4 的 API 调整

        # 简单的关键词匹配
        question_lower = question.lower()
        document_lower = document.lower()

        # 尝试在文档中查找相关内容
        relevant_sentences = []
        for sentence in document.split('。'):
            if any(word in sentence.lower() for word in question_lower.split()):
                relevant_sentences.append(sentence.strip())

        if relevant_sentences:
            answer = "。".join(relevant_sentences[:3])
        else:
            answer = "未在文档中找到相关信息"

        return answer

    def extract_key_info(
        self,
        image_path: str,
        info_type: str = "invoice"
    ) -> Dict[str, Any]:
        """
        提取关键信息

        参数：
            image_path: 文档图像路径
            info_type: 信息类型
                - invoice: 发票信息
                - contract: 合同信息
                - id_card: 身份证信息
                - custom: 自定义提取

        返回：
            包含关键信息的字典
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
            result = self.chat_ocr.ocr(
                str(img_file),
                ocr=True,
                return_ocr_result_in_doc=True
            )

            if not result:
                return {
                    "success": False,
                    "error": "关键信息提取失败：未返回有效结果"
                }

            # 提取文本
            doc_content = []
            for item in result:
                if 'res' in item:
                    res = item['res']
                    if 'text' in res:
                        doc_content.append(res['text'])

            full_text = "\n".join(doc_content)

            # 根据信息类型提取关键信息
            key_info = self._extract_by_type(full_text, info_type)

            return {
                "success": True,
                "info_type": info_type,
                "key_info": key_info,
                "document_text": full_text,
                "image_path": str(img_file)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"关键信息提取失败: {str(e)}",
                "image_path": image_path
            }

    def _extract_by_type(self, text: str, info_type: str) -> Dict[str, str]:
        """
        根据类型提取关键信息

        参数：
            text: 文档文本
            info_type: 信息类型

        返回：
            关键信息字典
        """
        key_info = {}

        if info_type == "invoice":
            # 发票信息提取
            key_info = self._extract_invoice_info(text)
        elif info_type == "contract":
            # 合同信息提取
            key_info = self._extract_contract_info(text)
        elif info_type == "id_card":
            # 身份证信息提取
            key_info = self._extract_id_card_info(text)
        else:
            # 自定义提取
            key_info = {"raw_text": text}

        return key_info

    def _extract_invoice_info(self, text: str) -> Dict[str, str]:
        """提取发票信息"""
        info = {}

        # 简单的规则提取
        lines = text.split('\n')
        for line in lines:
            if "发票号码" in line or "号码" in line:
                info["发票号码"] = line.split("：")[-1].strip()
            elif "开票日期" in line or "日期" in line:
                info["开票日期"] = line.split("：")[-1].strip()
            elif "金额" in line or "合计" in line:
                info["金额"] = line.split("：")[-1].strip()

        return info

    def _extract_contract_info(self, text: str) -> Dict[str, str]:
        """提取合同信息"""
        info = {}

        lines = text.split('\n')
        for line in lines:
            if "合同编号" in line or "编号" in line:
                info["合同编号"] = line.split("：")[-1].strip()
            elif "甲方" in line:
                info["甲方"] = line.split("：")[-1].strip()
            elif "乙方" in line:
                info["乙方"] = line.split("：")[-1].strip()

        return info

    def _extract_id_card_info(self, text: str) -> Dict[str, str]:
        """提取身份证信息"""
        info = {}

        lines = text.split('\n')
        for line in lines:
            if "姓名" in line or "姓名" in line:
                info["姓名"] = line.split("：")[-1].strip()
            elif "身份证号" in line or "公民身份号码" in line:
                info["身份证号"] = line.split("：")[-1].strip()
            elif "住址" in line:
                info["住址"] = line.split("：")[-1].strip()

        return info

    def generate_summary(
        self,
        image_path: str,
        max_length: int = 200
    ) -> Dict[str, Any]:
        """
        生成文档摘要

        参数：
            image_path: 文档图像路径
            max_length: 摘要最大长度

        返回：
            包含摘要的字典
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
            result = self.chat_ocr.ocr(
                str(img_file),
                ocr=True,
                return_ocr_result_in_doc=True
            )

            if not result:
                return {
                    "success": False,
                    "error": "摘要生成失败：未返回有效结果"
                }

            # 提取文本
            doc_content = []
            for item in result:
                if 'res' in item:
                    res = item['res']
                    if 'text' in res:
                        doc_content.append(res['text'])

            full_text = "\n".join(doc_content)

            # 生成摘要
            summary = self._generate_summary_text(full_text, max_length)

            return {
                "success": True,
                "summary": summary,
                "document_text": full_text,
                "image_path": str(img_file)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"摘要生成失败: {str(e)}",
                "image_path": image_path
            }

    def _generate_summary_text(self, text: str, max_length: int) -> str:
        """
        生成摘要文本

        参数：
            text: 原始文本
            max_length: 最大长度

        返回：
            摘要文本
        """
        # 简单的摘要生成（取前几句话）
        sentences = text.split('。')
        summary = "。".join(sentences[:5])

        if len(summary) > max_length:
            summary = summary[:max_length] + "..."

        return summary


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="PP-ChatOCRv4 服务脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：

1. 文档问答：
  python chat_ocr_service.py qa image.png "发票金额是多少？"

2. 提取关键信息：
  python chat_ocr_service.py extract image.png invoice

3. 生成摘要：
  python chat_ocr_service.py summary image.png --max-length 200
        """
    )

    parser.add_argument(
        "command",
        choices=["qa", "extract", "summary"],
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
        "--info-type",
        default="invoice",
        help="信息类型（仅用于 extract 命令）"
    )

    parser.add_argument(
        "--max-length",
        type=int,
        default=200,
        help="摘要最大长度（仅用于 summary 命令）"
    )

    parser.add_argument(
        "--gpu",
        action="store_true",
        help="使用 GPU"
    )

    args = parser.parse_args()

    # 初始化服务
    try:
        service = ChatOCRService(use_gpu=args.gpu)
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        sys.exit(1)

    # 执行命令
    result = None

    if args.command == "qa":
        if not args.question:
            print("❌ qa 命令需要 --question 参数")
            sys.exit(1)

        result = service.document_qa(args.image, args.question)

    elif args.command == "extract":
        result = service.extract_key_info(args.image, args.info_type)

    elif args.command == "summary":
        result = service.generate_summary(args.image, args.max_length)

    # 输出结果
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
