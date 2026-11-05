#!/usr/bin/env python3
"""
Nano PDF 核心处理模块
纯本地PDF操作，无任何第三方框架/OpenClaw依赖
"""
import sys
import json
import os
from pathlib import Path
from pypdf import PdfReader, PdfWriter


class NanoPDF:
    """轻量级PDF处理器"""

    @staticmethod
    def extract_text(pdf_path: str) -> str:
        """提取PDF全部文本"""
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
        return text.strip()

    @staticmethod
    def get_metadata(pdf_path: str) -> dict:
        """获取PDF元数据"""
        reader = PdfReader(pdf_path)
        meta = reader.metadata
        return {
            "title": meta.title if meta.title else "无标题",
            "author": meta.author if meta.author else "无作者",
            "page_count": len(reader.pages),
            "creator": meta.creator if meta.creator else "未知",
            "created_at": str(meta.creation_date) if meta.creation_date else "未知",
            "producer": meta.producer if meta.producer else "未知"
        }

    @staticmethod
    def merge_pdfs(input_paths: list, output_path: str) -> str:
        """合并多个PDF"""
        writer = PdfWriter()
        for path in input_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"文件不存在：{path}")
            reader = PdfReader(path)
            for page in reader.pages:
                writer.add_page(page)

        with open(output_path, "wb") as f:
            writer.write(f)
        return output_path

    @staticmethod
    def split_pdf(pdf_path: str, output_dir: str) -> list:
        """按页面拆分PDF，每页一个文件"""
        Path(output_dir).mkdir(exist_ok=True)
        reader = PdfReader(pdf_path)
        files = []

        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            output_path = os.path.join(output_dir, f"page_{i+1}.pdf")

            with open(output_path, "wb") as f:
                writer.write(f)
            files.append(output_path)

        return files

    @staticmethod
    def extract_pages(pdf_path: str, output_path: str, start: int, end: int = None) -> str:
        """提取指定页码范围"""
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)

        # 页码校验
        start = max(1, start)
        if end is None or end > total_pages:
            end = total_pages

        writer = PdfWriter()
        for i in range(start-1, end):
            writer.add_page(reader.pages[i])

        with open(output_path, "wb") as f:
            writer.write(f)
        return output_path


def run(input_data: dict = None):
    """
    Skill 统一入口函数
    :param input_data: {
        "action": 操作类型(text/metadata/merge/split/extract_pages),
        "file_path": PDF文件路径,
        "file_paths": 多文件路径(merge专用),
        "output_path": 输出路径,
        "output_dir": 输出目录(split专用),
        "start_page": 起始页,
        "end_page": 结束页
    }
    """
    try:
        if not input_data or not isinstance(input_data, dict):
            input_data = {}

        action = input_data.get("action", "").lower()
        processor = NanoPDF()
        result_data = {}

        # 文本提取
        if action == "text":
            path = input_data["file_path"]
            result_data["text"] = processor.extract_text(path)

        # 元数据
        elif action == "metadata":
            path = input_data["file_path"]
            result_data["metadata"] = processor.get_metadata(path)

        # 合并PDF
        elif action == "merge":
            paths = input_data["file_paths"]
            out = input_data["output_path"]
            result_data["merged_file"] = processor.merge_pdfs(paths, out)

        # 拆分PDF
        elif action == "split":
            path = input_data["file_path"]
            out_dir = input_data["output_dir"]
            result_data["split_files"] = processor.split_pdf(path, out_dir)

        # 提取页面
        elif action == "extract_pages":
            path = input_data["file_path"]
            out = input_data["output_path"]
            start = input_data["start_page"]
            end = input_data.get("end_page")
            result_data["extracted_file"] = processor.extract_pages(path, out, start, end)

        else:
            return {
                "status": "error",
                "data": None,
                "message_for_user": "不支持的操作类型，请使用 text/metadata/merge/split/extract_pages"
            }

        return {
            "status": "success",
            "data": result_data,
            "message_for_user": "PDF处理完成"
        }

    except KeyError as e:
        return {"status": "error", "data": None, "message_for_user": f"缺少必要参数：{str(e)}"}
    except FileNotFoundError as e:
        return {"status": "error", "data": None, "message_for_user": f"文件不存在：{str(e)}"}
    except Exception as e:
        return {"status": "error", "data": None, "message_for_user": f"处理失败：{str(e)}"}


if __name__ == "__main__":
    # 命令行执行模式
    if not sys.stdin.isatty():
        input_json = sys.stdin.read()
        input_data = json.loads(input_json) if input_json else {}
    else:
        input_data = {}

    output = run(input_data)
    print(json.dumps(output, ensure_ascii=False))
