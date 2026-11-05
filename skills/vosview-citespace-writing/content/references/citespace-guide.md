# CiteSpace 操作与解读指南

## 软件基本设置

### 时间参数
- **Time Span**: 分析时间范围（如2010-2024）
- **Per Year**: 每段时间切片（建议1年或2年）

### 阈值设置
- **Top N per slice**: 每个时间切片选择前N个节点
- **g-index**: 引文量g指数修正

### 聚类参数
| 算法 | 适用场景 |
|-----|---------|
| LLR (Log-likelihood ratio) | 默认推荐 |
| MI (Mutual Information) | 互信息 |
| TF*IDF | 词频-逆文档频率 |

## 功能模块

### 1. 关键词共现分析
- 节点类型: Keyword
- 阈值设置: Top 50 per slice
- 聚类标签: LLR算法

### 2. 作者合作网络
- 节点类型: Author
- 阈值设置: Top 20 per slice
- 聚类: 按合作关系分组

### 3. 机构合作网络
- 节点类型: Institution
- 阈值设置: Top 30 per slice

### 4. 参考文献共被引
- 节点类型: Cited Reference
- 阈值设置: Top 50 per slice

### 5. 突现词检测
- 突现算法: K-means变点检测
- 最小持续时间: 2年

## 数据解读标准

### 中心性指标
- **Degree centrality**: 度中心性
- **Betweenness centrality**: 介数中心性 > 0.1 表示重要节点
- **Closeness centrality**: 接近中心性

### 聚类指标
| 指标 | 含义 | 阈值 |
|-----|------|------|
| Q值 | 模块度 | > 0.3 |
| S值 | 轮廓值 | > 0.5 |

### 突现词
- **Burst strength**: 突现强度 > 3.0 显著
- **Burst duration**: 突现持续时间
- **Beginning/End**: 突现起止时间

## 常见输出格式

### 可视化
- **Cluster Timeline**: 时间线视图
- **Timezone**: 时区视图
- **Cluster View**: 聚类视图

### 数据表
- **Node table**: 节点详细信息
- **Link table**: 连线详细信息
- **Cluster table**: 聚类统计信息
