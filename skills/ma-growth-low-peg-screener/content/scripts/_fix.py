# Quick fix patch
import re

with open('/workspace/skills/ma-growth-low-peg-screener/scripts/screen.py', 'r') as f:
    content = f.read()

# Fix trade_cal line
old = '''    trade_cal = call_api("trade_cal", {"exchange": "SSE", "start_date": "20260401", "end_date": "20260416"})
    cal_items = [r for r in trade_cal.get("data", {}).get("items", []) if r[3] == 1]  # is_open=1'''
new = '''    trade_cal = call_api("trade_cal", {"exchange": "SSE", "start_date": "20260401", "end_date": "20260416"})
    cal_items_all = (trade_cal.get("data", {}).get("items", []) or []) if trade_cal else []
    cal_items = [r for r in cal_items_all if r[3] == 1]  # is_open=1'''

if old in content:
    content = content.replace(old, new)
    print("Fixed trade_cal line")
else:
    print("Pattern not found!")

with open('/workspace/skills/ma-growth-low-peg-screener/scripts/screen.py', 'w') as f:
    f.write(content)
print("Done")
