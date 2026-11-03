#!/usr/bin/env python3
"""
PPT备注批量导入脚本

功能：将文本备注文件批量导入到PowerPoint演示文稿中

使用方法：
    python import_notes.py <pptx文件> <备注文件夹> [--output <输出文件夹>]

示例：
    python import_notes.py presentation.pptx notes/ --output output/
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
except ImportError:
    print("错误：需要安装 python-pptx 库")
    print("请运行：pip install python-pptx")
    sys.exit(1)


def natural_sort_key(filename: str) -> Tuple:
    """自然排序键函数，按文件名中的数字排序"""
    return tuple(int(x) if x.isdigit() else x for x in re.findall(r'(\d+|\D+)', filename))


def extract_slide_number(filename: str) -> Optional[int]:
    """从文件名中提取幻灯片序号"""
    # 匹配文件名开头的数字
    match = re.match(r'^(\d+)', filename)
    if match:
        return int(match.group(1))
    return None


def read_note_content(file_path: Path) -> str:
    """读取备注文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except UnicodeDecodeError:
        # 尝试使用其他编码
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                return f.read().strip()
        except Exception as e:
            print(f"警告：无法读取文件 {file_path}: {e}")
            return ""


def get_notes_files(notes_dir: Path) -> List[Tuple[int, Path]]:
    """获取所有备注文件并按序号排序"""
    valid_extensions = ['.txt', '.md', '.rtf']
    notes_files = []

    if not notes_dir.exists():
        print(f"错误：备注文件夹不存在: {notes_dir}")
        return []

    for file_path in notes_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in valid_extensions:
            slide_num = extract_slide_number(file_path.name)
            if slide_num is not None:
                notes_files.append((slide_num, file_path))

    # 按序号排序
    notes_files.sort(key=lambda x: x[0])
    return notes_files


def import_notes_to_pptx(pptx_path: Path, notes_dir: Path, output_dir: Optional[Path] = None) -> Dict:
    """
    将备注导入到PowerPoint

    返回：{
        'success': bool,
        'total_slides': int,
        'notes_imported': int,
        'output_path': Path,
        'errors': List[str]
    }
    """
    result = {
        'success': False,
        'total_slides': 0,
        'notes_imported': 0,
        'output_path': None,
        'errors': []
    }

    # 检查PPTX文件
    if not pptx_path.exists():
        result['errors'].append(f"PPTX文件不存在: {pptx_path}")
        return result

    if not pptx_path.suffix.lower() in ['.pptx', '.ppt']:
        result['errors'].append(f"不支持的文件格式: {pptx_path.suffix}，仅支持.pptx和.ppt")
        return result

    # 获取备注文件
    notes_files = get_notes_files(notes_dir)
    if not notes_files:
        result['errors'].append("未找到有效的备注文件（请确保文件名以数字开头，如01.txt, 02.txt）")
        return result

    try:
        # 打开演示文稿
        prs = Presentation(str(pptx_path))
        result['total_slides'] = len(prs.slides)

        # 创建序号到备注内容的映射
        notes_map: Dict[int, str] = {}
        for slide_num, file_path in notes_files:
            content = read_note_content(file_path)
            if content:
                notes_map[slide_num] = content

        # 导入备注
        imported_count = 0
        for idx, slide in enumerate(prs.slides, start=1):
            # 获取或创建备注
            notes_slide = slide.notes_slide

            if idx in notes_map:
                # 设置备注文本
                text_frame = notes_slide.notes_text_frame
                text_frame.text = notes_map[idx]
                imported_count += 1
                print(f"✓ 已导入备注到第 {idx} 张幻灯片")
            else:
                print(f"○ 第 {idx} 张幻灯片无对应备注")

        result['notes_imported'] = imported_count

        # 保存文件
        if output_dir is None:
            output_dir = pptx_path.parent

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_filename = pptx_path.stem + '_with_notes.pptx'
        output_path = output_dir / output_filename

        prs.save(str(output_path))
        result['output_path'] = output_path
        result['success'] = True

    except Exception as e:
        result['errors'].append(f"处理时出错: {str(e)}")

    return result


def main():
    parser = argparse.ArgumentParser(
        description='批量将备注文件导入到PowerPoint演示文稿',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
    python import_notes.py presentation.pptx notes/
    python import_notes.py presentation.pptx notes/ --output output/

备注文件格式：
    文件名格式：[序号]_[可选描述].扩展名
    例如：01.txt, 02_intro.txt, 03_notes.txt

详细内容请查看：references/format_guide.md
        """
    )

    parser.add_argument('pptx_file', type=Path, help='PowerPoint文件路径(.pptx或.ppt)')
    parser.add_argument('notes_dir', type=Path, help='备注文件夹路径')
    parser.add_argument('--output', '-o', type=Path, default=None,
                        help='输出文件夹路径（默认为原文件所在目录）')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='显示详细输出')

    args = parser.parse_args()

    print("=" * 50)
    print("PPT备注批量导入工具")
    print("=" * 50)
    print()

    # 执行导入
    result = import_notes_to_pptx(args.pptx_file, args.notes_dir, args.output)

    print()
    print("-" * 50)
    print("导入结果：")
    print(f"  总幻灯片数：{result['total_slides']}")
    print(f"  备注导入数：{result['notes_imported']}")

    if result['success']:
        print(f"  输出文件：{result['output_path']}")
        print()
        print("✓ 导入完成！")
    else:
        print()
        print("✗ 导入失败：")
        for error in result['errors']:
            print(f"  - {error}")
        sys.exit(1)

    print("-" * 50)


if __name__ == '__main__':
    main()
