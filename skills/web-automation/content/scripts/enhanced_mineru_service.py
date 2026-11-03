#!/usr/bin/env python3
"""
增强版 MinerU 文档智能处理服务
新增功能：URL 直接下载 PDF、大文件优化、进度显示、断点续传

核心增强：
1. 从 URL 直接下载并解析 PDF
2. 下载进度实时显示
3. 大文件分块处理
4. 断点续传支持
5. 自动重试失败的下载

版本：2.0.0（增强版）
"""

import argparse
import sys
import json
import asyncio
import aiohttp
from typing import Optional, Dict, Any, List, Callable
from pathlib import Path
import os
from datetime import datetime


class DownloadProgress:
    """下载进度跟踪器"""
    
    def __init__(self, total_size: int = 0):
        """
        初始化进度跟踪器
        
        参数：
            total_size: 总大小（字节）
        """
        self.total_size = total_size
        self.downloaded_size = 0
        self.start_time = datetime.now()
        self.last_update_time = self.start_time
        self.last_downloaded = 0
    
    def update(self, chunk_size: int) -> Dict[str, Any]:
        """
        更新进度
        
        参数：
            chunk_size: 本次下载的字节数
        
        返回：
            进度信息
        """
        self.downloaded_size += chunk_size
        now = datetime.now()
        
        # 计算下载速度（每秒更新一次）
        speed = 0
        if (now - self.last_update_time).total_seconds() >= 1.0:
            elapsed = (now - self.last_update_time).total_seconds()
            speed = (self.downloaded_size - self.last_downloaded) / elapsed
            self.last_update_time = now
            self.last_downloaded = self.downloaded_size
        
        # 计算百分比
        percent = 0
        if self.total_size > 0:
            percent = (self.downloaded_size / self.total_size) * 100
        
        # 计算预计剩余时间
        eta = 0
        if speed > 0 and self.total_size > 0:
            remaining = self.total_size - self.downloaded_size
            eta = remaining / speed
        
        return {
            "total_size": self.total_size,
            "downloaded_size": self.downloaded_size,
            "percent": percent,
            "speed": speed,
            "eta": eta,
        }
    
    def get_elapsed_time(self) -> float:
        """获取已用时间（秒）"""
        return (datetime.now() - self.start_time).total_seconds()


