#!/usr/bin/env bash
#
# scripts/check-coverage.sh
#
# 主动缺口自检 — 对比 coverage-gap-detector.md 的待补缺口
# 与本技能实际模块,产出"应补未补"清单。
#
# 用法:
#   bash scripts/check-coverage.sh
#
# 检测:
#   1. coverage-gap-detector.md § 五 的待补缺口表是否过期(>90 天未更新)
#   2. 实际模块数 vs 缺口声称的覆盖范围
#   3. recipes 中是否缺某些常见场景(埋点检查)
#   4. api-quick-ref.md 中 API 数量(< 75 算偏少)

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[0;33m'; CYAN='\033[0;36m'; RESET='\033[0m'

echo -e "${CYAN}=== 缺口自检 ===${RESET}"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo

GAP_FILE="self-evolution/coverage-gap-detector.md"
if [ ! -f "$GAP_FILE" ]; then
  echo -e "${RED}✗ ${GAP_FILE} 不存在${RESET}"
  exit 1
fi

# 1. 检查待补缺口数量
echo "[1] 待补缺口数"
pending=$(grep -cE "^\\| .* \\| .* \\| .* \\| 待" "$GAP_FILE" || echo 0)
done_count=$(grep -c "✅.*已补" "$GAP_FILE" || echo 0)
echo "  待补: $pending 个"
echo "  已补: $done_count 个"
if [ "$pending" -gt 5 ]; then
  echo -e "  ${YELLOW}⚠ 待补缺口 > 5,可能需要批量处理${RESET}"
fi

# 2. 检查陈旧度(>90 天未更新)
echo
echo "[2] coverage-gap-detector.md 陈旧度"
last_verified=$(grep "^last_verified:" "$GAP_FILE" | head -1 | awk -F': ' '{print $2}' | tr -d '"\r')
if [ -n "$last_verified" ]; then
  # 简易天数计算(只支持 YYYY-MM-DD)
  last_ts=$(date -d "$last_verified" +%s 2>/dev/null || echo 0)
  now_ts=$(date +%s)
  if [ "$last_ts" -gt 0 ]; then
    days=$(( (now_ts - last_ts) / 86400 ))
    if [ "$days" -gt 90 ]; then
      echo -e "  ${RED}✗ 上次核验距今 $days 天(>90 天陈旧)${RESET}"
      echo "  建议:更新 last_verified + 重新审视缺口清单"
    elif [ "$days" -gt 30 ]; then
      echo -e "  ${YELLOW}⚠ 上次核验距今 $days 天${RESET}"
    else
      echo -e "  ${GREEN}✓ 上次核验距今 $days 天${RESET}"
    fi
  fi
fi

# 3. recipes 覆盖检查
echo
echo "[3] recipes 覆盖检查"
EXPECTED_RECIPES=(
  "measure-distance"
  "terrain-profile"
  "viewshed-analysis"
  "flood-inundation"
  "trajectory-replay"
  "underground-mode"
  "custom-3dtiles"
  "ion-token-rotation"
  "load-mvt"
)
missing_recipes=()
for r in "${EXPECTED_RECIPES[@]}"; do
  if [ ! -f "recipes/${r}.md" ]; then
    missing_recipes+=("$r")
  fi
done
if [ "${#missing_recipes[@]}" -eq 0 ]; then
  echo -e "  ${GREEN}✓ ${#EXPECTED_RECIPES[@]} 个核心 recipes 齐全${RESET}"
else
  echo -e "  ${RED}✗ 缺失: ${missing_recipes[*]}${RESET}"
fi

# 4. API 速查覆盖
echo
echo "[4] api-quick-ref.md 覆盖"
if [ -f "references/api-quick-ref.md" ]; then
  api_lines=$(grep -cE "^\| \`" "references/api-quick-ref.md" || echo 0)
  echo "  API 条目: $api_lines"
  if [ "$api_lines" -lt 75 ]; then
    echo -e "  ${YELLOW}⚠ API 速查偏少(<75 条),考虑补全${RESET}"
  else
    echo -e "  ${GREEN}✓ API 速查覆盖充足 (>= 75)${RESET}"
  fi
fi

# 5. 三大引擎集成是否齐全
echo
echo "[5] 引擎集成覆盖"
for mod in "modules/10-cesium-for-unity.md" "modules/11-cesium-for-unreal.md"; do
  if [ -f "$mod" ]; then
    echo -e "  ${GREEN}✓ $mod 存在${RESET}"
  else
    echo -e "  ${RED}✗ $mod 缺失${RESET}"
  fi
done

echo
echo "---"
echo "如发现问题,按 coverage-gap-detector.md § 六 SOP 处理"
echo "完成缺口补齐后:更新 coverage-gap-detector.md 缺口表 + changelog.md"