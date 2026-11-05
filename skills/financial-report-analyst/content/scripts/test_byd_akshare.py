"""
比亚迪年报分析脚本 - 使用 akshare 库
完全免费，无需 API Token！
"""

import akshare as ak
import pandas as pd
from datetime import datetime


def format_period(date_str):
    """格式化日期为中文报表期"""
    year = date_str[:4]
    month_day = date_str[4:]
    month_map = {
        "0331": "一季报",
        "0630": "半年报",
        "0930": "三季报",
        "1231": "年报"
    }
    return f"{year}年{month_map.get(month_day, '')}"


def to_yi(yuan_value):
    """元转亿元"""
    if pd.isna(yuan_value) or yuan_value is None:
        return None
    return round(yuan_value / 1e8, 2)


def calc_growth(current, previous):
    """计算增长率"""
    if previous is None or previous == 0 or pd.isna(previous) or pd.isna(current):
        return None
    return round((current - previous) / abs(previous) * 100, 2)


def format_value(value, unit="亿", is_percent=False):
    """格式化数值显示"""
    if value is None or pd.isna(value):
        return "N/A"
    if is_percent:
        return f"{value:.2f}%"
    return f"{value:.2f} {unit}"


def get_stock_name(stock_code):
    """获取股票名称"""
    try:
        df = ak.stock_individual_info_em(symbol=stock_code)
        name_row = df[df['item'] == '股票简称']
        if not name_row.empty:
            return name_row['value'].values[0]
    except:
        pass
    return "比亚迪"


def fetch_financial_data(stock_code):
    """获取所有财务数据"""
    print("📡 正在获取财务数据...\n")

    # 股票基本信息
    print("获取股票信息...")
    stock_name = get_stock_name(stock_code)

    # 利润表
    print("获取利润表...")
    income_df = ak.stock_financial_report_sina(stock=f'sz{stock_code}' if stock_code.startswith('00') else f'sh{stock_code}', symbol='利润表')

    # 资产负债表
    print("获取资产负债表...")
    balance_df = ak.stock_financial_report_sina(stock=f'sz{stock_code}' if stock_code.startswith('00') else f'sh{stock_code}', symbol='资产负债表')

    # 现金流量表
    print("获取现金流量表...")
    cashflow_df = ak.stock_financial_report_sina(stock=f'sz{stock_code}' if stock_code.startswith('00') else f'sh{stock_code}', symbol='现金流量表')

    # 主要财务指标
    print("获取主要财务指标...")
    indicator_df = ak.stock_financial_abstract_ths(symbol=stock_code, indicator='基本每股收益')

    return {
        'name': stock_name,
        'income': income_df,
        'balance': balance_df,
        'cashflow': cashflow_df,
        'indicator': indicator_df
    }


