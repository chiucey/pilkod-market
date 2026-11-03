#!/usr/bin/env python3
"""
TM聊天自动回复系统安装脚本
自动安装依赖并配置环境
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def print_step(msg):
    """打印步骤信息"""
    print(f"\n{'='*50}")
    print(f"  {msg}")
    print(f"{'='*50}\n")


def check_python():
    """检查Python版本"""
    print_step("检查Python环境")
    version = sys.version_info
    print(f"当前Python版本: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("⚠️  建议使用Python 3.8+")
        return False
    return True


def install_dependencies():
    """安装依赖"""
    print_step("安装Python依赖")

    dependencies = [
        'pywin32>=305',    # Windows API
    ]

    for dep in dependencies:
        print(f"安装 {dep}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep, '-q'])
        except subprocess.CalledProcessError as e:
            print(f"⚠️  安装 {dep} 失败: {e}")


def create_directories():
    """创建目录结构"""
    print_step("创建目录结构")

    dirs = [
        'logs',
        'data',
        'config',
    ]

    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"  ✓ 创建目录: {d}")


def copy_config():
    """复制配置文件"""
    print_step("配置系统")

    config_src = 'config/config.json.example'
    config_dst = 'config/config.json'

    if not os.path.exists(config_dst) and os.path.exists(config_src):
        shutil.copy(config_src, config_dst)
        print(f"  ✓ 配置文件已创建: {config_dst}")
    else:
        print(f"  ℹ  配置文件已存在，跳过")


def check_tm_installed():
    """检查TM是否安装"""
    print_step("检测TradeManager")

    possible_paths = [
        r"C:\Program Files\TradeManager",
        r"C:\Program Files (x86)\TradeManager",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            print(f"  ✓ 检测到TM: {path}")
            return path

    print("  ⚠️  未检测到TM安装，请手动确认安装路径")
    return None


def create_batch_files():
    """创建快捷启动批处理文件"""
    print_step("创建快捷方式")

    # 监控模式
    monitor_batch = """@echo off
cd /d "%~dp0"
python scripts/tm_monitor.py --mode monitor
pause
"""

    # 自动回复模式
    auto_batch = """@echo off
cd /d "%~dp0"
python scripts/tm_monitor.py --mode auto
pause
"""

    with open('start_monitor.bat', 'w', encoding='utf-8') as f:
        f.write(monitor_batch)

    with open('start_auto_reply.bat', 'w', encoding='utf-8') as f:
        f.write(auto_batch)

    print("  ✓ 创建启动脚本完成")


def print_usage():
    """打印使用说明"""
    print_step("使用说明")

    print("""
启动方式:
  1. 双击运行 start_monitor.bat - 仅监控模式
  2. 双击运行 start_auto_reply.bat - 自动回复模式
  3. 命令行: python scripts/tm_monitor.py --mode auto

配置文件:
  编辑 config/config.json 修改回复模板和关键词

注意事项:
  1. 首次使用请确保TM已登录
  2. 建议先用监控模式测试
  3. 开启审核模式可避免错误回复
""")


def main():
    """主函数"""
    print("\n" + "="*50)
    print("  TM聊天自动回复系统 - 安装向导")
    print("="*50)

    # 检查Python
    if not check_python():
        print("Python版本不符合要求")
        return 1

    # 安装依赖
    install_dependencies()

    # 创建目录
    create_directories()

    # 复制配置
    copy_config()

    # 检查TM
    tm_path = check_tm_installed()

    # 创建快捷方式
    create_batch_files()

    # 打印使用说明
    print_usage()

    print_step("安装完成!")

    return 0


if __name__ == '__main__':
    sys.exit(main())