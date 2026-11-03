"""
长期经营资产扩张性支出比例 - 数据获取与计算脚本

用法:
    python scripts/fetch_and_calc.py <股票代码或公司简称>

示例:
    python scripts/fetch_and_calc.py 600309
    python scripts/fetch_and_calc.py 万华化学
"""

import sys
import re
import warnings
from datetime import datetime, date

warnings.filterwarnings("ignore")

try:
    import akshare as ak
    import pandas as pd
    import numpy as np
except ImportError as e:
    print(f"[错误] 缺少依赖库：{e}")
    print("请先安装：pip install akshare pandas numpy")
    sys.exit(1)


# ──────────────────────────────────────────────
# 工具函数
# ──────────────────────────────────────────────

def to_wan(value):
    """将原始数值转换为万元（假设原始单位为元）"""
    try:
        v = float(value)
        return round(v / 10000, 2)
    except (TypeError, ValueError):
        return None


def fmt_num(value, is_pct=False):
    """格式化数字显示"""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "—"
    if is_pct:
        return f"{value:.2f}%"
    return f"{value:,.2f}"


def fuzzy_match_col(df_cols, keywords):
    """
    从 DataFrame 列名中模糊匹配最佳列，
    keywords 为候选关键词列表，按优先级排列
    """
    for kw in keywords:
        for col in df_cols:
            if kw in str(col):
                return col
    return None


# ──────────────────────────────────────────────
# 股票代码解析
# ──────────────────────────────────────────────

def resolve_stock_code(query: str) -> tuple[str, str]:
    """
    输入代码或简称，返回 (股票代码, 公司简称)
    """
    query = query.strip()

    # 如果本身是6位数字代码
    if re.match(r"^\d{6}$", query):
        try:
            info = ak.stock_individual_info_em(symbol=query)
            name_row = info[info.iloc[:, 0] == "股票简称"]
            name = name_row.iloc[0, 1] if not name_row.empty else query
            return query, str(name)
        except Exception:
            return query, query

    # 否则尝试从名称搜索
    try:
        stock_list = ak.stock_info_a_code_name()
        matched = stock_list[stock_list["name"].str.contains(query, na=False)]
        if matched.empty:
            matched = stock_list[stock_list["code"].str.contains(query, na=False)]
        if matched.empty:
            print(f"[警告] 未能匹配到公司：{query}，请直接输入6位股票代码")
            sys.exit(1)
        code = matched.iloc[0]["code"]
        name = matched.iloc[0]["name"]
        return str(code), str(name)
    except Exception as e:
        print(f"[错误] 查询股票列表失败：{e}")
        sys.exit(1)


# ──────────────────────────────────────────────
# 数据获取 - 东方财富接口（更稳定）
# ──────────────────────────────────────────────

def fetch_cash_flow(code: str) -> pd.DataFrame:
    """获取年度现金流量表（东方财富）"""
    try:
        df = ak.stock_cash_flow_sheet_by_yearly_em(symbol=code)
        return df
    except Exception as e:
        print(f"[警告] 东方财富现金流量表获取失败：{e}，尝试新浪接口...")
        try:
            # 新浪接口备用
            symbol = ("sh" if code.startswith("6") else "sz") + code
            df = ak.stock_financial_report_sina(
                stock=symbol, symbol="现金流量表"
            )
            return df
        except Exception as e2:
            print(f"[错误] 现金流量表获取失败：{e2}")
            return pd.DataFrame()


def fetch_balance_sheet(code: str) -> pd.DataFrame:
    """获取年度资产负债表（东方财富）"""
    try:
        df = ak.stock_balance_sheet_by_yearly_em(symbol=code)
        return df
    except Exception as e:
        print(f"[警告] 东方财富资产负债表获取失败：{e}，尝试新浪接口...")
        try:
            symbol = ("sh" if code.startswith("6") else "sz") + code
            df = ak.stock_financial_report_sina(
                stock=symbol, symbol="资产负债表"
            )
            return df
        except Exception as e2:
            print(f"[错误] 资产负债表获取失败：{e2}")
            return pd.DataFrame()


# ──────────────────────────────────────────────
# 字段提取
# ──────────────────────────────────────────────

# 现金流量表字段映射（关键词列表，按优先级）
CF_FIELDS = {
    "cash_from_disposal": [
        "处置固定资产、无形资产和其他长期资产收回的现金净额",
        "处置长期资产收回现金",
        "处置固定资产收回",
        "收回处置长期资产",
    ],
    "cash_for_acquisition": [
        "购建固定资产、无形资产和其他长期资产支付的现金",
        "购建固定资产支付",
        "购置固定资产",
        "资本支出",
    ],
    "depreciation_fa": [
        "固定资产折旧、油气资产折耗、生产性生物资产折旧",
        "固定资产折旧",
        "折旧和摊销",
        "折旧",
    ],
    "amort_intangible": [
        "无形资产摊销",
        "摊销无形资产",
    ],
    "amort_lt_prepaid": [
        "长期待摊费用摊销",
        "长期待摊",
    ],
    "loss_disposal": [
        "处置固定资产、无形资产和其他长期资产的损失",
        "处置长期资产损失",
        "固定资产损失",
    ],
    "loss_scrap": [
        "固定资产报废损失",
        "报废损失",
        "固定资产盘亏",
    ],
}

