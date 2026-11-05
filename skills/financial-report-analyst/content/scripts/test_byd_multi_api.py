"""
比亚迪 2025 年年报分析测试脚本 - 多数据源版本
支持: Tushare / 麦蕊智数 / 东方财富

股票代码: 002594.SZ (比亚迪)
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Optional, Dict, Any

# ============================================================
# 配置区域 - 请选择数据源并填入相应凭证
# ============================================================

# 数据源选择: "tushare" / "mairui" / "eastmoney"
DATA_SOURCE = "tushare"  # 使用 Tushare

# Tushare 配置 (如果选择 tushare)
TUSHARE_TOKEN = "a83b0314d676b2f64b6e3743f10f2be09500319d522dd632e8883198"
API_URL = "https://api.tushare.pro"

# 麦蕊智数配置 (如果选择 mairui)
# 测试 license: b997d4403688d5e66a (只能获取 000001 平安银行)
# 免费 license 申请: https://www.mairui.club/gratis.html
MAIRUI_LICENSE = "b997d4403688d5e66a"

# 股票代码
TS_CODE = "002594.SZ"
STOCK_CODE = "002594"


def format_period(end_date):
    """格式化日期为中文报表期"""
    if not end_date:
        return "N/A"
    year = end_date[:4]
    month_day = end_date[5:10] if "-" in end_date else end_date[4:8]
    month_map = {
        "03-31": "一季报",
        "06-30": "半年报",
        "09-30": "三季报",
        "12-31": "年报"
    }
    return f"{year}年{month_map.get(month_day, '')}"


def to_yi(yuan_value):
    """元转亿元，保留2位小数"""
    if yuan_value is None:
        return None
    return round(yuan_value / 1e8, 2)


def calc_growth(current, previous):
    """计算增长率"""
    if previous is None or previous == 0 or current is None:
        return None
    return round((current - previous) / abs(previous) * 100, 2)


def format_value(value, unit="亿", is_percent=False):
    """格式化数值显示"""
    if value is None:
        return "N/A"
    if is_percent:
        return f"{value:.2f}%"
    return f"{value:.2f} {unit}"


# ============================================================
# 数据源适配器
# ============================================================

async def fetch_tushare(api_name: str, ts_code: str, fields: str) -> Optional[Dict]:
    """Tushare API"""
    payload = {
        "api_name": api_name,
        "token": TUSHARE_TOKEN,
        "params": {"ts_code": ts_code},
        "fields": fields
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                result = await resp.json()
                if result.get("code") == 0:
                    data = result.get("data", {})
                    fields_list = data.get("fields", [])
                    items = data.get("items", [])
                    return {"fields": fields_list, "items": items}
                else:
                    print(f"Tushare {api_name} error: {result.get('msg')}")
                    return None
    except Exception as e:
        print(f"Tushare request failed: {e}")
        return None


async def fetch_mairui_financial(stock_code: str) -> Optional[Dict]:
    """
    麦蕊智数 - 主要财务指标接口
    文档: http://api.mairui.club/hscp/cwzb/list/{code}/{license}

    返回字段:
    - date: 报告日期
    - tbmg: 摊薄每股收益
    - jqmg: 加权每股收益
    - kfmg: 扣除非经常性损益后每股收益
    - mgjz: 每股净资产
    - mgsy: 每股收益
    - yysr: 营业收入(万元)
    - yysrze: 营业收入总额(万元)
    - mgjyxjl: 每股经营现金流
    - jlxjll: 经营现金流(万元)
    - gdjyxjl: 购头固定资产等长期投资支付的现金(万元)
    - mgxjzcsdsy: 每股现金等价物
    - mgxzjx: 每股现金股息
    - jlxjl: 经营现金净流量(万元)
    - gqtzsl: 股前投资收益率
    - tzsl: 投资收益率
    - roe_dltz: 净资产收益率(摊薄)
    - roe_jqtz: 净资产收益率(加权)
    - mll: 毛利率
    - jll: 净利率
    - cbl: 筹码集中度
    - sjl: 市盈率
    - zsz: 总市值
    - ltsz: 流通市值
    """
    url = f"http://api.mairui.club/hscp/cwzb/{stock_code}/{MAIRUI_LICENSE}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if isinstance(data, list) and len(data) > 0:
                        return data
                    elif isinstance(data, dict) and data.get("error"):
                        print(f"麦蕊智数错误: {data.get('msg', 'Unknown error')}")
                        return None
                return None
    except Exception as e:
        print(f"麦蕊智数请求失败: {e}")
        return None


async def get_data_tushare(ts_code: str) -> Optional[Dict]:
    """获取 Tushare 数据"""
    print("\n📡 正在从 Tushare 获取数据...")

    # 字段配置
    fields_config = {
        "income": "ts_code,end_date,total_revenue,revenue,oper_cost,operate_profit,total_profit,n_income,n_income_attr_p,sell_exp,admin_exp,fin_exp,rd_exp,invest_income,fv_value_chg_gain,oth_income,credit_impa_loss,assets_impair_loss",
        "balancesheet": "ts_code,end_date,total_assets,total_liab,total_hldr_eqy_exc_min_int,total_cur_assets,total_cur_liab,money_cap,goodwill,trad_asset,oth_equity_invest,oth_debt_invest,lt_eqt_invest,invest_real_estate,short_borrow,long_borrow,bonds_payable,lt_borrow,non_cur_liab_due_1y,notes_receiv,accounts_receiv,contract_assets,total_share,cap_rese,surplus_rese,undistr_porfit",
        "cashflow": "ts_code,end_date,n_cashflow_act,n_cashflow_inv_act,n_cash_flows_fnc_act,c_pay_acq_const_fiolta,c_recp_borrow,c_recp_cap_contrib,c_recp_sell_assets",
        "fina_indicator": "ts_code,end_date,profit_dedt"
    }

    # 并发请求
    tasks = [
        fetch_tushare(api, ts_code, fields)
        for api, fields in fields_config.items()
    ]
    results = await asyncio.gather(*tasks)

    return {
        "income": results[0],
        "balancesheet": results[1],
        "cashflow": results[2],
        "fina_indicator": results[3]
    }


async def get_data_mairui(stock_code: str) -> Optional[Dict]:
    """获取麦蕊智数数据"""
    print("\n📡 正在从麦蕊智数获取数据...")
    data = await fetch_mairui_financial(stock_code)
    return {"mairui": data}


def parse_tushare_result(data: Dict, api_name: str) -> list:
    """解析 Tushare 返回数据"""
    if not data:
        return []
    fields = data.get("fields", [])
    items = data.get("items", [])

    result = []
    for row in items:
        item = {}
        for i, field in enumerate(fields):
            if i < len(row):
                item[field] = row[i]
        result.append(item)

    # 按日期排序
    result.sort(key=lambda x: str(x.get("end_date", "")), reverse=True)
    return result


def analyze_mairui(data: list) -> Optional[Dict]:
    """分析麦蕊智数数据"""
    if not data:
        return None

    # 按日期倒序，取最新一期
    data.sort(key=lambda x: x.get("date", ""), reverse=True)
    current = data[0]
    previous = data[1] if len(data) > 1 else None

    # 提取关键指标（单位转换：万元 -> 亿元）
    result = {
        "period": format_period(current.get("date", "")),
        "revenue": round(current.get("yysrze", 0) / 10000, 2) if current.get("yysrze") else None,  # 万元转亿
        "eps_diluted": current.get("tbmg"),  # 摊薄每股收益
        "eps_deduct": current.get("kfmg"),  # 扣非每股收益
        "net_asset_per_share": current.get("mgjz"),  # 每股净资产
        "roe_diluted": current.get("roe_dltz"),  # ROE(摊薄)
        "roe_weighted": current.get("roe_jqtz"),  # ROE(加权)
        "gross_margin": current.get("mll"),  # 毛利率
        "net_margin": current.get("jll"),  # 净利率
        "per_share_op_cf": current.get("mgjyxjl"),  # 每股经营现金流
        "pe": current.get("sjl"),  # 市盈率
        "total_market_cap": round(current.get("zsz", 0) / 10000, 2) if current.get("zsz") else None,  # 总市值(万->亿)
    }

    return result


def output_report_mairui(analysis: Dict, previous: Optional[Dict] = None):
    """输出麦蕊智数分析报告"""
    print("\n" + "=" * 60)
    print(f"📊 {TS_CODE} 比亚迪 - {analysis.get('period', '最新财报')}关键指标")
    print("=" * 60)
    print(f"\n📈 收益指标:")
    print(f"   - 摊薄每股收益: {analysis.get('eps_diluted', 'N/A')} 元")
    print(f"   - 扣非每股收益: {analysis.get('eps_deduct', 'N/A')} 元")
    print(f"   - 每股净资产: {analysis.get('net_asset_per_share', 'N/A')} 元")
    print(f"   - 每股经营现金流: {analysis.get('per_share_op_cf', 'N/A')} 元")

    print(f"\n📊 盈利能力:")
    print(f"   - 毛利率: {format_value(analysis.get('gross_margin'), is_percent=True) if analysis.get('gross_margin') else 'N/A'}")
    print(f"   - 净利率: {format_value(analysis.get('net_margin'), is_percent=True) if analysis.get('net_margin') else 'N/A'}")
    print(f"   - ROE(摊薄): {format_value(analysis.get('roe_diluted'), is_percent=True) if analysis.get('roe_diluted') else 'N/A'}")
    print(f"   - ROE(加权): {format_value(analysis.get('roe_weighted'), is_percent=True) if analysis.get('roe_weighted') else 'N/A'}")

    print(f"\n💰 估值指标:")
    print(f"   - 市盈率(PE): {analysis.get('pe', 'N/A')}")
    if analysis.get('total_market_cap'):
        print(f"   - 总市值: {format_value(analysis.get('total_market_cap'))}")


async def main():
    print("=" * 60)
    print("🔍 马上办！正在为您查询比亚迪财报数据...")
    print(f"📌 数据源: {DATA_SOURCE}")
    print("=" * 60)

    start_time = datetime.now()

    if DATA_SOURCE == "tushare":
        if TUSHARE_TOKEN == "YOUR_TUSHARE_TOKEN":
            print("\n⚠️  请先在脚本中设置 Tushare Token!")
            print("   注册地址: https://tushare.pro/register")
            return

        raw_data = await get_data_tushare(TS_CODE)

    elif DATA_SOURCE == "mairui":
        raw_data = await get_data_mairui(STOCK_CODE)

    else:
        print(f"⚠️  不支持的数据源: {DATA_SOURCE}")
        return

    elapsed = (datetime.now() - start_time).total_seconds()

    if not raw_data:
        print("\n❌ 未能获取到数据，请检查网络或 API 配置")
        return

    print(f"\n✅ 数据获取完成，耗时 {elapsed:.2f} 秒")

    # 解析并输出
    if DATA_SOURCE == "mairui":
        mairui_data = raw_data.get("mairui")
        if mairui_data:
            analysis = analyze_mairui(mairui_data)
            output_report_mairui(analysis)
        else:
            print("\n❌ 麦蕊智数暂无该股票数据（可能需要申请正式 license）")
            print("💡 提示: 测试 license (b997d4403688d5e66a) 可能只支持部分股票")
            print("   申请免费正式 license: https://www.mairui.club/gratis.html")

    print("\n" + "=" * 60)
    print("✅ 财报查询完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
