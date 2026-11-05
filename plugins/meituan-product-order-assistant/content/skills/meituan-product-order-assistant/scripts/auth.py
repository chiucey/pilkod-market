#!/usr/bin/env python3
"""
meituan-product-order-assistant 设备标识模块
管理 device_token（下单时的 uuid 参数）；用户 Token 由 pt-passport 管理。

用法示例：
  python auth.py get-device-token
  python auth.py clear-device-token
"""

import argparse
import hashlib
import json
import random
import sys
import time
from pathlib import Path

# ── 常量 ──────────────────────────────────────────────────────────────
AUTH_KEY = "meituan-c-user-auth"


def _resolve_auth_file() -> Path:
    """
    跨平台确定存储路径，优先级：
    1. 环境变量 MINIMAX_AUTH_FILE（显式指定，最高优先级）
    2. $MINIMAX_SKILL_CREDENTIALS_DIR/device.json
    3. $MINIMAX_HOME/credentials/meituan-product-order-assistant/device.json
    """
    import os

    env_path = os.environ.get("MINIMAX_AUTH_FILE")
    if env_path:
        return Path(env_path)

    credentials_dir = os.environ.get("MINIMAX_SKILL_CREDENTIALS_DIR")
    if credentials_dir:
        return Path(credentials_dir) / "device.json"

    minimax_home = os.environ.get("MINIMAX_HOME") or str(Path.home() / ".minimax")
    return Path(minimax_home) / "credentials" / "meituan-product-order-assistant" / "device.json"


AUTH_FILE = _resolve_auth_file()


# ── 设备ID生成 ────────────────────────────────────────────────────────

def generate_device_token(seed: str) -> str:
    """
    生成设备唯一标识（device_token）。
    算法：MD5（seed + 毫秒时间戳 + 0~1000随机整数）
    device_token 与设备绑定，一旦生成后永不覆盖。
    """
    ts_ms = int(time.time() * 1000)
    rand_int = random.randint(0, 1000)
    raw = f"{seed}{ts_ms}{rand_int}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


# ── 存储操作 ──────────────────────────────────────────────────────────

def load_auth() -> dict:
    if AUTH_FILE.exists():
        with open(AUTH_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_auth(data: dict):
    import os, stat
    AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(AUTH_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    try:
        os.chmod(AUTH_FILE, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass


def get_token_data() -> dict:
    return load_auth().get(AUTH_KEY, {})


def save_token_data(token_data: dict):
    auth = load_auth()
    auth[AUTH_KEY] = token_data
    save_auth(auth)


def _ensure_device_token(token_data: dict) -> str:
    """确保 device_token 存在，不存在则生成并持久化，返回 device_token"""
    dt = token_data.get("device_token", "")
    if not dt:
        dt = generate_device_token("meituan-product-order-assistant")
        token_data["device_token"] = dt
        save_token_data(token_data)
    return dt


# ── 命令：get-device-token ───────────────────────────────────────────

def cmd_get_device_token():
    """获取 device_token，不存在则自动生成"""
    token_data = get_token_data()
    device_token = _ensure_device_token(token_data)
    print(json.dumps({
        "success": True,
        "device_token": device_token
    }, ensure_ascii=False))


# ── 命令：clear-device-token ─────────────────────────────────────────

def cmd_clear_device_token():
    """清除设备标识，仅在用户明确要求时调用"""
    token_data = get_token_data()
    had_device_token = bool(token_data.get("device_token"))

    # 清除 device_token
    token_data["device_token"] = ""
    save_token_data(token_data)

    print(json.dumps({
        "success": True,
        "message": "设备标识已清除，下次使用将生成新的 device_token",
        "device_token_cleared": had_device_token
    }, ensure_ascii=False))


# ── 入口 ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="meituan-product-order-assistant 设备标识模块")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("get-device-token",
                          help="获取/生成 device_token（下单需要）")
    subparsers.add_parser("clear-device-token",
                          help="清除设备标识，仅在用户明确要求时调用")

    args = parser.parse_args()

    if args.command == "get-device-token":
        cmd_get_device_token()
    elif args.command == "clear-device-token":
        cmd_clear_device_token()


if __name__ == "__main__":
    main()