# 资产负债表字段映射
BS_FIELDS = {
    "fa_net": [
        "固定资产",
        "固定资产净额",
        "固定资产净值",
    ],
    "intangible_net": [
        "无形资产",
    ],
    "lt_prepaid": [
        "长期待摊费用",
    ],
    "goodwill": [
        "商誉",
    ],
    "invest_property": [
        "投资性房地产",
    ],
    "productive_bio": [
        "生产性生物资产",
    ],
    "oil_gas": [
        "油气资产",
    ],
}


def extract_field(df: pd.DataFrame, keywords: list, date_col: str = None) -> dict:
    """
    从 DataFrame 中按关键词提取字段，返回 {日期: 值} 字典
    支持行式（每列为字段，每行为日期）和列式（每行为字段，每列为日期）两种格式
    """
    if df.empty:
        return {}

    # 东方财富接口：列为字段，行为日期，第一列通常是日期
    # 判断格式：如果第一列包含日期格式数据
    first_col = df.columns[0]
    first_vals = df[first_col].astype(str)

    date_pattern = re.compile(r"\d{4}-\d{2}-\d{2}")
    is_row_date = first_vals.str.match(r"\d{4}").any()

    if is_row_date:
        # 行式：每行是一个报告期，第一列是日期
        date_col_name = first_col
        col = fuzzy_match_col(df.columns.tolist(), keywords)
        if col is None:
            return {}
        result = {}
        for _, row in df.iterrows():
            date_str = str(row[date_col_name])[:10]
            val = row[col]
            try:
                result[date_str] = float(val) if val not in [None, "", "nan", "--"] else None
            except (ValueError, TypeError):
                result[date_str] = None
        return result
    else:
        # 列式：第一列是项目名，其余列是日期
        # 尝试匹配行（项目名）
        idx_col = df.columns[0]
        matched_row = None
        for kw in keywords:
            mask = df[idx_col].astype(str).str.contains(kw, na=False)
            if mask.any():
                matched_row = df[mask].iloc[0]
                break
        if matched_row is None:
            return {}
        result = {}
        for col in df.columns[1:]:
            date_str = str(col)[:10]
            if not re.match(r"\d{4}", date_str):
                continue
            val = matched_row[col]
            try:
                result[date_str] = float(val) if val not in [None, "", "nan", "--", "None"] else None
            except (ValueError, TypeError):
                result[date_str] = None
        return result


# ──────────────────────────────────────────────
# 核心计算
# ──────────────────────────────────────────────

def get_latest_n_years(all_dates: list, n: int = 5) -> list:
    """取最新 n 个年度日期（按年份，每年取12月31日数据）"""
    year_dates = {}
    for d in all_dates:
        try:
            dt = datetime.strptime(d[:10], "%Y-%m-%d")
            if dt.month == 12 and dt.day == 31:
                year_dates[dt.year] = d
        except ValueError:
            continue
    sorted_years = sorted(year_dates.keys(), reverse=True)[:n]
    return [year_dates[y] for y in sorted_years]


