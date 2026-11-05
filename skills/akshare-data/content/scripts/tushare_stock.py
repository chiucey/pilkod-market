#!/opt/pylib/bin/python3
"""tushare 股票数据查询脚本

ts_code 格式：
  600000.SH  上海证券交易所（SSE）— 主板股票
  000001.SZ  深圳证券交易所（SZSE）— 主板/中小板
  830942.BJ  北京证券交易所（BSE）— 北交所股票
  00700.HK   香港证券交易所（HKEX）— 港股
"""
import sys
import argparse
import os

try:
    import tushare as ts
except ImportError:
    print("错误：未安装 tushare")
    sys.exit(1)

TOKEN = os.getenv("TUSHARE_TOKEN", "84ce99cb1834d03ce83ae4ffc192cd4feab1e838cdb89b8b5e731734")
pro = ts.pro_api(TOKEN)


def stock_basic():
    """股票列表"""
    try:
        df = pro.stock_basic(exchange="", list_status="L",
                             fields="ts_code,symbol,name,area,industry,list_date")
        print(f"共 {len(df)} 只上市股票\n")
        print(df.head(30).to_string(index=False))
    except Exception as e:
        print(f"查询失败: {e}")


def daily(symbol: str = "", start_date: str = "", end_date: str = ""):
    """日K线（未复权）

    - 每请求一次 ≈ 提取单个股票约23年历史
    - 基础积分：500次/分钟，6000条/次
    - 数据更新：交易日15:00~16:00入库
    - 停牌期间无数据
    - 支持多股票同时提取（逗号分隔）
    """
    if not symbol:
        symbol = "000001.SZ"
    # 默认近90日，避免一次拉取过多
    from datetime import datetime, timedelta
    if not end_date:
        end_date = datetime.now().strftime("%Y%m%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=90)).strftime("%Y%m%d")

    try:
        df = pro.daily(ts_code=symbol, start_date=start_date, end_date=end_date)
        if df.empty:
            print(f"未找到 {symbol} [{start_date}~{end_date}] 的数据（可能停牌或非交易日）")
            return
        print(f"【{symbol}】日K线  {start_date} ~ {end_date}  共{len(df)}条")
        print(f"字段：ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, vol, amount")
        print(df.to_string(index=False))
    except Exception as e:
        print(f"获取日K线失败: {e}")


def financials(symbol: str = ""):
    """财务指标"""
    if not symbol:
        symbol = "600519.SH"
    try:
        df = pro.fina_indicator_pd(ts_code=symbol)
        if df.empty:
            print(f"未找到 {symbol} 的财务数据")
            return
        cols = ["ts_code", "ann_date", "roe", "np小板", "gross_profit_margin", "debt_to_assets"]
        available = [c for c in cols if c in df.columns]
        print(df[available].head(5).to_string(index=False))
    except Exception as e:
        print(f"获取财务数据失败: {e}")


def hsgt_top(n: int = 10):
    """沪深港通资金流向（近7日汇总）"""
    from datetime import datetime, timedelta
    end = datetime.now().strftime("%Y%m%d")
    start = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")
    try:
        df = pro.moneyflow_hsgt(start_date=start, end_date=end, top_n=n)
        print("=== 沪深股通近7日资金流向 ===")
        print(f"日期范围：{start} ~ {end}\n")
        print(df.to_string(index=False))
        print("\n字段：north_money=北向净买入(万), south_money=南向净买入(万)")
    except Exception as e:
        print(f"获取失败: {e}")


def hk_hold():
    """港股通持股明细"""
    try:
        df = pro.hk_hold_top(ths_code="SH", top=10)
        print("=== 沪股通十大持股 ===")
        print(df.to_string(index=False))
    except Exception as e:
        print(f"获取港股通持股失败: {e}")


def sector_fund_flow(n: int = 50):
    """东方财富板块资金流向（行业+概念）

    - 单次最大 5000 条，可循环提取全部数据
    - 数据更新：每天盘后（15:00~16:00）
    - 需 ≥6000 积分
    - 参数 top：返回条数（行业/概念各半）
    """
    from datetime import datetime, timedelta
    end = datetime.now().strftime("%Y%m%d")
    start = (datetime.now() - timedelta(days=5)).strftime("%Y%m%d")

    try:
        df = pro.moneyflow_ind_dc(top=n, start_date=start, end_date=end)
        if df.empty:
            print(f"未找到 [{start}~{end}] 的板块资金流向数据")
            return

        cols_map = {}
        for c in df.columns:
            if "板块名称" in c or "name" in c.lower():
                cols_map[c] = "板块名称"
            elif "涨幅" in c or "change" in c.lower():
                cols_map[c] = "涨跌幅%"
            elif "主力" in c and "净额" in c:
                cols_map[c] = "主力净流入"
            elif "超大单" in c and "净额" in c:
                cols_map[c] = "超大单净流入"
            elif "超大单" in c and "净占比" in c:
                cols_map[c] = "超大单净占比%"
            elif "主力净额" in c and "占比" not in c:
                cols_map[c] = "主力净额"
            elif "主力占比" in c:
                cols_map[c] = "主力净占比%"
            elif "上涨" in c and "家" in c:
                cols_map[c] = "上涨家数"
            elif "代码" in c:
                cols_map[c] = "板块代码"

        df = df.rename(columns=cols_map)
        key_cols = ["板块名称", "涨跌幅%", "主力净流入", "主力净占比%", "上涨家数"]
        available = [c for c in key_cols if c in df.columns]
        show_cols = available + [c for c in df.columns if c not in available]

        print(f"=== 板块资金流向  [{start} ~ {end}]  共 {len(df)} 条 ===")
        print(f"字段说明：主力净流入=超大单+大单净流入合计，单位（元）")
        print(df[show_cols].head(n).to_string(index=False))
    except Exception as e:
        print(f"获取板块资金流向失败: {e}")


def research_report(report_type: str = "个股研报", ts_code: str = "", ind_name: str = "",
                   start_date: str = "", end_date: str = "", n: int = 20):
    """券商研究报告

    - 单次最大 1000 条，每天总量不限制
    - 数据增量更新：每天两次
    - 权限：需单独开权限（与积分无关）
    - 历史数据：从 2017-01-01 起
    - 参数 report_type：个股研报 / 行业研报
    """
    from datetime import datetime, timedelta
    if not end_date:
        end_date = datetime.now().strftime("%Y%m%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

    try:
        df = pro.research_report(
            start_date=start_date,
            end_date=end_date,
            report_type=report_type,
            ts_code=ts_code if ts_code else None,
            ind_name=ind_name if ind_name else None,
        )
        if df.empty:
            print(f"未找到 [{start_date}~{end_date}] 的研报数据（确认已开权限？）")
            return
        print(f"=== {report_type}  [{start_date}~{end_date}]  共 {len(df)} 条 ===")
        # 选取关键列
        cols = ["公告日期", "机构名称", "研报标题", "行业", "评级类别", "评级星级"]
        available = [c for c in cols if c in df.columns]
        rest = [c for c in df.columns if c not in available]
        print(df[available + rest].head(n).to_string(index=False))
    except Exception as e:
        print(f"获取研报失败: {e}")
        print("提示：本接口需单独开通权限，参见 https://tushare.pro/document/51")


def weekly(symbol: str = "", start_date: str = "", end_date: str = ""):
    """A股周线行情（未复权）

    - 单次最大 6000 行，总量不限制
    - 每周最后一个交易日更新
    - 需 ≥2000 积分
    - ts_code 和 trade_date 二选一
    """
    if not symbol:
        symbol = "000001.SZ"
    from datetime import datetime, timedelta
    if not end_date:
        end_date = datetime.now().strftime("%Y%m%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=730)).strftime("%Y%m%d")  # 默认近2年

    try:
        df = pro.weekly(ts_code=symbol, start_date=start_date, end_date=end_date)
        if df.empty:
            print(f"未找到 {symbol} [{start_date}~{end_date}] 的周线数据")
            return
        print(f"【{symbol}】周线行情  {start_date} ~ {end_date}  共{len(df)}条")
        print(f"字段：ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, vol, amount")
        print(df.to_string(index=False))
    except Exception as e:
        print(f"获取周线失败: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Tushare 股票数据（ts_code 格式：600000.SH / 000001.SZ / 830942.BJ / 00700.HK）")
    parser.add_argument("--symbol",    help="股票代码，含后缀，如 600519.SH、00700.HK（支持逗号多只）")
    parser.add_argument("--start",     help="开始日期 YYYYMMDD")
    parser.add_argument("--end",       help="结束日期 YYYYMMDD")
    parser.add_argument("--basic",     action="store_true", help="股票列表")
    parser.add_argument("--daily",     action="store_true", help="日K线（未复权）")
    parser.add_argument("--fin",       action="store_true", help="财务指标（需 --symbol）")
    parser.add_argument("--flow",      action="store_true", help="沪深港通资金流向（近7日）")
    parser.add_argument("--hk-hold",      action="store_true", help="港股通持股明细")
    parser.add_argument("--sector-flow",  action="store_true", help="板块资金流向（东方财富，需≥6000积分）")
    parser.add_argument("--report",       action="store_true", help="券商研究报告（需单独开权限）")
    parser.add_argument("--weekly",       action="store_true", help="A股周线行情（未复权，需≥2000积分）")
    parser.add_argument("--report-type",   default="个股研报",
                       help="研报类别：个股研报（默认）/ 行业研报")
    parser.add_argument("--inst",          help="券商名称（模糊匹配）")
    parser.add_argument("--ind",           help="行业名称")
    args = parser.parse_args()

    if args.basic:
        stock_basic()
    elif args.daily:
        daily(args.symbol, args.start, args.end)
    elif args.fin:
        financials(args.symbol)
    elif args.flow:
        hsgt_top()
    elif args.hk_hold:
        hk_hold()
    elif args.sector_flow:
        sector_fund_flow()
    elif args.report:
        research_report(
            report_type=args.report_type,
            ts_code=args.symbol or "",
            ind_name=args.ind or "",
            start_date=args.start or "",
            end_date=args.end or "",
            n=30,
        )
    elif args.weekly:
        weekly(args.symbol, args.start, args.end)
    else:
        print("用法:")
        print("  --basic                  股票列表")
        print("  --daily --symbol 600519.SH --start 20260101    日K线（未复权）")
        print("  --weekly --symbol 600519.SH --start 20240101    周线行情（需≥2000积分）")
        print("  --fin   --symbol 600519.SH                   财务指标")
        print("  --flow                                   沪深港通资金流向（近7日）")
        print("  --hk-hold                                港股通持股明细")
        print("  --sector-flow                            板块资金流向（需≥6000积分）")
        print("  --report              # 个股研报（默认）")
        print("  --report --report-type 行业研报           行业研报")
        print("  --report --report-type 个股研报 --ind 新能源  按行业筛选")
        print("  --report --report-type 个股研报 --inst 中金    按券商名称筛选")
        print("\nts_code 后缀：.SH(沪) .SZ(深) .BJ(北交所) .HK(港股)")
        print("注意：daily/weekly 为未复权数据；周线每周最后一个交易日更新；日线交易日15:00~16:00更新")