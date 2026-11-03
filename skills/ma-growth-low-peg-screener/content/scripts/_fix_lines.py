import re

with open('/workspace/skills/ma-growth-low-peg-screener/scripts/screen.py', 'r') as f:
    content = f.read()

# Fix the conditional expression issue - need to use proper if/else
old = '    cal_items_all = (trade_cal.get("data", {}).get("items", []) or []) if trade_cal else []'
new = '    cal_items_all = trade_cal.get("data", {}).get("items", []) or [] if trade_cal else []'

if old in content:
    content = content.replace(old, new)
    print("Pattern found")
else:
    print("Not found")

with open('/workspace/skills/ma-growth-low-peg-screener/scripts/screen.py', 'w') as f:
    f.write(content)
print("Written")
