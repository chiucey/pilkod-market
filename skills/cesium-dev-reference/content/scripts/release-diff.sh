#!/usr/bin/env bash
#
# scripts/release-diff.sh
#
# 抓取 CesiumJS / Unity / Unreal 的最近 release notes,
# 跟当前技能基线 diff,产出"是否需要版本对齐"的报告。
#
# 用法:
#   bash scripts/release-diff.sh                # 最近 5 个 release
#   bash scripts/release-diff.sh --limit=10     # 最近 10 个

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

LIMIT=5
for arg in "$@"; do
  case "$arg" in
    --limit=*) LIMIT="${arg#*=}" ;;
    *) ;;
  esac
done

CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'; RESET='\033[0m'

# 从 SKILL.md 读基线
BASELINE_CESIUM=$(grep "^cesium_baseline:" SKILL.md | head -1 | awk -F': ' '{print $2}' | awk '{print $1}' | tr -d '"')
BASELINE_UNITY=$(grep "^cesium_for_unity_baseline:" SKILL.md | head -1 | awk -F': ' '{print $2}' | awk '{print $1}' | tr -d '"')
BASELINE_UNREAL=$(grep "^cesium_for_unreal_baseline:" SKILL.md | head -1 | awk -F': ' '{print $2}' | awk '{print $1}' | tr -d '"')

echo -e "${CYAN}=== Release Notes Diff ===${RESET}"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "基线: CesiumJS=$BASELINE_CESIUM / Unity=$BASELINE_UNITY / Unreal=$BASELINE_UNREAL"
echo

# 抓 releases 并解析为 "tag|date" 行(每个 release 一行)
# 用 python3 一次性解析 JSON,避免 awk/paste 分组歧义
fetch_releases() {
  local repo="$1"
  local count="$2"
  python3 - "$repo" "$count" <<'PYEOF' 2>/dev/null
import json, sys, urllib.request

repo = sys.argv[1]
count = int(sys.argv[2])
url = f"https://api.github.com/repos/{repo}/releases?per_page={count}"
try:
    req = urllib.request.Request(url, headers={"User-Agent": "cesium-dev-ref-script"})
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
    for rel in data:
        tag = rel.get("tag_name", "n/a")
        pub = rel.get("published_at", "n/a")[:10]  # 取日期部分
        print(f"{tag}|{pub}")
except Exception as e:
    print(f"ERR|{e}", file=sys.stderr)
    sys.exit(1)
PYEOF
}

show_product() {
  local name="$1"
  local repo="$2"
  local baseline="$3"

  echo -e "${CYAN}── ${name} ──${RESET}"
  echo "仓库: ${repo}"
  echo "基线: ${baseline}"
  echo "最近 ${LIMIT} 个 release:"

  local releases
  releases=$(fetch_releases "$repo" "$LIMIT")
  if [ -z "$releases" ]; then
    echo -e "  ${YELLOW}⚠ 无法获取(网络问题 / API 限流 / 仓库不存在)${RESET}"
    echo
    return
  fi

  while IFS='|' read -r tag date; do
    if [ "$tag" = "ERR" ]; then
      echo -e "  ${YELLOW}⚠ $date${RESET}"
    else
      echo "  $tag ($date)"
    fi
  done <<< "$releases"

  echo
  echo "  → 是否需要更新基线?对照 git log: https://github.com/${repo}/releases"
  echo
}

show_product "CesiumJS" "CesiumGS/cesium" "$BASELINE_CESIUM"
show_product "Cesium for Unity" "CesiumGS/cesium-unity" "$BASELINE_UNITY"
show_product "Cesium for Unreal" "CesiumGS/cesium-unreal" "$BASELINE_UNREAL"

echo "---"
echo "建议流程:"
echo "  1. 看每个产品的 changelog 判断是否有破坏性变更"
echo "  2. 若需要更新基线 → 改 SKILL.md frontmatter + 各模块 cesium_version"
echo "  3. 在 changelog.md 加 v1.x.y → v1.x.z 对齐条目"
echo "  4. 跑 bash scripts/health-check.sh 验证"