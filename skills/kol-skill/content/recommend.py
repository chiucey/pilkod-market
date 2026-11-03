#!/usr/bin/env python3
"""
kol-skill recommend v3.0 — 智能推荐引擎
零依赖（仅 Python 标准库），毫秒级响应。

改进:
  - 分类相关性加权：搜索词匹配分类时加分
  - 分类不相关惩罚：搜索词与分类矛盾时扣分
  - 中英文分词：英文词不做bigram碎化，中文词才做
  - 信源多样性：同一查询不连续出现3个同源skill
"""

import json, sys, argparse, os, re, io
from pathlib import Path

# Windows GBK 终端兼容
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ─── 数据加载 ───────────────────────────────────────────────
_DATA = None

def _load():
    global _DATA
    if _DATA is not None:
        return _DATA
    p = Path(__file__).parent / "skills.json"
    with open(p, encoding="utf-8") as f:
        _DATA = json.load(f)
    return _DATA

# ─── 查询词→分类映射（提升推荐精度）────────────────────────
_QUERY_CAT_MAP = {
    # 文档/Office
    "docx": ["OFFICE-DOC", "办公文档"], "doc": ["OFFICE-DOC", "办公文档"],
    "word": ["OFFICE-DOC", "办公文档"], "文档": ["OFFICE-DOC", "办公文档"],
    "pdf": ["OFFICE-DOC", "办公文档"], "pptx": ["OFFICE-DOC", "办公文档"],
    "ppt": ["OFFICE-DOC", "办公文档"], "幻灯片": ["OFFICE-DOC", "办公文档"],
    # Excel/表格
    "xlsx": ["OFFICE-DOC", "办公文档", "DATA-PROC"], "excel": ["OFFICE-DOC", "办公文档", "DATA-PROC"],
    "表格": ["OFFICE-DOC", "办公文档", "DATA-PROC"], "csv": ["OFFICE-DOC", "办公文档", "DATA-PROC"],
    # 视频
    "视频": ["CREATE-VIDEO", "AI创作", "媒体运营"], "视频制作": ["CREATE-VIDEO", "AI创作", "媒体运营"],
    "剪辑": ["CREATE-VIDEO", "AI创作", "媒体运营"], "video": ["CREATE-VIDEO", "AI创作", "媒体运营"],
    "剪映": ["CREATE-VIDEO", "媒体运营"],
    # 内容创作
    "内容创作": ["CREATE-WRITE", "内容写作", "AI创作"], "写作": ["CREATE-WRITE", "内容写作"],
    "文案": ["CREATE-WRITE", "内容写作", "电商营销"], "写作助手": ["CREATE-WRITE", "内容写作"],
    # 电商
    "电商": ["电商营销", "MKT"], "营销": ["电商营销", "MKT"], "广告": ["MKT-AD"],
    "带货": ["电商营销", "媒体运营"], "直播": ["媒体运营", "电商营销"],
    # 图片/设计
    "图片": ["CREATE-IMAGE", "设计创意", "AI创作"], "设计": ["设计创意", "CREATE-IMAGE"],
    "海报": ["设计创意", "CREATE-IMAGE"],
    # AI/Agent
    "ai": ["AI", "AI-AGENT"], "agent": ["AI-AGENT"], "智能体": ["AI-AGENT"],
    # 开发
    "代码": ["DEV", "DEV-FE", "DEV-BE"], "前端": ["DEV-FE"], "后端": ["DEV-BE"],
    "测试": ["DEV-TEST"], "运维": ["DEV-OPS"],
    # 搜索
    "搜索": ["LIFE-SEARCH", "AI-RAG"], "RAG": ["AI-RAG"],
    # 自我提升
    "自我提升": ["学习成长", "AI-AGENT"], "学习": ["学习成长"],
}

