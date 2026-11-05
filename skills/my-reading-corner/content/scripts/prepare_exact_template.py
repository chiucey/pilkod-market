#!/usr/bin/env python3
"""Extract the exact Weread Atlas design and keep only approved static modules."""

from __future__ import annotations

import argparse
import base64
import json
import re
from pathlib import Path


YEAR_CLIPS = {
    "clip-4-lamp.png": "clip-4-lamp.png",
    "clip-3-magnifier.png": "clip-3-magnifier.png",
    "clip-9-journal.png": "clip-9-journal.png",
    "clip-2-book-stack.png": "clip-2-book-stack.png",
    "clip-7-cup.png": "clip-8-candle.png",
    "clip-12-coffee.png": "clip-1-woman-reading.png",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Original index.html")
    parser.add_argument("--assets", required=True, help="Original demos/assets folder")
    parser.add_argument("--output", required=True, help="Sanitized exact template")
    return parser.parse_args()


def data_uri(path: Path) -> str:
    suffix = path.suffix.lower()
    mime = "image/png" if suffix == ".png" else "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"Expected source fragment is missing: {old[:90]}")
    return text.replace(old, new, 1)


def replace_regex_once(text: str, pattern: str, replacement: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1)
    if count != 1:
        raise ValueError(f"Expected source pattern is missing: {pattern[:90]}")
    return updated


def main() -> None:
    args = parse_args()
    source = Path(args.source).expanduser().resolve()
    assets_dir = Path(args.assets).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    html = source.read_text(encoding="utf-8")

    html = replace_once(
        html,
        '<script src="mock-data.js"></script>',
        '<script>window.MOCK = __ATLAS_DATA_JSON__;</script>',
    )

    for image_path in sorted(assets_dir.glob("*.png")):
        html = html.replace(
            f"demos/assets/{image_path.name}",
            data_uri(image_path),
        )

    asset_map = {}
    for filename, source_filename in YEAR_CLIPS.items():
        path = assets_dir / source_filename
        if not path.exists():
            raise FileNotFoundError(path)
        asset_map[filename] = data_uri(path)
    asset_script = (
        "<script>window.ATLAS_ASSETS="
        + json.dumps(asset_map, ensure_ascii=False, separators=(",", ":"))
        + ";</script>"
    )
    html = replace_once(
        html,
        '<script>window.MOCK = __ATLAS_DATA_JSON__;</script>',
        '<script>window.MOCK = __ATLAS_DATA_JSON__;</script>\n' + asset_script,
    )

    html = html.replace(
        'src="${y.clip}"',
        'src="${window.ATLAS_ASSETS[y.clip] || y.clip || \'\'}"',
    )
    html = html.replace(
        'src="demos/assets/${y.clip}"',
        'src="${window.ATLAS_ASSETS[y.clip] || y.clip || \'\'}"',
    )

    html = replace_regex_once(
        html,
        r'(<p class="cc-sub" id="hero-sub">)[\s\S]*?(</p>)',
        r"\1阅读数据载入后，这里会显示你的总时长、阅读日、笔记和书籍。\2",
    )
    html = replace_regex_once(
        html,
        r'(<section class="section paper" id="sec-ai">[\s\S]*?<div class="sh-title">)[\s\S]*?(</div>)',
        r"\1MCode 根据你的真实阅读数据，生成一份静态阅读侧写。\2",
    )
    html = replace_regex_once(
        html,
        r'(<section class="section paper" id="sec-ai">[\s\S]*?<div class="sh-sub">)[\s\S]*?(</div>)',
        r"\1它会综合分类、作者、阅读时长和代表性划线，整理出你的阅读特征。\2",
    )
    html = replace_regex_once(
        html,
        r'(<section class="section paper" id="sec-themes">[\s\S]*?<div class="sh-title">)[\s\S]*?(</div>)',
        r"\1把这些年的代表性划线放在一起，看看反复出现的主题。\2",
    )
    html = replace_regex_once(
        html,
        r'(<footer class="footer">[\s\S]*?<div class="ft-title">)[\s\S]*?(</div>)',
        r"\1How this was made<br>with <em>WeRead</em> × <em>MCode</em>.\2",
    )
    html = replace_regex_once(
        html,
        r'(<footer class="footer">[\s\S]*?<p class="ft-sub">)[\s\S]*?(</p>)',
        r"\1MCode 读取你的微信读书数据，再按固定模板生成这份个人阅读网页。\2",
    )
    html = html.replace(
        "微信读书真实阅读记录 · weread-exporter 抓取 · DeepSeek 分析侧写",
        "微信读书真实阅读记录 · WeRead Skill 读取 · MCode 静态分析",
    )

    # Keep the original visual system while removing modules the Skill does not offer.
    html = replace_regex_once(
        html,
        r'\n<!-- ============== Section 2: 365 天热力图 ============== -->'
        r'[\s\S]*?</section>\n',
        "\n",
    )
    html = replace_regex_once(
        html,
        r'\n<!-- ============== Section 3\.5:[\s\S]*?</section>\n',
        "\n",
    )
    html = replace_once(html, '  <div class="ai-recs" id="ai-recs"></div>\n', "")
    html = replace_once(html, '  <div class="ai-chat" id="ai-chat"></div>\n', "")

    # The second cover card keeps its position and style, but now opens the trends module.
    html = replace_once(
        html,
        '<div class="cb-num">06</div>',
        '<div class="cb-num" id="cb-1-num">00</div>',
    )
    html = replace_once(html, 'data-target="sec-heatmap"', 'data-target="sec-trends"')
    html = replace_once(
        html,
        '<div class="cb-label">天 · 一年一格</div>',
        '<div class="cb-label">条 · 阅读趋势</div>',
    )
    html = replace_once(
        html,
        "  // cb-2: 365 天热力图 mini (随机 7×12)\n"
        "  (function renderMiniHeatmap() {",
        "  // cb-2: 阅读时长趋势 mini\n"
        "  (function renderMiniTrends() {",
    )
    html = replace_regex_once(
        html,
        r"  // cb-2: 阅读时长趋势 mini\n"
        r"  \(function renderMiniTrends\(\) \{[\s\S]*?"
        r"  \}\)\(\);\n"
        r"  // cb-3:",
        """  // cb-2: 阅读时长趋势 mini
  (function renderMiniTrends() {
    const stats = M.yearStats || [];
    const max = Math.max(1, ...stats.map(item => item.hours || 0));
    const W = 220, H = 88, pad = 12;
    const step = stats.length > 1 ? (W - pad * 2) / (stats.length - 1) : 0;
    const points = stats.map((item, index) => {
      const x = pad + index * step;
      const y = H - pad - ((item.hours || 0) / max) * (H - pad * 2);
      return { x, y, year: item.year };
    });
    let svg = `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;display:block">`;
    if (points.length) {
      svg += `<polyline points="${points.map(p => `${p.x},${p.y}`).join(' ')}" fill="none" stroke="#1a1a1a" stroke-width="3"/>`;
      points.forEach(point => {
        svg += `<circle cx="${point.x}" cy="${point.y}" r="5" fill="#6b4c8f" stroke="#1a1a1a" stroke-width="1"/>`;
      });
    }
    svg += `</svg>`;
    document.getElementById('cb-mini-2').innerHTML = svg;
  })();
  // cb-3:""",
    )
    html = replace_once(
        html,
        "document.getElementById('cb-2-num').textContent = M.heatmapStats.readDays;",
        "document.getElementById('cb-2-num').textContent = '04';",
    )
    html = replace_once(
        html,
        "M.years.slice().reverse().slice(0, 5).map(y => `",
        "M.years.slice(0, 5).reverse().map(y => `",
    )

    # Year count, date range and all year-related headings follow the selected data.
    html = replace_once(
        html,
        '<div class="sh-eyebrow">FIG. A · 6 YEARS IN BOOKS · 2021—2026</div>',
        '<div class="sh-eyebrow" id="years-eyebrow"></div>',
    )
    html = replace_once(
        html,
        '<div class="sh-title">六年的你， 每一本是一帧。</div>',
        '<div class="sh-title" id="years-title"></div>',
    )
    html = replace_once(
        html,
        '<div class="sh-sub">从 2021 到 2026， 每年挑出最难忘的几本， 用你当年的颜色拼回去。 6 年， 6 种色， 6 个你。</div>',
        '<div class="sh-sub" id="years-sub"></div>',
    )
    html = replace_once(
        html,
        '<div class="sh-eyebrow">FIG. B · 6-YEAR PANORAMA · 4 TREND LINES</div>',
        '<div class="sh-eyebrow" id="trends-eyebrow"></div>',
    )
    html = replace_once(
        html,
        '<div class="sh-title">六年， 浓缩成 4 条线。</div>',
        '<div class="sh-title" id="trends-title"></div>',
    )
    html = replace_once(
        html,
        '<div class="sh-sub">把 6 年压成一屏—— 一年一本， 一年一小时， 一年一类， 一年一个词。 你的阅读曲线， 你的认知曲线。</div>',
        '<div class="sh-sub" id="trends-sub"></div>',
    )
    html = replace_once(
        html,
        '<div class="trend-num">06<span style="font-size: 16px; opacity: 0.6"> 词</span></div>',
        '<div class="trend-num"><span id="trend-d-num">0</span><span style="font-size: 16px; opacity: 0.6"> 词</span></div>',
    )
    html = replace_once(html, '  <div class="heatmaps6y" id="heatmaps6y"></div>\n', "")
    html = replace_once(
        html,
        "  const M = window.MOCK;\n",
        """  const M = window.MOCK;
  const yearCount = M.years.length;
  const range = M.meta.range;
  const firstYear = Math.min(...M.years.map(y => y.year));
  const lastYear = Math.max(...M.years.map(y => y.year));
  const chineseNumbers = ['零','一','二','三','四','五','六','七','八','九','十'];
  const yearWord = chineseNumbers[yearCount] || String(yearCount);
  const englishYearWord = yearCount === 1 ? 'YEAR' : 'YEARS';
  document.getElementById('cb-1-num').textContent = String(yearCount).padStart(2, '0');
  document.getElementById('years-eyebrow').textContent = `FIG. A · ${yearCount} ${englishYearWord} IN BOOKS · ${range}`;
  document.getElementById('years-title').textContent = `${yearWord}年的你， 每一本是一帧。`;
  document.getElementById('years-sub').textContent = yearCount === 1
    ? `${firstYear} 的代表书和阅读记录，都放进这一张年度卡片里。`
    : `从 ${firstYear} 到 ${lastYear}， 每年挑出最难忘的几本， 用当年的颜色拼回去。 ${yearCount} 年， ${yearCount} 个阅读切片。`;
  document.getElementById('trends-eyebrow').textContent = `FIG. B · ${yearCount}-YEAR PANORAMA · 4 TREND LINES`;
  document.getElementById('trends-title').textContent = `${yearWord}年， 浓缩成 4 条线。`;
  document.getElementById('trends-sub').textContent = `把 ${yearCount} 年压成一屏—— 每年的本数、时长、分类和关键词都在这里。`;
  document.getElementById('trend-d-num').textContent = yearCount;
""",
    )

    # Make all four trend panels safe for one year and readable for longer histories.
    html = replace_once(
        html,
        "    const xStep = (W - padX * 2) / (years.length - 1);\n"
        "    const xFor = (i) => padX + i * xStep;",
        "    const xStep = years.length > 1 ? (W - padX * 2) / (years.length - 1) : 0;\n"
        "    const xFor = (i) => years.length > 1 ? padX + i * xStep : W / 2;",
    )
    html = replace_once(
        html,
        "    const aMax = Math.max(...stats.map(s => s.books)) * 1.15;",
        "    const aMax = Math.max(1, ...stats.map(s => s.books)) * 1.15;",
    )
    html = replace_once(
        html,
        "    const bMax = Math.max(...stats.map(s => s.hours)) * 1.1;",
        "    const bMax = Math.max(1, ...stats.map(s => s.hours)) * 1.1;",
    )
    html = replace_once(
        html,
        "    const maxH = Math.max(...Object.values(hoursByYear));",
        "    const maxH = Math.max(1, ...Object.values(hoursByYear));",
    )
    html = replace_once(
        html,
        "    stats.forEach((s, i) => {\n"
        "      const x = xFor(i) - 18;",
        "    const barWidth = Math.max(14, Math.min(36, ((W - padX * 2) / Math.max(stats.length, 1)) * 0.55));\n"
        "    stats.forEach((s, i) => {\n"
        "      const x = xFor(i) - barWidth / 2;",
    )
    html = replace_once(html, 'width="36" height="${h}"', 'width="${barWidth}" height="${h}"')
    html = html.replace("截至 7 月已", "截至目前已")
    html = replace_once(
        html,
        "    document.getElementById('trend-a-label').textContent = `${aPeak.year} 年峰值 ${aPeak.books} 本（${aPeakCat}年）， ${aPartial.year} 截至目前已 ${aPartial.books} 本。`;",
        "    document.getElementById('trend-a-label').textContent = stats.length === 1 ? `${aPeak.year} 共读 ${aPeak.books} 本，主要分类为${aPeakCat}。` : `${aPeak.year} 年峰值 ${aPeak.books} 本（${aPeakCat}年）， ${aPartial.year} 截至目前已 ${aPartial.books} 本。`;",
    )
    html = replace_once(
        html,
        "    document.getElementById('trend-b-label').textContent = `${bTrough.year} 谷底 ${bTrough.hours}h， ${bPeak.year} 反弹 ${bPeak.hours}h， ${bPartial.year} 截至目前已 ${bPartial.hours}h。`;",
        "    document.getElementById('trend-b-label').textContent = stats.length === 1 ? `${bPeak.year} 共阅读 ${bPeak.hours} 小时。` : `${bTrough.year} 谷底 ${bTrough.hours}h， ${bPeak.year} 反弹 ${bPeak.hours}h， ${bPartial.year} 截至目前已 ${bPartial.hours}h。`;",
    )

    html = replace_regex_once(
        html,
        r"    // 每年每类估算：[\s\S]*?"
        r"    const cMax = Math\.max\(\.\.\.stats\.map\(s => s\.hours\)\) \* 1\.05;",
        """    // 按每年代表书的真实分类分配年度阅读时长；缺失时按总分类占比回退。
    const catH = {}; cats.forEach(c => catH[c.id] = Object.fromEntries(stats.map(s => [s.year, 0])));
    stats.forEach(s => {
      const totalH = s.hours;
      const yearData = M.years.find(y => y.year === s.year);
      const weights = {};
      (yearData?.books || []).forEach(book => {
        const categoryId = book.categoryId;
        if (catH[categoryId]) weights[categoryId] = (weights[categoryId] || 0) + Math.max(book.hours || 0, 1);
      });
      const weightTotal = Object.values(weights).reduce((sum, value) => sum + value, 0);
      if (weightTotal > 0) {
        Object.entries(weights).forEach(([categoryId, value]) => {
          catH[categoryId][s.year] = totalH * value / weightTotal;
        });
      } else {
        cats.forEach(category => {
          catH[category.id][s.year] = totalH * category.pct / 100;
        });
      }
    });
    const cMax = Math.max(1, ...stats.map(s => s.hours)) * 1.05;""",
    )
    html = replace_once(
        html,
        "    document.getElementById('trend-c-label').textContent = `6 年里 8 个分类的占比流变—— 2024 医学健康占主， 2026 文学回归。`;",
        "    document.getElementById('trend-c-label').textContent = `${yearCount} 年里 ${cats.length} 个分类的占比变化。`;",
    )
    html = replace_regex_once(
        html,
        r"    const moodWord = \{[\s\S]*?"
        r"    const hoursByYear = Object\.fromEntries\(stats\.map\(s => \[s\.year, s\.hours\]\)\);",
        """    const yearDetail = Object.fromEntries(M.years.map(year => [year.year, year]));
    const hoursByYear = Object.fromEntries(stats.map(s => [s.year, s.hours]));""",
    )
    html = replace_once(
        html,
        """      dHTML += `<div class="td-row">
        <span class="td-year">${s.year}</span>
        <span class="td-bar ${[2021,2022,2023,2025].includes(s.year) ? 'td-light' : ''}" style="--c: ${moodColor[s.year]}; width: ${w}%">${moodLabel[s.year]} · ${moodWord[s.year]}</span>
        <span style="font-family:'Special Elite';font-size:11px;opacity:0.7;width:50px;flex-shrink:0;text-align:right">${s.hours}h${s.partial ? '*' : ''}</span>
      </div>`;""",
        """      const detail = yearDetail[s.year] || {};
      const word = detail.sticker?.foot || 'READ';
      const label = detail.mood || '这一年';
      const color = detail.color || '#6b4c8f';
      dHTML += `<div class="td-row">
        <span class="td-year">${s.year}</span>
        <span class="td-bar td-light" style="--c: ${color}; width: ${w}%">${label} · ${word}</span>
        <span style="font-family:'Special Elite';font-size:11px;opacity:0.7;width:50px;flex-shrink:0;text-align:right">${s.hours}h${s.partial ? '*' : ''}</span>
      </div>`;""",
    )

    # The random six-year heatmap inside the trends module has no real data source.
    html = replace_regex_once(
        html,
        r"\n  // ============== 6 年 6 色迷你热力图 ==============\n"
        r"[\s\S]*?"
        r"\n  // ============== Section 1: 4 年份块 ==============",
        "\n  // ============== Section 1: 年份块 ==============",
    )

    # Remove runtime code for the deleted heatmap and companion modules.
    html = replace_regex_once(
        html,
        r"  // ============== Section 2: 365 天热力图 ==============\n"
        r"[\s\S]*?"
        r"  // ============== Section 3\.7:",
        "  // ============== Section 3.7:",
    )
    html = replace_regex_once(
        html,
        r"  // ============== Section 3\.5:[\s\S]*?"
        r"  // ============== Section 3: AI 阅读侧写 ==============",
        "  // ============== Section 3: AI 阅读侧写 ==============",
    )

    # Keep the static AI profile only. Recommendations and chat controls are excluded.
    html = replace_regex_once(
        html,
        r"(  // ============== Section 3: AI 阅读侧写 =============="
        r"[\s\S]*?document\.getElementById\('ai-wrap'\)\.innerHTML = aiHTML;)"
        r"[\s\S]*?"
        r"(\n  \}\)\(\);\n\n  // ============== Section 4:)",
        r"\1\2",
    )

    # Remove the unused heatmap tooltip runtime.
    html = replace_regex_once(
        html,
        r"\n  // ----- Heatmap Tooltip -----[\s\S]*?"
        r"\n  // ----- 作者网络 hover 联动 -----",
        "\n  // ----- 作者网络 hover 联动 -----",
    )
    html = replace_once(
        html,
        "document.querySelectorAll('.section-head, .heatmap-wrap, .heatmap-side, .ai-wrap, .ai-recs, .ai-chat, .network-wrap, .capsule-wrap, .footer')",
        "document.querySelectorAll('.section-head, .ai-wrap, .network-wrap, .capsule-wrap, .footer')",
    )

    # Renumber the remaining six sections without changing their visual treatment.
    for section_id, number in (
        ("sec-ai", "03"),
        ("sec-themes", "04"),
        ("sec-network", "05"),
        ("sec-capsule", "06"),
    ):
        html = replace_regex_once(
            html,
            rf'(<section class="section paper" id="{section_id}">[\s\S]*?<div class="sh-num">)\d\d(</div>)',
            rf"\g<1>{number}\2",
        )

    if re.search(r"wrk-[A-Za-z0-9_-]{8,}|WEREAD_API_KEY\s*=", html):
        raise ValueError("Secret residue remains in the prepared template")
    if "__ATLAS_DATA_JSON__" not in html:
        raise ValueError("Data placeholder missing")
    for forbidden in (
        'id="sec-heatmap"',
        'id="sec-companion"',
        'id="ai-recs"',
        'id="ai-chat"',
        'id="companion-input"',
        'id="chat-input"',
    ):
        if forbidden in html:
            raise ValueError(f"Removed module residue remains: {forbidden}")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    print(f"Prepared exact template: {output}")


if __name__ == "__main__":
    main()
