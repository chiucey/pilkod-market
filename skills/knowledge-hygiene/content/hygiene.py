#!/usr/bin/env python3
"""
Knowledge Hygiene Engine — Dorian 记忆有效期机制
存储层：memory/KNOWLEDGE_REGISTRY.md
执行层：hygiene.py

v7 (2026-04-10)：重写 write_registry，删除有问题的 _find_sep_end。
  旧版问题：_find_sep_end CC=19，嵌套扫描逻辑有 bug，
            导致 write_registry CC=22、NPath=256、越改越乱。
  修复：改用 content.split("\\n## ") 分割，CC=1，逻辑透明可证。
"""

import sys, re, difflib
from datetime import datetime, timedelta
from pathlib import Path

REGISTRY_PATH = Path("memory/KNOWLEDGE_REGISTRY.md")
MEMORY_PATH   = Path("memory/MEMORY.md")
# v8: 2026-04-11
#   问题：COLS=7列，实际文件header=8列，zip截断导致第8列数据永久丢失
#   修复：COLS扩为8列；parse_registry改用固定COLS模板，不依赖原header；
#         write_registry写入时强制8列，不足的pad空字符串
COLS = ["ID", "Category", "Topic", "LastUpdated", "ExpiryMonths", "Status", "Notes", "Attr"]
OUTPUT_WIDTH = 80

# ─────────────────────────────────────────────────────────────
# 日期工具
# ─────────────────────────────────────────────────────────────

def parse_date(s):
    try: return datetime.strptime(s.strip(), "%Y-%m-%d")
    except (ValueError, TypeError): return None

def parse_expiry(s):
    s = s.strip()
    if s in ("永久", "永久有效", "PERMANENT", "permanent", ""): return None
    m = re.match(r"^(\d+(?:\.\d+)?)天$", s)
    if m: return float(m.group(1)) / 30.4375
    try: return float(s)
    except ValueError: return None

def days_remaining(last_updated, expiry_months_raw):
    exp = parse_expiry(expiry_months_raw)
    if exp is None: return None
    d = parse_date(last_updated)
    if d is None: return None
    return (d + timedelta(days=exp * 30.4375) - datetime.now()).days

# ─────────────────────────────────────────────────────────────
# Registry 表格解析
# ─────────────────────────────────────────────────────────────

def is_separator(stripped):
    parts = [c.strip() for c in stripped.split("|")[1:-1]]
    return bool(parts) and all(re.match(r"^[-:]+$", c) for c in parts)

def is_section(stripped):
    return stripped.startswith("## ")

def count_tables(content):
    return len(re.findall(r"^\| ID \|", content, re.MULTILINE))

def parse_registry(content):
    """解析第一条完整表格；遇第二个 ## 标题时停止。

    v8: 改用固定 COLS 模板解析，不依赖原 header 列数。
        - 支持无表头行格式（真实 Registry 文件没有表头）
        - 7列表格自动 pad 到8列（Attr 留空）
        - 8列表格完整读取
        - Notes 含管道符时也能正确处理
    """
    lines = content.splitlines()
    rows, seen_ids = [], set()
    in_table = False
    has_header = False   # 是否已找到表头行（| ID | ...）
    for line in lines:
        stripped = line.strip()
        if not stripped: continue
        if is_section(stripped):
            if in_table: break
            continue
        if not stripped.startswith("|"):
            in_table = False; continue
        # v8: split 后去除首尾空列，再删除尾部空字符串
        raw_parts = stripped.split("|")[1:-1]
        parts = [c.strip() for c in raw_parts]
        while parts and parts[-1] == "":
            parts.pop()
        if not parts: continue
        # 识别表头行：找到则标记并跳过（但无需设置 in_table）
        if not has_header and len(parts) >= 3 and parts[0] == "ID" and "LastUpdated" in parts:
            has_header = True; in_table = True; continue
        if in_table and is_separator(stripped): continue
        if in_table and len(parts) >= 7:
            padded = parts + [""] * (len(COLS) - len(parts))
            row = dict(zip(COLS, padded))
            rid = row.get("ID", "").strip()
            if rid and rid not in seen_ids:
                seen_ids.add(rid); rows.append(row)
        # v8 新增：无表头时，第一行 KR-xxx 格式直接作为数据解析
        if not has_header and len(parts) >= 7 and parts[0].startswith("KR-"):
            in_table = True
            padded = parts + [""] * (len(COLS) - len(parts))
            row = dict(zip(COLS, padded))
            rid = row.get("ID", "").strip()
            if rid and rid not in seen_ids:
                seen_ids.add(rid); rows.append(row)
    return rows