# 不相关的分类对（搜索意图 vs skill分类），用于惩罚
_IRRELEVANT_PAIRS = [
    # 搜索意图关键词 → 应该被惩罚的分类
    ("docx", "DEV-TEST"), ("docx", "DEV-FE"), ("docx", "DEV-OPS"),
    ("word", "DEV-TEST"), ("word", "DEV-FE"),
    ("文档", "DEV-TEST"), ("文档", "DEV-FE"), ("文档", "DEV-OPS"),
    ("excel", "DEV-TEST"), ("excel", "DEV-FE"), ("excel", "AI-AGENT"),
    ("表格", "DEV-TEST"), ("表格", "DEV-FE"), ("表格", "AI-AGENT"),
    ("xlsx", "DEV-TEST"), ("xlsx", "DEV-FE"), ("xlsx", "AI-AGENT"),
    ("视频", "DEV-TEST"), ("视频", "DEV-FE"), ("视频", "DEV-OPS"),
    ("剪辑", "DEV-TEST"), ("剪辑", "DEV-FE"),
    ("内容创作", "DEV-TEST"), ("内容创作", "DEV-FE"),
    ("写作", "DEV-TEST"), ("写作", "DEV-FE"), ("写作", "DEV-OPS"),
    ("文案", "DEV-TEST"), ("文案", "DEV-FE"),
    ("电商", "DEV-TEST"), ("电商", "DEV-FE"),
    ("营销", "DEV-TEST"), ("营销", "DEV-FE"),
    ("设计", "DEV-TEST"), ("设计", "DEV-OPS"),
    ("图片", "DEV-TEST"), ("图片", "DEV-OPS"),
    ("pdf", "DEV-TEST"), ("pdf", "DEV-FE"), ("pdf", "DEV-OPS"),
]

# ─── 分类别名映射 ──────────────────────────────────────────
_CAT_ALIAS = {
    "办公": "OFFICE", "文档": "OFFICE-DOC", "日历": "OFFICE-CAL",
    "邮件": "OFFICE-MAIL", "项目管理": "OFFICE-PM", "知识库": "OFFICE-KB",
    "开发": "DEV", "前端": "DEV-FE", "后端": "DEV-BE", "全栈": "DEV-FS",
    "测试": "DEV-TEST", "运维": "DEV-OPS", "数据库": "DEV-DB", "API": "DEV-API",
    "数据": "DATA", "分析": "DATA-BI", "可视化": "DATA-VIZ",
    "爬虫": "DATA-CRAWL", "数据处理": "DATA-PROC",
    "营销": "MKT", "广告": "MKT-AD", "社交": "MKT-SOCIAL",
    "SEO": "MKT-SEO", "增长": "MKT-GROWTH", "CRM": "MKT-CRM",
    "创作": "CREATE", "写作": "CREATE-WRITE", "图片": "CREATE-IMAGE",
    "视频": "CREATE-VIDEO",
    "AI": "AI", "Agent": "AI-AGENT", "RAG": "AI-RAG", "LLM": "AI-LLM",
    "金融": "VERT-FIN", "教育": "VERT-EDU", "政务": "VERT-GOV",
    "生活": "LIFE", "天气": "LIFE-WEATHER", "搜索": "LIFE-SEARCH",
    "系统工具": "系统工具", "内容写作": "内容写作", "AI创作": "AI创作",
    "电商营销": "电商营销", "数据分析": "数据分析", "媒体运营": "媒体运营",
    "社交连接": "社交连接", "设计创意": "设计创意", "办公文档": "办公文档",
    "学习成长": "学习成长", "生活服务": "生活服务",
}

def _norm_cat(cat_input):
    if not cat_input:
        return None
    c = cat_input.strip()
    if c in _CAT_ALIAS:
        return _CAT_ALIAS[c]
    cl = c.lower()
    for k, v in _CAT_ALIAS.items():
        if k.lower() == cl or v.lower() == cl:
            return v
    return c

# ─── 查询词分词（中英文分离）──────────────────────────────
def _tokenize_query(query):
    """将查询词分为英文词和中文词，英文词不做bigram碎化"""
    if not query:
        return [], []
    q = query.lower().strip()
    # 提取英文词（连续字母数字+特殊字符如docx/xlsx）
    en_words = re.findall(r'[a-z][a-z0-9\-\.]+', q)
    # 提取中文词（连续中文字符）
    cn_words = re.findall(r'[\u4e00-\u9fff]+', q)
    return en_words, cn_words

