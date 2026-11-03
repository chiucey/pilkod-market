#!/usr/bin/env python3
"""
Cost Growth Analysis Script
Analyze cloud bill data from two periods to calculate growth ratio, magnitude, and contribution
"""

import pandas as pd
import sys
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows


def load_and_prepare_data(file_path):
    """Load and preprocess Excel data"""
    df = pd.read_excel(file_path, sheet_name='Sheet1')

    # Ensure cost column is numeric type
    df['成本（元）'] = pd.to_numeric(df['成本（元）'], errors='coerce').fillna(0)

    # Get period identifier
    if '账单出账月份' in df.columns:
        period = df['账单出账月份'].iloc[0]
    elif '账单出账日期' in df.columns:
        period = df['账单出账日期'].iloc[0]
    else:
        period = 'Unknown'

    return df, period


def aggregate_by_dimension(df, dimensions):
    """Aggregate cost by specified dimensions"""
    agg_df = df.groupby(dimensions, as_index=False)['成本（元）'].sum()
    return agg_df


def calculate_growth_metrics(df_before, df_after, dimensions):
    """Calculate growth metrics"""
    # Aggregate data
    agg_before = aggregate_by_dimension(df_before, dimensions)
    agg_after = aggregate_by_dimension(df_after, dimensions)

    # Merge for comparison
    merged = pd.merge(
        agg_before,
        agg_after,
        on=dimensions,
        how='outer',
        suffixes=('_start', '_end')
    ).fillna(0)

    merged['成本（元）_start'] = merged['成本（元）_start'].clip(lower=0)
    merged['成本（元）_end'] = merged['成本（元）_end'].clip(lower=0)

    # Calculate growth metrics
    merged['growth_amount'] = merged['成本（元）_end'] - merged['成本（元）_start']

    # Growth rate (avoid division by zero)
    merged['growth_rate_pct'] = merged.apply(
        lambda x: ((x['成本（元）_end'] - x['成本（元）_start']) / x['成本（元）_start'] * 100)
        if x['成本（元）_start'] > 0 else (100 if x['成本（元）_end'] > 0 else 0),
        axis=1
    )

    return merged


def calculate_contribution(df_before, df_after, dimensions):
    """Calculate growth contribution"""
    growth_df = calculate_growth_metrics(df_before, df_after, dimensions)

    total_growth = growth_df['growth_amount'].sum()

    if total_growth != 0:
        # Use absolute value for contribution calculation
        abs_total_growth = abs(total_growth)
        growth_df['contribution_pct'] = growth_df['growth_amount'] / abs_total_growth * 100

        if total_growth > 0:
            # Positive overall growth - sort descending
            growth_df['is_positive_contributor'] = growth_df['growth_amount'] > 0
            growth_df = growth_df.sort_values('growth_amount', ascending=False)
        else:
            # Negative overall growth - show contributors to reduction
            growth_df['is_positive_contributor'] = growth_df['growth_amount'] < 0
            growth_df = growth_df.sort_values('growth_amount', ascending=True)  # Most negative first

        growth_df['cumulative_contribution_pct'] = growth_df['contribution_pct'].cumsum()
    else:
        growth_df['contribution_pct'] = 0
        growth_df['cumulative_contribution_pct'] = 0
        growth_df['is_positive_contributor'] = False
        growth_df = growth_df.sort_values('growth_amount', ascending=False)

    return growth_df


def generate_summary(df_before, df_after, period_before, period_after):
    """Generate overall summary data"""
    total_before = df_before['成本（元）'].sum()
    total_after = df_after['成本（元）'].sum()
    total_growth = total_after - total_before

    growth_rate = ((total_after - total_before) / total_before * 100) if total_before > 0 else 0

    return {
        'Metric': ['Start Cost (CNY)', 'End Cost (CNY)', 'Growth Amount (CNY)', 'Growth Rate (%)', 'Start Period', 'End Period'],
        'Value': [round(total_before, 2), round(total_after, 2), round(total_growth, 2),
               round(growth_rate, 2), period_before, period_after]
    }


def detect_anomalies(growth_df, threshold_rate=50):
    """Detect abnormal growth items"""
    anomalies = growth_df[
        (growth_df['growth_rate_pct'] > threshold_rate) & (growth_df['成本（元）_end'] > 1000)
    ].copy()

    anomalies['anomaly_type'] = 'High Growth Rate'
    anomalies.loc[anomalies['growth_amount'] > 10000, 'anomaly_type'] = 'Significant Growth'

    return anomalies


