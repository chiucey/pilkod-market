#!/usr/bin/env python3
"""
pptx_build.py
将设计好的JSON内容转换为专业PPT文件
融合《演说之禅》+ 高桥流简洁法
"""
import sys
import json
import os
import re
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu

# ============ 配色方案 ============
STYLE_COLORS = {
    "商务专业": {"primary": "1e3a5f", "secondary": "2563eb", "accent": "f59e0b", "light": "dbeafe", "bg": "f8fafc"},
    "学术严谨": {"primary": "1e293b", "secondary": "475569", "accent": "0891b2", "light": "e0f2fe", "bg": "f1f5f9"},
    "活泼教学": {"primary": "7c3aed", "secondary": "2563eb", "accent": "f59e0b", "light": "ede9fe", "bg": "f5f3ff"},
    "中国古典": {"primary": "7c3aed", "secondary": "dc2626", "accent": "f59e0b", "light": "fef3c7", "bg": "faf4ed"},
    "简约现代": {"primary": "0f172a", "secondary": "64748b", "accent": "e11d48", "light": "f1f5f9", "bg": "ffffff"},
}

def hex_to_rgb(h):
    h = h.lstrip('#')
    return RGBColor(int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))

def add_slide_background(slide, color_hex):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = hex_to_rgb(color_hex)

def set_text_style(text_frame, font_size, font_name, color_rgb, bold=False, align=PP_ALIGN.LEFT):
    for para in text_frame.paragraphs:
        para.alignment = align
        for run in para.runs:
            run.font.size = Pt(font_size)
            run.font.name = font_name
            run.font.color.rgb = color_rgb
            run.font.bold = bold

# ========== 封面页 ==========
def make_cover(slide, data, theme):
    add_slide_background(slide, theme["primary"])
    shapes = slide.shapes

    # 装饰线
    line = shapes.add_shape(1, Inches(0), Inches(2.4), Inches(10), Inches(0.03))
    line.fill.solid(); line.fill.fore_color.rgb = hex_to_rgb(theme["accent"])
    line.line.fill.background()

    line2 = shapes.add_shape(1, Inches(0), Inches(3.8), Inches(10), Inches(0.03))
    line2.fill.solid(); line2.fill.fore_color.rgb = hex_to_rgb(theme["accent"])
    line2.line.fill.background()

    # 主标题
    title_box = shapes.add_textbox(Inches(0.5), Inches(2.6), Inches(9), Inches(1.2))
    tf = title_box.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    run = p.add_run(); run.text = data.get("title", "")
    run.font.size = Pt(54); run.font.name = "Microsoft YaHei"
    run.font.color.rgb = RGBColor(255,255,255); run.font.bold = True

    # 副标题
    sub_box = shapes.add_textbox(Inches(0.5), Inches(4.0), Inches(9), Inches(0.6))
    tf2 = sub_box.text_frame
    p2 = tf2.paragraphs[0]; p2.alignment = PP_ALIGN.CENTER
    run2 = p2.add_run(); run2.text = data.get("subtitle", "")
    run2.font.size = Pt(22); run2.font.name = "Microsoft YaHei"
    run2.font.color.rgb = hex_to_rgb(theme["light"])

