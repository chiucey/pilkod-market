#!/usr/bin/env python3
"""
Web Automation 环境检测脚本
全面检查所有依赖的安装状态和版本，提供详细的修复建议
"""

import sys
import subprocess
import platform
import os
from pathlib import Path
from typing import Dict, List, Any


def run_command(cmd: str, capture_output: bool = True, timeout: int = 10) -> Dict[str, Any]:
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=capture_output,
            text=True,
            timeout=timeout
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip() if result.stdout else "",
            "stderr": result.stderr.strip() if result.stderr else "",
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "命令超时"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def check_python() -> Dict[str, Any]:
    """检查 Python 版本"""
    result = {
        "name": "Python",
        "required": ">= 3.8",
        "installed": None,
        "status": "error",
        "category": "core",
        "fix": None
    }
    
    try:
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        result["installed"] = version_str
        
        if version.major == 3 and version.minor >= 8:
            result["status"] = "ok"
        else:
            result["status"] = "error"
            result["message"] = "版本过低，需要 3.8+"
            result["fix"] = "请升级 Python 到 3.8 或更高版本"
    except Exception as e:
        result["error"] = str(e)
        result["fix"] = "请安装 Python 3.8+"
    
    return result


def check_package(package_name: str, min_version: str = None, category: str = "optional") -> Dict[str, Any]:
    """检查 Python 包"""
    result = {
        "name": package_name,
        "required": f">= {min_version}" if min_version else "any",
        "installed": None,
        "status": "error",
        "category": category,
        "fix": None
    }
    
    try:
        output = run_command(f"{sys.executable} -m pip show {package_name}")
        
        if output["success"] and output["stdout"]:
            for line in output["stdout"].split('\n'):
                if line.startswith("Version:"):
                    version = line.split(":", 1)[1].strip()
                    result["installed"] = version
                    result["status"] = "ok"
                    
                    if min_version:
                        try:
                            from packaging import version as pkg_version
                            if pkg_version.parse(version) < pkg_version.parse(min_version):
                                result["status"] = "warn"
                                result["message"] = f"版本过低，建议升级到 {min_version}+"
                                result["fix"] = f"pip install --upgrade {package_name}"
                        except ImportError:
                            pass
                    break
        else:
            result["status"] = "missing"
            result["message"] = "未安装"
            result["fix"] = f"pip install {package_name}"
            
    except Exception as e:
        result["error"] = str(e)
        result["fix"] = f"pip install {package_name}"
    
    return result


def check_playwright_browsers() -> Dict[str, Any]:
    """检查 Playwright 浏览器"""
    result = {
        "name": "Playwright Browsers",
        "required": "Chromium",
        "installed": None,
        "status": "error",
        "category": "core",
        "fix": None
    }
    
    try:
        # 检查浏览器是否已安装
        output = run_command(f"{sys.executable} -m playwright install --dry-run chromium 2>&1")
        
        if "already installed" in output.get("stdout", "").lower():
            result["installed"] = "Chromium"
            result["status"] = "ok"
        else:
            result["status"] = "missing"
            result["message"] = "未安装"
            result["fix"] = "playwright install chromium"
            
    except Exception as e:
        result["status"] = "missing"
        result["message"] = "检测失败"
        result["fix"] = "playwright install chromium"
    
    return result


def check_module_import(module_name: str, package_name: str = None) -> Dict[str, Any]:
    """检查模块是否可以导入"""
    result = {
        "name": module_name,
        "installed": None,
        "status": "error",
        "category": "optional",
        "fix": None
    }
    
    try:
        __import__(module_name)
        result["installed"] = "可导入"
        result["status"] = "ok"
    except ImportError:
        result["status"] = "missing"
        result["message"] = "无法导入"
        result["fix"] = f"pip install {package_name or module_name}"
    
    return result


def get_system_info() -> Dict[str, Any]:
    """获取系统信息"""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python_executable": sys.executable,
        "python_version": sys.version.split()[0],
        "working_directory": os.getcwd()
    }


def print_header(title: str):
    """打印标题"""
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_check_result(check: Dict[str, Any], verbose: bool = False):
    """打印检查结果"""
    status_icons = {
        "ok": "✓",
        "warn": "!",
        "missing": "✗",
        "error": "✗"
    }
    
    icon = status_icons.get(check["status"], "?")
    name = check["name"]
    required = check.get("required", "")
    installed = check.get("installed", "")
    
    # 状态颜色
    if check["status"] == "ok":
        status_str = f"\033[92m{icon} OK\033[0m"
    elif check["status"] == "warn":
        status_str = f"\033[93m{icon} WARN\033[0m"
    else:
        status_str = f"\033[91m{icon} MISSING\033[0m"
    
    print(f"  {status_str} {name:<25} {required:<15} {installed}")
    
    if verbose:
        if check.get("message"):
            print(f"      └─ {check['message']}")
        if check.get("fix"):
            print(f"      └─ 修复: {check['fix']}")


