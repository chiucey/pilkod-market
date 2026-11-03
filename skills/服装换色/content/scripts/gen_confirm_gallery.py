#!/usr/bin/env python3
"""
gen_confirm_gallery.py — 生成换色选区确认画廊页面

用法：
    echo '<JSON>' | python3 gen_confirm_gallery.py
    python3 gen_confirm_gallery.py < data.json

输入 JSON 结构：
{
  "images": ["/abs/path/img1.jpg", ...],
  "change_items": [
    {
      "name": "黑色高腰运动短裙",
      "current_hex": "#1a1a1a",
      "current_name": "黑色",
      "warning": null          // 或 "与腰带同色系，建议一起换色"
    }
  ],
  "target_colors": [
    {"hex": "#228B22", "name": "森林绿"},
    {"hex": "#8B1A1A", "name": "枣红色"}
  ],
  "preserve_items": ["版型/裙长", "松紧带/抽绳", "模特姿势", "背景"]
}

输出（stdout）：canvas ID，例如 fuzhuang-confirm-1746000000
生成文件：/root/.openclaw/canvas/documents/<canvas_id>/index.html
"""

import json
import sys
import os
import shutil
import time
from pathlib import Path


def h(s: str) -> str:
    """HTML-escape a string."""
    return (str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def build_html(data: dict, image_filenames: list[str]) -> str:
    # ── Images row ──────────────────────────────────────────────────────────
    images_html = ""
    for i, fname in enumerate(image_filenames):
        images_html += f"""
        <div class="image-thumb">
          <img src="./{h(fname)}" alt="图片 {i+1}" loading="lazy">
          <div class="image-label">图片 {i+1}</div>
        </div>"""

    # ── Change items ─────────────────────────────────────────────────────────
    target_colors = data.get("target_colors", [])
    change_items_html = ""
    for item in data.get("change_items", []):
        name      = h(item.get("name", ""))
        cur_hex   = h(item.get("current_hex", "#cccccc"))
        cur_name  = h(item.get("current_name", ""))
        warning   = item.get("warning")

        warning_html = (
            f'<span class="warning-badge">⚠️ {h(warning)}</span>'
            if warning else ""
        )

        # target swatches (one per target color)
        target_swatches = "".join(
            f'<div class="swatch" style="background:{h(tc["hex"])}" title="{h(tc["hex"])}"></div>'
            for tc in target_colors
        )

        change_items_html += f"""
        <div class="change-item">
          <div class="item-info">
            <div class="item-name">{name}</div>
            {warning_html}
          </div>
          <div class="color-flow">
            <div class="color-col">
              <div class="swatch" style="background:{cur_hex}" title="{cur_hex}"></div>
              <div class="swatch-label">{cur_name}</div>
            </div>
            <div class="arrow-icon">→</div>
            <div class="multi-targets">{target_swatches}</div>
          </div>
        </div>"""

    # ── Target color cards ───────────────────────────────────────────────────
    target_cards_html = ""
    for tc in target_colors:
        hex_val = h(tc.get("hex", "#cccccc"))
        name    = h(tc.get("name", ""))
        target_cards_html += f"""
          <div class="target-color-card">
            <div class="target-swatch" style="background:{hex_val}"></div>
            <div class="target-name">{name}</div>
            <div class="target-hex">{hex_val}</div>
          </div>"""

    # ── Preserve tags ────────────────────────────────────────────────────────
    preserve_html = "".join(
        f'<div class="preserve-tag">{h(item)}</div>'
        for item in data.get("preserve_items", [])
    )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>换色选区确认</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Helvetica Neue', sans-serif;
      background: #f7f8fa;
      padding: 16px;
      color: #1a1a1a;
      font-size: 14px;
    }}

    /* ── Header ── */
    .header {{
      font-size: 17px;
      font-weight: 700;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    /* ── Image row ── */
    .images-row {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-bottom: 14px;
    }}
    .image-thumb {{
      border-radius: 10px;
      overflow: hidden;
      box-shadow: 0 2px 10px rgba(0,0,0,0.13);
      background: #fff;
      flex-shrink: 0;
    }}
    .image-thumb img {{
      display: block;
      width: 130px;
      height: 130px;
      object-fit: cover;
    }}
    .image-label {{
      font-size: 11px;
      color: #888;
      text-align: center;
      padding: 4px 6px;
    }}

    /* ── Section card ── */
    .section {{
      background: #fff;
      border-radius: 12px;
      padding: 14px 16px;
      margin-bottom: 12px;
      box-shadow: 0 1px 5px rgba(0,0,0,0.07);
    }}
    .section-title {{
      font-size: 12px;
      font-weight: 600;
      color: #888;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      margin-bottom: 12px;
    }}

    /* ── Change items ── */
    .change-item {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 9px 0;
      border-bottom: 1px solid #f2f2f2;
    }}
    .change-item:last-child {{ border-bottom: none; padding-bottom: 0; }}
    .item-info {{ flex: 1; min-width: 0; }}
    .item-name {{
      font-size: 14px;
      font-weight: 500;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .warning-badge {{
      display: inline-block;
      font-size: 11px;
      color: #d97706;
      background: #fef3c7;
      border-radius: 4px;
      padding: 2px 7px;
      margin-top: 4px;
    }}

    /* ── Color flow ── */
    .color-flow {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex-shrink: 0;
    }}
    .color-col {{
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 2px;
    }}
    .swatch {{
      width: 30px;
      height: 30px;
      border-radius: 7px;
      border: 1px solid rgba(0,0,0,0.1);
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }}
    .swatch-label {{
      font-size: 10px;
      color: #aaa;
      text-align: center;
      max-width: 40px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .multi-targets {{
      display: flex;
      gap: 5px;
      flex-wrap: wrap;
      max-width: 120px;
    }}
    .arrow-icon {{
      color: #ccc;
      font-size: 18px;
      line-height: 1;
    }}

    /* ── Target colors ── */
    .target-colors {{
      display: flex;
      gap: 14px;
      flex-wrap: wrap;
    }}
    .target-color-card {{
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 5px;
    }}
    .target-swatch {{
      width: 48px;
      height: 48px;
      border-radius: 12px;
      border: 1px solid rgba(0,0,0,0.1);
      box-shadow: 0 3px 8px rgba(0,0,0,0.12);
    }}
    .target-name {{
      font-size: 12px;
      color: #333;
      font-weight: 500;
    }}
    .target-hex {{
      font-size: 10px;
      color: #aaa;
      font-family: 'SF Mono', 'Fira Code', monospace;
    }}

    /* ── Preserve tags ── */
    .preserve-list {{
      display: flex;
      flex-wrap: wrap;
      gap: 7px;
    }}
    .preserve-tag {{
      background: #f0f0f0;
      border-radius: 6px;
      padding: 5px 11px;
      font-size: 13px;
      color: #555;
    }}

    /* ── Footer ── */
    .footer {{
      font-size: 12px;
      color: #aaa;
      text-align: center;
      margin-top: 4px;
      padding: 6px;
    }}
  </style>
</head>
<body>
  <div class="header">📋 换色选区确认</div>

  <!-- 原图缩略图 -->
  <div class="images-row">{images_html}
  </div>

  <!-- 将换色的项目 -->
  <div class="section">
    <div class="section-title">🎨 将换色的项目</div>{change_items_html}
  </div>

  <!-- 目标颜色 -->
  <div class="section">
    <div class="section-title">🎯 目标颜色</div>
    <div class="target-colors">{target_cards_html}
    </div>
  </div>

  <!-- 保留不变 -->
  <div class="section">
    <div class="section-title">🔒 保留不变的项目</div>
    <div class="preserve-list">{preserve_html}
    </div>
  </div>

  <div class="footer">以上换色范围是否正确？如需调整请直接告知，确认后立即执行。</div>
</body>
</html>"""


def main():
    data = json.load(sys.stdin)

    canvas_id  = f"fuzhuang-confirm-{int(time.time())}"
    canvas_dir = Path(f"/root/.openclaw/canvas/documents/{canvas_id}")
    canvas_dir.mkdir(parents=True, exist_ok=True)

    # 复制原图到 canvas 目录
    image_filenames: list[str] = []
    for i, img_path in enumerate(data.get("images", [])):
        if os.path.exists(img_path):
            ext   = Path(img_path).suffix.lower() or ".jpg"
            fname = f"img_{i}{ext}"
            shutil.copy2(img_path, canvas_dir / fname)
            image_filenames.append(fname)
        else:
            # 路径不存在时跳过，不阻断流程
            sys.stderr.write(f"[warn] image not found: {img_path}\n")

    # 生成并写入 HTML
    html = build_html(data, image_filenames)
    (canvas_dir / "index.html").write_text(html, encoding="utf-8")

    # 输出 canvas ID 供调用方使用
    print(canvas_id)


if __name__ == "__main__":
    main()
