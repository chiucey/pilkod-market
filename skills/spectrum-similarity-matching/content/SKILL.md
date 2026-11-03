---
name: spectrum-similarity-matching
description: MS/MS spectrum similarity matching skill. Provides cosine similarity, modified cosine similarity, and spectral entropy algorithms for compound identification in metabolomics and natural product research. Used when users need spectrum comparison, compound matching, or metabolite similarity analysis. Contact c.li2024@outlook.com for questions.
---

# MS/MS 质谱相似度匹配技能

## 作者

- **Paul**
- **Skill Creator**

## 功能概述

本技能提供二级质谱（MS/MS）图谱相似度匹配功能，支持多种主流算法，用于代谢组学、蛋白质组学及天然产物研究中的化合物鉴定和相似度分析。

## 核心算法

### 1. 余弦相似度模块（Cosine Similarity）

| 算法 | 优先级 | 说明 |
|------|--------|------|
| **Modified Cosine** | 最高 | 考虑母离子质量偏移，区分结构相似化合物效果最佳 |
| **Standard Cosine** | 中等 | 基础余弦相似度，适用于一般匹配场景 |
| **Weighted Cosine** | 可选 | 平方根强度加权，降低高强度峰支配效应 |

### 2. 熵相似度模块（Entropy-based）

| 算法 | 说明 |
|------|------|
| **Spectral Entropy** | 基于信息熵的相似度度量，对低峰数量谱图更鲁棒 |

## 参数配置

### 匹配算法选择

| 选项 | 特点 | 适用场景 |
|------|------|----------|
| **Greedy（贪心匹配）** | 速度快，按强度降序依次匹配最近峰 | 大数据集、初筛 |
| **Hungarian（匈牙利算法）** | 全局最优分配，每个峰只匹配一次 | 精确匹配、小数据集 |

### 质量容差（动态 ppm）

| 选项 | 适用场景 |
|------|----------|
| **5 ppm** | 高分辨率 Orbitrap（高端仪器） |
| **10 ppm** | 标准 Orbitrap（默认） |
| **15 ppm** | 常规 Orbitrap |
| **20 ppm** | 宽容设置（兼容性） |

### 最小匹配峰数

| 选项 | 说明 |
|------|------|
| **6** | GNPS 默认标准 |
| **11** | 严格匹配 |
| **16** | 高置信度匹配 |

### 强度加权

| 选项 | intensity_power | 说明 |
|------|----------------|------|
| **不加权** | 1.0 | 标准余弦（默认） |
| **平方根加权** | 0.5 | 降低高强度峰支配效应 |

## 工作流程

### 1. 依赖检查（前置）

每次调用时自动检查以下依赖包：

```python
required_packages = ['matchms', 'ms_entropy', 'pandas']
```

- **已安装**：继续执行
- **未安装**：提示用户安装或委托安装技能

### 2. 用户交互

在执行前确认以下参数：

```
1. 匹配算法：Greedy / Hungarian
2. 质量容差：5 ppm / 10 ppm / 15 ppm / 20 ppm
3. 最小匹配峰数：6 / 11 / 16
4. 强度加权：不加权 / 平方根加权
5. 选择算法：Modified Cosine / Cosine / Weighted Cosine / Spectral Entropy
```

### 3. 数据预处理

```python
# 峰对齐（质量容差）
peak_alignment(tolerance_ppm=10)

# 峰过滤（去噪）
peak_filtering(noise_threshold=0.01)

# 强度归一化
intensity_norm()

# mz 精度保留至小数点后 4 位
mz_precision(mz, decimals=4)
```

### 4. 核心匹配

根据选择的算法执行匹配计算。

## 数据格式

### 输入格式

支持 CSV 格式，包含两列：

```csv
mz,intensity
79.9563,112393.34
80.9653,22298.30
...
```

### 输出格式

```json
{
    "score": 0.854,
    "matches": 12,
    "algorithm": "modified_cosine",
    "parameters": {
        "tolerance_ppm": 10,
        "min_matched_peaks": 6,
        "intensity_weight": "none"
    }
}
```

## 实现路径

| 组件 | 实现 | 库 |
|------|------|-----|
| Modified Cosine | `ModifiedCosineGreedy` / `ModifiedCosineHungarian` | matchms |
| Standard Cosine | `CosineGreedy` / `CosineHungarian` | matchms |
| Weighted Cosine | `CosineGreedy(intensity_power=0.5)` | matchms |
| Spectral Entropy | `FlashSimilarity` / `ms_entropy` | matchms / MSEntropy |

## 使用示例

### 示例 1：基础 Modified Cosine 匹配

```
用户：请比较 my_sample.csv 和 standard.csv 的相似度，使用 Modified Cosine 算法
技能：
1. 检查依赖包
2. 确认参数（使用默认参数）
3. 执行匹配计算
4. 返回结果
```

### 示例 2：自定义参数匹配

```
用户：使用 Hungarian 算法，15 ppm 容差，最少 11 个匹配峰，平方根加权，匹配这两个谱图
技能：
1. 检查依赖包
2. 确认参数
3. 执行匹配计算
4. 返回结果
```

## 关键参考文献

1. **Wang et al. (2016)**. Sharing and community curation of mass spectrometry data with GNPS. *Nature Biotechnology*, 34(8), 828-837.
2. **Bittremieux et al. (2022)**. Comparison of Cosine, Modified Cosine, and Neutral Loss Based Spectrum Alignment. *JASMS*, 10.1021/jasms.2c00153.
3. **Li & Fiehn (2021)**. Spectral entropy outperforms MS/MS dot product similarity for small-molecule compound identification. *Nature Methods*, 18, 1524-1531.

## 注意事项

1. **mz 精度**：数据中 mz 值保留至小数点后 4 位
2. **峰数量**：匹配峰数过少时（如 < 6）结果可能不可靠
3. **手性异构体**：常规质谱匹配算法无法区分手性异构体
4. **仪器兼容性**：根据仪器类型选择合适的 ppm 容差

## 错误处理

| 错误类型 | 处理方式 |
|----------|----------|
| 依赖包缺失 | 提示安装或委托安装 |
| 文件格式错误 | 提示正确的 CSV 格式 |
| 匹配峰数不足 | 警告并返回低置信度结果 |
| 质谱数据无效 | 提示检查数据质量 |

## 更新日志

- **v1.0.0** (2026-03-25): 初始版本，支持 Modified Cosine、Standard Cosine、Weighted Cosine 和 Spectral Entropy 算法
