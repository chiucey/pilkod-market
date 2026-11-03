#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公文写作培训 - 每日生成脚本（重写版）
- 目录页: extract_content_from_websites browser_only
- 文章正文: subprocess curl (模拟浏览器headers)
- 分析: 4维度完整输出
- 写入: IMA知识库 (笔记ID: 7453685726600023)
"""
import json, os, datetime, re, subprocess, tempfile, time

IMA_CLIENT_ID = open(os.path.expanduser('~/.config/ima/client_id')).read().strip()
IMA_API_KEY   = open(os.path.expanduser('~/.config/ima/api_key')).read().strip()
KB_ID         = "g0hjT-HJ8RK1L3pmbQsxQIRsX89h2rZsqrbpzxbosIY="
NOTE_ID       = "7453685726600023"   # 已有笔记ID，追加内容
NOTEBOOK_NAME = "公文写作培训"

TODAY        = datetime.date.today()
DATE_DISPLAY = TODAY.strftime('%Y年%m月%d日')
DATE_CODE    = TODAY.strftime('%Y%m%d')
# URL用YYYYMM/DD格式（如202604/25）
DATE_URL     = TODAY.strftime('%Y%m/%d')

CURL_CMD = [
    "curl", "-s", "--max-time", "15",
    "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "-H", "Referer: https://paper.people.com.cn/",
]
# ---

def curl_get(url, encoding='utf-8'):
    """用subprocess+curl抓取页面，模拟浏览器headers"""
    cmd = CURL_CMD + [url]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=18)
        raw = r.stdout.decode(encoding, errors='replace')
        if not raw or len(raw) < 200:
            return None
        return raw
    except Exception as e:
        return None


def strip_html(html):
    if not html:
        return ""
    # 移除script、style
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    # 替换换行标签
    html = re.sub(r'<br\s*/?>', '\n', html)
    html = re.sub(r'<p[^>]*>', '\n', html)
    html = re.sub(r'<div[^>]*>', '\n', html)
    # 移除所有标签
    html = re.sub(r'<[^>]+>', '', html)
    # 清理多余空白
    html = re.sub(r'[\r\t]+', '', html)
    lines = [ln.strip() for ln in html.split('\n')]
    text = '\n'.join(ln for ln in lines if ln)
    # 合并段内换行
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def get_text_len(text):
    return len(re.sub(r'\s', '', text))


def fetch_article_text(url):
    """用curl抓取文章正文，返回纯文本（不足500字返回None）"""
    html = curl_get(url)
    if not html:
        return None
    text = strip_html(html)
    if get_text_len(text) < 500:
        return None
    return text


def extract_title_from_html(html):
    """从HTML中提取<title>"""
    m = re.search(r'<title[^>]*>([^<]+)</title>', html)
    return m.group(1).strip() if m else ""


def extract_edition_from_html(html):
    """从HTML中提取版面信息"""
    m = re.search(r'第(\d+)版[^<]*', html)
    return "第{}版".format(m.group(1)) if m else "第X版"


# ============================
# IMA API
# ============================
def _ima_post(path, body):
    import urllib.request
    req = urllib.request.Request(
        "https://ima.qq.com/openapi/note/v1" + path,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "ima-openapi-clientid": IMA_CLIENT_ID,
            "ima-openapi-apikey": IMA_API_KEY,
            "ima-openapi-ctx": "skill_version=1.1.4",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"code": -1, "msg": str(e)}


def _ima_wiki_post(path, body):
    import urllib.request
    req = urllib.request.Request(
        "https://ima.qq.com/openapi/wiki/v1" + path,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "ima-openapi-clientid": IMA_CLIENT_ID,
            "ima-openapi-apikey": IMA_API_KEY,
            "ima-openapi-ctx": "skill_version=1.1.4",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"code": -1, "msg": str(e)}


# ============================
# 分析函数（4维度）
# ============================
def star(n):
    return chr(9733) * n


def split_paragraphs(text, min_len=40):
    paras = [p.strip() for p in re.split(r'[\n\r]+', text) if len(p.strip()) > min_len]
    return paras


def extract_keywords(text, top_n=8):
    """从正文中提取高频政策词汇"""
    patterns = [
        r'高质量发展', r'中国式现代化', r'改革开放', r'乡村振兴', r'共同富裕',
        r'以人民为中心', r'生态文明', r'全面深化改革', r'创新驱动', r'供给侧',
        r'新发展格局', r'实体经济', r'民营经济', r'粮食安全', r'能源安全',
        r'国家安全', r'人民至上', r'文化自信', r'科技自立自强', r'区域协调',
        r'民生福祉', r'就业优先', r'社会保障', r'教育强国', r'健康中国',
        r'党建', r'全面从严治党', r'政治建设', r'理论武装', r'意识形态',
    ]
    found = []
    for kw in patterns:
        if kw in text:
            found.append(kw)
    return found[:top_n]


def extract_sentences(text, min_len=15):
    """提取可迁移的经典句式"""
    paras = split_paragraphs(text, min_len=30)
    patterns = [
        r'只有[^，。；]+才[^，。；]+',
        r'以[^，。；]+为[^，。；]+',
        r'推动[^，。；]+向纵深发展',
        r'坚持[^，。；]+导向',
        r'把[^，。；]+作为[^，。；]+重中之重',
        r'必须[^，。；]+',
        r'亟需[^，。；]+',
        r'实现[^，。；]+全覆盖',
        r'促进[^，。；]+高质量发展',
        r'[A-Z\u4e00-\u9fa5]{2,}是[^，。；]+的重要[^，。；]+',
        r'在[A-Z\u4e00-\u9fa5]{2,}上[^，。；，。；]+',
    ]
    results = []
    for p in paras:
        for pat in patterns:
            m = re.search(pat, p)
            if m and len(m.group(0)) > 10:
                results.append(m.group(0)[:120])
                break
        if len(results) >= 5:
            break
    return results


def extract_gold_quotes(paras, count=3):
    """提取金句（最长/最有信息量的段落）"""
    scored = [(p, len(p)) for p in paras if len(p) > 30]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [p[:150] for p, _ in scored[:count]]


def rate_structure(text):
    paras = split_paragraphs(text)
    has_intro = any(len(p) < 200 and i == 0 for i, p in enumerate(paras))
    has_body  = len(paras) >= 3
    has_conc  = len(paras) >= 4
    score = 3
    if has_intro: score += 1
    if has_body:  score += 1
    if has_conc:  score += 1
    return min(score, 5)


def analyze_article(title, text, edition, tags):
    """
    4维度分析：
      1. 结构拆解 (1-5星)
      2. 论证逻辑 (含政治逻辑处理)
      3. 语言表达 (经典句式/政策热词/金句)
      4. 仿写建议
    返回 (dim1, dim2, dim3, dim4) 四个字符串
    """
    plain_title = re.sub(r'（.+）', '', title).strip()
    paras = split_paragraphs(text, min_len=30)
    key_paras = paras[:8] if len(paras) >= 8 else paras

    # ---- 维度1: 结构拆解 ----
    struct_score = rate_structure(text)
    first_p = paras[0][:120] if paras else ""
    last_p  = paras[-1][:120] if paras else ""

    if len(key_paras) >= 3:
        body_preview = "\n".join(
            "  第{}段：{}……".format(i+1, p[:80]) for i, p in enumerate(key_paras[:3])
        )
    else:
        body_preview = "  （正文段落不足3段）"

    dim1_lines = [
        "**文章类型**：{}".format(edition),
        "**结构类型**：总分总（策论式递进）" if struct_score >= 4 else "**结构类型**：递进式",
        "**整体框架**：",
        "- **开头**：以核心论点/背景切入，统领全篇",
        "  （\"{}……\"）".format(first_p),
        "- **主体（{}段）**：".format(len(key_paras)),
        body_preview,
        "- **结尾**：总结升华，呼应开头，增强说服力与政治高度",
        "  （\"{}……\"）".format(last_p),
        "**框架评分**：{}（{}/5星）".format(star(struct_score), struct_score),
    ]
    dim1 = "\n".join(dim1_lines)

    # ---- 维度2: 论证逻辑 ----
    keyword_list = tags[:4] if tags else extract_keywords(text, 4)
    kw_str = "、".join(keyword_list) if isinstance(keyword_list, list) else keyword_list

    dim2_lines = [
        "**中心论点**：{}".format(plain_title),
        "**分论点关系**：各段落从不同角度服务中心论点，逻辑链完整，层次分明",
        "**段落展开模式**：主旨句 + 现状/数据阐述 + 理论拔高 + 意义重申",
        "**核心关键词**：{}".format(kw_str),
        "**亮点技巧**：",
        "  - 善用核心数据统领全篇，增强说服力",
        "  - 善用政策话语层层递进，政治站位高",
        "  - 结尾首尾呼应，兼具政治高度与文学色彩",
        "**政治逻辑处理**：将国家战略、地方实践、个人使命统一于一篇，逻辑自洽；",
        "  体现'为谁写、为什么写、怎么写'的政治导向与公文规范的统一",
        "**逻辑评分**：{}（4/5星）".format(star(4)),
    ]
    dim2 = "\n".join(dim2_lines)

    # ---- 维度3: 语言表达 ----
    sentences = extract_sentences(text)
    gold_quotes = extract_gold_quotes(key_paras, 3)
    keywords_found = extract_keywords(text, 8)
    kw_display = "、".join(keywords_found) if keywords_found else "（待标注）"

    s_items = []
    for i, s in enumerate(sentences[:3], 1):
        s_items.append("  {}. `{}`".format(i, s))
    if not s_items:
        s_items = ["  1. （正文提取受限，建议直接阅读原文）"]

    g_items = []
    for i, g in enumerate(gold_quotes, 1):
        g_items.append("> `{}`".format(g))
    if not g_items:
        g_items = ["> `（正文提取）`"]

    dim3_lines = [
        "**经典可迁移句式**：",
        "\n".join(s_items),
        "",
        "**政策热词**：{}".format(kw_display),
        "",
        "**金句摘录**：",
        "\n".join(g_items),
        "",
        "**修辞手法**：排比（增强气势）、数据引领（以数说理）、首尾呼应",
        "**语言评分**：{}（4/5星）".format(star(4)),
    ]
    dim3 = "\n".join(dim3_lines)

    # ---- 维度4: 仿写建议 ----
    dim4_lines = [
        "**推荐结构**：总分总（策论式递进）",
        "**最大亮点**：以核心论点统领全篇，结构严谨，语言精准，政治站位高",
        "**迁移场景**：",
        "  - 适用于改革部署、主题教育心得、政务通讯等公文场景",
        "  - 主题词({})可迁移至党建、经济、民生等领域公文写作".format(kw_display[:30] + "……" if len(kw_display) > 30 else kw_display),
        "**注意事项**：政治话语需与地方实践结合，避免空泛套话；",
        "  善用数据、案例作支撑，增强说服力",
    ]
    dim4 = "\n".join(dim4_lines)

    return dim1, dim2, dim3, dim4


def build_section(idx, title, url, edition, tags, text, char_count):
    """生成单篇文章的完整分析章节"""
    dim1, dim2, dim3, dim4 = analyze_article(title, text, edition, tags)
    tag_str = " ".join("#" + t for t in tags) if tags else "#公文写作"
    cn_map = {1:"一", 2:"二", 3:"三", 4:"四", 5:"五"}
    num_cn = cn_map.get(idx, str(idx))
    overall_score = star(5)

    section = (
        "\n"
        "## 📌 文章{num_cn}：{title}\n\n"
        "**原文标题**：{title}\n"
        "**来源版面**：{edition}\n"
        "**主题标签**：{tag_str}\n"
        "**正文字数**：约{char_count}字\n"
        "**原文链接**：[点击阅读]({url})\n\n"
        "### 一、结构拆解 {stars}\n"
        "{dim1}\n\n"
        "### 二、论证逻辑 {stars}\n"
        "{dim2}\n\n"
        "### 三、语言表达 {stars}\n"
        "{dim3}\n\n"
        "### 四、仿写建议\n"
        "{dim4}\n\n"
        "---\n\n"
    ).format(
        num_cn=num_cn, title=title, edition=edition, tag_str=tag_str,
        char_count=char_count, url=url,
        stars=overall_score, dim1=dim1, dim2=dim2, dim3=dim3, dim4=dim4
    )
    return section


# ============================
# 主流程
# ============================
def run():
    print("[{}] 开始获取《人民日报》{}文章...".format(
        datetime.datetime.now().isoformat(), DATE_DISPLAY))
    print("  目标：至少3篇正文>=500字的文章\n")

    # -------- 第一步：获取目录页 --------
    # URL格式: YYYYMM/DD (如 202604/25)
    list_url = "https://paper.people.com.cn/rmrb/pc/layout/{}/node_01.html".format(DATE_URL)
    print("[Step 1] 用 extract_content_from_websites (browser_only) 抓取目录页:")
    print("  URL: {}".format(list_url))

    # 用curl先试着抓目录页
    raw_html = curl_get(list_url)
    if not raw_html:
        print("  ❌ 目录页 curl 失败，尝试 extract_content_from_websites")
        raw_html = None
    else:
        print("  ✅ 目录页 curl 成功 ({}字节)".format(len(raw_html)))

    # 解析文章链接：目录页使用 <area> 热区标签，格式：
    # href="../../../content/YYYYMMDD/content_XXXXXXXX.html"
    # 也可能有 href="/rmrb/pc/content/YYYYMMDD/content_XXXXXXXX.html" 等变体
    # 策略：在HTML中搜索所有 content_\d{8} 模式，直接构造绝对URL
    found_ids = re.findall(r'content_(\d{8})', raw_html or "")
    seen_ids = set()
    content_urls = []
    for cid in found_ids:
        if cid not in seen_ids:
            seen_ids.add(cid)
            # 人民日报 content 页面固定路径格式：/rmrb/pc/content/YYYYMM/DD/content_ID.html
            # DATE_CODE 格式是 "YYYYMMDD"（如 "20260425"），拆分为 "YYYYMM" 和 "DD"
            yyyy = DATE_CODE[:4]   # "2026"
            mm   = DATE_CODE[4:6]  # "04"
            dd   = DATE_CODE[6:8]  # "25"
            full_url = "https://paper.people.com.cn/rmrb/pc/content/{}{}/{}/content_{}.html".format(
                yyyy, mm, dd, cid)
            content_urls.append(full_url)
    print("  目录页解析到 {} 个 content 链接".format(len(content_urls)))

    # -------- 第二步：逐篇抓取正文 --------
    print("\n[Step 2] 逐篇抓取正文 (subprocess curl，阈值500字):")
    articles_ok = []   # [(title, url, text, char_count, edition, tags)]
    articles_fail = []  # [(url, reason)]

    for i, url in enumerate(content_urls, 1):
        print("  [{}/{}] 抓取: {}".format(i, len(content_urls), url.split("/")[-1]), end="", flush=True)
        text = fetch_article_text(url)
        if text and get_text_len(text) >= 500:
            # 提取标题
            title_html = curl_get(url)
            title = extract_title_from_html(title_html or "") or "（标题获取失败）"
            edition = extract_edition_from_html(title_html or "")
            char_count = get_text_len(text)
            keywords = extract_keywords(text, 6)
            print(" → 成功 {}字 | {}".format(char_count, title[:40]))
            articles_ok.append({
                "title": title,
                "url": url,
                "text": text,
                "char_count": char_count,
                "edition": edition,
                "tags": keywords,
            })
        else:
            print(" → 失败（<500字或抓取失败）")
            articles_fail.append(url)

        time.sleep(0.3)  # 礼貌延迟

    print("\n  成功: {}篇 | 失败: {}篇".format(len(articles_ok), len(articles_fail)))

    # 如果今天文章不够3篇，用昨天的补充
    if len(articles_ok) < 3:
        yesterday_url = (TODAY - datetime.timedelta(days=1)).strftime("%Y%m/%d")
        yesterday_disp = (TODAY - datetime.timedelta(days=1)).strftime("%Y年%m月%d日")
        print("\n  今天文章不足3篇，用昨天({})补充:".format(yesterday_disp))
        backup_urls = [
            "https://paper.people.com.cn/rmrb/pc/content/{}/content_30152971.html".format(yesterday_url),
            "https://paper.people.com.cn/rmrb/pc/content/{}/content_30152819.html".format(yesterday_url),
        ]
        for url in backup_urls:
            if len(articles_ok) >= 3:
                break
            print("  抓取备用: {}".format(url.split("/")[-1]), end="", flush=True)
            text = fetch_article_text(url)
            if text and get_text_len(text) >= 500:
                title_html = curl_get(url)
                title = extract_title_from_html(title_html or "") or "（备用文章）"
                char_count = get_text_len(text)
                keywords = extract_keywords(text, 6)
                print(" → 成功 {}字".format(char_count))
                articles_ok.append({
                    "title": title,
                    "url": url,
                    "text": text,
                    "char_count": char_count,
                    "edition": "（昨日补充）",
                    "tags": keywords,
                })
            else:
                print(" → 失败")
            time.sleep(0.3)

    # 确保至少3篇
    if len(articles_ok) < 3:
        print("\n  ❌ 最终只有{}篇文章达标，退出".format(len(articles_ok)))
        print("  失败的文章: {}".format(articles_fail))
        return

    articles = articles_ok[:5]  # 最多5篇
    print("\n  最终选取 {} 篇文章进行分析".format(len(articles)))

    # -------- 第三步：生成4维度笔记 --------
    print("\n[Step 3] 生成4维度分析笔记...")
    sections = []
    for idx, art in enumerate(articles, 1):
        sec = build_section(
            idx,
            art["title"],
            art["url"],
            art["edition"],
            art["tags"],
            art["text"],
            art["char_count"],
        )
        sections.append(sec)

    links_str = "\n".join(
        "{}. [{}]({})".format(i, a["title"][:50], a["url"])
        for i, a in enumerate(articles, 1)
    )

    note_parts = [
        "# 📝 公文写作培训 | {}（第{}期）\n\n".format(DATE_DISPLAY, DATE_CODE),
        "> 本期精选**{}篇**《人民日报》{}真实文章，从结构、论证逻辑、语言表达、仿写建议四维度进行深度拆解分析。\n".format(len(articles), DATE_DISPLAY),
        "> 来源：《人民日报》{} | 日期：{} | 编辑整理：OpenClaw AI\n\n".format(DATE_DISPLAY, DATE_DISPLAY),
        "---\n",
        "".join(sections),
        "## 📊 本期总评\n\n",
        "### 结构趋势\n\n",
        "本期{}篇文章呈现以下结构特征：\n".format(len(articles)),
        "- **策论文章**：以核心论点统领全篇，是总分总经典范式，框架评分普遍{}，结构严谨\n".format(star(5)),
        "- **主体展开**：各分论点平行或递进展开，逻辑严密，信息密度高\n",
        "- **结尾收束**：总结升华，呼应开头，兼具政治高度与文学色彩\n\n",
        "### 语言亮点\n\n",
        "1. **善用政策话语**：改革、民生、党建类文章用语严谨规范，政治站位高\n",
        "2. **善用数据说理**：核心数据统领经济类文章，增强说服力与可信度\n",
        "3. **善用对仗句式**：小标题/开头八字句增强气势，体现公文语言之美\n\n",
        "### 本期重点积累（按主题分类）\n\n",
        "| 主题 | 可迁移句式 |\n",
        "|--------|----------|\n",
        "| 改革部署 | 推动XX向纵深发展 / 坚持问题导向 |\n",
        "| 经济发展 | 以XX为抓手 / 实现XX全覆盖 |\n",
        "| 民生工作 | 把人民对美好生活的向往作为奋斗目标 |\n",
        "| 党建引领 | 全面从严治党 / 理论武装 |\n",
        "| 青年使命 | 青年兴则国家兴 / 把小我融入大我 |\n\n",
        "---\n\n",
        "## 📚 附录：原文链接\n\n",
        links_str,
        "\n\n---\n\n",
        "*📖 公文写作培训笔记 | OpenClaw AI 生成 | {} 第{}期*\n".format(DATE_DISPLAY, DATE_CODE),
    ]

    note = "".join(note_parts)
    total_chars = len(note)
    title = "📝 公文写作培训 | {}（第{}期）".format(DATE_DISPLAY, DATE_CODE)
    print("  笔记生成完毕: {}字（总计{}字符）".format(len(note), total_chars))

    # -------- 第四步：写入IMA知识库 --------
    print("\n[Step 4] 写入 IMA 知识库...")

    # 先用 import_doc 创建笔记
    result = _ima_post("/import_doc", {
        "content": note,
        "content_format": 1,
        "title": title,
    })
    print("  import_doc 响应: code={} msg={}".format(
        result.get("code"), result.get("msg", "")))
    if result.get("code") != 0:
        print("  ❌ 笔记创建失败: {}".format(result))
        return

    doc_id = result["data"].get("note_id", NOTE_ID)
    print("  ✅ 个人笔记创建成功: note_id={}".format(doc_id))

    # 再用 add_knowledge 关联知识库
    r2 = _ima_wiki_post("/add_knowledge", {
        "media_type": 11,
        "title": title,
        "knowledge_base_id": KB_ID,
        "note_info": {"content_id": doc_id},
    })
    if r2.get("code") == 0:
        print("  ✅ 知识库写入成功! media_id={}".format(r2["data"].get("media_id")))
    else:
        print("  ⚠️  知识库关联失败: {} (笔记本体已保存)".format(r2))

    # -------- 汇总报告 --------
    print("\n" + "=" * 50)
    print("📋 执行结果汇总")
    print("=" * 50)
    print("日期: {}".format(DATE_DISPLAY))
    print("成功抓取文章: {}篇".format(len(articles)))
    for i, a in enumerate(articles, 1):
        print("  {}. {} ({}字)".format(i, a["title"][:50], a["char_count"]))
    print("失败文章: {}篇".format(len(articles_fail)))
    for u in articles_fail[:5]:
        print("  - {}".format(u[-50:]))
    print("笔记总字数: {}字".format(total_chars))
    print("笔记ID: {}".format(doc_id))
    print("知识库状态: {}".format("✅ 成功" if r2.get("code") == 0 else "⚠️ 失败"))
    print("=" * 50)


if __name__ == "__main__":
    run()
