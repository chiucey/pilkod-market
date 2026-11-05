#!/usr/bin/env python3
"""
Porting Status Updater
更新移植清单中的模块状态
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Optional


def load_manifest(path: Path) -> dict:
    """加载清单文件"""
    return json.loads(path.read_text(encoding='utf-8'))


def save_manifest(path: Path, manifest: dict):
    """保存清单文件"""
    manifest['updated_at'] = datetime.now().isoformat()
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')


def update_module_status(manifest: dict, module_name: str, new_status: str) -> bool:
    """更新模块状态"""
    for module in manifest.get('modules', []):
        if module['name'] == module_name:
            old_status = module.get('status', 'planned')
            module['status'] = new_status
            module['updated_at'] = datetime.now().isoformat()
            print(f"Updated {module_name}: {old_status} → {new_status}")
            return True
    return False


def update_module_progress(manifest: dict, module_name: str, completed_lines: int) -> bool:
    """更新模块进度"""
    for module in manifest.get('modules', []):
        if module['name'] == module_name:
            module['completed_lines'] = completed_lines
            module['updated_at'] = datetime.now().isoformat()
            print(f"Updated {module_name}: completed_lines = {completed_lines}")

            # 自动更新状态
            if completed_lines >= module.get('estimated_lines', 0) and module['status'] == 'in_progress':
                module['status'] = 'review'
                print(f"  → Auto-updated status to: review")

            return True
    return False


def add_module(
    manifest: dict,
    name: str,
    source_path: str,
    target_path: str,
    priority: str = "medium",
    dependencies: Optional[list[str]] = None,
    notes: str = ""
) -> bool:
    """添加新模块到清单"""
    # 检查是否已存在
    for module in manifest.get('modules', []):
        if module['name'] == name:
            print(f"Module '{name}' already exists")
            return False

    new_module = {
        "name": name,
        "source_path": source_path,
        "target_path": target_path,
        "status": "planned",
        "priority": priority,
        "dependencies": dependencies or [],
        "notes": notes,
        "file_count": 0,
        "estimated_lines": 0,
        "completed_lines": 0,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    manifest.setdefault('modules', []).append(new_module)
    print(f"Added new module: {name}")
    return True


def remove_module(manifest: dict, module_name: str) -> bool:
    """从清单中移除模块"""
    original_count = len(manifest.get('modules', []))
    manifest['modules'] = [m for m in manifest.get('modules', []) if m['name'] != module_name]

    if len(manifest['modules']) < original_count:
        print(f"Removed module: {module_name}")
        return True
    return False


def list_modules(manifest: dict, status_filter: Optional[str] = None):
    """列出所有模块"""
    modules = manifest.get('modules', [])

    if status_filter:
        modules = [m for m in modules if m.get('status') == status_filter]

    if not modules:
        print(f"No modules found" + (f" with status '{status_filter}'" if status_filter else ""))
        return

    print(f"\nModules ({len(modules)}):")
    print("-" * 80)
    print(f"{'Name':<20} {'Status':<12} {'Priority':<8} {'Lines':<12} {'Deps':<20}")
    print("-" * 80)

    for m in modules:
        deps = ', '.join(m.get('dependencies', [])[:2])
        if len(m.get('dependencies', [])) > 2:
            deps += '...'
        print(f"{m['name']:<20} {m.get('status', 'planned'):<12} "
              f"{m.get('priority', 'medium'):<8} "
              f"{m.get('completed_lines', 0)}/{m.get('estimated_lines', 0):<8} "
              f"{deps:<20}")


def check_blocked(manifest: dict) -> list[dict]:
    """检查阻塞项"""
    blocked = []

    for module in manifest.get('modules', []):
        if module.get('status') == 'blocked':
            blocked.append({
                'name': module['name'],
                'reason': module.get('notes', 'Unknown'),
                'dependencies': module.get('dependencies', [])
            })

    return blocked


def generate_diff(old_manifest: dict, new_manifest: dict) -> str:
    """生成变更差异"""
    old_modules = {m['name']: m for m in old_manifest.get('modules', [])}
    new_modules = {m['name']: m for m in new_manifest.get('modules', [])}

    lines = ["# Porting Progress Diff", ""]

    # 新增模块
    added = set(new_modules.keys()) - set(old_modules.keys())
    if added:
        lines.append("## Added Modules")
        for name in sorted(added):
            lines.append(f"+ {name}")
        lines.append("")

    # 移除模块
    removed = set(old_modules.keys()) - set(new_modules.keys())
    if removed:
        lines.append("## Removed Modules")
        for name in sorted(removed):
            lines.append(f"- {name}")
        lines.append("")

    # 状态变更
    lines.append("## Status Changes")
    for name, new_mod in sorted(new_modules.items()):
        if name in old_modules:
            old_status = old_modules[name].get('status', 'planned')
            new_status = new_mod.get('status', 'planned')
            if old_status != new_status:
                lines.append(f"{name}: {old_status} → {new_status}")

    # 进度更新
    lines.append("")
    lines.append("## Progress Updates")
    for name, new_mod in sorted(new_modules.items()):
        if name in old_modules:
            old_lines = old_modules[name].get('completed_lines', 0)
            new_lines = new_mod.get('completed_lines', 0)
            if new_lines > old_lines:
                lines.append(f"{name}: {old_lines} → {new_lines} (+{new_lines - old_lines})")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Update porting manifest status')
    parser.add_argument('manifest', type=Path, help='Manifest JSON file')
    parser.add_argument('--status', metavar='MODULE=STATUS',
                        help='Update module status (e.g., auth=completed)')
    parser.add_argument('--progress', metavar='MODULE=LINES',
                        help='Update module progress (e.g., auth=500)')
    parser.add_argument('--add', action='store_true', help='Add new module')
    parser.add_argument('--remove', help='Remove module by name')
    parser.add_argument('--list', action='store_true', help='List all modules')
    parser.add_argument('--filter', choices=['planned', 'in_progress', 'review',
                                               'completed', 'blocked'],
                        help='Filter modules by status')
    parser.add_argument('--check-blocked', action='store_true', help='Check blocked items')
    parser.add_argument('--diff', type=Path, help='Compare with another manifest')

    args = parser.parse_args()

    if not args.manifest.exists():
        print(f"Error: Manifest file '{args.manifest}' not found")
        return 1

    manifest = load_manifest(args.manifest)

    if args.status:
        module_name, new_status = args.status.split('=')
        if not update_module_status(manifest, module_name.strip(), new_status.strip()):
            print(f"Module '{module_name}' not found")
            return 1
        save_manifest(args.manifest, manifest)

    elif args.progress:
        module_name, lines = args.progress.split('=')
        if not update_module_progress(manifest, module_name.strip(), int(lines.strip())):
            print(f"Module '{module_name}' not found")
            return 1
        save_manifest(args.manifest, manifest)

    elif args.add:
        print("Interactive module addition not implemented.")
        print("Use --status or --progress to update existing modules.")

    elif args.remove:
        if not remove_module(manifest, args.remove):
            print(f"Module '{args.remove}' not found")
            return 1
        save_manifest(args.manifest, manifest)

    elif args.list:
        list_modules(manifest, args.filter)

    elif args.check_blocked:
        blocked = check_blocked(manifest)
        if blocked:
            print(f"\nBlocked Items ({len(blocked)}):")
            print("-" * 60)
            for item in blocked:
                print(f"\n### {item['name']}")
                print(f"Reason: {item['reason']}")
                if item['dependencies']:
                    print(f"Waiting for: {', '.join(item['dependencies'])}")
        else:
            print("No blocked items!")

    elif args.diff:
        if not args.diff.exists():
            print(f"Error: Diff file '{args.diff}' not found")
            return 1
        old_manifest = load_manifest(args.diff)
        print(generate_diff(old_manifest, manifest))

    else:
        parser.print_help()

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