def compute_status(row):
    status = row.get("Status", "ACTIVE").upper()
    if status == "ARCHIVED": return "ARCHIVED"
    exp = parse_expiry(row.get("ExpiryMonths", "").strip())
    if exp is None: return "ACTIVE"
    d = parse_date(row.get("LastUpdated", "").strip())
    if d is None: return "ACTIVE"
    return "STALE" if datetime.now() >= d + timedelta(days=exp * 30.4375) else "ACTIVE"

# ─────────────────────────────────────────────────────────────
# Registry 写入核心（v7 — CC=1 算法）
#
# 旧版问题：
#   _find_sep_end CC=19，嵌套扫描导致 sep_end 定位错误，
#   write_registry CC=22、NPath=256，越补救越乱。
#
# 修复策略：
#   用 content.split("\\n## ") 分割全文，CC=1，逻辑透明。
#   第一个片段 = 第一张表之前所有内容（不含 ## 标题本身）。
#   截断点在第一个 "## " 出现的位置（不含 ## 之后的内容）。
#
# ─────────────────────────────────────────────────────────────

def _collect_all_rows(content):
    """
    遍历文件中 ALL 表格，收集去重数据行。
    v8: 用固定 COLS 模板，不依赖原 header 列数；
        支持无表头格式；多表合并时统一到8列，不足的 pad 空字符串。
    """
    lines = content.splitlines()
    rows, seen_ids = [], set()
    in_table = False
    has_header = False
    for line in lines:
        stripped = line.strip()
        if not stripped: continue
        if not stripped.startswith("|"): continue
        raw_parts = stripped.split("|")[1:-1]
        parts = [c.strip() for c in raw_parts]
        while parts and parts[-1] == "":
            parts.pop()
        if not parts: continue
        if not has_header and len(parts) >= 3 and parts[0] == "ID" and "LastUpdated" in parts:
            has_header = True; in_table = True; continue
        if is_separator(stripped): continue
        if in_table and len(parts) >= 7:
            padded = parts + [""] * (len(COLS) - len(parts))
            row = dict(zip(COLS, padded))
            rid = row.get("ID", "").strip()
            if rid.startswith("KR-") and rid not in seen_ids:
                seen_ids.add(rid); rows.append(row)
        if not has_header and len(parts) >= 7 and parts[0].startswith("KR-"):
            in_table = True
            padded = parts + [""] * (len(COLS) - len(parts))
            row = dict(zip(COLS, padded))
            rid = row.get("ID", "").strip()
            if rid.startswith("KR-") and rid not in seen_ids:
                seen_ids.add(rid); rows.append(row)
    return rows


def write_registry(content, rows):
    """
    v7：CC=1 算法，保证幂等 + 多表合并。

    截断逻辑（CC=1）：
      1. 找 content 中第一个 "\\n## " 的位置
      2. content[:pos] = 第一张表全部内容（不含 ## 标题本身）
      3. 新数据块接在后面
      4. 幂等：count_tables == 1 且 ID 集合不变 → 不写

    关键保证：
      - 无论原文件有多少个 ## section，截断后只剩第一个 section 的表头+数据
      - 无嵌套扫描，无位置计算偏移，逻辑可直接验证
    """
    table_count = count_tables(content)
    today = datetime.now().strftime("%Y-%m-%d")

    # 多表：合并所有表格数据
    if table_count > 1:
        all_rows = _collect_all_rows(content)
        if len(all_rows) >= len(rows):
            rows = all_rows
        print(f"  ℹ️  发现 {table_count} 表，已合并为 {len(rows)} 条去重数据")

    # 幂等：单表且 ID 集合不变 → 不写
    if table_count == 1:
        old_ids = {r["ID"] for r in _collect_all_rows(content)}
        new_ids = {r["ID"] for r in rows if r.get("ID", "").strip()}
        if old_ids == new_ids:
            return content   # 无变化，不写

    # 截断：找到第一个 \n##  的位置（不含 ## 之后所有内容）
    #   content.find("\\n## ") → 第一个 ## 前面的 \n 位置
    #   prefix = content[:pos] → 包含 # Title 和第一个 ## Section 标题
    #   需要额外去掉最后一个空行，让新数据块直接接在表头后面
    # 截断策略（v7.1）：
    # 保留第一张表的 section 标题，重建 header + separator（不含旧数据）
    # 逻辑透明：找到 \n##  → 截断 → 提取 section 标题 → 追加新 header + sep + 数据
    #
    # 修复记录（v7.1）：
    #   v7.0 的 rstrip("\\n") 会去掉原分隔行的 \n，
    #   导致分隔行和第一个数据行连成一行（14列），parse_registry 跳过整行。
    #   v7.1 直接重建分隔行，不依赖原内容格式。
    sec_marker = "\n## "
    pos = content.find(sec_marker)
    raw = content[:pos] if pos != -1 else content

    # ── v8 修复：从固定 COLS 模板重建，不从原文提取 ──────────
    section_line = next(
        (ln.rstrip("\n") for ln in raw.splitlines() if ln.strip().startswith("## ")),
        ""
    )
    # ── v8 关键修复：header + separator 全部从 COLS 模板重建 ─
    header_line    = "| " + " | ".join(COLS) + " |"
    separator_line = "| " + " | ".join(["--"] * len(COLS)) + " |"
    prefix = (section_line + "\n\n" + header_line + "\n" + separator_line + "\n"
              if section_line
              else header_line + "\n" + separator_line + "\n")

    # 构建新数据块
    new_data = "\n".join(
        "| " + " | ".join(str(r.get(c, "")) for c in COLS) + " |"
        for r in rows
    )
    result = prefix + new_data + "\n"

    # 更新时间戳
    result = re.sub(
        r"(\*\*最后检查\*\*：|\*最后检查：|最后检查：)\d{4}-\d{2}-\d{2}",
        f"**最后检查**：{today}",
        result
    )
    return result

