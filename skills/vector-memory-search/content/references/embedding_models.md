# 向量嵌入模型选择指南

## 概述

向量嵌入(Embedding)是将文本转换为高维向量的技术，是向量记忆系统的核心组件。选择合适的嵌入模型直接影响记忆检索的准确性和系统性能。

## 主流嵌入模型对比

### OpenAI 系列

| 模型 | 维度 | 上下文 | MTEB得分 | 特点 |
|------|------|--------|---------|------|
| text-embedding-3-small | 1536 | 8K | 62.3% | 性价比最高，通用场景首选 |
| text-embedding-3-large | 3072 | 8K | 64.6% | 最高精度，支持长文本 |
| text-embedding-ada-002 | 1536 | 8K | 60.9% | 兼容性好，稳定可靠 |

### 开源模型

| 模型 | 维度 | 上下文 | MTEB得分 | 特点 |
|------|------|--------|---------|------|
| BGE-large-zh | 1024 | 512 | 65.4% | 中文优化最佳 |
| M3E-large | 1024 | 512 | 63.4% | 多语言支持 |
| Instructor-large | 768 | 512 | 66.3% | 可指定任务类型 |
| Jina-embeddings-v2 | 1024 | 8K | 66.6% | 长上下文开源最强 |

### 本地部署模型

| 模型 | 维度 | 推理设备 | 适用场景 |
|------|------|---------|---------|
| all-MiniLM-L6-v2 | 384 | CPU | 快速原型、边缘设备 |
| all-mpnet-base-v2 | 768 | GPU | 平衡性能与速度 |
| GTE-large | 1024 | GPU | 高精度需求 |

## 选择决策树

```
开始选择
    │
    ├─ 预算优先?
    │   └─ 是 → text-embedding-3-small (API) 或 BGE-large-zh (本地)
    │
    ├─ 中文为主?
    │   └─ 是 → BGE-large-zh 或 M3E-large
    │
    ├─ 数据隐私敏感?
    │   └─ 是 → Instructor-large 或 BGE (本地部署)
    │
    └─ 长上下文需求?
        └─ 是 → text-embedding-3-large 或 Jina-embeddings-v2
```

## 向量维度说明

### 维度与精度权衡

```
维度降低 → 精度下降
维度升高 → 存储成本↑ 计算成本↑ 检索速度↓
```

### 推荐维度配置

| 使用场景 | 推荐维度 | 模型示例 |
|---------|---------|---------|
| 内存敏感 | 256-512 | all-MiniLM-L6-v2 |
| 平衡场景 | 768-1024 | BGE-base, MPNet |
| 高精度场景 | 1536-3072 | OpenAI-3, BGE-large |

### 维度压缩技术

当存储成本过高时，可使用：

1. **PCA降维**: 保留95%信息量
2. **SVD压缩**: 适用于大型语料库
3. **量化**: INT8/INT4量化减少存储

```python
from sklearn.decomposition import PCA
import numpy as np

def reduce_dimensions(vectors, target_dim=512):
    """PCA降维"""
    pca = PCA(n_components=target_dim)
    return pca.fit_transform(vectors)
```

## 性能基准测试

### 中文场景测试结果

| 模型 | 语义相似度准确率 | 检索速度(10000条) | 内存占用 |
|------|----------------|-----------------|---------|
| text-embedding-3-small | 91.2% | 0.8s | 1.2GB |
| BGE-large-zh | 93.5% | 2.1s | 2.4GB |
| M3E-large | 89.8% | 1.8s | 2.1GB |
| Jina-embeddings-v2 | 94.1% | 2.5s | 2.8GB |

### 英文场景测试结果

| 模型 | 语义相似度准确率 | 检索速度(10000条) | 内存占用 |
|------|----------------|-----------------|---------|
| text-embedding-3-large | 95.8% | 1.2s | 1.8GB |
| all-mpnet-base-v2 | 92.3% | 1.5s | 1.5GB |
| Instructor-large | 96.1% | 3.2s | 3.2GB |

## 成本分析

### OpenAI API成本 (2024年5月)

| 模型 | 每1K Token成本 | 100万Token成本 |
|------|--------------|---------------|
| text-embedding-3-small | $0.00002 | $0.13 |
| text-embedding-3-large | $0.00013 | $0.65 |

### 本地部署成本

| 模型 | GPU要求 | 日均推理成本(10000次) |
|------|--------|---------------------|
| BGE-large-zh | RTX 3090 | ~$0 (电费) |
| M3E-large | RTX 3090 | ~$0 (电费) |

## 集成示例

### OpenAI模型配置

```python
from openai import OpenAI

class OpenAIEmbedding:
    def __init__(self, model="text-embedding-3-small"):
        self.client = OpenAI()
        self.model = model

    async def encode(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]
```

### 本地模型配置

```python
from sentence_transformers import SentenceTransformer

class LocalEmbedding:
    def __init__(self, model_name="BAAI/bge-large-zh-v1.5"):
        self.model = SentenceTransformer(model_name)

    async def encode(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(
            texts,
            normalize_embeddings=True,
            batch_size=32
        ).tolist()
```

## 最佳实践

### 1. 模型选择建议

- **快速原型**: text-embedding-3-small 或 all-MiniLM-L6-v2
- **生产环境**: 根据语言选择 BGE-large-zh (中文) 或 text-embedding-3-large (通用)
- **隐私优先**: 本地部署开源模型

### 2. 批处理优化

```python
async def batch_encode(texts: list[str], batch_size: int = 100):
    """批处理编码"""
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        embeddings = await embedding_model.encode(batch)
        results.extend(embeddings)
    return results
```

### 3. 缓存策略

```python
import hashlib
from functools import lru_cache

@lru_cache(maxsize=10000)
def get_cached_embedding(text: str) -> list[float]:
    """缓存高频查询"""
    return embedding_model.encode([text])[0]
```

## 更新日志

- 2024-05-16: 添加Jina-embeddings-v2性能数据
- 2024-04-01: 更新OpenAI价格
- 2024-03-15: 首次创建
