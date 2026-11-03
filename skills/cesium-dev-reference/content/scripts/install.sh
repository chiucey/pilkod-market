#!/usr/bin/env bash
#
# scripts/install.sh
#
# 一键初始化:git 仓库 + 装 git hooks + 设置文件权限
#
# 用法:
#   bash scripts/install.sh
#
# 效果:
#   - git init(若尚未初始化)
#   - 首次 commit
#   - 安装 .githooks/pre-commit(跑 health-check.sh --quick)
#   - 标记所有 scripts/*.sh 为可执行

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

GREEN='\033[0;32m'; YELLOW='\033[0;33m'; CYAN='\033[0;36m'; RESET='\033[0m'

echo -e "${CYAN}=== Cesium Dev Reference 安装脚本 ===${RESET}"
echo "工作目录: $ROOT"
echo

# 1. git init
if [ ! -d .git ]; then
  echo "[1/4] 初始化 git 仓库"
  git init -q
  git config user.email "cesium-dev-reference@example.com" 2>/dev/null
  git config user.name "Mavis Maintainer" 2>/dev/null
  echo -e "  ${GREEN}✓ git init 完成${RESET}"
else
  echo -e "[1/4] ${GREEN}✓ git 仓库已存在,跳过 init${RESET}"
fi

# 2. 标记脚本可执行
echo "[2/4] 设置 scripts/*.sh 可执行权限"
for f in scripts/*.sh; do
  if [ -f "$f" ]; then
    chmod +x "$f"
    echo "  ✓ $f"
  fi
done

# 3. 安装 git hooks
echo
echo "[3/4] 安装 git hooks"
mkdir -p .githooks
cat > .githooks/pre-commit <<'EOF'
#!/usr/bin/env bash
# Pre-commit hook:跑基础健康检查
set -uo pipefail
ROOT="$(git rev-parse --show-toplevel)"
echo "[pre-commit] 跑健康检查..."
if ! bash "$ROOT/scripts/health-check.sh" --quick; then
  echo "[pre-commit] 健康检查未通过,提交被阻止"
  echo "如需跳过: git commit --no-verify"
  exit 1
fi
exit 0
EOF
chmod +x .githooks/pre-commit
git config core.hooksPath .githooks
echo -e "  ${GREEN}✓ pre-commit hook 安装(每次 commit 前自动跑 health-check --quick)${RESET}"

# 4. 首次 commit
echo
echo "[4/4] 首次 commit"
if [ -z "$(git status --porcelain 2>/dev/null)" ]; then
  echo -e "  ${GREEN}✓ 已是空仓库或已 commit${RESET}"
else
  git add -A
  git commit -q -m "init: cesium-dev-reference v1.3.0

- 30 个 .md 模块(recipes/modules/references/self-evolution)
- 6 个 scripts/* 可执行脚本(health-check/check-baseline/check-links/check-coverage/release-diff/install)
- 3 个 .github/workflows/* 自动化(weekly/quarterly/monthly)
- self-evolution 4 机制文件升级为'真正可自我维护'"

  if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✓ 首次 commit 完成${RESET}"
  fi
fi

echo
echo -e "${CYAN}=== 安装完成 ===${RESET}"
echo
echo "后续:"
echo "  - git log            # 看提交历史"
echo "  - git status         # 看工作区状态"
echo "  - bash scripts/health-check.sh  # 手动跑健康检查"
echo "  - git remote add origin <your-git-url>  # 推送到远程"
echo "  - git push -u origin main"
echo
echo "自动化机制已就位:"
echo "  ✓ pre-commit hook → 每次 commit 前自动 health-check"
echo "  ✓ .github/workflows/weekly-health.yml → 每周基础检查(需推到 GitHub)"
echo "  ✓ .github/workflows/quarterly-baseline.yml → 每季度版本对齐"
echo "  ✓ .github/workflows/monthly-links.yml → 每月链接检查"