#!/usr/bin/env python3
"""
Web Automation Skill - Python 版依赖安装脚本
自动安装所有依赖包（不指定版本号，避免版本冲突）

用法：
    python scripts/install_dependencies.py
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """执行命令并显示结果"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ {description} 完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败")
        print(f"   错误: {e.stderr}")
        return False


def main():
    print("=" * 60)
    print("Web Automation Skill - 依赖安装（Python 版）")
    print("=" * 60)
    print()

    # 检查 Python 版本
    print("[1/4] 检查 Python 环境...")
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"✅ Python 版本: {python_version}")
    print()

    # 升级 pip
    print("[2/4] 升级 pip...")
    run_command("python -m pip install --upgrade pip -q", "pip 升级")
    print()

    # 安装 Python 依赖
    print("[3/4] 安装 Python 依赖包...")
    packages = [
        "playwright",
        "browser-use",
        "paddlex",  # 统一使用 PaddleX，包含 OCR 和页面解析能力
        "opencv-python",
        "magic-pdf",
        "pillow",
        "pypdf",
        "beautifulsoup4",
        "lxml",
        "pyyaml",
        "langchain",
        "python-docx",
        "numpy",
        "requests",
    ]

    packages_str = " ".join(packages)
    print(f"正在安装：{packages_str}")
    print()

    success = run_command(
        f"python -m pip install {packages_str} -q",
        "Python 依赖包安装"
    )

    if not success:
        print("\n⚠️ 某些包安装失败，请检查错误信息")
        print("   您可以手动安装：")
        for pkg in packages:
            print(f"   pip install {pkg}")
        sys.exit(1)

    print()

    # 安装系统依赖
    print("[4/4] 安装系统依赖...")
    print("正在安装 Playwright 浏览器...")
    run_command("playwright install chromium", "Playwright Chromium")

    print("正在下载 Magic-PDF 模型...")
    # Magic-PDF 可能不需要 download 命令，或者命令不同
    # 尝试运行一次让它自动下载，或者跳过
    try:
        subprocess.run(
            "magic-pdf --help",
            shell=True,
            check=True,
            capture_output=True
        )
        print("✅ Magic-PDF 可用")
    except:
        print("⚠️ Magic-PDF 需要配置（首次使用时会自动下载模型）")
    print()

    # 显示已安装的包
    print("=" * 60)
    print("验证安装结果")
    print("=" * 60)
    print()
    print("已安装的 Python 包：")

    try:
        result = subprocess.run(
            ["python", "-m", "pip", "list"],
            capture_output=True,
            text=True,
            check=True
        )

        target_packages = [
            "playwright",
            "browser-use",
            "paddleocr",
            "paddlepaddle",
            "opencv",
            "magic-pdf",
            "pillow",
            "pypdf",
            "beautifulsoup4",
            "lxml",
            "pyyaml",
            "langchain",
            "python-docx",
            "numpy",
            "requests",
        ]

        for line in result.stdout.split('\n'):
            for target in target_packages:
                if target.lower() in line.lower():
                    print(f"  ✅ {line}")
                    break

    except subprocess.CalledProcessError:
        print("  ⚠️ 无法获取包列表")

    print()
    print("=" * 60)
    print("✅ 安装完成！")
    print("=" * 60)
    print()
    print("注意事项：")
    print("  - LibreOffice 需要单独安装（系统级）")
    print()
    print("  Ubuntu/Debian:")
    print("    sudo apt-get install libreoffice")
    print()
    print("  CentOS/RHEL:")
    print("    sudo yum install libreoffice")
    print()
    print("  macOS:")
    print("    brew install libreoffice")
    print()
    print("  Windows:")
    print("    下载并安装：https://www.libreoffice.org/download/")
    print()


if __name__ == "__main__":
    main()