def compute_expansion_ratio(code: str, name: str, n_years: int = 5) -> None:
    """主计算函数：获取数据，计算，展示结果"""

    print(f"\n正在获取 {name}（{code}）的财务数据，请稍候...\n")

    cf_df = fetch_cash_flow(code)
    bs_df = fetch_balance_sheet(code)

    if cf_df.empty:
        print("[错误] 无法获取现金流量表数据")
        return
    if bs_df.empty:
        print("[错误] 无法获取资产负债表数据")
        return

    # 提取现金流量表字段
    cf_data = {}
    for field, keywords in CF_FIELDS.items():
        cf_data[field] = extract_field(cf_df, keywords)

    # 提取资产负债表字段
    bs_data = {}
    for field, keywords in BS_FIELDS.items():
        bs_data[field] = extract_field(bs_df, keywords)

    # 确定年度列表（取现金流量表中的年报日期）
    all_cf_dates = set()
    for field_data in cf_data.values():
        all_cf_dates.update(field_data.keys())

    selected_dates = get_latest_n_years(list(all_cf_dates), n=n_years)

    if not selected_dates:
        print("[错误] 未找到符合条件的年报数据（需要完整年度报告，即12月31日）")
        return

    print(f"已找到 {len(selected_dates)} 个年度报告：{', '.join(selected_dates)}\n")

    # 构建结果表
    rows = []
    for date_str in selected_dates:
        year = date_str[:4]

        # 当年现金流量数据（单位：元→万元）
        c1 = to_wan(cf_data["cash_from_disposal"].get(date_str))
        c2 = to_wan(cf_data["cash_for_acquisition"].get(date_str))
        c4 = to_wan(cf_data["depreciation_fa"].get(date_str))
        c5 = to_wan(cf_data["amort_intangible"].get(date_str))
        c6 = to_wan(cf_data["amort_lt_prepaid"].get(date_str))
        c7 = to_wan(cf_data["loss_disposal"].get(date_str))
        c8 = to_wan(cf_data["loss_scrap"].get(date_str))

        # (3) 长期经营资产净投资额 = (2) - (1)
        c3 = (c2 if c2 is not None else 0) - (c1 if c1 is not None else 0) \
            if (c2 is not None or c1 is not None) else None

        # (9) 扩张性资本支出 = (3) - (4) - (5) - (6) - (7) - (8)
        deductions = [c4, c5, c6, c7, c8]
        if c3 is not None:
            c9 = c3 - sum(d for d in deductions if d is not None)
        else:
            c9 = None

        # (10) 期初长期经营资产净额（取上一年年末数据）
        prev_year = str(int(year) - 1)
        prev_date = f"{prev_year}-12-31"
        bs_fields_10 = ["fa_net", "intangible_net", "lt_prepaid", "goodwill",
                        "invest_property", "productive_bio", "oil_gas"]
        c10_parts = []
        for bf in bs_fields_10:
            val = to_wan(bs_data[bf].get(prev_date))
            if val is not None:
                c10_parts.append(val)
        c10 = sum(c10_parts) if c10_parts else None

        # (11) 扩张性支出比例 = (9) / (10) × 100%
        if c9 is not None and c10 and c10 != 0:
            c11 = c9 / c10 * 100
        else:
            c11 = None

        rows.append({
            "date": date_str,
            "(1)": c1, "(2)": c2, "(3)": c3,
            "(4)": c4, "(5)": c5, "(6)": c6,
            "(7)": c7, "(8)": c8,
            "(9)": c9, "(10)": c10, "(11)": c11
        })

    # ──────────────────────────────────────────────
    # 输出 Markdown 表格
    # ──────────────────────────────────────────────

    date_headers = [r["date"] for r in rows]
    col_sep = " | "

    # 行定义
    row_defs = [
        ("(1)", "(1) 处置固定资产等收回的现金净额", False),
        ("(2)", "(2) 购建固定资产等支付的现金", False),
        ("(3)", "(3) 长期经营资产净投资额 (=(2)-(1))", False),
        ("(4)", "(4) 固定资产折旧、油气资产折耗、生产性生物资产折旧", False),
        ("(5)", "(5) 无形资产摊销", False),
        ("(6)", "(6) 长期待摊费用摊销", False),
        ("(7)", "(7) 处置固定资产、无形资产和其他长期资产的损失", False),
        ("(8)", "(8) 固定资产报废损失", False),
        ("(9)", "(9) 长期经营资产扩张性资本支出 (=(3)-(4)-…-(8))", False),
        ("(10)", "(10) 期初长期经营资产净额", False),
        ("(11)", "(11) 长期经营资产扩张性支出比例 (=(9)/(10)×100%)", True),
    ]

    # 标题行
    header_items = ["项目"] + date_headers
    separator = ["---"] + ["---:"] * len(date_headers)

    lines = []
    lines.append(f"\n## 表：{name}（{code}）投资活动现金流量分析\n")
    lines.append(f"金额单位：万元 &nbsp;&nbsp;&nbsp;&nbsp; 数据来源：AKShare &nbsp;&nbsp;&nbsp;&nbsp; 获取日期：{date.today()}\n")
    lines.append(col_sep.join(header_items))
    lines.append(col_sep.join(separator))

    for key, label, is_pct in row_defs:
        vals = [fmt_num(r[key], is_pct=is_pct) for r in rows]
        row_str = col_sep.join([label] + vals)
        lines.append(row_str)

    result_md = "\n".join(lines)
    print(result_md)

    # 保存到文件
    output_file = f"capital_expansion_{code}.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result_md)
    print(f"\n结果已保存至：{output_file}")


# ──────────────────────────────────────────────
# 入口
# ──────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        query = input("请输入股票代码或公司简称：").strip()
    else:
        query = sys.argv[1].strip()

    code, name = resolve_stock_code(query)
    print(f"已匹配：{name}（{code}）")
    compute_expansion_ratio(code, name, n_years=5)
