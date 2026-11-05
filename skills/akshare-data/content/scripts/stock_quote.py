#!/opt/pylib/bin/python3
"""股票行情查询脚本"""
import sys
import argparse
import pandas as pd

try:
    import akshare as ak
except ImportError:
    print("错误：未安装 akshare，请运行 `uv pip install akshare`")
    sys.exit(1)


def get_stock_code(name: str) -> str:
    """通过股票名称模糊匹配代码（简化版）"""
    try:
        df = ak.stock_zh_a_spot_em()
        match = df[df["名称"] == name]
        if match.empty:
            # 尝试模糊匹配
            match = df[df["名称"].str.contains(name, na=False)]
        if match.empty:
            return name  # 直接当作代码使用
        return match.iloc[0]["代码"]
    except Exception:
        return name


def quote(name: str):
    """实时行情"""
    code = get_stock_code(name)
    try:
        df = ak.stock_zh_a_spot_em()
        row = df[df["代码"] == code]
        if row.empty:
            row = df[df["名称"] == name]
        if row.empty:
            print(f"未找到股票: {name}")
            return
        r = row.iloc[0]
        print(f"【{r['名称']}】代码: {r['代码']}")
        print(f"最新价: {r['最新价']}  涨跌幅: {r['涨跌幅']}%  涨跌额: {r['涨跌额']}")
        print(f"今开: {r['今开']}  最高: {r['最高']}  最低: {r['最低']}")
        print(f"成交量: {r['成交量']}  成交额: {r['成交额']}")
        print(f"市盈率: {r['市盈率']}  市净率: {r['市净率']}  总市值: {r['总市值']}")
    except Exception as e:
        print(f"查询失败: {e}")


def history(name: str):
    """历史 K 线"""
    code = get_stock_code(name)
    try:
        df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")
        print(df.tail(30).to_string(index=False))
    except Exception as e:
        print(f"获取历史数据失败: {e}")


def fund_flow(name: str):
    """资金流向"""
    code = get_stock_code(name)
    try:
        df = ak.stock_individual_fund_flow(stock=code)
        print(df.to_string(index=False))
    except Exception as e:
        print(f"获取资金流向失败: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AKShare 股票行情查询")
    parser.add_argument("name", help="股票名称或代码")
    parser.add_argument("--hist", action="store_true", help="历史 K 线")
    parser.add_argument("--fund", action="store_true", help="资金流向")
    args = parser.parse_args()

    if args.hist:
        history(args.name)
    elif args.fund:
        fund_flow(args.name)
    else:
        quote(args.name)