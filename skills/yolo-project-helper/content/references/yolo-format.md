# YOLO 标注格式详解

## 基础格式

YOLO 格式的标注文件是纯文本文件，每行代表一个目标检测框：

```
<class_id> <x_center> <y_center> <width> <height>
```

## 坐标系统

### 归一化坐标
- 所有坐标值都是相对于图像尺寸的归一化值
- 取值范围：0.0 到 1.0
- 原点 (0, 0) 在图像左上角

### 坐标计算公式
```
x_center_norm = x_center_pixel / image_width
y_center_norm = y_center_pixel / image_height
width_norm = box_width_pixel / image_width
height_norm = box_height_pixel / image_height
```

## 示例

假设有一张 640x480 的图像，一个检测框的像素坐标为：
- 左上角: (100, 50)
- 右下角: (300, 200)

计算 YOLO 格式：
```
width = 300 - 100 = 200
height = 200 - 50 = 150
x_center = 100 + 100 = 200
y_center = 50 + 75 = 125

归一化:
x_center = 200 / 640 = 0.3125
y_center = 125 / 480 = 0.2604
width = 200 / 640 = 0.3125
height = 150 / 480 = 0.3125
```

对应的标注行：
```
0 0.3125 0.2604 0.3125 0.3125
```

## 多目标标注

每个检测对象一行，按顺序编号：
```
0 0.3125 0.2604 0.3125 0.3125
1 0.5000 0.4500 0.1500 0.2000
2 0.7500 0.3000 0.1000 0.1500
```

## 目录结构规范

### 标准数据集结构
```
dataset/
├── images/
│   ├── train/        # 训练集图片
│   │   ├── img001.jpg
│   │   ├── img002.jpg
│   │   └── ...
│   ├── val/          # 验证集图片
│   └── test/         # 测试集图片
├── labels/
│   ├── train/        # 训练集标注 (与 images/train 对应)
│   │   ├── img001.txt
│   │   ├── img002.txt
│   │   └── ...
│   ├── val/
│   └── test/
```

### 命名对应规则
- 图片和标注文件必须同名
- `images/train/img001.jpg` 对应 `labels/train/img001.txt`
- 支持的图片格式：`.jpg`, `.jpeg`, `.png`, `.bmp`

## 常见问题

### 1. 坐标超出范围
检查归一化是否正确，确保所有值在 [0, 1] 范围内。

### 2. 宽高为 0
检查标注框是否有效，避免创建宽高为 0 的框。

### 3. 中心点计算错误
中心点 = 左上角 + 宽/高的一半，不是简单的宽高。
