#!/usr/bin/env bash
#
# scripts/health-check.sh
#
# 一键质量检查 — 对应 maintenance-playbook.md § 9 (QC 清单)
#
# 检查项:
#   1. 结构完整性(目录 + 文件数量)
#   2. Frontmatter 合规(所有 .md 都有合法 frontmatter)
#   3. 引用数量(>= 50 条外链)
#   4. cesium_version 一致性(对比 SKILL.md cesium_baseline)
#   5. 过期清单(标记 status: deprecated 的文件未及时清理)
#   6. 缺口登记(列出待补缺口数量)
#   7. 深度自检 — 跨文件引用 / 字段值 / 编号唯一性 / 脚本权限 / 换行符 / SKILL/README 引用
#   8. SKILL.md ↔ README.md ↔ 实际文件 三方一致性
#
# 用法:
#   bash scripts/health-check.sh              # 跑全部(包括深度自检)
#   bash scripts/health-check.sh --quick      # 只跑 1-4(跳过深度自检,适合 pre-commit)
#   bash scripts/health-check.sh --json       # 输出 JSON 报告

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

QUICK=false
JSON=false
for arg in "$@"; do
  case "$arg" in
    --quick) QUICK=true ;;
    --json) JSON=true ;;
    *) ;;
  esac
done

PASS=0
FAIL=0
WARN=0

# 颜色(只在非 JSON 输出时启用)
if [ "$JSON" = false ]; then
  GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[0;33m'; CYAN='\033[0;36m'; RESET='\033[0m'
else
  GREEN=''; RED=''; YELLOW=''; CYAN=''; RESET=''
fi

report() {
  local status="$1"; local name="$2"; local detail="$3"
  if [ "$JSON" = true ]; then
    echo "{\"status\":\"$status\",\"check\":\"$name\",\"detail\":\"$detail\"}"
    return
  fi
  case "$status" in
    pass) echo -e "${GREEN}✓ PASS${RESET} $name — $detail"; PASS=$((PASS+1)) ;;
    fail) echo -e "${RED}✗ FAIL${RESET} $name — $detail"; FAIL=$((FAIL+1)) ;;
    warn) echo -e "${YELLOW}⚠ WARN${RESET} $name — $detail"; WARN=$((WARN+1)) ;;
  esac
}

echo -e "${CYAN}=== Cesium Dev Reference 健康检查 ===${RESET}"
echo "工作目录: $ROOT"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo

# ============ 1. 结构完整性 ============
echo -e "${CYAN}[1] 结构完整性${RESET}"
EXPECTED_MODULES=11
EXPECTED_RECIPES=9
EXPECTED_REFERENCES=3
EXPECTED_SELF=4

mod_count=$(find modules -maxdepth 1 -name "*.md" | wc -l | tr -d ' ')
rec_count=$(find recipes -maxdepth 1 -name "*.md" | wc -l | tr -d ' ')
ref_count=$(find references -maxdepth 1 -name "*.md" | wc -l | tr -d ' ')
self_count=$(find self-evolution -maxdepth 1 -name "*.md" | wc -l | tr -d ' ')

[ "$mod_count" -ge "$EXPECTED_MODULES" ] && report pass "modules 数" "实际 $mod_count(>= $EXPECTED_MODULES)" || report fail "modules 数" "实际 $mod_count(< $EXPECTED_MODULES)"
[ "$rec_count" -ge "$EXPECTED_RECIPES" ] && report pass "recipes 数" "实际 $rec_count(>= $EXPECTED_RECIPES)" || report warn "recipes 数" "实际 $rec_count(< $EXPECTED_RECIPES)"
[ "$ref_count" -ge "$EXPECTED_REFERENCES" ] && report pass "references 数" "实际 $ref_count(>= $EXPECTED_REFERENCES)" || report fail "references 数" "实际 $ref_count(< $EXPECTED_REFERENCES)"
[ "$self_count" -eq "$EXPECTED_SELF" ] && report pass "self-evolution 数" "实际 $self_count(== $EXPECTED_SELF)" || report warn "self-evolution 数" "实际 $self_count(≠ $EXPECTED_SELF)"

