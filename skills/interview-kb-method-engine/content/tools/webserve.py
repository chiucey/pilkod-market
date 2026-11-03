#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""webserve.py — 面经库的本地图形界面（H5）。

用法:
    python main.py web              # 起服务并自动打开浏览器
    python main.py web --port 8765  # 换端口
    python main.py web --no-open    # 不自动开浏览器
    python main.py web --export out.html   # 只导出一个静态单文件（不给改）

═══ 为什么要做成"服务"而不是单个 HTML ═══
使用者提的问题：**所有信息都堆在 AI 对话的上下文里，想定位一条要翻半天。**
"看"和"查"本该用界面，"改"才用对话。所以：

  · 界面负责 **看**：全部卡片全文搜索、筛选、报告可视化、趋势、同类题对比
  · 对话负责 **改**：建档、回填真值（第一步先只读，第二步再加写入）

做成服务（而不是静态 HTML）的原因：数据要**实时**读 `cards/`，
改完刷新就能看到，不用每次重新生成文件。

═══ 依赖 ═══
**零额外依赖** —— 只用 Python 自带 http.server / json / socketserver。
不装 flask、不联网、不上传。所有数据留在本机。
"""
import os
import re
import sys
import json
import glob
import html
import argparse
import threading
from datetime import date, datetime

try:
    import yaml
except Exception:
    yaml = None

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(BASE, ".."))
CARDS = os.path.join(ROOT, "cards")

# 报告文件 → 展示名
REPORTS = [
    ("求职总报.md", "求职总报", "章节最全，日常看这个"),
    ("求职定位报告_轮次正编.md", "轮次 / 正编外包", "按用工性质拆开的通过率"),
    ("求职动态洞察_pulse.md", "动态洞察", "趋势 + 跨界告警"),
    ("求职定位_v2.md", "浓缩决策", "该投/慎投/别投 + 下一步"),
    ("求职诊断报告.md", "自我诊断", "4 问：赛道/挂因/标签/该投什么"),
    ("求职定位报告.md", "求职定位", "匹配 vs 跨界"),
    ("痛点优势报告.md", "痛点优势", "失分点与优势项"),
    ("跨场分析.md", "跨场分析", "全量统计"),
]

# ── 对话（方案 A：网页记录 → AI 读）──────────────────────────────
#
# ═══ 为什么网页里的"对话框"不接 AI ═══
# 网页是离线的、没有模型；AI 在 DSH 会话里。要让网页"能对话"，
# 最省事又不必引入 API Key 的做法是：
#     网页把消息**存成本地文件** → 使用者回 DSH 说一句"看聊天" → AI 读并回复，
#     回复也写回同一个文件 → 网页刷新就看到。
#
# 为什么不做"网页直连 AI API"：要买 Key，且 Key 放前端有泄露风险，
# 更要重写整套"读卡/建档"的工具调用 —— 等于把 agent 重做一遍。
#
# 代价（如实说明）：**省不掉"回 DSH 说一句"这一步**。
# 因为我（AI）只在你发消息时才会动，无法主动轮询网页。
CHAT_DIR = os.path.join(ROOT, "chat")
CHAT_FILE = os.path.join(CHAT_DIR, "对话.md")

_CHAT_HEADER = """# 与 AI 的对话记录

> 这个文件由面经台（`python main.py web`）的「对话」页写入。
> 你在网页里发的消息会追加到这里；
> **回到 DSH 会话说一句「看聊天」，AI 就会读它并回复。**
>
> 格式：`## [时间] 我` / `## [时间] AI`，按时间顺序往下排。

