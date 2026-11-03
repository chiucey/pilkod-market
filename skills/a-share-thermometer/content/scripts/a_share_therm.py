import argparse
import akshare as ak
import pandas as pd

from datetime import date
from dateutil.relativedelta import relativedelta

def get_index_temperature(index_code: str = "沪深300") -> float:
    try:
        # 获取十年前的日期
        ten_years_ago = date.today() - relativedelta(years=10)

        # 指数估值
        df = ak.stock_index_pe_lg(index_code)

        # PE指标
        metric = "滚动市盈率"
        
        # 数据清洗
        df["日期"] = pd.to_datetime(df["日期"])
        df = df[(df["日期"] >= pd.to_datetime(ten_years_ago)) & (df[metric] > 0)].sort_values("日期")
        
        if len(df) < 250:
            raise ValueError("数据不足")
        
        # 计算温度
        latest_pe = df[metric].iloc[-1]
        pectile_pe = df[metric].rank(pct=True)[df[metric] == latest_pe]
        temperature = pectile_pe.mean() * 100

        print(f"指数：{index_code}")
        print(f"当前PE(TTM)：{latest_pe:.2f}")
        print(f"温度：{temperature:.1f}\n")
        return round(temperature, 1)

    except Exception as e:
        print(f"失败：{e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", default="沪深300", help="指数名称 如：沪深300、上证50等")
    args = parser.parse_args()
    get_index_temperature(args.index)