#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试脚本 - 验证环境和依赖
"""

import sys
import subprocess

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("  [警告] Python版本过低，建议3.8+")
        return False
    print("  [OK] Python版本符合要求")
    return True

def check_module(module_name):
    """检查模块是否安装"""
    try:
        __import__(module_name)
        print(f"  [OK] {module_name}")
        return True
    except ImportError:
        print(f"  [缺失] {module_name}")
        return False

def check_nodejs():
    """检查Node.js"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        print(f"Node.js版本: {result.stdout.strip()}")
        print("  [OK] Node.js")
        return True
    except:
        print("  [缺失] Node.js")
        return False

def check_npm_package(package_name):
    """检查npm包"""
    try:
        result = subprocess.run(['npm', 'list', '-g', package_name], capture_output=True, text=True)
        if package_name in result.stdout:
            print(f"  [OK] {package_name}")
            return True
        print(f"  [缺失] {package_name}")
        return False
    except:
        print(f"  [缺失] {package_name}")
        return False

def check_browser():
    """检查浏览器"""
    browsers = []
    
    # 检查Edge
    try:
        from selenium import webdriver
        from selenium.webdriver.edge.options import Options
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Edge(options=options)
        driver.quit()
        print("  [OK] Edge浏览器")
        browsers.append('edge')
    except:
        print("  [缺失] Edge浏览器")
    
    # 检查Chrome
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.quit()
        print("  [OK] Chrome浏览器")
        browsers.append('chrome')
    except:
        print("  [缺失] Chrome浏览器")
    
    return len(browsers) > 0

def main():
    print("=" * 60)
    print("环境检测")
    print("=" * 60)
    
    print("\n[Python环境]")
    check_python_version()
    
    print("\n[Python模块]")
    modules = ['selenium', 'requests', 'PIL']
    missing = []
    for m in modules:
        if not check_module(m):
            missing.append(m)
    
    print("\n[Node.js环境]")
    check_nodejs()
    check_npm_package('docx')
    
    print("\n[浏览器]")
    check_browser()
    
    print("\n[OCR工具]（可选）")
    ocr_available = []
    if check_module('easyocr'):
        ocr_available.append('easyocr')
    if check_module('paddleocr'):
        ocr_available.append('paddleocr')
    try:
        import pytesseract
        print("  [OK] pytesseract")
        ocr_available.append('pytesseract')
    except:
        print("  [缺失] pytesseract")
    
    print("\n" + "=" * 60)
    print("检测结果")
    print("=" * 60)
    
    if missing:
        print(f"\n[警告] 缺少Python模块: {', '.join(missing)}")
        print("安装命令: pip install " + ' '.join(missing))
    
    if ocr_available:
        print(f"\n[OK] OCR工具可用: {', '.join(ocr_available)}")
    else:
        print("\n[提示] 未安装OCR工具，图片文字识别功能不可用")
        print("安装命令: pip install easyocr")
    
    print("\n环境检测完成！")

if __name__ == '__main__':
    main()
