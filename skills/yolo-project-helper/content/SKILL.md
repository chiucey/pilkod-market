---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: f656ce0152b7fe3e506ad557bd1f5b4f
    PropagateID: f656ce0152b7fe3e506ad557bd1f5b4f
    ReservedCode1: 304402204e8fb2b49e395e5240294b2a5c5fecabda863f7a29509f777d097018dbf2106802200683d0363a99e2dc9e1680919e540a26cde678d3be69275cbe0f7632b1fa83d3
    ReservedCode2: 3045022100ec4d56265b041e82dec9ad394b8550171bd58ad2010c920d382ad92a524da3b00220142d2458b9da4fb35c4412d952d0c9a3032027a39f35332cee5b342a701e6315
description: YOLO 目标检测项目开发辅助工具。当用户要求创建 YOLO 项目、配置 YOLO 训练环境、准备数据集、训练 YOLO 模型、进行模型推理、使用 Ultralytics 库、转换 YOLO 模型格式，或分析 YOLO 项目结构时使用。
name: yolo-project-helper
---

# YOLO 项目助手

YOLO（You Only Look Once）是一种实时目标检测算法，本技能帮助用户完成 YOLO 项目的完整开发流程。

## 核心功能

### 1. 项目初始化

使用 Ultralytics 库创建标准 YOLO 项目结构：

```
yolo-project/
├── data/                  # 数据集目录
│   ├── images/           # 图片
│   └── labels/           # 标注文件
├── models/               # 模型配置
├── runs/                 # 训练输出
├── src/                  # 自定义代码
├── configs/              # 配置文件
├── requirements.txt
└── main.py
```

### 2. 数据集准备

#### 标注格式
YOLO 格式标注文件每行包含：
```
<class_id> <x_center> <y_center> <width> <height>
```
所有坐标值都是相对于图像尺寸的归一化值（0-1）。

#### 数据集配置 (data.yaml)
```yaml
path: ./data
train: images/train
val: images/val
test: images/test

nc: 80  # 类别数量
names: ['person', 'car', 'dog', ...]  # 类别名称
```

### 3. 模型训练

#### 基础训练命令
```bash
yolo detect train data=data.yaml model=yolov8n.pt epochs=100 imgsz=640
```

#### 常用训练参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `model` | 预训练模型或配置文件 | yolov8n.pt |
| `data` | 数据集配置文件路径 | - |
| `epochs` | 训练轮数 | 100 |
| `imgsz` | 输入图像尺寸 | 640 |
| `batch` | 批量大小 | 16 |
| `device` | 训练设备 (0, cpu, cuda:0) | auto |
| `project` | 项目保存目录 | runs/detect |
| `name` | 实验名称 | exp |
| `optimizer` | 优化器 (SGD, Adam, AdamW) | SGD |
| `lr0` | 初始学习率 | 0.01 |
| `patience` | 早停耐心值 | 50 |

#### 训练监控
训练过程中查看结果：
```bash
yolo detect train data=data.yaml model=yolov8n.pt epochs=100
# 训练完成后查看 results.png
```

### 4. 模型推理

#### 图像推理
```python
from ultralytics import YOLO

model = YOLO('yolov8n.pt')
results = model('image.jpg')
results[0].show()  # 显示结果
results[0].save('result.jpg')  # 保存结果
```

#### 批量推理
```python
# 推理整个文件夹
results = model('folder/*.jpg')
```

#### 返回结果解析
```python
for r in results:
    boxes = r.boxes  # 检测框
    for box in boxes:
        xyxy = box.xyxy[0]      # 边界框坐标
        conf = box.conf[0]      # 置信度
        cls = box.cls[0]        # 类别 ID
        print(f"Class: {int(cls)}, Conf: {conf:.2f}, Box: {xyxy}")
```

### 5. 模型导出

支持的导出格式：
- ONNX (`onnx`)
- TensorRT (`engine`)
- CoreML (`coreml`)
- TFLite (`tflite`)
- OpenVINO (`openvino`)
- PyTorch (`pt`)

```bash
yolo export model=yolov8n.pt format=onnx
```

### 6. 模型验证

```bash
yolo detect val model=runs/detect/train/weights/best.pt data=data.yaml
```

### 7. 常用 YOLO 模型对比

| 模型 | 参数量 | mAP@50 | 速度 (GPU) |
|------|--------|--------|------------|
| YOLOv8n | 3.2M | 37.4% | 0.99ms |
| YOLOv8s | 11.2M | 44.9% | 1.20ms |
| YOLOv8m | 25.9M | 50.2% | 1.83ms |
| YOLOv8l | 43.7M | 52.8% | 2.39ms |
| YOLOv8x | 68.2M | 53.9% | 3.53ms |

## 常见任务模板

### 任务：快速目标检测
```python
from ultralytics import YOLO

model = YOLO('yolov8n.pt')
results = model('image.jpg', conf=0.25, iou=0.45)
```

### 任务：自定义数据集训练
```python
from ultralytics import YOLO

model = YOLO('yolov8n.pt')
model.train(data='data.yaml', epochs=100, imgsz=640, patience=20)
```

### 任务：多模型对比
```python
models = ['yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt']
for m in models:
    model = YOLO(m)
    metrics = model.val(data='data.yaml')
    print(f"{m}: mAP50={metrics.box.map50:.3f}")
```

### 任务：目标跟踪
```python
from ultralytics import YOLO

model = YOLO('yolov8n.pt')
results = model.track('video.mp4', persist=True)
```

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 显存不足 | 减小 batch 或 imgsz |
| 训练不收敛 | 检查数据标注、学习率设置 |
| 推理速度慢 | 使用更小的模型或 FP16 量化 |
| 模型效果差 | 增加训练数据、增强数据、使用更大的模型 |

## 依赖安装

```bash
pip install ultralytics
```

或使用完整依赖：
```bash
pip install ultralytics[export]
```
