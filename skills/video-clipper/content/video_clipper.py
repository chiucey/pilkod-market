#!/usr/bin/env python3
"""
视频智能裁剪工具
==============

功能：从一个视频文件中智能分割出多个不雷同的短视频片段

使用方法：
1. 命令行模式：
   python video_clipper.py input.mp4 -n 10 -t 30

2. 作为模块导入：
   from video_clipper import VideoClipper
   clipper = VideoClipper("input.mp4")
   clipper.split_overlapping(num_clips=10, max_duration=30)

作者：MiniMax Agent
日期：2026-04-11
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class VideoClipper:
    """视频智能裁剪类"""

    def __init__(self, input_video: str, output_dir: Optional[str] = None):
        """
        初始化裁剪器

        Args:
            input_video: 输入视频文件路径
            output_dir: 输出目录路径，默认保存到"下载"文件夹
        """
        self.input_video = Path(input_video)
        if not self.input_video.exists():
            raise FileNotFoundError(f"视频文件不存在: {self.input_video}")

        # 自动设置输出目录为"下载"文件夹
        if output_dir is None:
            self.output_dir = self._get_download_folder()
        else:
            self.output_dir = Path(output_dir)

        self.duration = self._get_video_duration()
        self.width = self._get_video_width()
        self.height = self._get_video_height()

    def _get_download_folder(self) -> Path:
        """获取系统的下载文件夹路径"""
        import platform
        system = platform.system()

        if system == 'Windows':
            # Windows: 用户目录下的下载文件夹
            download_path = Path.home() / 'Downloads'
        elif system == 'Darwin':
            # macOS: 用户目录下的下载文件夹
            download_path = Path.home() / 'Downloads'
        else:
            # Linux: 用户目录下的下载文件夹
            download_path = Path.home() / 'Downloads'

        # 确保下载文件夹存在
        download_path.mkdir(parents=True, exist_ok=True)

        # 在下载文件夹内创建以原视频名为前缀的子文件夹
        video_name = self.input_video.stem  # 不带扩展名的文件名
        output_path = download_path / f"{video_name}_clips"
        output_path.mkdir(parents=True, exist_ok=True)

        return output_path

    def _run_ffprobe(self, args: List[str]) -> str:
        """运行ffprobe命令"""
        cmd = ['ffprobe', '-v', 'error'] + args + ['-of', 'json', str(self.input_video)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"ffprobe错误: {result.stderr}")
        return result.stdout

    def _get_video_duration(self) -> float:
        """获取视频时长（秒）"""
        output = self._run_ffprobe(['-show_entries', 'format=duration'])
        data = json.loads(output)
        return float(data['format']['duration'])

    def _get_video_width(self) -> int:
        """获取视频宽度"""
        output = self._run_ffprobe(['-select_streams', 'v:0', '-show_entries', 'stream=width'])
        data = json.loads(output)
        return data['streams'][0]['width']

    def _get_video_height(self) -> int:
        """获取视频高度"""
        output = self._run_ffprobe(['-select_streams', 'v:0', '-show_entries', 'stream=height'])
        data = json.loads(output)
        return data['streams'][0]['height']

    def split_overlapping(self, num_clips: int = 10, max_duration: int = 30) -> List[str]:
        """
        重叠分割：生成多个有时间重叠的片段（推荐）

        这个策略确保每个片段包含不同的内容，适合保留视频的关键时刻

        Args:
            num_clips: 要生成的视频数量
            max_duration: 每个视频的最大时长（秒）

        Returns:
            生成的文件路径列表
        """
        # 计算最佳分割策略
        clip_duration = min(max_duration, self.duration * 0.4)  # 每个片段时长不超过视频总长的40%
        step = (self.duration - clip_duration) / (num_clips - 1) if num_clips > 1 else 0

        self.output_dir.mkdir(parents=True, exist_ok=True)

        output_files = []
        for i in range(num_clips):
            start_time = i * step
            if start_time + clip_duration > self.duration:
                start_time = self.duration - clip_duration

            output_file = self.output_dir / f"clip_{i+1:02d}_{start_time:.0f}s_{start_time+clip_duration:.0f}s.mp4"

            self._extract_clip(start_time, clip_duration, output_file)
            output_files.append(str(output_file))
            print(f"  ✓ 片段 {i+1}/{num_clips}: {start_time:.1f}s - {start_time+clip_duration:.1f}s")

        return output_files

    def split_sequential(self, num_clips: int = 10, max_duration: int = 30) -> List[str]:
        """
        顺序分割：将视频等分为多个片段

        Args:
            num_clips: 要生成的视频数量
            max_duration: 每个视频的最大时长（秒）

        Returns:
            生成的文件路径列表
        """
        clip_duration = min(self.duration / num_clips, max_duration)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        output_files = []
        for i in range(num_clips):
            start_time = i * clip_duration
            if start_time + clip_duration > self.duration:
                clip_duration = self.duration - start_time

            output_file = self.output_dir / f"clip_{i+1:02d}_{start_time:.0f}s_{start_time+clip_duration:.0f}s.mp4"

            self._extract_clip(start_time, clip_duration, output_file)
            output_files.append(str(output_file))
            print(f"  ✓ 片段 {i+1}/{num_clips}: {start_time:.1f}s - {start_time+clip_duration:.1f}s")

        return output_files

    def split_custom(self, segments: List[Tuple[float, float]]) -> List[str]:
        """
        自定义分割：指定每个片段的起止时间

        Args:
            segments: [(start1, end1), (start2, end2), ...] 时间对列表

        Returns:
            生成的文件路径列表
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)

        output_files = []
        for i, (start, end) in enumerate(segments):
            duration = end - start
            output_file = self.output_dir / f"clip_{i+1:02d}_{start:.0f}s_{end:.0f}s.mp4"

            self._extract_clip(start, duration, output_file)
            output_files.append(str(output_file))
            print(f"  ✓ 片段 {i+1}/{len(segments)}: {start:.1f}s - {end:.1f}s")

        return output_files

    def _extract_clip(self, start_time: float, duration: float, output_file: Path):
        """使用ffmpeg提取视频片段"""
        cmd = [
            'ffmpeg', '-y',
            '-ss', str(start_time),
            '-i', str(self.input_video),
            '-t', str(duration),
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-movflags', '+faststart',
            str(output_file)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg错误: {result.stderr}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='视频智能裁剪工具 - 快速将长视频分割为多个短视频',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  python video_clipper.py input.mp4 -n 10 -t 30
  python video_clipper.py video.mp4 --mode overlapping
  python video_clipper.py video.mp4 --segments "0,25 10,35 20,45"
        """
    )

    parser.add_argument('input', help='输入视频文件路径')
    parser.add_argument('-n', '--num-clips', type=int, default=10,
                       help='要生成的视频数量 (默认: 10)')
    parser.add_argument('-t', '--max-duration', type=int, default=30,
                       help='每个视频的最大时长/秒 (默认: 30)')
    parser.add_argument('-m', '--mode', choices=['sequential', 'overlapping', 'custom'],
                       default='overlapping',
                       help='分割模式: sequential(顺序) / overlapping(重叠-推荐) / custom(自定义)')
    parser.add_argument('-s', '--segments',
                       help='自定义片段: "start1,end1 start2,end2 ..." (仅在custom模式下使用)')
    parser.add_argument('-o', '--output-dir',
                       help='输出目录 (默认: 自动保存到系统的下载文件夹)')

    args = parser.parse_args()

    print("\n" + "="*50)
    print("📹 视频智能裁剪工具")
    print("="*50)
    print(f"\n输入文件: {args.input}")
    print(f"分割数量: {args.num_clips} 个片段")
    print(f"最大时长: {args.max_duration} 秒/片段")
    print(f"分割模式: {args.mode}")
    print("-"*50 + "\n")

    try:
        clipper = VideoClipper(args.input, args.output_dir)

        print(f"📊 视频信息:")
        print(f"   时长: {clipper.duration:.2f} 秒")
        print(f"   分辨率: {clipper.width} x {clipper.height}")
        print(f"\n🎬 开始裁剪...\n")

        if args.mode == 'sequential':
            output_files = clipper.split_sequential(args.num_clips, args.max_duration)
        elif args.mode == 'overlapping':
            output_files = clipper.split_overlapping(args.num_clips, args.max_duration)
        else:  # custom
            if not args.segments:
                print("❌ 自定义模式需要指定 --segments 参数")
                sys.exit(1)
            segments = []
            for seg in args.segments.split():
                parts = seg.split(',')
                if len(parts) != 2:
                    print(f"❌ 无效的片段格式: {seg}")
                    sys.exit(1)
                segments.append((float(parts[0]), float(parts[1])))
            output_files = clipper.split_custom(segments)

        print("\n" + "="*50)
        print(f"✅ 完成！生成了 {len(output_files)} 个视频片段")
        print("="*50)
        print(f"\n📁 输出目录: {clipper.output_dir}")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
