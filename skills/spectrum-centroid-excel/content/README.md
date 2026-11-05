# spectrum-centroid-excel

MS2质谱数据Centroid归中心化处理技能。

## 功能描述

将MS2质谱的profile模式（连续谱）数据转换为centroid模式（离散峰）数据，模拟msconvert的质谱处理算法。

## 数据结构

### 输入文件结构

Excel文件包含以下区域：

- **第1-6行**：元数据（metadata）
  - 第1行：SPECTRUM - MS
  - 第2行：原始文件名
  - 第3行：质谱参数（如"FTMS + p ESI Full ms2 282.1230@hcd20.00 [50.0000-305.0000]"）
  - 第4行：Scan编号
  - 第5行：保留时间RT
  - 第6行：数据点数（如"Data points: 470"）

- **第7行**：表头（Mass, Intensity）

- **第8行开始**：质谱数据（两列：m/z值和强度值）

### 输出文件结构

- **第1-6行**：元数据（与输入相同）
- **第7行**：表头（Mass, Intensity）
- **第8行开始**：处理后的数据
  - Mass列：保留原始m/z值
  - Intensity列：峰位置保留centroid值，非峰位置设为0

## 算法原理

### 1. 峰值检测

使用局部最大值检测算法，找出质谱图中的峰顶点。

### 2. 质心计算

使用强度加权平均方法计算每个峰的精确m/z位置：

```
质心m/z = Σ(Intensity_i × m/z_i) / Σ(Intensity_i)
```

## 使用方法

### 命令行方式

```bash
python spectrum_centroid.py <输入文件> [输出文件] [最小强度阈值]
```

**参数说明：**

- `输入文件`：必填，输入的Excel文件路径
- `输出文件`：可选，默认在原文件名后加_centroid
- `最小强度阈值`：可选，默认500

**示例：**

```bash
python spectrum_centroid.py input.xlsx output.xlsx 500
python spectrum_centroid.py input.xlsx
```

### Python导入方式

```python
from spectrum_centroid import process_ms2_file

# 基本用法
output_file = process_ms2_file("input.xlsx")

# 指定输出文件和参数
output_file = process_ms2_file("input.xlsx", "output.xlsx", min_intensity=300)
```

## 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| min_intensity | 500 | 最小强度阈值，用于过滤低信噪比峰 |
| window | 3 | 质心计算窗口大小 |

## 依赖

- Python 3.12+
- openpyxl
- numpy

## 注意事项

1. 输入文件必须是Excel格式（.xlsx或.xls）
2. 质谱数据从第8行开始读取
3. Mass列完全保留原始值，不进行修改
4. 输出文件行数与输入文件一致
5. 建议根据具体数据调整min_intensity参数