# ========== 目录页 ==========
def make_toc(slide, data, theme):
    add_slide_background(slide, theme["bg"])
    shapes = slide.shapes

    # 标题
    title_box = shapes.add_textbox(Inches(0.5), Inches(0.4), Inches(9), Inches(0.8))
    tf = title_box.text_frame
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    run = p.add_run(); run.text = "目录"
    run.font.size = Pt(40); run.font.name = "Microsoft YaHei"
    run.font.color.rgb = hex_to_rgb(theme["primary"]); run.font.bold = True

    # 装饰线
    line = shapes.add_shape(1, Inches(3), Inches(1.2), Inches(4), Inches(0.04))
    line.fill.solid(); line.fill.fore_color.rgb = hex_to_rgb(theme["accent"])
    line.line.fill.background()

    items = data.get("items", [])
    colors_list = [theme["primary"], theme["secondary"], theme["accent"]]
    for i, item in enumerate(items[:5]):
        y = 1.6 + i * 0.75
        # 序号圆
        num_circle = shapes.add_shape(9, Inches(1), Inches(y), Inches(0.5), Inches(0.5))
        num_circle.fill.solid(); num_circle.fill.fore_color.rgb = hex_to_rgb(colors_list[i % 3])
        num_circle.line.fill.background()
        tf = num_circle.text_frame; tf.paragraphs[0].alignment = PP_ALIGN.CENTER
        run = tf.paragraphs[0].add_run(); run.text = str(i+1)
        run.font.size = Pt(16); run.font.name = "Arial"
        run.font.color.rgb = RGBColor(255,255,255); run.font.bold = True

        # 文字
        txt_box = shapes.add_textbox(Inches(1.7), Inches(y+0.05), Inches(7), Inches(0.45))
        tf2 = txt_box.text_frame
        p2 = tf2.paragraphs[0]
        run2 = p2.add_run(); run2.text = item
        run2.font.size = Pt(18); run2.font.name = "Microsoft YaHei"
        run2.font.color.rgb = hex_to_rgb(theme["primary"]); run2.font.bold = True

    add_page_number(slide, data.get("page", 2), theme)

# ========== 内容页 ==========
def make_content(slide, data, theme):
    add_slide_background(slide, "FFFFFF")
    shapes = slide.shapes

    # 顶部色带
    header = shapes.add_shape(1, Inches(0), Inches(0), Inches(10), Inches(0.08))
    header.fill.solid(); header.fill.fore_color.rgb = hex_to_rgb(theme["primary"])
    header.line.fill.background()

    # 左上角图标区
    icon_box = shapes.add_shape(1, Inches(0.4), Inches(0.3), Inches(0.6), Inches(0.6))
    icon_box.fill.solid(); icon_box.fill.fore_color.rgb = hex_to_rgb(theme["accent"])
    icon_box.line.fill.background()

    # 标题（高桥流：一行大字）
    title_box = shapes.add_textbox(Inches(1.2), Inches(0.3), Inches(8.5), Inches(0.8))
    tf = title_box.text_frame
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.LEFT
    run = p.add_run(); run.text = data.get("title", "")
    run.font.size = Pt(36); run.font.name = "Microsoft YaHei"
    run.font.color.rgb = hex_to_rgb(theme["primary"]); run.font.bold = True

    # 内容区域
    body = data.get("body", "")
    content_box = shapes.add_textbox(Inches(0.5), Inches(1.4), Inches(6), Inches(3.2))
    tf2 = content_box.text_frame; tf2.word_wrap = True
    p2 = tf2.paragraphs[0]; p2.alignment = PP_ALIGN.LEFT
    run2 = p2.add_run(); run2.text = body
    run2.font.size = Pt(16); run2.font.name = "Microsoft YaHei"
    run2.font.color.rgb = hex_to_rgb("374151")

    # 高亮金句
    highlight = data.get("highlight", "")
    if highlight:
        highlight_box = shapes.add_shape(1, Inches(6.8), Inches(1.4), Inches(2.9), Inches(2.5))
        highlight_box.fill.solid(); highlight_box.fill.fore_color.rgb = hex_to_rgb(theme["light"])
        highlight_box.line.fill.background()

        label_box = shapes.add_textbox(Inches(7), Inches(1.55), Inches(2.5), Inches(0.4))
        tf3 = label_box.text_frame
        p3 = tf3.paragraphs[0]
        run3 = p3.add_run(); run3.text = "[ 金句 ]"
        run3.font.size = Pt(11); run3.font.name = "Microsoft YaHei"
        run3.font.color.rgb = hex_to_rgb(theme["accent"]); run3.font.bold = True

        content_box2 = shapes.add_textbox(Inches(7), Inches(2.0), Inches(2.5), Inches(1.8))
        tf4 = content_box2.text_frame; tf4.word_wrap = True
        p4 = tf4.paragraphs[0]; p4.alignment = PP_ALIGN.CENTER
        run4 = p4.add_run(); run4.text = highlight
        run4.font.size = Pt(14); run4.font.name = "Microsoft YaHei"
        run4.font.color.rgb = hex_to_rgb(theme["primary"]); run4.font.bold = True

    add_page_number(slide, data.get("page", 3), theme)

