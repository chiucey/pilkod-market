#!/usr/bin/env python3
"""
SQLite 三库记忆系统 - Memory / Knowledge / Items
用法: python3 memory_store.py [db] [action] [args]

数据库:
  memory    - 个人记忆库（偏好、上下文、决定）
  knowledge - 知识库（客观事实、实体关系、有来源）
  items     - 物品库（实体物品、家庭资产管理）
"""
import sqlite3, json, sys, os
from datetime import datetime

SKILL_DIR = "/workspace/skills/self-sqlite-memory"

DBs = {
    "memory":   os.path.join(SKILL_DIR, "memory.db"),
    "knowledge": os.path.join(SKILL_DIR, "knowledge.db"),
    "items":    os.path.join(SKILL_DIR, "items.db"),
}

# ─── 公共 ───────────────────────────────────────────

def get_db(name):
    os.makedirs(SKILL_DIR, exist_ok=True)
    conn = sqlite3.connect(DBs[name])
    conn.row_factory = sqlite3.Row
    return conn

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def dict_row(cur):
    return [dict(r) for r in cur.fetchall()]

def print_row(r, truncate=200):
    tags = json.loads(r.get("tags","[]"))
    pin = "📌 " if r.get("is_pinned") else ""
    cat = r.get("category","")
    date = r.get("created_at","")[:16]
    acc = r.get("access_count",0)
    content = r.get("content", r.get("description",""))[:truncate]
    print(f"  [{r['id']}] {pin}{cat} | {date} | 访问{acc}次")
    print(f"    {content}")
    if tags: print(f"    标签: {', '.join(tags)}")

# ─── init ──────────────────────────────────────────

def init_memory():
    db = get_db("memory")
    db.executescript("""
    CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        category TEXT DEFAULT 'general',
        tags TEXT DEFAULT '[]',
        importance INTEGER DEFAULT 3,
        is_pinned INTEGER DEFAULT 0,
        access_count INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now')),
        last_accessed_at TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_mem_cat ON memories(category);
    CREATE TABLE IF NOT EXISTS evolutions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT,
        before TEXT,
        after TEXT,
        trigger TEXT,
        lesson TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );
    """)
    db.commit()
    return db

def init_knowledge():
    db = get_db("knowledge")
    db.executescript("""
    CREATE TABLE IF NOT EXISTS knowledge (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        property TEXT,
        value TEXT,
        description TEXT,
        source TEXT,
        confidence REAL DEFAULT 1.0,
        tags TEXT DEFAULT '[]',
        access_count INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS relations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_entity TEXT NOT NULL,
        relation_type TEXT NOT NULL,
        to_entity TEXT NOT NULL,
        description TEXT,
        source TEXT,
        confidence REAL DEFAULT 1.0,
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE INDEX IF NOT EXISTS idx_kg_subject ON knowledge(subject);
    CREATE INDEX IF NOT EXISTS idx_kg_type ON knowledge(entity_type);
    CREATE INDEX IF NOT EXISTS idx_rel_from ON relations(from_entity);
    """)
    db.commit()
    return db

