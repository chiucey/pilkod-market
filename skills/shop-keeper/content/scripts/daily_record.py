#!/usr/bin/env python3
"""
店铺管家 - 每日数据记录与分析脚本
用法: python3 daily_record.py [命令] [参数]
命令:
  record  日期  美团金额  饿了么金额  堂食金额  食材金额  [推广金额] [其他金额]
  report  [日期]           # 默认今天
  set_utility  月份  燃气金额  水电金额
  init                    # 初始化数据文件
"""

import json
import sys
import os
from datetime import datetime, timedelta

RECORDS_FILE = os.path.join(os.path.dirname(__file__), "..", "records.json")
MONTHLY_FILE = os.path.join(os.path.dirname(__file__), "..", "monthly_utilities.json")
COSTS_FILE = os.path.join(os.path.dirname(__file__), "references", "costs.md")

MONTHLY_FIXED_COST = 11945  # 月固定成本

# ---------- 工具函数 ----------

def load_records():
    if os.path.exists(RECORDS_FILE):
        with open(RECORDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_records(data):
    with open(RECORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_monthly():
    if os.path.exists(MONTHLY_FILE):
        with open(MONTHLY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_monthly(data):
    with open(MONTHLY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_date_key(date_str):
    """统一日期格式 YYYY-MM-DD"""
    if not date_str:
        return datetime.now().strftime("%Y-%m-%d")
    return date_str.strip()

def get_today_key():
    return datetime.now().strftime("%Y-%m-%d")

def get_yesterday_key():
    return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

def get_week_ago_key():
    return (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

def get_month_ago_key():
    return (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

def get_month_key():
    return datetime.now().strftime("%Y-%m")

def days_in_month(year_month):
    """获取某月的天数"""
    y, m = map(int, year_month.split("-"))
    if m == 12:
        return 31
    next_month = datetime(y, m + 1, 1)
    last_day = (next_month - timedelta(days=1)).day
    return last_day

def daily_fixed_cost(year_month=None):
    """计算日固定成本"""
    if year_month is None:
        year_month = get_month_key()
    days = days_in_month(year_month)
    return round(MONTHLY_FIXED_COST / days, 2)

def parse_amount(s):
    """解析金额字符串"""
    return float(str(s).strip().replace("元", "").replace("，", "").replace(",", ""))

def safe_get(data, key, default=0):
    return data.get(key, default)

# ---------- 命令实现 ----------

def cmd_record(args):
    """
    record YYYY-MM-DD 美团 饿了么 堂食 食材 [推广] [其他]
    """
    if len(args) < 6:
        print("参数不足，正确格式：record 日期 美团 饿了么 堂食 食材 [推广] [其他]")
        return

    date_key = args[0]
    meituan = parse_amount(args[1])
    eleme = parse_amount(args[2])
    dine_in = parse_amount(args[3])
    food_cost = parse_amount(args[4])
    ad_cost = parse_amount(args[5]) if len(args) > 5 else 0
    other_cost = parse_amount(args[6]) if len(args) > 6 else 0

    total_revenue = meituan + eleme + dine_in
    total_cost = food_cost + ad_cost + other_cost

    record = {
        "date": date_key,
        "revenue": {
            "美团": meituan,
            "饿了么": eleme,
            "堂食": dine_in,
            "合计": total_revenue
        },
        "cost": {
            "食材": food_cost,
            "推广": ad_cost,
            "其他": other_cost,
            "浮动合计": total_cost
        },
        "orders": total_revenue  # 营收作为订单标记
    }

    records = load_records()
    records[date_key] = record
    save_records(records)

    dc = daily_fixed_cost()
    gross_profit = total_revenue - total_cost
    net_profit = total_revenue - total_cost - dc

    print(f"✅ 记录已保存 [{date_key}]")
    print(f"   营收：{total_revenue:.2f}元（美团{meituan} + 饿了么{eleme} + 堂食{dine_in}）")
    print(f"   食材：{food_cost:.2f}元 | 推广：{ad_cost:.2f}元 | 其他：{other_cost:.2f}元")
    print(f"   毛利：{gross_profit:.2f}元 | 扣除日固定成本({dc:.2f}元)后利润：{net_profit:.2f}元")


def cmd_report(args):
    """显示对比报告"""
    # 确定目标日期
    if args:
        target_date = args[0]
    else:
        target_date = get_today_key()

    records = load_records()
    monthly = load_monthly()

    # 获取日期范围
    today = datetime.now()
    today_key = today.strftime("%Y-%m-%d")
    yesterday_key = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    week_ago_key = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    month_ago_key = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    current_month = today.strftime("%Y-%m")

    def get_day_data(d):
        return records.get(d, None)

    def calc_period(keys):
        total_rev = 0
        total_food = 0
        total_ad = 0
        total_other = 0
        count = 0
        for k in keys:
            if k in records:
                r = records[k]
                total_rev += r["revenue"]["合计"]
                total_food += r["cost"]["食材"]
                total_ad += r["cost"]["推广"]
                total_other += r["cost"]["其他"]
                count += 1
        return {
            "days": count,
            "revenue": round(total_rev, 2),
            "food_cost": round(total_food, 2),
            "ad_cost": round(total_ad, 2),
            "other_cost": round(total_other, 2),
            "daily_avg": round(total_rev / count, 2) if count > 0 else 0
        }

    # 今日数据
    today_data = get_day_data(today_key)
    # 昨日数据
    yesterday_data = get_day_data(yesterday_key)

    # 计算本周和上周
    this_week_keys = []
    last_week_keys = []
    for i in range(30):
        d = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        if d in records:
            if i < 7:
                this_week_keys.append(d)
            elif i < 14:
                last_week_keys.append(d)

    # 计算本月和上月
    this_month_keys = []
    last_month_keys = []
    for d, r in records.items():
        if d.startswith(current_month):
            this_month_keys.append(d)
        elif d.startswith(month_ago_key[:7]):
            last_month_keys.append(d)

    # 获取月度燃气水电
    month_utl = monthly.get(current_month, {})
    gas = month_utl.get("燃气", 0)
    elec = month_utl.get("水电", 0)

    # 日均燃气水电
    days_in_current = days_in_month(current_month)
    daily_gas = round(gas / days_in_current, 2) if gas else 0
    daily_elec = round(elec / days_in_current, 2) if elec else 0

    # 计算日均推广（本月）
    ad_days = len([d for d in records if d.startswith(current_month) and records[d]["cost"]["推广"] > 0])
    ad_total = sum(records[d]["cost"]["推广"] for d in records if d.startswith(current_month))
    daily_ad_avg = round(ad_total / ad_days, 2) if ad_days > 0 else 0

    dc = daily_fixed_cost(current_month)

    # ===== 打印报告 =====
    print()
    print("=" * 50)
    print(f"  🏪 店铺管家报告  [{target_date}]")
    print("=" * 50)

    # --- 今日 vs 昨日 ---
    print()
    print("📅 今日 vs 昨日")
    print("-" * 50)

    if today_data and yesterday_data:
        td = today_data
        yd = yesterday_data

        rev_t = td["revenue"]["合计"]
        rev_y = yd["revenue"]["合计"]
        fc_t = td["cost"]["食材"]; fc_y = yd["cost"]["食材"]
        ad_t = td["cost"]["推广"]; ad_y = yd["cost"]["推广"]
        gp_t = rev_t - fc_t - ad_t
        gp_y = rev_y - fc_y - ad_y
        np_t = gp_t - dc
        np_y = gp_y - dc

        def diff(a, b, is_rev=True):
            d = a - b
            sign = "+" if d > 0 else ""
            pct = (d / b * 100) if b != 0 else 0
            arrow = "↑" if d > 0 else ("↓" if d < 0 else "→")
            color = ("✅" if d > 0 else ("⚠️" if d < 0 else "➡️")) if is_rev else ("⚠️" if d > 0 else ("✅" if d < 0 else "➡️"))
            return f"{sign}{d:.2f}元 {arrow}{abs(pct):.1f}%", color

        r_diff, _ = diff(rev_t, rev_y)
        f_diff, _ = diff(fc_t, fc_y, is_rev=False)
        gp_diff, gp_col = diff(gp_t, gp_y)
        np_diff, np_col = diff(np_t, np_y)

        print(f"  今日营收：{rev_t:.2f}元  vs 昨日：{rev_y:.2f}元  ({r_diff})")
        print(f"  今日食材：{fc_t:.2f}元  vs 昨日：{fc_y:.2f}元  ({f_diff})")
        print(f"  今日毛利：{gp_t:.2f}元  vs 昨日：{gp_y:.2f}元  ({gp_col}{gp_diff})")
        print(f"  今日利润：{np_t:.2f}元  vs 昨日：{np_y:.2f}元  ({np_col}{np_diff})")
        print(f"  （日固定成本分摊：{dc:.2f}元/日）")
    elif today_data:
        print(f"  今日：营收{today_data['revenue']['合计']:.2f}元 | 食材{today_data['cost']['食材']:.2f}元 | 毛利{today_data['revenue']['合计']-today_data['cost']['浮动合计']:.2f}元 | 利润{today_data['revenue']['合计']-today_data['cost']['浮动合计']-dc:.2f}元")
        print(f"  （昨日数据尚未录入）")
    elif yesterday_data:
        print(f"  昨日：营收{yesterday_data['revenue']['合计']:.2f}元 | 食材{yesterday_data['cost']['食材']:.2f}元 | 毛利{yesterday_data['revenue']['合计']-yesterday_data['cost']['浮动合计']:.2f}元 | 利润{yesterday_data['revenue']['合计']-yesterday_data['cost']['浮动合计']-dc:.2f}元")
        print(f"  （今日数据尚未录入）")
    else:
        print("  今日和昨日数据均未录入，请先发送今日数据。")

    # --- 本周 vs 上周 ---
    print()
    print("📆 本周（近7天）vs 上周（8-14天）")
    print("-" * 50)

    if this_week_keys:
        tw = calc_period(this_week_keys)
        lw = calc_period(last_week_keys)
        rev_tw = tw["revenue"]; rev_lw = lw["revenue"]
        fc_tw = tw["food_cost"]; fc_lw = lw["food_cost"]
        gp_tw = rev_tw - fc_tw; gp_lw = rev_lw - fc_lw
        d_diff, d_col = (f"+{tw['days']-lw['days']}天", "✅") if tw["days"] > lw["days"] else (f"{tw['days']-lw['days']}天", "➡️")
        r_diff, _ = (f"+{rev_tw-rev_lw:.2f}元 ↑{(rev_tw-rev_lw)/rev_lw*100:.1f}%", "✅") if rev_lw > 0 else ("N/A", "")
        gp_diff, gp_col = (f"+{gp_tw-gp_lw:.2f}元", "✅") if gp_tw > gp_lw else (f"{gp_tw-gp_lw:.2f}元", "⚠️")

        print(f"  本周天数：{tw['days']}天 vs 上周：{lw['days']}天")
        print(f"  本周总营收：{rev_tw:.2f}元 vs 上周：{rev_lw:.2f}元  ({r_diff})")
        print(f"  本周日均：{tw['daily_avg']:.2f}元 vs 上周：{lw['daily_avg']:.2f}元")
        print(f"  本周毛利：{gp_tw:.2f}元 vs 上周：{gp_lw:.2f}元  ({gp_col}{gp_diff})")
    else:
        print("  本周暂无数据")

    # --- 本月 vs 上月 ---
    print()
    print(f"📆 本月（{current_month}）vs 上月")
    print("-" * 50)

    tm = calc_period(this_month_keys)
    lm = calc_period(last_month_keys)

    rev_tm = tm["revenue"]; rev_lm = lm["revenue"]
    fc_tm = tm["food_cost"]; fc_lm = lm["food_cost"]
    ad_tm = tm["ad_cost"]; ad_lm = lm["ad_cost"]
    gp_tm = rev_tm - fc_tm; gp_lm = rev_lm - fc_lm
    daily_tm = round(rev_tm / tm["days"], 1) if tm["days"] > 0 else 0

    # 月度固定成本
    month_dc = MONTHLY_FIXED_COST
    np_tm = gp_tm - month_dc - ad_tm - gas - elec
    np_lm = gp_lm - month_dc - ad_lm - gas - elec

    def mo_diff(a, b):
        d = a - b
        sign = "+" if d > 0 else ""
        pct = (d / abs(b) * 100) if b != 0 else 0
        arrow = "↑" if d > 0 else "↓"
        return f"{sign}{d:.0f}元 {arrow}{abs(pct):.1f}%"

    print(f"  本月天数：{tm['days']}天 | 上月天数：{lm['days']}天")
    print(f"  本月总营收：{rev_tm:.2f}元 | 上月：{rev_lm:.2f}元  ({mo_diff(rev_tm, rev_lm)})")
    print(f"  本月日均：{daily_tm:.2f}元")
    print(f"  本月食材成本：{fc_tm:.2f}元 | 上月：{fc_lm:.2f}元")
    print(f"  本月推广成本：{ad_tm:.2f}元 | 上月：{ad_lm:.2f}元")
    print(f"  本月燃气：{gas:.2f}元 | 水电：{elec:.2f}元")
    print(f"  本月毛利：{gp_tm:.2f}元 | 上月：{gp_lm:.2f}元")
    print(f"  本月净利润：{np_tm:.2f}元 | 上月：{np_lm:.2f}元")
    print(f"  （月固定成本：{month_dc:.2f}元 已扣除）")

    # --- 月度目标进度 ---
    print()
    print("🎯 月度目标进度")
    print("-" * 50)
    monthly_revenue_goal = float(os.environ.get("MONTHLY_GOAL", "0"))
    if monthly_revenue_goal > 0:
        progress = rev_tm / monthly_revenue_goal * 100
        bar_len = 20
        filled = int(bar_len * progress / 100)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"  营收目标：{rev_tm:.2f} / {monthly_revenue_goal:.2f}元 [{bar}] {progress:.1f}%")
    else:
        print("  （未设置月度目标，可回复'设置月度目标XXXX元'来设定）")

    print()
    print("=" * 50)


def cmd_set_utility(args):
    """设置月度燃气水电"""
    if len(args) < 3:
        print("格式：set_utility YYYY-MM 燃气 水电")
        return

    month_key = args[0]
    gas = parse_amount(args[1])
    elec = parse_amount(args[2])

    monthly = load_monthly()
    monthly[month_key] = {"燃气": gas, "水电": elec}
    save_monthly(monthly)

    print(f"✅ 已保存 {month_key} 燃气{gas:.2f}元、水电{elec:.2f}元")


def cmd_init():
    """初始化数据文件"""
    if not os.path.exists(RECORDS_FILE):
        save_records({})
    if not os.path.exists(MONTHLY_FILE):
        save_monthly({})
    print("✅ 数据文件初始化完成")


# ---------- 主入口 ----------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "record":
        cmd_record(args)
    elif cmd == "report":
        cmd_report(args)
    elif cmd == "set_utility":
        cmd_set_utility(args)
    elif cmd == "init":
        cmd_init()
    else:
        print(f"未知命令：{cmd}")
        print(__doc__)
