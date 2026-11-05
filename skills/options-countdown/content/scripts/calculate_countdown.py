#!/usr/bin/env python3
"""
期权近月合约剩余交易日计算脚本
计算所有上市期权品种距离近月合约到期还剩多少个交易日
"""

import json
from datetime import datetime, timedelta

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_trading_days():
    """获取交易日列表"""
    data = load_json('/workspace/temp-skills/options-countdown/references/trading_calendar_2026.json')
    return [datetime.strptime(d, '%Y-%m-%d') for d in data['trading_days']]

def get_month_trading_days(year, month, trading_days):
    """获取某月的所有交易日"""
    return [d for d in trading_days if d.year == year and d.month == month]

def get_nth_weekday(year, month, weekday, nth):
    """获取某月第n个星期几的日期"""
    # weekday: 0=Monday, 4=Friday
    days = get_month_trading_days(year, month, get_trading_days())
    weekdays_in_month = sorted([d for d in days if d.weekday() == weekday])
    if len(weekdays_in_month) >= nth:
        return weekdays_in_month[nth - 1]
    return None

def calculate_expiry_date_5th_friday(year, month):
    """计算某月第3个周五"""
    days = get_month_trading_days(year, month, get_trading_days())
    fridays = sorted([d for d in days if d.weekday() == 4])
    if len(fridays) >= 3:
        return fridays[2]
    return None

def get_contract_month(option_name, current_date):
    """确定近月合约月份"""
    current_month = current_date.month

    # 期货期权通常在当月、次月及后续季月上市
    # 近月通常是当月或次月合约
    # 判断当前是否已过月中，若是则近月可能是次月
    day = current_date.day

    # 以15号为分界：15日前近月为当月，15日后近月为次月
    if day <= 15:
        return current_month
    else:
        return (current_month % 12) + 1

def calculate_expiry_date(option_name, rule, year, month, trading_days):
    """根据到期规则计算到期日"""
    month_days = get_month_trading_days(year, month, trading_days)

    if not month_days:
        return None

    if rule['type'] == 'countback':
        # 倒数第N个交易日
        days_back = rule['days']
        if len(month_days) >= days_back:
            return month_days[-days_back]
        return None

    elif rule['type'] == 'forward':
        # 正数第N个交易日
        days_forward = rule['days']
        if len(month_days) >= days_forward:
            return month_days[days_forward - 1]
        return None

    elif rule['type'] == 'fixed_day_before':
        # 某日前第N个交易日
        target_day = rule['day']
        offset = rule['offset']
        # 找到该月第target_day天
        target_date = datetime(year, month, min(target_day, 28))
        # 从目标日期向前/后数offset个交易日
        if offset < 0:
            # 向前数
            count = abs(offset)
            target_idx = None
            for i, d in enumerate(month_days):
                if d.day == target_day:
                    target_idx = i
                    break
            if target_idx is not None and target_idx >= count:
                return month_days[target_idx - count]
        return None

    elif rule['type'] == 'nth_weekday':
        # 第N个周几
        weekday = rule['weekday']
        nth = rule['nth']
        return get_nth_weekday(year, month, weekday, nth)

    return None

def calculate_trading_days_remaining(expiry_date, current_date, trading_days):
    """计算从当前日期到到期日还剩多少个交易日（含头含尾）"""
    if expiry_date is None or expiry_date < current_date:
        return 0

    # 含头含尾：计算包括当前日和到期日在内的交易日数
    count = 0
    for d in trading_days:
        if d >= current_date and d <= expiry_date:
            count += 1
    return count

def get_next_contract_month(current_month, current_date, option_name, trading_days):
    """获取下一个可用合约月份"""
    year = current_date.year

    # 检查当月是否还有交易日
    current_month_days = get_month_trading_days(year, current_month, trading_days)
    if current_month_days and current_month_days[-1] > current_date:
        return current_month, year

    # 检查次月
    if current_month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = current_month + 1
        next_year = year

    next_month_days = get_month_trading_days(next_year, next_month, trading_days)
    if next_month_days and next_month_days[-1] > current_date:
        return next_month, next_year

    return None, None

def main():
    current_date = datetime(2026, 3, 21)  # 当前日期

    trading_days = get_trading_days()
    rules_data = load_json('/workspace/temp-skills/options-countdown/references/expiry_rules.json')
    options_data = load_json('/workspace/temp-skills/options-countdown/references/options_data.json')

    results = []

    for option in options_data['options']:
        option_name = option['name']

        # 找到对应的到期规则
        rule = None
        for r in rules_data['rules']:
            if r['option'] == option_name:
                rule = r
                break

        if rule is None:
            continue

        # 确定近月合约月份
        current_month = current_date.month
        contract_month, contract_year = get_next_contract_month(current_month, current_date, option_name, trading_days)

        # 如果当月已到期或不存在，尝试次月
        if contract_month is None:
            if current_month == 12:
                contract_month = 1
                contract_year = current_date.year + 1
            else:
                contract_month = current_month + 1

        # 计算到期日
        expiry_date = calculate_expiry_date(option_name, rule, contract_year, contract_month, trading_days)

        # 如果计算出的到期日已过，尝试下一月
        if expiry_date is None or expiry_date <= current_date:
            # 移动到下一月
            if contract_month == 12:
                contract_month = 1
                contract_year += 1
            else:
                contract_month += 1

            expiry_date = calculate_expiry_date(option_name, rule, contract_year, contract_month, trading_days)

        # 计算剩余交易日（含头含尾）
        remaining_days = calculate_trading_days_remaining(expiry_date, current_date, trading_days)

        if expiry_date and remaining_days > 0:
            results.append({
                'option': option_name,
                'exchange': option['exchange'],
                'contract_month': f"{contract_year}-{contract_month:02d}",
                'expiry_date': expiry_date.strftime('%Y-%m-%d'),
                'remaining_days': remaining_days,
                'rule': rule['rule']
            })

    # 按剩余交易日升序排序
    results.sort(key=lambda x: x['remaining_days'])

    # 输出结果
    print("=" * 80)
    print(f"📅 当前日期: {current_date.strftime('%Y-%m-%d')}")
    print("=" * 80)
    print()

    # 重点标识剩余交易日 <= 5 的品种
    warning_list = [r for r in results if r['remaining_days'] <= 5]
    normal_list = [r for r in results if r['remaining_days'] > 5]

    if warning_list:
        print("⚠️  【末日轮预警】剩余交易日 <= 5 的期权品种：")
        print("-" * 80)
        print(f"{'期权品种':<16} {'合约月份':<10} {'到期日':<12} {'剩余交易日':<10} {'规则'}")
        print("-" * 80)
        for r in warning_list:
            print(f"🔴 {r['option']:<12} {r['contract_month']:<10} {r['expiry_date']:<12} {r['remaining_days']:<10} {r['rule']}")
        print()

    print("📊 所有期权品种剩余交易日（升序）：")
    print("-" * 80)
    print(f"{'期权品种':<16} {'交易所':<8} {'合约月份':<10} {'到期日':<12} {'剩余交易日':<10} {'规则'}")
    print("-" * 80)

    for r in results:
        marker = "🔴" if r['remaining_days'] <= 5 else "  "
        print(f"{marker} {r['option']:<14} {r['exchange']:<8} {r['contract_month']:<10} {r['expiry_date']:<12} {r['remaining_days']:<10} {r['rule']}")

    print("-" * 80)
    print(f"总计: {len(results)} 个期权品种")
    print(f"末日轮预警 (<=5天): {len(warning_list)} 个品种")

if __name__ == '__main__':
    main()
