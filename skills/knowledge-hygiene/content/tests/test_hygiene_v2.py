#!/usr/bin/env python3
"""
test_hygiene_v2.py — hygiene.py write_registry 回归测试套件
覆盖：幂等性 / 多表保护 / 位置漂移 / Read-back 验证
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import re
import hygiene
from hygiene import COLS, write_registry, parse_registry

# ── 测试辅助 ──────────────────────────────────────────────────────────

def make_table(n_rows, n_tables=1, id_prefix="KR"):
    """生成 N 行 × M 表的 Registry 内容字符串。"""
    data = "| " + " | ".join(COLS) + " |\n"
    data += "| " + " | ".join("---" for _ in COLS) + " |\n"
    for i in range(n_rows):
        data += f"| {id_prefix}-{i:03d} | 分类 | 主题{i} | 2026-04-10 | 3 | ACTIVE | 测试 |\n"
    tables = [data] * n_tables
    header = "# Registry Test\n"
    sections = [f"\n## Section {i}\n" for i in range(1, n_tables + 1)]
    return header + "".join(s + t for s, t in zip(sections, tables))

def make_rows(n=5, id_prefix="KR"):
    return [
        {"ID": f"{id_prefix}-{i:03d}", "Category": "分类", "Topic": f"主题{i}",
         "LastUpdated": "2026-04-10", "ExpiryMonths": "3", "Status": "ACTIVE", "Notes": "测试"}
        for i in range(n)
    ]

# ── 测试 1：幂等性 ─────────────────────────────────────────────────────
def test_idempotent_no_change():
    """写入相同数据两次，第二次不得修改文件（幂等 guard）。"""
    content = make_table(5, n_tables=1)
    rows = make_rows(5)
    rows[0] = {"ID":"KR-000","Category":"分类","Topic":"主题0",
                "LastUpdated":"2026-04-10","ExpiryMonths":"3","Status":"ACTIVE","Notes":"测试"}

    c1 = write_registry(content, rows)
    c2 = write_registry(c1, rows)
    assert c1 == c2, f"幂等失败：两次写入结果不同！\n第1次：{len(c1)}行\n第2次：{len(c2)}行"
    print("  ✓ 幂等性测试通过")

# ── 测试 2：多表保护（核心 bug 修复验证）────────────────────────────────
def test_multi_table_protection():
    """历史文件有 4 个重复表，写入后只保留 1 个表（其余表数据区清空）。"""
    content = make_table(5, n_tables=4)
    rows = make_rows(5)

    result = write_registry(content, rows)

    table_count = len(re.findall(r"^\| ID \|", result, re.MULTILINE))
    assert table_count == 4, f"表头数量应保持4个（只清数据区，不删表头），实际：{table_count}"

    # 检查第一表数据 = 新数据，其余表数据区为空（只剩表头+分隔线）
    data_blocks = re.split(r"^\| ID \|", result, flags=re.MULTILINE)
    first_data = data_blocks[1].split("| --- |")[1].split("| --- |")[0] if len(data_blocks) > 1 else ""
    assert "KR-004" in first_data, f"第一表应包含新数据（含 KR-004），实际前100字：{first_data[:100]}"

    # 其余表数据区应为空（或只有空行）
    for i, block in enumerate(data_blocks[2:], start=2):
        parts = block.split("| --- |")
        if len(parts) < 2:
            continue
        data_section = parts[1]
        has_kr = any(f"KR-{j:03d}" in data_section for j in range(5))
        assert not has_kr, f"第{i}个表的数据区应为空，实际：{data_section[:80]}"

    print("  ✓ 多表保护测试通过（4→1 数据区 consolidation）")

# ── 测试 3：多表情况下 ID 集合相同则跳过写入 ──────────────────────────────
def test_idempotent_multi_table():
    """4 表文件 + 相同 ID 集合 → 幂等跳过，不触发任何写操作。"""
    content = make_table(5, n_tables=4)
    rows = make_rows(5)
    rows[0] = {"ID":"KR-000","Category":"分类","Topic":"主题0",
                "LastUpdated":"2026-04-10","ExpiryMonths":"3","Status":"ACTIVE","Notes":"测试"}

    c1 = write_registry(content, rows)
    c2 = write_registry(c1, rows)
    assert c1 == c2, "多表幂等失败"
    print("  ✓ 多表幂等测试通过")

# ── 测试 4：parse_registry 去重正确性 ─────────────────────────────────
def test_parse_deduplication():
    """同一 ID 在多处出现时只取第一个。"""
    content = make_table(5, n_tables=4)
    rows = parse_registry(content)
    ids = [r["ID"] for r in rows]
    assert len(ids) == len(set(ids)), f"有重复 ID：{ids}"
    assert len(ids) == 5, f"应为 5 条，去重后：{len(ids)} 条"
    print("  ✓ parse_registry 去重测试通过")

# ── 测试 5：parse_registry 完整恢复 ───────────────────────────────────
def test_parse_roundtrip():
    """写入 → 解析 → 数据完全一致（ID 集合不变）。"""
    content = make_table(5, n_tables=4)
    rows = make_rows(5)
    result = write_registry(content, rows)
    parsed = parse_registry(result)
    assert len(parsed) == 5, f"roundtrip 后应为 5 条，实际：{len(parsed)}"
    print("  ✓ roundtrip 测试通过")

# ── 测试 6：空文件保护 ─────────────────────────────────────────────────
def test_empty_file():
    content = "# Empty\n"
    rows = make_rows(3)
    result = write_registry(content, rows)
    assert result == content, "无表文件应直接返回，不写入"
    print("  ✓ 空文件保护测试通过")

# ── 运行全部测试 ───────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  hygiene.py v2 write_registry 回归测试")
    print("=" * 60)
    tests = [
        test_idempotent_no_change,
        test_multi_table_protection,
        test_idempotent_multi_table,
        test_parse_deduplication,
        test_parse_roundtrip,
        test_empty_file,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ {t.__name__}: 意外异常：{e}")
            failed += 1
    print()
    print(f"  结果：{passed} 通过 / {failed} 失败")
    print("=" * 60)
    sys.exit(0 if failed == 0 else 1)