def analyze_and_output(data, stock_code='002594'):
    """分析数据并按格式输出"""

    name = data['name']
    income_df = data['income']
    balance_df = data['balance']
    indicator_df = data['indicator']

    # 获取最新一期数据 (2024年报)
    current = income_df.iloc[0]
    previous = income_df.iloc[1] if len(income_df) > 1 else None

    current_period = format_period(str(current['报告日']))

    print("=" * 60)
    print(f"📊 {name} ({stock_code}) - {current_period}关键指标")
    print("=" * 60)

    # ========== 利润表 ==========
    print("\n【利润表】\n")

    revenue = to_yi(current.get('营业收入'))
    revenue_prev = to_yi(previous.get('营业收入')) if previous is not None else None
    revenue_growth = calc_growth(revenue, revenue_prev)
    print(f"📊 营业收入: {format_value(revenue)}，增长率: {format_value(revenue_growth, is_percent=True) if revenue_growth else 'N/A'}")

    oper_profit = to_yi(current.get('营业利润'))
    oper_profit_prev = to_yi(previous.get('营业利润')) if previous is not None else None
    oper_profit_growth = calc_growth(oper_profit, oper_profit_prev)
    print(f"🎯 营业利润: {format_value(oper_profit)}，增长率: {format_value(oper_profit_growth, is_percent=True) if oper_profit_growth else 'N/A'}")

    # 计算核心利润
    invest_income = current.get('投资收益', 0) or 0
    fv_change = current.get('公允价值变动收益', 0) or 0
    gov_subsidy = current.get('其他收益', 0) or 0
    credit_loss = current.get('信用减值损失', 0) or 0
    asset_loss = current.get('资产减值损失', 0) or 0

    invest_total = invest_income + fv_change
    core_profit = (current.get('营业利润') or 0) - invest_total - gov_subsidy - credit_loss - asset_loss
    core_profit_yi = to_yi(core_profit)

    if previous is not None:
        inv_prev = previous.get('投资收益', 0) or 0
        fv_prev = previous.get('公允价值变动收益', 0) or 0
        gov_prev = previous.get('其他收益', 0) or 0
        credit_prev = previous.get('信用减值损失', 0) or 0
        asset_prev = previous.get('资产减值损失', 0) or 0
        core_profit_prev = (previous.get('营业利润') or 0) - (inv_prev + fv_prev) - gov_prev - credit_prev - asset_prev
        core_profit_prev_yi = to_yi(core_profit_prev)
        core_profit_growth = calc_growth(core_profit_yi, core_profit_prev_yi)
    else:
        core_profit_growth = None

    print(f"🎯 核心利润: {format_value(core_profit_yi)}，增长率: {format_value(core_profit_growth, is_percent=True) if core_profit_growth else 'N/A'}")

    # 净利润
    net_profit = to_yi(current.get('净利润'))
    net_profit_prev = to_yi(previous.get('净利润')) if previous is not None else None
    net_profit_growth = calc_growth(net_profit, net_profit_prev)
    print(f"💲 净利润: {format_value(net_profit)}，增长率: {format_value(net_profit_growth, is_percent=True) if net_profit_growth else 'N/A'}")

    # 扣非净利润 (从指标表)
    deduct_profit = None
    if not indicator_df.empty:
        try:
            current_year = str(current['报告日'])[:4]
            deduct_row = indicator_df[indicator_df['报告期'].astype(str).str.contains(current_year)]
            if not deduct_row.empty:
                deduct_str = str(deduct_row['扣非净利润'].values[0]).replace('亿', '').replace('万', '')
                if '万' in str(deduct_row['扣非净利润'].values[0]):
                    deduct_profit = float(deduct_str) / 10000
                else:
                    deduct_profit = float(deduct_str)
                deduct_profit = round(deduct_profit, 2)
        except:
            pass

    if deduct_profit:
        print(f"💲 扣非归母净利润: {format_value(deduct_profit)}")

    # 毛利率和净利率
    oper_cost = to_yi(current.get('营业成本'))
    if revenue and oper_cost:
        gross_margin = ((revenue - oper_cost) / revenue) * 100
        gross_margin_prev = None
        if previous is not None:
            oper_cost_prev = to_yi(previous.get('营业成本'))
            revenue_prev_val = to_yi(previous.get('营业收入'))
            if revenue_prev_val and oper_cost_prev:
                gross_margin_prev = ((revenue_prev_val - oper_cost_prev) / revenue_prev_val) * 100
        gross_margin_growth = calc_growth(gross_margin, gross_margin_prev)
        print(f"📈 毛利率: {gross_margin:.2f}%，增长率: {format_value(gross_margin_growth, is_percent=True) if gross_margin_growth else 'N/A'}")

    if revenue and net_profit:
        net_margin = (net_profit / revenue) * 100
        print(f"📈 净利率: {net_margin:.2f}%")

    # 核心利润率
    if revenue and core_profit_yi:
        core_margin = (core_profit_yi / revenue) * 100
        print(f"📈 核心利润率: {core_margin:.2f}%")

    # 三支柱
    print(f"\n🌐 三支柱:")
    if oper_profit:
        core_ratio = (core_profit_yi / oper_profit) * 100 if oper_profit else 0
        invest_ratio = (to_yi(invest_total) / oper_profit) * 100 if oper_profit else 0
        gov_ratio = (to_yi(gov_subsidy) / oper_profit) * 100 if oper_profit else 0
        print(f"   - 核心利润: {format_value(core_profit_yi)}，占比: {core_ratio:.2f}%")
        print(f"   - 投资总收益: {format_value(to_yi(invest_total))}，占比: {invest_ratio:.2f}%")
        print(f"   - 政府补贴: {format_value(to_yi(gov_subsidy))}，占比: {gov_ratio:.2f}%")

    # 两搅局
    print(f"\n🕵️ 两搅局:")
    credit_loss_yi = to_yi(credit_loss)
    asset_loss_yi = to_yi(asset_loss)
    if oper_profit:
        credit_ratio = (credit_loss_yi / oper_profit) * 100 if oper_profit else 0
        asset_ratio = (asset_loss_yi / oper_profit) * 100 if oper_profit else 0
        print(f"   - 信用减值: {format_value(credit_loss_yi)}，占比 {credit_ratio:.2f}%")
        print(f"   - 资产减值: {format_value(asset_loss_yi)}，占比 {asset_ratio:.2f}%")

    # 四费管理
    print(f"\n💼 四费管理:")
    sell_exp = to_yi(current.get('销售费用'))
    admin_exp = to_yi(current.get('管理费用'))
    rd_exp = to_yi(current.get('研发费用'))
    fin_exp = to_yi(current.get('财务费用'))

    if sell_exp:
        sell_prev = to_yi(previous.get('销售费用')) if previous is not None else None
        sell_growth = calc_growth(sell_exp, sell_prev)
        sell_ratio = (sell_exp / revenue) * 100 if revenue else 0
        print(f"   - 销售费用: {format_value(sell_exp)}，增长率: {format_value(sell_growth, is_percent=True) if sell_growth else 'N/A'}，销售费用率: {sell_ratio:.2f}%")

    if admin_exp:
        admin_prev = to_yi(previous.get('管理费用')) if previous is not None else None
        admin_growth = calc_growth(admin_exp, admin_prev)
        admin_ratio = (admin_exp / revenue) * 100 if revenue else 0
        print(f"   - 管理费用: {format_value(admin_exp)}，增长率: {format_value(admin_growth, is_percent=True) if admin_growth else 'N/A'}，管理费用率: {admin_ratio:.2f}%")

    if rd_exp:
        rd_prev = to_yi(previous.get('研发费用')) if previous is not None else None
        rd_growth = calc_growth(rd_exp, rd_prev)
        rd_ratio = (rd_exp / revenue) * 100 if revenue else 0
        print(f"   - 研发费用: {format_value(rd_exp)}，增长率: {format_value(rd_growth, is_percent=True) if rd_growth else 'N/A'}，研发费用率: {rd_ratio:.2f}%")

    if fin_exp:
        fin_prev = to_yi(previous.get('财务费用')) if previous is not None else None
        fin_growth = calc_growth(fin_exp, fin_prev)
        fin_ratio = (fin_exp / revenue) * 100 if revenue else 0
        print(f"   - 财务费用: {format_value(fin_exp)}，增长率: {format_value(fin_growth, is_percent=True) if fin_growth else 'N/A'}，财务费用率: {fin_ratio:.2f}%")

    # ========== 资产负债表 ==========
    print("\n\n【资产负债表】\n")

    balance_current = balance_df.iloc[0]
    balance_prev = balance_df.iloc[1] if len(balance_df) > 1 else None

    total_assets = to_yi(balance_current.get('资产总计'))
    total_assets_prev = to_yi(balance_prev.get('资产总计')) if balance_prev is not None else None
    assets_growth = calc_growth(total_assets, total_assets_prev)
    print(f"📊 总资产: {format_value(total_assets)}，增长率: {format_value(assets_growth, is_percent=True) if assets_growth else 'N/A'}")

    total_liab = to_yi(balance_current.get('负债合计'))
    total_liab_prev = to_yi(balance_prev.get('负债合计')) if balance_prev is not None else None
    debt_ratio = (total_liab / total_assets) * 100 if total_assets else 0
    print(f"🎯 资产负债率: {debt_ratio:.2f}%")

    total_cur_assets = to_yi(balance_current.get('流动资产合计'))
    total_cur_liab = to_yi(balance_current.get('流动负债合计'))
    print(f"💲 流动资产: {format_value(total_cur_assets)}")
    print(f"💲 流动负债: {format_value(total_cur_liab)}")

    cur_ratio = total_cur_assets / total_cur_liab if total_cur_liab else 0
    print(f"📐 流动比率: {cur_ratio:.2f}")

    # 综合点评
    print("\n\n" + "=" * 60)
    print("💡 综合点评：")
    print("=" * 60)

    comments = []

    # 营收增长
    if revenue_growth and revenue_growth > 0:
        comments.append(f"营收持续增长 {revenue_growth:.1f}%，规模效应显著")
    elif revenue_growth and revenue_growth < 0:
        comments.append(f"营收同比下降 {abs(revenue_growth):.1f}%，需关注变化原因")

    # 盈利能力
    if core_profit_yi and net_profit:
        if core_profit_yi > net_profit:
            comments.append("核心利润表现强劲，主业盈利能力扎实")
        else:
            comments.append("非经常性损益对净利润贡献较大")

    # 现金流
    if debt_ratio:
        if debt_ratio > 70:
            comments.append(f"资产负债率较高 ({debt_ratio:.1f}%)，需关注债务风险")
        elif debt_ratio < 50:
            comments.append("资产负债率处于健康水平，财务结构稳健")

    # 研发投入
    if rd_exp and revenue:
        rd_ratio_val = (rd_exp / revenue) * 100
        if rd_ratio_val > 5:
            comments.append(f"研发费用率 {rd_ratio_val:.1f}%，创新投入力度大")

    # 扣非
    if deduct_profit and net_profit:
        if deduct_profit > net_profit * 0.9:
            comments.append("扣非净利润占比高，利润质量好")

    # 输出点评
    for i, comment in enumerate(comments[:5], 1):
        print(f"{i}. {comment}")

    print("\n" + "=" * 60)
    print("✅ 财报分析完成！")
    print("=" * 60)

    print("\n📝 数据来源: akshare (东方财富)")
    print("⚠️  本分析仅供参考，不构成投资建议")


def main():
    print("=" * 60)
    print("🔍 马上办！正在为您查询比亚迪财报数据...")
    print("📌 数据源: akshare (免费开源)")
    print("=" * 60)

    stock_code = "002594"  # 比亚迪

    start_time = datetime.now()

    try:
        # 获取数据
        data = fetch_financial_data(stock_code)

        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"\n✅ 数据获取完成，耗时 {elapsed:.2f} 秒\n")

        # 分析并输出
        analyze_and_output(data, stock_code)

    except Exception as e:
        print(f"\n❌ 获取数据失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
