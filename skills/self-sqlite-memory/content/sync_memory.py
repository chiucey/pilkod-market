#!/usr/bin/env python3
"""
定时记忆任务（增强版）
每天 03:00 运行，流程：
  1. MEMORY.md → memory.db（增量同步）
  2. 遍历所有记忆，重新归类
  3. 感悟生成 + 写入 memory.db（由唤醒的 sub-agent 完成）
  4. 感悟摘要发飞书（由唤醒的 sub-agent 完成）

感悟生成说明：
  - 由 cron 唤醒的 sub-agent 调用 OpenClaw 自身智能完成
  - 读取 memory.db + knowledge.db + items.db 内容
  - 生成 3-5 条感悟，写入 memory.db
  - 感悟摘要发飞书
"""
import sqlite3, json, os
from datetime import datetime, timedelta

SKILL_DIR = "/workspace/skills/self-sqlite-memory"
MEMORY_PATH = "/workspace/MEMORY.md"
MEMORY_DIR = "/workspace/memory"

DB_MEMORY  = f"{SKILL_DIR}/memory.db"
DB_KNOWLEDGE = f"{SKILL_DIR}/knowledge.db"
DB_ITEMS   = f"{SKILL_DIR}/items.db"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def get_conn(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def infer_category(text):
    t = text.lower()
    if any(k in t for k in ["偏好", "preference", "喜欢", "用户设定", "不喜欢"]): return "preferences"
    if any(k in t for k in ["教训", "纠正", "evolve", "错误"]): return "learned"
    if any(k in t for k in ["会话", "session", "本次", "这次", "今日"]): return "context"
    return "general"

def infer_tags(text):
    tags, t = [], text.lower()
    for tag, kw in [("platform","平台"), ("feishu","飞书"), ("skill","记忆"),
                    ("cleanup","清理"), ("nas","NAS"), ("protocol","协议")]:
        if kw in t: tags.append(tag)
    return tags or ["sync"]

# ════════════════════════════════════════════
# 1. MEMORY.md → memory.db 增量同步
# ════════════════════════════════════════════

def sync_memory_md():
    conn = get_conn(DB_MEMORY)
    existing = {r["content"] for r in conn.execute("SELECT content FROM memories")}
    conn.close()

    def parse_file(path):
        if not os.path.exists(path): return []
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
        entries, current = [], []
        in_code = False
        for line in lines:
            if line.startswith("```"): in_code = not in_code; continue
            if in_code: continue
            s = line.strip()
            if s.startswith("#") or s.startswith("<!--") or s.startswith("*") or not s:
                if current: entries.append("".join(current).strip()); current = []
                continue
            current.append(line)
        if current: entries.append("".join(current).strip())
        return [e for e in entries if e]

    # 只处理最近3天的文件
    three_days_ago = datetime.now() - timedelta(days=3)
    all_paths = [MEMORY_PATH] + sorted([
        os.path.join(MEMORY_DIR, f)
        for f in os.listdir(MEMORY_DIR)
    ] if os.path.exists(MEMORY_DIR) else [])

    def recent_paths():
        for p in all_paths:
            # MEMORY.md 永远处理
            if p == MEMORY_PATH:
                yield p
                continue
            # 3天内的每日记录才处理
            mtime = datetime.fromtimestamp(os.path.getmtime(p))
            if mtime >= three_days_ago:
                yield p

    new_entries = []
    for path in recent_paths():
        for e in parse_file(path):
            if e not in existing:
                new_entries.append(e)

    if new_entries:
        conn = get_conn(DB_MEMORY)
        now_s = datetime.now().isoformat()
        for entry in new_entries:
            conn.execute(
                "INSERT INTO memories(content,category,tags,created_at,updated_at) VALUES(?,?,?,?,?)",
                (entry, infer_category(entry), json.dumps(infer_tags(entry)), now_s, now_s))
        conn.commit()
        conn.close()
        log(f"✅ MEMORY.md → memory.db：{len(new_entries)} 条新内容")
    else:
        log("ℹ️ MEMORY.md → memory.db：无新增内容")

# ════════════════════════════════════════════
# 2. 遍历记忆，重新归类
# ════════════════════════════════════════════

def reclassify():
    conn = get_conn(DB_MEMORY)
    rows = conn.execute("SELECT id, content, category FROM memories").fetchall()
    updated = 0
    for r in rows:
        new_cat = infer_category(r["content"])
        if new_cat != r["category"]:
            conn.execute("UPDATE memories SET category=? WHERE id=?", (new_cat, r["id"]))
            updated += 1
    conn.commit()
    conn.close()
    if updated:
        log(f"✅ 重新归类：{updated} 条记忆分类已更新")
    else:
        log("ℹ️ 重新归类：无分类变更")

# ════════════════════════════════════════════
# 主流程（脚本执行部分）
# 注意：感悟生成由 cron 唤醒的 sub-agent 完成
# ════════════════════════════════════════════

def main():
    log("═══ 记忆任务开始 ═══")
    sync_memory_md()
    reclassify()
    log("═══ 脚本执行完毕，感悟生成由 sub-agent 完成 ═══")

if __name__ == "__main__":
    main()