def create_excel_report(
    df_before, df_after,
    period_before, period_after,
    output_path
):
    """Create Excel analysis report"""
    wb = Workbook()

    # Style definitions
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # Sheet 1: Overview
    ws_summary = wb.active
    ws_summary.title = "Overview"

    summary_data = generate_summary(df_before, df_after, period_before, period_after)
    summary_df = pd.DataFrame(summary_data)

    for r_idx, row in enumerate(dataframe_to_rows(summary_df, index=False, header=True), 1):
        for c_idx, value in enumerate(row, 1):
            cell = ws_summary.cell(row=r_idx, column=c_idx, value=value)
            cell.border = thin_border
            if r_idx == 1:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center')

    # Sheet 2: Level 1 Category Growth Analysis
    ws_l1 = wb.create_sheet("L1 Growth Analysis")
    growth_l1 = calculate_growth_metrics(df_before, df_after, ['资源一级分类'])
    growth_l1 = growth_l1.sort_values('growth_amount', ascending=False)

    for r_idx, row in enumerate(dataframe_to_rows(growth_l1, index=False, header=True), 1):
        for c_idx, value in enumerate(row, 1):
            cell = ws_l1.cell(row=r_idx, column=c_idx, value=round(value, 2) if isinstance(value, float) else value)
            cell.border = thin_border
            if r_idx == 1:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center')

    # Sheet 3: Level 2 Category Growth Analysis
    ws_l2 = wb.create_sheet("L2 Growth Analysis")
    growth_l2 = calculate_growth_metrics(df_before, df_after, ['资源一级分类', '资源二级分类'])
    growth_l2 = growth_l2.sort_values('growth_amount', ascending=False)

    for r_idx, row in enumerate(dataframe_to_rows(growth_l2, index=False, header=True), 1):
        for c_idx, value in enumerate(row, 1):
            cell = ws_l2.cell(row=r_idx, column=c_idx, value=round(value, 2) if isinstance(value, float) else value)
            cell.border = thin_border
            if r_idx == 1:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center')

    # Sheet 4: Contribution Analysis
    ws_contrib = wb.create_sheet("Contribution Analysis")
    contrib_l1 = calculate_contribution(df_before, df_after, ['资源一级分类'])
    contrib_l1 = contrib_l1[['资源一级分类', '成本（元）_start', '成本（元）_end',
                             'growth_amount', 'growth_rate_pct', 'contribution_pct',
                             'cumulative_contribution_pct', 'is_positive_contributor']]

    for r_idx, row in enumerate(dataframe_to_rows(contrib_l1, index=False, header=True), 1):
        for c_idx, value in enumerate(row, 1):
            cell = ws_contrib.cell(row=r_idx, column=c_idx, value=value)
            cell.border = thin_border
            if r_idx == 1:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center')

    # Sheet 5: TOP Growth Resources
    ws_top = wb.create_sheet("TOP Growth Resources")
    contrib_detail = calculate_contribution(df_before, df_after, ['资源一级分类', '资源二级分类', 'PSA'])
    contrib_detail = contrib_detail[contrib_detail['growth_amount'] > 0].head(20)
    contrib_detail = contrib_detail[['资源一级分类', '资源二级分类', 'PSA',
                                     '成本（元）_start', '成本（元）_end',
                                     'growth_amount', 'growth_rate_pct', 'contribution_pct']]

    for r_idx, row in enumerate(dataframe_to_rows(contrib_detail, index=False, header=True), 1):
        for c_idx, value in enumerate(row, 1):
            cell = ws_top.cell(row=r_idx, column=c_idx, value=round(value, 2) if isinstance(value, float) else value)
            cell.border = thin_border
            if r_idx == 1:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center')

    # Sheet 6: Anomaly Alert
    ws_anomaly = wb.create_sheet("Anomaly Alert")
    growth_all = calculate_growth_metrics(df_before, df_after, ['资源一级分类', '资源二级分类', 'PSA'])
    anomalies = detect_anomalies(growth_all)

    if len(anomalies) > 0:
        anomaly_cols = ['资源一级分类', '资源二级分类', 'PSA', '成本（元）_start',
                        '成本（元）_end', 'growth_amount', 'growth_rate_pct', 'anomaly_type']
        anomalies = anomalies[anomaly_cols]

        for r_idx, row in enumerate(dataframe_to_rows(anomalies, index=False, header=True), 1):
            for c_idx, value in enumerate(row, 1):
                cell = ws_anomaly.cell(row=r_idx, column=c_idx, value=round(value, 2) if isinstance(value, float) else value)
                cell.border = thin_border
                if r_idx == 1:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal='center')
    else:
        ws_anomaly['A1'] = "No significant abnormal growth detected (threshold: growth rate > 50% and end cost > 1000 CNY)"

    # Save file
    wb.save(output_path)
    return output_path


def main(file_before, file_after, output_path):
    """Main function"""
    print(f"Loading start period data: {file_before}")
    df_before, period_before = load_and_prepare_data(file_before)
    print(f"Loading end period data: {file_after}")
    df_after, period_after = load_and_prepare_data(file_after)

    print(f"\nStart Period: {period_before}")
    print(f"End Period: {period_after}")
    print(f"Total Start Cost: {df_before['成本（元）'].sum():,.2f} CNY")
    print(f"Total End Cost: {df_after['成本（元）'].sum():,.2f} CNY")

    print("\nGenerating analysis report...")
    output = create_excel_report(
        df_before, df_after,
        period_before, period_after,
        output_path
    )

    print(f"\nAnalysis report generated: {output}")
    return output


if __name__ == "__main__":
    if len(sys.argv) >= 4:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print("Usage: python analyze_cost_growth.py <start_period_file> <end_period_file> <output_file>")
