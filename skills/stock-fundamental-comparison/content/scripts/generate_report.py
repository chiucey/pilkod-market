#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票基本面对比报告生成脚本
根据fetch_data.py返回的数据生成可视化HTML报告
"""

import sys
import json
import os
from datetime import datetime
from string import Template

# HTML模板路径
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets', 'html_template.html')

def calculate_score(value, dimension):
    """计算各维度评分"""
    # 盈利能力评分
    if dimension == 'profitability':
        roe_score = 30 if value['roe'] > 20 else (20 if value['roe'] > 15 else (10 if value['roe'] > 10 else 0))
        net_margin_score = 30 if value['net_margin'] > 15 else (20 if value['net_margin'] > 10 else (10 if value['net_margin'] > 5 else 0))
        gross_margin_score = 40 if value['gross_margin'] > 40 else (30 if value['gross_margin'] > 30 else (20 if value['gross_margin'] > 20 else 10))
        return roe_score + net_margin_score + gross_margin_score
    
    # 成长性评分
    elif dimension == 'growth':
        revenue_growth_score = 40 if value['revenue_growth'] > 30 else (30 if value['revenue_growth'] > 20 else (20 if value['revenue_growth'] > 10 else 10))
        profit_growth_score = 60 if value['profit_growth'] > 50 else (40 if value['profit_growth'] > 30 else (20 if value['profit_growth'] > 10 else 10))
        return revenue_growth_score + profit_growth_score
    
    # 偿债能力评分
    elif dimension == 'solvency':
        debt_ratio_score = 40 if value['debt_ratio'] < 30 else (30 if value['debt_ratio'] < 50 else (20 if value['debt_ratio'] < 70 else 10))
        current_ratio_score = 30 if value['current_ratio'] > 2 else (20 if value['current_ratio'] > 1.5 else (10 if value['current_ratio'] > 1 else 0))
        quick_ratio_score = 30 if value['quick_ratio'] > 1.5 else (20 if value['quick_ratio'] > 1 else (10 if value['quick_ratio'] > 0.5 else 0))
        return debt_ratio_score + current_ratio_score + quick_ratio_score
    
    # 运营效率评分（简化）
    elif dimension == 'operation':
        return 50  # 默认中等分数
    
    # 现金流评分
    elif dimension == 'cashflow':
        ocf_score = 50 if value['ocf_to_profit'] > 1 else (30 if value['ocf_to_profit'] > 0.5 else 10)
        return ocf_score
    
    # 估值合理性评分
    elif dimension == 'valuation':
        dividend_score = 30 if value['dividend_yield'] > 5 else (20 if value['dividend_yield'] > 3 else (10 if value['dividend_yield'] > 1 else 0))
        pe_score = 40 if value['pe'] < 20 else (30 if value['pe'] < 30 else (20 if value['pe'] < 50 else 10))
        return dividend_score + pe_score
    
    return 0

def extract_key_metrics(data, period):
    """从数据中提取关键指标"""
    income = data.get('income', {}).get(period, {})
    balancesheet = data.get('balancesheet', {}).get(period, {})
    cashflow = data.get('cashflow', {}).get(period, {})
    fina_indicator = data.get('fina_indicator', {}).get(period, {})
    daily_basic = data.get('daily_basic', {})
    
    metrics = {
        'revenue': income.get('total_revenue', 0) / 1e8 if income.get('total_revenue') else 0,
        'net_profit': income.get('n_income_attr_p', 0) / 1e8 if income.get('n_income_attr_p') else 0,
        'gross_margin': fina_indicator.get('grossprofit_margin', 0) if fina_indicator.get('grossprofit_margin') else 0,
        'net_margin': fina_indicator.get('netprofit_margin', 0) if fina_indicator.get('netprofit_margin') else 0,
        'roe': fina_indicator.get('roe', 0) if fina_indicator.get('roe') else 0,
        'debt_ratio': fina_indicator.get('debt_to_assets', 0) * 100 if fina_indicator.get('debt_to_assets') else 0,
        'current_ratio': fina_indicator.get('current_ratio', 0) if fina_indicator.get('current_ratio') else 0,
        'quick_ratio': fina_indicator.get('quick_ratio', 0) if fina_indicator.get('quick_ratio') else 0,
        'ocf': cashflow.get('n_cashflow_act', 0) / 1e8 if cashflow.get('n_cashflow_act') else 0,
        'pe': daily_basic.get('pe_ttm', 0) if daily_basic.get('pe_ttm') else 0,
        'pb': daily_basic.get('pb', 0) if daily_basic.get('pb') else 0,
        'dividend_yield': daily_basic.get('dv_ratio', 0) * 100 if daily_basic.get('dv_ratio') else 0,
        'market_cap': daily_basic.get('total_mv', 0) / 1e8 if daily_basic.get('total_mv') else 0,
    }
    
    return metrics

def generate_horizontal_report(data, output_path):
    """生成横向对比HTML报告"""
    # 提取股票信息
    code_a = data['stock_a']
    code_b = data['stock_b']
    periods = data['periods']
    trade_date = data['trade_date']
    
    # 提取关键指标
    period = periods[0]  # 使用第一个报告期
    metrics_a = extract_key_metrics(data['data'][code_a], period)
    metrics_b = extract_key_metrics(data['data'][code_b], period)
    
    # 计算评分
    scores_a = {
        'profitability': calculate_score(metrics_a, 'profitability'),
        'growth': calculate_score(metrics_a, 'growth'),
        'solvency': calculate_score(metrics_a, 'solvency'),
        'operation': calculate_score(metrics_a, 'operation'),
        'cashflow': calculate_score(metrics_a, 'cashflow'),
        'valuation': calculate_score(metrics_a, 'valuation'),
    }
    scores_b = {
        'profitability': calculate_score(metrics_b, 'profitability'),
        'growth': calculate_score(metrics_b, 'growth'),
        'solvency': calculate_score(metrics_b, 'solvency'),
        'operation': calculate_score(metrics_b, 'operation'),
        'cashflow': calculate_score(metrics_b, 'cashflow'),
        'valuation': calculate_score(metrics_b, 'valuation'),
    }
    
    total_a = sum(scores_a.values())
    total_b = sum(scores_b.values())
    
    # 生成HTML内容（简化版，实际应读取模板并替换）
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{code_a} vs {code_b} 基本面对比分析</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <style>
        body {{ font-family: 'Microsoft YaHei', sans-serif; background: #0a1628; color: #e0e6ed; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .section {{ background: #1a2a4a; padding: 25px; border-radius: 10px; margin-bottom: 25px; }}
        h1 {{ color: #4a90e2; }}
        h2 {{ color: #4a90e2; border-bottom: 2px solid #4a90e2; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; border-bottom: 1px solid #2a3a5a; }}
        th {{ background: #2a3a5a; color: #4a90e2; }}
        .winner {{ color: #4caf50; }}
        .loser {{ color: #f44336; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{code_a} vs {code_b} 基本面对比分析</h1>
        <p>数据截止：{trade_date} | 报告期：{period}</p>
        
        <div class="section">
            <h2>盈利能力对比</h2>
            <table>
                <tr><th>指标</th><th>{code_a}</th><th>{code_b}</th><th>优胜方</th></tr>
                <tr><td>营业收入</td><td>{metrics_a['revenue']:.2f}亿元</td><td>{metrics_b['revenue']:.2f}亿元</td><td class="{('winner' if metrics_a['revenue'] > metrics_b['revenue'] else 'loser')}">{code_a if metrics_a['revenue'] > metrics_b['revenue'] else code_b}</td></tr>
                <tr><td>归母净利润</td><td>{metrics_a['net_profit']:.2f}亿元</td><td>{metrics_b['net_profit']:.2f}亿元</td><td class="{('winner' if metrics_a['net_profit'] > metrics_b['net_profit'] else 'loser')}">{code_a if metrics_a['net_profit'] > metrics_b['net_profit'] else code_b}</td></tr>
                <tr><td>毛利率</td><td>{metrics_a['gross_margin']:.1f}%</td><td>{metrics_b['gross_margin']:.1f}%</td><td class="{('winner' if metrics_a['gross_margin'] > metrics_b['gross_margin'] else 'loser')}">{code_a if metrics_a['gross_margin'] > metrics_b['gross_margin'] else code_b}</td></tr>
                <tr><td>净利率</td><td>{metrics_a['net_margin']:.1f}%</td><td>{metrics_b['net_margin']:.1f}%</td><td class="{('winner' if metrics_a['net_margin'] > metrics_b['net_margin'] else 'loser')}">{code_a if metrics_a['net_margin'] > metrics_b['net_margin'] else code_b}</td></tr>
                <tr><td>ROE</td><td>{metrics_a['roe']:.1f}%</td><td>{metrics_b['roe']:.1f}%</td><td class="{('winner' if metrics_a['roe'] > metrics_b['roe'] else 'loser')}">{code_a if metrics_a['roe'] > metrics_b['roe'] else code_b}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>综合评分</h2>
            <table>
                <tr><th>维度</th><th>{code_a}得分</th><th>{code_b}得分</th></tr>
                <tr><td>盈利能力</td><td>{scores_a['profitability']}</td><td>{scores_b['profitability']}</td></tr>
                <tr><td>成长性</td><td>{scores_a['growth']}</td><td>{scores_b['growth']}</td></tr>
                <tr><td>偿债能力</td><td>{scores_a['solvency']}</td><td>{scores_b['solvency']}</td></tr>
                <tr><td>运营效率</td><td>{scores_a['operation']}</td><td>{scores_b['operation']}</td></tr>
                <tr><td>现金流</td><td>{scores_a['cashflow']}</td><td>{scores_b['cashflow']}</td></tr>
                <tr><td>估值合理性</td><td>{scores_a['valuation']}</td><td>{scores_b['valuation']}</td></tr>
                <tr style="background:#2a3a5a;font-weight:600;"><td>综合得分</td><td>{total_a}</td><td>{total_b}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>综合结论</h2>
            <p><strong>{code_a}</strong>：综合得分{total_a}分</p>
            <p><strong>{code_b}</strong>：综合得分{total_b}分</p>
            <p><strong>优胜方</strong>：{code_a if total_a > total_b else code_b if total_b > total_a else '持平'}</p>
        </div>
    </div>
    
    <script>
        // 雷达图（实际生成时需完整配置）
        console.log('Chart.js loaded');
    </script>
</body>
</html>
"""
    
    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Report generated: {output_path}")

def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("Usage: python generate_report.py --input <json_file> --output <html_file>")
        sys.exit(1)
    
    input_file = None
    output_file = None
    
    i = 0
    while i < len(sys.argv):
        if sys.argv[i] == '--input':
            input_file = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == '--output':
            output_file = sys.argv[i+1]
            i += 2
        else:
            i += 1
    
    if not input_file or not output_file:
        print("Error: Missing parameters")
        sys.exit(1)
    
    # 读取数据
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 生成报告
    if data['type'] == 'horizontal':
        generate_horizontal_report(data, output_file)
    else:
        print("Vertical comparison report generation not implemented yet")

if __name__ == '__main__':
    main()