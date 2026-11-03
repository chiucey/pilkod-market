#!/usr/bin/env bash
#
# scripts/check-baseline.sh
#
# 自动版本对齐检测 — 抓取 CesiumJS / Unity / Unreal / Omniverse 最新版本,
# 对比本技能声明的基线,产出 diff 报告。
#
# 用法:
#   bash scripts/check-baseline.sh             # 全部产品
#   bash scripts/check-baseline.sh --cesium    # 只查 CesiumJS
#   bash scripts/check-baseline.sh --unity
#   bash scripts/check-baseline.sh --unreal

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[0;33m'
CYAN='\033[0;36m'; RESET='\033[0m'

ONLY=""

for arg in "$@"; do
  case "$arg" in
    --cesium)  ONLY="cesium" ;;
    --unity)   ONLY="unity" ;;
    --unreal)  ONLY="unreal" ;;
    *) ;;
  esac
done

# 网络工具
fetch_latest() {
  local repo="$1"
  curl -sL --max-time 15 "https://api.github.com/repos/${repo}/releases/latest" | \
    grep '"tag_name":' | head -1 | sed -E 's/.*"tag_name": *"([^"]+)".*/\1/'
}

declare -A BASELINE_RAW
# 从 SKILL.md 读基线
BASELINE_CESIUM=$(grep "^cesium_baseline:" SKILL.md | head -1 | awk -F': ' '{print $2}' | tr -d '"\r' | awk '{print $1}')
BASELINE_UNITY=$(grep "^cesium_for_unity_baseline:" SKILL.md | head -1 | awk -F': ' '{print $2}' | tr -d '"\r' | awk '{print $1}')
BASELINE_UNREAL=$(grep "^cesium_for_unreal_baseline:" SKILL.md | head -1 | awk -F': ' '{print $2}' | tr -d '"\r' | awk '{print $1}')

echo -e "${CYAN}=== Cesium 生态版本对齐检查 ===${RESET}"
echo "工作目录: $ROOT"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo

check_product() {
  local name="$1"
  local repo="$2"
  local baseline="$3"

  echo -e "${CYAN}[$name]${RESET}"
  echo "  基线: $baseline"

  local latest
  latest=$(fetch_latest "$repo")
  if [ -z "$latest" ]; then
    echo -e "  ${YELLOW}⚠ 无法获取最新版本(网络问题或 API 限流)${RESET}"
    echo
    return
  fi
  echo "  最新: $latest"

  # 提取版本主数字(v1.141.0 → 1.141)
  local baseline_short="${baseline//[!0-9.]/}"
  local latest_short="${latest//[!0-9.]/}"
  # 取前两段(如 1.141)
  local baseline_main="${baseline_short%%.*}.$(echo "$baseline_short" | cut -d. -f2)"
  local latest_main="${latest_short%%.*}.$(echo "$latest_short" | cut -d. -f2)"

  if [ "$baseline_main" = "$latest_main" ]; then
    echo -e "  ${GREEN}✓ 对齐${RESET}"
  else
    echo -e "  ${YELLOW}⚠ 不对齐 — 基线落后:${RESET} $baseline_main → $latest_main"
    echo "  建议:"
    echo "    1. 查 release notes: https://github.com/${repo}/releases"
    echo "    2. 跑 main: bash scripts/check-baseline.sh --$([ "$name" = "CesiumJS" ] && echo cesium || ([ "$name" = "Cesium for Unity" ] && echo unity || echo unreal))"
    echo "    3. 决策:更新基线 / 标记暂不升级"
    echo "    4. 跑 maintenance-playbook.md § 3 版本对齐任务"
  fi
  echo
}

if [ -z "$ONLY" ] || [ "$ONLY" = "cesium" ]; then
  check_product "CesiumJS" "CesiumGS/cesium" "$BASELINE_CESIUM"
fi

if [ -z "$ONLY" ] || [ "$ONLY" = "unity" ]; then
  check_product "Cesium for Unity" "CesiumGS/cesium-unity" "$BASELINE_UNITY"
fi

if [ -z "$ONLY" ] || [ "$ONLY" = "unreal" ]; then
  check_product "Cesium for Unreal" "CesiumGS/cesium-unreal" "$BASELINE_UNREAL"
fi

echo "完成后:更新 SKILL.md cesium_baseline + 各模块 cesium_version + changelog.md"