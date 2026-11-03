"""
xiaohongshu_common.py — 公共工具：链接解析、cookie 加载、标签去重、金句提取

依赖：requests（xhs 是 fetch_note 用的）
"""
from __future__ import annotations

import json
import os
import random
import re
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, parse_qs

import requests


# ===== Cookie 加载 =====
COOKIE_ENV = "XIAOHONGSHU_COOKIE"
COOKIE_FILE_PATHS = [
    Path.home() / ".config/xiaohongshu-link-to-md/cookie",
    Path.home() / ".xiaohongshu_cookie",
    Path("./xiaohongshu_cookie.txt"),
]


def load_cookie() -> Optional[str]:
    """按优先级加载 cookie：env > file > None（允许无 cookie 工作）"""
    cookie = os.environ.get(COOKIE_ENV, "").strip()
    if cookie:
        return cookie

    for path in COOKIE_FILE_PATHS:
        if path.exists():
            content = path.read_text(encoding="utf-8").strip()
            if content:
                return content

    return None  # 不抛错，让调用方决定是否需要 cookie


def cookie_available() -> bool:
    """检查是否配置了 cookie"""
    return load_cookie() is not None


# ===== 链接解析 =====
NOTE_ID_RE = re.compile(r"/(?:explore|discovery/item)/([a-f0-9]{24})")
SHORT_LINK_HOSTS = ("xhslink.com", "xhs.cn", "xhslink.cn")


def extract_note_id(url: str) -> Optional[str]:
    """从链接中提取 noteId（24 位 hex）"""
    # 1. 直接 regex 匹配
    m = NOTE_ID_RE.search(url)
    if m:
        return m.group(1)

    # 2. query string
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    if "noteId" in qs:
        return qs["noteId"][0]

    # 3. 短链：尝试展开
    host = parsed.hostname or ""
    if any(h in host for h in SHORT_LINK_HOSTS):
        expanded = expand_short_link(url)
        if expanded:
            return extract_note_id(expanded)

    return None


def expand_short_link(url: str, timeout: int = 8) -> Optional[str]:
    """展开 xhslink.com / xhs.cn 短链为长链"""
    try:
        resp = requests.get(
            url,
            allow_redirects=True,
            timeout=timeout,
            headers={
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
            },
        )
        return resp.url
    except Exception as e:
        print(f"[xiaohongshu_common] 短链展开失败: {url} → {e}", file=__import__("sys").stderr)
        return None


# ===== 限流 =====
def polite_sleep(base: float = 1.5):
    """礼貌延迟：避免被风控"""
    time.sleep(base + random.random() * 0.5)


# ===== 模式判断（v2.0 修复：与 fetch() 行为对齐）=====
def decide_mode(force: str = "auto") -> str:
    """
    决策：当前应该用什么抓取策略？

    重要：v2.0 行为对齐修复。
    v1.0 时期：decide_mode('auto') 有 cookie 时返回 'api'，但 fetch() 永远先试 HTML → 行为不一致。
    v2.0 行为：
        - force='html' → 强制 HTML（不需要 cookie）
        - force='api'  → 强制 API（需要 cookie）
        - force='auto' → 总是先 HTML 起步（无 cookie 也能用），有 cookie 时 HTML 拿不到数据再 fallback 到 API
                         这就是 fetch() 实际的行为！

    Returns:
        "html" 或 "api" —— 表示**第一步**尝试的模式，不是"最终走哪条"
    """
    if force in ("html", "api"):
        return force

    # auto 模式：永远先 HTML（便宜、不需要 cookie），有 cookie 时拿不到再 API
    return "html"


def fetch_strategy(mode: str) -> str:
    """人类可读的策略描述（用于日志和文档）"""
    has_cookie = cookie_available()
    if mode == "html":
        if has_cookie:
            return "L1 HTML 优先（带 cookie 时可补抓评论）"
        return "L1 HTML 模式（无 cookie，仅拿元信息 + 图片/视频直链）"
    if mode == "api":
        if has_cookie:
            return "L2 API 模式（带 cookie，数据最全 + 完整评论）"
        return "L2 API 模式（无 cookie，必失败）"
    return "未知模式"


# ===== 标签去重（v2.0 新增 - 真正的去重）=====
def normalize_tag(t: str) -> str:
    """标准化标签：去 #、去空白、转小写"""
    return t.strip().lstrip("#").strip().lower()


def dedupe_tags(
    raw_tags: list[str],
    max_main: int = 5,
    max_long_tail: int = 10,
    max_original: int = 3,
) -> dict:
    """
    真正的标签去重（v2.0 实现）

    策略：
    - 输入：原始 tags 列表（来自原笔记的 hashtag 列表，可能有重复、变体）
    - 主词：前 max_main 个（核心流量），按出现顺序
    - 长尾词：接下来 max_long_tail 个（蓝海搜索），自动去重 + 排除主词
    - 原文标签：剩下的独有标签（蹭原笔记流量），自动去重 + 排除主词/长尾

    Returns:
        {"main": [...], "long_tail": [...], "original": [...]}
    """
    # 1. 全局归一化 + 去重（保留首次出现顺序）
    seen = set()
    unique = []
    for t in raw_tags:
        norm = normalize_tag(t)
        if not norm:
            continue
        if norm in seen:
            continue
        seen.add(norm)
        unique.append(t.strip())  # 保留原始大小写

    # 2. 切分三类
    main = unique[:max_main]
    main_norm = {normalize_tag(t) for t in main}

    long_tail = []
    long_tail_norm = set()
    for t in unique[max_main:]:
        norm = normalize_tag(t)
        if norm in main_norm or norm in long_tail_norm:
            continue
        long_tail.append(t)
        long_tail_norm.add(norm)
        if len(long_tail) >= max_long_tail:
            break

    original = []
    original_norm = set()
    used_norm = main_norm | long_tail_norm
    for t in unique[max_main + len(long_tail):]:
        norm = normalize_tag(t)
        if norm in used_norm or norm in original_norm:
            continue
        original.append(t)
        original_norm.add(norm)
        used_norm.add(norm)
        if len(original) >= max_original:
            break

    return {"main": main, "long_tail": long_tail, "original": original}


