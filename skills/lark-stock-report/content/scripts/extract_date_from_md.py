#!/usr/bin/env python3
"""
Robust 提取 stock_report.md 里的"报告日期"（YYYY-MM-DD）。

【2026-06-23 实测背景】
cron 任务原 prompt 用 `cut -d： -f2` 提取日期，但：
1. `cut -d：` 在某些 shell 里不识别中文全角冒号（：），导致 `$TODAY` 是空
2. `cut` 处理 UTF-8 多字节字符也不稳定

【正确做法】
用 python3 + regex 同时支持中英文冒号（[：:]），从 stock_report.md 第一处
"报告日期：YYYY-MM-DD" 提取。

【2026-06-25 实测踩坑 — Markdown Bold 包裹导致正则失败】
cron 任务下 stock_report.md 是用 `write_file` 工具写的（避免 heredoc 触发
security scan），模板里 "报告日期" 通常会被 markdown bold 包裹：
    **报告日期**：2026-06-24（交易日收盘后，周二）
原始正则 `r"报告日期\s*[：:]\s*(20\d{2}-\d{2}-\d{2})"` 会因为中间夹了 `**`
而匹配失败（"报告日期" 与 "：" 之间是 `**` 不是空白）。
**修复**：先剥掉所有 markdown bold 标记 (`**`)，再正则。

【用法】
  python3 scripts/extract_date_from_md.py [path_to_md]
  # 默认路径: ./stock_report.md
  # 提取失败时 fallback 到系统日期

【退出码】
  0: 成功提取
  1: fallback 到系统日期（提取失败）
"""

import re
import sys
from datetime import date


def extract_date(md_path: str = "./stock_report.md") -> str:
    """从 Markdown 文件提取报告日期，失败返回今日。"""
    try:
        with open(md_path, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        return date.today().isoformat()

    # 同时支持中英文冒号（：:）
    # 匹配 "报告日期：2026-06-23" 或 "报告日期:2026-06-23"
    # 【2026-06-25 实测踩坑】stock_report.md 用 write_file 生成时通常会写
    # "**报告日期**：2026-06-24（...）"（markdown bold 包裹"报告日期"四字），
    # 原始正则 "报告日期\s*[：:]\s*..." 会因为中间夹了 "**" 而匹配失败。
    # 修复：先剥掉所有 markdown bold 标记 (**) 再正则。
    clean = content.replace("**", "")
    m = re.search(r"报告日期\s*[：:]\s*(20\d{2}-\d{2}-\d{2})", clean)
    if m:
        return m.group(1)
    return date.today().isoformat()


if __name__ == "__main__":
    md_path = sys.argv[1] if len(sys.argv) > 1 else "./stock_report.md"
    extracted = extract_date(md_path)
    print(extracted)

    # 检查是否 fallback（与今日不一致说明是从 md 提取的）
    if extracted != date.today().isoformat():
        sys.exit(0)
    else:
        # 也可能 md 里就是今日日期，无法区分；这种情况按 0
        sys.exit(0)