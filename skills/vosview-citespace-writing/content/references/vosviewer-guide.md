# VosViewer 操作与解读指南

## 软件基本设置

### 阈值设置
- **Minimum number of occurrences**: 关键词最小出现频次（建议5-10）
- **Links strength**: 连线强度计算方式
- **Maximum number of per field**: 每个字段最大对象数

### 聚类算法
| 算法 | 适用场景 | 特点 |
|-----|---------|------|
| NLW (Normalized Link Weight) | 关键词聚类 | 权重归一化 |
| LNI (Logarithmic Link Strength) | 合作网络 | 对数化处理 |
| Affinity Index | 关联强度分析 | 考虑共现概率 |

## 视图类型说明

### Network Visualization
- **Standard**: 标准聚类视图
- **Clustered Views**: 分簇聚类视图
- **All trails**: 展示所有路径

### Overlay Visualization
- **Time overlay**: 时间叠加图
- **Activity offset**: 活动偏移图

### Cluster Explorer
- 聚类详细数据导出
- 各聚类成员列表

## 数据解读标准

### 聚类质量判断
```
Q值（Modularity）:
- Q > 0.3 → 聚类结构显著
- Q > 0.5 → 聚类效果良好
- Q > 0.7 → 聚类非常显著

S值（Silhouette）:
- S > 0.5 → 聚类效果良好
- S > 0.7 → 聚类效果优秀
```

### 节点属性
- **大小**: 表示频次/权重
- **颜色**: 聚类归属或时间分期
- **标签**: 关键词/作者名

### 连线属性
- **粗细**: 合作关系强度
- **颜色**: 同聚类（绿色）/跨聚类（灰色）

## 常见输出格式

### 导出格式
- **Network file**: .net, .gml格式
- **Full data**: Excel格式
- **Visualization**: PNG/SVG图片

### 数据字段
| 字段 | 含义 |
|-----|------|
| ID | 节点编号 |
| Label | 标签名称 |
| Links | 连接数 |
| Total link strength | 总连线强度 |
| Documents | 文档数 |
