#!/opt/pylib/bin/python3
"""板块数据查询脚本"""
import sys
import argparse

try:
    import akshare as ak
except ImportError:
    print("错误：未安装 akshare，请运行 `uv pip install akshare`")
    sys.exit(1)


def industry_board():
    """行业板块涨跌榜"""
    try:
        df = ak.stock_board_industry_name_em()
        df = df.sort_values("涨跌幅", ascending=False)
        print(df.to_string(index=False))
    except Exception as e:
        print(f"获取行业板块失败: {e}")


def concept_board(keyword: str):
    """概念板块搜索"""
    try:
        df = ak.stock_board_concept_name_em()
        if keyword:
            df = df[df["板块名称"].str.contains(keyword, na=False)]
        print(df.to_string(index=False))
    except Exception as e:
        print(f"获取概念板块失败: {e}")


def sector_components(name: str):
    """板块成分股"""
    try:
        df = ak.stock_board_industry_cons_em(symbol=name)
        print(df.to_string(index=False))
    except Exception as e:
        print(f"获取成分股失败: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AKShare 板块查询")
    parser.add_argument("keyword", nargs="?", help="板块名称关键词")
    parser.add_argument("--concept", action="store_true", help="查询概念板块")
    parser.add_argument("--components", help="查询板块成分股")
    args = parser.parse_args()

    if args.components:
        sector_components(args.components)
    elif args.concept:
        concept_board(args.keyword or "")
    else:
        industry_board()