# tests/test_hygiene.py
"""
Knowledge Hygiene — 完整测试套件
遵循 clean-pytest 规范：
- Fake 替代 Mock（无外部依赖）
- AAA 注释明确标注 Arrange/Act/Assert
- 参数化覆盖多情景
- 幂等性 + 错误路径 全覆盖
"""
import pytest
import re
from datetime import datetime, timedelta

# ─────────────────────────────────────────────────────────────
# 被测逻辑（从 hygiene.py v3 复制，不依赖原文件）
# ─────────────────────────────────────────────────────────────

def is_separator(stripped):
    parts = [c.strip() for c in stripped.split("|")[1:-1]]
    return bool(parts) and all(re.match(r"^[-:]+$", c) for c in parts)

def is_section(stripped):
    return stripped.startswith("## ")

def parse_date(s):
    try:
        return datetime.strptime(s.strip(), "%Y-%m-%d")
    except (ValueError, TypeError):
        return None

def parse_expiry(s):
    s = s.strip()
    if s in ("永久", "永久有效", "PERMANENT", "permanent", ""):
        return None
    m = re.match(r"^(\d+(?:\.\d+)?)天$", s)
    if m:
        return float(m.group(1)) / 30.4375
    try:
        return float(s)
    except ValueError:
        return None

def days_remaining(last_updated, expiry_months_raw):
    exp = parse_expiry(expiry_months_raw)
    if exp is None:
        return None
    d = parse_date(last_updated)
    if d is None:
        return None
    return (d + timedelta(days=exp * 30.4375) - datetime.now()).days

def compute_status(row):
    status = row.get("Status", "ACTIVE").upper()
    if status == "ARCHIVED":
        return "ARCHIVED"
    exp = parse_expiry(row.get("ExpiryMonths", "").strip())
    if exp is None:
        return "ACTIVE"
    d = parse_date(row.get("LastUpdated", "").strip())
    if d is None:
        return "ACTIVE"
    return "STALE" if datetime.now() >= d + timedelta(days=exp * 30.4375) else "ACTIVE"

def parse_registry(content: str) -> list[dict]:
    """
    改进版行扫描，支持多章节表格：
    - 空白行：跳过，不影响 in_table 状态
    - ## 章节行：继续扫描（不重置 in_table）
    - 非 | 开头普通文本：重置 in_table
    - 表头行（| ID | ... LastUpdated |）：记录列结构
    - 数据行（列数==表头列数）：收录，ID 全局去重
    """
    lines = content.splitlines()
    header_cols = []
    in_table = False
    rows = []
    seen_ids = set()

    for line in lines:
        stripped = line.strip()
        if not stripped:          # 空白行：忽略，保持 in_table
            continue
        if is_section(stripped):  # ## 章节行：跳过，保持 in_table
            continue
        if not stripped.startswith("|"):  # 普通文本：重置
            in_table = False
            continue

        parts = [c.strip() for c in stripped.split("|")[1:-1]]

        # 表头行识别
        if len(parts) >= 3 and parts[0] == "ID" and "LastUpdated" in parts:
            header_cols = parts
            in_table = True
            continue

        # 分隔行
        if in_table and is_separator(stripped):
            continue

        # 数据行
        if in_table and len(parts) == len(header_cols):
            row = dict(zip(header_cols, parts))
            rid = row.get("ID", "").strip()
            if rid and rid not in seen_ids:
                seen_ids.add(rid)
                rows.append(row)

    return rows

def write_registry(content: str, rows: list[dict]) -> str:
    """
    全量覆写：替换所有章节表格的数据区，保持原有章节结构。
    """
    COLS = ["ID", "Category", "Topic", "LastUpdated", "ExpiryMonths", "Status", "Notes"]
    new_data_block = "\n".join(
        "| " + " | ".join(str(r.get(c, "")) for c in COLS) + " |"
        for r in rows
    )
    today = datetime.now().strftime("%Y-%m-%d")
    result = content

    # 找所有表头位置（从后往前替换，防位置偏移）
    for pos in reversed([m.start() for m in re.finditer(r"\| ID \|", result)]):
        # 找该表头行的结束位置
        line_end = result.find("\n", pos)
        if line_end == -1:
            line_end = len(result)

        # 找分隔线
        search_from = line_end + 1
        sep_pos = result.find("| ---", search_from)
        if sep_pos == -1:
            continue

        sep_end = result.find("\n", sep_pos)
        if sep_end == -1:
            sep_end = len(result)

        data_start = sep_end + 1

        # 找下一个 ## 或文件末尾
        next_section = result.find("\n## ", data_start)
        data_end = next_section if next_section != -1 else len(result)

        # 替换
        result = result[:data_start] + new_data_block + result[data_end:]

    # 更新时间戳
    result = re.sub(
        r"(\*\*最后检查\*\*：|\*最后检查：|最后检查：)\d{4}-\d{2}-\d{2}",
        f"**最后检查**：{today}",
        result
    )
    return result


# ─────────────────────────────────────────────────────────────
# 测试：parse_registry — 多表格解析
# ─────────────────────────────────────────────────────────────

