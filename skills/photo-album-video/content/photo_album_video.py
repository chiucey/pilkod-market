"""
Photo Album Video Generator
将多张图片连接成带过渡动画和背景音乐的相册视频
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

import numpy as np
from PIL import Image
from moviepy import (
    ImageClip,
    VideoFileClip,
    AudioFileClip,
    CompositeVideoClip,
    CompositeAudioClip,
    ColorClip,
    concatenate_videoclips,
    vfx,
    afx,
    io
)
from moviepy.video.fx.all import scroll

# 尝试导入可选依赖
try:
    from moviepy.video.fx.all import blur as video_blur
    BLUR_AVAILABLE = True
except ImportError:
    BLUR_AVAILABLE = False


class TransitionType(Enum):
    """过渡效果类型枚举"""
    FADE = "fade"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    SLIDE_UP = "slide_up"
    SLIDE_DOWN = "slide_down"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    DISSOLVE = "dissolve"
    WIPE = "wipe"
    BLUR = "blur"


class Resolution(Enum):
    """分辨率配置"""
    HD = "720p"
    FHD = "1080p"
    UHD_4K = "4k"

    @property
    def dimensions(self) -> tuple:
        if self.value == "720p":
            return (1280, 720)
        elif self.value == "1080p":
            return (1920, 1080)
        elif self.value == "4k":
            return (3840, 2160)
        return (1920, 1080)


@dataclass
class AlbumConfig:
    """相册视频配置类"""
    images: List[str]
    music: Optional[str] = None
    transition: str = "fade"
    image_duration: float = 3.0
    transition_duration: float = 1.0
    output: str = "output.mp4"
    resolution: str = "1080p"
    fps: int = 30
    music_volume: float = 0.7
    bg_color: str = "black"
    quality: str = "high"

    def __post_init__(self):
        """验证配置参数"""
        if not self.images:
            raise ValueError("至少需要一张图片")

        if self.image_duration < 0.5:
            raise ValueError("图片显示时长至少为0.5秒")

        if self.transition_duration < 0.3:
            raise ValueError("过渡动画时长至少为0.3秒")

        if self.transition_duration > self.image_duration:
            raise ValueError("过渡动画时长不能超过图片显示时长")

        if not 0 <= self.music_volume <= 1:
            raise ValueError("音量值必须在0.0到1.0之间")


class PhotoAlbumGenerator:
    """相册视频生成器类"""

    def __init__(self):
        """初始化生成器"""
        self.supported_image_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
        self.supported_audio_formats = {'.mp3', '.wav', '.aac', '.ogg', '.m4a'}
        self.quality_presets = {
            'low': {'codec': 'libx264', 'bitrate': '1000k'},
            'medium': {'codec': 'libx264', 'bitrate': '3000k'},
            'high': {'codec': 'libx264', 'bitrate': '8000k'}
        }

    def _validate_file(self, file_path: str, file_type: str = 'image') -> Path:
        """验证文件是否存在且格式正确"""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        if file_type == 'image' and path.suffix.lower() not in self.supported_image_formats:
            raise ValueError(f"不支持的图片格式: {path.suffix}，支持的格式: {self.supported_image_formats}")

        if file_type == 'audio' and path.suffix.lower() not in self.supported_audio_formats:
            raise ValueError(f"不支持的音频格式: {path.suffix}，支持的格式: {self.supported_audio_formats}")

        return path

    def _get_resolution(self, resolution: str) -> tuple:
        """获取分辨率尺寸"""
        resolution_map = {
            '720p': (1280, 720),
            '1080p': (1920, 1080),
            '4k': (3840, 2160)
        }
        return resolution_map.get(resolution, (1920, 1080))

    def _resize_image(self, img_path: Path, target_size: tuple, bg_color: str = 'black') -> np.ndarray:
        """调整图片大小，保持比例，填充背景"""
        with Image.open(img_path) as img:
            # 转换为RGB模式
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # 计算缩放比例
            img_width, img_height = img.size
            target_width, target_height = target_size

            ratio = min(target_width / img_width, target_height / img_height)
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)

            # 缩放图片
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # 创建背景
            bg = Image.new('RGB', target_size, bg_color)

            # 计算粘贴位置（居中）
            x = (target_width - new_width) // 2
            y = (target_height - new_height) // 2

            # 粘贴图片
            bg.paste(img, (x, y))

            return np.array(bg)

    def _create_image_clip(self, img_path: str, duration: float, resolution: str,
                          bg_color: str, start_time: float = 0) -> ImageClip:
        """创建单个图片片段"""
        path = self._validate_file(img_path, 'image')
        target_size = self._get_resolution(resolution)

        # 调整图片大小
        img_array = self._resize_image(path, target_size, bg_color)

        # 创建ImageClip
        clip = ImageClip(img_array).with_duration(duration)

        return clip

    def _apply_transition_fade(self, clip1: ImageClip, clip2: ImageClip,
                               transition_duration: float) -> List[ImageClip]:
        """应用淡入淡出过渡"""
        # 第一个片段截取最后部分用于过渡
        clip1_part = clip1.with_duration(clip1.duration - transition_duration)

        # 淡出效果
        fade_out = clip1.with_duration(transition_duration).with_effects([vfx.FadeOut(transition_duration)])

        # 淡入效果
        fade_in = clip2.with_duration(transition_duration).with_effects([vfx.FadeIn(transition_duration)])

        # 中间片段
        middle = clip2.with_duration(clip2.duration - 2 * transition_duration)

        return [clip1_part, fade_out.crossfadeout(transition_duration),
                fade_in.crossfadein(transition_duration), middle]

    def _apply_transition_slide(self, clip1: ImageClip, clip2: ImageClip,
                                  transition_duration: float, direction: str) -> List[ImageClip]:
        """应用滑动过渡效果"""
        w, h = clip1.size

        # 确定移动方向
        if direction == 'left':
            # clip2从右向左滑入
            def slide_func(get_frame, t):
                if t < transition_duration:
                    progress = t / transition_duration
                    frame1 = get_frame(t)
                    # 计算clip2的位移
                    x_offset = int(w * (1 - progress))
                    frame2 = clip2.get_frame(t)
                    # 简单叠加（实际应该用复合视频）
                    result = frame1.copy()
                    if x_offset < w:
                        end_x = min(x_offset + w, w)
                        result[:, max(0, x_offset):end_x] = frame2[:, :end_x - max(0, x_offset)]
                    return result
                else:
                    return clip2.get_frame(t - transition_duration)

            # 使用mask实现滑动
            clip1_with_mask = clip1.with_effects([
                vfx.SlideIn(transition_duration, direction)
            ])

        elif direction == 'right':
            # clip2从左向右滑入
            clip2_with_mask = clip2.with_effects([
                vfx.SlideIn(transition_duration, 'right')
            ])
            return [clip1, clip2_with_mask]

        elif direction == 'up':
            # clip2从下向上滑入
            clip2_with_mask = clip2.with_effects([
                vfx.SlideIn(transition_duration, 'up')
            ])
            return [clip1, clip2_with_mask]

        elif direction == 'down':
            # clip2从上向下滑入
            clip2_with_mask = clip2.with_effects([
                vfx.SlideIn(transition_duration, 'down')
            ])
            return [clip1, clip2_with_mask]

        return [clip1, clip2]

    def _apply_transition_zoom(self, clip1: ImageClip, clip2: ImageClip,
                                transition_duration: float, zoom_type: str) -> List[ImageClip]:
        """应用缩放过渡效果"""
        if zoom_type == 'in':
            # 放大效果
            clip2_transformed = clip2.with_effects([
                vfx.ZoomIn(transition_duration)
            ])
        else:  # zoom_out
            # 缩小效果
            clip2_transformed = clip2.with_effects([
                vfx.ZoomOut(transition_duration)
            ])

        return [clip1, clip2_transformed]

    def _apply_transition_dissolve(self, clip1: ImageClip, clip2: ImageClip,
                                    transition_duration: float) -> List[ImageClip]:
        """应用溶解过渡效果"""
        # 使用crossfade实现溶解
        return [clip1, clip2.crossfadein(transition_duration)]

    def _apply_transition_wipe(self, clip1: ImageClip, clip2: ImageClip,
                               transition_duration: float) -> List[ImageClip]:
        """应用擦拭过渡效果"""
        # 使用mask实现擦拭效果
        def make_wipe_mask(t):
            progress = min(t / transition_duration, 1.0)
            w, h = clip1.size
            mask = np.zeros((h, w), dtype=float)
            wipe_width = int(w * progress)
            if wipe_width > 0:
                mask[:, :wipe_width] = 1.0
            return mask

        clip2_with_mask = clip2.with_mask_layer(
            ImageClip(make_wipe_mask, ismask=True, duration=transition_duration)
        )

        return [clip1, clip2_with_mask]

    def _apply_transition_blur(self, clip1: ImageClip, clip2: ImageClip,
                                transition_duration: float) -> List[ImageClip]:
        """应用模糊过渡效果"""
        if not BLUR_AVAILABLE:
            # 如果模糊不可用，使用淡入淡出代替
            return self._apply_transition_fade(clip1, clip2, transition_duration)

        # 创建模糊过渡
        blur_clip1 = clip1.with_effects([video_blur(0, transition_duration)])
        blur_clip2 = clip2.with_effects([video_blur(0, transition_duration)])

        return [blur_clip1.crossfadeout(transition_duration * 0.5),
                blur_clip2.crossfadein(transition_duration * 0.5)]

    def _create_transition_clips(self, clip1: ImageClip, clip2: ImageClip,
                                  transition_type: str, transition_duration: float) -> List[ImageClip]:
        """根据类型创建过渡效果"""
        transition_map = {
            'fade': self._apply_transition_fade,
            'slide_left': lambda c1, c2, td: self._apply_transition_slide(c1, c2, td, 'left'),
            'slide_right': lambda c1, c2, td: self._apply_transition_slide(c1, c2, td, 'right'),
            'slide_up': lambda c1, c2, td: self._apply_transition_slide(c1, c2, td, 'up'),
            'slide_down': lambda c1, c2, td: self._apply_transition_slide(c1, c2, td, 'down'),
            'zoom_in': self._apply_transition_zoom,
            'zoom_out': lambda c1, c2, td: self._apply_transition_zoom(c1, c2, td, 'out'),
            'dissolve': self._apply_transition_dissolve,
            'wipe': self._apply_transition_wipe,
            'blur': self._apply_transition_blur
        }

        handler = transition_map.get(transition_type, self._apply_transition_fade)
        return handler(clip1, clip2, transition_duration)

    def _add_background_music(self, video: VideoFileClip, music_path: str, volume: float) -> VideoFileClip:
        """添加背景音乐"""
        if not music_path:
            return video

        music_path = self._validate_file(music_path, 'audio')

        audio = AudioFileClip(str(music_path))

        # 如果音乐时长短于视频，循环播放
        if audio.duration < video.duration:
            loops_needed = int(np.ceil(video.duration / audio.duration))
            audio = audio.loop(n=loops_needed)
            audio = audio.with_duration(video.duration)

        # 调整音量
        audio = audio.with_volume_scaled(volume)

        # 组合音频
        video = video.with_audio(audio)

        return video

    def create_video(self, config: Dict[str, Any]) -> str:
        """
        创建相册视频

        Args:
            config: 配置字典，包含以下键:
                - images: List[str] - 图片路径列表
                - music: str - 背景音乐路径（可选）
                - transition: str - 过渡效果类型
                - image_duration: float - 每张图片显示时长
                - transition_duration: float - 过渡动画时长
                - output: str - 输出文件路径
                - resolution: str - 输出分辨率
                - fps: int - 帧率
                - music_volume: float - 背景音乐音量
                - bg_color: str - 背景填充色
                - quality: str - 输出质量

        Returns:
            str: 生成的视频文件路径
        """
        # 解析配置
        album_config = AlbumConfig(**config)

        # 验证所有图片
        for img_path in album_config.images:
            self._validate_file(img_path, 'image')

        # 验证音乐（如果提供）
        if album_config.music:
            self._validate_file(album_config.music, 'audio')

        # 获取分辨率
        resolution = self._get_resolution(album_config.resolution)

        print(f"开始处理 {len(album_config.images)} 张图片...")
        print(f"分辨率: {album_config.resolution} ({resolution[0]}x{resolution[1]})")
        print(f"过渡效果: {album_config.transition}")

        # 创建所有图片片段
        clips = []
        for i, img_path in enumerate(album_config.images):
            print(f"处理图片 {i+1}/{len(album_config.images)}: {img_path}")

            # 计算每张图片的总时长（包含过渡）
            duration = album_config.image_duration

            clip = self._create_image_clip(
                img_path,
                duration,
                album_config.resolution,
                album_config.bg_color
            )
            clips.append(clip)

        # 处理过渡效果
        print("应用过渡效果...")
        final_clips = []

        if len(clips) == 1:
            final_clips = clips
        else:
            for i in range(len(clips) - 1):
                if i == 0:
                    # 第一张图片应用前过渡
                    clip1 = clips[i]
                    clip2 = clips[i + 1]
                    transition_clips = self._create_transition_clips(
                        clip1, clip2,
                        album_config.transition,
                        album_config.transition_duration
                    )
                    final_clips.extend(transition_clips[:-1])  # 最后一个会被下一个覆盖
                else:
                    # 中间图片
                    clip1 = clips[i]
                    clip2 = clips[i + 1]
                    transition_clips = self._create_transition_clips(
                        clip1, clip2,
                        album_config.transition,
                        album_config.transition_duration
                    )
                    # 保留中间的过渡效果
                    if len(transition_clips) > 2:
                        final_clips.append(transition_clips[1])
                    final_clips.append(transition_clips[-1])

            # 确保最后一张图片被包含
            if final_clips[-1].duration < clips[-1].duration:
                final_clips.append(clips[-1])

        # 合并所有片段
        print("合并视频片段...")
        if len(final_clips) > 1:
            video = concatenate_videoclips(final_clips, method="compose")
        else:
            video = final_clips[0]

        # 添加背景音乐
        if album_config.music:
            print("添加背景音乐...")
            video = self._add_background_music(video, album_config.music, album_config.music_volume)

        # 设置帧率
        video = video.with_fps(album_config.fps)

        # 获取编码设置
        codec_info = self.quality_presets.get(album_config.quality, self.quality_presets['high'])

        # 输出视频
        print(f"导出视频到: {album_config.output}")
        video.write_videofile(
            album_config.output,
            codec=codec_info['codec'],
            bitrate=codec_info['bitrate'],
            audio_codec='aac',
            audio_bitrate='192k',
            threads=4,
            logger=None  # 禁用进度条输出
        )

        # 清理资源
        video.close()
        for clip in clips:
            clip.close()

        print(f"视频生成完成: {album_config.output}")
        return album_config.output


# 便捷函数
def create_photo_album(
    images: List[str],
    output: str = "album.mp4",
    music: Optional[str] = None,
    transition: str = "fade",
    image_duration: float = 3.0,
    transition_duration: float = 1.0,
    resolution: str = "1080p",
    music_volume: float = 0.7
) -> str:
    """
    便捷函数：创建相册视频

    Args:
        images: 图片路径列表
        output: 输出文件路径
        music: 背景音乐路径
        transition: 过渡效果类型
        image_duration: 每张图片显示时长
        transition_duration: 过渡动画时长
        resolution: 输出分辨率
        music_volume: 背景音乐音量

    Returns:
        str: 生成的视频文件路径
    """
    generator = PhotoAlbumGenerator()

    config = {
        'images': images,
        'music': music,
        'transition': transition,
        'image_duration': image_duration,
        'transition_duration': transition_duration,
        'output': output,
        'resolution': resolution,
        'music_volume': music_volume
    }

    return generator.create_video(config)


if __name__ == "__main__":
    # 示例用法
    import argparse

    parser = argparse.ArgumentParser(description='相册视频生成器')
    parser.add_argument('images', nargs='+', help='图片文件路径')
    parser.add_argument('-o', '--output', default='album.mp4', help='输出文件路径')
    parser.add_argument('-m', '--music', help='背景音乐路径')
    parser.add_argument('-t', '--transition', default='fade',
                        choices=['fade', 'slide_left', 'slide_right', 'slide_up', 'slide_down',
                                'zoom_in', 'zoom_out', 'dissolve', 'wipe', 'blur'],
                        help='过渡效果类型')
    parser.add_argument('-d', '--duration', type=float, default=3.0, help='每张图片显示时长')
    parser.add_argument('-td', '--transition-duration', type=float, default=1.0, help='过渡动画时长')
    parser.add_argument('-r', '--resolution', default='1080p', choices=['720p', '1080p', '4k'], help='输出分辨率')
    parser.add_argument('-v', '--volume', type=float, default=0.7, help='背景音乐音量')

    args = parser.parse_args()

    generator = PhotoAlbumGenerator()
    config = {
        'images': args.images,
        'music': args.music,
        'transition': args.transition,
        'image_duration': args.duration,
        'transition_duration': args.transition_duration,
        'output': args.output,
        'resolution': args.resolution,
        'music_volume': args.volume
    }

    result = generator.create_video(config)
    print(f"视频已生成: {result}")
