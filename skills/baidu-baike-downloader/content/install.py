#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度百科下载器 - 安装脚本
"""

import subprocess
import sys


def install_dependencies():
    """安装所需依赖"""
    packages = ['requests', 'beautifulsoup4', 'lxml']

    print("正在安装依赖包...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '-q'])
            print(f"✓ {package} 安装成功")
        except subprocess.CalledProcessError:
            print(f"✗ {package} 安装失败")


if __name__ == '__main__':
    install_dependencies()
    print("\n依赖安装完成！现在可以使用 baidu_baike_downloader.py")
