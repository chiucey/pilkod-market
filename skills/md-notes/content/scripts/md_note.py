#!/usr/bin/env python3
"""
MD笔记工具 - 保存为本地MD文件 + 推送到IMA
用法:
  md_note.py save "<标题>" "<内容>"
  md_note.py list
  md_note.py search "<关键词>"
  md_note.py read "<标题关键词>"
"""
import json, sys, os, re
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError

CLIENT_ID = "ac450a75b90f5a62b87ccaeaf0e528ff"
API_KEY   = "DAljR5Wv5AXxFI046DzlWm0Wha8g7Kso1mLRv0suKhgcSqeNgxRhhmxaNnHMR5YEvQMQKgWtWg=="

NOTE_DIR = os.path.expanduser("~/.openclaw/md_notes")
INDEX_FILE = os.path.join(NOTE_DIR, "index.json")
os.makedirs(NOTE_DIR, exist_ok=True)

def slug(text):
    """生成安全的文件名"""
    s = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
    s = re.sub(r'[\s]+', '-', s).strip('-')
    return s[:40] or "untitled"

def today():
    return datetime.now().strftime("%Y-%m-%d")

def to_markdown(title, content):
    """构建标准MD格式"""
    return f"""# {title}

> 创建时间：{today()}

---

{content}

---
*由 AI 助手自动生成 | {today()}*
"""

def save_local(title, content):
    """保存到本地MD文件"""
    base = slug(title)
    i = 1
    fname = f"{base}.md"
    while os.path.exists(os.path.join(NOTE_DIR, fname)):
        fname = f"{base}_{i}.md"
        i += 1
    path = os.path.join(NOTE_DIR, fname)
    with open(path, "w", encoding="utf-8") as f:
        f.write(to_markdown(title, content))
    return path

def save_to_index(title, path):
    """更新本地索引"""
    idx = []
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE) as f:
            idx = json.load(f)
    idx.insert(0, {
        "title": title,
        "file": os.path.basename(path),
        "path": path,
        "created": today()
    })
    with open(INDEX_FILE, "w") as f:
        json.dump(idx, f, ensure_ascii=False, indent=2)

def push_ima(title, content):
    """推送到IMA笔记"""
    md = to_markdown(title, content)
    body = json.dumps({
        "content_format": 1,
        "content": md
    }).encode("utf-8")
    req = Request(
        "https://ima.qq.com/openapi/note/v1/import_doc",
        data=body,
        headers={
            "ima-openapi-clientid": CLIENT_ID,
            "ima-openapi-apikey": API_KEY,
            "Content-Type": "application/json; charset=utf-8"
        },
        method="POST"
    )
    try:
        with urlopen(req, timeout=15) as r:
            d = json.loads(r.read().decode("utf-8"))
            if d.get("code") == 0:
                nid = d.get("data", {}).get("note_id", "")
                return True, nid
            return False, d.get("msg", "未知错误")
    except HTTPError as e:
        return False, f"HTTP错误: {e.code}"
    except Exception as e:
        return False, str(e)

def cmd_save(args):
    title = args[0]
    content = args[1] if len(args) > 1 else ""
    # 保存本地
    path = save_local(title, content)
    save_to_index(title, path)
    # 推送IMA
    ok, result = push_ima(title, content)
    print(f"✅ 已保存: {title}")
    print(f"📁 本地: {path}")
    if ok:
        print(f"📱 IMA: 已推送 (note_id: {result})")
    else:
        print(f"⚠️ IMA推送失败: {result}")
    return path

def cmd_list(args):
    if not os.path.exists(INDEX_FILE):
        print("（暂无笔记）")
        return
    with open(INDEX_FILE) as f:
        idx = json.load(f)
    if not idx:
        print("（暂无笔记）")
        return
    print(f"\n📒 笔记列表（共 {len(idx)} 篇）\n")
    for item in idx:
        print(f"  [{item['created']}] {item['title']}")
        print(f"           📁 {item['file']}")
        print()

def cmd_search(args):
    kw = args[0].lower()
    if not os.path.exists(INDEX_FILE):
        print("（暂无笔记）")
        return
    with open(INDEX_FILE) as f:
        idx = json.load(f)
    hits = [i for i in idx if kw in i["title"].lower()]
    if not hits:
        print(f"未找到包含「{kw}」的笔记")
        return
    print(f"找到 {len(hits)} 篇：\n")
    for item in hits:
        print(f"  [{item['created']}] {item['title']}")
        print(f"           📁 {item['file']}")
        print()

def cmd_read(args):
    kw = args[0].lower()
    if not os.path.exists(INDEX_FILE):
        print("（暂无笔记）")
        return
    with open(INDEX_FILE) as f:
        idx = json.load(f)
    hits = [i for i in idx if kw in i["title"].lower()]
    if not hits:
        print(f"未找到：{kw}")
        return
    item = hits[0]
    path = item["path"]
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            print(f.read())
    else:
        print(f"本地文件不存在: {path}")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    fn = {"save": cmd_save, "list": cmd_list, "search": cmd_search, "read": cmd_read}.get(cmd)
    if fn:
        fn(sys.argv[2:])
    else:
        print("用法: md_note.py [save|list|search|read]")
