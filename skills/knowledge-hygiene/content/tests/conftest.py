# tests/conftest.py
"""
clean-pytest 规范：
- Fake 替代 Mock（隔离外部依赖）
- AAA 注释明确标注 Arrange/Act/Assert
- 依赖注入 Fixtures
- 参数化覆盖多情景
"""
import pytest
from datetime import datetime

TODAY = datetime.now().strftime("%Y-%m-%d")

# ─────────────────────────────────────────────────────────────
# Fixtures — 返回 Registry 字符串内容（纯数据，不含文件操作）
# ─────────────────────────────────────────────────────────────

@pytest.fixture
def multi_table_registry() -> str:
    """标准多章节 Registry（4章节，8条数据）"""
    return f"""| ID | Category | Topic | LastUpdated | ExpiryMonths | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| KR-T1 | 教训 | 有效教训A | {TODAY} | 6 | ACTIVE | 测试教训 |
| KR-T2 | 教训 | 永久教训 | {TODAY} | 永久 | ACTIVE | 永久不过期 |
| KR-T3 | 教训 | 已过期教训 | 2020-01-01 | 1 | ACTIVE | 应变STALE |

## 第二章节

| ID | Category | Topic | LastUpdated | ExpiryMonths | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| KR-T4 | 规则 | 第二章规则A | {TODAY} | 永久 | ACTIVE | 第二章永久 |
| KR-T5 | 规则 | 第二章过期规则 | 2020-01-01 | 1 | ACTIVE | 应变STALE |

## 数据源

| ID | Category | Topic | LastUpdated | ExpiryMonths | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| KR-T6 | 数据 | 天数格式 | 2020-01-01 | 1天 | ACTIVE | 应变STALE |
| KR-T7 | 数据 | 归档数据 | 2020-01-01 | 1 | ARCHIVED | 归档不变 |
"""


@pytest.fixture
def dupe_id_registry() -> str:
    """重复 ID 场景（模拟文件损坏）"""
    return f"""| ID | Category | Topic | LastUpdated | ExpiryMonths | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| KR-D1 | 教训 | 重复IDA | {TODAY} | 永久 | ACTIVE | A版本 |
| KR-D1 | 教训 | 重复IDB | {TODAY} | 永久 | ACTIVE | B版本应覆盖A |
| KR-D2 | 规则 | 第二章条目 | {TODAY} | 永久 | ACTIVE | 第二章唯一 |

## 第二章节

| ID | Category | Topic | LastUpdated | ExpiryMonths | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| KR-D3 | 数据 | 第二章数据 | {TODAY} | 永久 | ACTIVE | 第二章数据 |
"""


@pytest.fixture
def expired_and_active_registry() -> str:
    """混合过期/活跃 Registry（用于幂等性测试）"""
    return f"""| ID | Category | Topic | LastUpdated | ExpiryMonths | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| KR-E1 | 数据 | 过期数据A | 2020-01-01 | 1 | ACTIVE | 应变STALE |
| KR-E2 | 教训 | 活跃教训 | {TODAY} | 永久 | ACTIVE | 永久ACTIVE |
"""
