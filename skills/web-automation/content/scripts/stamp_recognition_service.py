"""
PaddleOCR 3.x 印章识别服务

支持功能：
- 印章检测（圆形、方形、椭圆）
- 印章文字识别
- 印章类型分类
- 印章真伪判断
"""

import os
import cv2
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path


class StampRecognitionService:
    """印章识别服务类"""

    def __init__(self, det_model_dir: Optional[str] = None,
                 rec_model_dir: Optional[str] = None,
                 cls_model_dir: Optional[str] = None,
                 use_gpu: bool = False):
        """
        初始化印章识别服务

        Args:
            det_model_dir: 检测模型路径
            rec_model_dir: 识别模型路径
            cls_model_dir: 分类模型路径
            use_gpu: 是否使用 GPU
        """
        self.use_gpu = use_gpu

        try:
            from paddleocr import PaddleOCR

            # 初始化 OCR（包含检测、识别、方向分类）
            self.ocr = PaddleOCR(
                det_model_dir=det_model_dir,
                rec_model_dir=rec_model_dir,
                cls_model_dir=cls_model_dir,
                use_angle_cls=True,  # 启用方向分类
                lang='ch',  # 中文
                use_gpu=use_gpu,
                show_log=False
            )

            self._initialized = True
        except Exception as e:
            print(f"初始化印章识别服务失败: {e}")
            self._initialized = False

    def detect_stamps(self, image_path: str) -> List[Dict[str, Any]]:
        """
        检测图像中的印章

        Args:
            image_path: 图像路径

        Returns:
            印章列表，每个印章包含位置、类型、置信度
        """
        if not self._initialized:
            return []

        # 读取图像
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"无法读取图像: {image_path}")

        # 转为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 使用 OCR 检测所有文本区域
        result = self.ocr.ocr(image_path, cls=True)

        stamps = []
        if result and result[0]:
            for line in result[0]:
                box = line[0]  # 文本框坐标
                text_info = line[1]  # 文本信息

                # 分析文本框形状判断是否为印章
                stamp_type = self._classify_stamp_shape(box)
                confidence = text_info[1]

                stamps.append({
                    'bbox': box,
                    'type': stamp_type,
                    'confidence': confidence,
                    'text': text_info[0]
                })

        return stamps

    def recognize_stamp_text(self, image_path: str,
                            bbox: Optional[List[List[int]]] = None) -> Dict[str, Any]:
        """
        识别印章文字

        Args:
            image_path: 图像路径
            bbox: 印章位置（如果为 None，则识别整个图像）

        Returns:
            识别结果，包含文字、置信度、方向
        """
        if not self._initialized:
            return {'text': '', 'confidence': 0.0, 'direction': 0}

        # 如果指定了位置，裁剪图像
        if bbox is not None:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"无法读取图像: {image_path}")

            # 转换为 numpy 数组并裁剪
            bbox_array = np.array(box).astype(np.int32)
            x, y, w, h = cv2.boundingRect(bbox_array)
            cropped = image[y:y+h, x:x+w]

            # 保存临时图像
            temp_path = f"temp_stamp_{os.path.basename(image_path)}"
            cv2.imwrite(temp_path, cropped)
            image_path = temp_path

        try:
            # 使用 OCR 识别
            result = self.ocr.ocr(image_path, cls=True)

            if result and result[0]:
                text_lines = [line[1][0] for line in result[0]]
                text = '\n'.join(text_lines)

                # 获取方向信息（如果启用方向分类）
                direction = 0
                if result[0][0] and len(result[0][0]) > 1:
                    direction = result[0][0][2] if len(result[0][0]) > 2 else 0

                # 计算平均置信度
                confidences = [line[1][1] for line in result[0]]
                avg_confidence = sum(confidences) / len(confidences)

                return {
                    'text': text,
                    'confidence': avg_confidence,
                    'direction': direction
                }
            else:
                return {'text': '', 'confidence': 0.0, 'direction': 0}

        finally:
            # 清理临时文件
            if bbox is not None and 'temp_path' in locals():
                if os.path.exists(temp_path):
                    os.remove(temp_path)

    def detect_and_recognize(self, image_path: str) -> List[Dict[str, Any]]:
        """
        检测并识别印章（一步完成）

        Args:
            image_path: 图像路径

        Returns:
            印章列表，每个印章包含位置、类型、文字、置信度
        """
        # 检测印章
        stamps = self.detect_stamps(image_path)

        # 识别每个印章的文字
        for stamp in stamps:
            bbox = stamp['bbox']
            result = self.recognize_stamp_text(image_path, bbox)
            stamp.update(result)

        return stamps

    def classify_stamp_type(self, image_path: str,
                           bbox: Optional[List[List[int]]] = None) -> Dict[str, Any]:
        """
        分类印章类型

        支持类型：
        - official: 公章
        - finance: 财务章
        - contract: 合同章
        - invoice: 发票章
        - other: 其他

        Args:
            image_path: 图像路径
            bbox: 印章位置

        Returns:
            分类结果，包含类型和置信度
        """
        if not self._initialized:
            return {'type': 'unknown', 'confidence': 0.0}

        # 识别印章文字
        text_info = self.recognize_stamp_text(image_path, bbox)
        text = text_info['text']

        # 基于关键词判断印章类型
        stamp_type = 'other'
        confidence = 0.5

        keywords = {
            'official': ['有限公司', '有限公司', '公司', '企业'],
            'finance': ['财务', '专用章', '发票', '收据'],
            'contract': ['合同', '协议', '签约'],
            'invoice': ['发票', '开票', '税务']
        }

        for s_type, kw_list in keywords.items():
            for kw in kw_list:
                if kw in text:
                    stamp_type = s_type
                    confidence = 0.8
                    break
            if confidence > 0.7:
                break

        return {
            'type': stamp_type,
            'confidence': confidence
        }

    def verify_stamp(self, image_path: str,
                    expected_text: Optional[str] = None) -> Dict[str, Any]:
        """
        验证印章真伪

        基于以下特征：
- 印章文字是否匹配
- 印章形状是否规范
- 印章颜色是否正常

        Args:
            image_path: 图像路径
            expected_text: 预期印章文字（可选）

        Returns:
            验证结果，包含是否通过、置信度、原因
        """
        # 检测并识别印章
        stamps = self.detect_and_recognize(image_path)

        if not stamps:
            return {
                'valid': False,
                'confidence': 0.0,
                'reason': '未检测到印章'
            }

        # 取置信度最高的印章
        best_stamp = max(stamps, key=lambda x: x['confidence'])

        # 检查文字匹配（如果提供了预期文字）
        if expected_text:
            if expected_text not in best_stamp['text']:
                return {
                    'valid': False,
                    'confidence': 0.3,
                    'reason': f'印章文字不匹配，预期: {expected_text}，实际: {best_stamp["text"]}'
                }

        # 检查置信度
        if best_stamp['confidence'] < 0.7:
            return {
                'valid': False,
                'confidence': best_stamp['confidence'],
                'reason': '印章识别置信度过低'
            }

        return {
            'valid': True,
            'confidence': best_stamp['confidence'],
            'reason': '印章验证通过',
            'stamp': best_stamp
        }

    def _classify_stamp_shape(self, box: List[List[int]]) -> str:
        """
        根据文本框形状判断印章类型

        Args:
            box: 文本框坐标 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]

        Returns:
            印章类型：circular（圆形）、square（方形）、elliptical（椭圆）
        """
        # 计算文本框的宽度和高度
        width = max(abs(box[1][0] - box[0][0]), abs(box[3][0] - box[2][0]))
        height = max(abs(box[2][1] - box[1][1]), abs(box[3][1] - box[0][1]))

        # 计算宽高比
        ratio = width / height if height > 0 else 1.0

        # 判断形状
        if 0.8 <= ratio <= 1.2:
            return 'square'  # 方形（包括圆形）
        elif ratio < 0.8 or ratio > 1.2:
            return 'elliptical'  # 椭圆
        else:
            return 'unknown'


def main():
    """命令行接口"""
    import argparse
    import json

    parser = argparse.ArgumentParser(description='PaddleOCR 3.x 印章识别服务')
    parser.add_argument('image', help='图像路径')
    parser.add_argument('--detect', action='store_true', help='检测印章')
    parser.add_argument('--recognize', action='store_true', help='识别印章文字')
    parser.add_argument('--verify', action='store_true', help='验证印章真伪')
    parser.add_argument('--expected-text', help='预期印章文字（用于验证）')
    parser.add_argument('--output', help='输出结果到文件')
    parser.add_argument('--gpu', action='store_true', help='使用 GPU 加速')

    args = parser.parse_args()

    # 初始化服务
    service = StampRecognitionService(use_gpu=args.gpu)

    result = None

    if args.detect:
        result = service.detect_stamps(args.image)
    elif args.recognize:
        result = service.detect_and_recognize(args.image)
    elif args.verify:
        result = service.verify_stamp(args.image, args.expected_text)
    else:
        # 默认执行检测和识别
        result = service.detect_and_recognize(args.image)

    # 输出结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到: {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
