#!/usr/bin/env python3
"""
科普动画分镜脚本生成器
根据医学主题生成结构化分镜表（含画面描述 + 解说词）

Usage:
    python3 generate_storyboard.py "<医学主题>" --audience public --scenes 10 [options]
"""

import argparse
import sys
from pathlib import Path

# ─── 风格模板 ────────────────────────────────────────────

STYLE_PROMPTS = {
    "flat_medical": (
        "Flat medical illustration, clean white background, modern healthcare style, "
        "anatomical accuracy, soft pastel colors, professional medical icon design, "
        "no text, no people unless specified, [SCENE_DESC]"
    ),
    "infographic": (
        "Medical infographic, minimalist style, white background, data visualization, "
        "clean typography, healthcare design language, no text in image, [SCENE_DESC]"
    ),
    "cartoon": (
        "Medical cartoon style, friendly colorful characters, educational science illustration, "
        "clean lines, white background, approachable healthcare art, [SCENE_DESC]"
    ),
}

AUDIENCE_TONES = {
    "public": "通俗易懂、贴近生活、温暖友好",
    "medical": "专业准确、适度深入、可含专业术语",
    "patient": "温和易懂、避免恐惧、给予希望",
}

# ─── 典型科普动画结构 ────────────────────────────────────

STRUCTURE_TEMPLATE = [
    {
        "phase": "开场",
        "pct": 0.10,  # 时长占比
        "type": "hook",
        "guide": "用一个惊人的数据/问题/场景抓住注意力",
        "visual_style": "吸引眼球的全局画面，不用解剖细节"
    },
    {
        "phase": "背景铺垫",
        "pct": 0.15,
        "type": "context",
        "guide": "介绍这个疾病/机制是什么，有多常见",
        "visual_style": "示意图或信息图，易于理解"
    },
    {
        "phase": "核心揭秘",
        "pct": 0.40,
        "type": "core",
        "guide": "发病机制/核心原理，用通俗比喻解释",
        "visual_style": "解剖图+动画箭头，分步骤展示"
    },
    {
        "phase": "关键数据",
        "pct": 0.15,
        "type": "data",
        "guide": "预防/诊断/治疗的关键数字或要点",
        "visual_style": "数据可视化，大字体数字突出"
    },
    {
        "phase": "总结行动",
        "pct": 0.15,
        "type": "action",
        "guide": "核心要点总结 + 可操作的建议",
        "visual_style": "简洁有力，关键词突出"
    },
    {
        "phase": "收尾",
        "pct": 0.05,
        "type": "outro",
        "guide": "感谢观看/欢迎提问/相关阅读推荐",
        "visual_style": "品牌感，温馨收尾"
    },
]


