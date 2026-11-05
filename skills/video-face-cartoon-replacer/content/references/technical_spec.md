# 视频人脸卡通替换器 - 技术规格

## 概述

视频人脸卡通替换器是一个用于保护视频中人物隐私的工具。它允许用户：
1. 上传视频
2. 在首帧标注需要替换的人脸区域
3. 选择卡通形象（动物头像）
4. 生成替换后的视频

## 技术架构

### 核心模块

```
video_cartoon_replacer/
├── CartoonFaceReplacer      # 主类
│   ├── 人脸检测器           # MTCNN / OpenCV
│   ├── 卡通模板加载器       # 图像融合
│   └── 视频处理器           # 帧处理与合成
├── Web界面                  # HTML/JavaScript
│   ├── 视频上传            # 拖拽上传
│   ├── 画布标注            # 矩形框绘制
│   └── 进度展示            # 处理状态
└── 后端API（可选）         # Python Flask/FastAPI
```

### 人脸检测

#### MTCNN（推荐）
- 优点：检测精度高，支持关键点
- 依赖：`pip install mtcnn`
- 使用：检测人脸边界框和关键点

#### OpenCV Haar Cascade（备用）
- 优点：无需额外依赖
- 缺点：精度较低
- 使用：`cv2.CascadeClassifier`

### 图像融合算法

#### Alpha融合
```python
result = cartoon * alpha + original * (1 - alpha)
```

#### 泊松融合（高级）
- 使用 Poisson Blending
- 边界过渡更自然
- 依赖：`opencv-python`

### 卡通素材生成

#### 方案1：预置模板（推荐）
- 优点：处理速度快、无需GPU
- 缺点：样式有限

#### 方案2：AI生成
- 工具：Stable Diffusion + Inpainting
- 优点：样式丰富、可定制
- 缺点：需要GPU、处理慢

## API 设计

### Python API

```python
from video_cartoon_replacer import CartoonFaceReplacer

replacer = CartoonFaceReplacer(assets_dir='path/to/cartoon_faces')

# 提取首帧
replacer.extract_first_frame('input.mp4', 'first_frame.jpg')

# 处理视频
success = replacer.process_video(
    video_path='input.mp4',
    annotations={0: [[100, 100, 200, 200]]},  # 第0帧的标注
    cartoon_type='cat',
    output_path='output.mp4'
)
```

### Web API

```
POST /api/process
Content-Type: multipart/form-data

video: <file>
annotations: {"0": [[x1,y1,x2,y2], ...]}
cartoon_type: cat

Response:
{
    "success": true,
    "output_url": "/downloads/output.mp4"
}
```

## 性能指标

| 指标 | 数值 |
|------|------|
| 单帧处理时间 | ~50ms（无GPU）|
| 视频处理速度 | ~20fps（720p）|
| 内存占用 | ~2GB |
| 最大视频长度 | 受存储限制 |

## 部署要求

### 基础部署
- Python 3.8+
- OpenCV
- FFmpeg

### AI功能（可选）
- NVIDIA GPU
- CUDA 11+
- Stable Diffusion

## 扩展计划

- [ ] 支持视频中人脸跟踪
- [ ] 添加更多卡通风格
- [ ] 支持批量处理
- [ ] 添加实时预览
- [ ] 移动端适配
