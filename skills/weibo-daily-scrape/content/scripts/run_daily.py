#!/usr/bin/env python3
"""
咪咕微博每日内容调度脚本
自动判断真实/演示模式，生成Excel并输出文件路径
"""
import subprocess, sys, os, json, re
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
COOKIE_FILE = os.path.join(SCRIPT_DIR, "weibo_cookies.json")
DATA_DIR = os.path.join(SKILL_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

def get_date_window():
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")
    return date_str

def load_cookie():
    if not os.path.exists(COOKIE_FILE):
        return None
    try:
        with open(COOKIE_FILE) as f:
            cfg = json.load(f)
        return cfg if cfg.get("enabled") and cfg.get("cookie") else None
    except:
        return None

def main():
    date_str = get_date_window()
    cookie = load_cookie()
    mode = "真实模式" if cookie else "演示模式"
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 咪咕微博抓取开始 | 模式：{mode} | 日期：{date_str}")

    result = subprocess.run(
        ["node", os.path.join(SCRIPT_DIR, "scrape_weibo.js")],
        cwd=SCRIPT_DIR, capture_output=True, text=True
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    xlsx_file = os.path.join(DATA_DIR, f"{date_str}.xlsx")
    json_file = os.path.join(DATA_DIR, f"{date_str}.json")

    print(f"\n完成：{date_str}")
    print(f"JSON：{json_file}")
    print(f"Excel：{xlsx_file}")
    print(f"EXCEL_PATH:{xlsx_file}")

if __name__ == "__main__":
    main()