class EnhancedMinerUService:
    """
    增强版 MinerU 文档处理服务
    
    新增功能：
    1. 从 URL 直接下载 PDF
    2. 下载进度显示
    3. 大文件优化
    4. 断点续传
    """
    
    def __init__(self, output_dir: str = ".web-automation/mineru-output"):
        """
        初始化服务
        
        参数：
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 下载目录
        self.download_dir = self.output_dir / "downloads"
        self.download_dir.mkdir(exist_ok=True)
        
        # 尝试导入 MinerU
        try:
            from magic_pdf.pipe.UNIPipe import UNIPipe
            from magic_pdf.rw.DiskReaderWriter import DiskReaderWriter
            self.MINERU_AVAILABLE = True
            self.UNIPipe = UNIPipe
            self.DiskReaderWriter = DiskReaderWriter
        except ImportError:
            self.MINERU_AVAILABLE = False
    
    async def download_pdf_from_url(
        self,
        url: str,
        output_path: Optional[str] = None,
        timeout: int = 600,
        chunk_size: int = 1024 * 1024,  # 1MB
        max_retries: int = 3,
        progress_callback: Optional[Callable[[Dict], None]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        从 URL 下载 PDF 文件
        
        参数：
            url: PDF 文件的 URL
            output_path: 输出路径（可选，默认自动生成）
            timeout: 超时时间（秒）
            chunk_size: 分块大小（字节）
            max_retries: 最大重试次数
            progress_callback: 进度回调函数
            headers: 自定义请求头
        
        返回：
            下载结果
        """
        try:
            # 生成输出路径
            if not output_path:
                # 从 URL 提取文件名
                filename = url.split("/")[-1].split("?")[0]
                if not filename.endswith(".pdf"):
                    filename = f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                output_path = str(self.download_dir / filename)
            
            output_file = Path(output_path)
            
            # 检查是否支持断点续传
            temp_file = output_file.with_suffix(".tmp")
            resume_position = 0
            
            if temp_file.exists():
                resume_position = temp_file.stat().st_size
                print(f"📦 检测到未完成的下载，从 {resume_position} 字节处继续")
            
            # 准备请求头
            request_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            }
            if headers:
                request_headers.update(headers)
            
            if resume_position > 0:
                request_headers["Range"] = f"bytes={resume_position}-"
            
            # 重试机制
            last_error = None
            for attempt in range(max_retries):
                try:
                    # 发起请求
                    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                        async with session.get(url, headers=request_headers) as response:
                            # 检查响应状态
                            if response.status == 404:
                                return {
                                    "success": False,
                                    "error": f"PDF 文件不存在: {url}"
                                }
                            
                            if response.status not in [200, 206]:
                                return {
                                    "success": False,
                                    "error": f"下载失败: HTTP {response.status}"
                                }
                            
                            # 获取文件大小
                            total_size = int(response.headers.get("Content-Length", 0))
                            if resume_position > 0 and response.status == 206:
                                # 断点续传：总大小需要加上已下载部分
                                total_size += resume_position
                            
                            # 初始化进度跟踪器
                            progress = DownloadProgress(total_size)
                            progress.downloaded_size = resume_position
                            
                            print(f"📥 开始下载: {url}")
                            print(f"   文件大小: {total_size / (1024*1024):.2f} MB")
                            
                            # 打开临时文件（追加模式）
                            mode = "ab" if resume_position > 0 else "wb"
                            with open(temp_file, mode) as f:
                                # 分块下载
                                async for chunk in response.content.iter_chunked(chunk_size):
                                    f.write(chunk)
                                    
                                    # 更新进度
                                    progress_info = progress.update(len(chunk))
                                    
                                    # 调用回调
                                    if progress_callback:
                                        progress_callback(progress_info)
                                    
                                    # 显示进度
                                    if progress_info["speed"] > 0:
                                        print(
                                            f"\r   进度: {progress_info['percent']:.1f}% | "
                                            f"速度: {progress_info['speed']/(1024*1024):.2f} MB/s | "
                                            f"剩余: {progress_info['eta']:.0f}s",
                                            end=""
                                        )
                            
                            print()  # 换行
                            
                            # 重命名临时文件
                            temp_file.rename(output_file)
                            
                            print(f"✅ 下载完成: {output_path}")
                            print(f"   耗时: {progress.get_elapsed_time():.1f}秒")
                            
                            return {
                                "success": True,
                                "path": str(output_file),
                                "size": output_file.stat().st_size,
                                "url": url,
                                "elapsed_time": progress.get_elapsed_time(),
                            }
                    
                except asyncio.TimeoutError:
                    last_error = "下载超时"
                    print(f"\n⏳ 下载超时，尝试重试 ({attempt + 1}/{max_retries})")
                    
                except aiohttp.ClientError as e:
                    last_error = str(e)
                    print(f"\n❌ 下载错误: {e}，尝试重试 ({attempt + 1}/{max_retries})")
                
                # 等待后重试
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
            
            return {
                "success": False,
                "error": f"下载失败，已重试 {max_retries} 次: {last_error}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"下载失败: {str(e)}"
            }
    
    async def download_and_parse_pdf(
        self,
        url: str,
        output_format: str = "markdown",
        timeout: int = 600,
        max_retries: int = 3,
        progress_callback: Optional[Callable[[Dict], None]] = None,
    ) -> Dict[str, Any]:
        """
        从 URL 下载并解析 PDF
        
        参数：
            url: PDF 文件的 URL
            output_format: 输出格式 (markdown/json/html)
            timeout: 超时时间（秒）
            max_retries: 最大重试次数
            progress_callback: 进度回调函数
        
        返回：
            解析结果
        """
        if not self.MINERU_AVAILABLE:
            return {
                "success": False,
                "error": "MinerU (magic-pdf) 未安装，请运行: pip install magic-pdf[full]"
            }
        
        # 1. 下载 PDF
        download_result = await self.download_pdf_from_url(
            url,
            timeout=timeout,
            max_retries=max_retries,
            progress_callback=progress_callback,
        )
        
        if not download_result["success"]:
            return download_result
        
        # 2. 解析 PDF
        print(f"\n📄 开始解析 PDF...")
        parse_result = self.parse_pdf(
            download_result["path"],
            output_format=output_format
        )
        
        # 合并结果
        return {
            **parse_result,
            "download": download_result
        }
    
    def parse_pdf(
        self,
        pdf_path: str,
        output_format: str = "markdown",
        ocr_enabled: bool = True,
        extract_images: bool = False
    ) -> Dict[str, Any]:
        """
        解析 PDF 文档（增强版）
        
        参数：
            pdf_path: PDF 文件路径
            output_format: 输出格式 (markdown/json/html)
            ocr_enabled: 是否启用 OCR
            extract_images: 是否提取图片
        
        返回：
            解析结果
        """
        if not self.MINERU_AVAILABLE:
            return {
                "success": False,
                "error": "MinerU (magic-pdf) 未安装"
            }
        
        try:
            pdf_file = Path(pdf_path)
            
            if not pdf_file.exists():
                return {
                    "success": False,
                    "error": f"PDF 文件不存在: {pdf_path}"
                }
            
            # 检查文件大小
            file_size = pdf_file.stat().st_size
            print(f"   文件大小: {file_size / (1024*1024):.2f} MB")
            
            # 大文件警告
            if file_size > 50 * 1024 * 1024:  # 50MB
                print("⚠️  文件较大，解析可能需要较长时间...")
            
            # 读取 PDF
            with open(pdf_file, "rb") as f:
                pdf_bytes = f.read()
            
            # 创建输出目录
            doc_output_dir = self.output_dir / pdf_file.stem
            doc_output_dir.mkdir(exist_ok=True)
            
            # 初始化 UNIPipe
            image_writer = self.DiskReaderWriter(str(doc_output_dir))
            pipe = self.UNIPipe(pdf_bytes, model_json=None, image_writer=image_writer)
            
            # 解析 PDF
            print("   正在解析...")
            pipe.parse()
            
            # 生成输出
            if output_format == "markdown":
                data = pipe.pipe_mk_markdown("")
            elif output_format == "json":
                data = pipe.pipe_mk_uni_format("")
            elif output_format == "html":
                data = pipe.pipe_mk_html("")
            else:
                return {
                    "success": False,
                    "error": f"不支持的输出格式: {output_format}"
                }
            
            print(f"✅ 解析完成")
            
            return {
                "success": True,
                "data": data,
                "output_format": output_format,
                "output_dir": str(doc_output_dir),
                "file_size": file_size,
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"解析失败: {str(e)}"
            }
    
    async def batch_download_and_parse(
        self,
        urls: List[str],
        output_format: str = "markdown",
        max_concurrent: int = 3,
        timeout: int = 600,
    ) -> Dict[str, Any]:
        """
        批量下载并解析 PDF
        
        参数：
            urls: PDF URL 列表
            output_format: 输出格式
            max_concurrent: 最大并发数
            timeout: 超时时间
        
        返回：
            批量处理结果
        """
        results = []
        failed = []
        
        # 使用信号量控制并发
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_url(url: str, index: int):
            async with semaphore:
                print(f"\n[{index + 1}/{len(urls)}] 处理: {url}")
                result = await self.download_and_parse_pdf(
                    url,
                    output_format=output_format,
                    timeout=timeout
                )
                result["url"] = url
                result["index"] = index
                
                if result["success"]:
                    results.append(result)
                else:
                    failed.append(result)
        
        # 并发执行
        tasks = [
            process_url(url, i)
            for i, url in enumerate(urls)
        ]
        await asyncio.gather(*tasks)
        
        return {
            "success": True,
            "total": len(urls),
            "success_count": len(results),
            "failed_count": len(failed),
            "results": results,
            "failed": failed
        }


