# Ultralytics YOLOv8 API 参考

## 模型加载

```python
from ultralytics import YOLO

# 加载预训练模型
model = YOLO('yolov8n.pt')      # nano - 最快
model = YOLO('yolov8s.pt')      # small
model = YOLO('yolov8m.pt')      # medium
model = YOLO('yolov8l.pt')      # large
model = YOLO('yolov8x.pt')      # extra-large

# 加载自定义模型
model = YOLO('path/to/custom_model.pt')

# 从头训练
model = YOLO('yolov8n.yaml')    # 使用配置文件
```

## 模型训练 (train)

```python
results = model.train(
    data='coco128.yaml',        # 数据集配置路径
    epochs=100,                 # 训练轮数
    imgsz=640,                  # 输入图像尺寸
    batch=16,                   # 批量大小
    device=0,                   # 设备 (0, 1, 'cpu', '0,1,2,3')
    workers=8,                  # 数据加载线程数
    project='runs/detect',      # 项目保存路径
    name='exp',                 # 实验名称
    exist_ok=True,              # 允许覆盖已有实验
    pretrained=True,            # 使用预训练权重
    optimizer='SGD',            # 优化器
    lr0=0.01,                   # 初始学习率
    lrf=0.01,                   # 最终学习率 = lr0 * lrf
    momentum=0.937,             # SGD 动量
    weight_decay=0.0005,         # 权重衰减
    patience=50,                # 早停耐心值
    close_mosaic=10,            # 最后 N 轮关闭 mosaic 增强
    resume=False,               # 恢复训练
    amp=True,                   # 混合精度训练
    fraction=1.0,               # 使用数据比例
    profile=False,              # 性能分析
    freeze=None,                # 冻结层数
)
```

## 模型验证 (val)

```python
results = model.val(
    data='coco128.yaml',        # 数据集配置
    batch=16,                   # 批量大小
    imgsz=640,                  # 输入尺寸
    device=0,                   # 设备
    split='val',                # 数据集划分 (train/val/test)
    save_json=False,            # 保存 COCO JSON
    save_hybrid=False,          # 保存混合标签
    conf=None,                  # 置信度阈值
    iou=0.6,                    # NMS IoU 阈值
    max_det=300,                # 最大检测数
    half=True,                  # FP16 推理
    dnn=False,                  # 使用 OpenCV DNN
    plots=True,                 # 生成可视化图表
)
```

### 返回结果

```python
# results 对象的属性
results.box.map          # mAP50-95
results.box.map50        # mAP50
results.box.map75        # mAP75
results.box.maps         # 每个类别的 mAP50-95
results.box.ap_class_index  # AP 对应的类别索引
```

## 模型推理 (predict)

```python
results = model.predict(
    source='image.jpg',         # 图像源
    conf=0.25,                  # 置信度阈值
    iou=0.45,                   # NMS IoU 阈值
    imgsz=640,                  # 输入尺寸
    device=0,                   # 设备
    save=True,                  # 保存结果
    save_txt=True,              # 保存标签
    save_conf=True,             # 保存置信度
    save_crop=False,            # 保存裁剪图
    show=False,                 # 显示结果
    show_labels=True,          # 显示标签
    show_conf=True,            # 显示置信度
    show_boxes=True,           # 显示边框
    line_width=3,               # 边框线宽
    vid_stride=1,              # 视频帧间隔
    retina_masks=False,        # Retina 掩码
    augment=False,              # 测试时增强
    agnostic_nms=False,        # 类别无关 NMS
    classes=None,              # 筛选特定类别
    embed=None,                # 提取特征层
)

# 结果迭代
for r in results:
    boxes = r.boxes            # 检测框对象
    masks = r.masks            # 分割掩码 (分割模型)
    probs = r.probs            # 分类概率 (分类模型)
```

### 边界框对象 (Boxes)

```python
boxes = results[0].boxes

# 属性
boxes.xyxy       # xyxy 格式坐标 (N, 4)
boxes.xywh       # xywh 格式坐标 (N, 4)
boxes.xyxyn      # 归一化 xyxy (N, 4)
boxes.xywhn      # 归一化 xywh (N, 4)
boxes.conf       # 置信度 (N,)
boxes.cls        # 类别 ID (N,)
boxes.data       # 完整数据 (N, 6)

# 方法
boxes.cpu()      # 移到 CPU
boxes.numpy()    # 转为 numpy
boxes.cuda()     # 移到 CUDA
boxes.id         # 跟踪 ID (跟踪时)
boxes.is_track   # 是否跟踪模式
```

## 模型导出 (export)

```python
# 导出模型
model.export(
    format='onnx',             # 导出格式
    imgsz=640,                  # 输入尺寸
    keras=False,                # Keras 格式
    optimize=False,             # TorchScript 优化
    half=False,                # FP16 导出
    int8=False,                # INT8 量化
    dynamic=False,              # 动态输入尺寸
    simplify=False,            # 简化 ONNX 模型
    opset=12,                  # ONNX opset 版本
    workspace=4,                # TensorRT 工作空间
    nms=False,                 # 导出后 NMS
    batch=1,                   # 批量大小
    device=None,               # 设备
)
```

### 导出格式对比

| 格式 | 后缀 | 用途 | GPU | CPU | INT8 |
|------|------|------|-----|-----|------|
| PyTorch | .pt | 通用 | 是 | 是 | 否 |
| TorchScript | .torchscript | 部署 | 是 | 是 | 否 |
| ONNX | .onnx | 跨平台 | 是 | 是 | 是 |
| OpenVINO | _openvino_model/ | Intel CPU | 否 | 是 | 是 |
| TensorRT | .engine | NVIDIA GPU | 是 | 否 | 是 |
| CoreML | .mlmodel | Apple 设备 | 是 | 是 | 是 |
| TFLite | .tflite | 移动端 | 否 | 是 | 是 |
| Edge TPU | _edgetpu.tflite | Coral | 否 | 是 | 是 |

## 模型跟踪 (track)

```python
# 目标跟踪
results = model.track(
    source='video.mp4',
    persist=True,               # 帧间持续跟踪
    tracker='bytetrack.yaml',    # 跟踪器配置
    conf=0.25,
    iou=0.45,
    classes=None,               # 跟踪特定类别
    show=False,
)

# 跟踪结果包含 ID
for r in results:
    if r.boxes.id is not None:
        track_ids = r.boxes.id.int().tolist()
        print(f"Track IDs: {track_ids}")
```

## 高级用法

### 批量处理

```python
# 处理多个图像
images = ['img1.jpg', 'img2.jpg', 'img3.jpg']
results = model(images)

# 处理文件夹
results = model('path/to/images/')

# 异步处理 (适合视频流)
model = YOLO('yolov8n.pt')
stream = model('video.mp4', stream=True)
for frame in stream:
    # 处理每帧
    pass
```

### 自定义后处理

```python
# 获取原始预测
results = model.predict(source='image.jpg', verbose=False)

# 自定义 NMS
from ultralytics.utils.ops import non_max_suppression

boxes = results[0].boxes.xyxy.cpu().numpy()
confs = results[0].boxes.conf.cpu().numpy()

# 自定义阈值过滤
mask = confs > 0.5
filtered_boxes = boxes[mask]
filtered_confs = confs[mask]
```

### 特征提取

```python
# 提取特征向量
features = model('image.jpg', embed='layer20')
```

## 错误处理

```python
from ultralytics import YOLO

try:
    model = YOLO('invalid_path.pt')
    results = model.predict('image.jpg')
except FileNotFoundError:
    print("Model or image not found")
except Exception as e:
    print(f"Error: {e}")
```
