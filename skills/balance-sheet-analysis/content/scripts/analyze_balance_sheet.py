#!/usr/bin/env python3
"""
Balance Sheet Analysis Script
Processes stock financial data and generates standardized balance sheet analysis tables
"""

import json
import sys
from typing import Dict, List, Any, Optional

def format_number(value: Any, is_percentage: bool = False, decimals: int = 2) -> str:
    """Format numeric output"""
    if value is None or value == '':
        return '-'
    try:
        num = float(value)
        if is_percentage:
            return f"{num:.2f}%"
        return f"{num:.2f}"
    except (ValueError, TypeError):
        return '-'

def calculate_net_cash(cash: float, debt: float) -> float:
    """Calculate Net Cash = Cash - Interest-bearing Debt"""
    return cash - debt

def calculate_working_capital(receivable: float, inventory: float, payable: float) -> float:
    """Calculate Working Capital = Receivables + Inventory - Payables"""
    return receivable + inventory - payable

def calculate_free_cash_flow(operating_cf: float, capex: float) -> float:
    """Calculate Free Cash Flow = Operating Cash Flow - Capital Expenditure"""
    return operating_cf - capex

def calculate_leverage_ratio(total_debt: float, total_assets: float) -> float:
    """Calculate Debt-to-Asset Ratio = Total Liabilities / Total Assets"""
    if total_assets == 0:
        return 0
    return (total_debt / total_assets) * 100

def generate_analysis_notes(data: Dict) -> Dict[str, str]:
    """Generate analysis notes based on data characteristics"""
    notes = {}

    # Cash reserve analysis
    latest_cash = data.get('cash', {}).get('latest', 0)
    if latest_cash > 100:
        notes['cash'] = "Abundant cash reserves, stable financial condition"
    elif latest_cash > 50:
        notes['cash'] = "Good cash reserves, sufficient liquidity"
    elif latest_cash > 0:
        notes['cash'] = "Moderate cash reserves, monitor liquidity"
    else:
        notes['cash'] = "Insufficient cash reserves, tight liquidity"

    # Leverage trend analysis
    leverage_ratios = data.get('leverage_ratio', [])
    if len(leverage_ratios) >= 2:
        latest = leverage_ratios[-1]
        previous = leverage_ratios[-2]
        if latest < previous - 2:
            notes['leverage'] = "Leverage ratio declining, financial structure improving"
        elif latest > previous + 2:
            notes['leverage'] = "Leverage ratio rising, monitor debt repayment pressure"
        else:
            notes['leverage'] = "Leverage ratio stable"

    # Cash flow quality analysis
    latest_fcf_ratio = data.get('fcf_ratio', {}).get('latest', 0)
    if latest_fcf_ratio > 0.8:
        notes['cash_flow'] = "Excellent cash flow quality"
    elif latest_fcf_ratio > 0.5:
        notes['cash_flow'] = "Good cash flow quality"
    elif latest_fcf_ratio > 0:
        notes['cash_flow'] = "Moderate cash flow, profit quality needs improvement"
    else:
        notes['cash_flow'] = "Negative cash flow, monitor capital chain"

    return notes