def generate_storyboard(topic: str, audience: str = "public",
                       total_scenes: int = 10,
                       style: str = "flat_medical",
                       total_duration_min: float = 2.0) -> str:
    """
    生成分镜 Markdown 文本
    """
    scene_template = STYLE_PROMPTS.get(style, STYLE_PROMPTS["flat_medical"])
    tone = AUDIENCE_TONES.get(audience, AUDIENCE_TONES["public"])
    total_s = int(total_duration_min * 60)

    lines = [
        f"# 医学科普动画分镜脚本",
        f"> **主题**: {topic}",
        f"> **目标受众**: {audience}（{tone}）",
        f"> **总时长**: {total_duration_min} 分钟（约 {total_s} 秒）",
        f"> **场景数**: {total_scenes} 场景（每场景 ~{total_s // total_scenes} 秒）",
        f"",
        f"---",
        f"",
    ]

    # 分配各阶段场景数
    phase分配 = []
    remaining = total_scenes
    for ph in STRUCTURE_TEMPLATE:
        n = max(1, round(ph["pct"] * total_scenes))
        n = min(n, remaining)
        phase分配.append((ph, n))
        remaining -= n
    # 把剩余的补到核心阶段
    if remaining > 0:
        for i, (ph, n) in enumerate(phase分配):
            if ph["type"] == "core":
                phase分配[i] = (ph, n + remaining)
                break

    scene_num = 1

    for ph, n_scenes in phase分配:
        phase = ph["phase"]
        guide = ph["guide"]
        vstyle = ph["visual_style"]

        lines.append(f"## 【{phase}】— {n_scenes} 场景")
        lines.append(f"> 画面风格指引：{vstyle}")
        lines.append(f"> 内容指引：{guide}")
        lines.append(f"")
        lines.append(f"| 场景 | 画面描述（用于AI生成） | 解说词（约 {total_s // total_scenes * n_scenes // n_scenes * 6 // 6} 字） | 动画指令 | 时长 |")

        for i in range(n_scenes):
            scene_id = str(scene_num).zfill(2)

            # 生成具体内容
            if scene_num == 1 and ph["type"] == "hook":
                scene_desc = (
                    f"Single dramatic medical scene: concerned person looking at doctor screen, "
                    f"glowing DNA helix emerging from background, bright lighting, "
                    f"emotional hook for {topic}"
                )
                narration = (
                    f"你知道吗？{topic}，可能正在影响我们身边每一个家庭。"
                )
            elif scene_num == total_scenes and ph["type"] == "outro":
                scene_desc = (
                    f"Friendly medical team icon, warm glow, clean white background, "
                    f"celebration illustration style, {topic} awareness ribbon subtle"
                )
                narration = "感谢观看，了解更多医学科普，关注我们！"
            elif ph["type"] == "core":
                scene_desc = (
                    f"Medical mechanism diagram, flat illustration, showing biological process "
                    f"of {topic}, colorful cell diagram, clean background, "
                    f"animated arrows pointing to key structures, educational clarity"
                )
                subtopics = [
                    f"{topic}的细胞层面示意图",
                    f"{topic}相关器官正常与异常状态对比",
                    f"药物作用机制模式图",
                    f"关键分子信号通路",
                    f"治疗原理图解",
                ]
                if i < len(subtopics):
                    scene_desc = scene_desc.replace(
                        f"{topic}的细胞层面示意图",
                        subtopics[min(i, len(subtopics)-1)]
                    )
                narration_templates = [
                    f"让我们来看看，这背后的原理是什么。",
                    f"关键在于这个分子，它起到了核心作用。",
                    f"当这个机制出了问题，疾病就随之而来。",
                    f"好消息是，我们有办法干预它。",
                    f"研究证实，调控这个通路可以显著改善病情。",
                ]
                narration = narration_templates[i % len(narration_templates)]
            elif ph["type"] == "data":
                scene_desc = (
                    f"Medical data visualization, large bold numbers on clean infographic, "
                    f"contrast background, {topic} statistics, flat design, "
                    f"professional healthcare chart style, no text labels"
                )
                narrations_data = [
                    f"全球约有XX万人受此影响，早期发现至关重要。",
                    f"记住这三个数字，关键时刻能救命。",
                    f"只要做好这一件事，发病风险就能降低一半！",
                ]
                narration = narrations_data[i % len(narrations_data)]
            elif ph["type"] == "action":
                scene_desc = (
                    f"Empowering healthcare action scene, person doing preventive exercise, "
                    f"healthy lifestyle illustration, bright positive colors, "
                    f"action-oriented composition, {topic} prevention"
                )
                narrations_action = [
                    f"预防其实很简单，从今天开始做这件事！",
                    f"如果出现这些症状，请尽快就医。",
                    f"定期检查，是最好的健康管理方式。",
                ]
                narration = narrations_action[i % len(narrations_action)]
            else:  # context
                scene_desc = (
                    f"Clean medical context illustration, relevant organ or condition diagram, "
                    f"modern flat healthcare design, {topic} overview, "
                    f"approachable science communication style"
                )
                narrations_context = [
                    f"说起{topic}，很多人可能还不太了解它。",
                    f"这其实是一种非常常见的医学问题。",
                    f"让我们先从基础说起。",
                ]
                narration = narrations_context[i % len(narrations_context)]

            animation = {
                "hook": "fade in, dramatic zoom in",
                "context": "gentle fade in, smooth transition",
                "core": "zoom in, highlight arrows animate, diagram build-up",
                "data": "number counter animation, smooth reveal",
                "action": "uplifting zoom in, encouraging motion",
                "outro": "gentle fade, warm glow"
            }.get(ph["type"], "gentle fade in")

            scene_duration = 6  # 默认6秒/场景

            # 构建完整画面 prompt（英文详细描述）
            visual_prompt = scene_desc + f", {scene_template}"

            lines.append(
                f"| {scene_id} | **{scene_desc[:60]}...** | "
                f"「{narration}」 | {animation} | {scene_duration}s |"
            )

            # 生成详细 scene 数据（追加到注释）
            scene_num += 1

    # 添加详细 scene 数据区
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📋 详细场景数据（用于 AI 生成）")
    lines.append("")
    lines.append("| # | Visual Prompt（直接用于image_synthesize） | Narration Text | Duration |")
    lines.append("|---|--------------------------------------|----------------|----------|")

    scene_num = 1
    for ph, n_scenes in phase分配:
        for i in range(n_scenes):
            sid = str(scene_num).zfill(2)
            scene_desc = "medical flat illustration placeholder"  # 简化，实际用上面生成的
            narration = "解说词占位"
            lines.append(f"| {sid} | {scene_desc} | {narration} | 6s |")
            scene_num += 1

    # 添加 FFmpeg 拼接说明
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🔧 拼接指引")
    lines.append("")
    lines.append("```bash")
    lines.append("# 1. 拼接视频片段（clips/ 目录）")
    lines.append("ffmpeg -f concat -safe 0 -i <(for f in clips/*.mp4; do echo \"file '$f'\"; done) \\")
    lines.append("  -c:v libx264 -crf 23 -preset fast output_video.mp4")
    lines.append("")
    lines.append("# 2. 合并 TTS 配音（voice/ 目录）")
    lines.append("ffmpeg -f concat -safe 0 -i <(for f in voice/*.mp3; do echo \"file '$f'\"; done) \\")
    lines.append("  -c:a copy combined_audio.mp3")
    lines.append("")
    lines.append("# 3. 音画合成")
    lines.append("ffmpeg -i output_video.mp4 -i combined_audio.mp3 \\")
    lines.append("  -c:v copy -c:a aac -shortest final.mp4")
    lines.append("```")

    return "\n".join(lines)


def main():
    import argparse
    p = argparse.ArgumentParser(description="生成分镜脚本")
    p.add_argument("topic", help="医学主题")
    p.add_argument("--audience", default="public",
                   choices=["public", "medical", "patient"])
    p.add_argument("--scenes", type=int, default=10, help="场景数量")
    p.add_argument("--duration", type=float, default=2.0, help="总时长（分钟）")
    p.add_argument("--style", default="flat_medical",
                   choices=["flat_medical", "infographic", "cartoon"])
    p.add_argument("--output", default="/workspace/medical-cartoon/output/script.md")
    args = p.parse_args()

    storyboard = generate_storyboard(
        topic=args.topic,
        audience=args.audience,
        total_scenes=args.scenes,
        style=args.style,
        total_duration_min=args.duration,
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(storyboard, encoding="utf-8")
    print(f"[OK] 分镜脚本已生成: {out_path}")
    print(f"[OK] 包含 {args.scenes} 个场景，约 {args.duration} 分钟")


if __name__ == "__main__":
    main()
