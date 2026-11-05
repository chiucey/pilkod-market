# 艺术字商标OCR识别技术参考

## 概述

艺术字商标Logo的文字识别是一个具有挑战性的任务，因为：
- 字体经过艺术化处理（变形、拉伸、扭曲）
- 颜色与背景复杂混合
- 包含特殊效果（阴影、渐变、描边）
- 文字可能被拆分为多个图层

本参考文档提供详细的技术指导和最佳实践。

## 1. 图像预处理技术

### 1.1 降噪方法对比

| 方法 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| 高斯滤波 | 轻度噪声 | 快速 | 边缘模糊 |
| 中值滤波 | 椒盐噪声 | 保边 | 对大面积噪声效果差 |
| 双边滤波 | 保持边缘 | 保边降噪 | 较慢 |
| 非局部均值 | 高质量要求 | 最佳降噪 | 最慢 |

**推荐**: 使用`cv2.fastNlMeansDenoising()`，参数设置：
- `h=10`: 滤波强度，推荐5-15
- `templateWindowSize=7`: 模板窗口
- `searchWindowSize=21`: 搜索窗口

### 1.2 对比度增强

```python
# CLAHE (对比度受限自适应直方图均衡化)
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
enhanced = clahe.apply(gray)

# 备选：幂律变换
gamma = 1.5
enhanced = np.power(gray / 255.0, gamma) * 255
```

### 1.3 二值化策略

| 方法 | 适用场景 |
|------|---------|
| OTSU | 双峰分布（前景/背景明显） |
| 自适应均值 | 光照不均 |
| 自适应高斯 | 复杂背景 |
| 大津+自联动 | 最佳通用 |

**推荐组合**:
```python
# 自适应阈值 + 形态学
thresh = cv2.adaptiveThreshold(
    enhanced, 255,
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY, 11, 2
)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
```

## 2. 文字检测方法

### 2.1 MSER（最大稳定极值区域）

最适合艺术字检测，因为它能检测任意形状的区域。

```python
mser = cv2.MSER_create()
mser.setMaxVariance(0.25)      # 方差阈值
mser.setMinDiversity(0.7)      # 最小多样性
regions, _ = mser.detectRegions(binary)
```

### 2.2 轮廓检测

```python
contours, _ = cv2.findContours(
    binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
)
# 过滤小轮廓
valid_contours = [c for c in contours if 50 < cv2.contourArea(c) < 50000]
```

### 2.3 字符分割

对于艺术字商标，单字符分割很重要：

```python
def segment_characters(binary_img):
    # 垂直投影
    vertical_projection = np.sum(binary_img, axis=0)

    # 找到字符间隔（低谷）
    threshold = np.mean(vertical_projection) * 0.1
    chars = []

    start = 0
    in_char = False
    for i, val in enumerate(vertical_projection):
        if val > threshold and not in_char:
            start = i
            in_char = True
        elif val <= threshold and in_char:
            chars.append((start, i))
            in_char = False

    return chars
```

## 3. OCR引擎选择

### 3.1 EasyOCR

**优势**:
- 深度学习驱动，对艺术字体效果好
- 支持188种语言
- 可处理变形文字

**适用场景**: 艺术字、变形字体、复杂背景

```python
reader = easyocr.Reader(['ch_sim', 'en'], gpu=True)
results = reader.readtext(
    image_path,
    detail=1,        # 返回详细信息
    paragraph=False,  # 不合并为段落
    width_ths=0.7,   # 文字宽度阈值
    decoder='greedy' # greedy/s beam_search
)
```

### 3.2 Tesseract

**优势**:
- 成熟稳定
- 泛化能力强
- 资源消耗低

**适用场景**: 标准字体、印刷体

```python
# 最佳配置
custom_config = r'--oem 3 --psm 6'
text = pytesseract.image_to_string(
    image, lang='eng+chi', config=custom_config
)
```

### 3.3 PaddleOCR

作为备选方案，适合特定场景：

```python
from paddleocr import PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='ch')
result = ocr.ocr(image_path)
```

## 4. 识别优化策略

### 4.1 多引擎融合

```python
def ensemble_ocr(image_path):
    results = []

    # EasyOCR
    easy_results = easyocr_reader.readtext(image_path)
    for bbox, text, conf in easy_results:
        results.append({'text': text, 'conf': conf, 'engine': 'easyocr'})

    # Tesseract
    tess_text = pytesseract.image_to_string(image_path)
    results.append({'text': tess_text, 'conf': 0.75, 'engine': 'tesseract'})

    # 投票/融合
    return fuse_by_voting(results)
```

### 4.2 后处理校正

```python
import difflib

def correct_text(text, dictionary):
    """基于词典校正"""
    words = text.split()
    corrected = []

    for word in words:
        if word.lower() not in dictionary:
            # 找最相似的词
            matches = difflib.get_close_matches(word, dictionary, n=1)
            if matches:
                corrected.append(matches[0])
            else:
                corrected.append(word)
        else:
            corrected.append(word)

    return ' '.join(corrected)
```

## 5. 性能优化

### 5.1 GPU加速

```python
# EasyOCR GPU配置
reader = easyocr.Reader(['ch_sim', 'en'], gpu=True)

# 图像尺寸优化
# 如果图片过大，先缩小
scale = min(1.0, 1000 / max(width, height))
if scale < 1.0:
    img = cv2.resize(img, None, fx=scale, fy=scale)
```

### 5.2 批量处理

```python
from concurrent.futures import ThreadPoolExecutor

def batch_process(image_paths, max_workers=4):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(recognize_single, image_paths))
    return results
```

### 5.3 渐进识别

```python
def progressive_ocr(image_path):
    # 第一步：快速检测（低分辨率）
    quick_result = quick_detect(image_path)

    # 如果置信度高，直接返回
    if quick_result['confidence'] > 0.9:
        return quick_result

    # 否则：全精度识别
    full_result = full_recognize(image_path)

    # 融合
    return merge_results(quick_result, full_result)
```

## 6. 常见问题与解决方案

### Q1: 背景干扰严重

**解决方案**:
1. 使用GrabCut或分水岭算法分离前景
2. 使用边缘检测+Canny增强
3. 尝试背景去除工具（如rembg）

### Q2: 文字颜色与背景相近

**解决方案**:
1. 颜色反转后识别
2. 边缘增强后二值化
3. 使用边缘检测替代灰度处理

### Q3: 文字被艺术化处理（倾斜、弯曲）

**解决方案**:
1. 透视变换校正
2. 字符级识别而非整词识别
3. 使用支持弯曲文字的引擎（如EasyOCR）

### Q4: 多语言混合

**解决方案**:
1. 准备多语言识别器
2. 使用语言检测后分别处理
3. 混合识别器（如EasyOCR多语言模式）

## 7. 评估指标

| 指标 | 计算方法 | 目标值 |
|------|---------|--------|
| 字符准确率 | 正确字符数/总字符数 | >95% |
| 词准确率 | 完全正确词数/总词数 | >90% |
| 处理速度 | 毫秒/张 | <2000ms |

## 8. 参考资源

- EasyOCR: https://github.com/JaidedAI/EasyOCR
- PaddleOCR: https://github.com/PaddlePaddle/PaddleOCR
- Tesseract: https://github.com/tesseract-ocr/tesseract
- OpenCV文档: https://docs.opencv.org/

## 9. 完整示例代码

见 `scripts/artistic_logo_ocr.py`