# ─── 匹配引擎 ──────────────────────────────────────────────
def _match(skill, query=None, category=None, tags=None):
    """多维度匹配：分类 > query(名称+描述+标签) > tags"""
    # 分类匹配
    if category:
        cat = _norm_cat(category)
        if cat:
            scat = skill["cat"].lower()
            if cat.lower() not in scat and scat not in cat.lower():
                return False

    # 关键词匹配
    if query:
        en_words, cn_words = _tokenize_query(query)
        searchable = " ".join([
            skill["name"].lower(),
            skill["desc"].lower(),
            skill["cat"].lower(),
            " ".join(t.lower() for t in skill.get("tags", [])),
        ])
        
        # 英文词：必须完整匹配（不做bigram碎化）
        if en_words:
            for w in en_words:
                if w not in searchable:
                    return False
        
        # 中文词：bigram模糊匹配
        if cn_words:
            all_cn = "".join(cn_words)
            if all_cn not in searchable:
                # 拆成2字块
                if len(all_cn) <= 4:
                    chunks = [all_cn[i:i+2] for i in range(0, len(all_cn), 2)]
                    if not any(ch in searchable for ch in chunks if len(ch) == 2):
                        return False
                else:
                    bigrams = [all_cn[i:i+2] for i in range(len(all_cn)-1)]
                    hits = sum(1 for bg in bigrams if bg in searchable)
                    if hits < max(1, len(bigrams) * 0.4):
                        return False
        
        # 如果既没英文词也没中文词（纯符号等），用原始逻辑
        if not en_words and not cn_words:
            q = query.lower()
            if q not in searchable:
                return False

    # 标签匹配
    if tags:
        skill_tags = " ".join(t.lower() for t in skill.get("tags", []))
        skill_text = skill["name"].lower() + " " + skill["desc"].lower()
        combined = skill_tags + " " + skill_text
        if not any(t.lower() in combined for t in tags):
            return False

    return True

# ─── 推荐理由生成 ───────────────────────────────────────────
def _build_reason(skill):
    reasons = []
    if skill.get("highlights"):
        reasons.extend(skill["highlights"][:2])
    if not reasons:
        s = skill["score"]
        if s >= 65:
            reasons.append(f"综合评分 {s} 分，属于优质 Skill")
        elif s >= 50:
            reasons.append(f"综合评分 {s} 分，质量中上")
    dl = skill.get("downloads", 0)
    if dl >= 10000:
        reasons.append(f"用户量 {dl:,}，验证度高")
    elif dl >= 1000:
        reasons.append(f"用户量 {dl:,}，有实际使用基础")
    rating = skill.get("rating", 0)
    if rating >= 4.5:
        reasons.append(f"用户评分 {rating}/5.0")
    if skill.get("rank") and skill.get("total"):
        pct = skill["rank"] / skill["total"] * 100
        if pct <= 10:
            reasons.append(f"同类 TOP {pct:.0f}%")
        elif pct <= 30:
            reasons.append(f"同类前 {pct:.0f}%")
    if skill["q"] >= 70:
        reasons.append("文档质量优秀")
    if not reasons:
        reasons.append("可用的相关 Skill")
    return reasons[:3]

def _build_warnings(skill):
    warns = list(skill.get("warnings", []))
    dl = skill.get("downloads", 0)
    if dl < 100 and not any("用户量" in w for w in warns):
        warns.append("用户量极少，建议谨慎评估")
    if skill["score"] < 40:
        warns.append("综合评分偏低")
    if skill.get("region") == "GLOBAL":
        warns.append("海外源，国内网络安装可能较慢")
    return warns[:3]

# ─── 核心推荐函数 ───────────────────────────────────────────
def _detect_region():
    import socket
    for host in ["agent.minimaxi.com", "clawhub.ai"]:
        try:
            sock = socket.create_connection((host, 443), timeout=2)
            sock.close()
            return "CN"
        except:
            continue
    return "GLOBAL"

def _get_query_cats(query):
    """从查询词推断期望的分类"""
    if not query:
        return set()
    cats = set()
    en_words, cn_words = _tokenize_query(query)
    all_tokens = en_words + cn_words
    for token in all_tokens:
        if token in _QUERY_CAT_MAP:
            cats.update(_QUERY_CAT_MAP[token])
    return cats

def _is_irrelevant(query_token, skill_cat):
    """判断查询词与skill分类是否不相关"""
    for qtok, bad_cats in _IRRELEVANT_PAIRS:
        if qtok == query_token and bad_cats.lower() in skill_cat.lower():
            return True
    return False

