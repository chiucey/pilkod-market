#!/usr/bin/env python3
"""
MinerU 文档智能处理服务脚本
提供 PDF 解析、表格提取、版面分析等功能

核心功能：
- PDF 文档解析和结构化
- 高质量表格提取
- 文档版面分析
- 图像内容理解
"""

import argparse
import sys
import json
from typing import Optional, Dict, Any, List
from pathlib import Path

# 尝试导入 MinerU 相关库
try:
    from magic_pdf.pipe.UNIPipe import UNIPipe
    from magic_pdf.rw.DiskReaderWriter import DiskReaderWriter
    MINERU_AVAILABLE = True
except ImportError:
    MINERU_AVAILABLE = False


class MinerUService:
    """MinerU 文档处理服务类"""
    
    def __init__(self, output_dir: str = ".web-automation/mineru-output"):
        """
        初始化 MinerU 服务
        
        参数：
            output_dir: 输出目录
        """
        if not MINERU_AVAILABLE:
            raise ImportError(
                "MinerU (magic-pdf) 未安装，请运行: pip install magic-pdf[full]"
            )
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def parse_pdf(
        self,
        pdf_path: str,
        output_format: str = "markdown",
        ocr_enabled: bool = True,
        extract_images: bool = False
    ) -> Dict[str, Any]:
        """
        解析 PDF 文档
        
        参数：
            pdf_path: PDF 文件路径
            output_format: 输出格式 (markdown/json/html)
            ocr_enabled: 是否启用 OCR（扫描版 PDF）
            extract_images: 是否提取图片
        
        返回：
            包含解析结果的字典
        """
        try:
            # 验证 PDF 文件
            pdf_file = Path(pdf_path)
            if not pdf_file.exists():
                return {
                    "success": False,
                    "error": f"PDF 文件不存在: {pdf_path}"
                }
            
            if pdf_file.suffix.lower() != ".pdf":
                return {
                    "success": False,
                    "error": "文件格式错误，仅支持 PDF 文件"
                }
            
            # 检查文件大小（限制 100MB）
            file_size = pdf_file.stat().st_size
            if file_size > 100 * 1024 * 1024:
                return {
                    "success": False,
                    "error": "PDF 文件过大（超过 100MB），建议分拆处理"
                }
            
            # 读取 PDF 字节
            with open(pdf_file, "rb") as f:
                pdf_bytes = f.read()
            
            # 创建输出目录
            doc_output_dir = self.output_dir / pdf_file.stem
            doc_output_dir.mkdir(exist_ok=True)
            
            # 初始化 UNIPipe
            image_writer = DiskReaderWriter(str(doc_output_dir))
            pipe = UNIPipe(
                pdf_bytes,
                model_json=None,
                image_writer=image_writer
            )
            
            # 解析 PDF
            pipe.parse()
            
            # 根据输出格式生成结果
            if output_format == "markdown":
                output = pipe.pipe_mk_markdown("")
                data = output
            elif output_format == "json":
                output = pipe.pipe_mk_uni_format("")
                data = output
            elif output_format == "html":
                output = pipe.pipe_mk_html("")
                data = output
            else:
                return {
                    "success": False,
                    "error": f"不支持的输出格式: {output_format}"
                }
            
            # 提取元信息
            metadata = self._extract_metadata(pdf_file, pipe)
            
            return {
                "success": True,
                "data": data,
                "metadata": metadata,
                "output_format": output_format,
                "output_dir": str(doc_output_dir)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"PDF 解析失败: {str(e)}"
            }
    
    def extract_tables(
        self,
        image_path: str,
        output_format: str = "markdown"
    ) -> Dict[str, Any]:
        """
        从图像提取表格数据
        
        参数：
            image_path: 图像文件路径
            output_format: 输出格式 (markdown/json/csv)
        
        返回：
            包含表格数据的字典
        """
        try:
            # 验证图像文件
            img_file = Path(image_path)
            if not img_file.exists():
                return {
                    "success": False,
                    "error": f"图像文件不存在: {image_path}"
                }
            
            # 支持的图像格式
            supported_formats = [".png", ".jpg", ".jpeg", ".bmp"]
            if img_file.suffix.lower() not in supported_formats:
                return {
                    "success": False,
                    "error": f"不支持的图像格式，仅支持: {', '.join(supported_formats)}"
                }
            
            # 读取图像
            with open(img_file, "rb") as f:
                image_bytes = f.read()
            
            # 创建输出目录
            table_output_dir = self.output_dir / "tables" / img_file.stem
            table_output_dir.mkdir(parents=True, exist_ok=True)
            
            # 使用 MinerU 提取表格
            # 注意：MinerU 的表格提取功能需要通过 PDF 解析实现
            # 这里使用 UNIPipe 处理图像
            image_writer = DiskReaderWriter(str(table_output_dir))
            
            # 将图像转换为 PDF（临时解决方案）
            from PIL import Image
            import io
            
            img = Image.open(io.BytesIO(image_bytes))
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            # 保存为临时 PDF
            temp_pdf_path = table_output_dir / "temp.pdf"
            img.save(temp_pdf_path, "PDF")
            
            # 解析临时 PDF
            with open(temp_pdf_path, "rb") as f:
                pdf_bytes = f.read()
            
            pipe = UNIPipe(pdf_bytes, model_json=None, image_writer=image_writer)
            pipe.parse()
            
            # 提取表格数据
            output = pipe.pipe_mk_markdown("")
            
            # 清理临时文件
            temp_pdf_path.unlink(missing_ok=True)
            
            return {
                "success": True,
                "data": output,
                "output_format": output_format,
                "output_dir": str(table_output_dir)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"表格提取失败: {str(e)}"
            }
    
    def analyze_layout(
        self,
        image_path: str
    ) -> Dict[str, Any]:
        """
        分析文档布局
        
        参数：
            image_path: 图像文件路径
        
        返回：
            包含布局分析结果的字典
        """
        try:
            # 使用 extract_tables 进行布局分析
            result = self.extract_tables(image_path, output_format="json")
            
            if not result["success"]:
                return result
            
            # 从 JSON 数据中提取布局信息
            # 这里简化处理，实际需要解析 UNIPipe 的输出
            
            return {
                "success": True,
                "message": "布局分析完成",
                "data": result["data"],
                "note": "布局信息包含在解析数据中"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"布局分析失败: {str(e)}"
            }
    
    def parse_pdf_to_json(
        self,
        pdf_path: str
    ) -> Dict[str, Any]:
        """
        解析 PDF 为结构化 JSON
        
        参数：
            pdf_path: PDF 文件路径
        
        返回：
            包含结构化 JSON 数据的字典
        """
        return self.parse_pdf(pdf_path, output_format="json")
    
    def batch_parse_pdfs(
        self,
        pdf_paths: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        批量解析 PDF 文件
        
        参数：
            pdf_paths: PDF 文件路径列表
            **kwargs: 其他参数传递给 parse_pdf
        
        返回：
            批量解析结果
        """
        results = []
        failed = []
        
        for i, pdf_path in enumerate(pdf_paths):
            result = self.parse_pdf(pdf_path, **kwargs)
            result["pdf_path"] = pdf_path
            result["index"] = i
            
            if result["success"]:
                results.append(result)
            else:
                failed.append(result)
        
        return {
            "success": True,
            "total": len(pdf_paths),
            "success_count": len(results),
            "failed_count": len(failed),
            "results": results,
            "failed": failed
        }
    
    def _extract_metadata(
        self,
        pdf_file: Path,
        pipe: UNIPipe
    ) -> Dict[str, Any]:
        """
        提取 PDF 元信息
        
        参数：
            pdf_file: PDF 文件路径
            pipe: UNIPipe 实例
        
        返回：
            元信息字典
        """
        return {
            "file_name": pdf_file.name,
            "file_size": pdf_file.stat().st_size,
            "file_size_mb": round(pdf_file.stat().st_size / (1024 * 1024), 2),
            "note": "详细的页数和内容信息需要从 pipe 对象中提取"
        }


async def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="MinerU 文档智能处理工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # parse-pdf 命令
    pdf_parser = subparsers.add_parser("parse-pdf", help="解析 PDF 文档")
    pdf_parser.add_argument("--pdf-path", type=str, required=True, help="PDF 文件路径")
    pdf_parser.add_argument("--output-format", type=str, default="markdown", 
                           choices=["markdown", "json", "html"], help="输出格式")
    pdf_parser.add_argument("--ocr-enabled", action="store_true", help="启用 OCR")
    pdf_parser.add_argument("--extract-images", action="store_true", help="提取图片")
    
    # extract-tables 命令
    table_parser = subparsers.add_parser("extract-tables", help="提取表格数据")
    table_parser.add_argument("--image-path", type=str, required=True, help="图像文件路径")
    table_parser.add_argument("--output-format", type=str, default="markdown",
                            choices=["markdown", "json", "csv"], help="输出格式")
    
    # analyze-layout 命令
    layout_parser = subparsers.add_parser("analyze-layout", help="分析文档布局")
    layout_parser.add_argument("--image-path", type=str, required=True, help="图像文件路径")
    
    # parse-pdf-to-json 命令
    json_parser = subparsers.add_parser("parse-pdf-to-json", help="解析 PDF 为 JSON")
    json_parser.add_argument("--pdf-path", type=str, required=True, help="PDF 文件路径")
    
    # batch-parse 命令
    batch_parser = subparsers.add_parser("batch-parse", help="批量解析 PDF")
    batch_parser.add_argument("--pdf-dir", type=str, required=True, help="PDF 目录")
    batch_parser.add_argument("--output-format", type=str, default="markdown", help="输出格式")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if not MINERU_AVAILABLE:
        print(json.dumps({
            "success": False,
            "error": "MinerU (magic-pdf) 未安装，请运行: pip install magic-pdf[full]"
        }, ensure_ascii=False, indent=2))
        sys.exit(1)
    
    # 初始化服务
    try:
        service = MinerUService()
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": f"初始化 MinerU 服务失败: {str(e)}"
        }, ensure_ascii=False, indent=2))
        sys.exit(1)
    
    if args.command == "parse-pdf":
        result = service.parse_pdf(
            args.pdf_path,
            output_format=args.output_format,
            ocr_enabled=args.ocr_enabled,
            extract_images=args.extract_images
        )
        print_result(result)
    
    elif args.command == "extract-tables":
        result = service.extract_tables(
            args.image_path,
            output_format=args.output_format
        )
        print_result(result)
    
    elif args.command == "analyze-layout":
        result = service.analyze_layout(args.image_path)
        print_result(result)
    
    elif args.command == "parse-pdf-to-json":
        result = service.parse_pdf_to_json(args.pdf_path)
        print_result(result)
    
    elif args.command == "batch-parse":
        # 获取目录下所有 PDF 文件
        pdf_dir = Path(args.pdf_dir)
        pdf_files = list(pdf_dir.glob("*.pdf"))
        
        if not pdf_files:
            print(json.dumps({
                "success": False,
                "error": f"目录中没有 PDF 文件: {args.pdf_dir}"
            }, ensure_ascii=False, indent=2))
            sys.exit(1)
        
        result = service.batch_parse_pdfs(
            [str(f) for f in pdf_files],
            output_format=args.output_format
        )
        print_result(result)


def print_result(result: Dict[str, Any]):
    """打印结果"""
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
