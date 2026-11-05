"""
比亚迪 2025 年年报分析测试脚本
股票代码: 002594.SZ
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# ============ 配置区域 - 请填入您的 Tushare Token ============
TUSHARE_TOKEN = "YOUR_TUSHARE_TOKEN_HERE"  # 请替换为您的 Tushare Token
API_URL = "https://api.tushare.pro"

# 比亚迪股票代码
TS_CODE = "002594.SZ"

# 字段配置 - 只请求必要的字段
FIELDS_CONFIG = {
    "income": "ts_code,end_date,total_revenue,revenue,oper_cost,operate_profit,total_profit,n_income,n_income_attr_p,sell_exp,admin_exp,fin_exp,rd_exp,invest_income,fv_value_chg_gain,oth_income,credit_impa_loss,assets_impair_loss",
    "balancesheet": "ts_code,end_date,total_assets,total_liab,total_hldr_eqy_exc_min_int,total_cur_assets,total_cur_liab,money_cap,goodwill,trad_asset,oth_equity_invest,oth_debt_invest,lt_eqt_invest,invest_real_estate,short_borrow,long_borrow,bonds_payable,lt_borrow,non_cur_liab_due_1y,notes_receiv,accounts_receiv,contract_assets,total_share,cap_rese,surplus_rese,undistr_porfit",
    "cashflow": "ts_code,end_date,n_cashflow_act,n_cashflow_inv_act,n_cash_flows_fnc_act,c_pay_acq_const_fiolta,c_recp_borrow,c_recp_cap_contrib,c_recp_sell_assets",
    "fina_indicator": "ts_code,end_date,profit_dedt"
}


def format_period(end_date):
    """格式化日期为中文报表期"""
    year = end_date[:4]
    month_day = end_date[4:]
    month_map = {
        "0331": "一季报",
        "0630": "半年报",
        "0930": "三季报",
        "1231": "年报"
    }
    return f"{year}年{month_map.get(month_day, '')}"


def to_yi(yuan_value):
    """元转亿元，保留2位小数"""
    if yuan_value is None:
        return None
    return round(yuan_value / 1e8, 2)


def calc_growth(current, previous):
    """计算增长率"""
    if previous is None or previous == 0:
        return None
    return round((current - previous) / abs(previous) * 100, 2)


def format_value(value, unit="亿", is_percent=False):
    """格式化数值显示"""
    if value is None:
        return "N/A"
    if is_percent:
        return f"{value:.2f}%"
    return f"{value:.2f} {unit}"


async def fetch_data(session, api_name, ts_code, fields):
    """单个 API 请求"""
    payload = {
        "api_name": api_name,
        "token": TUSHARE_TOKEN,
        "params": {"ts_code": ts_code},
        "fields": fields
    }
    try:
        async with session.post(API_URL, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            result = await resp.json()
            if result.get("code") == 0:
                return api_name, result.get("data", {}).get("items", [])
            else:
                print(f"API {api_name} error: {result.get('msg')}")
                return api_name, []
    except Exception as e:
        print(f"Request {api_name} failed: {e}")
        return api_name, []


async def get_all_data(ts_code):
    """并发获取所有数据"""
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_data(session, name, ts_code, fields)
            for name, fields in FIELDS_CONFIG.items()
        ]
        results = await asyncio.gather(*tasks)
        return {name: data for name, data in results}


def parse_data(data, api_name):
    """解析 API 返回的数据"""
    fields_map = {
        "income": "total_revenue,revenue,oper_cost,operate_profit,total_profit,n_income,n_income_attr_p,sell_exp,admin_exp,fin_exp,rd_exp,invest_income,fv_value_chg_gain,oth_income,credit_impa_loss,assets_impair_loss".split(","),
        "balancesheet": "total_assets,total_liab,total_hldr_eqy_exc_min_int,total_cur_assets,total_cur_liab,money_cap,goodwill,trad_asset,oth_equity_invest,oth_debt_invest,lt_eqt_invest,invest_real_estate,short_borrow,long_borrow,bonds_payable,lt_borrow,non_cur_liab_due_1y,notes_receiv,accounts_receiv,contract_assets,total_share,cap_rese,surplus_rese,undistr_porfit".split(","),
        "cashflow": "n_cashflow_act,n_cashflow_inv_act,n_cash_flows_fnc_act,c_pay_acq_const_fiolta,c_recp_borrow,c_recp_cap_contrib,c_recp_sell_assets".split(","),
        "fina_indicator": "profit_dedt".split(",")
    }

    if not data:
        return []

    fields = fields_map.get(api_name, [])
    result = []
    for row in data:
        item = {"ts_code": row[0], "end_date": row[1]}
        for i, field in enumerate(fields):
            if i + 2 < len(row):
                item[field] = row[i + 2]
        result.append(item)

    # 按日期排序，返回最新的
    result.sort(key=lambda x: x["end_date"], reverse=True)
    return result


def analyze_income(income_data):
    """分析利润表数据"""
    if not income_data:
        return None

    current = income_data[0]
    previous = income_data[1] if len(income_data) > 1 else None

    # 核心利润计算
    # 核心利润 = 营业利润 - 投资总收益 - 政府补贴 - 资产减值损失 - 信用减值损失
    invest_total = (current.get("invest_income") or 0) + (current.get("fv_value_chg_gain") or 0)
    gov_subsidy = current.get("oth_income") or 0
    credit_loss = current.get("credit_impa_loss") or 0
    asset_loss = current.get("assets_impair_loss") or 0

    core_profit = (current.get("operate_profit") or 0) - invest_total - gov_subsidy - credit_loss - asset_loss

    # 上期核心利润
    if previous:
        invest_total_prev = (previous.get("invest_income") or 0) + (previous.get("fv_value_chg_gain") or 0)
        gov_subsidy_prev = previous.get("oth_income") or 0
        credit_loss_prev = previous.get("credit_impa_loss") or 0
        asset_loss_prev = previous.get("assets_imppair_loss") or 0
        core_profit_prev = (previous.get("operate_profit") or 0) - invest_total_prev - gov_subsidy_prev - credit_loss_prev - asset_loss_prev
    else:
        core_profit_prev = None

    return {
        "revenue": to_yi(current.get("revenue")),
        "revenue_prev": to_yi(previous.get("revenue")) if previous else None,
        "operate_profit": to_yi(current.get("operate_profit")),
        "operate_profit_prev": to_yi(previous.get("operate_profit")) if previous else None,
        "core_profit": to_yi(core_profit),
        "core_profit_prev": to_yi(core_profit_prev) if core_profit_prev else None,
        "n_income": to_yi(current.get("n_income_attr_p")),
        "n_income_prev": to_yi(previous.get("n_income_attr_p")) if previous else None,
        "invest_total": to_yi(invest_total),
        "gov_subsidy": to_yi(gov_subsidy),
        "credit_loss": to_yi(credit_loss),
        "asset_loss": to_yi(asset_loss),
        "oper_cost": to_yi(current.get("oper_cost")),
        "sell_exp": to_yi(current.get("sell_exp")),
        "sell_exp_prev": to_yi(previous.get("sell_exp")) if previous else None,
        "admin_exp": to_yi(current.get("admin_exp")),
        "admin_exp_prev": to_yi(previous.get("admin_exp")) if previous else None,
        "rd_exp": to_yi(current.get("rd_exp")),
        "rd_exp_prev": to_yi(previous.get("rd_exp")) if previous else None,
        "fin_exp": to_yi(current.get("fin_exp")),
        "fin_exp_prev": to_yi(previous.get("fin_exp")) if previous else None,
    }


async def main():
    print("=" * 60)
    print("马上办！请稍等片刻，正在为您查询比亚迪财报数据...")
    print("=" * 60)

    if TUSHARE_TOKEN == "YOUR_TUSHARE_TOKEN_HERE":
        print("\n⚠️  请先在脚本中设置您的 Tushare Token！")
        print("   访问 https://tushare.pro/register 注册获取 Token")
        return

    # 并发获取数据
    print("\n[1/4] 正在并发获取四张报表数据...")
    start_time = datetime.now()
    raw_data = await get_all_data(TS_CODE)

    # 解析数据
    income_data = parse_data(raw_data.get("income"), "income")
    balancesheet_data = parse_data(raw_data.get("balancesheet"), "balancesheet")
    cashflow_data = parse_data(raw_data.get("cashflow"), "cashflow")
    fina_indicator_data = parse_data(raw_data.get("fina_indicator"), "fina_indicator")

    if not income_data:
        print("\n❌ 未能获取到数据，请检查 Token 或网络连接")
        return

    # 获取最新一期信息
    current_period = format_period(income_data[0]["end_date"])

    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"✅ 数据获取完成，耗时 {elapsed:.2f} 秒")
    print(f"📅 当前分析期: {current_period}")

    # 输出分析结果
    print("\n" + "=" * 60)
    print(f"您想要查询的公司为 比亚迪，股票代码 {TS_CODE}，这是{current_period}的关键信息：")
    print("=" * 60)

    # 利润表分析
    income_analysis = analyze_income(income_data)
    if income_analysis:
        print("\n【利润表】\n")

        revenue_growth = calc_growth(income_analysis["revenue"], income_analysis["revenue_prev"])
        print(f"📊 营业收入: {format_value(income_analysis['revenue'])}，增长率: {format_value(revenue_growth, is_percent=True) if revenue_growth else 'N/A'}")

        op_growth = calc_growth(income_analysis["operate_profit"], income_analysis["operate_profit_prev"])
        print(f"🎯 营业利润: {format_value(income_analysis['operate_profit'])}，增长率: {format_value(op_growth, is_percent=True) if op_growth else 'N/A'}")

        core_growth = calc_growth(income_analysis["core_profit"], income_analysis["core_profit_prev"])
        print(f"🎯 核心利润: {format_value(income_analysis['core_profit'])}，增长率: {format_value(core_growth, is_percent=True) if core_growth else 'N/A'}")

        ni_growth = calc_growth(income_analysis["n_income"], income_analysis["n_income_prev"])
        print(f"💲 净利润: {format_value(income_analysis['n_income'])}，增长率: {format_value(ni_growth, is_percent=True) if ni_growth else 'N/A'}")

        # 毛利率
        if income_analysis["revenue"] and income_analysis["oper_cost"]:
            gross_margin = ((income_analysis["revenue"] - income_analysis["oper_cost"]) / income_analysis["revenue"]) * 100
            print(f"📈 毛利率: {gross_margin:.2f}%")

        # 四费管理
        print(f"\n💼 四费管理:")
        sell_growth = calc_growth(income_analysis["sell_exp"], income_analysis["sell_exp_prev"])
        sell_ratio = (income_analysis["sell_exp"] / income_analysis["revenue"]) * 100 if income_analysis["revenue"] else 0
        print(f"   - 销售费用: {format_value(income_analysis['sell_exp'])}，增长率: {format_value(sell_growth, is_percent=True) if sell_growth else 'N/A'}，销售费用率: {sell_ratio:.2f}%")

        admin_growth = calc_growth(income_analysis["admin_exp"], income_analysis["admin_exp_prev"])
        admin_ratio = (income_analysis["admin_exp"] / income_analysis["revenue"]) * 100 if income_analysis["revenue"] else 0
        print(f"   - 管理费用: {format_value(income_analysis['admin_exp'])}，增长率: {format_value(admin_growth, is_percent=True) if admin_growth else 'N/A'}，管理费用率: {admin_ratio:.2f}%")

        rd_growth = calc_growth(income_analysis["rd_exp"], income_analysis["rd_exp_prev"])
        rd_ratio = (income_analysis["rd_exp"] / income_analysis["revenue"]) * 100 if income_analysis["revenue"] else 0
        print(f"   - 研发费用: {format_value(income_analysis['rd_exp'])}，增长率: {format_value(rd_growth, is_percent=True) if rd_growth else 'N/A'}，研发费用率: {rd_ratio:.2f}%")

        fin_growth = calc_growth(income_analysis["fin_exp"], income_analysis["fin_exp_prev"])
        fin_ratio = (income_analysis["fin_exp"] / income_analysis["revenue"]) * 100 if income_analysis["revenue"] else 0
        print(f"   - 财务费用: {format_value(income_analysis['fin_exp'])}，增长率: {format_value(fin_growth, is_percent=True) if fin_growth else 'N/A'}，财务费用率: {fin_ratio:.2f}%")

    print("\n" + "=" * 60)
    print("✅ 财报分析完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
