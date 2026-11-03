"""命令行检索工具：支持关键词、标签过滤、交互模式与 CSV 导出。"""

import argparse
import csv
import os
import sqlite3
from typing import Dict, List

from config import DB_PATH
from index_manager import clean_missing_files, ensure_index, search


def _parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="国资资料库命令行检索工具",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("-k", "--keyword", default="", help="关键词，搜索文件名和内容")
    parser.add_argument("-t", "--tags", default="", help="标签，逗号分隔（AND 逻辑）")
    parser.add_argument("-l", "--limit", type=int, default=20, help="显示条数，默认 20")
    parser.add_argument(
        "--export",
        choices=["csv"],
        default="",
        help="导出结果，例如：--export csv",
    )
    return parser.parse_args()


def _interactive_input() -> tuple[str, str, int, str]:
    """无参数时进入交互模式。"""
    print("进入交互检索模式（直接回车可留空）：")
    keyword = input("请输入关键词: ").strip()
    tags = input("请输入标签（逗号分隔）: ").strip()
    limit_text = input("请输入显示条数（默认20）: ").strip()
    limit = 20
    if limit_text.isdigit() and int(limit_text) > 0:
        limit = int(limit_text)
    export = input("是否导出 CSV？输入 csv 或留空: ").strip().lower()
    export = "csv" if export == "csv" else ""
    return keyword, tags, limit, export


def _get_meta_by_doc_id(doc_id: str) -> Dict[str, str]:
    """从 SQLite 读取分类、处理时间等展示字段。"""
    if not os.path.exists(DB_PATH):
        return {"category": "", "processed_time": "", "tags": ""}

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT category1, category2, tags, processed_time FROM files WHERE id = ?",
            (doc_id,),
        )
        row = cur.fetchone()
        if not row:
            return {"category": "", "processed_time": "", "tags": ""}
        category1, category2, tags, processed_time = row
        category = "_".join([x for x in [category1 or "", category2 or ""] if x])
        return {
            "category": category,
            "processed_time": processed_time or "",
            "tags": tags or "",
        }
    finally:
        conn.close()


def _filter_by_tags(items: List[Dict[str, str]], tags_text: str) -> List[Dict[str, str]]:
    """按 AND 逻辑过滤标签。"""
    query_tags = [t.strip() for t in tags_text.split(",") if t.strip()]
    if not query_tags:
        return items

    filtered: List[Dict[str, str]] = []
    for item in items:
        item_tags = {t.strip() for t in (item.get("tags") or "").split(",") if t.strip()}
        if all(tag in item_tags for tag in query_tags):
            filtered.append(item)
    return filtered


def _format_table(rows: List[Dict[str, str]]) -> str:
    """手动对齐输出表格。"""
    headers = ["文件名", "分类", "标签", "处理时间"]
    data = [[r["file_name"], r["category"], r["tags"], r["processed_time"]] for r in rows]

    widths = [len(h) for h in headers]
    for row in data:
        for i, col in enumerate(row):
            widths[i] = max(widths[i], len(str(col)))

    def fmt_line(cols: List[str]) -> str:
        return " | ".join(str(c).ljust(widths[i]) for i, c in enumerate(cols))

    sep = "-+-".join("-" * w for w in widths)
    lines = [fmt_line(headers), sep]
    lines.extend(fmt_line(row) for row in data)
    return "\n".join(lines)


def _export_csv(rows: List[Dict[str, str]], file_name: str = "search_results.csv") -> str:
    """导出检索结果到 CSV 文件。"""
    with open(file_name, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["file_name", "category", "tags", "processed_time"])
        for row in rows:
            writer.writerow([row["file_name"], row["category"], row["tags"], row["processed_time"]])
    return os.path.abspath(file_name)


def main() -> None:
    """检索入口。"""
    ensure_index()
    cleaned = clean_missing_files()
    if cleaned:
        print(f"[INFO] 已清理缺失文件记录: {cleaned} 条")
    args = _parse_args()

    has_cli_args = any([args.keyword, args.tags, args.limit != 20, args.export])
    if not has_cli_args:
        keyword, tags_text, limit, export_type = _interactive_input()
    else:
        keyword, tags_text, limit, export_type = (
            args.keyword.strip(),
            args.tags.strip(),
            max(args.limit, 1),
            args.export,
        )

    whoosh_results = search(keyword or "*")
    merged: List[Dict[str, str]] = []
    for item in whoosh_results:
        meta = _get_meta_by_doc_id(item.get("doc_id", ""))
        merged.append(
            {
                "doc_id": item.get("doc_id", ""),
                "file_name": item.get("file_name", ""),
                "category": meta["category"],
                "tags": meta["tags"] or item.get("tags", ""),
                "processed_time": meta["processed_time"],
            }
        )

    filtered = _filter_by_tags(merged, tags_text)
    limited = filtered[:limit]

    if not limited:
        print("未检索到结果。")
        return

    print(f"关键词: {keyword or '(全部)'} | 标签: {tags_text or '(无)'} | 数量: {len(limited)}")
    print(_format_table(limited))

    if export_type == "csv":
        output_path = _export_csv(limited)
        print(f"\n已导出 CSV: {output_path}")


if __name__ == "__main__":
    main()

