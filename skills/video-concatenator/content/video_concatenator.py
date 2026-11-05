#!/usr/bin/env python3
"""
Video Concatenator - AI Video Concatenation Tool
Automatically sorts and concatenates multiple video clips by sequence number
"""

import argparse
import glob
import os
import re
import subprocess
import sys
import shutil
from pathlib import Path
from typing import List, Tuple, Optional


class VideoConcatenator:
    """Video concatenation handler"""

    # Supported video formats
    SUPPORTED_FORMATS = ['.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv', '.wmv']

    def __init__(self, quality: str = 'high'):
        self.quality = quality
        self.quality_settings = {
            'low': {'crf': 28, 'preset': 'veryfast'},
            'medium': {'crf': 23, 'preset': 'medium'},
            'high': {'crf': 18, 'preset': 'slow'}
        }

    def extract_sequence_number(self, filename: str) -> Tuple[int, str]:
        """
        Extract sequence number from filename
        Returns: (sequence_number, cleaned_filename)
        """
        basename = os.path.basename(filename)
        name_without_ext = os.path.splitext(basename)[0]

        # Multiple sequence matching patterns
        patterns = [
            r'(\d+)',                    # Pure number
            r'[_\-\s](\d+)$',           # Number at end of filename
            r'[_\-\s](\d+)[_\-\s]',     # Number in middle
            r'\((\d+)\)',               # Number in parentheses
            r'\[(\d+)\]',               # Number in brackets
        ]

        max_num = 0
        for pattern in patterns:
            matches = re.findall(pattern, name_without_ext)
            for match in matches:
                num = int(match)
                if num > max_num:
                    max_num = num

        return max_num, name_without_ext

    def get_video_duration(self, video_path: str) -> float:
        """Get video duration in seconds"""
        try:
            cmd = [
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except Exception:
            return 0.0

    def get_video_info(self, video_path: str) -> dict:
        """Get detailed video information"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet',
                '-print_format', 'json',
                '-show_format', '-show_streams',
                video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout
        except Exception:
            return {}

    def validate_videos(self, video_files: List[str]) -> List[str]:
        """Validate video file integrity"""
        valid_files = []
        for video in video_files:
            if not os.path.exists(video):
                print(f"  [WARN] File not found: {video}")
                continue
            if not os.path.isfile(video):
                print(f"  [WARN] Not a file: {video}")
                continue
            ext = os.path.splitext(video)[1].lower()
            if ext not in self.SUPPORTED_FORMATS:
                print(f"  [WARN] Unsupported format: {video}")
                continue
            valid_files.append(video)
        return valid_files

    def sort_videos_by_sequence(self, video_files: List[str]) -> List[str]:
        """Sort video files by sequence number"""
        def sort_key(path):
            num, _ = self.extract_sequence_number(path)
            return num

        return sorted(video_files, key=sort_key)

    def collect_videos_from_directory(self, directory: str, pattern: str = '*.mp4') -> List[str]:
        """Collect video files from directory"""
        videos = []

        # If pattern contains wildcard, use directly
        if '*' in pattern:
            search_pattern = os.path.join(directory, pattern)
            videos.extend(glob.glob(search_pattern))
        else:
            # Otherwise search all supported formats
            for ext in self.SUPPORTED_FORMATS:
                search_pattern = os.path.join(directory, f'*{ext}')
                videos.extend(glob.glob(search_pattern))

        # Deduplicate
        return list(set(videos))

    def create_concatenation_list(self, video_files: List[str], output_path: str) -> str:
        """Create ffmpeg concat list file"""
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        list_file = output_path + '.list'
        with open(list_file, 'w') as f:
            for video in video_files:
                f.write(f"file '{video}'\n")
        return list_file

    def concatenate_videos(self, video_files: List[str], output_path: str,
                          show_progress: bool = True) -> bool:
        """
        Concatenate videos
        Uses complex filter to ensure videos with different codecs can be concatenated correctly
        """
        if not video_files:
            print("[ERROR] No video files to concatenate")
            return False

        if len(video_files) == 1:
            # Only one video, just copy
            print(f"[INFO] Only 1 video file, copying directly...")
            shutil.copy2(video_files[0], output_path)
            print(f"[DONE] Output: {output_path}")
            return True

        # Get quality settings
        quality = self.quality_settings.get(self.quality, self.quality_settings['high'])

        print(f"\n[PROCESSING] Concatenating {len(video_files)} videos...")
        print(f"   Output: {output_path}")
        print(f"   Quality: {self.quality} (crf={quality['crf']}, preset={quality['preset']})")

        # Estimate total duration
        total_duration = sum(self.get_video_duration(v) for v in video_files)
        print(f"   Total duration: {total_duration:.1f} seconds")

        # Method 1: Use concat demuxer (for videos with same codec)
        list_file = self.create_concatenation_list(video_files, output_path)

        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', list_file,
            '-c:v', 'libx264',
            '-crf', str(quality['crf']),
            '-preset', quality['preset'],
            '-c:a', 'aac',
            '-b:a', '128k',
            '-movflags', '+faststart',
            output_path
        ]

        if show_progress:
            cmd.extend(['-progress', 'pipe:1'])

        try:
            print("\n[WORKING] Processing...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )

            # Clean up temp file
            if os.path.exists(list_file):
                os.remove(list_file)

            if result.returncode != 0:
                print(f"[WARN] Simple concatenation failed, trying complex filter...")
                return self._concatenate_with_complex_filter(video_files, output_path, quality)

            print(f"\n[DONE] Concatenation complete!")
            return True

        except Exception as e:
            print(f"[ERROR] Concatenation failed: {e}")
            return False

    def _concatenate_with_complex_filter(self, video_files: List[str],
                                          output_path: str, quality: dict) -> bool:
        """
        Concatenate videos using complex filter (for videos with different codecs)
        """
        try:
            # Build filter graph
            inputs = []
            for i, video in enumerate(video_files):
                inputs.extend(['-i', video])

            filter_parts = []
            for i in range(len(video_files)):
                filter_parts.append(f'[{i}:v][{i}:a]')

            filter_complex = f'{",".join(filter_parts)}concat=n={len(video_files)}:v=1:a=1[outv][outa]'

            cmd = [
                'ffmpeg', '-y'
            ] + inputs + [
                '-filter_complex', filter_complex,
                '-map', '[outv]',
                '-map', '[outa]',
                '-c:v', 'libx264',
                '-crf', str(quality['crf']),
                '-preset', quality['preset'],
                '-c:a', 'aac',
                '-b:a', '128k',
                '-movflags', '+faststart',
                output_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0

        except Exception as e:
            print(f"[ERROR] Complex filter concatenation also failed: {e}")
            return False

    def run(self, input_dir: Optional[str] = None,
            files: Optional[List[str]] = None,
            output: str = 'concatenated.mp4',
            pattern: str = '*.mp4',
            delete_input: bool = False) -> bool:
        """Main execution method"""
        print("=" * 50)
        print("VIDEO CONCATENATOR - AI Video Concatenation Tool")
        print("=" * 50)

        # Collect video files
        video_files = []

        if input_dir:
            print(f"\n[SCANNING] Collecting videos from: {input_dir}")
            video_files = self.collect_videos_from_directory(input_dir, pattern)
        elif files:
            print(f"\n[INFO] Using specified file list")
            video_files = files
        else:
            print("[ERROR] Please specify --input-dir or --files")
            return False

        # Validate files
        video_files = self.validate_videos(video_files)

        if not video_files:
            print("[ERROR] No valid video files found")
            return False

        # Sort
        video_files = self.sort_videos_by_sequence(video_files)

        print(f"\n[FOUND] {len(video_files)} video files:")
        for i, video in enumerate(video_files, 1):
            duration = self.get_video_duration(video)
            num, _ = self.extract_sequence_number(video)
            print(f"   {i}. [{num:03d}] {os.path.basename(video)} ({duration:.1f}s)")

        # Execute concatenation
        success = self.concatenate_videos(video_files, output)

        if success and delete_input:
            print(f"\n[CLEANUP] Deleting source files...")
            for video in video_files:
                try:
                    os.remove(video)
                    print(f"   Deleted: {os.path.basename(video)}")
                except Exception as e:
                    print(f"   Failed to delete: {video} - {e}")

        return success


def main():
    parser = argparse.ArgumentParser(
        description='Video Concatenator - AI Video Concatenation Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--input-dir', '-i',
                        help='Video directory')
    parser.add_argument('--files', '-f', nargs='+',
                        help='Video file list')
    parser.add_argument('--output', '-o', default='concatenated.mp4',
                        help='Output file path (default: concatenated.mp4)')
    parser.add_argument('--pattern', '-p', default='*.mp4',
                        help='File matching pattern (default: *.mp4)')
    parser.add_argument('--quality', '-q', choices=['low', 'medium', 'high'],
                        default='high',
                        help='Output quality (default: high)')
    parser.add_argument('--delete-input', '-d', action='store_true',
                        help='Delete source files after concatenation')

    args = parser.parse_args()

    concatenator = VideoConcatenator(quality=args.quality)

    success = concatenator.run(
        input_dir=args.input_dir,
        files=args.files,
        output=args.output,
        pattern=args.pattern,
        delete_input=args.delete_input
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