# ============ 2. Frontmatter 合规 ============
echo
echo -e "${CYAN}[2] Frontmatter 合规${RESET}"
missing_fm=0
while IFS= read -r f; do
  first=$(head -1 "$f")
  if [ "$first" != "---" ]; then
    [ "$missing_fm" -eq 0 ] && echo "缺 frontmatter:"
    echo "  - $f"
    missing_fm=$((missing_fm+1))
  fi
done < <(find . -name "*.md" -not -path "./.git/*" -not -path "./node_modules/*")
[ "$missing_fm" -eq 0 ] && report pass "frontmatter 完整性" "所有 .md 都有 frontmatter" || report fail "frontmatter 完整性" "$missing_fm 个文件缺失 frontmatter"

# ============ 3. 引用数量 ============
echo
echo -e "${CYAN}[3] 引用数量${RESET}"
link_count=$(grep -rE 'https?://[^)\s]+' --include="*.md" . 2>/dev/null | wc -l | tr -d ' ')
[ "$link_count" -ge 50 ] && report pass "外部链接数" "实际 $link_count 条(>= 50)" || report warn "外部链接数" "实际 $link_count 条(< 50)"

# ============ 4. cesium_version 一致性 ============
if [ "$QUICK" = false ]; then
  echo
  echo -e "${CYAN}[4] cesium_version 一致性${RESET}"
  baseline=$(grep "cesium_baseline:" SKILL.md | head -1 | awk -F': ' '{print $2}' | tr -d '"\r')
  echo "  基线: $baseline"
  inconsistent=0
  while IFS= read -r f; do
    cv=$(grep "^cesium_version:" "$f" | head -1 | awk -F': ' '{print $2}' | tr -d '"\r')
    [ -z "$cv" ] && continue
    if [[ "$cv" == N/A* ]] || [[ "$cv" == all* ]] || [[ "$cv" == 全部* ]]; then
      continue
    fi
    case "$baseline" in "$cv"*) ;; *) inconsistent=$((inconsistent+1)); echo "    ! $f: $cv" ;; esac
  done < <(find modules recipes references self-evolution -maxdepth 1 -name "*.md" 2>/dev/null)
  [ "$inconsistent" -eq 0 ] && report pass "version 一致性" "全部声明与基线兼容" || report warn "version 一致性" "$inconsistent 个文件版本声明不一致"
fi

# ============ 5. 过期标记 ============
if [ "$QUICK" = false ]; then
  echo
  echo -e "${CYAN}[5] 过期标记检查${RESET}"
  deprecated_count=$(grep -rl "^status: deprecated" --include="*.md" . 2>/dev/null | wc -l | tr -d ' ')
  [ "$deprecated_count" -eq 0 ] && report pass "无废弃模块" "0 个 deprecated 状态文件" || report warn "存在废弃模块" "$deprecated_count 个文件标记为 deprecated"
fi

# ============ 6. 缺口登记 ============
if [ "$QUICK" = false ]; then
  echo
  echo -e "${CYAN}[6] 缺口登记${RESET}"
  if [ -f self-evolution/coverage-gap-detector.md ]; then
    pending=$(grep -c "^| .* | .* | .* | 待补 " self-evolution/coverage-gap-detector.md 2>/dev/null || echo 0)
    done_count=$(grep -c "✅.*已补" self-evolution/coverage-gap-detector.md 2>/dev/null || echo 0)
    echo "  待补缺口: $pending 个"
    echo "  已补缺口: $done_count 个"
    [ "$pending" -gt 0 ] && report warn "缺口待办" "$pending 个待补缺口" || report pass "缺口待办" "0 个待补缺口"
  else
    report fail "缺口登记文件" "self-evolution/coverage-gap-detector.md 不存在"
  fi
fi

