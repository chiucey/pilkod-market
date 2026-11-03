#!/usr/bin/env python3
"""
客户分析脚本 — RFM分析、客户聚类、生命周期价值计算

用法:
    python customer_analysis.py --input data.csv --output results/

输入 CSV 必须包含以下字段:
    customer_id, order_date, order_id, revenue

可选字段:
    product_category, channel, region
"""

import pandas as pd
import numpy as np
from datetime import datetime, date
import argparse
import os
import warnings
warnings.filterwarnings('ignore')


# ============================================================
# RFM 分析
# ============================================================

def calculate_rfm(df: pd.DataFrame, analysis_date=None) -> pd.DataFrame:
    """
    计算客户 RFM 指标并打分。

    Args:
        df: 包含 customer_id, order_date, order_id, revenue 的 DataFrame
        analysis_date: 分析基准日期，默认为数据最大日期

    Returns:
        带 RFM 评分和客户细分标签的 DataFrame
    """
    df = df.copy()
    df['order_date'] = pd.to_datetime(df['order_date'])

    if analysis_date is None:
        analysis_date = df['order_date'].max()

    # 计算 RFM 原始值
    rfm = df.groupby('customer_id').agg(
        recency   = ('order_date',  lambda x: (analysis_date - x.max()).days),
        frequency = ('order_id',    'nunique'),
        monetary  = ('revenue',     'sum')
    ).reset_index()

    # 分位数打分（1-5）
    rfm['r_score'] = pd.qcut(rfm['recency'],  5, labels=[5, 4, 3, 2, 1], duplicates='drop')
    rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    rfm['m_score'] = pd.qcut(rfm['monetary'],  5, labels=[1, 2, 3, 4, 5], duplicates='drop')

    rfm['rfm_score'] = (rfm['r_score'].astype(str)
                        + rfm['f_score'].astype(str)
                        + rfm['m_score'].astype(str))

    # 打分总分（加权：R=0.4, F=0.35, M=0.25）
    rfm['rfm_total'] = (rfm['r_score'].astype(int) * 0.4
                        + rfm['f_score'].astype(int) * 0.35
                        + rfm['m_score'].astype(int) * 0.25)

    rfm['segment'] = rfm.apply(_segment_customer, axis=1)
    return rfm


def _segment_customer(row) -> str:
    """根据 RFM 评分进行客户细分。"""
    r = int(row['r_score'])
    f = int(row['f_score'])
    m = int(row['m_score'])

    if r >= 4 and f >= 4 and m >= 4:
        return '冠军客户'
    elif f >= 4 and m >= 4:
        return '忠诚客户'
    elif r >= 4 and f <= 2:
        return '潜力客户'
    elif r >= 4 and f <= 1 and m <= 2:
        return '新客户'
    elif r <= 2 and f >= 3:
        return '高风险客户'
    elif r <= 2 and f <= 2:
        return '流失客户'
    else:
        return '一般客户'


def rfm_summary(rfm: pd.DataFrame) -> dict:
    """生成 RFM 分析摘要统计。"""
    summary = {
        'total_customers': len(rfm),
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        'segment_distribution': rfm['segment'].value_counts().to_dict(),
        'segment_revenue': rfm.groupby('segment')['monetary'].sum().sort_values(ascending=False).to_dict(),
        'segment_avg_value': rfm.groupby('segment')['monetary'].mean().round(2).to_dict(),
        'top_10pct_revenue_share': round(
            rfm.nlargest(int(len(rfm) * 0.1), 'monetary')['monetary'].sum() / rfm['monetary'].sum() * 100, 1
        ),
    }
    return summary


# ============================================================
# 客户生命周期价值 (CLV)
# ============================================================

