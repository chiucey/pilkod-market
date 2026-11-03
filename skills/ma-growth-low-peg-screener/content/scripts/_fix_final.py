with open('/workspace/skills/ma-growth-low-peg-screener/scripts/screen.py', 'r') as f:
    content = f.read()

old = '    cal_items_all = (trade_cal.get("data", {}).get("items", []) or []) if trade_cal else []'
new = '    _td = trade_cal.get("data", {}) if trade_cal else {}; cal_items_all = (_td.get("items") or []) if _td else []'

if old in content:
    content = content.replace(old, new)
    print("Replaced OK")
else:
    lines = content.split('\n')
    print("Not found. Lines 252-256:")
    for i,l in enumerate(lines[251:257], 252):
        print(f"  {i}: {repr(l)}")

with open('/workspace/skills/ma-growth-low-peg-screener/scripts/screen.py', 'w') as f:
    f.write(content)
