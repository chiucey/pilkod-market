#!/usr/bin/env python3
"""
website-testing skill — Report Formatter
Usage: python format_report.py <audit_json_path> [--format md|txt]

Converts the JSON output of audit.py into a human-readable Markdown or
plain-text report suitable for attaching to a user message.
"""

import sys
import json
import argparse
from datetime import datetime

SEVERITY_EMOJI = {
    "CRITICAL": "🔴",
    "HIGH":     "🟠",
    "MEDIUM":   "🟡",
    "WARNING":  "🔵",
}

DIMENSION_LABELS = {
    "infrastructure": "基础设施 & SSL",
    "performance":    "性能",
    "seo":            "SEO",
    "security":       "安全性",
    "content":        "内容质量",
}

def score_label(s: int) -> str:
    if s >= 80: return "良好 ✅"
    if s >= 60: return "待改进 ⚠️"
    if s >= 40: return "较差 🟠"
    return "严重不足 🔴"


def fmt_md(data: dict) -> str:
    url = data["url"]
    date = data.get("test_date", "")[:10]
    score = data["overall_score"]
    counts = data["issue_counts"]
    issues = data["all_issues"]

    lines = [
        f"# 网站测试报告 — {url}",
        f"",
        f"> **测试日期**: {date}  |  **综合评分**: {score}/100 ({score_label(score)})",
        f"> **问题统计**: 🔴 严重 {counts['critical']}  🟠 高 {counts['high']}  🟡 中 {counts['medium']}  🔵 警告 {counts['warning']}",
        f"",
        f"---",
        f"",
        f"## 一、综合评分",
        f"",
        f"| 维度 | 状态 | 问题数 |",
        f"|------|------|--------|",
    ]

    for dim_key, dim_label in DIMENSION_LABELS.items():
        dim_data = data.get(dim_key, {})
        dim_issues = dim_data.get("issues", [])
        critical = sum(1 for i in dim_issues if i.startswith("CRITICAL"))
        high = sum(1 for i in dim_issues if i.startswith("HIGH"))
        if critical > 0:
            status = "🔴 严重"
        elif high > 0:
            status = "🟠 需改进"
        elif dim_issues:
            status = "🟡 注意"
        else:
            status = "✅ 正常"
        lines.append(f"| {dim_label} | {status} | {len(dim_issues)} |")

    lines += ["", "---", "", "## 二、各维度详情", ""]

    # Infrastructure
    infra = data.get("infrastructure", {})
    lines += [
        "### 基础设施 & SSL",
        "",
        f"- **IP 地址**: `{infra.get('ip_address', 'N/A')}`",
        f"- **CDN**: {infra.get('cdn_detected', '未检测到')}",
        f"- **HTTPS 强制跳转**: {'✅' if infra.get('https_redirect') else '❌'}",
        f"- **HTTP/2**: {'✅' if infra.get('http2') else '❌'}",
        f"- **SSL 颁发机构**: {infra.get('ssl_issuer', 'N/A')}",
        "",
    ]

    # Performance
    perf = data.get("performance", {})
    lines += [
        "### 性能",
        "",
        f"| 指标 | 实测值 | 建议上限 |",
        f"|------|--------|----------|",
        f"| TTFB | {perf.get('ttfb_s', 'N/A')}s | 0.8s |",
        f"| 总加载时间 | {perf.get('total_s', 'N/A')}s | 3.0s |",
        f"| HTML 体积 | {perf.get('html_size_kb', 'N/A')} KB | 100 KB |",
        f"| CSS 文件数 | {perf.get('css_count', 'N/A')} | ≤10 |",
        f"| JS 文件数 | {perf.get('js_count', 'N/A')} | ≤10 |",
        f"| 图片数量 | {perf.get('img_count', 'N/A')} | — |",
        "",
    ]

    # SEO
    seo = data.get("seo", {})
    lines += [
        "### SEO",
        "",
        f"| 检查项 | 状态 |",
        f"|--------|------|",
        f"| Title 标签 | {'✅ ' + repr(seo['title'][:50]) if seo.get('title') else '❌ 缺失'} |",
        f"| Meta Description | {'✅ 已配置' if seo.get('meta_description') else '❌ 缺失'} |",
        f"| H1 标签 | {'✅ ' + str(seo.get('h1_count')) + ' 个' if seo.get('h1_count', 0) == 1 else ('⚠️ ' + str(seo.get('h1_count', 0)) + ' 个') if seo.get('h1_count', 0) > 1 else '❌ 缺失'} |",
        f"| 图片 Alt 属性 | {'❌ ' + str(seo.get('img_missing_alt', 0)) + '/' + str(seo.get('img_total', 0)) + ' 缺失' if seo.get('img_missing_alt', 0) > 0 else '✅ 全部配置'} |",
        f"| Open Graph | {'✅' if seo.get('og_tags') else '❌ 缺失'} |",
        f"| Twitter Card | {'✅' if seo.get('twitter_card') else '❌ 缺失'} |",
        f"| Schema.org | {'✅' if seo.get('schema_org') else '❌ 缺失'} |",
        f"| Sitemap | {'✅ ' + seo.get('sitemap_url', '') if seo.get('sitemap_found') else '❌ 未找到'} |",
        f"| robots.txt | {'✅' if seo.get('robots_found') else '❌ 未找到'} |",
        "",
    ]

    # Security
    sec = data.get("security", {})
    lines += ["### 安全性", ""]
    present = sec.get("headers_present", {})
    missing = sec.get("headers_missing", [])
    for h in ["strict-transport-security", "content-security-policy",
              "x-frame-options", "x-content-type-options",
              "referrer-policy", "permissions-policy"]:
        status = "✅ 已配置" if h in present else "❌ 缺失"
        lines.append(f"- **{h}**: {status}")
    lines.append("")

    # Content
    content = data.get("content", {})
    lines += ["### 内容质量", ""]
    ph = content.get("placeholder_found", [])
    if ph:
        lines.append(f"- ❌ **占位符文本**: 发现 {len(ph)} 种模式 (`{', '.join(ph[:3])}`)")
    else:
        lines.append("- ✅ **占位符文本**: 未检测到")
    emails = content.get("emails_found", [])
    if len(emails) > 1:
        lines.append(f"- ⚠️ **邮箱一致性**: 发现多个邮箱 `{', '.join(emails)}`")
    elif emails:
        lines.append(f"- ✅ **邮箱**: `{emails[0]}`")
    broken = content.get("broken_links", [])
    if broken:
        lines.append(f"- ❌ **死链**: {len(broken)} 个")
        for b in broken[:5]:
            lines.append(f"  - `{b['url']}` → HTTP {b['status']}")
    else:
        lines.append("- ✅ **死链**: 未检测到（抽样前 20 条内链）")
    lines.append("")

    # All issues
    lines += ["---", "", "## 三、问题清单（按严重程度）", ""]
    for sev in ("CRITICAL", "HIGH", "MEDIUM", "WARNING"):
        sev_issues = [i for i in issues if i["issue"].startswith(sev)]
        if sev_issues:
            lines.append(f"### {SEVERITY_EMOJI.get(sev, '')} {sev}")
            for i in sev_issues:
                lines.append(f"- **[{DIMENSION_LABELS.get(i['dimension'], i['dimension'])}]** {i['issue'].split(':', 1)[-1].strip()}")
            lines.append("")

    lines += [
        "---",
        "",
        f"*报告由 website-testing skill 自动生成 · 第一性原理驱动*",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("json_path", help="Path to audit JSON file")
    parser.add_argument("--format", choices=["md", "txt"], default="md")
    parser.add_argument("--output", help="Output file path (default: stdout)")
    args = parser.parse_args()

    with open(args.json_path, encoding="utf-8") as f:
        data = json.load(f)

    result = fmt_md(data)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(result)


if __name__ == "__main__":
    main()
