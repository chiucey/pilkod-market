#!/usr/bin/env python3
"""
判断今日是否为 A 股交易日
逻辑：周一至周五为潜在交易日，排除中国法定节假日
"""

import datetime, os, json

def is_trading_day():
    today = datetime.date.today()
    weekday = today.weekday()  # 0=周一, 6=周日

    # 周六周日直接判定为非交易日
    if weekday >= 5:
        return False

    holidays = get_holidays()

    return today not in holidays

def get_holidays():
    """获取节假日列表，从配置文件读取或使用默认"""
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)
    config_file = os.path.join(skill_dir, 'config', 'stocks.json')
    
    # 尝试从配置文件读取节假日（如果配置文件存在且包含节假日配置）
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if 'holidays' in config:
                    return [datetime.date.fromisoformat(h) for h in config['holidays']]
        except:
            pass
    
    # 默认节假日
    year = datetime.date.today().year
    return [
        # 元旦
        datetime.date(year, 1, 1),
        # 春节（根据实际情况调整）
        datetime.date(year, 2, 15), datetime.date(year, 2, 16), datetime.date(year, 2, 17),
        datetime.date(year, 2, 18), datetime.date(year, 2, 19), datetime.date(year, 2, 20),
        datetime.date(year, 2, 21),
        # 清明节
        datetime.date(year, 4, 4), datetime.date(year, 4, 5), datetime.date(year, 4, 6),
        # 劳动节
        datetime.date(year, 5, 1), datetime.date(year, 5, 2), datetime.date(year, 5, 3),
        datetime.date(year, 5, 4), datetime.date(year, 5, 5),
        # 端午节
        datetime.date(year, 5, 31), datetime.date(year, 6, 1), datetime.date(year, 6, 2),
        # 中秋节/国庆节
        datetime.date(year, 10, 1), datetime.date(year, 10, 2), datetime.date(year, 10, 3),
        datetime.date(year, 10, 4), datetime.date(year, 10, 5), datetime.date(year, 10, 6),
        datetime.date(year, 10, 7), datetime.date(year, 10, 8),
    ]

if __name__ == '__main__':
    exit(0 if is_trading_day() else 1)