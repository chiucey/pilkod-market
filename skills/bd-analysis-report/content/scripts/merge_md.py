#!/usr/bin/env python3
"""
BD分析报告 MD 分章节合并脚本

将按章节拆分的多个MD文件按顺序合并为一个完整的MD报告文件。

章节文件命名规则：
  ch00-header.md         — 报告头部（标题+meta）
  ch01.md ~ ch05.md      — 第一章至第五章
  ch06a.md ~ ch06e.md    — 第六章BD武器库（5个子节）
  ch07.md ~ ch13.md      — 第七章至第十三章
  app-a.md ~ app-c.md    — 附录A/B/C

用法：
    python scripts/merge_md.py --dir ./chapters --output report.md
    python scripts/merge_md.py --dir ./chapters --output report.md --enterprise "企业名"
"""

import argparse
import json
import os
import sys

# 合并顺序：严格按此顺序拼接，不处理列表外的文件
MERGE_ORDER = [
    "ch00-header.md",
    "ch01.md", "ch02.md", "ch03.md", "ch04.md", "ch05.md",
    "ch06a.md", "ch06b.md", "ch06c.md", "ch06d.md", "ch06e.md",
    "ch07.md", "ch08.md", "ch09.md", "ch10.md",
    "ch11.md", "ch12.md", "ch13.md",
    "app-a.md", "app-b.md", "app-c.md",
]


def merge_chapters(chapter_dir: str, output_path: str, enterprise: str = "") -> dict:
    """
    按顺序合并章节MD文件为一个完整MD报告。

    Args:
        chapter_dir: 章节MD文件所在目录
        output_path: 合并后输出的MD文件路径
        enterprise: 企业名称（用于报告元数据）

    Returns:
        合并结果dict，包含找到/缺失的章节信息
    """
    if not os.path.isdir(chapter_dir):
        return {"status": "error", "message": f"目录不存在: {chapter_dir}"}

    merged_parts = []
    missing = []
    found = 0

    for filename in MERGE_ORDER:
        filepath = os.path.join(chapter_dir, filename)
        if os.path.isfile(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            # 去除每章首尾空白，保留章节内部格式
            merged_parts.append(content.strip())
            found += 1
        else:
            # 文件不存在不影响合并，记录缺失即可
            missing.append(filename)

    # 合并：章节间用两个空行分隔，保证Markdown渲染时章节间有清晰间隔
    merged_content = "\n\n\n".join(merged_parts)

    # 确保文件末尾有换行
    if not merged_content.endswith("\n"):
        merged_content += "\n"

    # 写入输出文件（确保UTF-8无BOM）
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        f.write(merged_content)

    result = {
        "status": "success",
        "output": output_path,
        "chapters_found": found,
        "chapters_total": len(MERGE_ORDER),
        "chapters_missing": missing if missing else [],
        "merged_lines": merged_content.count("\n") + 1,
        "merged_size": len(merged_content.encode("utf-8")),
    }
    if enterprise:
        result["enterprise"] = enterprise

    return result


def main():
    parser = argparse.ArgumentParser(description="合并BD分析报告分章节MD文件")
    parser.add_argument("--dir", required=True, help="章节MD文件所在目录")
    parser.add_argument("--output", required=True, help="合并后输出的MD文件路径")
    parser.add_argument("--enterprise", default="", help="企业名称（可选）")
    args = parser.parse_args()

    result = merge_chapters(args.dir, args.output, args.enterprise)
    print(json.dumps(result, ensure_ascii=False))

    if result["status"] == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
