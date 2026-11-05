#!/usr/bin/env python3
"""
LOF基金套利分析技能主入口
核心功能：全市场LOF数据拉取、双向套利指标计算、高安全边际机会筛选
合规声明：数据源均为公开免费接口，仅供个人学习研究使用，请勿高频请求
"""

import sys
import json
import requests
import pandas as pd
import yaml
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# 全局请求配置，避免反爬
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://fund.eastmoney.com/",
    "Accept": "application/json, text/javascript, */*; q=0.01"
}
REQUEST_TIMEOUT = 10


def load_config() -> Dict:
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(__file__), '../config/settings.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_trade_date() -> str:
    """获取最近一个交易日日期（排除周末/节假日）"""
    now = datetime.now()
    if now.weekday() >= 5:
        offset = now.weekday() - 4
        trade_date = (now - timedelta(days=offset)).strftime("%Y-%m-%d")
    elif now.hour < 15:
        trade_date = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        trade_date = now.strftime("%Y-%m-%d")
    return trade_date


def get_all_lof_fund_list() -> pd.DataFrame:
    """
    获取全市场可交易LOF基金基础列表
    筛选规则：LOF型基金、排除封闭期、排除定开型
    Returns:
        pd.DataFrame: 基金代码、名称、类型、交易所等基础信息
    """
    try:
        # 天天基金网LOF基金列表接口
        url = "http://fund.eastmoney.com/data/rankhandler.aspx"
        params = {
            "op": "ph",
            "dt": "kf",
            "ft": "LOF",
            "rs": "",
            "gs": 0,
            "sc": "zzf",
            "st": "desc",
            "sd": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
            "ed": datetime.now().strftime("%Y-%m-%d"),
            "pi": 1,
            "pn": 500,  # 覆盖全市场300+LOF基金
            "f": "fundcode,name,type,jjjl,starlevel,enddate"
        }
        response = requests.get(url, params=params, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        # 解析返回数据
        data_text = response.text
        data_start = data_text.find("[")
        data_end = data_text.find("]") + 1
        fund_list = json.loads(data_text[data_start:data_end])

        # 格式化数据
        fund_data = []
        for fund in fund_list:
            fund_info = fund.split(",")
            fund_code = fund_info[0]
            fund_name = fund_info[1]
            fund_type = fund_info[2]
            # 区分交易所：深交所16开头，上交所50/51开头
            exchange = "SZSE" if fund_code.startswith("16") else "SHSE" if fund_code.startswith(("50", "51")) else "OTHER"
            if exchange == "OTHER":
                continue
            fund_data.append({
                "fund_code": fund_code,
                "fund_name": fund_name,
                "fund_type": fund_type,
                "exchange": exchange
            })

        return pd.DataFrame(fund_data)
    except Exception as e:
        print(f"获取LOF基金列表失败: {str(e)}", file=sys.stderr)
        return pd.DataFrame()


def get_fund_net_value(fund_code: str) -> Dict:
    """
    获取单个基金最新场外净值
    Args:
        fund_code: 基金代码
    Returns:
        Dict: 最新净值、净值日期、申赎状态
    """
    try:
        # 最新净值接口
        net_value_url = f"http://api.fund.eastmoney.com/f10/lsjz?fundCode={fund_code}&pageIndex=1&pageSize=1"
        nv_response = requests.get(net_value_url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
        nv_response.raise_for_status()
        nv_data = nv_response.json()

        if not nv_data.get("Data", {}).get("LSJZList"):
            return {}

        latest_nv = nv_data["Data"]["LSJZList"][0]
        net_value = float(latest_nv["DWJZ"]) if latest_nv["DWJZ"] else 0
        net_value_date = latest_nv["FSRQ"]

        # 基金申赎状态接口
        status_url = f"http://fund.eastmoney.com/pingzhongdata/{fund_code}.js"
        status_response = requests.get(status_url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
        status_response.raise_for_status()
        status_text = status_response.text

        # 解析申赎状态
        can_purchase = "申购状态:开放申购" in status_text
        can_redeem = "赎回状态:开放赎回" in status_text

        return {
            "net_value": net_value,
            "net_value_date": net_value_date,
            "can_purchase": can_purchase,
            "can_redeem": can_redeem
        }
    except Exception:
        return {}


def get_fund_exchange_price(fund_code: str, exchange: str) -> Dict:
    """
    获取单个基金场内实时价格、成交额
    Args:
        fund_code: 基金代码
        exchange: 交易所 SZSE/SHSE
    Returns:
        Dict: 场内最新价、昨收价、日均成交额
    """
    try:
        # 东方财富行情接口，深交所secid=0.代码，上交所secid=1.代码
        secid = f"0.{fund_code}" if exchange == "SZSE" else f"1.{fund_code}"
        price_url = f"https://push2.eastmoney.com/api/qt/stock/details/get?secid={secid}&fields=f43,f44,f60,f47,f8"
        price_response = requests.get(price_url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
        price_response.raise_for_status()
        price_data = price_response.json()

        if not price_data.get("data"):
            return {}

        data = price_data["data"]
        latest_price = float(data["f43"])/100 if data.get("f43") else 0  # 最新价
        close_price = float(data["f60"])/100 if data.get("f60") else 0  # 昨收价
        amount = float(data["f8"])/10000 if data.get("f8") else 0  # 今日成交额(万元)

        return {
            "exchange_price": latest_price if latest_price > 0 else close_price,
            "daily_amount": amount
        }
    except Exception:
        return {}


def get_full_lof_data(config: Dict) -> pd.DataFrame:
    """
    获取全市场LOF基金完整场内外数据
    Args:
        config: 配置字典
    Returns:
        pd.DataFrame: 完整的基金数据
    """
    # 1. 获取LOF基金列表
    fund_list_df = get_all_lof_fund_list()
    if fund_list_df.empty:
        raise Exception("未获取到LOF基金列表，请检查网络连接或数据源接口")

    # 2. 批量获取场内外数据
    full_data = []
    trade_date = get_trade_date()
    max_funds = config["data"]["max_analyze_funds"]

    for idx, row in fund_list_df.head(max_funds).iterrows():
        fund_code = row["fund_code"]
        # 获取场外净值与申赎状态
        nv_info = get_fund_net_value(fund_code)
        if not nv_info or nv_info["net_value"] <= 0:
            continue
        # 净值日期校验，仅保留最新交易日数据
        if nv_info["net_value_date"] != trade_date:
            continue
        # 获取场内价格与成交额
        price_info = get_fund_exchange_price(fund_code, row["exchange"])
        if not price_info or price_info["exchange_price"] <= 0:
            continue

        # 合并数据
        full_data.append({
            **row.to_dict(),
            **nv_info,
            **price_info,
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    return pd.DataFrame(full_data)


def calculate_arbitrage_indicators(df: pd.DataFrame, config: Dict) -> pd.DataFrame:
    """
    计算双向套利核心指标
    Args:
        df: 原始基金数据
        config: 配置字典
    Returns:
        pd.DataFrame: 新增套利指标的数据集
    """
    arbitrage_config = config["arbitrage"]

    # 核心指标计算
    df["premium_rate"] = (df["exchange_price"] - df["net_value"]) / df["net_value"] * 100
    df["discount_rate"] = (df["net_value"] - df["exchange_price"]) / df["net_value"] * 100

    # 溢价套利成本与安全边际（场外申购->场内卖出）
    premium_total_fee = arbitrage_config["purchase_fee"] + arbitrage_config["sell_fee"] + arbitrage_config["transfer_fee"]
    df["premium_safety_margin"] = df["premium_rate"] - premium_total_fee - arbitrage_config["premium_risk_buffer"]

    # 折价套利成本与安全边际（场内买入->场外赎回）
    discount_total_fee = arbitrage_config["buy_fee"] + arbitrage_config["redeem_fee"]
    df["discount_safety_margin"] = df["discount_rate"] - discount_total_fee - arbitrage_config["discount_risk_buffer"]

    # 套利方向标记
    df["arbitrage_direction"] = df.apply(
        lambda x: "溢价套利" if x["premium_safety_margin"] > 0 and x["can_purchase"]
        else "折价套利" if x["discount_safety_margin"] > 0 and x["can_redeem"]
        else "无套利机会", axis=1
    )

    return df


def filter_arbitrage_opportunities(df: pd.DataFrame, config: Dict) -> pd.DataFrame:
    """
    筛选高安全边际套利机会，执行硬门槛过滤
    Args:
        df: 含指标的基金数据
        config: 配置字典
    Returns:
        pd.DataFrame: 筛选后的套利机会
    """
    filter_config = config["filter"]

    # 基础硬门槛过滤
    filtered_df = df[
        # 流动性门槛：日均成交额达标，避免滑点与无法成交
        (df["daily_amount"] >= filter_config["min_daily_amount"])
        # 申赎状态过滤
        & ((df["can_purchase"] == True) | (df["can_redeem"] == True))
        # 排除净值异常
        & (df["net_value"] > 0)
        & (df["exchange_price"] > 0)
    ].copy()

    # 按套利方向筛选有效机会
    premium_opportunities = filtered_df[
        (filtered_df["arbitrage_direction"] == "溢价套利")
        & (filtered_df["premium_rate"] >= filter_config["min_premium_rate"])
    ]

    discount_opportunities = filtered_df[
        (filtered_df["arbitrage_direction"] == "折价套利")
        & (filtered_df["discount_rate"] >= filter_config["min_discount_rate"])
    ]

    # 合并结果，按安全边际降序排序
    result_df = pd.concat([premium_opportunities, discount_opportunities], ignore_index=True)
    result_df = result_df.sort_values(
        by=["premium_safety_margin", "discount_safety_margin"],
        ascending=[False, False]
    )

    # 保留核心字段
    result_df = result_df[[
        "fund_code", "fund_name", "fund_type", "exchange",
        "net_value", "net_value_date", "exchange_price",
        "premium_rate", "discount_rate",
        "premium_safety_margin", "discount_safety_margin",
        "arbitrage_direction", "daily_amount",
        "can_purchase", "can_redeem", "analysis_time"
    ]]

    return result_df


def run(input_data: Optional[Dict] = None) -> Dict:
    """
    Skill核心执行入口，供Minimax Agent调用
    Args:
        input_data: 可选入参，支持自定义参数：
            - min_premium_rate: 自定义最低溢价率阈值
            - min_discount_rate: 自定义最低折价率阈值
            - max_analyze_funds: 最大分析基金数量
            - arbitrage_direction: 套利方向，可选 premium/discount/both
    Returns:
        Dict: 标准化执行结果
    """
    try:
        # 1. 加载配置并合并自定义参数
        config = load_config()
        input_data = input_data or {}

        # 自定义参数覆盖
        if "min_premium_rate" in input_data:
            config["filter"]["min_premium_rate"] = float(input_data["min_premium_rate"])
        if "min_discount_rate" in input_data:
            config["filter"]["min_discount_rate"] = float(input_data["min_discount_rate"])
        if "max_analyze_funds" in input_data:
            config["data"]["max_analyze_funds"] = int(input_data["max_analyze_funds"])

        # 2. 获取全市场LOF完整数据
        full_df = get_full_lof_data(config)
        if full_df.empty:
            return {
                "status": "error",
                "data": None,
                "message_for_user": "未获取到有效LOF基金数据，请检查网络连接，或确认数据源接口正常。"
            }

        # 3. 计算套利指标
        indicator_df = calculate_arbitrage_indicators(full_df, config)

        # 4. 筛选套利机会
        opportunities_df = filter_arbitrage_opportunities(indicator_df, config)

        # 5. 结果保存
        output_dir = config["output"]["directory"]
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"lof_arbitrage_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        opportunities_df.to_excel(output_file, index=False)

        # 6. 构建返回结果
        result_data = {
            "analysis_base_info": {
                "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "latest_trade_date": get_trade_date(),
                "total_funds_analyzed": len(full_df),
                "valid_opportunities_count": len(opportunities_df),
                "premium_opportunities_count": len(opportunities_df[opportunities_df["arbitrage_direction"] == "溢价套利"]),
                "discount_opportunities_count": len(opportunities_df[opportunities_df["arbitrage_direction"] == "折价套利"])
            },
            "filter_config_used": config["filter"],
            "arbitrage_config_used": config["arbitrage"],
            "arbitrage_opportunities": opportunities_df.to_dict(orient="records")
        }

        return {
            "status": "success",
            "data": result_data,
            "message_for_user": f"LOF基金套利分析完成！本次共分析{len(full_df)}只可交易LOF基金，筛选出{len(opportunities_df)}个有效套利机会（溢价套利{len(opportunities_df[opportunities_df['arbitrage_direction'] == '溢价套利'])}个，折价套利{len(opportunities_df[opportunities_df['arbitrage_direction'] == '折价套利'])}个），详细结果已保存至：{output_file}"
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "message_for_user": f"LOF分析执行失败：{str(e)}"
        }


if __name__ == "__main__":
    # 命令行执行入口
    if not sys.stdin.isatty():
        input_json = sys.stdin.read()
        input_data = json.loads(input_json) if input_json else {}
    else:
        input_data = {}

    output = run(input_data)
    print(json.dumps(output, ensure_ascii=False))
