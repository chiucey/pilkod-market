#!/usr/bin/env python3
"""
批量渲染 — Python + Remotion Lambda
"""
import json, os, subprocess

# 示例：多组数据批量生成视频
video_props = [
    {"title": "Q1业绩报告", "quarter": "Q1", "revenue": 285, "growth": 12},
    {"title": "Q2业绩报告", "quarter": "Q2", "revenue": 342, "growth": 20},
    {"title": "Q3业绩报告", "quarter": "Q3", "revenue": 398, "growth": 18},
    {"title": "Q4业绩报告", "quarter": "Q4", "revenue": 428, "growth": 23},
]

OUTPUT = os.path.expanduser("~/.openclaw/remotion-output")
os.makedirs(OUTPUT, exist_ok=True)

for props in video_props:
    slug = props["quarter"]
    out_file = os.path.join(OUTPUT, f"{slug}.mp4")
    props_json = json.dumps(props)

    # 方案1：本地渲染
    cmd = f'''npx remotion render DataReportVideo "{out_file}" \
      --props='{props_json}' \
      --fps=30 \
      --codec=h264'''

    print(f"[{slug}] 渲染中...")
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode == 0:
        print(f"  ✓ 完成：{out_file}")
    else:
        print(f"  ✗ 失败：{r.stderr[:200]}")

print("\n全部完成！")
