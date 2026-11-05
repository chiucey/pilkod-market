#!/usr/bin/env python3
"""
自我迭代技能 - 升级执行器
执行经过验证的升级，更新版本号
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Any
import re

def get_skill_dir() -> str:
    """获取技能目录"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def create_backup(skill_dir: str) -> str:
    """创建备份"""
    backup_dir = os.path.join(skill_dir, 'data', 'backups')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'backup_{timestamp}')

    os.makedirs(backup_path, exist_ok=True)

    # 备份关键文件
    files_to_backup = ['SKILL.md', '_meta.json']
    for f in files_to_backup:
        src = os.path.join(skill_dir, f)
        if os.path.exists(src):
            shutil.copy2(src, backup_path)

    # 备份 scripts 目录
    scripts_src = os.path.join(skill_dir, 'scripts')
    if os.path.exists(scripts_src):
        shutil.copytree(scripts_src, os.path.join(backup_path, 'scripts'))

    # 备份 references 目录
    refs_src = os.path.join(skill_dir, 'references')
    if os.path.exists(refs_src):
        shutil.copytree(refs_src, os.path.join(backup_path, 'references'))

    return backup_path

def get_current_version(meta_path: str) -> str:
    """获取当前版本号"""
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
            return meta.get('version', '1.0.0')
    return '1.0.0'

def bump_version(current_version: str, level: str = 'patch') -> str:
    """更新版本号"""
    parts = current_version.split('.')
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

    if level == 'major':
        major += 1
        minor = 0
        patch = 0
    elif level == 'minor':
        minor += 1
        patch = 0
    else:  # patch
        patch += 1

    return f'{major}.{minor}.{patch}'

def update_meta_version(skill_dir: str, new_version: str) -> bool:
    """更新 _meta.json 版本号"""
    meta_path = os.path.join(skill_dir, '_meta.json')
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        old_version = meta.get('version', '1.0.0')
        meta['version'] = new_version

        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        return True
    except Exception as e:
        print(f"更新版本失败: {e}")
        return False

def apply_skill_md_update(skill_dir: str, update_content: str) -> bool:
    """应用 SKILL.md 更新"""
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    try:
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 在文件末尾添加更新内容
        content += '\n\n---\n\n## 更新日志\n\n'
        content += f'**版本更新**: {datetime.now().isoformat()}\n\n'
        content += update_content

        with open(skill_md_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return True
    except Exception as e:
        print(f"更新 SKILL.md 失败: {e}")
        return False

def apply_reference_creation(skill_dir: str, ref_path: str, content: str) -> bool:
    """创建新的参考文档"""
    full_path = os.path.join(skill_dir, ref_path)
    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"创建参考文档失败: {e}")
        return False

def apply_script_creation(skill_dir: str, script_path: str, content: str) -> bool:
    """创建新的脚本"""
    full_path = os.path.join(skill_dir, script_path)
    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        # 设置执行权限
        os.chmod(full_path, 0o755)
        return True
    except Exception as e:
        print(f"创建脚本失败: {e}")
        return False

def validate_upgrade(skill_dir: str) -> Dict[str, Any]:
    """验证升级完整性"""
    validation = {
        'valid': True,
        'issues': []
    }

    # 检查必要文件
    required_files = ['SKILL.md', '_meta.json']
    for f in required_files:
        if not os.path.exists(os.path.join(skill_dir, f)):
            validation['valid'] = False
            validation['issues'].append(f'缺少必要文件: {f}')

    # 检查 _meta.json 格式
    meta_path = os.path.join(skill_dir, '_meta.json')
    if os.path.exists(meta_path):
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            if 'id' not in meta or 'version' not in meta:
                validation['valid'] = False
                validation['issues'].append('_meta.json 缺少 id 或 version 字段')
        except:
            validation['valid'] = False
            validation['issues'].append('_meta.json 格式错误')

    # 检查 SKILL.md frontmatter
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    if os.path.exists(skill_md_path):
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if not content.startswith('---'):
            validation['valid'] = False
            validation['issues'].append('SKILL.md 必须以 frontmatter (---) 开头')

    return validation

