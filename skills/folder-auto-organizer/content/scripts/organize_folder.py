#!/usr/bin/env python3
"""
文件夹自动整理工具 - 主脚本
自动分析、分类、整理文件夹中的文件，并在每级目录生成内容总结
"""

import os
import sys
import shutil
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from utils import (
    get_file_type,
    extract_topic,
    format_file_size,
    calculate_folder_size,
    is_sensitive_file,
    scan_directory_structure,
    generate_summary_content,
    generate_root_summary,
    sanitize_filename,
    get_unique_path,
    FILE_TYPE_MAP,
)


class FolderOrganizer:
    """文件夹整理器类"""

    def __init__(self, target_path: str, options: Dict = None):
        self.target_path = os.path.abspath(target_path)
        self.options = options or {}
        self.dry_run = self.options.get('dry_run', True)
        self.deep_analysis = self.options.get('deep_analysis', False)
        self.by_topic = self.options.get('by_topic', False)
        self.by_date = self.options.get('by_date', False)
        self.move_history = []  # 记录移动操作，用于回滚
        self.created_folders = []

    def run(self):
        """执行整理流程"""
        print(f"\n{'='*60}")
        print(f"文件夹自动整理工具")
        print(f"{'='*60}")
        print(f"目标路径: {self.target_path}")
        print(f"模式: {'预览模式' if self.dry_run else '执行模式'}")
        print(f"{'='*60}\n")

        # 阶段 1: 扫描目录
        print("[1/5] 扫描目录结构...")
        files = self._scan_files()
        print(f"      发现 {len(files)} 个文件\n")

        if not files:
            print("未发现任何文件，退出。")
            return

        # 阶段 2: 分析和分类
        print("[2/5] 分析文件类型...")
        classified_files = self._classify_files(files)
        print(f"      完成分类统计\n")

        # 阶段 3: 生成整理计划
        print("[3/5] 生成整理计划...")
        plan = self._create_plan(classified_files)
        self._print_plan(plan)
        print()

        # 阶段 4: 预览/执行
        if self.dry_run:
            print("[4/5] 预览模式 - 按回车键开始执行整理，或 Ctrl+C 取消...")
            try:
                input()
                self.dry_run = False
                print("开始执行整理...\n")
            except KeyboardInterrupt:
                print("\n\n已取消整理。")
                return
        else:
            print("[4/5] 执行整理...")

        self._execute_plan(plan)

        # 阶段 5: 生成总结文档
        print("\n[5/5] 生成目录总结文档...")
        self._generate_summaries()

        # 输出结果
        self._print_report()

    def _scan_files(self) -> List[Dict]:
        """扫描目标文件夹中的所有文件"""
        files = []

        for root, dirs, filenames in os.walk(self.target_path):
            # 跳过隐藏目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for filename in filenames:
                if filename.startswith('.'):
                    continue

                filepath = os.path.join(root, filename)

                # 检查是否为敏感文件
                if is_sensitive_file(filepath):
                    print(f"      ⚠️  跳过敏感文件: {filename}")
                    continue

                try:
                    stat = os.stat(filepath)
                    files.append({
                        'original_path': filepath,
                        'filename': filename,
                        'size': stat.st_size,
                        'modified': stat.st_mtime,
                        'modified_str': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                    })
                except (OSError, FileNotFoundError):
                    continue

        return files

    def _classify_files(self, files: List[Dict]) -> Dict[str, List[Dict]]:
        """根据文件类型和主题进行分类"""
        classified = {}

        for file in files:
            file_type, type_desc = get_file_type(file['original_path'])
            category_folder = file_type

            # 如果启用了主题分类，尝试进一步细分
            if self.by_topic:
                topic = extract_topic(file['original_path'])
                if topic:
                    category_folder = topic

            # 如果启用了日期分类，按年份组织
            if self.by_date:
                year = datetime.fromtimestamp(file['modified']).strftime('%Y')
                category_folder = f"{year}/{category_folder}"

            if category_folder not in classified:
                classified[category_folder] = []

            file['type_category'] = category_folder
            file['type_desc'] = type_desc
            classified[category_folder].append(file)

        return classified

    def _create_plan(self, classified_files: Dict[str, List[Dict]]) -> List[Dict]:
        """创建文件整理计划"""
        plan = []

        for category, files in classified_files.items():
            target_folder = os.path.join(self.target_path, category)

            for file in files:
                # 生成目标路径
                target_path = os.path.join(target_folder, file['filename'])

                # 如果文件名冲突，生成唯一的文件名
                if not self.dry_run and os.path.exists(target_path):
                    base, ext = os.path.splitext(file['filename'])
                    target_path = get_unique_path(target_path)

                plan.append({
                    'source': file['original_path'],
                    'target': target_path,
                    'category': category,
                    'filename': file['filename'],
                    'size': file['size'],
                    'type_desc': file['type_desc'],
                    'modified': file['modified_str'],
                })

        return plan

    def _print_plan(self, plan: List[Dict]):
        """打印整理计划"""
        # 按类别分组显示
        categories = {}
        for item in plan:
            cat = item['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(item)

        for category, items in sorted(categories.items()):
            print(f"      📁 {category}/ ({len(items)} 个文件)")
            for item in items[:5]:  # 只显示前5个
                print(f"         └── {item['filename']}")
            if len(items) > 5:
                print(f"         └── ... 还有 {len(items) - 5} 个文件")
        print()

    def _execute_plan(self, plan: List[Dict]):
        """执行整理计划"""
        # 按类别创建目标文件夹
        categories = set(item['category'] for item in plan)
        for category in categories:
            target_folder = os.path.join(self.target_path, category)
            if not os.path.exists(target_folder):
                if not self.dry_run:
                    os.makedirs(target_folder, exist_ok=True)
                    self.created_folders.append(target_folder)
                print(f"      📁 创建文件夹: {category}/")

        # 移动文件
        for item in plan:
            if self.dry_run:
                print(f"      📄 移动: {item['filename']} → {item['category']}/")
            else:
                target_dir = os.path.dirname(item['target'])
                os.makedirs(target_dir, exist_ok=True)

                try:
                    shutil.move(item['source'], item['target'])
                    self.move_history.append({
                        'source': item['source'],
                        'target': item['target'],
                    })
                    print(f"      ✓ 移动: {item['filename']} → {item['category']}/")
                except Exception as e:
                    print(f"      ✗ 失败: {item['filename']} - {str(e)}")

    def _generate_summaries(self):
        """生成各层级的总结文档"""
        # 扫描整理后的结构
        structure = scan_directory_structure(self.target_path)

        # 生成子文件夹总结
        for child in structure.get('children', []):
            if child['name'].startswith('00_'):
                continue  # 跳过已有的总结文件

            summary_path = os.path.join(
                self.target_path,
                child['name'],
                f"00_{child['name']}_目录总结.md"
            )

            content = generate_summary_content(child['path'], child)

            if not self.dry_run:
                with open(summary_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"      ✓ 生成: {summary_path}")

        # 生成根目录总报告
        root_summary = os.path.join(self.target_path, "00_总目录总结.md")
        content = generate_root_summary(self.target_path, structure.get('children', []))

        if not self.dry_run:
            with open(root_summary, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"      ✓ 生成: {root_summary}")

    def _print_report(self):
        """打印整理报告"""
        print(f"\n{'='*60}")
        print(f"整理 {'预览' if self.dry_run else '完成'}")
        print(f"{'='*60}")

        if self.dry_run:
            print("以上是整理预览，如需执行请重新运行并使用 --execute 参数")
        else:
            print(f"✓ 已整理 {len(self.move_history)} 个文件")
            print(f"✓ 已创建 {len(self.created_folders)} 个文件夹")
            print(f"✓ 已生成总结文档")

        print(f"{'='*60}\n")

    def rollback(self):
        """回滚操作 - 将文件移回原位置"""
        if not self.move_history:
            print("没有可回滚的操作。")
            return

        print("开始回滚操作...")
        for item in reversed(self.move_history):
            try:
                shutil.move(item['target'], item['source'])
                print(f"  ✓ 回滚: {Path(item['target']).name}")
            except Exception as e:
                print(f"  ✗ 回滚失败: {item['target']} - {str(e)}")

        # 删除创建的文件夹
        for folder in reversed(self.created_folders):
            try:
                if os.path.isdir(folder) and not os.listdir(folder):
                    os.rmdir(folder)
                    print(f"  ✓ 删除空文件夹: {folder}")
            except Exception:
                pass

        self.move_history = []
        self.created_folders = []


def main():
    parser = argparse.ArgumentParser(
        description='文件夹自动整理工具 - 根据文件类型自动分类整理文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s /path/to/folder              # 预览模式
  %(prog)s /path/to/folder --execute    # 执行模式
  %(prog)s /path/to/folder -t           # 按主题进一步分类
  %(prog)s /path/to/folder --rollback   # 回滚上次操作
        """
    )

    parser.add_argument('path', nargs='?', help='要整理的文件夹路径')
    parser.add_argument('-e', '--execute', action='store_true',
                        help='执行整理操作（默认只预览）')
    parser.add_argument('-t', '--topic', action='store_true',
                        help='启用主题深度分类')
    parser.add_argument('-d', '--date', action='store_true',
                        help='按日期（年份）组织文件')
    parser.add_argument('-r', '--rollback', action='store_true',
                        help='回滚上次的整理操作')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='静默模式，不显示详细信息')

    args = parser.parse_args()

    # 回滚模式
    if args.rollback:
        # 需要从某处加载上次的操作历史
        print("回滚功能需要指定目标路径和历史文件")
        return

    # 检查路径
    if not args.path:
        parser.print_help()
        return

    if not os.path.isdir(args.path):
        print(f"错误: 路径不存在或不是文件夹: {args.path}")
        return

    # 创建整理器并运行
    options = {
        'dry_run': not args.execute,
        'by_topic': args.topic,
        'by_date': args.date,
        'quiet': args.quiet,
    }

    organizer = FolderOrganizer(args.path, options)
    organizer.run()


if __name__ == '__main__':
    main()
