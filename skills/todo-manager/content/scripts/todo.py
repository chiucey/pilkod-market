#!/usr/bin/env python3
"""
Todo Manager - 命令行工具
用法:
  python3 todo.py add "<内容>" [YYYY-MM-DD HH:MM]
  python3 todo.py list
  python3 todo.py done <id>
  python3 todo.py rm <id>
  python3 todo.py info <id>
"""
import json, sys, os
from datetime import datetime

TODO_DIR = os.path.expanduser("~/.openclaw/todo_manager")
TODO_FILE = os.path.join(TODO_DIR, "todos.json")
os.makedirs(TODO_DIR, exist_ok=True)

def load():
    if not os.path.exists(TODO_FILE):
        return []
    with open(TODO_FILE) as f:
        return json.load(f)

def save(data):
    with open(TODO_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def next_id(data):
    return max([0] + [t["id"] for t in data]) + 1

def cmd_add(args):
    data = load()
    content = args[0]
    due = args[1] if len(args) > 1 else None
    t = {
        "id": next_id(data),
        "content": content,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "due": due,
        "done": False
    }
    data.append(t)
    save(data)
    print(f"✅ 已添加待办 #{t['id']}: {content}" + (f" (提醒: {due})" if due else ""))
    return t

def cmd_list(args):
    data = load()
    if not data:
        print("📋 暂无待办事项")
        return
    undone = [t for t in data if not t["done"]]
    done = [t for t in data if t["done"]]
    print(f"📋 待办列表（共 {len(undone)} 项未完成，{len(done)} 项已完成）\n")
    for t in undone:
        due_str = f" ⏰ {t['due']}" if t.get("due") else ""
        print(f"  [{t['id']}] {t['content']}{due_str}")
    if done:
        print(f"\n  ✅ 已完成:")
        for t in done:
            print(f"  [{t['id']}] {t['content']}")

def cmd_done(args):
    data = load()
    tid = int(args[0])
    for t in data:
        if t["id"] == tid:
            t["done"] = True
            save(data)
            print(f"✅ 已完成: {t['content']}")
            return
    print(f"❌ 未找到 #{tid}")

def cmd_rm(args):
    data = load()
    tid = int(args[0])
    new_data = [t for t in data if t["id"] != tid]
    if len(new_data) == len(data):
        print(f"❌ 未找到 #{tid}")
        return
    save(new_data)
    print(f"🗑️ 已删除 #{tid}")

def cmd_info(args):
    data = load()
    tid = int(args[0])
    for t in data:
        if t["id"] == tid:
            print(f"#{t['id']}: {t['content']}")
            print(f"创建时间: {t['created']}")
            print(f"截止时间: {t.get('due','未设置')}")
            print(f"状态: {'✅ 已完成' if t['done'] else '⬜ 未完成'}")
            return
    print(f"❌ 未找到 #{tid}")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    fn = {"add": cmd_add, "list": cmd_list, "done": cmd_done, "rm": cmd_rm, "info": cmd_info}.get(cmd)
    if fn:
        fn(sys.argv[2:])
    else:
        print("未知命令:", cmd)
