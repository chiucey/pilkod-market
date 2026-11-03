# OpenScholar Models Reference

## Available Models

### Generator Models

| Model | Description | Size | Use Case |
|-------|-------------|------|----------|
| `OpenScholar/Llama-3.1_OpenScholar-8B` | Main OpenScholar generator | 8B | Standard research synthesis |
| `gpt-4o` | OpenAI proprietary model | - | High-quality proprietary |

### Reranker Models

| Model | Description | Base Architecture |
|-------|-------------|-------------------|
| `OpenScholar/OpenScholar_Reranker` | Specialized scientific reranker | BAAI/bge-reranker-base |

### Datastores

| Datastore | Description | Scale |
|-----------|-------------|-------|
| `OpenScholar-DataStore-V2` | Initial passage index | 200M+ embeddings |
| `OpenScholar-DataStore-V3` | Enhanced passage index | Improved coverage |

## Model Training Details

### Embedding Model
- **Training Data**: peS2o dataset
- **Base Architecture**: Contriever (contriever/base)
- **Training Method**: Continued pre-training

### Reranker Model
- **Base Architecture**: BGE reranker large
- **Training Data**: Custom scientific paper pairs
- **Framework**: FlagEmbeddings with torch tune

### Generator Model
- **Base Model**: Llama 3.1 8B
- **Training Data**: 13k instruction-tuning samples
- **Hardware**: 8x A100 GPUs
- **Training Data Source**: OpenScholar/OS_Train_Data

## Inference Configuration

### Memory Requirements

| Pipeline | GPU Memory | CPU Memory |
|----------|------------|------------|
| Standard RAG | ~16GB | ~32GB |
| With Reranker | ~20GB | ~32GB |
| Self-Reflective | ~24GB | ~48GB |

### Batch Processing

For large-scale inference:
- Recommended batch size: 8-16
- Max sequence length: 4096 tokens
- Top-k sampling: 50
- Temperature: 0.7

## Model Selection Guidelines

1. **Simple queries**: Standard RAG with `Llama-3.1_OpenScholar-8B`
2. **Complex synthesis**: Add reranker for accuracy
3. **Nuanced claims**: Enable self-reflective pipeline
4. **Maximum quality**: Use GPT-4o with reranking