def generate_balance_sheet_table(financial_data: Dict, stock_name: str, stock_code: str) -> str:
    """Generate Balance Sheet Analysis Table"""

    # Extract annual data
    years = financial_data.get('years', [])
    balance_sheet = financial_data.get('balance_sheet', {})
    cash_flow = financial_data.get('cash_flow', {})
    income_statement = financial_data.get('income_statement', {})
    equity = financial_data.get('equity', {})

    # Build table data
    table_data = {
        'cash': {},
        'receivable': {},
        'inventory': {},
        'payable': {},
        'working_capital': {},
        'fixed_assets': {},
        'debt': {},
        'net_cash': {},
        'leverage_ratio': {},
        'current_assets': {},
        'non_current_assets': {},
        'total_liabilities': {},
        'liquidatable_assets': {},
        'operating_cf': {},
        'capex': {},
        'free_cash_flow': {},
        'profit': {},
        'fcf_ratio': {},
        'bvps': {}
    }

    # Process each year
    for year in years:
        bs = balance_sheet.get(year, {})
        cf = cash_flow.get(year, {})
        inc = income_statement.get(year, {})
        eq = equity.get(year, {})

        # Extract raw data
        cash = bs.get('cash_equivalents', 0) + bs.get('financial_assets', 0)
        receivable = bs.get('accounts_receivable', 0)
        inventory = bs.get('inventories', 0) + bs.get('contract_assets', 0)
        payable = bs.get('accounts_payable', 0)
        fixed_assets = bs.get('fixed_assets', 0) + bs.get('property_plant_equipment', 0)
        debt = bs.get('short_term_borrowings', 0) + bs.get('long_term_borrowings', 0)
        current_assets = bs.get('current_assets', 0)
        non_current_assets = bs.get('non_current_assets', 0)
        total_liabilities = bs.get('total_liabilities', 0)
        operating_cf = cf.get('operating_cash_flow', 0)
        capex = cf.get('capital_expenditure', 0)
        profit = inc.get('net_income', 0)
        total_assets = bs.get('total_assets', 0)
        shares = eq.get('total_shares', 1)

        # Calculate derived metrics
        working_capital = calculate_working_capital(receivable, inventory, payable)
        net_cash = calculate_net_cash(cash, debt)
        leverage_ratio = calculate_leverage_ratio(total_liabilities, total_assets)
        free_cash_flow = calculate_free_cash_flow(operating_cf, capex)
        fcf_ratio = profit / free_cash_flow if free_cash_flow != 0 else 0
        liquidatable_assets = current_assets - total_liabilities
        bvps = (total_assets - total_liabilities) / shares if shares > 0 else 0

        # Store data
        table_data['cash'][year] = cash
        table_data['receivable'][year] = receivable
        table_data['inventory'][year] = inventory
        table_data['payable'][year] = payable
        table_data['working_capital'][year] = working_capital
        table_data['fixed_assets'][year] = fixed_assets
        table_data['debt'][year] = debt
        table_data['net_cash'][year] = net_cash
        table_data['leverage_ratio'][year] = leverage_ratio
        table_data['current_assets'][year] = current_assets
        table_data['non_current_assets'][year] = non_current_assets
        table_data['total_liabilities'][year] = total_liabilities
        table_data['liquidatable_assets'][year] = liquidatable_assets
        table_data['operating_cf'][year] = operating_cf
        table_data['capex'][year] = capex
        table_data['free_cash_flow'][year] = free_cash_flow
        table_data['profit'][year] = profit
        table_data['fcf_ratio'][year] = fcf_ratio
        table_data['bvps'][year] = bvps

    # Generate notes
    notes = generate_analysis_notes(table_data)

    # Build output table
    output = []
    output.append(f"Stock Code: {stock_code}")
    output.append(f"Stock Name: {stock_name}")
    output.append(f"Analysis Date: 2026-04-01")
    output.append("")
    output.append("| Item | " + " | ".join(years) + " | Notes |")
    output.append("|" + "|".join(["---"] * (len(years) + 2)) + "|")

    # Define row items
    row_definitions = [
        ('Cash & Financial Assets', 'cash', False),
        ('Accounts Receivable', 'receivable', False),
        ('Contract Assets & Inventory', 'inventory', False),
        ('Accounts Payable', 'payable', False),
        ('Working Capital (Rec+Inv-Pay)', 'working_capital', False),
        ('Fixed Assets', 'fixed_assets', False),
        ('Interest-bearing Debt', 'debt', False),
        ('Net Cash', 'net_cash', False),
        ('Debt-to-Asset Ratio', 'leverage_ratio', True),
        ('Current Assets', 'current_assets', False),
        ('Non-current Assets', 'non_current_assets', False),
        ('Total Liabilities', 'total_liabilities', False),
        ('Liquidatable Assets (CA-TL)', 'liquidatable_assets', False),
        ('Operating Cash Flow', 'operating_cf', False),
        ('Capital Expenditure', 'capex', False),
        ('Free Cash Flow', 'free_cash_flow', False),
        ('Total Profit', 'profit', False),
        ('FCF/Profit Ratio', 'fcf_ratio', True),
        ('Book Value Per Share', 'bvps', False),
    ]

    # Generate each row
    for row_name, data_key, is_percentage in row_definitions:
        values = [format_number(table_data[data_key].get(year, '-'), is_percentage) for year in years]

        # Select appropriate notes for different metrics
        if data_key in ['cash', 'leverage_ratio', 'fcf_ratio']:
            note = notes.get(data_key.replace('_', '_'), '')
        elif data_key == 'cash':
            note = notes.get('cash', '')
        elif data_key == 'leverage_ratio':
            note = notes.get('leverage', '')
        elif data_key == 'fcf_ratio':
            note = notes.get('cash_flow', '')
        else:
            note = ''

        output.append(f"| {row_name} | " + " | ".join(values) + f" | {note} |")

    return "\n".join(output)


def main():
    """Main function: receives command line arguments and processes"""
    if len(sys.argv) < 2:
        print("Usage: python analyze_balance_sheet.py <stock_code>")
        sys.exit(1)

    stock_code = sys.argv[1]

    # This is where actual API calls would be made
    # Since API calls require MCP tools, this is just a sample structure
    print(f"Analyzing Stock Code: {stock_code}")
    print("Please use stocks_financial_data tool to get actual financial data for analysis")


if __name__ == "__main__":
    main()