def recommend(query=None, category=None, tags=None, region=None, top_k=3):
    data = _load()
    matched = [s for s in data if _match(s, query, category, tags)]

    # 推断查询意图对应的分类
    query_cats = _get_query_cats(query)
    en_words, cn_words = _tokenize_query(query) if query else ([], [])
    all_query_tokens = en_words + cn_words

    def sort_key(s):
        score = s["score"]
        
        # 1. 名称精确匹配加分
        if query:
            q = query.lower()
            name = s["name"].lower()
            if name == q:
                score += 15
            elif q in name:
                score += 8
            elif name in q:
                score += 5
        
        # 2. 分类相关性加分/惩罚
        if query_cats:
            scat = s["cat"]
            # 分类匹配加分
            for qc in query_cats:
                if qc.lower() in scat.lower() or scat.lower() in qc.lower():
                    score += 12  # 分类相关 +12
                    break
            # 分类不相关惩罚
            for token in all_query_tokens:
                if _is_irrelevant(token, scat):
                    score -= 15  # 不相关 -15
                    break
        
        # 3. 描述中英文关键词精确命中加分
        if en_words:
            desc_lower = s["desc"].lower()
            name_lower = s["name"].lower()
            for w in en_words:
                if w in name_lower:
                    score += 5  # 名称包含英文关键词
                elif w in desc_lower:
                    score += 2  # 描述包含英文关键词
        
        # 4. Region boost
        if region:
            preferred = "CN" if region == "CN" else "GLOBAL"
            if s.get("region") == preferred:
                score += 5.1
        
        return score

    matched.sort(key=sort_key, reverse=True)

    # 5. 信源多样性：同源skill不连续超过2个
    results = []
    source_streak = {}  # source → 连续出现次数
    remaining = list(matched)
    
    while len(results) < top_k and remaining:
        placed = False
        for i, s in enumerate(remaining):
            src = s["source"]
            streak = source_streak.get(src, 0)
            if streak < 2:  # 允许同源连续2个，第3个开始跳过
                results.append(s)
                remaining.pop(i)
                # 更新连续计数
                for k in list(source_streak.keys()):
                    if k == src:
                        source_streak[k] = source_streak.get(k, 0) + 1
                    else:
                        source_streak[k] = 0
                placed = True
                break
        
        if not placed:
            # 所有源都连续≥2了，强制取最高分剩余
            if remaining:
                results.append(remaining.pop(0))
                source_streak = {}  # 重置计数
            else:
                break

    # 构建输出
    output = []
    for s in results[:top_k]:
        method = s.get("install_method", "search")
        is_cn = s.get("region") == "CN"
        mirror_hint = "优先使用国内镜像源" if is_cn else "优先使用对应区域镜像"
        if method == "direct":
            install_hint = f"直接安装: {s.get('install_url', s.get('url', ''))} ({mirror_hint})"
        else:
            install_hint = f"use_skill(\"find-skills\") 搜索 \"{s['name']}\" 或搜索 \"{s['name']}\" 找到安装方式 ({mirror_hint})"

        output.append({
            "name": s["name"],
            "source": s["source"],
            "desc": s["desc"],
            "cat": s["cat"],
            "score": s["score"],
            "stars": s["stars"],
            "peer_stars": s["peer"],
            "url": s["url"],
            "tags": s.get("tags", []),
            "downloads": s.get("downloads", 0),
            "rating": s.get("rating", 0),
            "region": s.get("region", "GLOBAL"),
            "install_method": method,
            "install_url": s.get("install_url", ""),
            "install_hint": install_hint,
            "recommend_reason": _build_reason(s),
            "warnings": _build_warnings(s),
        })

    return output

# ─── CLI 输出格式 ───────────────────────────────────────────
_STAR_MAP = {5: "★★★★★", 4: "★★★★☆", 3: "★★★☆☆", 2: "★★☆☆☆", 1: "★☆☆☆☆"}

