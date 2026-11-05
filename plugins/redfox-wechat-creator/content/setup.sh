#!/usr/bin/env bash
# wechat-content-suite 安装脚本（macOS / Linux / WSL）
# 用法：bash ./setup.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "[setup] 工作目录: $SCRIPT_DIR"

# 1) Python
if ! command -v python3 >/dev/null 2>&1; then
    echo "[FAIL] 未检测到 python3，请先安装 Python 3.9+"
    exit 1
fi
PY=python3
echo "[setup] 使用 Python: $($PY --version 2>&1)"

# 2) 虚拟环境
if [ ! -d ".venv" ]; then
    echo "[setup] 创建虚拟环境 .venv"
    "$PY" -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
PY=python

# 3) 依赖
echo "[setup] 升级 pip 并安装 requirements.txt"
"$PY" -m pip install --upgrade pip >/dev/null
"$PY" -m pip install -r requirements.txt

# 4) Playwright 浏览器
echo "[setup] 安装 Playwright Chromium 浏览器"
"$PY" -m playwright install chromium || echo "[WARN] playwright install chromium 失败，可稍后手动重试"

# 5) REDFOX_API_KEY
echo ""
echo "=== REDFOX_API_KEY 配置 ==="
if [ -n "${REDFOX_API_KEY:-}" ]; then
    echo "[ok] 当前 shell 已存在 REDFOX_API_KEY（前 8 位：${REDFOX_API_KEY:0:8}...）"
else
    read -rp "请输入 REDFOX_API_KEY（留空跳过）：" key
    if [ -n "$key" ]; then
        # 持久到 ~/.bashrc 和 ~/.zshrc
        for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
            if [ -f "$rc" ] || [ "$rc" = "$HOME/.bashrc" ]; then
                if ! grep -q '^export REDFOX_API_KEY=' "$rc" 2>/dev/null; then
                    echo "" >> "$rc"
                    echo "# wechat-content-suite" >> "$rc"
                    echo "export REDFOX_API_KEY=\"$key\"" >> "$rc"
                fi
            fi
        done
        export REDFOX_API_KEY="$key"
        echo "[ok] REDFOX_API_KEY 已写入 ~/.bashrc 和 ~/.zshrc，当前 shell 同步生效"
    else
        echo "[skip] 跳过 API Key 配置"
    fi
fi

echo ""
echo "[done] 安装完成。重新打开终端让环境变量生效。"
echo "       激活虚拟环境：source .venv/bin/activate"
