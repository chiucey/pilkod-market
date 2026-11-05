#!/usr/bin/env python3
"""
医学科普动画流水线 - 主协调脚本
Usage:
    python3 main_pipeline.py <input> --type pdf|url|topic [options]

Examples:
    python3 main_pipeline.py /workspace/docs/paper.pdf --type pdf --audience public
    python3 main_pipeline.py "https://pubmed.ncbi.nlm.nih.gov/..." --type url --duration 2
    python3 main_pipeline.py "二甲双胍延缓衰老的机制" --type topic --audience public
"""

import argparse
import os
import sys
import subprocess
import json
import shutil
from pathlib import Path

BASE_DIR = Path("/workspace/medical-cartoon")
OUTPUT_DIR = BASE_DIR / "output"
SCRIPTS_DIR = Path(__file__).parent


def run_cmd(cmd, desc=""):
    print(f"\n[STEP] {desc or cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[WARN] {result.stderr[:500]}")
    return result


def main():
    parser = argparse.ArgumentParser(description="医学科普动画流水线")
    parser.add_argument("input", help="PDF路径 / URL / 主题")
    parser.add_argument("--type", choices=["pdf", "url", "topic"], default="topic",
                        help="输入类型")
    parser.add_argument("--audience", default="public",
                        choices=["public", "medical", "patient"],
                        help="目标受众")
    parser.add_argument("--duration", type=float, default=2.0,
                        help="目标总时长（分钟），默认2分钟")
    parser.add_argument("--style", default="flat_medical",
                        choices=["flat_medical", "infographic", "cartoon"],
                        help="插画风格")
    parser.add_argument("--lang", default="zh-CN",
                        help="配音语言，默认中文")
    parser.add_argument("--voice", default="female-tianmei",
                        help="TTS音色")
    parser.add_argument("--output", default=str(OUTPUT_DIR),
                        help="输出目录")
    args = parser.parse_args()

    # 创建输出目录
    output = Path(args.output)
    for sub in ["scenes", "clips", "voice"]:
        (output / sub).mkdir(parents=True, exist_ok=True)

    print(f"""
╔══════════════════════════════════════════════════════════╗
║     医学科普动画生成流水线  Medical Cartoon Pipeline   ║
╠══════════════════════════════════════════════════════════╣
║  输入: {args.input[:50]}        ║
║  类型: {args.type:<12}  受众: {args.audience:<8}  时长: {args.duration}min  ║
╚══════════════════════════════════════════════════════════╝
    """)

    # ── Step 1: 文献阅读 ──────────────────────────────────
    if args.type == "pdf":
        extract_script = SCRIPTS_DIR / "extract_pdf.py"
        if extract_script.exists():
            run_cmd(
                f"python3 {extract_script} \"{args.input}\" --output {output}/literature.txt",
                "Step 1: 提取PDF文本"
            )
            literature_content = open(output / "literature.txt").read()
        else:
            literature_content = "[PDF内容] 请手动粘贴文献关键段落"
            print("[WARN] extract_pdf.py 不存在，请手动提供文献内容")

    elif args.type == "url":
        print("[Step 1] 使用 extract_content_from_websites 工具提取URL内容")
        literature_content = "[URL内容] 请通过 extract_content_from_websites 工具提取"

    else:  # topic
        literature_content = f"[主题]: {args.input}"

    # ── Step 2: 生成分镜脚本 ────────────────────────────────
    storyboard_script = SCRIPTS_DIR / "generate_storyboard.py"
    scenes_count = max(8, int(args.duration * 4.5))  # ~4.5 scenes/min

    print(f"[Step 2] 生成 {scenes_count} 个场景的分镜脚本...")

    if storyboard_script.exists():
        run_cmd(
            f'python3 {storyboard_script} "{args.input}" '
            f'--audience {args.audience} --scenes {scenes_count} '
            f'--style {args.style} --output {output}/script.md',
            "Step 2: 生成分镜脚本"
        )
    else:
        print("[WARN] generate_storyboard.py 不存在，将生成默认分镜模板")

    # ── Step 3 & 4: 并发生成图像和视频 ──────────────────────
    print("""
[Step 3+4] 图像生成 + 视频片段制作
  → 请复制分镜表中的画面描述字段
  → 调用 image_synthesize 生成医学插画（每次最多5张）
  → 调用 batch_image_to_video 将图像动画化（每次最多5个片段）
  → 保存到 output/scenes/ 和 output/clips/
""")

    # ── Step 5: TTS配音 ─────────────────────────────────
    print("""
[Step 5] TTS配音生成
  → 从分镜表的解说词列提取每段文字
  → 调用 batch_text_to_audio 生成 .mp3 文件
  → 保存到 output/voice/
""")

    # ── Step 6: 打包 ────────────────────────────────────
    print("""
[Step 6] 打包所有素材
  → 所有素材已保存到: {output}
  → 使用 FFmpeg 拼接视频片段和配音
  → 生成最终视频文件
""")

    # 生成拼接指引文件
    guide = output / "assembly_guide.txt"
    guide.write_text(f"""
医学科普动画素材包 - 拼接指引
=====================================

素材目录：
  scenes/  - 原始医学插画 PNG 文件
  clips/   - AI 视频片段 .mp4 文件（clip_01.mp4, clip_02.mp4 ...）
  voice/   - TTS 配音 .mp3 文件（voice_01.mp3, voice_02.mp3 ...）
  script.md - 完整分镜脚本

步骤一：拼接视频片段
------------------------
# 创建片段列表文件 clips_list.txt：
file 'clip_01.mp4'
file 'clip_02.mp4'
file 'clip_03.mp4'
...（按顺序列出所有片段）

# 执行拼接：
ffmpeg -f concat -safe 0 -i clips_list.txt \\
  -c:v libx264 -crf 23 -preset fast \\
  -c:a aac -b:a 128k \\
  output_video.mp4

步骤二：合并所有配音
------------------------
# 创建配音列表文件 voice_list.txt：
file 'voice_01.mp3'
file 'voice_02.mp3'
file 'voice_03.mp3'
...（按顺序列出所有配音）

# 执行合并：
ffmpeg -f concat -safe 0 -i voice_list.txt -c:a copy combined_audio.mp3

步骤三：音画合成
------------------------
ffmpeg -i output_video.mp4 -i combined_audio.mp3 \\
  -c:v copy -c:a aac -shortest \\
  final_medical_cartoon.mp4

可选：添加背景音乐
------------------------
ffmpeg -i final_medical_cartoon.mp4 -i bgm.mp3 \\
  -filter_complex "[1:a]volume=0.15[bgm]" \\
  -map 0:v -map "[bgm]" \\
  -c:v copy -c:a aac final_with_bgm.mp4

质量提示：
  - CRF 18-22 画质最好，文件较大
  - CRF 23-26 平衡画质和体积
  - 768P 片段建议输出 1080P（ upscale）：
    ffmpeg -i input_768p.mp4 -vf scale=1920:1080 -c:a copy output_1080p.mp4
""")

    print(f"\n[完成] 素材已保存到: {output}")
    print(f"[完成] 请阅读: {guide}")
    print("\n下一步：请将分镜脚本发给我，我将帮你逐场景生成图像和视频片段！")


if __name__ == "__main__":
    main()
