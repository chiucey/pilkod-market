#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票基本面数据获取脚本
支持横向对比（两只股票同时期）和纵向对比（单只股票历史）
"""

import sys
import json
import tushare as ts
from datetime import datetime

# Tushare Token
TS_TOKEN = '89cb8feb948d75ffbcc1222b611409dbdf701d25ad32c924fadb9643'

def init_tushare():
    """初始化Tushare Pro API"""
    ts.set_token(TS_TOKEN)
    return ts.pro_api()

def get_income_data(pro, ts_code, periods):
    """获取利润表数据"""
    data = {}
    for period in periods:
        df = pro.income(
            ts_code=ts_code,
            period=period,
            fields='ts_code,end_date,ann_date,total_revenue,revenue,oper_cost,n_income,n_income_attr_p,netprofit_incl_min_int_inc'
        )
        if not df.empty:
            data[period] = df.iloc[0].to_dict()
    return data

def get_balancesheet_data(pro, ts_code, periods):
    """获取资产负债表数据"""
    data = {}
    for period in periods:
        df = pro.balancesheet(
            ts_code=ts_code,
            period=period,
            fields='ts_code,end_date,total_assets,total_liab,total_hldr_eqy_exc_min_int,monetary_cap,inventory'
        )
        if not df.empty:
            data[period] = df.iloc[0].to_dict()
    return data

def get_cashflow_data(pro, ts_code, periods):
    """获取现金流量表数据"""
    data = {}
    for period in periods:
        df = pro.cashflow(
            ts_code=ts_code,
            period=period,
            fields='ts_code,end_date,n_cashflow_act,n_cashflow_inv_act'
        )
        if not df.empty:
            data[period] = df.iloc[0].to_dict()
    return data

def get_fina_indicator_data(pro, ts_code, periods):
    """获取财务指标数据"""
    data = {}
    for period in periods:
        df = pro.fina_indicator(
            ts_code=ts_code,
            period=period,
            fields='ts_code,end_date,roe,roe_dt,netprofit_margin,grossprofit_margin,current_ratio,quick_ratio,debt_to_assets'
        )
        if not df.empty:
            data[period] = df.iloc[0].to_dict()
    return data

def get_daily_basic_data(pro, ts_code, trade_date):
    """获取每日指标数据（PE/PB/市值）"""
    df = pro.daily_basic(
        ts_code=ts_code,
        trade_date=trade_date,
        fields='ts_code,trade_date,close,pe_ttm,pb,ps_ttm,total_mv,dv_ratio'
    )
    if not df.empty:
        return df.iloc[0].to_dict()
    return {}

def fetch_horizontal_comparison(code_a, code_b, report_periods, trade_date):
    """横向对比：两只股票同时期数据"""
    pro = init_tushare()
    
    result = {
        'type': 'horizontal',
        'stock_a': code_a,
        'stock_b': code_b,
        'periods': report_periods,
        'trade_date': trade_date,
        'data': {}
    }
    
    for code in [code_a, code_b]:
        stock_data = {
            'income': get_income_data(pro, code, report_periods),
            'balancesheet': get_balancesheet_data(pro, code, report_periods),
            'cashflow': get_cashflow_data(pro, code, report_periods),
            'fina_indicator': get_fina_indicator_data(pro, code, report_periods),
            'daily_basic': get_daily_basic_data(pro, code, trade_date)
        }
        result['data'][code] = stock_data
    
    return result

def fetch_vertical_comparison(code, annual_periods, quarterly_periods, trade_date):
    """纵向对比：单只股票历史数据"""
    pro = init_tushare()
    
    result = {
        'type': 'vertical',
        'stock': code,
        'annual_periods': annual_periods,
        'quarterly_periods': quarterly_periods,
        'trade_date': trade_date,
        'data': {}
    }
    
    all_periods = annual_periods + quarterly_periods
    
    stock_data = {
        'income': get_income_data(pro, code, all_periods),
        'balancesheet': get_balancesheet_data(pro, code, all_periods),
        'cashflow': get_cashflow_data(pro, code, all_periods),
        'fina_indicator': get_fina_indicator_data(pro, code, all_periods),
        'daily_basic': get_daily_basic_data(pro, code, trade_date)
    }
    result['data'] = stock_data
    
    return result

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Horizontal: python fetch_data.py --mode horizontal --code-a 000426.SZ --code-b 000408.SZ --periods 20251231,20260331 --trade-date 20260423")
        print("  Vertical: python fetch_data.py --mode vertical --code 000408.SZ --annual 20231231,20241231,20251231 --quarterly 20250930,20251231,20260331 --trade-date 20260423")
        sys.exit(1)
    
    args = sys.argv[1:]
    mode = None
    code_a = None
    code_b = None
    code = None
    periods = []
    annual_periods = []
    quarterly_periods = []
    trade_date = datetime.now().strftime('%Y%m%d')
    
    # 解析参数
    i = 0
    while i < len(args):
        if args[i] == '--mode':
            mode = args[i+1]
            i += 2
        elif args[i] == '--code-a':
            code_a = args[i+1]
            i += 2
        elif args[i] == '--code-b':
            code_b = args[i+1]
            i += 2
        elif args[i] == '--code':
            code = args[i+1]
            i += 2
        elif args[i] == '--periods':
            periods = args[i+1].split(',')
            i += 2
        elif args[i] == '--annual':
            annual_periods = args[i+1].split(',')
            i += 2
        elif args[i] == '--quarterly':
            quarterly_periods = args[i+1].split(',')
            i += 2
        elif args[i] == '--trade-date':
            trade_date = args[i+1]
            i += 2
        else:
            i += 1
    
    # 执行查询
    if mode == 'horizontal' and code_a and code_b and periods:
        result = fetch_horizontal_comparison(code_a, code_b, periods, trade_date)
    elif mode == 'vertical' and code and annual_periods and quarterly_periods:
        result = fetch_vertical_comparison(code, annual_periods, quarterly_periods, trade_date)
    else:
        print("Error: Invalid parameters")
        sys.exit(1)
    
    # 输出JSON
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()