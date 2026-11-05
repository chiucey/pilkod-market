#!/usr/bin/env bash
# 一键安装 bjj-video-extraction 技能
#
# 用法:
#   bash install.sh [目标技能目录]
#
# 默认目标: ~/.hermes/skills/personal
#
# 装完会运行 selftest.py 验证完整性。

set -euo pipefail

SKILL_NAME="bjj-video-extraction"

# 本脚本放在 <skill>/scripts/ 下，技能根目录是上一级。
# 但也允许直接从技能根目录运行，所以两种情况都要认。
_here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$_here/SKILL.md" ]; then
  SRC_DIR="$_here"
elif [ -f "$_here/../SKILL.md" ]; then
  SRC_DIR="$(cd "$_here/.." && pwd)"
else
  echo "FAIL: 找不到 SKILL.md（从 $_here 向上找过了）"
  exit 1
fi

DEST_BASE="${1:-$HOME/.hermes/skills/personal}"

echo "=========================================="
echo " 安装技能: $SKILL_NAME"
echo " 来源: $SRC_DIR"
echo " 目标: $DEST_BASE"
echo "=========================================="

if [ ! -f "$SRC_DIR/SKILL.md" ]; then
  echo "FAIL: 当前目录不是技能包（找不到 SKILL.md）"
  exit 1
fi

mkdir -p "$DEST_BASE"
DEST="$DEST_BASE/$SKILL_NAME"

if [ -d "$DEST" ]; then
  echo "提示: 目标已存在，将覆盖"
  BACKUP="${DEST}.backup.$(date +%Y%m%d%H%M%S)"
  cp -r "$DEST" "$BACKUP"
  echo "已备份到: $BACKUP"
  rm -rf "$DEST"
fi

cp -r "$SRC_DIR" "$DEST"

# 解压后的执行位常丢失，这里统一补上
chmod +x "$DEST"/scripts/*.sh 2>/dev/null || true
chmod +x "$DEST"/scripts/*.py 2>/dev/null || true

echo ""
echo "验证安装..."
if python3 "$DEST/scripts/selftest.py"; then
  echo ""
  echo "安装成功。"
  echo "  技能目录: $DEST"
  echo "  查看: 在对话中说「列出技能」或「看看 $SKILL_NAME」"
else
  echo ""
  echo "安装完成但自检有失败项，请检查上面的输出。"
  exit 1
fi