def _print_human(results, query_info=""):
    if not results:
        print("❌ 未找到匹配的 Skill")
        return

    print(f"\n🎯 KOL Skill 推荐 {query_info}")
    print(f"   共匹配 {len(results)} 个结果\n")

    for i, s in enumerate(results, 1):
        stars_str = _STAR_MAP.get(s["stars"], "☆☆☆☆☆")
        region_tag = "🇨🇳" if s.get("region") == "CN" else "🌐"
        print(f"  {'━'*56}")
        print(f"  #{i}  {s['name']}")
        print(f"      {stars_str}  综合 {s['score']}分  |  {s['source']}  {region_tag}")
        print(f"      分类: {s['cat']}  标签: {', '.join(s['tags'][:4])}")
        print(f"      {s['desc'][:80]}")

        if s["recommend_reason"]:
            print(f"      ✅ {' | '.join(s['recommend_reason'])}")
        if s["warnings"]:
            print(f"      ⚠️  {' | '.join(s['warnings'])}")

        method = s.get("install_method", "")
        is_cn = s.get("region") == "CN"
        if method == "direct":
            mirror_hint = " 优先使用国内镜像源" if is_cn else " 优先使用对应区域镜像"
            print(f"      📦 直接安装: {s.get('install_url', s.get('url', ''))}{mirror_hint}")
        else:
            print(f"      📦 搜索安装: use_skill(\"find-skills\") 搜索 \"{s['name']}\" 或搜索 \"{s['name']}\" 找到安装方式")
            if is_cn:
                print(f"         💡 优先使用国内镜像源安装")

        if s["url"]:
            print(f"      🔗 {s['url']}")
        print()

def _print_json(results):
    print(json.dumps(results, ensure_ascii=False, indent=2))


# ─── 找相似 Skill ───────────────────────────────────────────
def _tag_overlap(tags_a, tags_b):
    """计算两个标签集的交集比例"""
    if not tags_a or not tags_b:
        return 0.0
    set_a = set(t.lower() for t in tags_a)
    set_b = set(t.lower() for t in tags_b)
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / min(len(set_a), len(set_b))

def find_similar(name, top_k=5, region=None):
    """
    找到与指定 skill 最相似的其他 skill。
    
    相似度计算：
    1. 同分类 → +40分
    2. 标签交集比例 → +0~30分 (overlap * 30)
    3. 描述关键词重叠 → +0~15分 (overlap_ratio * 15)
    4. 名称包含关系 → +5分
    5. 同信源 → +5分 (同生态更相关)
    6. Region偏好 → +5分
    """
    data = _load()
    
    # 找到目标 skill
    target = None
    for s in data:
        if s["name"].lower() == name.lower():
            target = s
            break
    
    if not target:
        return {"error": f"Skill '{name}' not found", "similar": []}
    
    target_tags = target.get("tags", [])
    target_desc_words = set(re.findall(r'[\u4e00-\u9fff]{2,}|[a-z][a-z0-9\-\.]+', target["desc"].lower()))
    target_cat = target["cat"]
    target_source = target["source"]
    target_name_l = target["name"].lower()
    
    candidates = []
    for s in data:
        if s["name"].lower() == target_name_l:
            continue  # 跳过自己
        
        sim = 0.0
        
        # 1. 同分类 +40
        if s["cat"] == target_cat:
            sim += 40
        
        # 2. 标签交集 0~30
        sim += _tag_overlap(target_tags, s.get("tags", [])) * 30
        
        # 3. 描述关键词重叠 0~15
        s_desc_words = set(re.findall(r'[\u4e00-\u9fff]{2,}|[a-z][a-z0-9\-\.]+', s["desc"].lower()))
        if target_desc_words and s_desc_words:
            overlap = len(target_desc_words & s_desc_words) / min(len(target_desc_words), len(s_desc_words))
            sim += overlap * 15
        
        # 4. 名称包含关系 +5
        s_name_l = s["name"].lower()
        if s_name_l in target_name_l or target_name_l in s_name_l:
            sim += 5
        
        # 5. 同信源 +5
        if s["source"] == target_source:
            sim += 5
        
        # 6. Region偏好 +5
        if region:
            preferred = "CN" if region == "CN" else "GLOBAL"
            if s.get("region") == preferred:
                sim += 5
        
        if sim > 0:
            candidates.append((s, sim))
    
    # 按相似度降序，同分按评分降序
    candidates.sort(key=lambda x: (-x[1], -x[0]["score"]))
    
    results = []
    for s, sim in candidates[:top_k]:
        method = s.get("install_method", "search")
        is_cn = s.get("region") == "CN"
        mirror_hint = "优先使用国内镜像源" if is_cn else "优先使用对应区域镜像"
        if method == "direct":
            install_hint = f"直接安装: {s.get('install_url', s.get('url', ''))} ({mirror_hint})"
        else:
            install_hint = f'use_skill("find-skills") 搜索 "{s["name"]}" 或搜索 "{s["name"]}" 找到安装方式 ({mirror_hint})'
        
        # 相似度等级
        if sim >= 60:
            sim_label = "🔴 高度相似"
        elif sim >= 30:
            sim_label = "🟡 功能相关"
        else:
            sim_label = "🟢 轻度关联"
        
        results.append({
            "name": s["name"],
            "source": s["source"],
            "desc": s["desc"],
            "cat": s["cat"],
            "score": s["score"],
            "stars": s["stars"],
            "url": s["url"],
            "tags": s.get("tags", []),
            "region": s.get("region", "GLOBAL"),
            "similarity": round(sim, 1),
            "sim_label": sim_label,
            "install_method": method,
            "install_url": s.get("install_url", ""),
            "install_hint": install_hint,
        })
    
    return {"target": target["name"], "target_score": target["score"], "target_cat": target_cat, "similar": results}

