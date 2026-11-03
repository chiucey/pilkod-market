#!/usr/bin/env python3
"""
Dream Skill — 自动记忆整合脚本

用法：
    python dream.py --setup      安装 cron job
    python dream.py --status    查看状态
    python dream.py --run        手动触发整合
    python dream.py --teardown   卸载
    python dream.py --check      三门检查（供 cron handler 调用）
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── 路径常量 ────────────────────────────────────────────────
SKILL_DIR = Path(__file__).parent.parent.resolve()
STATE_DIR = SKILL_DIR / "state"
LOCK_FILE = STATE_DIR / "lock.json"
STATE_FILE = STATE_DIR / "state.json"
CONFIG_FILE = SKILL_DIR / "config.json"

DEFAULT_CONFIG = {
    "autoDreamEnabled": True,
    "minHours": 24,
    "minSessions": 5,
    "notificationChannel": "webchat",
}
STALE_THRESHOLD_MS = 30 * 60 * 1000   # 30 分钟内有 holder = 正在运行
CRON_JOB_NAME = "dream-skill-consolidation"


# ── 工具函数 ────────────────────────────────────────────────

def load_json(path: Path, default=None):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return default


def save_json(path: Path, data: dict):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_config() -> dict:
    return load_json(CONFIG_FILE, DEFAULT_CONFIG)


def load_lock() -> dict:
    return load_json(LOCK_FILE, {"lastConsolidatedAt": 0, "holderSessionId": "", "holderTimestamp": 0})


def save_lock(data: dict):
    save_json(LOCK_FILE, data)


def load_state() -> dict:
    return load_json(STATE_FILE, {})


def save_state(data: dict):
    save_json(STATE_FILE, data)


def ts_to_iso(ms: int) -> str:
    if not ms:
        return "从未"
    dt = datetime.fromtimestamp(ms / 1000, tz=timezone.utc).astimezone()
    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


def hours_since(ms: int) -> float:
    if not ms:
        return float("inf")
    return (time.time() * 1000 - ms) / 3_600_000


# ── 核心逻辑 ────────────────────────────────────────────────

def get_workspace_transcripts():
    """扫描 workspace 下的 transcripts 目录，返回 mtime > since_ms 的 session id 列表。"""
    transcripts_dir = Path.home() / ".qclaw" / "workspace" / "transcripts"
    if not transcripts_dir.is_dir():
        return []
    sessions = []
    for f in transcripts_dir.iterdir():
        if f.is_file() and f.suffix == ".jsonl":
            # 跳过 agent-*.jsonl（内部 session）
            if f.stem.startswith("agent-"):
                continue
            sessions.append({"sessionId": f.stem, "mtime": f.stat().st_mtime})
    return sessions


def check_time_gate(lock: dict, cfg: dict) -> tuple[bool, str]:
    last_at = lock.get("lastConsolidatedAt", 0)
    min_hours = cfg.get("minHours", 24)
    elapsed_h = hours_since(last_at)
    passed = elapsed_h >= min_hours
    reason = f"时间门: {elapsed_h:.1f}h >= {min_hours}h → {'通过' if passed else '未过'}"
    return passed, reason


def check_session_gate(lock: dict, cfg: dict) -> tuple[bool, str, int]:
    last_at = lock.get("lastConsolidatedAt", 0)
    min_sessions = cfg.get("minSessions", 5)
    sessions = get_workspace_transcripts()
    # mtime（修改时间）> lastConsolidatedAt（毫秒转秒）
    since_sec = last_at / 1000
    touched = [s for s in sessions if s["mtime"] > since_sec]
    passed = len(touched) >= min_sessions
    reason = f"会话门: {len(touched)} 个 >= {min_sessions} 个 → {'通过' if passed else '未过'}"
    return passed, reason, len(touched)


def check_lock_gate(lock: dict) -> tuple[bool, str]:
    holder_ts = lock.get("holderTimestamp", 0)
    elapsed_ms = time.time() * 1000 - holder_ts
    if holder_ts > 0 and elapsed_ms < STALE_THRESHOLD_MS:
        holder = lock.get("holderSessionId", "?")
        reason = f"锁门: 持有者 '{holder}' 活跃中（{elapsed_ms/1000:.0f}s前），退出"
        return False, reason
    reason = "锁门: 无活跃持有者，可获取"
    return True, reason


def try_acquire_lock(session_id: str) -> tuple[bool, dict]:
    """尝试获取锁。成功返回(True, 更新后的lock)；失败返回(False, 当前lock)。"""
    lock = load_lock()
    holder_ts = lock.get("holderTimestamp", 0)
    elapsed_ms = time.time() * 1000 - holder_ts

    # 仍有活跃持有者
    if holder_ts > 0 and elapsed_ms < STALE_THRESHOLD_MS:
        return False, lock

    # 获取锁
    now_ms = int(time.time() * 1000)
    new_lock = {
        "lastConsolidatedAt": lock.get("lastConsolidatedAt", 0),
        "holderSessionId": session_id,
        "holderTimestamp": now_ms,
    }
    save_lock(new_lock)

    # 二次验证（防止竞争写入）
    verify = load_lock()
    if verify.get("holderSessionId") != session_id:
        return False, verify

    return True, new_lock


def release_lock(new_lock: dict):
    """整合完成后更新 lastConsolidatedAt，清除 holder。"""
    now_ms = int(time.time() * 1000)
    updated = {
        "lastConsolidatedAt": now_ms,
        "holderSessionId": "",
        "holderTimestamp": 0,
    }
    save_lock(updated)
    return updated


def all_gates_pass(cfg: dict) -> tuple[bool, dict]:
    """执行全部三门检查。返回 (passed, gate_results)。"""
    lock = load_lock()
    results = {}

    passed, results["time"] = check_time_gate(lock, cfg)
    if not passed:
        return False, results

    passed, results["session"], _ = check_session_gate(lock, cfg)
    if not passed:
        return False, results

    passed, results["lock"] = check_lock_gate(lock)
    return passed, results


# ── cron job 管理 ────────────────────────────────────────────

def get_cron_script_path() -> Path:
    return SKILL_DIR / "scripts" / "dream_run.py"


def build_cron_payload() -> str:
    """生成 isolated session 的 prompt message。"""
    prompt = (
        "你正在执行 Dream 记忆整合。\n"
        "请阅读 ~/.qclaw/skills/dream-skill/references/prompt.md\n"
        "严格按其中 Phase 1→2→3→4 的步骤执行。\n"
        "执行完毕后，发送完成摘要通知。\n"
        "注意：仅操作 ~/.qclaw/workspace/memory/ 目录下的文件。"
    )
    return prompt


def setup_cron():
    """通过 OpenClaw cron API 创建定时任务（输出指令给用户执行）。"""
    from SkillHub import skillhub
    import json as _json

    skill_dir = str(SKILL_DIR)
    interval_ms = load_config().get("minHours", 24) * 3600 * 1000

    # 生成 dream_run.py 内容（cron handler）
    run_script = f'''#!/usr/bin/env python3
"""Dream Skill — cron handler（由 dream.py --setup 自动生成）"""
import sys
sys.path.insert(0, r"{skill_dir}")
from scripts.dream import all_gates_pass, try_acquire_lock, release_lock, load_config, save_state, load_lock
import time
import json

session_id = f"dream-{{int(time.time())}}"
cfg = load_config()

if not cfg.get("autoDreamEnabled", True):
    sys.exit(0)

passed, results = all_gates_pass(cfg)
if not passed:
    print(f"[dream] 三门未全过: {{results}}")
    sys.exit(0)

ok, lock = try_acquire_lock(session_id)
if not ok:
    print(f"[dream] 锁获取失败")
    sys.exit(0)

# 触发 isolated session（输出指令，由 OpenClaw cron 执行）
print("[dream] 三门全过，开始整合...")
import subprocess
cmd = [
    "node", "-e",
    '''
    const {{ sessions_spawn }} = require("openclaw").sessions_spawn;
    sessions_spawn({{
        task: "执行记忆整合",
        label: "dream-consolidation",
        runtime: "isolated",
        mode: "run"
    }}).then(r => console.log(JSON.stringify(r))).catch(e => console.error(e));
    '''
]
print("[dream] 请在 OpenClaw cron 中配置触发上述 isolated session")
save_state({{"status": "triggered", "at": int(time.time()*1000), "sessionId": session_id}})
'''

    run_path = get_cron_script_path()
    run_path.write_text(run_script, encoding="utf-8")

    # 输出 cron 创建指令（供用户在 OpenClaw 控制台执行）
    cron_config = {
        "name": CRON_JOB_NAME,
        "schedule": {"kind": "every", "everyMs": int(interval_ms)},
        "payload": {
            "kind": "agentTurn",
            "message": (
                "执行 Dream 记忆整合。\n"
                "读取并执行 ~/.qclaw/skills/dream-skill/references/prompt.md 的 Phase 1→4。\n"
                "操作目录：~/.qclaw/workspace/memory/。\n"
                "完成后发通知。"
            ),
        },
        "sessionTarget": "isolated",
        "enabled": True,
    }

    print("\n✅ Dream Skill cron job 脚本已生成。")
    print(f"\n📋 请在 OpenClaw 控制台执行以下命令创建 cron job：\n")
    print("【命令1：获取 cron action 路径】")
    print("   openclaw cron --help")
    print(f"\n【命令2：创建 cron job】")
    print(f"   openclaw cron add '{_json.dumps(cron_config, ensure_ascii=False)}'")
    print("\n（或者：告诉我在哪个界面操作，我来生成具体命令）")


def teardown_cron():
    """输出卸载指令。"""
    print(f"✅ 卸载步骤：")
    print(f"   openclaw cron remove {CRON_JOB_NAME}")
    print(f"   rm -rf {STATE_DIR}")


# ── CLI 命令 ────────────────────────────────────────────────

def cmd_status(cfg: dict):
    lock = load_lock()
    state = load_state()
    last_at = lock.get("lastConsolidatedAt", 0)
    elapsed_h = hours_since(last_at)
    min_h = cfg.get("minHours", 24)

    print("┌─ Dream Skill 状态 ────────────")
    print(f"│ 上次整合：{ts_to_iso(last_at)}")
    print(f"│ 距今：{elapsed_h:.1f} 小时")
    print(f"│ 下次触发：约 {max(0, min_h - elapsed_h):.1f} 小时后")

    _, session_count, count = check_session_gate(lock, cfg)
    print(f"│ {session_count}")
    print(f"│ 功能：{'启用' if cfg.get('autoDreamEnabled') else '禁用'}")
    print(f"│ 配置：minHours={cfg.get('minHours')} / minSessions={cfg.get('minSessions')}")
    if state:
        print(f"│ 最近状态：{state.get('status')} @ {ts_to_iso(state.get('at', 0))}")
    print("└────────────────────────────────")


def cmd_check(cfg: dict):
    """供 cron 或手动调用，执行完整 gate 检查。"""
    if not cfg.get("autoDreamEnabled", True):
        print("[dream] 功能已禁用（autoDreamEnabled=false）")
        sys.exit(0)

    passed, results = all_gates_pass(cfg)
    for gate, msg in results.items():
        print(f"[dream] {msg}")

    if not passed:
        sys.exit(0)

    # 尝试获取锁
    session_id = f"dream-{int(time.time())}"
    ok, lock = try_acquire_lock(session_id)
    if not ok:
        print("[dream] 锁获取失败，退出")
        sys.exit(0)

    print(f"[dream] 锁获取成功（session={session_id}）")
    print("[dream] 触发 isolated session 执行整合...")
    print(f"[dream] 提示：请通过 OpenClaw cron 触发 isolated session 执行 prompt")
    print(f"[dream] 整合完成后调用：python dream.py --finish")


def cmd_finish(cfg: dict):
    """整合完成后调用，更新 lock 并发送通知。"""
    lock = load_lock()
    new_lock = release_lock(lock)
    save_state({
        "status": "completed",
        "at": new_lock["lastConsolidatedAt"],
    })
    print(f"[dream] 整合完成，lock 已更新：{ts_to_iso(new_lock['lastConsolidatedAt'])}")


def cmd_run(cfg: dict):
    """手动触发（绕过三门限制）。"""
    session_id = f"dream-manual-{int(time.time())}"
    ok, _ = try_acquire_lock(session_id)
    if not ok:
        print("[dream] 锁获取失败（可能有其他实例正在运行），退出")
        sys.exit(1)
    print(f"[dream] 手动触发成功，开始整合...")
    print("[dream] 请在 OpenClaw 中启动 isolated session 执行整合")
    print(f"[dream] 完成后运行：python dream.py --finish")


def main():
    parser = argparse.ArgumentParser(description="Dream Skill 控制脚本")
    parser.add_argument("--setup", action="store_true", help="安装 cron job")
    parser.add_argument("--status", action="store_true", help="查看状态")
    parser.add_argument("--run", action="store_true", help="手动触发整合")
    parser.add_argument("--check", action="store_true", help="三门检查（供 cron 调用）")
    parser.add_argument("--finish", action="store_true", help="整合完成确认")
    parser.add_argument("--teardown", action="store_true", help="卸载")
    args = parser.parse_args()

    cfg = load_config()

    if args.setup:
        setup_cron()
    elif args.teardown:
        teardown_cron()
    elif args.status:
        cmd_status(cfg)
    elif args.check:
        cmd_check(cfg)
    elif args.finish:
        cmd_finish(cfg)
    elif args.run:
        cmd_run(cfg)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
