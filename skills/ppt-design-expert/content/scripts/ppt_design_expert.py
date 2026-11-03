#!/usr/bin/env python3
"""
ppt_design_expert.py
PPT设计专家 - 融合《演说之禅》+ 金字塔原理 + 高桥流简洁法
自动生成专业演示文稿
"""
import sys
import json
import re
import os
import urllib.request
import ssl

# ============ 配置 ============
DEEPSEEK_API_KEY = "sk-7fc61eea4157402688bd3d4e75d391c2"
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

# ============ DeepSeek 调用 ============
def deepseek(prompt, temperature=0.6, max_tokens=3000):
    ctx = ssl._create_unverified_context()
    data = json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens
    }).encode()
    req = urllib.request.Request(DEEPSEEK_API_URL, data=data, headers={
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    })
    with urllib.request.urlopen(req, timeout=90, context=ctx) as resp:
        result = json.loads(resp.read())
    return result["choices"][0]["message"]["content"]

# ============ 交互式收集信息 ============
def ask(text):
    print(f"\n📋 {text}")
    return input("→ ").strip()

def choose_question(text, options):
    print(f"\n📋 {text}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    while True:
        try:
            sel = int(input("→ 选择编号: ").strip())
            if 1 <= sel <= len(options):
                return options[sel - 1]
        except ValueError:
            pass
        print("⚠️ 请输入有效编号")

# ============ 生成设计方案 ============
def generate_design_plan(topic, audience, goal, content, time_limit, style, material):
    prompt = f"""你是一位顶级商业演示设计专家，融合《演说之禅》简约哲学、麦肯锡金字塔原理、高桥流简洁法。

为以下演示任务生成完整设计方案：

【主题】
{topic}

【目标受众】
{audience}

【演示目标】
{goal}

【核心内容要点】
{content}

【时间/页数限制】
{time_limit}

【风格偏好】
{style}

【现有素材】
{material}

请按以下JSON格式输出（只输出JSON，不要任何其他文字）：
{{"design":{{"theme":"主题词","audience":"受众分析","goal":"核心目标"}},"structure":{{"core_conclusion":"封面核心结论（5秒内抓住注意力）","spokes":["主要论点1","主要论点2","主要论点3"],"spoke_details":[{{"spoke":"论点1","evidence":["支撑数据或案例1","支撑数据或案例2"],"story":"一个相关小故事或案例"]}},{{"spoke":"论点2","evidence":["支撑数据或案例1","支撑数据或案例2"],"story":"一个相关小故事或案例"]}},{{"spoke":"论点3","evidence":["支撑数据或案例1","支撑数据或案例2"],"story":"一个相关小故事或案例"]}}],"scqa":{{"situation":"背景设定（一句话）","complication":"冲突/问题","question":"核心问题","answer":"解决方案（核心结论）"}}},"slides":[{{"type":"cover","title":"封面标题","subtitle":"副标题","visual":"视觉建议"}}]}},"visual":{{"primary_color":"主色（hex不带#）","secondary_color":"辅色","accent_color":"强调色","font_main":"主字体","font_size_title":"标题字号","font_size_body":"正文字号","layout_principle":"核心布局原则","white_space":"留白比例建议"}}}}"""
    result = deepseek(prompt, temperature=0.5, max_tokens=3000)
    m = re.search(r"\{[\s\S]+?\}", result)
    if m:
        try:
            return json.loads(m.group())
        except:
            pass
    return None

# ============ 生成完整幻灯片内容 ============
def generate_slide_content(design_plan, slide_count=8):
    content_str = json.dumps(design_plan, ensure_ascii=False) if design_plan else "null"
    prompt = f"""你是一位顶级PPT内容设计专家。基于以下设计方案，为每个页面生成精确的文字内容。

设计方案：
{content_str}

【任务】
生成{slide_count}页幻灯片的完整内容（JSON数组格式）：

请按以下JSON数组格式输出（只输出JSON，不要任何其他文字）：
[
  {{
    "page": 1,
    "type": "cover",
    "title": "封面大标题（一行，极简有力）",
    "subtitle": "副标题",
    "speaker_notes": "演讲者备注：针对这个封面的开场白，建议20秒内完成"
  }},
  {{
    "page": 2,
    "type": "toc",
    "title": "议程",
    "items": ["论点一：标题","论点二：标题","论点三：标题"],
    "speaker_notes": "演讲者备注"
  }},
  {{
    "page": 3,
    "type": "content",
    "title": "一页一意的论点标题",
    "body": "核心内容：数据或案例支撑，2-3句话",
    "highlight": "高亮金句（一句话）",
    "icon": "视觉图标建议（英文单词）",
    "speaker_notes": "演讲者备注：停留30秒"
  }},
  ...继续生成第4到{slide_count}页...
  {{
    "page": {slide_count},
    "type": "summary",
    "title": "总结行动号召",
    "call_to_action": "核心行动（让听众做什么）",
    "speaker_notes": "演讲者备注"
  }}
]

【原则】（严格遵守）：
1. 封面结论前置，不说废话，直接告诉听众能得到什么
2. 每页只传达一个核心观点，不要堆砌信息
3. 语言精准有力，符合高桥流"一行大字"风格
4. 数据具体，案例真实
5. 演讲备注要像真实的演讲稿，不要像摘要
"""
    result = deepseek(prompt, temperature=0.6, max_tokens=3000)
    m = re.search(r"\[[\s\S]+\]", result)
    if m:
        try:
            return json.loads(m.group())
        except:
            pass
    return None

# ============ 主流程 ============
def main():
    print("=" * 55)
    print("PPT设计专家  v1.0")
    print("融合《演说之禅》+ 麦肯锡金字塔 + 高桥流简洁法")
    print("=" * 55)

    print("\n" + "="*55)
    print("Step 1：收集演示信息")
    print("="*55)

    topic = ask("演示主题是什么？（例如：小学四年级《山海经》课研汇报）")
    audience = ask("目标受众是谁？（例如：学校领导、家长、学生）")
    goal = ask("演示目标是什么？（例如：展示研究成果、说服领导拨款）")
    content_raw = ask("核心内容要点有哪些？（简要列出，分条输入）")
    time_limit = ask("时间/页数限制？（例如：10分钟，12页）")
    style = choose_question("风格偏好是什么？", [
        "商务专业", "学术严谨", "活泼教学", "中国古典", "简约现代"
    ])
    material = ask("现有素材？（没有则输入"无"，有则描述）")

    print("\n" + "="*55)
    print("Step 2：设计方案生成中...")
    print("="*55)
    print("🤖 正在分析任务，设计方案...")

    # 判断幻灯片数量
    slide_count = 8
    if "页" in time_limit:
        try:
            slide_count = int(re.search(r"(\d+)\s*页", time_limit).group(1))
        except:
            pass
    slide_count = min(max(slide_count, 6), 15)

    design_plan = generate_design_plan(topic, audience, goal, content_raw, time_limit, style, material)
    if design_plan:
        print("✅ 设计方案生成成功！")

    print("\n" + "="*55)
    print("Step 3：生成幻灯片内容...")
    print("="*55)
    print(f"🤖 正在生成 {slide_count} 页幻灯片内容...")

    slides = generate_slide_content(design_plan, slide_count)
    if not slides:
        print("❌ 内容生成失败，请重试")
        return

    print(f"✅ 幻灯片内容生成成功！共 {len(slides)} 页")

    # 保存JSON
    output_dir = os.path.expanduser("~/reading-writing-project/output")
    os.makedirs(output_dir, exist_ok=True)
    safe_name = re.sub(r'[^\w\-]', '_', topic)[:30]
    json_path = os.path.join(output_dir, f"ppt_content_{safe_name}.json")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "design": design_plan,
            "slides": slides,
            "meta": {
                "topic": topic,
                "audience": audience,
                "goal": goal,
                "style": style,
                "slide_count": len(slides)
            }
        }, f, ensure_ascii=False, indent=2)

    print(f"\n" + "="*55)
    print("✅ 完成！")
    print("="*55)
    print(f"📄 内容已保存: {json_path}")
    print(f"📝 共 {len(slides)} 页幻灯片内容")
    print(f"\n下一步：运行 `python3 scripts/pptx_build.py` 将内容制作为PPT")

    # 打印幻灯片概览
    print(f"\n{'页码':<4} {'类型':<10} {'标题'}")
    print("-" * 50)
    for s in slides:
        print(f"{s.get('page',''):<4} {s.get('type',''):<10} {s.get('title','')[:30]}")

if __name__ == "__main__":
    main()