def init_items():
    db = get_db("items")
    db.executescript("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        owner TEXT DEFAULT '全局',
        brand TEXT,
        model TEXT,
        serial_number TEXT,
        purchase_date TEXT,
        warranty_expire TEXT,
        estimated_value REAL,
        location TEXT,
        condition TEXT DEFAULT '良好',
        notes TEXT,
        tags TEXT DEFAULT '[]',
        access_count INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );
    CREATE INDEX IF NOT EXISTS idx_item_cat ON items(category);
    CREATE INDEX IF NOT EXISTS idx_item_owner ON items(owner);
    """)
    db.commit()
    return db

def init_all():
    init_memory()
    init_knowledge()
    init_items()

# ══════════════════════════════════════════════════
# MEMORY 库
# ══════════════════════════════════════════════════

def cmd_mem_add(args):
    """mem add <内容> --category --tags --importance"""
    init_memory()
    conn = get_db("memory")
    content, category, tags, importance = None, "general", "[]", 3
    i = 0
    while i < len(args):
        if args[i] == "--category" and i+1<len(args): category=args[i+1]; i+=2
        elif args[i] == "--tags" and i+1<len(args): tags=json.dumps(args[i+1].split(",")); i+=2
        elif args[i] == "--importance" and i+1<len(args): importance=int(args[i+1]); i+=2
        elif not content: content=args[i]; i+=1
        else: i+=1
    if not content:
        print("❌ 内容不能为空"); return
    cur = conn.execute(
        "INSERT INTO memories(content,category,tags,importance) VALUES(?,?,?,?)",
        (content, category, tags, importance)
    )
    conn.commit()
    print(f"✅ 记忆已添加，ID: {cur.lastrowid}")
    conn.close()

def cmd_mem_search(args):
    """mem search <关键词>"""
    init_memory()
    conn = get_db("memory")
    query = args[0] if args else ""
    cur = conn.execute(
        "SELECT * FROM memories WHERE content LIKE ? ORDER BY importance DESC, created_at DESC LIMIT 20",
        (f"%{query}%",)
    )
    rows = cur.fetchall()
    if not rows: print("未找到匹配记忆"); conn.close(); return
    print(f"找到 {len(rows)} 条记忆:\n")
    for r in rows: print_row(r)
    conn.close()

def cmd_mem_list(args):
    """mem list --category --limit"""
    init_memory()
    conn = get_db("memory")
    cat, limit = None, 20
    i = 0
    while i < len(args):
        if args[i]=="--category" and i+1<len(args): cat=args[i+1]; i+=2
        elif args[i]=="--limit" and i+1<len(args): limit=int(args[i+1]); i+=2
        else: i+=1
    if cat:
        cur = conn.execute(
            "SELECT * FROM memories WHERE category=? ORDER BY is_pinned DESC, importance DESC, created_at DESC LIMIT ?",
            (cat, limit)
        )
    else:
        cur = conn.execute(
            "SELECT * FROM memories ORDER BY is_pinned DESC, importance DESC, created_at DESC LIMIT ?",
            (limit,)
        )
    rows = cur.fetchall()
    print(f"共 {len(rows)} 条记忆:\n")
    for r in rows: print_row(r)
    conn.close()

def cmd_mem_stats(_=None):
    """mem stats"""
    init_memory()
    conn = get_db("memory")
    cur = conn.execute
    total = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
    cats = conn.execute("SELECT category,COUNT(*) cnt FROM memories GROUP BY category").fetchall()
    evo  = conn.execute("SELECT COUNT(*) FROM evolutions").fetchone()[0]
    print(f"📊 记忆统计")
    print(f"  总记忆数: {total}  条")
    print(f"  进化记录: {evo}   条")
    for r in cats: print(f"    {r['category']}: {r['cnt']} 条")
    conn.close()

def cmd_mem_evolve(args):
    """mem evolve <topic> <before> <after> <trigger> <lesson..."""
    init_memory()
    if len(args) < 4: print("用法: mem evolve <topic> <before> <after> <trigger> <lesson>"); return
    topic, before, after, trigger = args[0], args[1], args[2], args[3]
    lesson = " ".join(args[4:])
    conn = get_db("memory")
    conn.execute(
        "INSERT INTO evolutions(topic,before,after,trigger,lesson) VALUES(?,?,?,?,?)",
        (topic, before, after, trigger, lesson)
    )
    conn.commit()
    print(f"✅ 进化记录已保存")
    conn.close()

# ══════════════════════════════════════════════════
# KNOWLEDGE 库
# ══════════════════════════════════════════════════

def cmd_kg_add(args):
    """kg add <主体> <类型> [description] --property --value --source --tags"""
    init_knowledge()
    if len(args) < 2: print("用法: kg add <主体> <类型> [描述] [--property] [--value] [--source] [--tags]"); return
    subject, entity_type, description = args[0], args[1], " ".join(args[2:])
    prop, value, source, tags = None, None, None, "[]"
    args2 = args[2:]
    i = 0
    while i < len(args2):
        if args2[i]=="--property" and i+1<len(args2): prop=args2[i+1]; i+=2
        elif args2[i]=="--value" and i+1<len(args2): value=args2[i+1]; i+=2
        elif args2[i]=="--source" and i+1<len(args2): source=args2[i+1]; i+=2
        elif args2[i]=="--tags" and i+1<len(args2): tags=json.dumps(args2[i+1].split(",")); i+=2
        else: i+=1
    conn = get_db("knowledge")
    conn.execute(
        "INSERT INTO knowledge(subject,entity_type,description,property,value,source,tags) VALUES(?,?,?,?,?,?,?)",
        (subject, entity_type, description, prop, value, source, tags)
    )
    conn.commit()
    print(f"✅ 知识条目已添加")
    conn.close()

def cmd_kg_search(args):
    """kg search <关键词>"""
    init_knowledge()
    if not args: print("用法: kg search <关键词>"); return
    query = args[0]
    conn = get_db("knowledge")
    cur = conn.execute(
        "SELECT * FROM knowledge WHERE subject LIKE ? OR description LIKE ? OR property LIKE ? ORDER BY confidence DESC, created_at DESC LIMIT 20",
        (f"%{query}%", f"%{query}%", f"%{query}%")
    )
    rows = cur.fetchall()
    if not rows: print("未找到匹配知识"); conn.close(); return
    print(f"找到 {len(rows)} 条知识:\n")
    for r in rows:
        tags = json.loads(r["tags"] or "[]")
        print(f"  [{r['id']}] {r['entity_type']} | {r['subject']} | 置信度 {r['confidence']:.0%}")
        if r["property"]: print(f"    属性: {r['property']} = {r['value']}")
        if r["description"]: print(f"    {r['description'][:150]}")
        if r["source"]: print(f"    来源: {r['source']}")
        if tags: print(f"    标签: {', '.join(tags)}")
        print()
    conn.close()

def cmd_kg_rel_add(args):
    """kg rel <from_entity> <relation_type> <to_entity> [--source] [--desc]"""
    init_knowledge()
    if len(args) < 3: print("用法: kg rel <实体A> <关系> <实体B> [--source] [--desc]"); return
    from_e, rel_type, to_e = args[0], args[1], args[2]
    source, desc = None, None
    i = 3
    while i < len(args):
        if args[i]=="--source" and i+1<len(args): source=args[i+1]; i+=2
        elif args[i]=="--desc" and i+1<len(args): desc=args[i+1]; i+=2
        else: i+=1
    conn = get_db("knowledge")
    conn.execute(
        "INSERT INTO relations(from_entity,relation_type,to_entity,description,source) VALUES(?,?,?,?,?)",
        (from_e, rel_type, to_e, desc, source)
    )
    conn.commit()
    print(f"✅ 关系已添加: {from_e} —[{rel_type}]→ {to_e}")
    conn.close()

def cmd_kg_rel_search(args):
    """kg rels <实体名>"""
    init_knowledge()
    if not args: print("用法: kg rels <实体名>"); return
    entity = args[0]
    conn = get_db("knowledge")
    cur = conn.execute(
        "SELECT * FROM relations WHERE from_entity LIKE ? OR to_entity LIKE ? LIMIT 20",
        (f"%{entity}%", f"%{entity}%")
    )
    rows = cur.fetchall()
    if not rows: print("未找到关系"); conn.close(); return
    print(f"找到 {len(rows)} 条关系:\n")
    for r in rows:
        print(f"  {r['from_entity']} —[{r['relation_type']}]→ {r['to_entity']}")
        if r["description"]: print(f"    {r['description']}")
        if r["source"]: print(f"    来源: {r['source']}")
    conn.close()

def cmd_kg_stats(_=None):
    """kg stats"""
    init_knowledge()
    conn = get_db("knowledge")
    total = conn.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0]
    types = conn.execute("SELECT entity_type,COUNT(*) cnt FROM knowledge GROUP BY entity_type").fetchall()
    rels  = conn.execute("SELECT COUNT(*) FROM relations").fetchone()[0]
    print(f"📊 知识统计")
    print(f"  知识条目: {total} 条")
    print(f"  关系数:   {rels}  条")
    for r in types: print(f"    {r['entity_type']}: {r['cnt']} 条")
    conn.close()

# ══════════════════════════════════════════════════
# ITEMS 库
# ══════════════════════════════════════════════════

ITEM_CATEGORIES = [
    "电子产品", "家具", "证件", "文件", "工具",
    "家用电器", "服装", "食品/药品", "收藏品", "其他"
]

def cmd_item_add(args):
    """item add <名称> <类别> --owner --brand --model --serial --value --location --condition --notes"""
    init_items()
    if len(args) < 2: print("用法: item add <名称> <类别> [--owner] [--brand] [--model] [--serial] [--value] [--location] [--condition] [--notes]"); return
    name, category = args[0], args[1]
    if category not in ITEM_CATEGORIES:
        print(f"⚠️  未知类别，建议用: {', '.join(ITEM_CATEGORIES)}")
    owner, brand, model, serial, value, location, condition, notes = "全局", None, None, None, None, None, "良好", None
    tags = "[]"; i = 2
    while i < len(args):
        if args[i]=="--owner" and i+1<len(args): owner=args[i+1]; i+=2
        elif args[i]=="--brand" and i+1<len(args): brand=args[i+1]; i+=2
        elif args[i]=="--model" and i+1<len(args): model=args[i+1]; i+=2
        elif args[i]=="--serial" and i+1<len(args): serial=args[i+1]; i+=2
        elif args[i]=="--value" and i+1<len(args): value=float(args[i+1]); i+=2
        elif args[i]=="--location" and i+1<len(args): location=args[i+1]; i+=2
        elif args[i]=="--condition" and i+1<len(args): condition=args[i+1]; i+=2
        elif args[i]=="--notes" and i+1<len(args): notes=args[i+1]; i+=2
        elif args[i]=="--tags" and i+1<len(args): tags=json.dumps(args[i+1].split(",")); i+=2
        else: i+=1
    conn = get_db("items")
    conn.execute(
        "INSERT INTO items(name,category,owner,brand,model,serial_number,estimated_value,location,condition,notes,tags) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
        (name, category, owner, brand, model, serial, value, location, condition, notes, tags)
    )
    conn.commit()
    print(f"✅ 物品已添加: {name}（{category}，所属: {owner}）")
    conn.close()

def cmd_item_search(args):
    """item search <关键词> [--owner] [--category]"""
    init_items()
    query, owner, category = "", None, None
    i = 0
    while i < len(args):
        if args[i]=="--owner" and i+1<len(args): owner=args[i+1]; i+=2
        elif args[i]=="--category" and i+1<len(args): category=args[i+1]; i+=2
        elif not query: query=args[i]; i+=1
        else: i+=1
    conn = get_db("items")
    sql = "SELECT * FROM items WHERE (name LIKE ? OR brand LIKE ? OR model LIKE ? OR notes LIKE ?)"
    params = [f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"]
    if owner:   sql += " AND owner=?";   params.append(owner)
    if category: sql += " AND category=?"; params.append(category)
    sql += " ORDER BY created_at DESC LIMIT 20"
    rows = conn.execute(sql, params).fetchall()
    if not rows: print("未找到匹配物品"); conn.close(); return
    print(f"找到 {len(rows)} 件物品:\n")
    for r in rows:
        val = f"¥{r['estimated_value']:,.0f}" if r['estimated_value'] else "未定价"
        print(f"  [{r['id']}] {r['name']} | {r['category']} | {r['owner']} | {val}")
        if r["brand"] or r["model"]: print(f"    品牌型号: {r['brand'] or ''} {r['model'] or ''}".strip())
        if r["location"]: print(f"    位置: {r['location']}")
        if r["condition"]: print(f"    状态: {r['condition']}")
        if r["serial_number"]: print(f"    序列号: {r['serial_number']}")
        print()
    conn.close()

def cmd_item_list(args):
    """item list --owner --category --limit"""
    init_items()
    owner, category, limit = None, None, 50
    i = 0
    while i < len(args):
        if args[i]=="--owner" and i+1<len(args): owner=args[i+1]; i+=2
        elif args[i]=="--category" and i+1<len(args): category=args[i+1]; i+=2
        elif args[i]=="--limit" and i+1<len(args): limit=int(args[i+1]); i+=2
        else: i+=1
    conn = get_db("items")
    sql, params = "SELECT * FROM items WHERE 1=1", []
    if owner:    sql += " AND owner=?";    params.append(owner)
    if category: sql += " AND category=?"; params.append(category)
    sql += " ORDER BY category, name LIMIT ?"; params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    if not rows: print("没有物品记录"); conn.close(); return
    print(f"共 {len(rows)} 件物品:\n")
    for r in rows:
        val = f"¥{r['estimated_value']:,.0f}" if r['estimated_value'] else "未定价"
        print(f"  [{r['id']}] {r['name']} | {r['category']} | {r['owner']} | {val}")
    conn.close()

def cmd_item_get(args):
    """item get <id>"""
    init_items()
    if not args: print("用法: item get <id>"); return
    conn = get_db("items")
    r = conn.execute("SELECT * FROM items WHERE id=?", (args[0],)).fetchone()
    if not r: print("物品不存在"); conn.close(); return
    val = f"¥{r['estimated_value']:,.0f}" if r['estimated_value'] else "未定价"
    print(f"📦 {r['name']}")
    print(f"  类别: {r['category']}  |  使用人: {r['owner']}  |  状态: {r['condition']}")
    print(f"  品牌: {r['brand'] or '—'}  |  型号: {r['model'] or '—'}")
    print(f"  序列号: {r['serial_number'] or '—'}")
    print(f"  估值: {val}  |  位置: {r['location'] or '—'}")
    print(f"  购买日期: {r['purchase_date'] or '—'}  |  保修到期: {r['warranty_expire'] or '—'}")
    if r["notes"]: print(f"  备注: {r['notes']}")
    if r["tags"]:
        tags = json.loads(r["tags"]); print(f"  标签: {', '.join(tags)}")
    conn.close()

def cmd_item_update(args):
    """item update <id> [--name] [--owner] [--value] [--location] [--condition] [--notes]"""
    init_items()
    if not args or not args[0].isdigit(): print("用法: item update <id> [--name] [--owner] [--value] [--location] [--condition] [--notes]"); return
    conn = get_db("items")
    id_ = int(args[0]); i = 1
    updates, params = [], []
    while i < len(args):
        if args[i]=="--name" and i+1<len(args): updates.append("name=?"); params.append(args[i+1]); i+=2
        elif args[i]=="--owner" and i+1<len(args): updates.append("owner=?"); params.append(args[i+1]); i+=2
        elif args[i]=="--value" and i+1<len(args): updates.append("estimated_value=?"); params.append(float(args[i+1])); i+=2
        elif args[i]=="--location" and i+1<len(args): updates.append("location=?"); params.append(args[i+1]); i+=2
        elif args[i]=="--condition" and i+1<len(args): updates.append("condition=?"); params.append(args[i+1]); i+=2
        elif args[i]=="--notes" and i+1<len(args): updates.append("notes=?"); params.append(args[i+1]); i+=2
        else: i+=1
    if not updates: print("没有更新字段"); conn.close(); return
    params.append(str(now())); params.append(id_)
    conn.execute(f"UPDATE items SET {','.join(updates)}, updated_at=? WHERE id=?", params)
    conn.commit()
    print(f"✅ 物品已更新")
    conn.close()

def cmd_item_delete(args):
    """item delete <id>"""
    init_items()
    if not args: print("用法: item delete <id>"); return
    conn = get_db("items")
    conn.execute("DELETE FROM items WHERE id=?", (args[0],))
    conn.commit()
    print(f"✅ 物品已删除")
    conn.close()

def cmd_item_stats(_=None):
    """item stats"""
    init_items()
    conn = get_db("items")
    total = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
    total_val = conn.execute("SELECT SUM(estimated_value) FROM items WHERE estimated_value IS NOT NULL").fetchone()[0] or 0
    cats = conn.execute("SELECT category,COUNT(*) cnt,SUM(estimated_value) val FROM items GROUP BY category").fetchall()
    owners = conn.execute("SELECT owner,COUNT(*) cnt FROM items GROUP BY owner").fetchall()
    print(f"📊 物品统计")
    print(f"  总物品数: {total} 件")
    print(f"  总估值:   ¥{total_val:,.0f}")
    print(f"  按类别:")
    for r in cats:
        val = f"¥{r['val']:,.0f}" if r['val'] else ""
        print(f"    {r['category']}: {r['cnt']}件  {val}")
    print(f"  按使用人:")
    for r in owners: print(f"    {r['owner']}: {r['cnt']}件")
    conn.close()

# ══════════════════════════════════════════════════
# DISPATCH
# ══════════════════════════════════════════════════

USAGE = """
╔══════════════════════════════════════════════════╗
║        SQLite 三库记忆系统 - 帮助              ║
╠══════════════════════════════════════════════════╣
║  memory 库 - 个人记忆（偏好、上下文、决定）    ║
║  ┣ add <内容> [--category] [--tags] [--importance] ║
║  ┣ search <关键词>                             ║
║  ┣ list [--category] [--limit]                  ║
║  ┣ stats                                       ║
║  ┗ evolve <topic> <before> <after> <trigger> <lesson> ║
╠══════════════════════════════════════════════════╣
║  knowledge 库 - 客观知识（有来源的事实）      ║
║  ┣ add <主体> <类型> [描述] [--property] [--value] [--source] ║
║  ┣ search <关键词>                             ║
║  ┣ rel <A> <关系> <B> [--source] [--desc]    ║
║  ┣ rels <实体名>                               ║
║  ┗ stats                                       ║
╠══════════════════════════════════════════════════╣
║  items 库 - 家庭物品管理                      ║
║  ┣ add <名称> <类别> [--owner] [--brand] [--model] [--serial] [--value] [--location] [--condition] ║
║  ┣ search <关键词> [--owner] [--category]      ║
║  ┣ list [--owner] [--category] [--limit]       ║
║  ┣ get <id>                                    ║
║  ┣ update <id> [--name/owner/value/location/condition/notes] ║
║  ┣ delete <id>                                  ║
║  ┗ stats                                       ║
╚══════════════════════════════════════════════════╝

