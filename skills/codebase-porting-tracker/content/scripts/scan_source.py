#!/usr/bin/env python3
"""
Codebase Source Scanner
自动扫描代码库结构并生成模块统计信息
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class ModuleInfo:
    """模块信息"""
    name: str
    path: str
    file_count: int
    total_lines: int
    extensions: dict[str, int]
    submodules: list[str]


@dataclass
class ScanResult:
    """扫描结果"""
    root: str
    scan_time: str
    total_files: int
    total_lines: int
    modules: list[ModuleInfo]
    extensions: dict[str, int]


def count_lines(file_path: Path) -> int:
    """计算文件行数"""
    try:
        return len(file_path.read_text(encoding='utf-8', errors='ignore').splitlines())
    except Exception:
        return 0


def scan_codebase(
    root: Path,
    extensions: Optional[list[str]] = None,
    exclude_dirs: Optional[list[str]] = None
) -> ScanResult:
    """
    扫描代码库

    Args:
        root: 代码库根目录
        extensions: 要扫描的文件扩展名列表，如 ['.py', '.ts']
        exclude_dirs: 要排除的目录名列表

    Returns:
        ScanResult: 扫描结果
    """
    if extensions is None:
        extensions = ['.py', '.ts', '.tsx', '.js', '.jsx', '.java', '.go', '.rs', '.cpp', '.vue', '.svelte']

    if exclude_dirs is None:
        exclude_dirs = [
            'node_modules', '__pycache__', '.git', '.venv', 'venv',
            'dist', 'build', '.idea', '.vscode', 'coverage', '.pytest_cache'
        ]

    files: list[tuple[Path, int]] = []  # (file_path, lines)
    modules_dict: dict[str, dict] = defaultdict(lambda: {
        'files': 0,
        'lines': 0,
        'extensions': Counter(),
        'submodules': set()
    })

    # 扫描文件
    for ext in extensions:
        for file_path in root.rglob(f'*{ext}'):
            # 检查是否在排除目录中
            if any(excl in file_path.parts for excl in exclude_dirs):
                continue

            rel_path = file_path.relative_to(root)
            lines = count_lines(file_path)
            files.append((rel_path, lines))

            # 确定模块名（顶层目录）
            if len(rel_path.parts) > 1:
                module_name = rel_path.parts[0]
                submodules = rel_path.parts[1:-1]
            else:
                module_name = rel_path.stem
                submodules = []

            modules_dict[module_name]['files'] += 1
            modules_dict[module_name]['lines'] += lines
            modules_dict[module_name]['extensions'][file_path.suffix] += 1
            for sub in submodules:
                modules_dict[module_name]['submodules'].add(sub)

    # 转换为 ModuleInfo 对象
    modules = []
    for name, info in sorted(modules_dict.items()):
        modules.append(ModuleInfo(
            name=name,
            path=str(root / name),
            file_count=info['files'],
            total_lines=info['lines'],
            extensions=dict(info['extensions']),
            submodules=sorted(list(info['submodules']))
        ))

    total_files = len(files)
    total_lines = sum(lines for _, lines in files)
    all_extensions = Counter(ext for _, ext in modules_dict.items() for ext in ext)

    return ScanResult(
        root=str(root),
        scan_time=datetime.now().isoformat(),
        total_files=total_files,
        total_lines=total_lines,
        modules=modules,
        extensions=dict(all_extensions)
    )


def format_markdown(result: ScanResult) -> str:
    """格式化为 Markdown 报告"""
    lines = [
        "# Codebase Scan Report",
        "",
        f"**Root**: `{result.root}`",
        f"**Scan Time**: {result.scan_time}",
        "",
        "## Overview",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total Files | {result.total_files} |",
        f"| Total Lines | {result.total_lines:,} |",
        f"| Total Modules | {len(result.modules)} |",
        "",
        "## Module Details",
        "",
        "| Module | Files | Lines | Extensions |",
        "|--------|-------|-------|-----------|",
    ]

    for m in result.modules:
        exts = ', '.join(f"{k}({v})" for k, v in sorted(m.extensions.items()))
        lines.append(f"| {m.name} | {m.file_count} | {m.total_lines:,} | {exts} |")

    if result.modules:
        lines.extend([
            "",
            "## Module Tree",
            ""
        ])
        for m in result.modules:
            if m.submodules:
                lines.append(f"### {m.name}/")
                for sub in m.submodules:
                    lines.append(f"  - {sub}")
                lines.append("")

    lines.extend([
        "## File Extensions",
        "",
        "| Extension | Count |",
        "|-----------|-------|",
    ])
    for ext, count in sorted(result.extensions.items(), key=lambda x: -x[1]):
        lines.append(f"| {ext} | {count} |")

    return '\n'.join(lines)


def format_json(result: ScanResult) -> str:
    """格式化为 JSON"""
    return json.dumps(asdict(result), indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description='Scan codebase and generate module statistics')
    parser.add_argument('root', type=Path, help='Codebase root directory')
    parser.add_argument('-e', '--extensions', nargs='+', help='File extensions to scan')
    parser.add_argument('-o', '--output', type=Path, help='Output file path')
    parser.add_argument('-f', '--format', choices=['markdown', 'json'], default='markdown',
                        help='Output format')

    args = parser.parse_args()

    if not args.root.exists():
        print(f"Error: Directory '{args.root}' does not exist")
        return 1

    # 执行扫描
    result = scan_codebase(args.root, args.extensions)

    # 格式化输出
    if args.format == 'markdown':
        output = format_markdown(result)
    else:
        output = format_json(result)

    # 输出
    if args.output:
        args.output.write_text(output, encoding='utf-8')
        print(f"Report saved to: {args.output}")
    else:
        print(output)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
