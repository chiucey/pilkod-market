#!/usr/bin/env python3
"""
Utility scripts package
包含各种辅助函数和工具
"""

def format_large_number(num):
    """格式化大数字"""
    if num is None:
        return "N/A"
    if num >= 1e12:
        return f"${num/1e12:.2f}T"
    elif num >= 1e9:
        return f"${num/1e9:.2f}B"
    elif num >= 1e6:
        return f"${num/1e6:.2f}M"
    else:
        return f"${num:,.0f}"


def format_percentage(value):
    """格式化百分比"""
    if value is None:
        return "N/A"
    return f"{value:+.2f}%"


def validate_ticker(ticker):
    """验证股票代码格式"""
    import re

    # 美股
    if re.match(r'^[A-Z]{1,5}$', ticker) and not ticker.isdigit():
        return "US"

    # A股
    if re.match(r'^[0-9]{6}$', ticker):
        return "CN"

    # 港股
    if re.match(r'^[0-9]{4,5}$', ticker):
        return "HK"
    if ticker.endswith('.HK'):
        return "HK"

    return "UNKNOWN"


if __name__ == "__main__":
    print("Utility functions for Stock Market Pro")
    print(format_large_number(1500000000))  # $1.50B
    print(format_percentage(3.5))  # +3.50%
    print(validate_ticker("AAPL"))  # US
    print(validate_ticker("600519"))  # CN
    print(validate_ticker("00700"))  # HK
