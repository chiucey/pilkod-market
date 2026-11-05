#!/usr/bin/env python3
"""
FFmpeg Whisper 智能剪辑工具
结合 FFmpeg 和 Whisper 语音识别实现基于文字的精准剪辑
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import tempfile

try:
    import whisper
    from pydub import AudioSegment
except ImportError:
    print("错误: 缺少必要依赖，请运行: pip install openai-whisper pydub")
    sys.exit(1)


class FFmpegWhisperClipper:
    """FFmpeg Whisper 智能剪辑工具主类"""

    def __init__(self, model_name: str = "base"):
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        """加载 Whisper 模型"""
        print(f"正在加载 Whisper {self.model_name} 模型...")
        self.model = whisper.load_model(self.model_name)
        print("模型加载完成!")

    def transcribe(
        self,
        audio_path: str,
        language: str = None,
        output_format: str = "srt",
        output_path: str = None
    ) -> Dict:
        """
        转录音频/视频文件

        Args:
            audio_path: 输入文件路径
            language: 语言代码（None 为自动检测）
            output_format: 输出格式 (srt/json/text)
            output_path: 输出文件路径

        Returns:
            转录结果字典
        """
        print(f"开始转录: {audio_path}")

        # 如果是视频文件，先提取音频
        if self._is_video(audio_path):
            audio_path = self._extract_audio(audio_path)

        # 执行转录
        options = {
            "task": "transcribe",
            "verbose": False,
        }
        if language:
            options["language"] = language

        result = self.model.transcribe(audio_path, **options)

        # 保存结果
        if output_path:
            self._save_transcription(result, output_path, output_format)

        return result

    def search_keywords(
        self,
        transcription: Dict,
        keywords: List[str],
        case_sensitive: bool = False
    ) -> List[Dict]:
        """
        在转录结果中搜索关键词

        Args:
            transcription: 转录结果字典
            keywords: 关键词列表
            case_sensitive: 是否区分大小写

        Returns:
            匹配的片段列表
        """
        matches = []

        for segment in transcription.get("segments", []):
            text = segment["text"]
            if not case_sensitive:
                text = text.lower()
                search_keywords = [k.lower() for k in keywords]
            else:
                search_keywords = keywords

            for keyword in search_keywords:
                if keyword in text:
                    matches.append({
                        "start": segment["start"],
                        "end": segment["end"],
                        "text": segment["text"].strip(),
                        "keyword": keyword
                    })
                    break  # 每个片段只匹配一次

        return matches

    def clip_by_keywords(
        self,
        input_path: str,
        keywords: List[str],
        output_path: str,
        padding: float = 0.5,
        merge_gaps: float = 2.0
    ) -> bool:
        """
        基于关键词剪辑音视频

        Args:
            input_path: 输入文件路径
            keywords: 关键词列表
            output_path: 输出文件路径
            padding: 每个片段前后添加的秒数
            merge_gaps: 合并间隔小于此值的片段（秒）

        Returns:
            是否成功
        """
        # 先转录
        transcription = self.transcribe(input_path)

        # 搜索关键词
        matches = self.search_keywords(transcription, keywords)

        if not matches:
            print("未找到匹配的关键词!")
            return False

        print(f"找到 {len(matches)} 个匹配片段")

        # 计算要保留的时间范围（合并相邻片段）
        time_ranges = self._merge_time_ranges(
            [(m["start"], m["end"]) for m in matches],
            merge_gaps
        )

        # 添加 padding
        time_ranges = [
            (max(0, start - padding), end + padding)
            for start, end in time_ranges
        ]

        # 执行剪辑
        return self._extract_ranges(input_path, output_path, time_ranges)

    def trim(
        self,
        input_path: str,
        output_path: str,
        start: float = None,
        end: float = None
    ) -> bool:
        """
        修剪音视频文件

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            start: 开始时间（秒）
            end: 结束时间（秒）

        Returns:
            是否成功
        """
        time_ranges = [(start, end)]
        return self._extract_ranges(input_path, output_path, time_ranges)

    def remove_silence(
        self,
        input_path: str,
        output_path: str,
        silence_thresh: float = -40,
        min_silence_len: float = 0.5
    ) -> bool:
        """
        去除静音片段

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            silence_thresh: 静音阈值（dB）
            min_silence_len: 最小静音时长（秒）

        Returns:
            是否成功
        """
        if self._is_video(input_path):
            return self._remove_silence_video(
                input_path, output_path, silence_thresh, min_silence_len
            )
        else:
            return self._remove_silence_audio(
                input_path, output_path, silence_thresh, min_silence_len
            )

    def convert_format(
        self,
        input_path: str,
        output_path: str,
        codec: str = None,
        bitrate: str = "192k",
        format: str = None
    ) -> bool:
        """
        转换音视频格式

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            codec: 视频编码器（如 libx264, aac）
            bitrate: 比特率
            format: 输出格式

        Returns:
            是否成功
        """
        cmd = ["ffmpeg", "-i", input_path, "-y"]

        if codec:
            cmd.extend(["-c:v", codec, "-c:a", "copy"])
        if bitrate:
            cmd.extend(["-b:a", bitrate])
        if format:
            cmd.extend(["-f", format])

        cmd.append(output_path)

        return self._run_ffmpeg(cmd)

    def get_media_info(self, input_path: str) -> Dict:
        """
        获取媒体文件信息

        Args:
            input_path: 输入文件路径

        Returns:
            媒体信息字典
        """
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            input_path
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"获取媒体信息失败: {e}")
            return {}

    # ==================== 私有方法 ====================

    def _is_video(self, path: str) -> bool:
        """检查是否为视频文件"""
        video_exts = {'.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.webm'}
        return Path(path).suffix.lower() in video_exts

    def _extract_audio(self, video_path: str) -> str:
        """从视频提取音频"""
        audio_path = tempfile.mktemp(suffix=".wav")

        cmd = [
            "ffmpeg", "-i", video_path,
            "-vn",  # 不处理视频
            "-acodec", "pcm_s16le",  # WAV 格式
            "-ar", "16000",  # 16kHz 采样率
            "-ac", "1",  # 单声道
            "-y",  # 覆盖
            audio_path
        ]

        print("正在提取音频...")
        self._run_ffmpeg(cmd)
        return audio_path

    def _save_transcription(
        self,
        result: Dict,
        output_path: str,
        format: str
    ):
        """保存转录结果"""
        if format == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        elif format == "srt":
            self._save_as_srt(result, output_path)
        elif format == "text":
            text = result.get("text", "")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)

        print(f"转录结果已保存: {output_path}")

    def _save_as_srt(self, result: Dict, output_path: str):
        """保存为 SRT 格式"""
        with open(output_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(result.get("segments", []), 1):
                start = self._format_timestamp(segment["start"])
                end = self._format_timestamp(segment["end"])
                text = segment["text"].strip()

                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{text}\n\n")

    def _format_timestamp(self, seconds: float) -> str:
        """格式化时间戳为 SRT 格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def _merge_time_ranges(
        self,
        ranges: List[Tuple[float, float]],
        gap_threshold: float
    ) -> List[Tuple[float, float]]:
        """合并相邻的时间范围"""
        if not ranges:
            return []

        # 按开始时间排序
        sorted_ranges = sorted(ranges, key=lambda x: x[0])

        merged = [sorted_ranges[0]]

        for current in sorted_ranges[1:]:
            last = merged[-1]
            if current[0] - last[1] <= gap_threshold:
                # 合并
                merged[-1] = (last[0], max(last[1], current[1]))
            else:
                merged.append(current)

        return merged

    def _extract_ranges(
        self,
        input_path: str,
        output_path: str,
        time_ranges: List[Tuple[float, float]]
    ) -> bool:
        """从输入文件提取多个时间范围"""
        if len(time_ranges) == 1 and time_ranges[0] == (None, None):
            # 无时间限制，直接复制
            cmd = ["ffmpeg", "-i", input_path, "-c", "copy", "-y", output_path]
            return self._run_ffmpeg(cmd)

        # 构建复杂滤镜
        filter_parts = []
        for i, (start, end) in enumerate(time_ranges):
            if start is None:
                start = 0
            if end is None:
                filter_parts.append(f"[0:v]trim=start={start}[v{i}];[0:a]trim=start={start},asetpts=PTS-STARTPTS[a{i}]")
            else:
                filter_parts.append(f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[v{i}];[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[a{i}]")

        # 合并所有片段
        v_concat = "[v0]"
        a_concat = "[a0]"
        for i in range(1, len(time_ranges)):
            v_concat += f"[v{i}]"
            a_concat += f"[a{i}]"
        v_concat += f"concat=n={len(time_ranges)}:v=1:a=0[vout]"
        a_concat += f"concat=n={len(time_ranges)}:v=0:a=1[aout]"

        filter_parts.append(v_concat)
        filter_parts.append(a_concat)

        filter_complex = ";".join(filter_parts)

        cmd = [
            "ffmpeg", "-i", input_path,
            "-filter_complex", filter_complex,
            "-map", "[vout]", "-map", "[aout]",
            "-y", output_path
        ]

        return self._run_ffmpeg(cmd)

    def _remove_silence_audio(
        self,
        input_path: str,
        output_path: str,
        silence_thresh: float,
        min_silence_len: float
    ) -> bool:
        """去除音频中的静音"""
        cmd = [
            "ffmpeg", "-i", input_path,
            "-af", f"silenceremove=start_threshold={silence_thresh}dB:"
                   f"stop_threshold={silence_thresh}dB:"
                   f"start_periods=1:start_duration=0.1:"
                   f"detection=peak,silenceremove=start_periods=1",
            "-y", output_path
        ]

        print("正在去除静音...")
        return self._run_ffmpeg(cmd)

    def _remove_silence_video(
        self,
        input_path: str,
        output_path: str,
        silence_thresh: float,
        min_silence_len: float
    ) -> bool:
        """去除视频中的静音"""
        cmd = [
            "ffmpeg", "-i", input_path,
            "-af", f"silenceremove=start_threshold={silence_thresh}dB:"
                   f"stop_threshold={silence_thresh}dB:"
                   f"start_periods=1:start_duration=0.1",
            "-c:v", "copy",
            "-y", output_path
        ]

        print("正在去除静音...")
        return self._run_ffmpeg(cmd)

    def _run_ffmpeg(self, cmd: List[str]) -> bool:
        """运行 FFmpeg 命令"""
        print(f"执行: {' '.join(cmd[:5])}...")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg 错误: {e.stderr}")
            return False


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="FFmpeg Whisper 智能剪辑工具 - 结合 FFmpeg 和 Whisper 的音视频剪辑工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s transcribe video.mp4 --model base
  %(prog)s clip video.mp4 --keywords "重要" "关键点" --output clip.mp4
  %(prog)s trim video.mp4 --start 10 --end 60 --output trim.mp4
  %(prog)s info video.mp4
        """
    )

    parser.add_argument(
        "--model", "-m",
        choices=["tiny", "base", "small", "medium", "large"],
        default="base",
        help="Whisper 模型大小 (默认: base)"
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # transcribe 命令
    transcribe_parser = subparsers.add_parser(
        "transcribe",
        help="转录音视频文件"
    )
    transcribe_parser.add_argument("input", help="输入文件路径")
    transcribe_parser.add_argument(
        "--language", "-l",
        help="语言代码（如 zh, en, ja）"
    )
    transcribe_parser.add_argument(
        "--output", "-o",
        help="输出文件路径"
    )
    transcribe_parser.add_argument(
        "--format", "-f",
        choices=["srt", "json", "text"],
        default="srt",
        help="输出格式 (默认: srt)"
    )

    # clip 命令
    clip_parser = subparsers.add_parser(
        "clip",
        help="基于关键词剪辑"
    )
    clip_parser.add_argument("input", help="输入文件路径")
    clip_parser.add_argument(
        "--keywords", "-k",
        nargs="+",
        required=True,
        help="要搜索的关键词"
    )
    clip_parser.add_argument(
        "--output", "-o",
        required=True,
        help="输出文件路径"
    )
    clip_parser.add_argument(
        "--padding", "-p",
        type=float,
        default=0.5,
        help="每个片段前后添加的秒数 (默认: 0.5)"
    )
    clip_parser.add_argument(
        "--merge-gap", "-g",
        type=float,
        default=2.0,
        help="合并间隔小于此值的片段 (默认: 2.0)"
    )

    # trim 命令
    trim_parser = subparsers.add_parser(
        "trim",
        help="修剪音视频"
    )
    trim_parser.add_argument("input", help="输入文件路径")
    trim_parser.add_argument(
        "--output", "-o",
        required=True,
        help="输出文件路径"
    )
    trim_parser.add_argument(
        "--start", "-s",
        type=float,
        help="开始时间（秒）"
    )
    trim_parser.add_argument(
        "--end", "-e",
        type=float,
        help="结束时间（秒）"
    )

    # remove-silence 命令
    silence_parser = subparsers.add_parser(
        "remove-silence",
        help="去除静音片段"
    )
    silence_parser.add_argument("input", help="输入文件路径")
    silence_parser.add_argument(
        "--output", "-o",
        required=True,
        help="输出文件路径"
    )
    silence_parser.add_argument(
        "--threshold", "-t",
        type=float,
        default=-40,
        help="静音阈值 dB (默认: -40)"
    )

    # convert 命令
    convert_parser = subparsers.add_parser(
        "convert",
        help="转换格式"
    )
    convert_parser.add_argument("input", help="输入文件路径")
    convert_parser.add_argument(
        "--output", "-o",
        required=True,
        help="输出文件路径"
    )
    convert_parser.add_argument(
        "--codec", "-c",
        help="视频编码器"
    )
    convert_parser.add_argument(
        "--bitrate", "-b",
        default="192k",
        help="音频比特率 (默认: 192k)"
    )

    # info 命令
    info_parser = subparsers.add_parser(
        "info",
        help="查看媒体信息"
    )
    info_parser.add_argument("input", help="输入文件路径")

    return parser


def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # 初始化剪辑器
    clipper = FFmpegWhisperClipper(model_name=args.model)

    # 执行命令
    if args.command == "transcribe":
        output_path = args.output
        if not output_path:
            # 自动生成输出路径
            input_path = Path(args.input)
            output_path = str(input_path.with_suffix(f".{args.format}"))

        result = clipper.transcribe(
            args.input,
            language=args.language,
            output_format=args.format,
            output_path=output_path
        )

        print("\n转录结果预览:")
        print(result.get("text", "")[:500])

    elif args.command == "clip":
        success = clipper.clip_by_keywords(
            args.input,
            keywords=args.keywords,
            output_path=args.output,
            padding=args.padding,
            merge_gaps=args.merge_gap
        )

        if success:
            print(f"剪辑完成: {args.output}")
        else:
            print("剪辑失败!")
            sys.exit(1)

    elif args.command == "trim":
        success = clipper.trim(
            args.input,
            output_path=args.output,
            start=args.start,
            end=args.end
        )

        if success:
            print(f"修剪完成: {args.output}")
        else:
            print("修剪失败!")
            sys.exit(1)

    elif args.command == "remove-silence":
        success = clipper.remove_silence(
            args.input,
            output_path=args.output,
            silence_thresh=args.threshold
        )

        if success:
            print(f"静音去除完成: {args.output}")
        else:
            print("处理失败!")
            sys.exit(1)

    elif args.command == "convert":
        success = clipper.convert_format(
            args.input,
            output_path=args.output,
            codec=args.codec,
            bitrate=args.bitrate
        )

        if success:
            print(f"格式转换完成: {args.output}")
        else:
            print("转换失败!")
            sys.exit(1)

    elif args.command == "info":
        info = clipper.get_media_info(args.input)

        if info:
            print(f"\n文件: {args.input}")
            print(f"格式: {info.get('format', {}).get('format_name', 'N/A')}")
            print(f"时长: {info.get('format', {}).get('duration', 'N/A')} 秒")

            for stream in info.get('streams', []):
                codec_type = stream.get('codec_type', 'N/A')
                codec_name = stream.get('codec_name', 'N/A')

                if codec_type == 'video':
                    width = stream.get('width', 'N/A')
                    height = stream.get('height', 'N/A')
                    fps = stream.get('r_frame_rate', 'N/A')
                    print(f"视频: {codec_name} {width}x{height} @ {fps} fps")

                elif codec_type == 'audio':
                    sample_rate = stream.get('sample_rate', 'N/A')
                    channels = stream.get('channels', 'N/A')
                    print(f"音频: {codec_name} {sample_rate}Hz {channels}声道")
        else:
            print("无法获取媒体信息")


if __name__ == "__main__":
    main()