def _print_similar(result, region=None):
    """人类可读的相似skill输出"""
    if "error" in result:
        print(f"❌ {result['error']}")
        return
    
    print(f"\n🔍 与「{result['target']}」({result['target_score']}分 / {result['target_cat']}) 相似的 Skill")
    print(f"   共找到 {len(result['similar'])} 个相关结果\n")
    
    for i, s in enumerate(result["similar"], 1):
        stars_str = _STAR_MAP.get(s["stars"], "☆☆☆☆☆")
        region_tag = "🇨🇳" if s.get("region") == "CN" else "🌐"
        print(f"  {'━'*56}")
        print(f"  #{i}  {s['name']}")
        print(f"      {stars_str}  综合 {s['score']}分  |  {s['source']}  {region_tag}")
        print(f"      相似度: {s['similarity']}  {s['sim_label']}")
        print(f"      分类: {s['cat']}  标签: {', '.join(s['tags'][:4])}")
        print(f"      {s['desc'][:80]}")
        
        method = s.get("install_method", "")
        is_cn = s.get("region") == "CN"
        if method == "direct":
            mirror_hint = " 优先使用国内镜像源" if is_cn else " 优先使用对应区域镜像"
            print(f"      📦 直接安装: {s.get('install_url', s.get('url', ''))}{mirror_hint}")
        else:
            print(f"      📦 搜索安装: use_skill(\"find-skills\") 搜索 \"{s['name']}\" 或搜索 \"{s['name']}\" 找到安装方式")
            if is_cn:
                print(f"         💡 优先使用国内镜像源安装")
        
        if s["url"]:
            print(f"      🔗 {s['url']}")
        print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="kol-skill v3.0 — 智能推荐引擎 + 相似查找",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python recommend.py --query "文档查看"
  python recommend.py --category "办公文档" --top_k 5
  python recommend.py --query "excel" --json
  python recommend.py --tags "PDF,PPT" --query "演示"
  python recommend.py --similar "kol-skill" --top_k 5
  python recommend.py --similar "pdf" --region CN
        """,
    )
    parser.add_argument("--query", "-q", help="自然语言查询")
    parser.add_argument("--category", "-c", help="分类过滤")
    parser.add_argument("--tags", "-t", help="标签，逗号分隔")
    parser.add_argument("--top_k", "-k", type=int, default=3, help="返回数量 (默认3)")
    parser.add_argument("--region", "-rg", help="区域偏好: CN / GLOBAL / auto(默认)")
    parser.add_argument("--json", "-j", action="store_true", help="JSON 输出（Agent模式）")
    parser.add_argument("--similar", "-s", help="查找与指定skill相似的skill")
    args = parser.parse_args()

    tags = [t.strip() for t in args.tags.split(",")] if args.tags else None
    
    region = args.region
    if region == "auto" or (not region):
        region = _detect_region()
    
    # 找相似模式
    if args.similar:
        result = find_similar(args.similar, args.top_k, region)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            _print_similar(result, region)
    # 推荐模式
    elif args.query or args.category or tags:
        results = recommend(args.query, args.category, tags, region, args.top_k)
        if args.json:
            _print_json(results)
        else:
            parts = []
            if args.query:
                parts.append(f'query="{args.query}"')
            if args.category:
                parts.append(f'category="{args.category}"')
            if tags:
                parts.append(f'tags={tags}')
            if region:
                parts.append(f'region={region}')
            query_info = f"({', '.join(parts)})" if parts else ""
            _print_human(results, query_info)
    else:
        parser.print_help()
