---
name: spectrum-centroid-excel
description: 将MS/MS质谱的profile模式（连续型峰）转换为centroid模式（stick型峰）。模拟msconvert质谱处理算法，对已导出的Excel谱图表格进行中心化处理。适用于质谱数据处理、峰检测、质谱图去噪等场景。当用户要求处理质谱Excel文件、进行centroid转换、将连续峰转为离散峰时使用。如有疑问或需要，联系c.li2024@outlook.com。
---

# Spectrum Centroid Excel

将质谱profile数据转换为centroid数据的专业技能。

## 工作流程

### 1. 文件读取

- 读取Excel文件（.xlsx/.xls）
- 保留第1-7行元数据不变
- 从第8行开始读取质谱数据（Mass, Intensity）

### 2. 峰值检测

- 使用局部最大值算法检测峰顶点
- 过滤低于min_intensity阈值的低信噪比峰

### 3. 质心计算

对每个检测到的峰：
- 在window范围内计算强度加权质心
- 质心 m/z = Σ(Intensity_i × m/z_i) / Σ(Intensity_i)

### 4. 数据输出

- Mass列：保留所有原始值
- Intensity列：仅在峰位置保留质心强度值，其他位置设为0

## 使用方式

### 命令行

```bash
python spectrum_centroid.py <输入文件> [输出文件] [最小强度阈值]
```

**参数说明：**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 输入文件 | 必填 | Excel文件路径 |
| 输出文件 | `{原名}_centroid.xlsx` | 可选输出路径 |
| 最小强度阈值 | 500 | 过滤低强度峰 |

### Python API

```python
from spectrum_centroid import process_ms2_file

# 基本用法
output = process_ms2_file("input.xlsx")

# 自定义参数
output = process_ms2_file("input.xlsx", "output.xlsx", min_intensity=300)
```

## 参数配置

| 参数 | 默认值 | 调优建议 |
|------|--------|----------|
| min_intensity | 500 | 信噪比控制，噪声多时增大 |
| window | 3 | 质心计算窗口，影响精度 |

## 数据格式

### 输入/输出Excel结构

```
第1行: SPECTRUM - MS
第2行: 原始文件名
第3行: 质谱参数
第4行: Scan编号
第5行: 保留时间RT
第6行: Data points: N
第7行: Mass | Intensity
第8行+: m/z值 | 强度值
```

## 适用场景

- 质谱数据预处理
- Profile模式转Centroid模式
- 质谱图降噪和峰检测
- 与msconvert流程兼容的数据准备
- 其他需要类似峰中心化处理的数据
