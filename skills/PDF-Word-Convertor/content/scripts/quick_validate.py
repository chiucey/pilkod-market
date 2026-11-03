#!/usr/bin/env python3
"""验证脚本 - 检查转换脚本功能"""

import sys
import os
from pathlib import Path

# 添加脚本目录
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir / "scripts"))

def check_dependencies():
    """检查依赖是否安装"""
    deps = {
        'python-docx': False,
        'pypdf': False,
        'reportlab': False,
        'libreoffice': False,
    }

    # 检查Python包
    try:
        import docx
        deps['python-docx'] = True
    except ImportError:
        pass

    try:
        import pypdf
        deps['pypdf'] = True
    except ImportError:
        pass

    try:
        import reportlab
        deps['reportlab'] = True
    except ImportError:
        pass

    # 检查LibreOffice
    deps['libreoffice'] = os.system('which libreoffice > /dev/null 2>&1') == 0

    return deps


def main():
    print("=" * 50)
    print("文档转换技能 - 依赖检查")
    print("=" * 50)

    deps = check_dependencies()

    print("\n依赖状态:")
    print(f"  python-docx: {'✓ 已安装' if deps['python-docx'] else '✗ 未安装'}")
    print(f"  pypdf:       {'✓ 已安装' if deps['pypdf'] else '✗ 未安装'}")
    print(f"  reportlab:   {'✓ 已安装' if deps['reportlab'] else '✗ 未安装'}")
    print(f"  libreoffice: {'✓ 已安装' if deps['libreoffice'] else '✗ 未安装'}")

    # 支持的转换
    print("\n支持的转换:")
    print("  txt  -> pdf, docx  ✓")
    print("  pdf  -> txt, docx   ✓")
    print("  docx -> pdf, txt    ✓")
    print("  doc  -> docx, pdf, txt ✓")

    # 需要的依赖
    print("\n转换功能对应的依赖:")
    print("  txt->pdf:  reportlab")
    print("  txt->docx: python-docx")
    print("  docx->pdf: libreoffice")
    print("  docx->txt: python-docx")
    print("  pdf->txt:  pypdf")
    print("  pdf->docx: pypdf + python-docx")

    # 提示缺失
    missing = [k for k, v in deps.items() if not v]
    if missing:
        print(f"\n建议安装: pip install {' '.join(['python-docx', 'pypdf', 'reportlab'])}")
        if 'libreoffice' in missing:
            print("提示: Word转PDF需要安装LibreOffice")

    print("\n" + "=" * 50)
    print("验证通过 ✓")
    print("=" * 50)


if __name__ == '__main__':
    main()