# ============ 7. 深度自检(默认跑;--quick 跳过) ============
if [ "$QUICK" = false ]; then
  echo
  echo -e "${CYAN}[7] 深度自检(跨文件引用 / 字段合法性 / 编号唯一性 / 脚本权限 / 换行符)${RESET}"

  # 7.1 跨文件引用完整性 — 扫所有 .md 引用的 modules/recipes/references/self-evolution/architecture 路径
  # 跳过代码块内(``` 包围)的占位符示例(如 "modules/NN-xxx.md"、"recipes/xxx.md")
  bad_refs=0
  while IFS= read -r ref; do
    [ -z "$ref" ] && continue
    # 跳过占位符(NN-xxx / xxx / yyy 之类)
    case "$ref" in
      */NN-*|*/xxx.md|*/yyy.md|*/zzz.md) continue ;;
    esac
    if [ ! -f "$ref" ] && [ ! -d "$ref" ]; then
      [ "$bad_refs" -eq 0 ] && echo "  失效引用:"
      echo "    - $ref"
      bad_refs=$((bad_refs+1))
    fi
  done < <(grep -ohE '\b((modules|recipes|references|self-evolution)/[a-z0-9\-]+\.md|architecture\.md)\b' --include="*.md" -r . 2>/dev/null | sort -u)
  [ "$bad_refs" -eq 0 ] && report pass "跨文件引用" "所有引用路径真实存在" || report fail "跨文件引用" "$bad_refs 个失效引用"

  # 7.2 字段值合法性 — frontmatter 中 status/cesium_version/last_verified 格式
  invalid_fm=0
  while IFS= read -r f; do
    in_fm=0
    fm_line=0
    while IFS= read -r line; do
      fm_line=$((fm_line+1))
      # 第一行必须是 ---
      if [ "$fm_line" -eq 1 ]; then
        [ "$line" != "---" ] && { invalid_fm=$((invalid_fm+1)); break; }
        in_fm=1
        continue
      fi
      # 第二个 --- 表示 frontmatter 结束
      if [ "$line" = "---" ] && [ "$fm_line" -gt 1 ]; then break; fi
      # 检查字段值
      case "$line" in
        status:*) 
          v=$(echo "$line" | awk -F': ' '{print $2}' | tr -d '"\r')
          case "$v" in stable|experimental|deprecated) ;; *) invalid_fm=$((invalid_fm+1)); echo "    ! $f status 值非法: $v" ;; esac
          ;;
        last_verified:*) 
          v=$(echo "$line" | awk -F': ' '{print $2}' | tr -d '"\r')
          echo "$v" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}' || { invalid_fm=$((invalid_fm+1)); echo "    ! $f last_verified 格式错: $v"; }
          ;;
      esac
    done < "$f"
  done < <(find . -name "*.md" -not -path "./.git/*" -not -path "./node_modules/*" 2>/dev/null)
  [ "$invalid_fm" -eq 0 ] && report pass "frontmatter 字段值" "所有 status/last_verified 合法" || report fail "frontmatter 字段值" "$invalid_fm 处非法"

  # 7.3 module 编号唯一性 — 只读真实 frontmatter(代码块示例不计入)
  dup_modules=0
  rm -f /tmp/.dup_modules
  while IFS= read -r f; do
    awk 'BEGIN{p=0} /^---$/{ if(p==0){p=1; next} else exit } p==1{ print }' "$f" | grep "^module:" | head -1
  done < <(find modules references self-evolution -maxdepth 1 -name "*.md" 2>/dev/null) | \
    awk -F': ' '{print $2}' | tr -d '"\r' | sort | uniq -d > /tmp/.dup_modules 2>/dev/null
  seen_modules=$(wc -l < /tmp/.dup_modules 2>/dev/null | tr -d ' ' || echo 0)
  if [ "$seen_modules" -gt 0 ]; then
    echo "  重复的 module 编号:"
    while IFS= read -r dup; do
      [ -n "$dup" ] && echo "    - $dup"
    done < /tmp/.dup_modules
    rm -f /tmp/.dup_modules
  fi
  [ "$seen_modules" -eq 0 ] && report pass "module 编号唯一" "无重复" || report fail "module 编号唯一" "$seen_modules 个 module 编号重复"

  # 7.4 scripts 可执行权限 + LF 换行
  bad_scripts=0
  for s in scripts/*.sh; do
    [ -x "$s" ] || { bad_scripts=$((bad_scripts+1)); echo "    ! $s 不可执行"; }
    # 检查 CRLF
    if grep -q $'\r' "$s" 2>/dev/null; then
      bad_scripts=$((bad_scripts+1))
      echo "    ! $s 含 CRLF 换行"
    fi
  done
  [ "$bad_scripts" -eq 0 ] && report pass "scripts 权限与换行" "全部可执行 + LF 换行" || report fail "scripts 权限与换行" "$bad_scripts 个脚本有问题"

  # 7.5 scripts 互相依赖图 — 检测循环依赖
  cyclic=0
  for s in scripts/*.sh; do
    deps=$(grep -hE "bash[^\"]*scripts/" "$s" 2>/dev/null | grep -oE "scripts/[a-z\-]+\.sh" | sort -u)
    for d in $deps; do
      [ "$d" = "$(basename "$s")" ] && continue  # 跳过自指
      [ -f "$d" ] || { cyclic=$((cyclic+1)); echo "    ! $s 引用不存在的脚本 $d"; }
    done
  done
  [ "$cyclic" -eq 0 ] && report pass "scripts 依赖图" "无失效引用" || report warn "scripts 依赖图" "$cyclic 处失效"

  # ============ 8. SKILL.md ↔ README.md ↔ 实际文件 三方一致性 ============
  echo
  echo -e "${CYAN}[8] SKILL.md / README.md ↔ 实际文件 一致性${RESET}"

  # 8.1 SKILL.md 引用的所有 modules/recipes 必须存在
  missing_skill=0
  while IFS= read -r ref; do
    [ -z "$ref" ] && continue
    if [ ! -f "$ref" ]; then
      [ "$missing_skill" -eq 0 ] && echo "  SKILL.md 引用失效:"
      echo "    - $ref"
      missing_skill=$((missing_skill+1))
    fi
  done < <(grep -ohE '`((modules|recipes|references|self-evolution)/[a-z0-9\-]+\.md|architecture\.md)`' SKILL.md 2>/dev/null | sed 's/`//g' | sort -u)
  [ "$missing_skill" -eq 0 ] && report pass "SKILL.md 引用" "全部真实存在" || report fail "SKILL.md 引用" "$missing_skill 处失效"

  # 8.2 README.md "目录速览"里列出的文件必须都存在
  # 目录速览只写文件名(如 "api-quick-ref.md"),但子目录里也有
  # 用 find 在任意子目录找,找到就 OK
  missing_readme=0
  listed_files=$(grep -oE '[├└]── [a-zA-Z][a-zA-Z0-9\-]*\.md' README.md 2>/dev/null | awk '{print $NF}' | sort -u)
  for fname in $listed_files; do
    [ -z "$fname" ] && continue
    if ! find "$ROOT" -name "$fname" -not -path "*/.git/*" -not -path "*/node_modules/*" -print -quit 2>/dev/null | grep -q .; then
      [ "$missing_readme" -eq 0 ] && echo "  README.md 目录速览失效:"
      echo "    - $fname"
      missing_readme=$((missing_readme+1))
    fi
  done
  [ "$missing_readme" -eq 0 ] && report pass "README.md 目录速览" "列出的文件都存在" || report warn "README.md 目录速览" "$missing_readme 处失效"

  # 8.3 SKILL.md version 字段 vs changelog 章节标题(###)版本一致
  skill_ver=$(grep "^version:" SKILL.md | head -1 | awk -F': ' '{print $2}' | tr -d '"\r')
  # 只从 ### 章节标题里抓本技能的版本号(避免抓到产品版本如 v1.24.0)
  latest_changelog=$(grep "^### " self-evolution/changelog.md | grep -oE "v[0-9]+\.[0-9]+\.[0-9]+" | head -1)
  if [ -n "$skill_ver" ] && [ -n "$latest_changelog" ]; then
    if echo "$skill_ver" | grep -q "^$(echo $latest_changelog | sed 's/^v//')$"; then
      report pass "version 一致性" "SKILL.md=$skill_ver ↔ changelog=$latest_changelog"
    else
      report warn "version 一致性" "SKILL.md=$skill_ver 与 changelog 标题 $latest_changelog 不一致"
    fi
  fi
fi

# ============ 总结 ============
echo
echo -e "${CYAN}=== 总结 ===${RESET}"
echo -e "${GREEN}PASS: $PASS${RESET}  ${YELLOW}WARN: $WARN${RESET}  ${RED}FAIL: $FAIL${RESET}"

[ "$FAIL" -gt 0 ] && exit 1
exit 0