---
"""


def _chat_ensure():
    if not os.path.isdir(CHAT_DIR):
        os.makedirs(CHAT_DIR, exist_ok=True)
    if not os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "w", encoding="utf-8") as f:
            f.write(_CHAT_HEADER)


def read_chat():
    """读回对话记录（原文 + 结构化条目）。"""
    _chat_ensure()
    with open(CHAT_FILE, encoding="utf-8") as f:
        txt = f.read()
    msgs = []
    cur = None
    for ln in txt.splitlines():
        m = re.match(r"^##\s*\[([^\]]+)\]\s*(我|AI)\s*$", ln)
        if m:
            if cur:
                msgs.append(cur)
            cur = {"time": m.group(1), "who": m.group(2), "text": ""}
        elif cur is not None:
            cur["text"] += ln + "\n"
    if cur:
        msgs.append(cur)
    for m in msgs:
        m["text"] = m["text"].strip()
    return txt, msgs


def append_chat(text, who="我"):
    """追加一条消息。只允许这两个角色，且长度受限。"""
    if who not in ("我", "AI"):
        who = "我"
    t = str(text or "").strip()
    if not t:
        return False, "消息为空"
    if len(t) > 20000:
        return False, "消息太长（上限 2 万字）"
    _chat_ensure()
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    with _get_lock():
        with open(CHAT_FILE, "a", encoding="utf-8") as f:
            f.write("\n## [%s] %s\n\n%s\n" % (stamp, who, t))
    return True, "已记入 chat/对话.md"


def clear_chat():
    """清空对话（保留表头）。"""
    _chat_ensure()
    with _get_lock():
        with open(CHAT_FILE, "w", encoding="utf-8") as f:
            f.write(_CHAT_HEADER)
    return True, "已清空"


# ── 复用引擎口径（绝不自己再写一套判定）──────────────────────────
def _tax():
    try:
        sys.path.insert(0, BASE)
        from industry_taxonomy import (track_of_card, nature_of, offer_flag)
        return track_of_card, nature_of, offer_flag
    except Exception:
        return None, None, None


TRACK_OF, NATURE_OF, OFFER_FLAG = _tax()


def _outcome(c):
    s = str((c.get("result") or {}).get("outcome") or "").strip().lower()
    if "pass" in s:
        return "pass"
    if "fail" in s or "挂" in s:
        return "fail"
    if "no_offer" in s:
        return "no_offer"
    return "unknown"


def _track(c):
    if TRACK_OF:
        try:
            return TRACK_OF(c, fallback="其他")
        except Exception:
            pass
    return "其他"


def _nature(c):
    if NATURE_OF:
        try:
            return NATURE_OF(c)
        except Exception:
            pass
    return str((c.get("interview") or {}).get("nature") or "未标")


def _offer(c):
    if OFFER_FLAG:
        try:
            return OFFER_FLAG(c)
        except Exception:
            pass
    return ""


def load_cards():
    """读全部正式卡，归一成前端要的形状。"""
    out = []
    for p in sorted(glob.glob(os.path.join(CARDS, "I*.yaml"))):
        try:
            with open(p, encoding="utf-8") as f:
                d = yaml.safe_load(f)
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        iv = d.get("interview") or {}
        res = d.get("result") or {}
        refl = d.get("reflection") or {}
        qs = []
        for q in (d.get("questions") or []):
            if not isinstance(q, dict):
                continue
            qs.append({
                "q": str(q.get("question") or ""),
                "theme": str(q.get("theme") or ""),
                "a": str(q.get("how_answered") or ""),
                "score": q.get("score"),
            })
        out.append({
            "id": str(d.get("id") or os.path.basename(p).split("_")[0]),
            "file": os.path.basename(p),
            "company": str(iv.get("company") or ""),
            "position": str(iv.get("position") or ""),
            "round": str(iv.get("round") or ""),
            "date": str(iv.get("date") or ""),
            "level": str(iv.get("level") or ""),
            "nature": _nature(d),
            "track": _track(d),
            "outcome": _outcome(d),
            "offer": _offer(d),
            "reason": str(res.get("reason") or ""),
            "why_ended": str(res.get("why_ended") or ""),
            "signal": str(res.get("signal") or ""),
            "strength": str(refl.get("strength") or ""),
            "weakness": str(refl.get("weakness") or ""),
            "improvement": str(refl.get("improvement") or ""),
            "skills": [str(s) for s in (d.get("skills") or [])],
            "context": str(d.get("context") or ""),
            "questions": qs,
        })
    return out


def compute_todos(cards):
    """缺口看板：还缺哪些真值 / 哪些卡有问题。判据与 remind 一致。"""
    todos = []
    for c in cards:
        r = {"id": c["id"]}
        if c["outcome"] == "pass" and not c["offer"]:
            todos.append(dict(r, kind="缺 offer", why="过了但不知道最终拿没拿到",
                              cmd='record fix %s --offer got|no|ongoing' % c["id"],
                              company=c["company"], position=c["position"]))
        elif c["outcome"] == "fail" and not c["why_ended"]:
            todos.append(dict(r, kind="缺 why_ended", why="挂了但没写为什么",
                              cmd='record fix %s --why-ended "…"' % c["id"],
                              company=c["company"], position=c["position"]))
        elif c["outcome"] == "unknown":
            todos.append(dict(r, kind="缺 outcome", why="还没回填这轮过没过",
                              cmd='record fix %s --outcome pass|fail' % c["id"],
                              company=c["company"], position=c["position"]))
        if not c["questions"]:
            todos.append(dict(r, kind="无题目", why="这张卡没记任何面试题",
                              cmd='record ask --file %s --q "题目"' % c["id"],
                              company=c["company"], position=c["position"]))
    return todos


def compute_tracks(cards):
    """赛道维度的通过率（正编口径）。"""
    agg = {}
    for c in cards:
        if c["nature"] != "正编" or c["outcome"] not in ("pass", "fail"):
            continue
        a = agg.setdefault(c["track"], [0, 0])
        a[0 if c["outcome"] == "pass" else 1] += 1
    rows = []
    for k, (p, f) in agg.items():
        n = p + f
        rows.append({"track": k, "pass": p, "fail": f, "n": n,
                     "rate": round(p / n * 100, 1) if n else 0})
    rows.sort(key=lambda r: (-r["n"], -r["rate"]))
    return rows


def list_reports():
    """可看的报告（只列真实存在的）。"""
    out = []
    for fn, name, desc in REPORTS:
        p = os.path.join(ROOT, fn)
        if os.path.exists(p):
            mt = datetime.fromtimestamp(os.path.getmtime(p)).strftime("%m-%d %H:%M")
            out.append({"file": fn, "name": name, "desc": desc, "mtime": mt})
    return out


def read_report(fn):
    """安全地读一个报告文件（防目录穿越）。"""
    if fn not in [r[0] for r in REPORTS]:
        return None
    p = os.path.join(ROOT, fn)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return f.read()


# ── 写卡（危险操作，四道防护）──────────────────────────────────
#
# ═══ 为什么写接口必须小心 ═══
# 本地服务虽然只监听 127.0.0.1，但**你浏览器里打开的任何网页**
# 都能向它发请求 —— 一个恶意页面可以悄悄 POST 到 /api/edit 去改你的卡。
# 所以不能因为"是本地"就不设防。
#
# 四道防护：
#   ① 只接受**卡号**（如 I007），路径由后端自己 find_card 定位
#      → 杜绝目录穿越（不接受任何路径片段）
#   ② **字段白名单**：只允许改 outcome / why_ended / offer / reason / track
#      → 杜绝"把整张卡改烂"
#   ③ **CSRF 防护**：校验 Origin/Referer 必须是本机来源，
#      且要求自定义头 X-Mianjing-Edit —— 跨站表单/简单请求带不了自定义头
#   ④ **写锁**：多线程服务下把写操作串行化，避免并发互相覆盖
#
# 备份与"未写入"告警复用 build_card（与命令行 `record fix` **同一条路径**）——
# 网页改和命令行改享受完全相同的保护，不会出现两套逻辑。
_WRITE_LOCK = None
_WRITABLE = {"outcome", "why_ended", "offer", "reason"}

# 前端下拉里可选的取值（只是建议，后端不强校验语义）
OUTCOMES = ["pass", "fail", "no_offer", "unknown"]
OFFERS = ["got", "no", "ongoing", ""]


def _get_lock():
    global _WRITE_LOCK
    if _WRITE_LOCK is None:
        import threading
        _WRITE_LOCK = threading.Lock()
    return _WRITE_LOCK


def _is_local_origin(handler):
    """只信本机来源：Origin/Referer 为空（curl 等）或指向 127.0.0.1/localhost。

    ⚠️ 浏览器发跨站请求时会带上攻击者页面的 Origin，
       所以这里必须**拒绝**任何非本机来源。
       注意：不为空但非本机 → 拒绝；为空 → 允许（本页 fetch 同源会带 Origin，
       命令行 curl 不带，两种都要能用）。
    """
    for h in ("Origin", "Referer"):
        v = handler.headers.get(h)
        if not v:
            continue
        if not (v.startswith("http://127.0.0.1") or v.startswith("http://localhost")
                or v.startswith("http://[::1]")):
            return False
    return True


def apply_edit(card_id, fields):
    """改一张卡的字段。返回 (ok, 消息, 变更明细)。

    所有写入都走这里 —— 后端唯一入口，方便审计。
    """
    import build_card

    # ① 卡号格式校验（只允许 I###/P###，杜绝任何路径成分）
    cid = str(card_id or "").strip()
    if not re.fullmatch(r"[IPip]\d{1,4}", cid):
        return False, "卡号格式不对（应形如 I007 / P1）", []

    # ② 字段白名单
    clean = {}
    for k, v in (fields or {}).items():
        if k not in _WRITABLE:
            return False, "不允许改字段：%s（只允许 %s）" % (k, "/".join(sorted(_WRITABLE))), []
        clean[k] = "" if v is None else str(v)

    # ③ 至少要改一样
    nonempty = {k: v for k, v in clean.items() if v != ""}
    if not nonempty:
        return False, "没有要改的内容", []

    path = build_card.find_card(cid)
    if path is None:
        return False, "未找到卡片 %s" % cid, []

    with _get_lock():                       # ④ 串行化
        bak = build_card.backup_before_write(path, why="网页改卡")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        changes, missing = [], []
        for k, v in nonempty.items():
            old = build_card._get_yaml_field(content, k)
            content, ok = build_card._set_yaml_field(content, k, v)
            if ok:
                if old != v:
                    changes.append({"field": k, "old": old, "new": v})
            else:
                # 字段不存在 → 在 result 块补一行（与 record fix 同逻辑）
                added = False
                if k in ("outcome", "why_ended", "offer", "reason"):
                    m = re.search(r"^(result:)[ \t]*$", content, re.M)
                    if m:
                        rest = content[m.end():]
                        nxt = re.search(r"^\S", rest, re.M)
                        at = m.end() + (nxt.start() if nxt else len(rest))
                        content = content[:at] + "  %s: %s\n" % (k, v) + content[at:]
                        added = True
                        changes.append({"field": k, "old": "(无此字段)", "new": v})
                if not added:
                    missing.append(k)
        if missing:
            return False, "这些字段写不进去：%s" % ", ".join(missing), changes
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    return True, "已更新 %s" % cid, (changes + ([{"field": "_backup",
                                                "old": "", "new": os.path.basename(bak)}] if bak else []))


# ── HTTP 服务 ──────────────────────────────────────────────────
def make_handler():
    from http.server import BaseHTTPRequestHandler
    from urllib.parse import urlparse, parse_qs

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass                      # 静音，别刷屏

        def _send(self, code, body, ctype="application/json; charset=utf-8"):
            if isinstance(body, str):
                body = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, obj):
            self._send(200, json.dumps(obj, ensure_ascii=False))

        def do_GET(self):
            u = urlparse(self.path)
            q = parse_qs(u.query)
            path = u.path

            if path in ("/", "/index.html"):
                return self._send(200, PAGE, "text/html; charset=utf-8")

            if path == "/api/meta":
                # 前端要用到的可选项（避免前后端各写一份枚举）
                return self._json({"outcomes": OUTCOMES, "offers": OFFERS,
                                   "writable": sorted(_WRITABLE)})

            if path == "/api/chat":
                txt, msgs = read_chat()
                return self._json({"messages": msgs, "file": "chat/对话.md"})

            if path == "/api/cards":
                return self._json(load_cards())

            if path == "/api/overview":
                cards = load_cards()
                p = sum(1 for c in cards if c["outcome"] == "pass")
                f = sum(1 for c in cards if c["outcome"] == "fail")
                z = sum(1 for c in cards if c["nature"] == "正编")
                return self._json({
                    "n": len(cards), "pass": p, "fail": f, "zheng": z,
                    "questions": sum(len(c["questions"]) for c in cards),
                    "tracks": compute_tracks(cards),
                        "todos": compute_todos(cards),
                })

            if path == "/api/reports":
                return self._json(list_reports())

            if path == "/api/report":
                fn = (q.get("f") or [""])[0]
                txt = read_report(fn)
                if txt is None:
                    return self._send(404, json.dumps({"error": "not found"}),
                                      "application/json; charset=utf-8")
                return self._json({"file": fn, "text": txt})

            return self._send(404, json.dumps({"error": "not found"}),
                              "application/json; charset=utf-8")

        def do_POST(self):
            """写接口。四道防护见 apply_edit / _is_local_origin 的注释。"""
            u = urlparse(self.path)
            if u.path not in ("/api/edit", "/api/chat"):
                return self._send(404, json.dumps({"error": "not found"}),
                                  "application/json; charset=utf-8")

            # ③ CSRF：必须是本机来源 + 带自定义头
            if not _is_local_origin(self):
                return self._send(403, json.dumps(
                    {"ok": False, "msg": "拒绝：请求来源不是本机页面"}, ensure_ascii=False))
            if self.headers.get("X-Mianjing-Edit") != "1":
                return self._send(403, json.dumps(
                    {"ok": False, "msg": "拒绝：缺少 X-Mianjing-Edit 头"}, ensure_ascii=False))

            try:
                n = int(self.headers.get("Content-Length") or 0)
                if n <= 0 or n > 100000:
                    raise ValueError("长度异常")
                body = json.loads(self.rfile.read(n).decode("utf-8"))
            except Exception as e:
                return self._send(400, json.dumps(
                    {"ok": False, "msg": "请求体不是合法 JSON：%s" % e}, ensure_ascii=False))

            if u.path == "/api/chat":
                act = body.get("action") or "send"
                if act == "clear":
                    ok, msg = clear_chat()
                else:
                    ok, msg = append_chat(body.get("text"), body.get("who") or "我")
                _, msgs = read_chat()
                return self._json({"ok": ok, "msg": msg, "messages": msgs})

            ok, msg, changes = apply_edit(body.get("id"), body.get("fields") or {})
            return self._json({"ok": ok, "msg": msg, "changes": changes})

    return H


PAGE = r"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>面经台</title>
<style>
/* ══════════════════════════════════════════════════════════════
   每页一套主题（使用者要求："每个 tab 按不同设计方式做，看效果再定"）

   分工（按页面特性挑最合适的风格）：
     对话 chat    → 极简工具风：留白大、克制、几乎无阴影
     卡片 board   → 现代 SaaS：白卡浮起 + 柔和阴影 + 主色（层次最强）
     报告 report  → 文档阅读风：接近纸质，字号大、行距宽
     待办 todo    → 看板风：紧凑列表 + 左侧色条
     趋势 trend   → 仪表盘：深色数据面板、高对比数字
     同类题 cross → 杂志风：大标题、强调引用块

   ⚠️ 旧版被使用者指出"太丑"，诊断是：
      box-shadow 0 次（无层次）、transition 0 次（无动效）、
      字号 11 档（碎）、强调色是纯黑（等于没有强调）。
      这一版针对这四条重做。
   ══════════════════════════════════════════════════════════════ */

:root{
  /* 字阶收敛到 6 档 */
  --t-xs:11.5px; --t-sm:12.5px; --t-md:13.5px; --t-lg:15px;
  --t-xl:18px;   --t-2xl:23px;
  --r-sm:8px; --r-md:11px; --r-lg:15px;
  --sp:14px;
  /* 主色（靛蓝）：用于按钮、选中态、强调 —— 旧版 accent 是纯黑，等于没强调 */
  --brand:#4f46e5; --brand-ink:#fff; --brand-soft:rgba(79,70,229,.09);
  --pass:#15803d; --fail:#b91c1c; --warn:#a16207;
  --sh-1:0 1px 2px rgba(16,24,40,.05);
  --sh-2:0 1px 3px rgba(16,24,40,.07), 0 4px 12px rgba(16,24,40,.05);
  --sh-3:0 4px 10px rgba(16,24,40,.07), 0 14px 32px rgba(16,24,40,.07);
  --ease:.16s cubic-bezier(.4,0,.2,1);
}
/* 默认（未分主题时兜底）：现代 SaaS */
:root{
  --bg:#f7f8fa; --card:#fff; --ink:#111827; --dim:#6b7280;
  --line:#e8eaee; --line2:#f1f2f5; --accent:var(--brand);
}
@media(prefers-color-scheme:dark){
  :root{ --bg:#0f1115; --card:#181b21; --ink:#e8eaed; --dim:#9aa0a6;
         --line:#262a32; --line2:#1f232a;
         --brand-soft:rgba(129,120,255,.14); }
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);
 font:var(--t-lg)/1.62 -apple-system,BlinkMacSystemFont,"Segoe UI",
 "PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
 -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}

/* ── 顶栏（全主题共用，但随主题变色）── */
header{position:sticky;top:0;z-index:20;background:var(--hdr-bg,var(--bg));
 border-bottom:1px solid var(--line);padding:13px 20px 0;
 backdrop-filter:saturate(180%) blur(12px)}
.top{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}
h1{font-size:var(--t-xl);margin:0;font-weight:680;letter-spacing:-.01em}
.sub{color:var(--dim);font-size:var(--t-sm)}
.tabs{display:flex;gap:3px;margin-top:11px;flex-wrap:wrap}
.tab{padding:8px 15px;border:0;background:none;color:var(--dim);
 font-size:var(--t-md);cursor:pointer;border-bottom:2px solid transparent;
 font-family:inherit;transition:color var(--ease),border-color var(--ease);
 border-radius:var(--r-sm) var(--r-sm) 0 0;font-weight:500}
.tab:hover{color:var(--ink);background:var(--brand-soft)}
.tab.on{color:var(--brand);border-bottom-color:var(--brand);font-weight:650}
main{max-width:1220px;margin:0 auto;padding:20px}
footer{max-width:1220px;margin:0 auto;padding:6px 20px 40px;
 color:var(--dim);font-size:var(--t-xs)}
.hide{display:none}
.load{color:var(--dim);text-align:center;padding:34px;font-size:var(--t-md)}
.empty{color:var(--dim);text-align:center;padding:40px 16px;font-size:var(--t-md);
 line-height:1.9}
mark{background:#fde68a;color:inherit;border-radius:3px;padding:0 2px}
@media(prefers-color-scheme:dark){mark{background:#4d3f11;color:#fde68a}}

/* 通用控件 */
input,select,textarea{font-family:inherit;font-size:var(--t-md);color:var(--ink);
 background:var(--card);border:1px solid var(--line);border-radius:var(--r-sm);
 padding:8px 11px;transition:border-color var(--ease),box-shadow var(--ease)}
input:focus,select:focus,textarea:focus{outline:0;border-color:var(--brand);
 box-shadow:0 0 0 3px var(--brand-soft)}
button.go{font-family:inherit;font-size:var(--t-md);padding:8px 18px;border-radius:var(--r-sm);
 border:1px solid var(--brand);background:var(--brand);color:var(--brand-ink);
 cursor:pointer;font-weight:600;transition:filter var(--ease),transform var(--ease)}
button.go:hover{filter:brightness(1.08)}
button.go:active{transform:translateY(1px)}
button.gh{background:var(--card);color:var(--ink);border-color:var(--line);font-weight:500}
button.gh:hover{background:var(--line2)}
button.sm{font-size:var(--t-sm);padding:6px 14px}
.pill{font-size:var(--t-xs);padding:2px 8px;border-radius:99px;font-weight:650;
 white-space:nowrap;letter-spacing:.01em}
.p-pass{color:#fff;background:var(--pass)}
.p-fail{color:#fff;background:var(--fail)}
.p-unknown{color:var(--dim);background:var(--line2)}
.p-g{color:var(--dim);border:1px solid var(--line);background:transparent}
.p-t{color:var(--brand);background:var(--brand-soft)}
.meta{color:var(--dim);font-size:var(--t-sm)}
.cmd{font-size:var(--t-xs);background:var(--line2);border:1px solid var(--line);
 border-radius:6px;padding:3px 8px;
 font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}

/* ═══ 卡片页：现代 SaaS（白卡浮起 + 柔和阴影）═══ */
.stats{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:18px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:var(--r-md);
 padding:13px 17px;min-width:104px;box-shadow:var(--sh-1);
 transition:box-shadow var(--ease),transform var(--ease)}
.stat:hover{box-shadow:var(--sh-2);transform:translateY(-1px)}
.stat b{display:block;font-size:var(--t-2xl);font-weight:680;line-height:1.25;
 letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.stat span{color:var(--dim);font-size:var(--t-xs)}
.filters{display:flex;gap:9px;flex-wrap:wrap;margin-bottom:15px}
.filters input[type=search]{flex:1;min-width:190px}
.grid{display:grid;gap:11px}
.c{background:var(--card);border:1px solid var(--line);border-radius:var(--r-md);
 padding:14px 16px;cursor:pointer;box-shadow:var(--sh-1);
 transition:box-shadow var(--ease),transform var(--ease),border-color var(--ease)}
.c:hover{box-shadow:var(--sh-3);transform:translateY(-2px);border-color:var(--brand)}
.c h3{margin:0 0 5px;font-size:var(--t-md);font-weight:640;
 display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.c .meta{margin-bottom:5px}
.c .why{font-size:var(--t-sm);color:var(--dim);border-left:2px solid var(--line);
 padding-left:10px;margin-top:7px}
.detail{background:var(--card);border:1px solid var(--line);
 border-radius:var(--r-lg);padding:22px;box-shadow:var(--sh-2)}
.detail h2{letter-spacing:-.01em}
.q{border-top:1px solid var(--line2);padding:13px 0}
.q:first-of-type{border-top:0}
.qq{font-weight:640;font-size:var(--t-md);line-height:1.6}
.aa{color:var(--dim);font-size:var(--t-md);margin-top:5px;white-space:pre-wrap;
 line-height:1.75}
.tag{font-size:var(--t-xs);color:var(--brand);background:var(--brand-soft);
 margin-left:7px;font-weight:500;padding:1px 7px;border-radius:99px}
.back{background:none;border:0;color:var(--dim);cursor:pointer;font-family:inherit;
 font-size:var(--t-sm);padding:0;margin-bottom:11px;transition:color var(--ease)}
.back:hover{color:var(--brand)}

/* ═══ 统一风格：白卡浮起 + 柔和阴影 + 悬浮轻微抬起 ═══
   （使用者选定这一版；原来六页各一套风格的做法已废弃）

   分层原则（避免"所有盒子一样浮"导致又糊成一片）：
     · 列表项 / 统计卡     → 阴影 1 级；hover 升 3 级 + 上移 2px  ← 就是"轻微抬起"
     · 主容器（详情/报告/对话面板） → 阴影 2 级；**不抬**（容器抬起反而怪）
     · 按钮               → 不抬，只改色
*/
.stat,.c,.todo{
  box-shadow:var(--sh-1);
  transition:box-shadow var(--ease),transform var(--ease),border-color var(--ease);
}
.stat:hover,.c:hover,.todo:hover{
  box-shadow:var(--sh-3);transform:translateY(-2px);border-color:var(--brand);
}
.detail,.md,.pane-chat,.pane-side,table{box-shadow:var(--sh-2)}
/* 不可点的容器被 hover 时不要有反馈（避免误导"这个能点"） */
.detail:hover,.md:hover{box-shadow:var(--sh-2)}

/* 报告页：纸张感弱化，回归卡片语言（但正文仍留大字号，读起来舒服） */
.md{background:var(--card);border:1px solid var(--line);
 border-radius:var(--r-lg);padding:30px 34px;max-width:860px;margin:0 auto;
 font-size:15.5px;line-height:1.9}
.md h1{font-size:23px;margin:0 0 16px;font-weight:680;letter-spacing:-.01em}
.md h2{font-size:17.5px;margin:28px 0 10px;padding-top:14px;
 border-top:1px solid var(--line2);font-weight:660}
.md h3{font-size:15.5px;margin:19px 0 7px;font-weight:640}
.md p{margin:10px 0}
.md table{margin:14px 0;font-size:13.5px;box-shadow:none}
.md blockquote{border-left:3px solid var(--brand);margin:14px 0;
 padding:3px 0 3px 15px;color:var(--dim)}
.md code{background:var(--line2);padding:2px 6px;border-radius:5px;font-size:12.5px}
.md ul{margin:10px 0;padding-left:23px}
.md li{margin:4px 0}

/* 对话页：面板给 2 级阴影，聊天气泡给 1 级 */
.pane-chat,.pane-side{background:var(--card);border:1px solid var(--line);
 border-radius:var(--r-lg);padding:16px;min-width:0}
.chatlog{background:transparent;border:0;padding:3px;min-height:230px;
 max-height:54vh;overflow:auto;display:flex;flex-direction:column;gap:13px}
.bub{max-width:84%;border-radius:var(--r-md);padding:11px 14px;font-size:var(--t-md);
 line-height:1.75;white-space:pre-wrap;word-break:break-word;box-shadow:var(--sh-1)}
.bub.me{align-self:flex-end;background:var(--brand);color:var(--brand-ink);
 border-bottom-right-radius:4px}
.bub.ai{align-self:flex-start;background:var(--bg);border:1px solid var(--line);
 border-bottom-left-radius:4px}
.bubmeta{font-size:var(--t-xs);opacity:.65;margin-bottom:4px;font-weight:500}
.chatbox{border:0;padding:0;margin-top:13px;background:none}
.chatbox textarea{width:100%;min-height:92px;line-height:1.7}
.chatnote2{margin-top:13px;padding-top:12px;border-top:1px solid var(--line2);
 font-size:var(--t-sm);line-height:1.85;color:var(--dim)}
.chatnote2 strong{color:var(--ink)}

/* 待办：紧凑但仍用卡片语言（左色条提示"待办"语义） */
.todo{border-left:3px solid var(--warn);border-radius:var(--r-md);padding:11px 15px}

/* 趋势：进度条用主色渐变（不再整页反色） */
td{font-variant-numeric:tabular-nums}

/* 同类题：引用块用主色边（与详情页一致，靠内容区分而非换主题） */
.detail blockquote,.q .aa{border-left:2px solid var(--line2);padding-left:13px}

/* 对话页侧栏的统计速览（替代原来重复的卡片列表） */
.sidequick{padding:2px}
.quicktitle{font-size:var(--t-xs);color:var(--dim);font-weight:640;
 margin:15px 0 8px;letter-spacing:.02em}
.quickrow{display:flex;gap:9px;flex-wrap:wrap}
.quickrow>div{flex:1;min-width:74px;background:var(--bg);border:1px solid var(--line);
 border-radius:var(--r-sm);padding:9px 11px}
.quickrow b{display:block;font-size:19px;font-weight:680;line-height:1.3;
 letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.quickrow span{color:var(--dim);font-size:var(--t-xs)}
.qb{display:flex;align-items:center;gap:9px;margin:7px 0;font-size:var(--t-sm)}
.qname{flex:0 0 84px;color:var(--ink);overflow:hidden;text-overflow:ellipsis;
 white-space:nowrap}
.qbar{flex:1;height:7px;background:var(--line2);border-radius:99px;overflow:hidden}
.qbar i{display:block;height:100%;border-radius:99px;
 background:linear-gradient(90deg,var(--brand),#818cf8)}
.qnum{flex:0 0 26px;text-align:right;color:var(--dim);
 font-variant-numeric:tabular-nums}
.quickhint{margin-top:14px;padding-top:11px;border-top:1px solid var(--line2);
 font-size:var(--t-xs);color:var(--dim);line-height:1.7}

/* 共用表格 */
table{width:100%;border-collapse:collapse;font-size:var(--t-md);background:var(--card);
 border-radius:var(--r-md);overflow:hidden;box-shadow:var(--sh-1)}
th,td{text-align:left;padding:10px 13px;border-bottom:1px solid var(--line2)}
th{color:var(--dim);font-weight:640;font-size:var(--t-xs);background:var(--line2)}
tr:last-child td{border-bottom:0}

/* 编辑区 */
.editbox{margin:16px 0;padding:15px;border:1px dashed var(--line);
 border-radius:var(--r-md);background:var(--bg)}
.edittitle{font-size:var(--t-sm);font-weight:660;margin-bottom:11px}
.editrow{display:flex;gap:9px;align-items:center;flex-wrap:wrap;margin-bottom:9px}
.editrow label{font-size:var(--t-xs);color:var(--dim);min-width:70px;
 font-family:ui-monospace,Menlo,Consolas,monospace}
.editrow input[type=text]{flex:1;min-width:190px}
</style></head><body>
<header>
  <div class="top"><h1>面经台</h1><span class="sub" id="sub">载入中…</span></div>
  <div class="tabs" id="tabs"></div>
</header>
<main><div id="view"><div class="load">载入中…</div></div></main>
<footer>数据实时读自本地 <code>cards/</code> · 不联网 · 不上传</footer>
<script>
const TABS=[["chat","对话"],["board","卡片"],["report","报告"],["todo","待办"],["trend","赛道"],
            ["cross","同类题"]];
let CARDS=[],OV=null,cur="board";

const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>
 ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const oLab=o=>({pass:"过",fail:"挂",no_offer:"无offer",unknown:"未标"}[o]||o);
const hi=(t,kw)=>{if(!kw)return esc(t);
 const i=String(t).toLowerCase().indexOf(kw.toLowerCase());
 if(i<0)return esc(t);
 return esc(t.slice(0,i))+"<mark>"+esc(t.slice(i,i+kw.length))+"</mark>"+esc(t.slice(i+kw.length));};

function tabs(){
 document.getElementById("tabs").innerHTML=TABS.map(([k,n])=>
  `<button class="tab ${k===cur?'on':''}" data-k="${k}">${n}</button>`).join("");
 // 主题切换：body[data-tab] 决定这一页用哪套设计（每页一种风格）
 document.body.dataset.tab=cur;
 document.querySelectorAll(".tab").forEach(b=>b.onclick=()=>{
   if(typeof stopChatPoll==="function") stopChatPoll();   // 离开对话页就别轮询了
   cur=b.dataset.k;tabs();go();
 });
}
function go(){
 if(cur==="chat")return chat();
 if(cur==="board")return board();
 if(cur==="report")return report();
 if(cur==="todo")return todo();
 if(cur==="trend")return trend();
 if(cur==="cross")return cross();
}

/* ── 对话 ──────────────────────────────────────────────────
   这一页**不接 AI**：它把消息写进 chat/对话.md，回到 DSH 会话
   说一句「看聊天」，AI 就会读它并回复（回复也写回同一文件）。
   这样网页不必持有 API Key，数据也不出本机。
   代价是省不掉"回来说一句"—— 如实写在页面提示里。 */
async function chat(){
 document.getElementById("view").innerHTML=`
  <div class="split">
   <div class="pane-chat">
    <div class="panehead">
      <strong>对话</strong>
      <span class="meta" id="cstat">自动刷新中</span>
    </div>
    <div id="chatlog" class="chatlog"><div class="load">载入中…</div></div>
    <div class="chatbox">
      <textarea id="cinput" placeholder="想跟 AI 说什么…&#10;&#10;例如：&#10;· 帮我看看我在某家公司那几场都挂在哪&#10;· 这段转写稿帮我建成卡（然后粘内容）&#10;· 哪类岗我拿得下&#10;&#10;（Ctrl+Enter 发送）"></textarea>
      <div class="editrow" style="margin-top:8px">
        <button class="go sm" id="csend">发送</button>
        <button class="gh sm" id="cclear">清空</button>
        <span class="meta" id="cmsg"></span>
      </div>
    </div>
    <div class="chatnote2">
      <strong>怎么拿到回复</strong>：回到 DSH 会话说「<strong>看聊天</strong>」，
      AI 读了就回复 —— 回复会<strong>自动出现在这里</strong>（本页每 2 秒刷新一次），
      不用手动刷。<br>
      <span class="meta">AI 只在收到消息时才会动，所以"回来说一句"这步省不掉；
      换来的是零依赖、不用 API Key、数据不出本机。</span>
    </div>
   </div>
   <div class="pane-side">
    <div class="panehead">
      <strong>这个库里有什么</strong>
      <span class="meta">在「卡片」页可搜可筛</span>
    </div>
    <div id="sidequick" class="sidequick"><div class="load">载入中…</div></div>
   </div>
  </div>`;
 await chatLoad();
 document.getElementById("csend").onclick=chatSend;
 document.getElementById("cinput").addEventListener("keydown",e=>{
   if((e.ctrlKey||e.metaKey)&&e.key==="Enter") chatSend();
 });
 document.getElementById("cclear").onclick=async()=>{
   if(!confirm("清空全部对话记录？（不可撤销）"))return;
   await chatPost({action:"clear"});
 };
 drawQuick();
 startChatPoll();
}

/* 侧栏：不再放一份卡片列表（那跟「卡片」页重复）。
   改成**统计速览** —— 边聊边能看到"我库里什么情况"，
   想看明细就点「卡片」页。 */
function drawQuick(){
 const el=document.getElementById("sidequick");
 if(!el) return;
 if(!CARDS.length){el.innerHTML='<div class="empty">还没有卡片</div>';return;}
 const byTrack={}, byOut={pass:0,fail:0,unknown:0,no_offer:0};
 CARDS.forEach(c=>{
   byTrack[c.track]=(byTrack[c.track]||0)+1;
   byOut[c.outcome]=(byOut[c.outcome]||0)+1;
 });
 const top=Object.entries(byTrack).sort((a,b)=>b[1]-a[1]).slice(0,6);
 const maxN=top.length?top[0][1]:1;
 const rate=Math.round(byOut.pass/Math.max(byOut.pass+byOut.fail,1)*100);
 el.innerHTML=`
  <div class="quickrow">
    <div><b>${CARDS.length}</b><span>总场次</span></div>
    <div><b style="color:var(--pass)">${rate}%</b><span>轮次通过率</span></div>
    <div><b>${OV.todos?OV.todos.length:0}</b><span>待补真值</span></div>
  </div>
  <div class="quicktitle">赛道分布（前 6）</div>
  ${top.map(([k,n])=>`<div class="qb">
     <span class="qname">${esc(k)}</span>
     <span class="qbar"><i style="width:${Math.round(n/maxN*100)}%"></i></span>
     <span class="qnum">${n}</span></div>`).join("")}
  <div class="quicktitle">结果</div>
  <div class="quickrow">
    <div><b>${byOut.pass}</b><span>过</span></div>
    <div><b>${byOut.fail}</b><span>挂</span></div>
    <div><b>${byOut.unknown+byOut.no_offer}</b><span>未标/无offer</span></div>
  </div>
  <div class="quickhint">想看明细（搜索/筛选/点开题目）→ 点顶部「卡片」</div>`;
}

/* ── 自动刷新：AI 的回复写进文件后，这里自己出现 ──
   每 2 秒拉一次 /api/chat，比对"最后一条"是否有变化；
   只在**真变了**或**条目数变了**时才重绘 —— 否则会把正在输入/滚动的位置冲掉。 */
let _chatTimer=null, _chatSig="";
function startChatPoll(){
 stopChatPoll();
 _chatTimer=setInterval(async()=>{
  if(cur!=="chat"){stopChatPoll();return;}     // 切走就停，别空跑
  try{
   const d=await (await fetch("/api/chat")).json();
   const ms=d.messages||[];
   const last=ms.length?ms[ms.length-1]:{};
   const sig=ms.length+"|"+last.time+"|"+last.who+"|"+(last.text||"").slice(0,40);
   if(sig!==_chatSig){
    _chatSig=sig;
    chatDraw(ms);
    const st=document.getElementById("cstat");
    if(st) st.textContent="已刷新 "+new Date().toLocaleTimeString().slice(0,5);
   }
  }catch(e){/* 网络抖动忽略，下一轮再试 */}
 },2000);
}
function stopChatPoll(){
 if(_chatTimer){clearInterval(_chatTimer);_chatTimer=null;}
}
async function chatLoad(){
 try{
  const d=await (await fetch("/api/chat")).json();
  chatDraw(d.messages||[]);
 }catch(e){
  document.getElementById("chatlog").innerHTML=
   `<div class="empty">读取失败：${esc(String(e))}</div>`;
 }
}
function chatDraw(ms){
 const box=document.getElementById("chatlog");
 if(!ms.length){
  box.innerHTML='<div class="empty">还没有对话。在下面写第一条，然后回 DSH 说「看聊天」。</div>';
  return;
 }
 box.innerHTML=ms.map(m=>`<div class="bub ${m.who==="我"?"me":"ai"}">
   <div class="bubmeta">${esc(m.who)} · ${esc(m.time)}</div>
   <div class="bubtext">${esc(m.text)}</div></div>`).join("");
 box.scrollTop=box.scrollHeight;
}
async function chatPost(payload){
 const r=await fetch("/api/chat",{
   method:"POST",
   headers:{"Content-Type":"application/json","X-Mianjing-Edit":"1"},
   body:JSON.stringify(payload)});
 return await r.json();
}
async function chatSend(){
 const ta=document.getElementById("cinput");
 const t=ta.value.trim();
 if(!t){document.getElementById("cmsg").textContent="先写点什么";return;}
 const msg=document.getElementById("cmsg");
 msg.textContent="记录中…";
 const d=await chatPost({text:t,who:"我"});
 if(!d.ok){msg.innerHTML=`<span style="color:var(--fail)">✗ ${esc(d.msg)}</span>`;return;}
 ta.value="";
 chatDraw(d.messages||[]);
 msg.innerHTML='<span style="color:var(--pass)">✓ 已记入</span> · 回 DSH 说「看聊天」';
}

/* ── 空库引导：新用户第一次打开看到的第一屏 ──
   ⚠️ 这一屏是"产品"的一部分，跟具体某个人的数据无关：
      任何新装这个包的人，cards/ 都是空的，必须先告诉他怎么开始。
      旧版直接显示「没有匹配的场次」，会让人以为是自己筛错了。 */
function emptyState(){
 document.getElementById("view").innerHTML=`
  <div class="detail" style="max-width:640px;margin:26px auto">
   <h2 style="margin:0 0 6px;font-size:16px">还没有面试记录</h2>
   <p class="meta" style="margin:0 0 14px">
     这个界面读的是包根 <code>cards/</code> 里的卡片。里面还没有正式卡，所以是空的。</p>
   <p style="margin:0 0 8px"><strong>三种开始方式，挑一个：</strong></p>
   <ol style="padding-left:20px;margin:0 0 14px;line-height:1.9">
     <li><strong>最省事</strong>：把某场面试的转写稿直接发给 AI，
         让它按 <code>tools/digest_guide.md</code> 拆成卡片（不用自己敲命令）</li>
     <li><strong>自己建</strong>：<code class="cmd">python main.py record new --company 公司 --position 岗位 --round 一面 --nature 正编</code></li>
     <li><strong>看示例</strong>：<code>example/</code> 里有虚构的示范卡，先照着理解字段</li>
   </ol>
   <p class="meta" style="margin:0">
     建完刷新本页即可（数据是实时读的）。草稿卡在 <code>cards/_inbox/</code>，
     用 <code class="cmd">python main.py merge formalize</code> 转正后会出现在这里。</p>
  </div>`;
}

/* ── 卡片 ── */
function board(){
 if(!CARDS.length)return emptyState();
 const tracks=[...new Set(CARDS.map(c=>c.track))].sort();
 const nats=[...new Set(CARDS.map(c=>c.nature))].sort();
 document.getElementById("view").innerHTML=`
  <div class="stats">
    <div class="stat"><b>${OV.n}</b><span>总场次</span></div>
    <div class="stat"><b style="color:var(--pass)">${OV.pass}</b><span>过</span></div>
    <div class="stat"><b style="color:var(--fail)">${OV.fail}</b><span>挂</span></div>
    <div class="stat"><b>${OV.questions}</b><span>问答条数</span></div>
  </div>
  <div class="filters">
    <input type="search" id="kw" placeholder="搜公司 / 岗位 / 题目 / 回答全文…">
    <select id="fo"><option value="">全部结果</option><option value="pass">只看过</option>
      <option value="fail">只看挂</option><option value="unknown">未标</option></select>
    <select id="ft"><option value="">全部赛道</option>${tracks.map(t=>`<option>${esc(t)}</option>`).join("")}</select>
    <select id="fn"><option value="">全部性质</option>${nats.map(t=>`<option>${esc(t)}</option>`).join("")}</select>
  </div>
  <div class="grid" id="list"></div>`;
 ["kw","fo","ft","fn"].forEach(i=>document.getElementById(i).addEventListener("input",drawList));
 drawList();
}
function drawList(){
 const kw=document.getElementById("kw").value.trim();
 const fo=document.getElementById("fo").value, ft=document.getElementById("ft").value,
       fn=document.getElementById("fn").value;
 const low=kw.toLowerCase();
 const hit=CARDS.filter(c=>{
  if(fo&&c.outcome!==fo)return false;
  if(ft&&c.track!==ft)return false;
  if(fn&&c.nature!==fn)return false;
  if(!low)return true;
  const b=(c.company+" "+c.position+" "+c.id+" "+c.track+" "+c.reason+" "+
   c.why_ended+" "+c.weakness+" "+c.strength+" "+c.context+" "+
   c.questions.map(q=>q.q+" "+q.theme+" "+q.a).join(" ")).toLowerCase();
  return b.includes(low);
 });
 const L=document.getElementById("list");
 if(!hit.length){
  // 说明为什么没结果：有筛选条件 → 是筛掉的；没条件却空 → 库本来就是空的
  const hasFilter=!!(kw||fo||ft||fn);
  L.innerHTML='<div class="empty">'+(hasFilter
   ?'没有符合条件的场次 —— 试试放宽筛选'
   :'cards/ 里还没有正式卡')+'</div>';
  return;}
 L.innerHTML=hit.map(c=>`<div class="c" data-id="${esc(c.id)}">
   <h3><span class="pill p-${esc(c.outcome)}">${oLab(c.outcome)}</span>
   <span>${esc(c.id)} ${hi(c.company,kw)}</span>
   <span class="pill p-g">${esc(c.nature)}</span>
   <span class="pill p-t">${esc(c.track)}</span></h3>
   <div class="meta">${hi(c.position,kw).slice(0,150)}${c.round?" · "+esc(c.round):""}${c.date?" · "+esc(c.date):""} · ${c.questions.length} 题</div>
   ${c.why_ended||c.reason?`<div class="why">${hi((c.why_ended||c.reason),kw).slice(0,170)}</div>`:""}
 </div>`).join("");
 L.querySelectorAll(".c").forEach(e=>e.onclick=()=>detail(e.dataset.id,kw));
}
function detail(id,kw){
 const c=CARDS.find(x=>x.id===id); if(!c)return;
 const qs=c.questions.length?c.questions.map(q=>`<div class="q">
   <div class="qq">${hi(q.q,kw)}${q.theme?`<span class="tag">${esc(q.theme)}</span>`:""}${q.score?`<span class="tag">自评 ${esc(q.score)}</span>`:""}</div>
   ${q.a?`<div class="aa">${hi(q.a,kw)}</div>`:'<div class="aa">（没记回答）</div>'}
 </div>`).join(""):'<div class="empty">这场没记题目</div>';
 document.getElementById("list").innerHTML=`
  <button class="back">← 回列表</button>
  <div class="detail">
   <h2 style="margin:0 0 5px;font-size:16px">${esc(c.id)} ${esc(c.company)} · ${esc(c.position)}</h2>
   <div class="meta" style="margin-bottom:11px">
     <span class="pill p-${esc(c.outcome)}">${oLab(c.outcome)}</span>
     <span class="pill p-g">${esc(c.nature)}</span>
     <span class="pill p-t">${esc(c.track)}</span>
     ${c.round?" · "+esc(c.round):""}${c.date?" · "+esc(c.date):""}
     ${c.offer?" · offer="+esc(c.offer):""}</div>
   ${c.why_ended?`<p><strong>为什么没推进：</strong>${esc(c.why_ended)}</p>`:""}
   ${c.reason?`<p><strong>当时记的原因：</strong>${esc(c.reason)}</p>`:""}
   ${c.signal?`<p><strong>面试官信号：</strong>${esc(c.signal)}</p>`:""}
   ${c.strength?`<p><strong>做得好的：</strong>${esc(c.strength)}</p>`:""}
   ${c.weakness?`<p><strong>暴露的短板：</strong>${esc(c.weakness)}</p>`:""}
   ${c.improvement?`<p><strong>下次改进：</strong>${esc(c.improvement)}</p>`:""}
   ${c.skills.length?`<p><strong>能力标签：</strong>${c.skills.map(esc).join(" / ")}</p>`:""}
   ${editForm(c)}
   <h3 style="margin:15px 0 2px;font-size:14px">题目与回答（${c.questions.length}）</h3>
   ${qs}</div>`;
 document.querySelector(".back").onclick=()=>{board();
  document.getElementById("kw").value=kw; drawList();};
 bindEdit(c);
 window.scrollTo({top:0,behavior:"smooth"});
}

/* ── 改卡（第二阶段的写功能）──────────────────────────────
   设计取舍：
     · 只暴露 4 个真值字段 + 赛道，不做"编辑整张卡" —— 卡是核心资产，
       要改复杂内容请用命令行/AI。
     · 保存前**必须二次确认**，并显示将要把「旧值 → 新值」写进去。
     · 保存后不回退到列表，而是就地刷新，方便连着补几张。 */
function editForm(c){
 return `<div class="editbox">
   <div class="edittitle">✎ 补齐真值 <span class="meta">（写前自动备份到 cards/_bak/）</span></div>
   <div class="editrow">
     <label>outcome</label>
     <select id="e-outcome">${["","pass","fail","no_offer","unknown"]
       .map(o=>`<option value="${o}" ${c.outcome===o?"selected":""}>${o||"（不改）"}</option>`).join("")}</select>
     <label>offer</label>
     <select id="e-offer">${["","got","no","ongoing"]
       .map(o=>`<option value="${o}" ${c.offer===o?"selected":""}>${o||"（不改）"}</option>`).join("")}</select>
   </div>
   <div class="editrow">
     <label>why_ended</label>
     <input type="text" id="e-why" placeholder="为什么没推进（如：横向对比 / 无HC / 薪资）">
   </div>
   <div class="editrow">
     <label>reason</label>
     <input type="text" id="e-reason" placeholder="你记的原因（可留空）">
   </div>
   <div class="editrow">
     <button class="go sm" id="e-save" data-id="${esc(c.id)}">保存</button>
     <span class="meta" id="e-msg"></span>
   </div>
 </div>`;
}
function bindEdit(c){
 const btn=document.getElementById("e-save");
 if(!btn) return;
 btn.onclick=async()=>{
  const f={};
  const o=document.getElementById("e-outcome").value;
  const of=document.getElementById("e-offer").value;
  const w=document.getElementById("e-why").value.trim();
  const r=document.getElementById("e-reason").value.trim();
  if(o) f.outcome=o;
  if(of) f.offer=of;
  if(w) f.why_ended=w;
  if(r) f.reason=r;
  if(!Object.keys(f).length){document.getElementById("e-msg").textContent="没有要改的内容";return;}
  const desc=Object.entries(f).map(([k,v])=>`${k} = ${v}`).join("\n");
  if(!confirm(`确认把这 ${Object.keys(f).length} 项写入 ${c.id}？\n\n${desc}\n\n（原卡会先备份到 cards/_bak/）`)) return;
  const msg=document.getElementById("e-msg");
  msg.textContent="保存中…";
  try{
   const res=await fetch("/api/edit",{
     method:"POST",
     headers:{"Content-Type":"application/json","X-Mianjing-Edit":"1"},
     body:JSON.stringify({id:c.id,fields:f})});
   const d=await res.json();
   if(!d.ok){msg.innerHTML=`<span style="color:var(--fail)">✗ ${esc(d.msg)}</span>`;return;}
   const ch=(d.changes||[]).filter(x=>x.field!=="_backup")
     .map(x=>`${x.field}: 「${esc(String(x.old).slice(0,20))}」→「${esc(String(x.new).slice(0,20))}」`).join("<br>");
   msg.innerHTML=`<span style="color:var(--pass)">✓ ${esc(d.msg)}</span><br>${ch}<br>`
     +`<span class="meta">已备份 · 刷新列表可见新状态</span>`;
   // 同步内存里的数据，避免列表还显示旧值
   CARDS=await (await fetch("/api/cards")).json();
   OV=await (await fetch("/api/overview")).json();
  }catch(e){
   msg.innerHTML=`<span style="color:var(--fail)">✗ 请求失败：${esc(String(e))}</span>`;
  }
 };
}

/* ── 报告 ── */
async function report(){
 const rs=await (await fetch("/api/reports")).json();
 if(!rs.length){document.getElementById("view").innerHTML=
  `<div class="detail" style="max-width:600px;margin:26px auto">
    <h2 style="margin:0 0 6px;font-size:16px">还没有生成过报告</h2>
    <p class="meta" style="margin:0 0 12px">报告是由引擎从卡片推导出来的。</p>
    <p>在 <code>tools/</code> 下跑一次：</p>
    <p><code class="cmd">python main.py report</code></p>
    <p class="meta" style="margin-top:12px">跑完刷新本页即可。
      报告需要一定样本量才有意义（十几场以上再看结论）。</p>
   </div>`;return;}
 document.getElementById("view").innerHTML=`
  <div class="filters"><select id="rf">${rs.map(r=>
   `<option value="${esc(r.file)}">${esc(r.name)} — ${esc(r.desc)}</option>`).join("")}</select>
  <span class="meta" id="rmt"></span></div>
  <div class="md" id="rc">载入中…</div>`;
 const sel=document.getElementById("rf");
 const load=async()=>{
  const r=await (await fetch("/api/report?f="+encodeURIComponent(sel.value))).json();
  document.getElementById("rc").innerHTML=md(r.text||"（空）");
  const meta=rs.find(x=>x.file===sel.value);
  document.getElementById("rmt").textContent=meta?"更新于 "+meta.mtime:"";
 };
 sel.onchange=load; load();
}
/* 极简 md 渲染（报告是我们自己生成的，格式可控） */
function md(t){
 const L=t.split("\n"); let o=[],inT=false,inL=false,inQ=false;
 const inline=s=>esc(s)
  .replace(/`([^`]+)`/g,"<code>$1</code>")
  .replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>")
  .replace(/\*([^*]+)\*/g,"<em>$1</em>");
 for(let i=0;i<L.length;i++){
  const l=L[i];
  if(/^\|/.test(l)){
   const cells=l.split("|").slice(1,-1).map(s=>s.trim());
   if(/^\|[\s:|-]+\|$/.test(L[i+1]||"")){o.push("<table><tr>"+
    cells.map(c=>"<th>"+inline(c)+"</th>").join("")+"</tr>");i++;inT=true;continue;}
   if(inT){o.push("<tr>"+cells.map(c=>"<td>"+inline(c)+"</td>").join("")+"</tr>");continue;}
  } else if(inT){o.push("</table>");inT=false;}
  if(/^###\s/.test(l)){o.push("<h3>"+inline(l.slice(4))+"</h3>");continue;}
  if(/^##\s/.test(l)){o.push("<h2>"+inline(l.slice(3))+"</h2>");continue;}
  if(/^#\s/.test(l)){o.push("<h1>"+inline(l.slice(2))+"</h1>");continue;}
  if(/^>\s?/.test(l)){o.push('<blockquote>'+inline(l.replace(/^>\s?/,""))+"</blockquote>");continue;}
  if(/^[-*]\s/.test(l)){if(!inL){o.push("<ul>");inL=true;}
   o.push("<li>"+inline(l.slice(2))+"</li>");continue;}
  if(inL){o.push("</ul>");inL=false;}
  if(l.trim()===""){o.push("");continue;}
  o.push("<p>"+inline(l)+"</p>");
 }
 if(inT)o.push("</table>"); if(inL)o.push("</ul>");
 return o.join("\n");
}

/* ── 待办 ── */
function todo(){
 if(!CARDS.length){document.getElementById("view").innerHTML=
  '<div class="empty">还没有卡片 —— 先建一场面试，这里会列出缺真值的场次</div>';return;}
 const t=OV.todos;
 const by={}; t.forEach(x=>by[x.kind]=(by[x.kind]||0)+1);
 document.getElementById("view").innerHTML=`
  <div class="stats">${Object.entries(by).map(([k,v])=>
   `<div class="stat"><b>${v}</b><span>${esc(k)}</span></div>`).join("")}</div>
  ${t.length?`<p class="meta">这些卡还缺真值。真值是统计的唯一来源 —— 缺了它们，
    报告里对应那几节会失真。命令可直接复制到 <code>tools/</code> 下执行。</p>
   <div class="grid">${t.map(x=>`<div class="todo">
    <div><strong>${esc(x.id)}</strong> ${esc(x.company)} · <span class="meta">${esc(x.kind)} —— ${esc(x.why)}</span></div>
    <code class="cmd">python main.py ${esc(x.cmd)}</code></div>`).join("")}</div>`
   :'<div class="empty">所有卡的真值都齐了 👍</div>'}`;
}

/* ── 趋势 ── */
function trend(){
 if(!CARDS.length){document.getElementById("view").innerHTML=
  '<div class="empty">还没有卡片 —— 先攒够十几场再看</div>';return;}
 if(!OV.tracks||!OV.tracks.length)return document.getElementById("view").innerHTML=
  '<div class="empty">还没有足够带结果的正编卡来算赛道通过率<br>'
  +'<span class="meta">（只看正编口径、且结果已确定的场次）</span></div>';
 document.getElementById("view").innerHTML=`
  <p class="meta" style="margin-bottom:13px">各赛道通过率（正编口径，结果已确定的场次）</p>
  <table><tr><th>赛道</th><th>过</th><th>挂</th><th>场次</th><th>通过率</th></tr>
  ${OV.tracks.map(r=>`<tr>
   <td>${esc(r.track)}</td>
   <td>${r.pass}</td>
   <td>${r.fail}</td>
   <td class="meta">${r.n}</td>
   <td><strong>${r.rate}%</strong></td></tr>`).join("")}
  </table>`;
}

/* ── 同类题对比 ── */
function cross(){
 document.getElementById("view").innerHTML=`
  <div class="filters"><input type="search" id="cq"
   placeholder="输入一个关键词或题目，看你在各场是怎么答的（如：供给、冷启动、垂类划分）">
   </div><div id="cr"><div class="empty">输入关键词开始</div></div>`;
 const box=document.getElementById("cr");
 let t=null;
 document.getElementById("cq").addEventListener("input",e=>{
  clearTimeout(t); t=setTimeout(()=>draw(e.target.value.trim()),260);
 });
 function draw(kw){
  if(kw.length<2){box.innerHTML='<div class="empty">至少输入 2 个字</div>';return;}
  const low=kw.toLowerCase(); const rows=[];
  CARDS.forEach(c=>c.questions.forEach(q=>{
   const blob=(q.q+" "+q.theme+" "+q.a).toLowerCase();
   if(blob.includes(low))rows.push({c,q});
  }));
  if(!rows.length){box.innerHTML='<div class="empty">没有匹配的题目</div>';return;}
  box.innerHTML=`<p class="meta">命中 ${rows.length} 条，来自 ${new Set(rows.map(r=>r.c.id)).size} 张卡（按自评分排序）</p>`+
   rows.sort((a,b)=>(b.q.score||0)-(a.q.score||0)).map(({c,q})=>`
   <div class="detail" style="margin-bottom:9px">
     <div class="meta"><span class="pill p-${esc(c.outcome)}">${oLab(c.outcome)}</span>
      <strong>${esc(c.id)} ${esc(c.company)}</strong> · ${esc(c.round)}
      ${q.score?`· 自评 ${esc(q.score)}`:""}${q.theme?` · ${esc(q.theme)}`:""}</div>
     <div class="qq" style="margin-top:6px">${hi(q.q,kw)}</div>
     <div class="aa">${q.a?hi(q.a,kw):"（没记回答）"}</div>
   </div>`).join("");
 }
}

/* ── 启动 ── */
(async()=>{
 tabs();
 CARDS=await (await fetch("/api/cards")).json();
 OV=await (await fetch("/api/overview")).json();
 document.getElementById("sub").textContent=
  `${OV.n} 场 · ${OV.questions} 条问答 · 正编 ${OV.zheng}`;
 go();
})();
</script></body></html>
"""


