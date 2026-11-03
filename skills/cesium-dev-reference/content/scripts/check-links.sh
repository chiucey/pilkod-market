#!/usr/bin/env bash
#
# scripts/check-links.sh
#
# 批量检查所有 .md 文件中外部链接的 HTTP 状态码。
#
# 用法:
#   bash scripts/check-links.sh                 # 默认 5s 超时
#   bash scripts/check-links.sh --timeout=10    # 10s 超时
#   bash scripts/check-links.sh --output=report.txt  # 写到文件
#
# 输出:
#   - 状态码 200:OK
#   - 301/302:重定向(后续脚本可读 URL 自动更新)
#   - 404:失效(从文档移除)
#   - 5xx:服务异常(稍后重试)

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TIMEOUT=5
OUTPUT=""

for arg in "$@"; do
  case "$arg" in
    --timeout=*) TIMEOUT="${arg#*=}" ;;
    --output=*) OUTPUT="${arg#*=}" ;;
    *) ;;
  esac
done

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[0;33m'; RESET='\033[0m'

TMP_LINKS=$(mktemp)
TMP_RESULTS=$(mktemp)

# 提取所有链接
find . -name "*.md" -not -path "./.git/*" -exec \
  grep -ohE 'https?://[^)>\]\s]+' {} \; | sort -u > "$TMP_LINKS"

total=$(wc -l < "$TMP_LINKS" | tr -d ' ')
echo "=== 链接存活检测 ==="
echo "工作目录: $ROOT"
echo "总链接: $total 条"
echo "超时: ${TIMEOUT}s"
echo

check_one() {
  local url="$1"
  local code
  code=$(curl -sL -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$url" 2>/dev/null)
  echo "$code $url"
}

# 串行检查(并发可能触发限流)
i=0
while read -r url; do
  i=$((i+1))
  printf "[%3d/%d] " "$i" "$total"
  check_one "$url" >> "$TMP_RESULTS"
done < "$TMP_LINKS"

# 分类
ok=$(grep -c "^200 " "$TMP_RESULTS" || true)
redirect=$(grep -cE "^(301|302) " "$TMP_RESULTS" || true)
not_found=$(grep -c "^404 " "$TMP_RESULTS" || true)
server_err=$(grep -cE "^5[0-9][0-9] " "$TMP_RESULTS" || true)
timeout=$(grep -c "^000 " "$TMP_RESULTS" || true)
other=$((total - ok - redirect - not_found - server_err - timeout))

echo
echo "=== 结果汇总 ==="
echo -e "${GREEN}OK (200):    $ok${RESET}"
echo -e "${YELLOW}重定向:      $redirect${RESET}"
echo -e "${RED}404 失效:    $not_found${RESET}"
echo -e "${RED}5xx 错误:    $server_err${RESET}"
echo -e "${YELLOW}超时:        $timeout${RESET}"
echo "其他:         $other"

# 详细报告
echo
echo "=== 失效链接(待处理) ==="
grep -E "^404|^5[0-9][0-9]|^000" "$TMP_RESULTS" | head -20 || echo "  (无)"

echo
echo "=== 重定向链接(可选更新) ==="
grep -E "^(301|302) " "$TMP_RESULTS" | head -20 || echo "  (无)"

if [ -n "$OUTPUT" ]; then
  cp "$TMP_RESULTS" "$OUTPUT"
  echo
  echo "完整报告写入: $OUTPUT"
fi

rm -f "$TMP_LINKS" "$TMP_RESULTS"

# 退出码:有失效就 1
if [ "$not_found" -gt 0 ] || [ "$server_err" -gt 0 ]; then
  exit 1
fi
exit 0