def calculate_clv(df: pd.DataFrame,
                  discount_rate: float = 0.1,
                  projection_months: int = 12) -> pd.DataFrame:
    """
    计算简化版客户生命周期价值（基于历史行为外推）。

    Args:
        df: 包含 customer_id, order_date, revenue 的 DataFrame
        discount_rate: 年折现率（默认10%）
        projection_months: 预测月数（默认12个月）

    Returns:
        包含 CLV 估算值的 DataFrame
    """
    df = df.copy()
    df['order_date'] = pd.to_datetime(df['order_date'])

    # 每客户历史统计
    customer_stats = df.groupby('customer_id').agg(
        total_revenue  = ('revenue', 'sum'),
        total_orders   = ('order_id', 'nunique'),
        first_order    = ('order_date', 'min'),
        last_order     = ('order_date', 'max')
    ).reset_index()

    # 客户生命周期（月）
    customer_stats['lifetime_months'] = (
        (customer_stats['last_order'] - customer_stats['first_order']).dt.days / 30
    ).clip(lower=1)

    # 月均消费 & 月均订单频率
    customer_stats['avg_monthly_revenue'] = (
        customer_stats['total_revenue'] / customer_stats['lifetime_months']
    )
    customer_stats['avg_monthly_orders'] = (
        customer_stats['total_orders'] / customer_stats['lifetime_months']
    )

    # 简化 CLV：月均收入 × 预测月数 × 折现因子
    monthly_discount = discount_rate / 12
    discount_factor = (1 - (1 + monthly_discount) ** (-projection_months)) / monthly_discount

    customer_stats['clv_projected'] = (
        customer_stats['avg_monthly_revenue'] * discount_factor
    ).round(2)

    customer_stats['clv_tier'] = pd.qcut(
        customer_stats['clv_projected'],
        q=[0, 0.25, 0.5, 0.75, 1.0],
        labels=['低价值', '中等价值', '高价值', '超高价值'],
        duplicates='drop'
    )

    return customer_stats


# ============================================================
# 流失预测（基于规则）
# ============================================================

def churn_risk_scoring(rfm: pd.DataFrame,
                       days_threshold_medium: int = 60,
                       days_threshold_high: int = 120) -> pd.DataFrame:
    """
    基于 RFM 指标打流失风险分。

    Args:
        rfm: rfm DataFrame（含 recency, frequency, monetary）
        days_threshold_medium: 中等风险天数阈值
        days_threshold_high: 高风险天数阈值

    Returns:
        带流失风险评级的 DataFrame
    """
    df = rfm.copy()

    def risk_level(row):
        if row['recency'] > days_threshold_high and row['frequency'] < 3:
            return '高风险'
        elif row['recency'] > days_threshold_medium:
            return '中风险'
        elif row['recency'] > 30 and int(row['r_score']) <= 2:
            return '低风险'
        else:
            return '健康'

    df['churn_risk'] = df.apply(risk_level, axis=1)
    return df


# ============================================================
# 主程序
# ============================================================

def main():
    parser = argparse.ArgumentParser(description='客户 RFM 分析工具')
    parser.add_argument('--input',  required=True, help='输入 CSV 文件路径')
    parser.add_argument('--output', default='./output', help='输出目录')
    parser.add_argument('--date',   default=None, help='分析基准日期 YYYY-MM-DD')
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    print(f"📂 读取数据: {args.input}")
    df = pd.read_csv(args.input)
    print(f"   原始记录数: {len(df):,}")

    # RFM 分析
    analysis_date = pd.to_datetime(args.date) if args.date else None
    print("\n🔍 执行 RFM 分析...")
    rfm = calculate_rfm(df, analysis_date)

    # 流失风险
    rfm = churn_risk_scoring(rfm)

    # CLV
    print("💰 计算客户生命周期价值...")
    clv = calculate_clv(df)
    rfm = rfm.merge(clv[['customer_id', 'clv_projected', 'clv_tier',
                           'avg_monthly_revenue']], on='customer_id', how='left')

    # 保存结果
    output_path = os.path.join(args.output, 'rfm_analysis.csv')
    rfm.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n✅ 分析结果已保存: {output_path}")

    # 打印摘要
    summary = rfm_summary(rfm)
    print(f"\n📊 分析摘要")
    print(f"   总客户数: {summary['total_customers']:,}")
    print(f"   前10%客户贡献收入占比: {summary['top_10pct_revenue_share']}%")
    print(f"\n   客户细分分布:")
    for seg, count in sorted(summary['segment_distribution'].items(),
                              key=lambda x: x[1], reverse=True):
        avg_val = summary['segment_avg_value'].get(seg, 0)
        print(f"     {seg}: {count:,} 人  均值: ¥{avg_val:,.0f}")

    high_risk = rfm[rfm['churn_risk'] == '高风险']
    print(f"\n   ⚠️  高流失风险客户: {len(high_risk):,} 人")
    print(f"      预计损失收入: ¥{high_risk['monetary'].sum():,.0f}")


if __name__ == '__main__':
    main()