# ===== 金句提取（v2.0 新增）=====
def extract_key_quotes(text: str, max_count: int = 4) -> list[str]:
    """
    从正文里自动提取金句（启发式）

    规则（按优先级）：
    1. 含感叹号 / 问号 / emoji 的短句
    2. 长度 10-60 字的句子
    3. 含 "必须" / "关键" / "重要" / "记住" / "注意" / "首先" / "其实" / "本质" 等强观点词
    4. 数字开头的列表式句子（"3 步" / "5 个" / "第一"）

    Returns:
        金句列表（最多 max_count 句），按原顺序
    """
    if not text:
        return []

    # 拆句
    sentences = re.split(r"[。!?\n]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    # 启发式打分
    KEYWORDS = [
        "必须", "关键", "重要", "记住", "注意", "首先", "其次", "最后",
        "其实", "本质", "核心", "不要", "一定", "千万", "一定不要", "切记",
        "建议", "推荐", "不要", "避免", "误区", "坑", "真相", "原因",
    ]

    scored = []
    for i, s in enumerate(sentences):
        if len(s) < 8 or len(s) > 80:
            continue  # 太短或太长
        score = 0
        if any(kw in s for kw in KEYWORDS):
            score += 3
        if re.match(r"^[\d一二三四五六七八九十]+[、.\s]", s):
            score += 2  # 列表式开头
        if "！" in text[max(0, text.find(s) - 1): text.find(s) + len(s) + 1]:
            score += 1
        if any(emoji in s for emoji in ["💡", "🔥", "⭐", "✨", "🎯", "❗", "📌", "👀"]):
            score += 2
        if any(quote in s for quote in ['"', '"', '"']):
            score += 1  # 含引号的强调
        if score > 0:
            scored.append((score, i, s))

    # 按分数降序，再按原顺序
    scored.sort(key=lambda x: (-x[0], x[1]))
    quotes = [s for _, _, s in scored[:max_count]]

    # 恢复原文顺序
    quotes_ordered = []
    seen_idx = set()
    for _, i, s in scored:
        if i in seen_idx:
            continue
        if s in quotes:
            quotes_ordered.append(s)
            seen_idx.add(i)
        if len(quotes_ordered) >= max_count:
            break

    return quotes_ordered


# ===== 测试入口 =====
if __name__ == "__main__":
    test_urls = [
        "https://www.xiaohongshu.com/explore/abc123def456abc123def456",
        "https://www.xiaohongshu.com/discovery/item/abc123def456abc123def456",
        "https://xhslink.com/o/abc",
        "https://www.xiaohongshu.com/explore/abc123def456abc123def456?xsec_token=ABcd123",
    ]
    print("=== 链接解析测试 ===")
    for u in test_urls:
        print(f"  {u}")
        print(f"    → noteId = {extract_note_id(u)}")

    print()
    print(f"=== cookie 可用性 ===")
    print(f"  cookie_available() = {cookie_available()}")
    print(f"  decide_mode('auto') = {decide_mode('auto')} → {fetch_strategy('html')}")
    print(f"  decide_mode('html') = {decide_mode('html')}")
    print(f"  decide_mode('api')  = {decide_mode('api')} → {fetch_strategy('api')}")

    print()
    print("=== 标签去重测试 ===")
    test_tags = [
        "vibecoding", "VibeCoding", "Vibe Coding", "AI产品经理", "产品经理",
        "vibecoding",  # 重复
        "AI编程", "Cursor", "v0", "求职", "面试", "AI产品经理",  # 重复
        "AIGC", "简历", "智元行方",
    ]
    result = dedupe_tags(test_tags)
    print(f"  输入 ({len(test_tags)}): {test_tags}")
    print(f"  主词: {result['main']}")
    print(f"  长尾: {result['long_tail']}")
    print(f"  原文: {result['original']}")

    print()
    print("=== 金句提取测试 ===")
    test_text = """cc-switch 也能切换Codex，没想到吧，可别被它的名字所欺骗，其实支持好久了！
新版 Codex app 和 Codex CLI 只支持 `/v1/responses`，但国产模型还没跟进。
3 步法：第一步添加供应商，第二步开启路由，第三步切换重启。
注意：必须重启 Codex CLI，否则不会生效。
AI 不会取代程序员，但会用 AI 的程序员会取代不会用 AI 的程序员。"""
    quotes = extract_key_quotes(test_text)
    print(f"  提取到 {len(quotes)} 句:")
    for i, q in enumerate(quotes, 1):
        print(f"    {i}. {q}")
