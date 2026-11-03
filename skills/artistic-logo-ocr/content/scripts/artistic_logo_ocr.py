#!/usr/bin/env python3
"""
艺术字商标Logo OCR识别脚本
Artistic Logo OCR Recognition Script

此脚本提供完整的多引擎OCR识别流程，专门针对艺术字体商标Logo优化。
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import json
import time
from typing import Dict, List, Tuple, Optional

# 全局变量用于缓存模型
_easyocr_reader = None
_tesseract_available = False

def init_engines():
    """初始化OCR引擎（可选）"""
    global _easyocr_reader, _tesseract_available

    try:
        import easyocr
        _easyocr_reader = easyocr.Reader(['ch_sim', 'en'], gpu=True)
        print("[OK] EasyOCR initialized")
    except Exception as e:
        print(f"[WARN] EasyOCR init failed: {e}")

    try:
        import pytesseract
        _tesseract_available = True
        print("[OK] Tesseract available")
    except Exception as e:
        print(f"[WARN] Tesseract not available: {e}")


def preprocess_image(image_path: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    预处理艺术字Logo图片

    Args:
        image_path: 图片路径

    Returns:
        Tuple[原始灰度图, 预处理后图像]
    """
    # 读取图像
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 1. 去噪 - 非局部均值降噪
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

    # 2. 对比度增强 - CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)

    # 3. 自适应二值化
    binary = cv2.adaptiveThreshold(
        enhanced, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )

    # 4. 形态学操作
    kernel = np.ones((2, 2), np.uint8)
    processed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    return gray, processed


def detect_text_regions(processed_img: np.ndarray) -> List[Dict]:
    """
    检测文字区域

    Args:
        processed_img: 预处理后的图像

    Returns:
        文字区域列表
    """
    regions = []

    # MSER检测
    mser = cv2.MSER_create()
    mser_regions, _ = mser.detectRegions(processed_img)

    for region in mser_regions:
        x, y, w, h = cv2.boundingRect(region)
        area = w * h

        # 过滤太小或太大的区域
        if 50 < area < 50000 and w > 5 and h > 5:
            regions.append({
                'x': int(x),
                'y': int(y),
                'width': int(w),
                'height': int(h),
                'area': int(area)
            })

    # 按位置排序
    regions.sort(key=lambda r: (r['y'], r['x']))

    return regions


def ocr_with_easyocr(image_path: str) -> List[Tuple]:
    """
    使用EasyOCR识别

    Args:
        image_path: 图片路径

    Returns:
        识别结果列表 [(边界框, 文字, 置信度), ...]
    """
    global _easyocr_reader

    if _easyocr_reader is None:
        init_engines()

    if _easyocr_reader is None:
        return []

    try:
        results = _easyocr_reader.readtext(image_path)
        return results
    except Exception as e:
        print(f"EasyOCR error: {e}")
        return []


def ocr_with_tesseract(image_path: str) -> str:
    """
    使用Tesseract识别

    Args:
        image_path: 图片路径

    Returns:
        识别文本
    """
    global _tesseract_available

    if not _tesseract_available:
        try:
            import pytesseract
            _tesseract_available = True
        except ImportError:
            return ""

    if not _tesseract_available:
        return ""

    try:
        result = pytesseract.image_to_string(image_path, lang='eng+chi')
        return result.strip()
    except Exception as e:
        print(f"Tesseract error: {e}")
        return ""


def fuse_results(easyocr_results: List[Tuple], tesseract_result: str) -> Dict:
    """
    融合多引擎识别结果

    Args:
        easyocr_results: EasyOCR结果
        tesseract_result: Tesseract结果

    Returns:
        融合后的结果
    """
    all_texts = []

    # 从EasyOCR提取结果
    if easyocr_results:
        for (bbox, text, conf) in easyocr_results:
            if text.strip():
                all_texts.append({
                    'text': text.strip(),
                    'confidence': conf,
                    'source': 'easyocr'
                })

    # 添加Tesseract结果
    if tesseract_result:
        all_texts.append({
            'text': tesseract_result,
            'confidence': 0.75,
            'source': 'tesseract'
        })

    # 按置信度排序
    all_texts.sort(key=lambda x: x['confidence'], reverse=True)

    # 构建最终结果
    if not all_texts:
        return {
            'success': False,
            'text': '',
            'confidence': 0,
            'alternatives': []
        }

    best = all_texts[0]
    alternatives = [
        {'text': t['text'], 'confidence': t['confidence']}
        for t in all_texts[1:5]
    ]

    return {
        'success': True,
        'text': best['text'],
        'confidence': best['confidence'],
        'source': best['source'],
        'alternatives': alternatives
    }


def recognize_artistic_logo(
    image_path: str,
    use_preprocessing: bool = True,
    use_all_engines: bool = True
) -> Dict:
    """
    主识别函数

    Args:
        image_path: 图片路径
        use_preprocessing: 是否使用预处理
        use_all_engines: 是否使用所有引擎

    Returns:
        识别结果字典
    """
    start_time = time.time()

    # 预处理
    processed_img = None
    if use_preprocessing:
        try:
            _, processed_img = preprocess_image(image_path)
        except Exception as e:
            print(f"Preprocessing failed: {e}")

    # OCR识别
    easyocr_results = ocr_with_easyocr(image_path) if use_all_engines else []
    tesseract_result = ocr_with_tesseract(image_path) if use_all_engines else ""

    # 检测文字区域
    regions = []
    if processed_img is not None:
        regions = detect_text_regions(processed_img)

    # 融合结果
    result = fuse_results(easyocr_results, tesseract_result)

    # 完善返回结果
    result['regions'] = regions
    result['processing_time_ms'] = int((time.time() - start_time) * 1000)

    return result


def batch_recognize(image_paths: List[str]) -> List[Dict]:
    """
    批量识别

    Args:
        image_paths: 图片路径列表

    Returns:
        识别结果列表
    """
    # 初始化引擎一次
    init_engines()

    results = []
    for path in image_paths:
        try:
            result = recognize_artistic_logo(path)
            result['image_path'] = path
            results.append(result)
        except Exception as e:
            results.append({
                'success': False,
                'image_path': path,
                'error': str(e)
            })

    return results


# 命令行接口
if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description='艺术字商标Logo OCR识别工具'
    )
    parser.add_argument('image', help='图片路径')
    parser.add_argument('--no-preprocess', action='store_true',
                        help='跳过预处理')
    parser.add_argument('--single-engine', action='store_true',
                        help='仅使用EasyOCR')
    parser.add_argument('--output', '-o', help='输出JSON文件路径')

    args = parser.parse_args()

    # 执行识别
    result = recognize_artistic_logo(
        args.image,
        use_preprocessing=not args.no_preprocess,
        use_all_engines=not args.single_engine
    )

    # 输出结果
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\nResult saved to: {args.output}")