def print_progress(info: Dict):
    """打印下载进度"""
    pass  # 进度已在 download_pdf_from_url 中打印


async def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="增强版 MinerU 文档处理工具 - 支持URL下载和优化处理"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # download-pdf 命令
    download_parser = subparsers.add_parser("download-pdf", help="从 URL 下载 PDF")
    download_parser.add_argument("--url", type=str, required=True, help="PDF URL")
    download_parser.add_argument("--output", type=str, help="输出路径")
    download_parser.add_argument("--timeout", type=int, default=600, help="超时时间（秒）")
    download_parser.add_argument("--max-retries", type=int, default=3, help="最大重试次数")
    
    # download-and-parse 命令
    dap_parser = subparsers.add_parser("download-and-parse", help="下载并解析 PDF")
    dap_parser.add_argument("--url", type=str, required=True, help="PDF URL")
    dap_parser.add_argument("--output-format", type=str, default="markdown",
                           choices=["markdown", "json", "html"], help="输出格式")
    dap_parser.add_argument("--timeout", type=int, default=600, help="超时时间（秒）")
    
    # batch-process 命令
    batch_parser = subparsers.add_parser("batch-process", help="批量下载并解析")
    batch_parser.add_argument("--urls", type=str, nargs="+", required=True, help="PDF URL 列表")
    batch_parser.add_argument("--output-format", type=str, default="markdown", help="输出格式")
    batch_parser.add_argument("--max-concurrent", type=int, default=3, help="最大并发数")
    
    # parse-pdf 命令（保留原有功能）
    pdf_parser = subparsers.add_parser("parse-pdf", help="解析本地 PDF")
    pdf_parser.add_argument("--pdf-path", type=str, required=True, help="PDF 文件路径")
    pdf_parser.add_argument("--output-format", type=str, default="markdown",
                           choices=["markdown", "json", "html"], help="输出格式")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 初始化服务
    service = EnhancedMinerUService()
    
    if args.command == "download-pdf":
        result = await service.download_pdf_from_url(
            url=args.url,
            output_path=args.output,
            timeout=args.timeout,
            max_retries=args.max_retries,
            progress_callback=print_progress,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.command == "download-and-parse":
        result = await service.download_and_parse_pdf(
            url=args.url,
            output_format=args.output_format,
            timeout=args.timeout,
            progress_callback=print_progress,
        )
        # 不打印解析的 data 内容（太大）
        output_result = {k: v for k, v in result.items() if k != "data"}
        if "data" in result:
            output_result["data_length"] = len(str(result["data"]))
        print(json.dumps(output_result, ensure_ascii=False, indent=2))
    
    elif args.command == "batch-process":
        result = await service.batch_download_and_parse(
            urls=args.urls,
            output_format=args.output_format,
            max_concurrent=args.max_concurrent,
        )
        # 简化输出
        output_result = {
            "success": result["success"],
            "total": result["total"],
            "success_count": result["success_count"],
            "failed_count": result["failed_count"],
        }
        print(json.dumps(output_result, ensure_ascii=False, indent=2))
    
    elif args.command == "parse-pdf":
        result = service.parse_pdf(
            pdf_path=args.pdf_path,
            output_format=args.output_format,
        )
        output_result = {k: v for k, v in result.items() if k != "data"}
        if "data" in result:
            output_result["data_length"] = len(str(result["data"]))
        print(json.dumps(output_result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