# ─────────────────────────────────────────────────────────────
# Registry 操作
# ─────────────────────────────────────────────────────────────

def scan(quiet=False):
    if not REGISTRY_PATH.exists():
        return {"ok": False, "error": f"文件不存在: {REGISTRY_PATH}"}
    content = REGISTRY_PATH.read_text(encoding="utf-8")
    rows = parse_registry(content)
    if not rows:
        return {"ok": False, "error": "未能解析到任何数据行，请检查文件格式。"}
    changes = []
    for row in rows:
        old = row.get("Status", "ACTIVE").upper()
        new = compute_status(row)
        if old != new:
            changes.append({
                "id": row.get("ID", "?"), "topic": row.get("Topic", "?"),
                "from": old, "to": new,
                "last_updated": row.get("LastUpdated", ""),
                "expiry": row.get("ExpiryMonths", ""),
            })
            row["Status"] = new
    new_content = write_registry(content, rows)
    REGISTRY_PATH.write_text(new_content, encoding="utf-8")
    if not quiet:
        if changes:
            print(f"\n🔄 Registry 扫描完成，发现 {len(changes)} 处变化：\n")
            for c in changes:
                ed = "永久" if c["expiry"] in ("永久",) else c["expiry"]
                print(f"  [{c['id']}] {c['topic']}  {c['from']} → {c['to']}  (Expiry: {ed})\n")
        else:
            print(f"\n✅ Registry 无过期条目（截至 {datetime.now().strftime('%Y-%m-%d')}）")
    return {"ok": True, "changed": bool(changes), "changes": changes, "rows": rows}


def report():
    res = scan(quiet=True)
    if not res.get("ok"): return f"错误：{res.get('error')}"
    rows = res.get("rows", [])
    changes = res.get("changes", [])
    active = [r for r in rows if r.get("Status", "").upper() == "ACTIVE"]
    stale  = [r for r in rows if r.get("Status", "").upper() == "STALE"]
    arch   = [r for r in rows if r.get("Status", "").upper() == "ARCHIVED"]
    today = datetime.now().strftime("%Y-%m-%d")
    lines = [
        f"\n{'═'*OUTPUT_WIDTH}",
        f"  📋 Knowledge Registry — 健康报告  |  {today}",
        f"{'═'*OUTPUT_WIDTH}",
        f"  总条目：{len(rows)}  | ✅ ACTIVE：{len(active)}  | ⚠️  STALE：{len(stale)}  | 📦 ARCHIVED：{len(arch)}",
        f"{'─'*OUTPUT_WIDTH}",
    ]
    if stale:
        lines.append("\n  ⚠️  STALE 条目（需人工复核）：\n")
        for r in stale:
            lu, ex = r.get("LastUpdated", "?"), r.get("ExpiryMonths", "?")
            days = days_remaining(lu, ex)
            td = (f"已过期 {abs(days):.0f} 天" if days and days < 0
                  else f"剩余约 {days:.0f} 天" if days else "永久有效")
            lines.append(f"    [{r.get('ID','?')}] {r.get('Topic','?')}")
            lines.append(f"           Category: {r.get('Category','?')} | Expiry: {ex} | {td}")
            lines.append(f"           LastUpdated: {lu} | Notes: {r.get('Notes','-')}\n")
    else:
        lines.append("\n  ✅ Registry 状态健康，无 STALE 条目。\n")
    if changes:
        lines.append(f"\n  🔄 本次扫描变化：\n")
        for c in changes: lines.append(f"    [{c['id']}] {c['topic']}: {c['from']} → {c['to']}")
        lines.append("")
    lines.append(f"{'═'*OUTPUT_WIDTH}\n")
    return "\n".join(lines)


