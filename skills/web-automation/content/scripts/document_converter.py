#!/usr/bin/env python3
"""
文档格式转换服务脚本（完整版）
支持 Word、PPT、Excel 等格式转换为 PDF

核心功能：
- 系统环境检测（操作系统、架构、LibreOffice 安装状态）
- 跨平台自动安装 LibreOffice
- 文档格式转换
- 批量转换
- 格式自动检测
"""

import argparse
import sys
import json
import subprocess
import shutil
import platform
import os
import tempfile
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path

# 尝试导入 requests（用于下载安装包）
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class SystemDetector:
    """系统环境检测器"""
    
    @staticmethod
    def get_os_type() -> str:
        """获取操作系统类型"""
        system = platform.system().lower()
        if system == "windows":
            return "windows"
        elif system == "darwin":
            return "darwin"  # macOS
        elif system == "linux":
            return "linux"
        else:
            return "unknown"
    
    @staticmethod
    def get_architecture() -> str:
        """获取系统架构"""
        machine = platform.machine().lower()
        
        # 标准化架构名称
        if machine in ["x86_64", "amd64"]:
            return "x86_64"
        elif machine in ["arm64", "aarch64"]:
            return "arm64"
        elif machine.startswith("arm"):
            return "arm"
        elif machine.startswith("mips"):
            return "mips"
        elif machine.startswith("i386") or machine.startswith("i686"):
            return "x86"
        else:
            return "unknown"
    
    @staticmethod
    def get_libreoffice_installed() -> Tuple[bool, Optional[str]]:
        """检查 LibreOffice 是否安装
        
        返回：
            (是否安装, 版本信息)
        """
        # 检查不同的命令名称
        commands = ["soffice", "libreoffice", "libreoffice7.x", "libreoffice24.2"]
        
        for cmd in commands:
            if shutil.which(cmd):
                try:
                    # 获取版本
                    result = subprocess.run(
                        [cmd, "--version"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        version = result.stdout.strip()
                        return True, version
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
        
        return False, None
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """获取完整的系统信息"""
        os_type = SystemDetector.get_os_type()
        arch = SystemDetector.get_architecture()
        installed, version = SystemDetector.get_libreoffice_installed()
        
        return {
            "os_type": os_type,
            "os_version": platform.version(),
            "architecture": arch,
            "python_version": platform.python_version(),
            "libreoffice": {
                "installed": installed,
                "version": version if installed else None
            }
        }


class LibreOfficeInstaller:
    """LibreOffice 自动安装器"""
    
    # LibreOffice 版本
    VERSION = "24.2.5"
    
    # 下载镜像
    MIRROR_URL = "https://download.documentfoundation.org/libreoffice/stable"
    
    def __init__(self):
        self.system_info = SystemDetector.get_system_info()
    
    def get_download_url(self) -> Optional[str]:
        """获取适合当前系统的下载 URL"""
        os_type = self.system_info["os_type"]
        arch = self.system_info["architecture"]
        
        if os_type == "windows":
            if arch == "x86_64":
                return f"{self.MIRROR_URL}/{self.VERSION}/win/x86_64/LibreOffice_{self.VERSION}_Win_x86-64.msi"
            else:
                return f"{self.MIRROR_URL}/{self.VERSION}/win/x86/LibreOffice_{self.VERSION}_Win_x86.msi"
        
        elif os_type == "darwin":
            if arch == "arm64":
                return f"{self.MIRROR_URL}/{self.VERSION}/mac/aarch64/LibreOffice_{self.VERSION}_MacOS_aarch64.dmg"
            else:
                return f"{self.MIRROR_URL}/{self.VERSION}/mac/x86_64/LibreOffice_{self.VERSION}_MacOS_x86-64.dmg"
        
        elif os_type == "linux":
            # Linux 不提供通用下载，需要使用包管理器
            return None
        
        return None
    
    def download_installer(self, url: str, dest: str) -> Dict[str, Any]:
        """下载安装包
        
        参数：
            url: 下载地址
            dest: 保存路径
        
        返回：
            下载结果
        """
        if not REQUESTS_AVAILABLE:
            return {
                "success": False,
                "error": "requests 库未安装，无法下载。请运行: pip install requests"
            }
        
        try:
            print(f"正在下载: {url}")
            print(f"保存到: {dest}")
            
            # 创建目标目录
            dest_path = Path(dest)
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 下载文件
            response = requests.get(url, stream=True, timeout=300)
            response.raise_for_status()
            
            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0
            
            with open(dest_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # 显示进度
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r下载进度: {progress:.1f}%", end="")
            
            print()  # 换行
            
            return {
                "success": True,
                "file_path": str(dest_path),
                "file_size": dest_path.stat().st_size
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"下载失败: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"下载失败: {str(e)}"
            }
    
    def install_linux(self) -> Dict[str, Any]:
        """在 Linux 上安装 LibreOffice"""
        # 检测包管理器
        package_managers = [
            {"cmd": "apt-get", "install": "sudo apt-get install -y libreoffice --no-install-recommends"},
            {"cmd": "yum", "install": "sudo yum install -y libreoffice"},
            {"cmd": "dnf", "install": "sudo dnf install -y libreoffice"},
            {"cmd": "pacman", "install": "sudo pacman -S --noconfirm libreoffice-fresh"}
        ]
        
        for pm in package_managers:
            if shutil.which(pm["cmd"]):
                print(f"检测到包管理器: {pm['cmd']}")
                print(f"执行安装命令: {pm['install']}")
                
                try:
                    result = subprocess.run(
                        pm["install"],
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=600  # 10分钟超时
                    )
                    
                    if result.returncode == 0:
                        return {
                            "success": True,
                            "method": "package_manager",
                            "package_manager": pm["cmd"]
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"安装失败: {result.stderr}"
                        }
                except subprocess.TimeoutExpired:
                    return {
                        "success": False,
                        "error": "安装超时（超过 10 分钟）"
                    }
                except Exception as e:
                    continue
        
        return {
            "success": False,
            "error": "未找到支持的包管理器，请手动安装 LibreOffice"
        }
    
    def install_windows(self, installer_path: str) -> Dict[str, Any]:
        """在 Windows 上安装 LibreOffice"""
        try:
            # 使用 msiexec 安装
            cmd = [
                "msiexec",
                "/i", installer_path,
                "/qn",  # 静默安装
                "/norestart"
            ]
            
            print(f"执行安装命令: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10分钟超时
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "method": "msiexec"
                }
            else:
                return {
                    "success": False,
                    "error": f"安装失败: {result.stderr}"
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "安装超时（超过 10 分钟）"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"安装失败: {str(e)}"
            }
    
    def install_macos(self, installer_path: str) -> Dict[str, Any]:
        """在 macOS 上安装 LibreOffice"""
        try:
            # 挂载 DMG 并安装
            print(f"挂载 DMG 文件: {installer_path}")
            
            # 使用 hdiutil 挂载
            mount_result = subprocess.run(
                ["hdiutil", "attach", installer_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if mount_result.returncode != 0:
                return {
                    "success": False,
                    "error": f"挂载 DMG 失败: {mount_result.stderr}"
                }
            
            # 获取挂载点
            mount_output = mount_result.stdout
            mount_point = None
            for line in mount_output.split("\n"):
                if "/Volumes/" in line:
                    mount_point = line.split("\t")[-1]
                    break
            
            if not mount_point:
                return {
                    "success": False,
                    "error": "无法确定 DMG 挂载点"
                }
            
            # 查找 .app 文件
            app_path = None
            mount_dir = Path(mount_point)
            for item in mount_dir.iterdir():
                if item.suffix == ".app":
                    app_path = item
                    break
            
            if not app_path:
                return {
                    "success": False,
                    "error": "DMG 中未找到 .app 文件"
                }
            
            # 复制到 Applications 目录
            print(f"安装到 /Applications/{app_path.name}")
            subprocess.run(
                ["cp", "-R", str(app_path), "/Applications/"],
                timeout=300
            )
            
            # 卸载 DMG
            subprocess.run(
                ["hdiutil", "detach", mount_point],
                timeout=30
            )
            
            return {
                "success": True,
                "method": "dmg"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"安装失败: {str(e)}"
            }
    
    def install(self, force: bool = False) -> Dict[str, Any]:
        """安装 LibreOffice
        
        参数：
            force: 是否强制重新安装
        
        返回：
            安装结果
        """
        # 检查是否已安装
        installed, version = SystemDetector.get_libreoffice_installed()
        if installed and not force:
            return {
                "success": True,
                "message": f"LibreOffice 已安装: {version}",
                "version": version
            }
        
        os_type = self.system_info["os_type"]
        
        # 根据操作系统执行不同的安装方法
        if os_type == "linux":
            result = self.install_linux()
        
        elif os_type == "windows":
            # 获取下载 URL
            download_url = self.get_download_url()
            if not download_url:
                return {
                    "success": False,
                    "error": "无法获取 Windows 下载 URL"
                }
            
            # 下载安装包
            temp_dir = Path(tempfile.gettempdir())
            installer_path = temp_dir / "LibreOffice_installer.msi"
            
            download_result = self.download_installer(download_url, str(installer_path))
            if not download_result["success"]:
                return download_result
            
            # 安装
            result = self.install_windows(str(installer_path))
            
            # 清理
            try:
                installer_path.unlink()
            except:
                pass
        
        elif os_type == "darwin":
            # 获取下载 URL
            download_url = self.get_download_url()
            if not download_url:
                return {
                    "success": False,
                    "error": "无法获取 macOS 下载 URL"
                }
            
            # 下载安装包
            temp_dir = Path(tempfile.gettempdir())
            installer_path = temp_dir / "LibreOffice_installer.dmg"
            
            download_result = self.download_installer(download_url, str(installer_path))
            if not download_result["success"]:
                return download_result
            
            # 安装
            result = self.install_macos(str(installer_path))
            
            # 清理
            try:
                installer_path.unlink()
            except:
                pass
        
        else:
            return {
                "success": False,
                "error": f"不支持的操作系统: {os_type}"
            }
        
        # 验证安装
        if result["success"]:
            installed, version = SystemDetector.get_libreoffice_installed()
            if installed:
                result["version"] = version
                result["message"] = f"LibreOffice 安装成功: {version}"
            else:
                result["success"] = False
                result["error"] = "安装完成但验证失败"
        
        return result


class DocumentConverter:
    """文档格式转换服务类"""
    
    # 支持的源格式
    SUPPORTED_FORMATS = {
        ".doc": "Microsoft Word 97-2003",
        ".docx": "Microsoft Word 2007+",
        ".ppt": "Microsoft PowerPoint 97-2003",
        ".pptx": "Microsoft PowerPoint 2007+",
        ".xls": "Microsoft Excel 97-2003",
        ".xlsx": "Microsoft Excel 2007+",
        ".odt": "OpenDocument Text",
        ".ods": "OpenDocument Spreadsheet",
        ".odp": "OpenDocument Presentation",
        ".rtf": "Rich Text Format",
        ".txt": "Plain Text",
        ".html": "HTML Document",
        ".htm": "HTML Document"
    }
    
    def __init__(self, output_dir: str = ".web-automation/converted"):
        """
        初始化文档转换服务
        
        参数：
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 检查 LibreOffice 是否安装
        installed, version = SystemDetector.get_libreoffice_installed()
        if not installed:
            raise RuntimeError(
                "LibreOffice 未安装。\n"
                "请运行: python scripts/document_converter.py install-libreoffice\n"
                "或手动安装：\n"
                "  Ubuntu/Debian: sudo apt-get install libreoffice --no-install-recommends\n"
                "  macOS: brew install --cask libreoffice\n"
                "  Windows: 下载并安装 https://www.libreoffice.org/"
            )
        
        self.libreoffice_version = version
    
    def _get_libreoffice_command(self) -> str:
        """获取 LibreOffice 命令"""
        # 检查不同的命令名称
        for cmd in ["soffice", "libreoffice", "libreoffice7.x", "libreoffice24.2"]:
            if shutil.which(cmd):
                return cmd
        
        raise RuntimeError("未找到 LibreOffice 命令")
    
    def convert_to_pdf(
        self,
        input_file: str,
        output_dir: Optional[str] = None,
        remove_source: bool = False
    ) -> Dict[str, Any]:
        """
        转换文档为 PDF
        
        参数：
            input_file: 输入文件路径
            output_dir: 输出目录（可选）
            remove_source: 是否删除源文件
        
        返回：
            包含转换结果的字典
        """
        try:
            # 验证输入文件
            input_path = Path(input_file)
            if not input_path.exists():
                return {
                    "success": False,
                    "error": f"文件不存在: {input_file}"
                }
            
            # 检查文件格式
            file_ext = input_path.suffix.lower()
            if file_ext not in self.SUPPORTED_FORMATS:
                return {
                    "success": False,
                    "error": f"不支持的文件格式: {file_ext}\n"
                            f"支持的格式: {', '.join(self.SUPPORTED_FORMATS.keys())}"
                }
            
            # 检查文件大小（建议 <50MB）
            file_size = input_path.stat().st_size
            if file_size > 50 * 1024 * 1024:
                return {
                    "success": False,
                    "error": f"文件过大（{file_size / (1024*1024):.2f}MB），建议 <50MB"
                }
            
            # 确定输出目录
            if output_dir:
                out_dir = Path(output_dir)
            else:
                out_dir = self.output_dir
            
            out_dir.mkdir(parents=True, exist_ok=True)
            
            # 获取 LibreOffice 命令
            libreoffice_cmd = self._get_libreoffice_command()
            
            # 执行转换
            cmd = [
                libreoffice_cmd,
                "--headless",
                "--convert-to", "pdf",
                "--outdir", str(out_dir),
                str(input_path)
            ]
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if process.returncode != 0:
                return {
                    "success": False,
                    "error": f"转换失败: {process.stderr}"
                }
            
            # 查找生成的 PDF 文件
            pdf_path = out_dir / f"{input_path.stem}.pdf"
            
            if not pdf_path.exists():
                return {
                    "success": False,
                    "error": "转换完成但未找到 PDF 文件"
                }
            
            # 验证 PDF 文件
            pdf_size = pdf_path.stat().st_size
            if pdf_size == 0:
                pdf_path.unlink()
                return {
                    "success": False,
                    "error": "生成的 PDF 文件为空"
                }
            
            # 删除源文件（如果需要）
            if remove_source:
                input_path.unlink()
            
            return {
                "success": True,
                "input_file": str(input_path),
                "output_file": str(pdf_path),
                "input_format": file_ext,
                "output_format": ".pdf",
                "input_size": file_size,
                "output_size": pdf_size,
                "compression_ratio": round(pdf_size / file_size, 2) if file_size > 0 else 0
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "转换超时（超过 5 分钟）"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"转换失败: {str(e)}"
            }
    
    def batch_convert(
        self,
        input_files: List[str],
        output_dir: Optional[str] = None,
        remove_source: bool = False
    ) -> Dict[str, Any]:
        """批量转换文档为 PDF"""
        results = []
        failed = []
        
        for i, input_file in enumerate(input_files):
            result = self.convert_to_pdf(
                input_file,
                output_dir=output_dir,
                remove_source=remove_source
            )
            result["index"] = i
            
            if result["success"]:
                results.append(result)
            else:
                failed.append(result)
        
        return {
            "success": True,
            "total": len(input_files),
            "success_count": len(results),
            "failed_count": len(failed),
            "results": results,
            "failed": failed
        }
    
    def convert_directory(
        self,
        input_dir: str,
        output_dir: Optional[str] = None,
        recursive: bool = False,
        remove_source: bool = False
    ) -> Dict[str, Any]:
        """转换目录中的所有文档"""
        input_path = Path(input_dir)
        if not input_path.exists() or not input_path.is_dir():
            return {
                "success": False,
                "error": f"目录不存在或无效: {input_dir}"
            }
        
        # 收集所有支持的文件
        if recursive:
            files = []
            for ext in self.SUPPORTED_FORMATS.keys():
                files.extend(input_path.rglob(f"*{ext}"))
        else:
            files = []
            for ext in self.SUPPORTED_FORMATS.keys():
                files.extend(input_path.glob(f"*{ext}"))
        
        if not files:
            return {
                "success": False,
                "error": f"目录中没有支持的文档: {input_dir}"
            }
        
        # 批量转换
        return self.batch_convert(
            [str(f) for f in files],
            output_dir=output_dir,
            remove_source=remove_source
        )
    
    def detect_format(self, file_path: str) -> Dict[str, Any]:
        """检测文档格式"""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext in self.SUPPORTED_FORMATS:
            return {
                "success": True,
                "format": file_ext,
                "description": self.SUPPORTED_FORMATS[file_ext],
                "supported": True
            }
        else:
            return {
                "success": True,
                "format": file_ext,
                "supported": False,
                "description": "未知格式",
                "supported_formats": list(self.SUPPORTED_FORMATS.keys())
            }
    
    def get_supported_formats(self) -> Dict[str, Any]:
        """获取所有支持的格式"""
        return {
            "success": True,
            "count": len(self.SUPPORTED_FORMATS),
            "formats": self.SUPPORTED_FORMATS
        }


async def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="文档格式转换工具（基于 LibreOffice，支持跨平台自动安装）"
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # check-env 命令
    subparsers.add_parser("check-env", help="检查系统环境")
    
    # install-libreoffice 命令
    install_parser = subparsers.add_parser("install-libreoffice", help="安装 LibreOffice")
    install_parser.add_argument("--force", action="store_true", help="强制重新安装")
    
    # convert 命令
    convert_parser = subparsers.add_parser("convert", help="转换单个文档为 PDF")
    convert_parser.add_argument("--input-file", type=str, required=True, help="输入文件路径")
    convert_parser.add_argument("--output-dir", type=str, help="输出目录")
    convert_parser.add_argument("--remove-source", action="store_true", help="删除源文件")
    
    # batch 命令
    batch_parser = subparsers.add_parser("batch", help="批量转换文档")
    batch_parser.add_argument("--input-files", type=str, nargs="+", required=True, help="输入文件列表")
    batch_parser.add_argument("--output-dir", type=str, help="输出目录")
    batch_parser.add_argument("--remove-source", action="store_true", help="删除源文件")
    
    # convert-dir 命令
    dir_parser = subparsers.add_parser("convert-dir", help="转换目录中的所有文档")
    dir_parser.add_argument("--input-dir", type=str, required=True, help="输入目录")
    dir_parser.add_argument("--output-dir", type=str, help="输出目录")
    dir_parser.add_argument("--recursive", action="store_true", help="递归处理子目录")
    dir_parser.add_argument("--remove-source", action="store_true", help="删除源文件")
    
    # detect 命令
    detect_parser = subparsers.add_parser("detect", help="检测文档格式")
    detect_parser.add_argument("--file-path", type=str, required=True, help="文件路径")
    
    # list-formats 命令
    subparsers.add_parser("list-formats", help="列出所有支持的格式")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "check-env":
        # 检查系统环境
        info = SystemDetector.get_system_info()
        print_result({"success": True, "system_info": info})
    
    elif args.command == "install-libreoffice":
        # 安装 LibreOffice
        installer = LibreOfficeInstaller()
        result = installer.install(force=args.force)
        print_result(result)
    
    elif args.command in ["convert", "batch", "convert-dir", "detect", "list-formats"]:
        # 需要先初始化 DocumentConverter
        try:
            converter = DocumentConverter()
        except RuntimeError as e:
            print_result({"success": False, "error": str(e)})
            sys.exit(1)
        
        if args.command == "convert":
            result = converter.convert_to_pdf(
                args.input_file,
                output_dir=args.output_dir,
                remove_source=args.remove_source
            )
            print_result(result)
        
        elif args.command == "batch":
            result = converter.batch_convert(
                args.input_files,
                output_dir=args.output_dir,
                remove_source=args.remove_source
            )
            print_result(result)
        
        elif args.command == "convert-dir":
            result = converter.convert_directory(
                args.input_dir,
                output_dir=args.output_dir,
                recursive=args.recursive,
                remove_source=args.remove_source
            )
            print_result(result)
        
        elif args.command == "detect":
            result = converter.detect_format(args.file_path)
            print_result(result)
        
        elif args.command == "list-formats":
            result = converter.get_supported_formats()
            print_result(result)


def print_result(result: Dict[str, Any]):
    """打印结果"""
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
