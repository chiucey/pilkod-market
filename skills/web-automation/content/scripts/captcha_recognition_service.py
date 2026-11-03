"""
PaddleOCR 3.x 验证码识别服务

支持功能：
- 图形验证码识别（数字、字母、混合）
- 验证码预处理（去噪、二值化、增强）
- 干扰线和干扰点处理
- 多种验证码类型支持
"""

import cv2
import numpy as np
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path


class CaptchaRecognitionService:
    """验证码识别服务类"""

    def __init__(self, use_gpu: bool = False, enhance: bool = True):
        """
        初始化验证码识别服务

        Args:
            use_gpu: 是否使用 GPU
            enhance: 是否进行图像增强
        """
        self.use_gpu = use_gpu
        self.enhance = enhance

        try:
            from paddleocr import PaddleOCR

            # 初始化 OCR（使用轻量级模型，适合验证码识别）
            self.ocr = PaddleOCR(
                use_angle_cls=False,  # 验证码通常不需要方向分类
                lang='en',  # 验证码通常是字母和数字
                use_gpu=use_gpu,
                show_log=False,
                # 使用轻量级检测和识别模型
                det_model_dir=None,  # 使用默认轻量级模型
                rec_model_dir=None
            )

            self._initialized = True
        except Exception as e:
            print(f"初始化验证码识别服务失败: {e}")
            self._initialized = False

    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        预处理验证码图像

        处理步骤：
        1. 读取图像
        2. 转为灰度图
        3. 去噪（高斯模糊）
        4. 二值化（自适应阈值）
        5. 去除干扰线和干扰点
        6. 形态学操作（增强字符）

        Args:
            image_path: 图像路径

        Returns:
            处理后的图像
        """
        # 1. 读取图像
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"无法读取图像: {image_path}")

        # 2. 转为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 3. 去噪（高斯模糊）
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)

        # 4. 二值化（自适应阈值）
        binary = cv2.adaptiveThreshold(
            blurred, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        # 5. 去除干扰线和干扰点
        denoised = self._remove_noise(binary)

        # 6. 形态学操作（增强字符）
        kernel = np.ones((2, 2), np.uint8)
        enhanced = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)

        return enhanced

    def _remove_noise(self, binary: np.ndarray) -> np.ndarray:
        """
        去除干扰线和干扰点

        Args:
            binary: 二值化图像

        Returns:
            去噪后的图像
        """
        # 使用连通区域分析去除小噪点
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, 8, cv2.CV_32S)

        # 创建输出图像
        output = np.zeros(binary.shape, dtype=np.uint8)

        # 过滤小的连通区域（噪点）
        min_area = 20  # 最小区域面积
        for i in range(1, num_labels):
            area = stats[i, cv2.CC_STAT_AREA]
            if area >= min_area:
                output[labels == i] = 255

        return output

    def recognize(self, image_path: str,
                  preprocess: bool = True,
                  pattern: Optional[str] = None) -> Dict[str, Any]:
        """
        识别验证码

        Args:
            image_path: 验证码图像路径
            preprocess: 是否进行预处理
            pattern: 正则表达式模式（用于提取特定格式的验证码）

        Returns:
            识别结果，包含验证码文本、置信度
        """
        if not self._initialized:
            return {
                'success': False,
                'error': '验证码识别服务未初始化'
            }

        try:
            # 预处理图像
            if preprocess:
                processed_image = self.preprocess_image(image_path)
                # 保存预处理后的图像（用于调试）
                temp_path = f"temp_captcha_{Path(image_path).stem}.png"
                cv2.imwrite(temp_path, processed_image)
                ocr_path = temp_path
            else:
                ocr_path = image_path

            # 使用 OCR 识别
            result = self.ocr.ocr(ocr_path, cls=False)

            # 清理临时文件
            if preprocess and 'temp_path' in locals():
                import os
                if os.path.exists(temp_path):
                    os.remove(temp_path)

            # 处理识别结果
            if not result or result[0] is None:
                return {
                    'success': False,
                    'text': '',
                    'confidence': 0.0,
                    'error': '未能识别验证码'
                }

            # 提取所有识别到的文本
            texts = []
            confidences = []

            for line in result[0]:
                text_info = line[1]
                text = text_info[0]
                confidence = text_info[1]

                texts.append(text)
                confidences.append(confidence)

            # 合并文本
            captcha_text = ''.join(texts).replace(' ', '').replace('\n', '')

            # 应用正则表达式模式
            if pattern:
                match = re.search(pattern, captcha_text)
                if match:
                    captcha_text = match.group(0)
                else:
                    captcha_text = ''

            # 计算平均置信度
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            return {
                'success': True,
                'text': captcha_text,
                'confidence': avg_confidence,
                'raw_texts': texts,
                'raw_confidences': confidences
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'识别验证码失败: {str(e)}'
            }

    def recognize_with_retry(self, image_path: str,
                            max_retries: int = 3,
                            pattern: Optional[str] = None) -> Dict[str, Any]:
        """
        带重试的验证码识别

        尝试多种预处理参数组合，提高识别率

        Args:
            image_path: 验证码图像路径
            max_retries: 最大重试次数
            pattern: 正则表达式模式

        Returns:
            识别结果
        """
        best_result = None
        best_confidence = 0.0

        # 第一次尝试：标准预处理
        result = self.recognize(image_path, preprocess=True, pattern=pattern)
        if result['success'] and result['confidence'] > best_confidence:
            best_result = result
            best_confidence = result['confidence']

        # 如果置信度低，尝试不预处理
        if best_confidence < 0.7 and max_retries > 1:
            result = self.recognize(image_path, preprocess=False, pattern=pattern)
            if result['success'] and result['confidence'] > best_confidence:
                best_result = result
                best_confidence = result['confidence']

        # 如果还是没有高置信度，尝试不同的二值化阈值
        if best_confidence < 0.7 and max_retries > 2:
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # 尝试不同的阈值
            thresholds = [100, 127, 150, 180]
            for threshold in thresholds:
                _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
                temp_path = f"temp_captcha_thresh_{threshold}.png"
                cv2.imwrite(temp_path, binary)

                result = self.recognize(temp_path, preprocess=False, pattern=pattern)

                import os
                if os.path.exists(temp_path):
                    os.remove(temp_path)

                if result['success'] and result['confidence'] > best_confidence:
                    best_result = result
                    best_confidence = result['confidence']

        return best_result if best_result else {
            'success': False,
            'error': '识别失败，多次尝试后仍无法获得高置信度结果'
        }

    def batch_recognize(self, image_paths: List[str],
                       pattern: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        批量识别验证码

        Args:
            image_paths: 验证码图像路径列表
            pattern: 正则表达式模式

        Returns:
            识别结果列表
        """
        results = []
        for image_path in image_paths:
            result = self.recognize_with_retry(image_path, pattern=pattern)
            results.append({
                'image_path': image_path,
                **result
            })
        return results


def main():
    """命令行接口"""
    import argparse
    import json

    parser = argparse.ArgumentParser(description='PaddleOCR 3.x 验证码识别服务')
    parser.add_argument('image', help='验证码图像路径')
    parser.add_argument('--no-preprocess', action='store_true',
                       help='不进行预处理')
    parser.add_argument('--pattern', help='正则表达式模式（如 ^[A-Z0-9]{4}$）')
    parser.add_argument('--retry', type=int, default=3,
                       help='最大重试次数')
    parser.add_argument('--output', help='输出结果到文件')
    parser.add_argument('--gpu', action='store_true', help='使用 GPU 加速')

    args = parser.parse_args()

    # 初始化服务
    service = CaptchaRecognitionService(use_gpu=args.gpu)

    # 识别验证码
    if args.retry > 1:
        result = service.recognize_with_retry(
            args.image,
            max_retries=args.retry,
            pattern=args.pattern
        )
    else:
        result = service.recognize(
            args.image,
            preprocess=not args.no_preprocess,
            pattern=args.pattern
        )

    # 输出结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到: {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
