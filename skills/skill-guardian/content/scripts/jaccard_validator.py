#!/usr/bin/env python3
"""
Jaccard 相似度验证器
用于计算和验证技能触发词之间的相似度
"""

import argparse
import re
from pathlib import Path
from typing import Set


def parse_triggers_string(triggers_str: str) -> Set[str]:
    """解析逗号分隔的触发词字符串"""
    return set(t.strip() for t in triggers_str.split(',') if t.strip())


def extract_triggers_from_file(file_path: Path) -> Set[str]:
    """从 SKILL.md 文件中提取触发词"""
    triggers = set()
    try:
        content = file_path.read_text(encoding='utf-8')

        # 提取 frontmatter 中的 triggers
        if '---' in content:
            parts = content.split('---')
            if len(parts) >= 2:
                frontmatter = parts[1]

                # 匹配 triggers 列表
                trigger_match = re.search(
                    r'triggers:\s*\n((?:\s*-\s*.+\n)*)',
                    frontmatter
                )
                if trigger_match:
                    for line in trigger_match.group(1).split('\n'):
                        if line.strip().startswith('-'):
                            triggers.add(line.strip()[1:].strip())

                # 从 description 中提取触发短语
                desc_match = re.search(
                    r'description:\s*(.+?)(?:\n---|$)',
                    frontmatter,
                    re.DOTALL
                )
                if desc_match:
                    desc = desc_match.group(1)
                    # 提取中文和英文短语
                    for phrase in re.findall(r'[\u4e00-\u9fa5a-zA-Z0-9]{2,20}', desc):
                        triggers.add(phrase)

    except Exception as e:
        print(f"警告：无法读取文件 {file_path}: {e}")

    return triggers


def calculate_jaccard(set_a: Set[str], set_b: Set[str]) -> float:
    """计算 Jaccard 相似度"""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def get_merge_recommendation(similarity: float) -> tuple:
    """根据相似度返回融合建议"""
    if similarity > 0.6:
        return "🚨 必须融合", "critical", "立即执行融合"
    elif similarity > 0.3:
        return "⚠️ 建议融合", "warning", "询问用户后决定"
    else:
        return "✅ 不融合", "info", "保持现状"


def main():
    parser = argparse.ArgumentParser(
        description='Jaccard 相似度验证器 - 计算技能触发词相似度'
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--skill-a',
        help='技能A的触发词（逗号分隔）'
    )
    group.add_argument(
        '--skill-a-file',
        help='技能A的 SKILL.md 文件路径'
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--skill-b',
        help='技能B的触发词（逗号分隔）'
    )
    group.add_argument(
        '--skill-b-file',
        help='技能B的 SKILL.md 文件路径'
    )

    args = parser.parse_args()

    # 提取触发词
    if args.skill_a:
        triggers_a = parse_triggers_string(args.skill_a)
    else:
        triggers_a = extract_triggers_from_file(Path(args.skill_a_file))

    if args.skill_b:
        triggers_b = parse_triggers_string(args.skill_b)
    else:
        triggers_b = extract_triggers_from_file(Path(args.skill_b_file))

    # 计算相似度
    similarity = calculate_jaccard(triggers_a, triggers_b)
    intersection = triggers_a & triggers_b
    union = triggers_a | triggers_b
    recommendation, level, action = get_merge_recommendation(similarity)

    # 输出结果
    print("=" * 50)
    print("Jaccard 相似度分析结果")
    print("=" * 50)
    print(f"\n技能A 触发词 ({len(triggers_a)}个):")
    for t in sorted(triggers_a):
        print(f"  - {t}")

    print(f"\n技能B 触发词 ({len(triggers_b)}个):")
    for t in sorted(triggers_b):
        print(f"  - {t}")

    print(f"\n交集 ({len(intersection)}个):")
    for t in sorted(intersection):
        print(f"  - {t}")

    print(f"\n并集 ({len(union)}个):")
    for t in sorted(union):
        print(f"  - {t}")

    print("\n" + "=" * 50)
    print(f"Jaccard 相似度: {similarity:.2%}")
    print(f"推荐操作: {recommendation}")
    print(f"建议: {action}")
    print("=" * 50)

    return 0 if level == "info" else (1 if level == "critical" else 0)


if __name__ == '__main__':
    exit(main())
