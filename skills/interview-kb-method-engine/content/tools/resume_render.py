#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Skill v3「简历修改」阶段 — 简历源渲染器（终稿输出）。

把结构化简历源(YAML)渲染成"单栏、克制、数据突出"的 HTML（风格向超级简历/WonderCV 靠）。

设计原则（参考超级简历公开的排版理念，非其专有模板）：
  - 单栏、无花哨图表/图标/色块
  - 强文字层级：姓名/区块标题/经历公司角色/成果点，层级分明
  - 数据(before→after / 百分比)视觉突出
  - 留白充分、行距舒服、A4 适配
  - 不自动加"个人总结/自评"等无依据的空话；只基于结构化字段渲染

用法:
  python resume_render.py --file <简历源.yaml> --out resume.html [--md resume.md]

结构化源字段（与 resume_check.py 一致）:
  header: {name, title, phone, email, base, ...}   # 可选，基本信息区
  experiences:
    - company / role / period / headline / bullets[{action, metric, goal}]
  skills: []
"""
import sys, os, html, re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml
except Exception:
    print("[ERR] 需要 pyyaml: pip install pyyaml"); sys.exit(2)


def esc(s):
    return html.escape(str(s))


def load(fp):
    with open(fp, encoding="utf-8") as f:
        return yaml.safe_load(f.read())


# ---------- HTML 模板（单栏，向超级简历风格靠） ----------

CSS = """
:root{
  --ink:#1f2328; --muted:#6a7079; --line:#e6e9ee; --accent:#1a73e8;
  --font: -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",Roboto,Helvetica,Arial,sans-serif;
}
*{box-sizing:border-box;}
body{margin:0;background:#f4f5f7;font-family:var(--font);color:var(--ink);-webkit-font-smoothing:antialiased;}
.page{max-width:816px;margin:24px auto;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.08);padding:56px 64px;line-height:1.55;}
h1.name{font-size:26px;font-weight:700;margin:0;letter-spacing:.5px;}
.subtitle{font-size:14px;color:var(--muted);margin:6px 0 0;}
.contact{margin-top:10px;font-size:13px;color:var(--muted);}
.contact span{margin-right:14px;}
.section{margin-top:28px;}
.section-title{font-size:15px;font-weight:700;letter-spacing:1px;color:var(--ink);margin:0 0 12px;padding-bottom:6px;border-bottom:1.5px solid var(--line);}
.exp{margin-bottom:20px;}
.exp-head{display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:6px;}
.exp-role{font-size:15px;font-weight:700;}
.exp-company{font-size:15px;font-weight:700;color:var(--ink);}
.exp-period{font-size:13px;color:var(--muted);white-space:nowrap;}
.exp-headline{font-size:13.5px;color:#3c434c;margin:6px 0 8px;}
.bullets{margin:0;padding:0;list-style:none;}
.bullets li{position:relative;padding-left:14px;margin:5px 0;font-size:13.5px;color:#2b3037;}
.bullets li::before{content:"·";position:absolute;left:0;color:var(--accent);font-weight:700;}
.gain{color:#0b6a3f;font-weight:700;}
.skills{margin:0;padding:0;list-style:none;display:flex;flex-wrap:wrap;gap:8px;}
.skills li{font-size:13px;padding:3px 10px;border-radius:4px;background:#f2f4f7;color:#3c434c;}
@media print{body{background:#fff}.page{box-shadow:none;margin:0;padding:40px 48px;}}
"""

GAIN_SPAN_RE = re.compile(r"(\d[\d\.]*\s*[→%倍至到]\s*[\d\.%\u4e00-\u9fff]*|[\uff08(]?\d+[\uff09)]?(倍|%|\+))")

# ── 个人总结 / 技能特长字段白名单 ──
# 必须与 resume_check.py 的 SUMMARY_FIELDS 保持一致：
# check 那边管这批字段的写法，render 这边必须能把它们渲染出来，
# 否则"规则改了、渲染丢了"（实测踩过：加了 summary 但 render 不输出）。
SUMMARY_FIELDS = [
    ("summary", "个人总结"), ("个人总结", "个人总结"),
    ("自我评价", "自我评价"), ("自我描述", "自我描述"),
    ("个人简介", "个人简介"), ("个人评价", "个人评价"),
    ("技能特长", "技能特长"), ("个人优势", "个人优势"),
    ("核心能力", "核心能力"), ("核心优势", "核心优势"),
    ("专业技能", "专业技能"), ("专业特长", "专业特长"),
    ("highlights", "亮点"), ("strengths", "优势"),
    ("self_summary", "个人总结"), ("skills_summary", "技能特长"),
]

_SUMMARY_TOKENS = ("总结", "自我评价", "自我描述", "个人简介", "个人评价",
                   "技能特长", "个人优势", "核心能力", "核心优势",
                   "专业技能", "专业特长")


def _as_items(v):
    """把字段值统一成字符串列表。"""
    if v is None:
        return []
    if isinstance(v, str):
        return [v.strip()] if v.strip() else []
    if isinstance(v, list):
        out = []
        for it in v:
            if isinstance(it, str):
                if it.strip():
                    out.append(it.strip())
            elif isinstance(it, dict):
                for kk in ("text", "content", "desc", "description", "value", "name"):
                    if it.get(kk):
                        out.append(str(it[kk]).strip())
                        break
                else:
                    out.append(str(it))
        return out
    return [str(v)]


def collect_summary(data):
    """取出总结/技能特长字段，返回 [(显示名, [条目...]), ...]，保持原顺序。"""
    out = []
    if not isinstance(data, dict):
        return out
    for k, v in data.items():
        label = None
        for key, disp in SUMMARY_FIELDS:
            if str(k).strip().lower() == key:
                label = disp
                break
        if label is None and any(t in str(k) for t in _SUMMARY_TOKENS):
            label = str(k)
        if label:
            items = _as_items(v)
            if items:
                out.append((label, items))
    return out


def highlight_gain(text):
    """把 metric 里 before→after / 百分比 数字加粗上色（.gain）。"""
    t = esc(text)
    def repl(m):
        return f'<span class="gain">{m.group(0)}</span>'
    return GAIN_SPAN_RE.sub(repl, t)


def render_html(data):
    hdr = data.get("header") or {}
    name = hdr.get("name", "") or ""
    title = hdr.get("title", "") or ""
    items = []
    contact = []
    for k in ("base", "phone", "email", "site", "years"):
        v = hdr.get(k)
        if v:
            contact.append(esc(str(v)))
    # 基本信息
    chunks = []
    if name:
        chunks.append(f'<h1 class="name">{esc(name)}</h1>')
    if title:
        chunks.append(f'<div class="subtitle">{esc(title)}</div>')
    if contact:
        chunks.append('<div class="contact">' + "".join(f"<span>{c}</span>" for c in contact) + "</div>")

    # 个人总结 / 技能特长（放最前，先给主线）
    # 复用已有的 .section / .section-title / .bullets 样式，不新增 CSS
    for label, items in collect_summary(data):
        chunks.append('<div class="section">')
        chunks.append(f'<div class="section-title">{esc(label)}</div>')
        chunks.append('<ul class="bullets">' +
                      "".join(f"<li>{highlight_gain(it)}</li>" for it in items) +
                      "</ul>")
        chunks.append('</div>')

    exps = data.get("experiences") or []
    exp_html = []
    for blk in exps:
        if not isinstance(blk, dict):
            continue
        company = esc(blk.get("company", "") or "")
        role = esc(blk.get("role", "") or "")
        period = esc(blk.get("period", "") or "")
        hl = highlight_gain(blk.get("headline", "") or "")
        roleline = ""
        if role and company:
            roleline = f'<span class="exp-role">{role}</span>'
            if company:
                roleline += f' <span class="exp-company">· {company}</span>'
        elif role:
            roleline = f'<span class="exp-role">{role}</span>'
        else:
            roleline = f'<span class="exp-role">{company}</span>'
        head = f'<div class="exp-head">{roleline}<span class="exp-period">{period}</span></div>'
        lis = []
        for b in (blk.get("bullets") or []):
            if not isinstance(b, dict):
                continue
            act = esc(b.get("action", "") or "")
            met = highlight_gain(b.get("metric", "") or "")
            parts = [act]
            if met:
                parts.append(met)
            lis.append("<li>" + "　".join(p for p in parts if p) + "</li>")
        blk_html = head
        if hl:
            blk_html += f'<div class="exp-headline">{hl}</div>'
        blk_html += f'<ul class="bullets">{"".join(lis)}</ul>'
        exp_html.append(f'<div class="exp">{blk_html}</div>')

    sk = data.get("skills") or []
    sk_html = ""
    if sk:
        sk_html = ('<div class="section"><div class="section-title">技能</div>'
                   '<ul class="skills">' + "".join(f"<li>{esc(s)}</li>" for s in sk) + "</ul></div>")

    body = "".join(chunks)
    body += '<div class="section"><div class="section-title">工作经历</div>' + "".join(exp_html) + "</div>"
    body += sk_html

    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(name or '简历')}</title>
<style>{CSS}</style></head>
<body><div class="page">{body}</div></body></html>"""


def render_markdown(data):
    hdr = data.get("header") or {}
    L = []
    if hdr.get("name"):
        L.append(f"# {hdr['name']}")
    if hdr.get("title"):
        L.append(f"**{hdr['title']}**  ")
    contact = [str(hdr[k]) for k in ("base", "phone", "email", "site", "years") if hdr.get(k)]
    if contact:
        L.append(" · ".join(contact))
    L.append("")
    # ── 个人总结 / 技能特长（放在最前，让人先看到主线）──
    # 之前 render 只输出「工作经历 + 技能」，把总结区整个丢掉了 ——
    # 而 resume_check 的 5 条规则恰恰是在管这一块，规则改了却渲染不出来。
    sums = collect_summary(data)
    if sums:
        for field, items in sums:
            L.append(f"## {field}")
            for it in items:
                L.append(f"- {it}")
            L.append("")
    L.append("## 工作经历")
    for blk in (data.get("experiences") or []):
        if not isinstance(blk, dict):
            continue
        role = blk.get("role", "") or ""
        company = blk.get("company", "") or ""
        period = blk.get("period", "") or ""
        L.append(f"### {role} · {company}  （{period}）")
        if blk.get("headline"):
            L.append(f">{blk['headline']}")
        for b in (blk.get("bullets") or []):
            if not isinstance(b, dict):
                continue
            act = b.get("action", "") or ""
            met = b.get("metric", "") or ""
            L.append(f"- {act}　**{met}**")
        L.append("")
    sk = data.get("skills") or []
    if sk:
        L.append("## 技能")
        L.append("  | ".join(str(s) for s in sk))
        L.append("")
    return "\n".join(L)


def main(argv=None):
    argv = list(argv) if argv else sys.argv[1:]
    if "--file" not in argv or "--out" not in argv:
        print(__doc__); return 2
    fp = argv[argv.index("--file") + 1]
    out = argv[argv.index("--out") + 1]
    md_out = None
    if "--md" in argv:
        md_out = argv[argv.index("--md") + 1]
    if not os.path.exists(fp):
        print(f"[ERR] 文件不存在: {fp}"); return 2
    try:
        data = load(fp)
    except Exception as e:
        print(f"[ERR] YAML 解析失败: {e}"); return 2
    with open(out, "w", encoding="utf-8") as f:
        f.write(render_html(data))
    print(f"[OK] 已生成 HTML 简历: {out}")
    if md_out:
        with open(md_out, "w", encoding="utf-8") as f:
            f.write(render_markdown(data))
        print(f"[OK] 已生成 Markdown 简历: {md_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