def serve(port, auto_open):
    from http.server import ThreadingHTTPServer
    H = make_handler()
    srv = ThreadingHTTPServer(("127.0.0.1", port), H)
    url = "http://127.0.0.1:%d/" % port
    print()
    print("  面经台已启动 →  %s" % url)
    print("  （Ctrl+C 停止；数据实时读自 cards/，改完刷新即可）")
    print()
    if auto_open:
        try:
            import webbrowser
            threading.Timer(0.6, lambda: webbrowser.open(url)).start()
        except Exception:
            pass
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n  已停止。")
    finally:
        srv.server_close()
    return 0


def export_static(out):
    """导出单文件 HTML（数据内嵌）。只读快照，适合发给别人看（注意含个人数据）。"""
    cards = load_cards()
    ov = {
        "n": len(cards),
        "pass": sum(1 for c in cards if c["outcome"] == "pass"),
        "fail": sum(1 for c in cards if c["outcome"] == "fail"),
        "zheng": sum(1 for c in cards if c["nature"] == "正编"),
        "questions": sum(len(c["questions"]) for c in cards),
        "tracks": compute_tracks(cards),
        "todos": compute_todos(cards),
    }
    page = PAGE.replace(
        'CARDS=await (await fetch("/api/cards")).json();\n'
        ' OV=await (await fetch("/api/overview")).json();',
        "CARDS=%s; OV=%s;" % (json.dumps(cards, ensure_ascii=False),
                              json.dumps(ov, ensure_ascii=False)))
    # 报告页在静态模式下不可用 → 去掉该标签
    page = page.replace('["report","报告"],', '')
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    return out


def main():
    ap = argparse.ArgumentParser(description="面经台 · 本地图形界面")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-open", action="store_true", help="不自动打开浏览器")
    ap.add_argument("--export", help="导出单文件 HTML（只读快照）")
    a = ap.parse_args()
    if yaml is None:
        print("[ERR] 需要 pyyaml: pip install pyyaml")
        return 2
    if a.export:
        p = export_static(a.export)
        print("[OK] 已导出 →", p)
        print("     ⚠️ 该文件内嵌了你的全部卡片数据，别外发")
        return 0
    return serve(a.port, not a.no_open)


if __name__ == "__main__":
    sys.exit(main())
