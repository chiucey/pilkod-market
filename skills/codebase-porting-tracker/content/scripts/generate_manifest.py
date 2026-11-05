#!/usr/bin/env python3
"""
Porting Manifest Generator
从扫描结果生成移植清单
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Optional
from enum import Enum


class PortingStatus(Enum):
    """移植状态"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class Priority(Enum):
    """优先级"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class PortingModule:
    """移植模块"""
    name: str
    source_path: str
    target_path: str
    status: str = "planned"
    priority: str = "medium"
    dependencies: list[str] = field(default_factory=list)
    notes: str = ""
    file_count: int = 0
    estimated_lines: int = 0
    completed_lines: int = 0
    created_at: str = ""
    updated_at: str = ""


@dataclass
class PortingManifest:
    """移植清单"""
    project_name: str
    source_lang: str
    target_lang: str
    source_root: str
    target_root: str
    modules: list[PortingModule] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

    def get_stats(self) -> dict:
        """获取统计信息"""
        total = len(self.modules)
        completed = sum(1 for m in self.modules if m.status == "completed")
        in_progress = sum(1 for m in self.modules if m.status == "in_progress")
        blocked = sum(1 for m in self.modules if m.status == "blocked")
        planned = sum(1 for m in self.modules if m.status == "planned")

        total_lines = sum(m.estimated_lines for m in self.modules)
        done_lines = sum(m.completed_lines for m in self.modules)

        completion_rate = (completed / total * 100) if total > 0 else 0
        lines_rate = (done_lines / total_lines * 100) if total_lines > 0 else 0

        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "blocked": blocked,
            "planned": planned,
            "completion_rate": completion_rate,
            "total_lines": total_lines,
            "done_lines": done_lines,
            "lines_rate": lines_rate
        }

    def to_markdown(self) -> str:
        """转换为 Markdown 格式"""
        stats = self.get_stats()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines = [
            "# Porting Manifest",
            "",
            f"**Project**: {self.project_name}",
            f"**Direction**: {self.source_lang} → {self.target_lang}",
            f"**Source Root**: `{self.source_root}`",
            f"**Target Root**: `{self.target_root}`",
            f"**Generated**: {now}",
            "",
            "## Overview",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Total Modules | {stats['total']} |",
            f"| Completed | {stats['completed']} |",
            f"| In Progress | {stats['in_progress']} |",
            f"| Blocked | {stats['blocked']} |",
            f"| Planned | {stats['planned']} |",
            f"| Module Completion | {stats['completion_rate']:.1f}% |",
            f"| Lines Completed | {stats['done_lines']:,} / {stats['total_lines']:,} ({stats['lines_rate']:.1f}%) |",
            "",
            "## Module Status",
            "",
            "| Module | Source | Target | Status | Priority | Dependencies |",
            "|--------|--------|--------|--------|----------|--------------|",
        ]

        # 按状态和优先级排序
        status_order = {"in_progress": 0, "review": 1, "completed": 2, "blocked": 3, "planned": 4}
        priority_order = {"high": 0, "medium": 1, "low": 2}

        sorted_modules = sorted(
            self.modules,
            key=lambda m: (status_order.get(m.status, 99), priority_order.get(m.priority, 99), m.name)
        )

        for m in sorted_modules:
            deps = ', '.join(m.dependencies) if m.dependencies else '-'
            notes = f"*{m.notes}*" if m.notes else ""
            lines.append(
                f"| {m.name} | {m.source_path} | {m.target_path} | {m.status} | {m.priority} | {deps} |"
            )

        # 阻塞项
        blocked_modules = [m for m in self.modules if m.status == "blocked"]
        if blocked_modules:
            lines.extend(["", "## Blocked Items", ""])
            for m in blocked_modules:
                lines.append(f"### {m.name}")
                lines.append(f"- **Reason**: {m.notes or 'Unknown'}")
                lines.append(f"- **Dependencies**: {', '.join(m.dependencies) if m.dependencies else 'None'}")
                lines.append("")

        # 待处理项
        planned_modules = [m for m in self.modules if m.status == "planned"]
        if planned_modules:
            lines.extend(["", "## Planned Items", ""])
            for m in planned_modules:
                lines.append(f"- **{m.name}** ({m.priority} priority) - {m.notes or 'No description'}")

        lines.extend([
            "",
            "---",
            f"*Last updated: {self.updated_at or now}*"
        ])

        return '\n'.join(lines)

    def to_json(self) -> str:
        """转换为 JSON 格式"""
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, path: Path) -> 'PortingManifest':
        """从 JSON 文件加载"""
        data = json.loads(path.read_text(encoding='utf-8'))
        # 转换 modules
        data['modules'] = [PortingModule(**m) for m in data.get('modules', [])]
        return cls(**data)


def create_from_scan(
    scan_result_path: Path,
    project_name: str,
    source_lang: str,
    target_lang: str,
    source_root: str,
    target_root: str
) -> PortingManifest:
    """从扫描结果创建清单"""
    # 加载扫描结果
    scan_data = json.loads(scan_result_path.read_text(encoding='utf-8'))

    modules = []
    for mod in scan_data.get('modules', []):
        modules.append(PortingModule(
            name=mod['name'],
            source_path=mod['path'],
            target_path=mod['path'].replace(source_root, target_root),
            file_count=mod.get('file_count', 0),
            estimated_lines=mod.get('total_lines', 0),
            created_at=datetime.now().isoformat()
        ))

    # 设置依赖关系（基于命名约定推断）
    _infer_dependencies(modules)

    manifest = PortingManifest(
        project_name=project_name,
        source_lang=source_lang,
        target_lang=target_lang,
        source_root=source_root,
        target_root=target_root,
        modules=modules,
        created_at=datetime.now().isoformat()
    )

    return manifest


def _infer_dependencies(modules: list[PortingModule]):
    """基于命名约定推断依赖关系"""
    common_patterns = {
        'core': ['models', 'types', 'utils', 'constants'],
        'auth': ['models', 'utils'],
        'api': ['models', 'auth', 'utils'],
        'ui': ['models', 'utils', 'hooks'],
    }

    for mod in modules:
        mod_name_lower = mod.name.lower()
        for base, deps in common_patterns.items():
            if mod_name_lower in deps and base in [m.name.lower() for m in modules]:
                base_mod = next((m for m in modules if m.name.lower() == base), None)
                if base_mod and base not in mod.dependencies:
                    mod.dependencies.append(base)


def main():
    parser = argparse.ArgumentParser(description='Generate or update porting manifest')
    parser.add_argument('--create', action='store_true', help='Create new manifest from scan')
    parser.add_argument('--scan', type=Path, help='Scan result JSON file')
    parser.add_argument('--project', type=str, help='Project name')
    parser.add_argument('--source-lang', type=str, help='Source language')
    parser.add_argument('--target-lang', type=str, help='Target language')
    parser.add_argument('--source-root', type=str, help='Source root path')
    parser.add_argument('--target-root', type=str, help='Target root path')
    parser.add_argument('--output', type=Path, help='Output manifest file')
    parser.add_argument('--format', choices=['markdown', 'json'], default='markdown',
                        help='Output format')

    args = parser.parse_args()

    if args.create:
        if not all([args.scan, args.project, args.source_lang, args.target_lang]):
            print("Error: --create requires --scan, --project, --source-lang, and --target-lang")
            return 1

        manifest = create_from_scan(
            args.scan,
            args.project,
            args.source_lang,
            args.target_lang,
            args.source_root or "./src",
            args.target_root or "./target_src"
        )
    else:
        print("Error: Use --create to generate a new manifest")
        return 1

    # 输出
    if args.format == 'json':
        output = manifest.to_json()
    else:
        output = manifest.to_markdown()

    if args.output:
        args.output.write_text(output, encoding='utf-8')
        print(f"Manifest saved to: {args.output}")
    else:
        print(output)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