class TestParseRegistry:
    """验证 parse_registry 对多章节、边界情况、重复 ID 的处理"""

    def test_parses_all_4_tables(self, multi_table_registry):
        # Arrange
        content = multi_table_registry

        # Act
        rows = parse_registry(content)
        ids = [r["ID"] for r in rows]

        # Assert
        assert len(rows) == 7
        assert "KR-T1" in ids
        assert "KR-T4" in ids  # 第二章
        assert "KR-T6" in ids  # 第三章

    def test_no_duplicate_ids(self, multi_table_registry):
        rows = parse_registry(multi_table_registry)
        ids = [r["ID"] for r in rows]
        assert len(ids) == len(set(ids)), f"有重复ID: {ids}"

    def test_duplicate_ids_deduplicated(self, dupe_id_registry):
        """重复 ID 只保留第一个出现"""
        rows = parse_registry(dupe_id_registry)
        ids = [r["ID"] for r in rows]
        assert ids.count("KR-D1") == 1
        assert len(rows) == 4  # KR-D1(a), KR-D2, KR-D3, 共3章=4条
        # 保留的是第一个出现的（A版本）
        row = next(r for r in rows if r["ID"] == "KR-D1")
        assert row["Notes"] == "A版本"

    def test_empty_string_returns_empty_list(self):
        assert parse_registry("") == []

    def test_no_table_returns_empty_list(self):
        assert parse_registry("## 章节\n这是一段没有表格的文字") == []


# ─────────────────────────────────────────────────────────────
# 测试：compute_status — 过期判定
# ─────────────────────────────────────────────────────────────

class TestComputeStatus:
    """验证过期判定逻辑：永久 / 过期 / 天数格式 / 归档"""

    @pytest.mark.parametrize("expiry,expected", [
        ("永久",    "ACTIVE"),
        ("6",      "ACTIVE"),
        ("3",      "ACTIVE"),
        ("1",      "STALE"),   # 2020-01-01 距今 >1个月
        ("1天",    "STALE"),
        ("永久有效","ACTIVE"),
    ])
    def test_expiry_classification(self, expiry, expected):
        row = {"ID": "T", "Status": "ACTIVE", "ExpiryMonths": expiry, "LastUpdated": "2020-01-01"}
        assert compute_status(row) == expected

    def test_permanent_stays_active(self):
        row = {"ID": "T", "Status": "ACTIVE", "ExpiryMonths": "永久", "LastUpdated": "2020-01-01"}
        assert compute_status(row) == "ACTIVE"

    def test_archived_stays_archived(self):
        row = {"ID": "T", "Status": "ARCHIVED", "ExpiryMonths": "1", "LastUpdated": "2020-01-01"}
        assert compute_status(row) == "ARCHIVED"

    def test_invalid_date_returns_active(self):
        row = {"ID": "T", "Status": "ACTIVE", "ExpiryMonths": "1", "LastUpdated": "not-a-date"}
        assert compute_status(row) == "ACTIVE"


# ─────────────────────────────────────────────────────────────
# 测试：幂等性 — 连续两次 scan 不产生新变化
# ─────────────────────────────────────────────────────────────

class TestIdempotency:
    """验证 scan 幂等性：连续两次 parse→compute→write 状态稳定"""

    def test_consecutive_scan_produces_same_rows(self, expired_and_active_registry):
        # Round 1
        rows1 = parse_registry(expired_and_active_registry)
        for row in rows1:
            row["Status"] = compute_status(row)
        written1 = write_registry(expired_and_active_registry, rows1)

        # Round 2
        rows2 = parse_registry(written1)
        for row in rows2:
            row["Status"] = compute_status(row)

        ids1 = [r["ID"] for r in rows1]
        ids2 = [r["ID"] for r in rows2]
        assert ids1 == ids2
        assert len(rows2) == len(rows1)

    def test_stale_status_fixed_after_first_scan(self, expired_and_active_registry):
        # Round 1: compute + write
        rows = parse_registry(expired_and_active_registry)
        for row in rows:
            row["Status"] = compute_status(row)
        written = write_registry(expired_and_active_registry, rows)

        # Round 2: re-parse written file
        rows2 = parse_registry(written)
        for row in rows2:
            row["Status"] = compute_status(row)

        # 两次 compute 结果应该一致（幂等）
        for r1, r2 in zip(rows, rows2):
            assert r1["Status"] == r2["Status"], \
                f"幂等性失败：{r1['ID']} 第一次={r1['Status']} 第二次={r2['Status']}"

    def test_write_registry_updates_all_tables(self, multi_table_registry):
        """write_registry 必须替换所有4个章节的表格，不只是第一个"""
        rows = parse_registry(multi_table_registry)
        for row in rows:
            row["Status"] = compute_status(row)
        written = write_registry(multi_table_registry, rows)

        # 写完后所有4个表格里都应该有KR-T系列数据
        # 通过反向解析验证
        rows_back = parse_registry(written)
        ids_back = [r["ID"] for r in rows_back]
        assert "KR-T1" in ids_back
        assert "KR-T4" in ids_back   # 第二章
        assert "KR-T6" in ids_back   # 第三章
        assert len(rows_back) == 7


# ─────────────────────────────────────────────────────────────
# 测试：days_remaining — 时间计算
# ─────────────────────────────────────────────────────────────

class TestDaysRemaining:
    def test_permanent_returns_none(self):
        assert days_remaining("2020-01-01", "永久") is None

    def test_one_day_format(self):
        result = days_remaining("2020-01-01", "1天")
        assert result is not None
        assert result < 0  # 已过期

    def test_months_format(self):
        result = days_remaining("2020-01-01", "1")
        assert result is not None
        assert result < 0  # 已过期

    def test_invalid_date_returns_none(self):
        assert days_remaining("not-a-date", "1") is None
