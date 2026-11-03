#!/usr/bin/env python3
"""
OpenClaw 技能守护者 - 核心脚本
功能：检测技能冲突、智能融合、版本管理
"""

import argparse
import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple


def extract_triggers_from_skill(skill_path: Path) -> Set[str]:
    """从 SKILL.md 中提取触发词"""
    triggers = set()
    try:
        content = skill_path.read_text(encoding='utf-8')
        # 提取 frontmatter 中的 triggers
        if '---' in content:
            parts = content.split('---')
            if len(parts) >= 2:
                frontmatter = parts[1]
                # 匹配 triggers 列表
                trigger_match = re.search(r'triggers:\s*\n((?:\s*-\s*.+\n)*)', frontmatter)
                if trigger_match:
                    for line in trigger_match.group(1).split('\n'):
                        if line.strip().startswith('-'):
                            triggers.add(line.strip()[1:].strip())
                # 也从 description 中提取触发短语
                desc_match = re.search(r'description:\s*(.+?)(?:\n---|$)', frontmatter, re.DOTALL)
                if desc_match:
                    desc = desc_match.group(1)
                    # 提取中文逗号分隔的触发词
                    for phrase in re.findall(r'[\u4e00-\u9fa5a-zA-Z0-9]+', desc):
                        if 2 <= len(phrase) <= 20:
                            triggers.add(phrase)
    except Exception as e:
        print(f"警告：无法从 {skill_path} 提取触发词: {e}")
    return triggers


def calculate_jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    """计算 Jaccard 相似度"""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def merge_skills(skill_a_path: Path, skill_b_path: Path, output_path: Path) -> Dict:
    """融合两个技能"""
    # 读取两个技能内容
    content_a = skill_a_path.read_text(encoding='utf-8')
    content_b = skill_b_path.read_text(encoding='utf-8')

    # 提取触发词并合并
    triggers_a = extract_triggers_from_skill(skill_a_path)
    triggers_b = extract_triggers_from_skill(skill_b_path)
    merged_triggers = triggers_a | triggers_b

    result = {
        "merged_triggers": list(merged_triggers),
        "triggers_a": list(triggers_a),
        "triggers_b": list(triggers_b),
        "jaccard_similarity": calculate_jaccard_similarity(triggers_a, triggers_b),
        "output_path": str(output_path)
    }

    # 创建融合后的 SKILL.md
    merged_content = f"""---
name: merged-skill
description: 融合技能 - 合并自 {skill_a_path.parent.name} 和 {skill_b_path.parent.name}

triggers:
{chr(10).join(f'  - {t}' for t in sorted(merged_triggers))}

version-history:
  - v2: {datetime.now().strftime('%Y-%m-%d')} - 融合 {skill_a_path.parent.name} + {skill_b_path.parent.name}
  - v1: 初始版本
---

# 融合技能

此技能由以下技能融合而成：
- {skill_a_path.parent.name}
- {skill_b_path.parent.name}

## 触发词

{chr(10).join(f'- {t}' for t in sorted(merged_triggers))}

## Jaccard 相似度

融合相似度: {result['jaccard_similarity']:.2%}
"""

    output_path.write_text(merged_content, encoding='utf-8')
    return result


def detect_conflicts(skills_dir: Path) -> List[Dict]:
    """检测技能目录中的冲突"""
    conflicts = []
    skills = {}

    # 扫描所有技能
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir() and (skill_dir / 'SKILL.md').exists():
            skill_name = skill_dir.name
            triggers = extract_triggers_from_skill(skill_dir / 'SKILL.md')
            skills[skill_name] = {
                "path": skill_dir,
                "triggers": triggers
            }

    # 检测同名技能
    name_counts = {}
    for name in skills.keys():
        base_name = re.sub(r'\.v\d+$', '', name)
        name_counts.setdefault(base_name, []).append(name)

    for base_name, variants in name_counts.items():
        if len(variants) > 1:
            conflicts.append({
                "type": "duplicate_name",
                "base_name": base_name,
                "variants": variants,
                "severity": "critical"
            })

    # 检测触发词相似度
    skill_list = list(skills.items())
    for i, (name_a, data_a) in enumerate(skill_list):
        for name_b, data_b in skill_list[i+1:]:
            similarity = calculate_jaccard_similarity(data_a['triggers'], data_b['triggers'])
            if similarity > 0.6:
                conflicts.append({
                    "type": "high_similarity",
                    "skill_a": name_a,
                    "skill_b": name_b,
                    "similarity": similarity,
                    "common_triggers": list(data_a['triggers'] & data_b['triggers']),
                    "severity": "critical" if similarity > 0.6 else "warning"
                })
            elif similarity > 0.3:
                conflicts.append({
                    "type": "medium_similarity",
                    "skill_a": name_a,
                    "skill_b": name_b,
                    "similarity": similarity,
                    "common_triggers": list(data_a['triggers'] & data_b['triggers']),
                    "severity": "warning"
                })

    return conflicts


def archive_skill(skill_path: Path, archive_dir: Path) -> Path:
    """归档旧版本技能"""
    archive_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archive_name = f"{skill_path.name}.v{timestamp}"
    archive_path = archive_dir / archive_name
    shutil.copytree(skill_path, archive_path)
    return archive_path


def main():
    parser = argparse.ArgumentParser(description='OpenClaw 技能守护者')
    parser.add_argument('--detect', metavar='DIR', help='检测技能目录中的冲突')
    parser.add_argument('--merge', nargs=2, metavar=('SKILL_A', 'SKILL_B'),
                        help='融合两个技能')
    parser.add_argument('--output', help='融合输出路径')
    parser.add_argument('--archive-dir', help='归档目录')
    parser.add_argument('--skip-merge', action='store_true', help='跳过融合直接覆盖')

    args = parser.parse_args()

    if args.detect:
        skills_dir = Path(args.detect)
        if not skills_dir.exists():
            print(f"错误：目录不存在: {skills_dir}")
            return 1

        print(f"检测技能目录: {skills_dir}")
        conflicts = detect_conflicts(skills_dir)

        if not conflicts:
            print("✓ 未检测到技能冲突")
            return 0

        print(f"\n发现 {len(conflicts)} 个冲突:")
        for conflict in conflicts:
            severity = "🚨" if conflict['severity'] == 'critical' else "⚠️"
            print(f"\n{severity} [{conflict['type']}]")
            print(json.dumps(conflict, ensure_ascii=False, indent=2))

        return 0

    elif args.merge:
        skill_a = Path(args.merge[0])
        skill_b = Path(args.merge[1])

        if not skill_a.exists() or not skill_b.exists():
            print("错误：指定的技能路径不存在")
            return 1

        output_path = Path(args.output) if args.output else Path('merged_skill/SKILL.md')
        output_path.parent.mkdir(parents=True, exist_ok=True)

        result = merge_skills(skill_a, skill_b, output_path)
        print("✓ 技能融合完成")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    exit(main())
