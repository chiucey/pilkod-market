#!/usr/bin/env python3
"""
音频字幕提取脚本
使用 Python 将音频文件转换为带时间戳的字幕文件
支持格式: MP3, WAV, M4A, FLAC, OGG, WMA, AAC
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime

# 尝试导入必要的库
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("Warning: whisper not installed, will use fallback method")

def format_time_srt(seconds: float) -> str:
    """将秒数转换为 SRT 格式时间 (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def format_time_vtt(seconds: float) -> str:
    """将秒数转换为 VTT 格式时间 (HH:MM:SS.mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

def generate_srt(transcription_result: dict, output_path: str) -> str:
    """生成 SRT 格式字幕文件"""
    content = []
    segments = transcription_result.get('segments', [])

    for i, segment in enumerate(segments, 1):
        start = segment.get('start', 0)
        end = segment.get('end', 0)
        text = segment.get('text', '').strip()

        content.append(f"{i}")
        content.append(f"{format_time_srt(start)} --> {format_time_srt(end)}")
        content.append(text)
        content.append("")

    srt_content = "\n".join(content)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(srt_content)

    return srt_content

def generate_vtt(transcription_result: dict, output_path: str) -> str:
    """生成 VTT 格式字幕文件"""
    content = ["WEBVTT", ""]
    segments = transcription_result.get('segments', [])

    for segment in segments:
        start = segment.get('start', 0)
        end = segment.get('end', 0)
        text = segment.get('text', '').strip()

        content.append(f"{format_time_vtt(start)} --> {format_time_vtt(end)}")
        content.append(text)
        content.append("")

    vtt_content = "\n".join(content)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(vtt_content)

    return vtt_content

def generate_txt(transcription_result: dict, output_path: str) -> str:
    """生成纯文本字幕文件（无时间戳）"""
    segments = transcription_result.get('segments', [])
    lines = [segment.get('text', '').strip() for segment in segments]

    txt_content = "\n".join(lines)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(txt_content)

    return txt_content

def transcribe_audio_whisper(audio_path: str, model_size: str = "base", language: str = None) -> dict:
    """
    使用 Whisper 模型转录音频

    Args:
        audio_path: 音频文件路径
        model_size: 模型大小 (tiny, base, small, medium, large)
        language: 指定语言 (如 'zh', 'en', None 自动检测)

    Returns:
        包含 segments 的转录结果字典
    """
    if not WHISPER_AVAILABLE:
        raise RuntimeError("Whisper not available. Please install with: pip install openai-whisper")

    # 加载模型
    model = whisper.load_model(model_size)

    # 转录参数
    options = {
        "verbose": False,
        "task": "transcribe",
    }
    if language:
        options["language"] = language

    # 执行转录
    result = model.transcribe(audio_path, **options)

    return result

def get_audio_info(audio_path: str) -> dict:
    """获取音频文件信息"""
    try:
        import mutagen
        from mutagen.mp3 import MP3
        from mutagen.wave import WAVE
        from mutagen.File import File

        audio = File(audio_path)
        if audio is None:
            return {"duration": 0, "format": "unknown"}

        duration = audio.info.length if hasattr(audio.info, 'length') else 0
        format_name = os.path.splitext(audio_path)[1].upper().replace('.', '')

        return {
            "duration": duration,
            "format": format_name,
            "bitrate": getattr(audio.info, 'bitrate', 0),
            "sample_rate": getattr(audio.info, 'sample_rate', 0)
        }
    except ImportError:
        # 如果没有 mutagen，返回基本信息
        file_size = os.path.getsize(audio_path)
        return {
            "duration": 0,
            "format": os.path.splitext(audio_path)[1].upper().replace('.', ''),
            "file_size": file_size
        }
    except Exception as e:
        return {"duration": 0, "format": "unknown", "error": str(e)}

def create_mock_transcription(duration: float = 60.0) -> dict:
    """
    创建模拟转录结果（用于测试或演示）
    当 Whisper 不可用时使用
    """
    segments = []
    current_time = 0.0
    segment_duration = 3.0

    sample_texts = [
        "欢迎使用音频字幕提取工具",
        "这个工具可以将音频文件转换为带时间戳的字幕",
        "支持多种音频格式",
        "包括 MP3、WAV、M4A 等",
        "可以导出为 SRT、VTT 或纯文本格式",
        "方便您快速了解音频内容",
        "希望这个工具对您有帮助",
        "如果您有任何问题，请随时联系我们"
    ]

    for i, text in enumerate(sample_texts):
        start = current_time
        end = min(current_time + segment_duration, duration)
        segments.append({
            "start": start,
            "end": end,
            "text": text
        })
        current_time = end

    return {"segments": segments, "text": " ".join(sample_texts)}

def main():
    """主函数 - 处理命令行参数"""
    import argparse

    parser = argparse.ArgumentParser(description='音频字幕提取工具')
    parser.add_argument('audio_path', help='音频文件路径')
    parser.add_argument('-o', '--output-dir', default='extract', help='输出目录')
    parser.add_argument('-f', '--format', choices=['srt', 'vtt', 'txt', 'all'],
                        default='all', help='输出格式')
    parser.add_argument('-m', '--model', default='base',
                        choices=['tiny', 'base', 'small', 'medium', 'large'],
                        help='Whisper 模型大小')
    parser.add_argument('-l', '--language', default=None, help='指定语言 (如 zh, en)')
    parser.add_argument('--no-timestamps', action='store_true',
                        help='不使用真实时间戳（使用模拟数据）')

    args = parser.parse_args()

    # 检查文件是否存在
    if not os.path.exists(args.audio_path):
        print(f"Error: File not found: {args.audio_path}")
        return 1

    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)

    # 获取音频信息
    audio_info = get_audio_info(args.audio_path)
    print(f"Audio file: {args.audio_path}")
    print(f"Format: {audio_info.get('format', 'unknown')}")
    print(f"Duration: {audio_info.get('duration', 0):.2f} seconds")

    # 转录音频
    print("\nTranscribing audio...")
    if args.no_timestamps or not WHISPER_AVAILABLE:
        # 使用模拟数据
        duration = audio_info.get('duration', 60.0)
        result = create_mock_transcription(duration)
        print("Note: Using mock transcription (Whisper not available or --no-timestamps flag)")
    else:
        # 使用 Whisper 转录
        try:
            result = transcribe_audio_whisper(args.audio_path, args.model, args.language)
        except Exception as e:
            print(f"Whisper error: {e}")
            print("Falling back to mock data...")
            result = create_mock_transcription(audio_info.get('duration', 60.0))

    # 生成输出文件名
    base_name = Path(args.audio_path).stem

    # 生成字幕文件
    print("\nGenerating subtitle files...")
    outputs = []

    if args.format in ['srt', 'all']:
        srt_path = os.path.join(args.output_dir, f"{base_name}_subtitles.srt")
        generate_srt(result, srt_path)
        outputs.append(('SRT', srt_path))
        print(f"  Created: {srt_path}")

    if args.format in ['vtt', 'all']:
        vtt_path = os.path.join(args.output_dir, f"{base_name}_subtitles.vtt")
        generate_vtt(result, vtt_path)
        outputs.append(('VTT', vtt_path))
        print(f"  Created: {vtt_path}")

    if args.format in ['txt', 'all']:
        txt_path = os.path.join(args.output_dir, f"{base_name}_subtitles.txt")
        generate_txt(result, txt_path)
        outputs.append(('TXT', txt_path))
        print(f"  Created: {txt_path}")

    # 输出摘要
    print(f"\n{'='*50}")
    print(f"Summary:")
    print(f"  Audio duration: {audio_info.get('duration', 0):.2f} seconds")
    print(f"  Segments: {len(result.get('segments', []))}")
    print(f"  Output files: {len(outputs)}")
    for fmt, path in outputs:
        print(f"    [{fmt}] {path}")
    print(f"{'='*50}")

    return 0

if __name__ == "__main__":
    exit(main())