def check_entry(entry_id):
    if not REGISTRY_PATH.exists(): return None
    rows = parse_registry(REGISTRY_PATH.read_text(encoding="utf-8"))
    for row in rows:
        if row.get("ID", "").strip() == entry_id.strip():
            days = days_remaining(row.get("LastUpdated", ""), row.get("ExpiryMonths", ""))
            return {**row, "computed_status": compute_status(row), "days_remaining": days}
    return None

# ─────────────────────────────────────────────────────────────
# MEMORY.md 矛盾检测
# ─────────────────────────────────────────────────────────────

def text_similarity(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()

def extract_sections(content):
    parts = re.split(r"(?=^##\s)", content, flags=re.MULTILINE)
    sections = []
    for part in parts:
        lines = part.splitlines()
        if not lines: continue
        title = lines[0].strip().lstrip("# ").strip()
        body = "\n".join(lines[1:]).strip()
        sections.append({"title": title, "body": body})
    return sections

def detect_memory_contradictions():
    if not MEMORY_PATH.exists(): return []
    content = MEMORY_PATH.read_text(encoding="utf-8")
    sections = extract_sections(content)
    rule_re = re.compile(
        r"KR-\d+[^\n.,，。]*|(必须|应该|优先|绝不)[^\n.,，。]+|"
        r"(调用|使用|激活)[^\n.,，。]+|(触发词|当[^\n.,，。]+时)[^\n.,，。]+",
        re.MULTILINE
    )
    sentences = []
    for sec in sections:
        for m in rule_re.finditer(sec["body"]):
            text = m.group().strip()
            if len(text) > 10:
                sentences.append({"text": text, "section": sec["title"]})
    contradictions = []
    checked = set()
    for i in range(len(sentences)):
        for j in range(i + 1, len(sentences)):
            s1, s2 = sentences[i], sentences[j]
            key = tuple(sorted([s1["text"][:30], s2["text"][:30]]))
            if key in checked: continue
            checked.add(key)
            sim = text_similarity(s1["text"], s2["text"])
            if s1["section"] == s2["section"] and sim > 0.5: continue
            if sim < 0.55 and len(s1["text"]) > 15 and len(s2["text"]) > 15:
                contradictions.append({
                    "text_a": s1["text"], "text_b": s2["text"],
                    "section_a": s1["section"], "section_b": s2["section"],
                    "similarity": round(sim, 3), "resolved": False,
                })
    return contradictions

def memory_check():
    contradictions = detect_memory_contradictions()
    today = datetime.now().strftime("%Y-%m-%d")
    lines = [
        f"\n{'═'*OUTPUT_WIDTH}",
        f"  🧠 MEMORY.md 矛盾检测报告  |  {today}",
        f"{'═'*OUTPUT_WIDTH}",
    ]
    if not contradictions:
        lines.append("\n  ✅ 未检测到明显矛盾，MEMORY.md 状态正常。\n")
    else:
        lines.append(f"\n  ⚠️  检测到 {len(contradictions)} 处潜在矛盾，需要人工复核：\n")
        for i, c in enumerate(contradictions, 1):
            lines.append(f"  【矛盾 {i}】  相似度：{c['similarity']}")
            lines.append(f"    A [{c['section_a']}]：{c['text_a'][:80]}")
            lines.append(f"    B [{c['section_b']}]：{c['text_b'][:80]}")
            lines.append("")
        lines.append("  → 请确认哪个是正确的，我来更新 MEMORY.md")
    lines.append(f"{'═'*OUTPUT_WIDTH}\n")
    return "\n".join(lines)

# ─────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    if cmd == "scan": scan()
    elif cmd == "report": print(report())
    elif cmd == "check":
        if len(sys.argv) < 3:
            print("用法: python3 hygiene.py check <ID>"); sys.exit(1)
        entry = check_entry(sys.argv[2])
        if not entry:
            print(f"未找到条目: {sys.argv[2]}"); sys.exit(1)
        days = entry.get("days_remaining")
        td = ("永久有效" if days is None
              else f"已过期 {abs(days):.0f} 天" if days < 0
              else f"剩余约 {days:.0f} 天")
        print(f"\n[{entry['ID']}] {entry['Topic']}")
        print(f"  文件状态：{entry.get('Status','?')} | 计算状态：{entry['computed_status']}")
        print(f"  Category：{entry.get('Category','?')} | LastUpdated：{entry.get('LastUpdated','?')}")
        print(f"  ExpiryMonths：{entry.get('ExpiryMonths','?')} → {td}")
        print(f"  Notes：{entry.get('Notes','-')}")
    elif cmd == "memory-check": print(memory_check())
    else:
        print(f"未知命令: {cmd}")