# ========== 总结页 ==========
def make_summary(slide, data, theme):
    add_slide_background(slide, theme["primary"])
    shapes = slide.shapes

    line = shapes.add_shape(1, Inches(0), Inches(2.2), Inches(10), Inches(0.04))
    line.fill.solid(); line.fill.fore_color.rgb = hex_to_rgb(theme["accent"]); line.line.fill.background()

    line2 = shapes.add_shape(1, Inches(0), Inches(3.8), Inches(10), Inches(0.04))
    line2.fill.solid(); line2.fill.fore_color.rgb = hex_to_rgb(theme["accent"]); line2.line.fill.background()

    title_box = shapes.add_textbox(Inches(0.5), Inches(2.45), Inches(9), Inches(1.2))
    tf = title_box.text_frame
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    run = p.add_run(); run.text = data.get("title", "")
    run.font.size = Pt(48); run.font.name = "Microsoft YaHei"
    run.font.color.rgb = RGBColor(255,255,255); run.font.bold = True

    cta = data.get("call_to_action", "")
    if cta:
        cta_box = shapes.add_textbox(Inches(0.5), Inches(4.1), Inches(9), Inches(0.6))
        tf2 = cta_box.text_frame
        p2 = tf2.paragraphs[0]; p2.alignment = PP_ALIGN.CENTER
        run2 = p2.add_run(); run2.text = cta
        run2.font.size = Pt(20); run2.font.name = "Microsoft YaHei"
        run2.font.color.rgb = hex_to_rgb(theme["light"])

    add_page_number(slide, data.get("page", 8), theme)

# ========== 页码 ==========
def add_page_number(slide, page_num, theme):
    shapes = slide.shapes
    num_circle = shapes.add_shape(9, Inches(9.3), Inches(5.1), Inches(0.4), Inches(0.4))
    num_circle.fill.solid(); num_circle.fill.fore_color.rgb = hex_to_rgb(theme["accent"])
    num_circle.line.fill.background()
    tf = num_circle.text_frame; tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    run = tf.paragraphs[0].add_run(); run.text = str(page_num)
    run.font.size = Pt(11); run.font.name = "Arial"
    run.font.color.rgb = RGBColor(255,255,255); run.font.bold = True

# ========== 主函数 ==========
def build_pptx(json_path, style="活泼教学"):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    slides_data = data.get("slides", [])
    meta = data.get("meta", {})
    topic = meta.get("topic", "演示")

    prs = Presentation()
    prs.slide_width = Inches(10); prs.slide_height = Inches(5.625)

    theme = STYLE_COLORS.get(style, STYLE_COLORS["活泼教学"])

    slide_makers = {
        "cover": make_cover,
        "toc": make_toc,
        "content": make_content,
        "summary": make_summary,
    }

    for s in slides_data:
        blank_layout = prs.slide_layouts[6]
        slide = prs.slides.add_slide(blank_layout)
        stype = s.get("type", "content")
        maker = slide_makers.get(stype, make_content)
        maker(slide, s, theme)

    output_dir = os.path.expanduser("~/reading-writing-project/output")
    os.makedirs(output_dir, exist_ok=True)
    safe_name = re.sub(r'[^\w\-]', '_', topic)[:30]
    output_path = os.path.join(output_dir, f"演示_{safe_name}.pptx")
    prs.save(output_path)
    return output_path

def main():
    if len(sys.argv) < 2:
        print("用法: python3 pptx_build.py <JSON文件路径> [风格]")
        print("示例: python3 pptx_build.py ~/reading-writing-project/output/ppt_content_山海经.json 活泼教学")
        sys.exit(1)

    json_path = sys.argv[1]
    style = sys.argv[2] if len(sys.argv) > 2 else "活泼教学"

    if not os.path.exists(json_path):
        print(f"❌ 文件不存在: {json_path}")
        sys.exit(1)

    print(f"🎨 使用风格: {style}")
    print(f"📄 正在读取: {json_path}")
    output = build_pptx(json_path, style)
    print(f"✅ PPT已生成: {output}")

if __name__ == "__main__":
    main()