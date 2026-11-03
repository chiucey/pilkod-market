#!/usr/bin/env python3
"""
视频背景音乐添加工具
使用 moviepy 库为视频添加循环背景音乐
"""

import os
import sys
from pathlib import Path

try:
    from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
except ImportError:
    print("正在安装 moviepy...")
    os.system("pip install moviepy -q")
    from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip


def add_background_music(
    video_path: str,
    audio_path: str,
    output_path: str = None,
    volume: float = 0.3
) -> str:
    """
    为视频添加背景音乐

    Args:
        video_path: 视频文件路径
        audio_path: 音频文件路径
        output_path: 输出文件路径，默认在原视频名前加"with_music_"
        volume: 背景音乐音量 (0.0-1.0)，默认 0.3

    Returns:
        输出文件路径
    """
    # 验证输入文件
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"视频文件不存在: {video_path}")
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"音频文件不存在: {audio_path}")

    # 设置默认输出路径
    if output_path is None:
        video_name = Path(video_path).stem
        output_path = f"{video_name}_with_music.mp4"

    # 确保音量在有效范围内
    volume = max(0.0, min(1.0, volume))

    print(f"正在加载视频: {video_path}")
    video_clip = VideoFileClip(video_path)
    video_duration = video_clip.duration
    print(f"视频时长: {video_duration:.2f} 秒")

    print(f"正在加载音频: {audio_path}")
    audio_clip = AudioFileClip(audio_path)
    audio_duration = audio_clip.duration
    print(f"音频时长: {audio_duration:.2f} 秒")

    # 循环音频以匹配视频长度
    if audio_duration < video_duration:
        loops_needed = int(video_duration / audio_duration) + 2
        print(f"正在循环音频 ({loops_needed} 次)...")

        # 循环音频
        looped_audio = audio_clip.loop(n=loops_needed)

        # 截取与视频相同的长度
        looped_audio = looped_audio.subclip(0, video_duration)

        # 设置音量和持续时间
        looped_audio = looped_audio.set_duration(video_duration)
    else:
        # 如果音频比视频长，只使用与视频相同的长度
        print("音频比视频长，截取与视频相同长度...")
        looped_audio = audio_clip.subclip(0, video_duration)

    # 设置背景音乐音量
    looped_audio = looped_audio.volumex(volume)

    # 保留原视频音轨（如果有）
    if video_clip.audio is not None:
        print("保留原视频音轨...")
        # 降低原音轨音量以避免与背景音乐冲突
        original_audio = video_clip.audio.volumex(0.7)
        final_audio = CompositeAudioClip([original_audio, looped_audio])
    else:
        final_audio = looped_audio

    # 将音频添加到视频
    video_with_audio = video_clip.set_audio(final_audio)

    # 导出视频
    print(f"正在导出视频到: {output_path}")
    video_with_audio.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        audio_bitrate='192k',
        threads=4,
        verbose=False,
        logger=None
    )

    # 清理内存
    video_clip.close()
    audio_clip.close()
    video_with_audio.close()

    print(f"完成！输出文件: {output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python add_background_music.py <视频路径> <音频路径> [输出路径] [音量 0.0-1.0]")
        print("示例: python add_background_music.py input.mp4 background.mp3 output.mp4 0.3")
        sys.exit(1)

    video_path = sys.argv[1]
    audio_path = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else None
    volume = float(sys.argv[4]) if len(sys.argv) > 4 else 0.3

    add_background_music(video_path, audio_path, output_path, volume)
