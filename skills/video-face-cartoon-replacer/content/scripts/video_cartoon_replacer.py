#!/usr/bin/env python3
"""
视频人脸卡通替换器 - 核心处理模块
将视频中指定的人物头像替换为卡通形象，保护人物隐私
"""

import os
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import json
import tempfile
import subprocess
import sys

# 尝试导入可选依赖
try:
    from mtcnn import MTCNN
    MTCNN_AVAILABLE = True
except ImportError:
    MTCNN_AVAILABLE = False
    print("Warning: MTCNN not available, using fallback face detection")

try:
    import torch
    from diffusers import StableDiffusionInpaintPipeline
    SD_AVAILABLE = True
except ImportError:
    SD_AVAILABLE = False
    print("Warning: Stable Diffusion not available, using template-based replacement")


class CartoonFaceReplacer:
    """视频人脸卡通替换器"""

    CARTAGON_TYPES = {
        'cat': {'name': 'Cat', 'emoji': '🐱', 'prompt': 'cute cartoon cat face'},
        'tiger': {'name': 'Tiger', 'emoji': '🐯', 'prompt': 'majestic cartoon tiger face'},
        'lion': {'name': 'Lion', 'emoji': '🦁', 'prompt': 'king cartoon lion face'},
        'bear': {'name': 'Bear', 'emoji': '🐻', 'prompt': 'cute cartoon bear face'},
        'rabbit': {'name': 'Rabbit', 'emoji': '🐰', 'prompt': 'adorable cartoon rabbit face'},
        'panda': {'name': 'Panda', 'emoji': '🐼', 'prompt': 'cute cartoon panda face'},
        'fox': {'name': 'Fox', 'emoji': '🦊', 'prompt': 'clever cartoon fox face'},
        'dog': {'name': 'Dog', 'emoji': '🐶', 'prompt': 'friendly cartoon dog face'}
    }

    def __init__(self, assets_dir: Optional[str] = None):
        """
        初始化卡通替换器

        Args:
            assets_dir: 卡通素材目录路径
        """
        self.assets_dir = assets_dir or os.path.join(
            os.path.dirname(__file__), '..', 'assets', 'cartoon_faces'
        )
        self.detector = None
        self.sd_pipeline = None

        # 初始化人脸检测器
        self._init_face_detector()

    def _init_face_detector(self):
        """初始化人脸检测器"""
        if MTCNN_AVAILABLE:
            try:
                self.detector = MTCNN()
                print("Using MTCNN for face detection")
            except Exception as e:
                print(f"MTCNN initialization failed: {e}")
                self.detector = None

        if self.detector is None:
            print("Using OpenCV Haar Cascade for face detection")

    def _detect_faces_opencv(self, image: np.ndarray) -> List[Dict]:
        """
        使用OpenCV检测人脸

        Args:
            image: 输入图像 (BGR格式)

        Returns:
            人脸区域列表
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        results = []
        for (x, y, w, h) in faces:
            results.append({
                'box': [int(x), int(y), int(x + w), int(y + h)],
                'confidence': 0.9,
                'keypoints': None
            })
        return results

    def _detect_faces_mtcnn(self, image: np.ndarray) -> List[Dict]:
        """
        使用MTCNN检测人脸

        Args:
            image: 输入图像 (RGB格式)

        Returns:
            人脸区域列表
        """
        results = self.detector.detect_faces(image)
        formatted = []
        for face in results:
            box = face['box']
            formatted.append({
                'box': [box[0], box[1], box[0] + box[2], box[1] + box[3]],
                'confidence': face['confidence'],
                'keypoints': face.get('keypoints')
            })
        return formatted

    def detect_faces(self, image: np.ndarray) -> List[Dict]:
        """
        检测图像中的人脸

        Args:
            image: 输入图像 (BGR格式)

        Returns:
            人脸区域列表
        """
        if MTCNN_AVAILABLE and self.detector:
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            return self._detect_faces_mtcnn(rgb)
        else:
            return self._detect_faces_opencv(image)

    def load_cartoon_template(self, cartoon_type: str, size: Tuple[int, int]) -> Optional[Image.Image]:
        """
        加载卡通模板

        Args:
            cartoon_type: 卡通类型 (cat, tiger, lion等)
            size: 目标尺寸 (width, height)

        Returns:
            卡通图像
        """
        template_path = os.path.join(self.assets_dir, f'{cartoon_type}.png')

        if os.path.exists(template_path):
            template = Image.open(template_path).convert('RGBA')
            template = template.resize(size, Image.LANCZOS)
            return template

        # 如果模板不存在，生成简单的卡通图像
        return self._generate_cartoon_image(cartoon_type, size)

    def _generate_cartoon_image(self, cartoon_type: str, size: Tuple[int, int]) -> Image.Image:
        """
        生成卡通图像（备用方案）

        Args:
            cartoon_type: 卡通类型
            size: 目标尺寸

        Returns:
            卡通图像
        """
        # 创建一个简单的彩色圆形作为占位符
        img = Image.new('RGBA', size, (255, 200, 100, 255))
        return img

    def blend_cartoon_face(
        self,
        frame: np.ndarray,
        bbox: List[int],
        cartoon_img: Image.Image,
        blend_mode: str = 'alpha'
    ) -> np.ndarray:
        """
        将卡通人脸融入原帧

        Args:
            frame: 原视频帧 (BGR格式)
            bbox: 人脸边界框 [x1, y1, x2, y2]
            cartoon_img: 卡通图像
            blend_mode: 融合模式

        Returns:
            处理后的帧
        """
        x1, y1, x2, y2 = bbox
        h, w = frame.shape[:2]

        # 确保边界在图像范围内
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)

        # 提取人脸区域
        face_roi = frame[y1:y2, x1:x2]
        if face_roi.size == 0:
            return frame

        # 转换卡通图像到OpenCV格式
        cartoon_cv = cv2.cvtColor(np.array(cartoon_img), cv2.COLOR_RGBA2BGRA)

        # 调整卡通图像大小
        face_h, face_w = face_roi.shape[:2]
        cartoon_resized = cv2.resize(cartoon_cv, (face_w, face_h))

        # Alpha融合
        if cartoon_resized.shape[2] == 4:
            alpha = cartoon_resized[:, :, 3] / 255.0
            alpha = np.stack([alpha] * 3, axis=-1)

            # 平滑边缘
            alpha = cv2.GaussianBlur(alpha, (5, 5), 0)

            # 融合
            blended = (cartoon_resized[:, :, :3] * alpha + face_roi * (1 - alpha)).astype(np.uint8)
        else:
            blended = cartoon_resized

        # 替换原帧中的区域
        result = frame.copy()
        result[y1:y2, x1:x2] = blended

        return result

    def process_frame(
        self,
        frame: np.ndarray,
        user_annotations: List[List[int]],
        cartoon_type: str,
        use_ai_generation: bool = False
    ) -> np.ndarray:
        """
        处理单帧图像

        Args:
            frame: 输入帧
            user_annotations: 用户标注的区域列表 [[x1,y1,x2,y2], ...]
            cartoon_type: 卡通类型
            use_ai_generation: 是否使用AI生成

        Returns:
            处理后的帧
        """
        result = frame.copy()

        for bbox in user_annotations:
            # 获取区域尺寸
            x1, y1, x2, y2 = bbox
            width, height = x2 - x1, y2 - y1

            if width <= 0 or height <= 0:
                continue

            # 加载或生成卡通图像
            if use_ai_generation and SD_AVAILABLE:
                cartoon_img = self._generate_ai_cartoon(frame, bbox, cartoon_type)
            else:
                cartoon_img = self.load_cartoon_template(cartoon_type, (width, height))

            # 融合卡通人脸
            result = self.blend_cartoon_face(result, bbox, cartoon_img)

        return result

    def _generate_ai_cartoon(self, frame: np.ndarray, bbox: List[int], cartoon_type: str) -> Image.Image:
        """使用AI生成卡通人脸"""
        # 提取人脸区域
        x1, y1, x2, y2 = bbox
        face = frame[y1:y2, x1:x2]

        # 使用模板作为备用
        return self._generate_cartoon_image(cartoon_type, (x2-x1, y2-y1))

    def extract_video_frames(self, video_path: str, output_dir: str) -> List[str]:
        """
        提取视频所有帧

        Args:
            video_path: 视频路径
            output_dir: 输出目录

        Returns:
            帧文件路径列表
        """
        os.makedirs(output_dir, exist_ok=True)

        cap = cv2.VideoCapture(video_path)
        frames = []
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_path = os.path.join(output_dir, f'frame_{frame_idx:06d}.jpg')
            cv2.imwrite(frame_path, frame)
            frames.append(frame_path)
            frame_idx += 1

        cap.release()
        return frames

    def process_video(
        self,
        video_path: str,
        annotations: Dict[int, List[List[int]]],  # frame_idx -> [[x1,y1,x2,y2], ...]
        cartoon_type: str,
        output_path: str,
        use_ai_generation: bool = False,
        progress_callback=None
    ) -> bool:
        """
        处理视频，将指定区域替换为卡通形象

        Args:
            video_path: 输入视频路径
            annotations: 帧标注字典 {帧索引: [[x1,y1,x2,y2], ...]}
            cartoon_type: 卡通类型
            output_path: 输出视频路径
            use_ai_generation: 是否使用AI生成
            progress_callback: 进度回调函数

        Returns:
            是否成功
        """
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {video_path}")

            # 获取视频属性
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            # 创建输出视频
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

            frame_idx = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # 检查是否有该帧的标注
                if frame_idx in annotations:
                    frame = self.process_frame(
                        frame,
                        annotations[frame_idx],
                        cartoon_type,
                        use_ai_generation
                    )

                out.write(frame)
                frame_idx += 1

                # 进度回调
                if progress_callback:
                    progress_callback(frame_idx / total_frames)

            cap.release()
            out.release()

            # 使用FFmpeg重新编码以获得更好的兼容性
            self._reencode_video(output_path)

            return True

        except Exception as e:
            print(f"Video processing error: {e}")
            return False

    def _reencode_video(self, video_path: str, temp_path: Optional[str] = None):
        """使用FFmpeg重新编码视频"""
        if temp_path is None:
            temp_path = video_path + '.tmp.mp4'

        try:
            subprocess.run([
                'ffmpeg', '-i', video_path,
                '-c:v', 'libx264', '-preset', 'medium',
                '-crf', '23', '-c:a', 'aac', '-b:a', '128k',
                '-y', temp_path
            ], capture_output=True, check=True)

            os.replace(temp_path, video_path)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("FFmpeg not available, keeping original encoding")

    def extract_first_frame(self, video_path: str, output_path: str) -> bool:
        """
        提取视频首帧

        Args:
            video_path: 视频路径
            output_path: 输出图像路径

        Returns:
            是否成功
        """
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        cap.release()

        if ret:
            cv2.imwrite(output_path, frame)
            return True
        return False

    def get_available_cartoon_types(self) -> Dict[str, Dict]:
        """获取可用的卡通类型"""
        return self.CARTAGON_TYPES.copy()


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='视频人脸卡通替换器')
    parser.add_argument('--video', '-i', required=True, help='输入视频路径')
    parser.add_argument('--output', '-o', required=True, help='输出视频路径')
    parser.add_argument('--annotations', '-a', required=True, help='标注JSON文件路径')
    parser.add_argument('--cartoon', '-c', default='cat',
                        choices=list(CartoonFaceReplacer.CARTAGON_TYPES.keys()),
                        help='卡通类型')
    parser.add_argument('--assets-dir', help='卡通素材目录')

    args = parser.parse_args()

    # 加载标注
    with open(args.annotations, 'r') as f:
        annotations = json.load(f)

    # 转换标注格式
    annotations = {int(k): v for k, v in annotations.items()}

    # 处理视频
    replacer = CartoonFaceReplacer(assets_dir=args.assets_dir)
    success = replacer.process_video(
        args.video,
        annotations,
        args.cartoon,
        args.output
    )

    if success:
        print(f"视频处理完成: {args.output}")
    else:
        print("视频处理失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