def main():
    """主函数"""
    # 获取系统信息
    system_info = get_system_info()
    
    print_header("Web Automation 环境检测")
    
    print()
    print(f"  操作系统: {system_info['system']} {system_info['release']}")
    print(f"  架构: {system_info['machine']}")
    print(f"  Python: {system_info['python_version']}")
    print(f"  Python 路径: {system_info['python_executable']}")
    print(f"  工作目录: {system_info['working_directory']}")
    
    # 收集所有检查结果
    all_checks: List[Dict[str, Any]] = []
    
    # 核心依赖
    print_header("核心依赖（必需）")
    core_checks = [
        check_python(),
        check_package("playwright", "1.48.0", "core"),
        check_package("browser-use", None, "core"),
        check_package("langchain", "0.1.0", "core"),
        check_package("requests", "2.28.0", "core"),
        check_package("aiohttp", "3.8.0", "core"),
        check_playwright_browsers(),
    ]
    
    for check in core_checks:
        check["category"] = "core"
        print_check_result(check, verbose=True)
        all_checks.append(check)
    
    # 数据处理依赖
    print_header("数据处理依赖（必需）")
    data_checks = [
        check_package("beautifulsoup4", "4.12.0", "core"),
        check_package("lxml", "4.9.0", "core"),
        check_package("pyyaml", "6.0", "core"),
        check_package("numpy", "1.24.0", "core"),
    ]
    
    for check in data_checks:
        check["category"] = "core"
        print_check_result(check, verbose=False)
        all_checks.append(check)
    
    # LLM 集成依赖
    print_header("LLM 集成依赖（可选）")
    llm_checks = [
        check_package("langchain-openai", None, "llm"),
        check_package("langchain-anthropic", None, "llm"),
        check_package("langchain-google-genai", None, "llm"),
    ]
    
    for check in llm_checks:
        print_check_result(check, verbose=False)
        all_checks.append(check)
    
    # OCR 依赖
    print_header("OCR 依赖（可选）")
    ocr_checks = [
        check_module_import("paddleocr", "paddleocr"),
        check_module_import("paddle", "paddlepaddle"),
        check_module_import("cv2", "opencv-python"),
        check_package("pillow", None, "ocr"),
    ]
    
    for check in ocr_checks:
        check["category"] = "ocr"
        print_check_result(check, verbose=False)
        all_checks.append(check)
    
    # PDF 依赖
    print_header("PDF 依赖（可选）")
    pdf_checks = [
        check_module_import("magic_pdf", "magic-pdf[full]"),
        check_package("pypdf", None, "pdf"),
        check_package("python-docx", None, "pdf"),
    ]
    
    for check in pdf_checks:
        check["category"] = "pdf"
        print_check_result(check, verbose=False)
        all_checks.append(check)
    
    # 统计结果
    print_header("检测结果统计")
    
    core_ok = sum(1 for c in all_checks if c["category"] == "core" and c["status"] == "ok")
    core_total = sum(1 for c in all_checks if c["category"] == "core")
    
    optional_ok = sum(1 for c in all_checks if c["category"] in ["llm", "ocr", "pdf"] and c["status"] == "ok")
    optional_total = sum(1 for c in all_checks if c["category"] in ["llm", "ocr", "pdf"])
    
    missing = sum(1 for c in all_checks if c["status"] in ["missing", "error"])
    
    print()
    print(f"  核心依赖: {core_ok}/{core_total} OK")
    print(f"  可选依赖: {optional_ok}/{optional_total} OK")
    print(f"  缺失项: {missing}")
    
    # 给出建议
    print_header("修复建议")
    print()
    
    if core_ok < core_total:
        print("  ⚠️  核心依赖缺失，请运行安装脚本：")
        print("     Linux/macOS: ./install.sh")
        print("     Windows: install.bat")
        print()
        
        # 显示缺失的核心依赖
        missing_core = [c for c in all_checks if c["category"] == "core" and c["status"] != "ok"]
        if missing_core:
            print("  缺失的核心依赖：")
            for check in missing_core:
                if check.get("fix"):
                    print(f"     - {check['name']}: {check['fix']}")
            print()
    
    # 显示缺失的可选依赖
    missing_optional = [c for c in all_checks if c["category"] in ["llm", "ocr", "pdf"] and c["status"] != "ok"]
    if missing_optional:
        print("  📝 可选依赖（根据需要安装）：")
        print()
        
        ocr_missing = [c for c in missing_optional if c["category"] == "ocr"]
        if ocr_missing:
            print("     OCR 功能：")
            print("     pip install paddleocr paddlepaddle opencv-python pillow")
            print()
        
        pdf_missing = [c for c in missing_optional if c["category"] == "pdf"]
        if pdf_missing:
            print("     PDF 功能：")
            print("     pip install magic-pdf[full] pypdf python-docx")
            print()
        
        llm_missing = [c for c in missing_optional if c["category"] == "llm"]
        if llm_missing:
            print("     LLM 集成：")
            print("     pip install langchain-openai langchain-anthropic langchain-google-genai")
            print()
    
    if core_ok == core_total and missing == 0:
        print("  ✅ 所有依赖已正确安装！")
        print()
        print("  您可以开始使用 Web Automation Skill 了。")
        print()
    
    return 0 if core_ok == core_total else 1


if __name__ == "__main__":
    sys.exit(main())