def execute_upgrade(plan: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """执行升级"""
    skill_dir = get_skill_dir()
    result = {
        'success': True,
        'backup_path': None,
        'applied_changes': [],
        'new_version': None,
        'validation': None
    }

    if dry_run:
        print("【Dry Run 模式】 - 不实际执行任何更改")
        return result

    # 1. 创建备份
    try:
        result['backup_path'] = create_backup(skill_dir)
        result['applied_changes'].append(f'备份已创建: {result["backup_path"]}')
    except Exception as e:
        result['success'] = False
        result['error'] = f'备份失败: {e}'
        return result

    # 2. 确定版本更新级别
    current_version = get_current_version(os.path.join(skill_dir, '_meta.json'))
    high_priority_count = sum([
        len(plan['suggestions']['skill_md']),
        len(plan['suggestions']['scripts'])
    ])
    version_level = 'minor' if high_priority_count > 0 else 'patch'
    new_version = bump_version(current_version, version_level)

    # 3. 应用更改
    # SKILL.md 更新
    if plan['suggestions']['skill_md']:
        skill_updates = '\n'.join([f'- {s["title"]}: {s["description"]}'
                                   for s in plan['suggestions']['skill_md'][:3]])
        if apply_skill_md_update(skill_dir, skill_updates):
            result['applied_changes'].append('SKILL.md 已更新')

    # 参考文档创建
    for ref in plan['suggestions']['references'][:2]:
        default_content = f'# {ref["title"]}\n\n{ref["description"]}\n\n## 概述\n\nTODO: 补充详细内容\n'
        if apply_reference_creation(skill_dir, ref['target'], default_content):
            result['applied_changes'].append(f'创建参考文档: {ref["target"]}')

    # 4. 更新版本号
    if update_meta_version(skill_dir, new_version):
        result['new_version'] = new_version
        result['applied_changes'].append(f'版本更新: {current_version} → {new_version}')

    # 5. 验证
    result['validation'] = validate_upgrade(skill_dir)

    return result

def print_upgrade_result(result: Dict[str, Any]) -> None:
    """打印升级结果"""
    print("\n" + "="*60)
    print("自我迭代升级执行报告")
    print("="*60)
    print(f"\n时间: {datetime.now().isoformat()}")
    print(f"状态: {'成功' if result['success'] else '失败'}")

    if result.get('backup_path'):
        print(f"\n备份位置: {result['backup_path']}")

    if result['applied_changes']:
        print(f"\n【已应用的更改】")
        for change in result['applied_changes']:
            print(f"  ✓ {change}")

    if result.get('new_version'):
        print(f"\n新版本: {result['new_version']}")

    if result.get('validation'):
        v = result['validation']
        if v['valid']:
            print(f"\n验证结果: 通过 ✓")
        else:
            print(f"\n验证结果: 失败 ✗")
            for issue in v['issues']:
                print(f"  - {issue}")

    if result.get('error'):
        print(f"\n错误: {result['error']}")

    print("\n" + "="*60)

if __name__ == '__main__':
    import sys

    dry_run = '--dry-run' in sys.argv

    # 尝试加载改进计划
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    plan_path = os.path.join(skill_dir, 'data', 'improvement_plan.json')

    if os.path.exists(plan_path):
        with open(plan_path, 'r', encoding='utf-8') as f:
            plan = json.load(f)
    else:
        # 创建空计划
        plan = {
            'timestamp': datetime.now().isoformat(),
            'suggestions': {
                'skill_md': [],
                'scripts': [],
                'references': []
            }
        }

    result = execute_upgrade(plan, dry_run=dry_run)
    print_upgrade_result(result)
