#!/usr/bin/env bash
# 把 Chart.js 库 + shell 模板 + REPORT_DATA 数据 拼装成单文件 HTML 报告。
# 用法：build-report.sh <data.json 路径> <输出 html 路径>
# data.json 必须是符合 shell 模板 REPORT_DATA 结构的 JSON。
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"   # skill 根目录
LIB="$HERE/assets/chart.umd.min.js"
SHELL_HTML="$HERE/assets/report-shell.html"
DATA="${1:?用法: build-report.sh <data.json> <out.html>}"
OUT="${2:?用法: build-report.sh <data.json> <out.html>}"

[ -f "$LIB" ] || { echo "缺 $LIB"; exit 1; }
[ -f "$SHELL_HTML" ] || { echo "缺 $SHELL_HTML"; exit 1; }
[ -f "$DATA" ] || { echo "缺数据文件 $DATA"; exit 1; }

# 用 python 做占位符替换（避免 sed 对特殊字符转义的坑）
python3 - "$LIB" "$SHELL_HTML" "$DATA" "$OUT" <<'PY'
import sys, json, pathlib
lib, shell, data, out = sys.argv[1:5]
libjs   = pathlib.Path(lib).read_text(encoding='utf-8')
html    = pathlib.Path(shell).read_text(encoding='utf-8')
raw     = pathlib.Path(data).read_text(encoding='utf-8')
d = json.loads(raw)  # 校验 JSON 合法，非法直接抛错
kw = str(d.get('keyword','小红书热点报告'))
html = html.replace('__CHARTJS__', libjs)
html = html.replace('__TITLE__', kw + ' · 小红书热点报告')
html = html.replace('__REPORT_DATA__', raw)
pathlib.Path(out).write_text(html, encoding='utf-8')
print('已生成', out, len(html), '字节')
PY
