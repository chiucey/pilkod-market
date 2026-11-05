#!/usr/bin/env python3
"""快速验证脚本 - 检查依赖和转换功能"""

import subprocess
import sys
from pathlib import Path

def check_dependencies():
    """检查所需依赖"""
    print("检查依赖...")

    required = ['python-docx']
    missing = []

    for lib in required:
        try:
            __import__(lib.replace('-', '_'))
            print(f"  ✓ {lib}")
        except ImportError:
            print(f"  ✗ {lib} (未安装)")
            missing.append(lib)

    # 检查LibreOffice (可选)
    try:
        result = subprocess.run(['libreoffice', '--version'],
                             capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"  ✓ libreoffice")
        else:
            print(f"  ! libreoffice (未完全可用)")
    except FileNotFoundError:
        print(f"  ! libreoffice (未安装，仅支持md<->docx)")
    except Exception:
        print(f"  ! libreoffice (不可用)")

    if missing:
        print(f"\n请安装缺失依赖: pip install {' '.join(missing)}")
        return False

    return True

def check_script():
    """检查脚本是否存在"""
    script_path = Path(__file__).parent / 'convert.py'
    if script_path.exists():
        print(f"✓ convert.py 脚本已就绪")
        return True
    else:
        print(f"✗ convert.py 脚本未找到")
        return False

def main():
    print("=" * 50)
    print("Markdown-Word 转换器 - 依赖检查")
    print("=" * 50)

    deps_ok = check_dependencies()
    script_ok = check_script()

    print("=" * 50)
    if deps_ok and script_ok:
        print("✓ 检查通过！可以正常使用转换功能")
        print("\n用法:")
        print("  python convert.py input.md -o output.docx   # md转docx")
        print("  python convert.py input.docx -o output.md   # docx转md")
        return 0
    else:
        print("✗ 检查未通过，请修复上述问题")
        return 1

if __name__ == '__main__':
    sys.exit(main())
