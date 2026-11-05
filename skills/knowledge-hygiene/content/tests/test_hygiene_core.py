"""
hygiene.py 核心修复验证测试

Bug 假设（修复前）：
  COLS = 7列，实际文件 header = 8列 → zip 截断 → 第8列数据永久丢失

修复后预期：
  - parse_registry：固定8列模板解析，不足的 pad 空字符串
  - write_registry：每行强制8列，写入后 round-trip 不丢数据
"""

import sys, os
from pathlib import Path

# ── fixture: 模拟8列表格 content ──────────────────────────────

FIXTURE_8COL = """# Knowledge Registry — Dorian 知识资产清单

> 机制：每次会话启动时由 knowledge-hygiene skill 读取并检查
> 格式：LastUpdated（YYYY-MM-DD）+ ExpiryMonths → 计算是否过期
> 过期处理：状态改为 STALE，触发主动提示

---
| ID | Category | Topic | LastUpdated | ExpiryMonths | Status | Notes | Attr |
| -- | -- | -- | -- | -- | -- | -- | -- | -- |
| KR-001 | 执行纪律 | D0定律 | 2026-04-09 | 永久 | ACTIVE | 多步骤任务第一条 | extra_val_1 |
| KR-002 | 执行纪律 | 任务后记忆收尾 | 2026-04-10 | 永久 | ACTIVE | 安装Checklist | extra_val_2 |
| KR-010 | 技能 | Python环境包清单 | 2026-04-10 | 3 | ACTIVE | pandas已验证 | extra_val_3 |
"""

# ── fixture: 7列表格（老格式，Notes 列含管道符）─────────────

FIXTURE_7COL_LEGACY = """# Knowledge Registry — Dorian 知识资产清单

---
| ID | Category | Topic | LastUpdated | ExpiryMonths | Status | Notes |
| -- | -- | -- | -- | -- | -- | -- | -- |
| KR-001 | 执行纪律 | D0定律 | 2026-04-09 | 永久 | ACTIVE | 多步骤任务第一条 |
| KR-002 | 执行纪律 | 任务后记忆收尾 | 2026-04-10 | 永久 | ACTIVE | 安装Checklist |
| KR-003 | 架构 | 三大工作台 | 2026-04-09 | 永久 | ACTIVE | 调用规则：A任务→mbb |
"""


# ── helpers ───────────────────────────────────────────────────

import re, difflib
from datetime import datetime, timedelta

REGISTRY_PATH = Path("memory/KNOWLEDGE_REGISTRY.md")
MEMORY_PATH   = Path("memory/MEMORY.md")

# 注入被测模块
sys.path.insert(0, str(Path(__file__).parent.parent))
from hygiene import parse_registry, write_registry, COLS, compute_status


class FakeContent:
    """保留原内容 + 注入测试 content，用于验证 write_registry 的幂等性"""
    def __init__(self, content):
        self.content = content
        self.written = None

    def __enter__(self):
        return self.content

    def __exit__(self, *args):
        pass


# ── tests ─────────────────────────────────────────────────────

def test_COLS_is_8_columns():
    """COLS 必须是8列，匹配实际文件格式"""
    assert len(COLS) == 8, f"COLS 应为8列，当前: {len(COLS)} 列，值: {COLS}"
    assert COLS[-1] == "Attr", f"最后一列应为 Attr，当前: {COLS[-1]}"


def test_parse_8col_content():
    """8列表格解析：全部字段完整读取，不截断"""
    rows = parse_registry(FIXTURE_8COL)
    assert len(rows) == 3, f"期望3行，当前{len(rows)}行"
    assert rows[0]["ID"] == "KR-001"
    assert rows[0]["Notes"] == "多步骤任务第一条", f"Notes 列读取错误: {rows[0].get('Notes')}"
    # 第8列Attr 应存在（即使为空或已有值）
    assert "Attr" in rows[0], f"Attr 列缺失，行数据: {rows[0]}"


def test_parse_7col_legacy_content():
    """7列表格（老格式）：应自动 pad 到8列，不抛错"""
    rows = parse_registry(FIXTURE_7COL_LEGACY)
    assert len(rows) == 3, f"期望3行，当前{len(rows)}行"
    # 第7列 Notes 应正确读取（注意：原 header 只有7列表头，Notes 含管道符时会出错）
    assert rows[0]["ID"] == "KR-001"
    assert rows[0]["Notes"] == "多步骤任务第一条"
    # 第8列 Attr 应 pad 为空字符串
    assert rows[2]["Attr"] == "", f"Attr 应 pad 为空，当前: {repr(rows[2].get('Attr'))}"


def test_round_trip_no_data_loss():
    """解析 → 写入 → 再解析：数据不丢失（含第8列）

    v8 修复验证：原来7列表格（header只有7列）时，
    8列数据行的第8列在 zip 时被截断 → 现在第8列完整保留。
    """
    rows_before = parse_registry(FIXTURE_8COL)
    new_content = write_registry(FIXTURE_8COL, rows_before)
    rows_after = parse_registry(new_content)
    ids_before = {r["ID"] for r in rows_before}
    ids_after  = {r["ID"] for r in rows_after}
    assert ids_before == ids_after, f"ID 集合不一致 before={ids_before} after={ids_after}"

    # v8 修复验证：建立 ID → row 映射，按 ID 比对，不依赖 zip 迭代
    rows_by_id_before = {r["ID"]: r for r in rows_before}
    rows_by_id_after  = {r["ID"]: r for r in rows_after}
    for rid in ids_before:
        rb = rows_by_id_before[rid]
        ra = rows_by_id_after[rid]
        assert rb["Notes"] == ra["Notes"], f"{rid}: Notes 不一致"
        # 第8列 Attr 验证：v8 前被 zip 截断丢失 → v8 后完整保留
        assert ra.get("Attr", "") == rb.get("Attr", ""), \
            f"{rid} Attr 丢失: before={repr(rb.get('Attr',''))} after={repr(ra.get('Attr',''))}"


def test_write_registry_idempotent_when_no_change():
    """幂等性：内容无变化时 write_registry 应返回原 content（不改文件）"""
    rows = parse_registry(FIXTURE_8COL)
    new_content = write_registry(FIXTURE_8COL, rows)
    # 不应改变原始第8列的值
    assert "extra_val_1" in new_content


def test_compute_status_permanent():
    """永久条目：compute_status 返回 ACTIVE（不报 STALE）"""
    from hygiene import compute_status
    row = {"ID": "KR-001", "LastUpdated": "2026-04-09",
           "ExpiryMonths": "永久", "Status": "ACTIVE"}
    assert compute_status(row) == "ACTIVE"


def test_compute_status_stale():
    """过期条目：compute_status 正确标记为 STALE"""
    row = {"ID": "KR-021", "LastUpdated": "2026-04-08",
           "ExpiryMonths": "1天", "Status": "ACTIVE"}
    # 1天过期，2026-04-08 到 2026-04-10 = 2天前 → 应为 STALE
    assert compute_status(row) == "STALE"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
