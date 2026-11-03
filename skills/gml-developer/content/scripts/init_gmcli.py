#!/usr/bin/env python3
"""
gm_cli初始化脚本
首次使用时自动安装并配置gm_cli工具
"""

import subprocess
import sys
import os
import json

def check_node_npm():
    """检查Node.js和npm是否已安装"""
    try:
        node_result = subprocess.run(['node', '--version'],
                                      capture_output=True, text=True)
        npm_result = subprocess.run(['npm', '--version'],
                                    capture_output=True, text=True)
        if node_result.returncode == 0 and npm_result.returncode == 0:
            print(f"✓ Node.js v{node_result.stdout.strip()}, npm v{npm_result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    print("✗ Node.js或npm未安装")
    return False

def install_gmcli():
    """安装gm_cli工具"""
    print("正在安装 @gamemaker/gm-cli...")
    try:
        result = subprocess.run(['npm', 'install', '-g', '@gamemaker/gm-cli'],
                                capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ gm_cli安装成功")
            return True
        else:
            print(f"✗ 安装失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ 安装异常: {e}")
        return False

def verify_installation():
    """验证gm_cli安装"""
    try:
        result = subprocess.run(['gm-cli', '--version'],
                                capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ gm_cli验证成功: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    print("✗ gm_cli验证失败")
    return False

def main():
    """主函数：确保gm_cli可用"""
    print("=== gm_cli初始化 ===")

    if not check_node_npm():
        print("\n请先安装Node.js: https://nodejs.org/")
        sys.exit(1)

    # 检查是否已安装
    try:
        subprocess.run(['gm-cli', '--version'],
                      capture_output=True, check=True)
        print("✓ gm_cli已安装")
    except (subprocess.CalledProcessError, FileNotFoundError):
        if not install_gmcli():
            sys.exit(1)
        verify_installation()

    print("\n=== 初始化完成 ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())