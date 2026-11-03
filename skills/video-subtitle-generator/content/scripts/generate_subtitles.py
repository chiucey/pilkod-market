#!/usr/bin/env python3
"""
视频字幕生成器
使用 Whisper 进行语音识别，自动为视频生成同步字幕
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import timedelta

def check_dependencies():
    """检查必要的依赖是否已安装"""
    required = ['ffmpeg', 'whisper']
    missing = []

    for dep in required:
        try:
            if dep == 'ffmpeg':
                subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            else:
                __import__(dep)
        except (subprocess.CalledProcessError, ImportError):
            missing.append(dep)

    if missing:
        print(f"警告: 缺少依赖: {', '.join(missing)}")
        print("请运行: pip install openai-whisper ffmpeg-python")
        return False
    return True

def extract_audio(video_path: str, output_path: str = None) -> str:
    """从视频中提取音频"""
    if output_path is None:
        output_path = Path(video_path).with_suffix('.wav')

    cmd = [
        'ffmpeg', '-i', video_path,
        '-vn', '-acodec', 'pcm_s16le',
        '-ar', '16000', '-ac', '1',
        '-y', str(output_path)
    ]

    print(f"正在提取音频...")
    subprocess.run(cmd, capture_output=True, check=True)
    print(f"音频已提取至: {output_path}")
    return str(output_path)

def format_timestamp(seconds: float) -> str:
    """将秒数转换为 SRT 时间戳格式 (HH:MM:SS,mmm)"""
    td = timedelta(seconds=seconds)
    hours = int(td.total_seconds() // 3600)
    minutes = int((td.total_seconds() % 3600) // 60)
    secs = int(td.total_seconds() % 60)
    millis = int((td.total_seconds() - int(td.total_seconds())) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def generate_srt(transcription_result: dict, output_path: str):
    """生成 SRT 字幕文件"""
    segments = transcription_result.get('segments', [])

    with open(output_path, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(segments, 1):
            start = format_timestamp(segment['start'])
            end = format_timestamp(segment['end'])
            text = segment['text'].strip()

            f.write(f"{i}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{text}\n")
            f.write("\n")

    print(f"字幕文件已生成: {output_path}")

def transcribe_audio(audio_path: str, model: str = "base") -> dict:
    """使用 Whisper 进行语音识别"""
    import whisper

    print(f"正在加载 Whisper {model} 模型...")
    model = whisper.load_model(model)

    print(f"正在识别音频...")
    result = model.transcribe(audio_path, verbose=False)

    return result

def burn_subtitles(video_path: str, subtitle_path: str, output_path: str = None,
                   font_size: int = 48, font_color: str = "white",
                   bg_color: str = "#000000CC", position: str = "bottom"):
    """将字幕烧录到视频中"""

    if output_path is None:
        output_path = Path(video_path).with_suffix('_subtitled.mp4')

    # 构建字幕样式字符串
    style = f"FontSize={font_size},PrimaryColour=&H{font_color.replace('#', '')},Alignment=2"

    if position == "bottom":
        style += ",MarginV=50"

    cmd = [
        'ffmpeg', '-i', video_path,
        '-vf', f"subtitles='{subtitle_path}'",
        '-c:a', 'copy',
        '-y', str(output_path)
    ]

    print(f"正在烧录字幕到视频...")
    subprocess.run(cmd, capture_output=True, check=True)
    print(f"带字幕视频已生成: {output_path}")

    return str(output_path)

def main():
    parser = argparse.ArgumentParser(description='视频字幕生成器')
    parser.add_argument('video', help='视频文件路径')
    parser.add_argument('-m', '--model', default='base',
                        choices=['tiny', 'base', 'small', 'medium', 'large'],
                        help='Whisper 模型大小 (默认: base)')
    parser.add_argument('-o', '--output', default=None,
                        help='输出路径 (默认: 与视频同目录)')
    parser.add_argument('--burn', action='store_true',
                        help='是否将字幕烧录到视频中')
    parser.add_argument('--font-size', type=int, default=48,
                        help='字体大小 (默认: 48)')
    parser.add_argument('--font-color', default='white',
                        help='字体颜色 (默认: white)')

    args = parser.parse_args()

    # 检查依赖
    if not check_dependencies():
        sys.exit(1)

    video_path = Path(args.video)
    if not video_path.exists():
        print(f"错误: 视频文件不存在: {video_path}")
        sys.exit(1)

    # 设置输出路径
    output_dir = Path(args.output) if args.output else video_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    base_name = video_path.stem
    audio_path = output_dir / f"{base_name}.wav"
    srt_path = output_dir / f"{base_name}.srt"

    try:
        # 1. 提取音频
        extract_audio(str(video_path), str(audio_path))

        # 2. 语音识别
        result = transcribe_audio(str(audio_path), args.model)

        # 3. 生成字幕文件
        generate_srt(result, str(srt_path))

        # 4. 可选：烧录字幕
        if args.burn:
            output_video = output_dir / f"{base_name}_subtitled.mp4"
            burn_subtitles(
                str(video_path), str(srt_path), str(output_video),
                font_size=args.font_size, font_color=args.font_color
            )

        print("\n处理完成!")
        print(f"字幕文件: {srt_path}")
        if args.burn:
            print(f"带字幕视频: {output_video}")

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg 执行错误: {e.stderr.decode() if e.stderr else str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"处理错误: {e}")
        sys.exit(1)
    finally:
        # 清理临时音频文件
        if audio_path.exists():
            audio_path.unlink()

if __name__ == '__main__':
    main()