示例:
  python3 memory_store.py mem add "我喜欢在安静环境工作" --category preference
  python3 memory_store.py kg add T310 timer "T310定时器定义" --property 章节 --value "5.3.10" --source "TS 36.331"
  python3 memory_store.py kg rel T310 触发 N310 --source "TS 36.331 §5.3.10"
  python3 memory_store.py item add "MacBook Pro" 电子产品 --owner kirk --value 12000 --location 书房
  python3 memory_store.py item list --owner kirk
  python3 memory_store.py item stats
"""

if __name__ == "__main__":
    init_all()
    if len(sys.argv) < 3:
        print(USAGE); sys.exit(0)

    db = sys.argv[1]
    cmd = sys.argv[2]
    args = sys.argv[3:]

    if db == "mem":
        dispatch = {
            "add": cmd_mem_add, "search": cmd_mem_search,
            "list": cmd_mem_list, "stats": cmd_mem_stats,
            "evolve": cmd_mem_evolve,
        }
    elif db == "kg":
        dispatch = {
            "add": cmd_kg_add, "search": cmd_kg_search,
            "rel": cmd_kg_rel_add, "rels": cmd_kg_rel_search,
            "stats": cmd_kg_stats,
        }
    elif db == "item":
        dispatch = {
            "add": cmd_item_add, "search": cmd_item_search,
            "list": cmd_item_list, "get": cmd_item_get,
            "update": cmd_item_update, "delete": cmd_item_delete,
            "stats": cmd_item_stats,
        }
    else:
        print(f"未知数据库: {db}，可用: mem / kg / item")
        sys.exit(1)

    if cmd in dispatch:
        dispatch[cmd](args)
    else:
        print(f"未知命令: {cmd}，可用: {', '.join(dispatch.keys())}")
