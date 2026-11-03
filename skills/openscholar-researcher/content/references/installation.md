# OpenScholar Installation Guide

## Prerequisites

- Python 3.10.0+
- CUDA-capable GPU (for local inference)
- Semantic Scholar API key

## Installation Steps

### 1. Create Environment

```bash
conda create -n os_env python=3.10.0
conda activate os_env
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. API Key Setup

```bash
export S2_API_KEY=YOUR_S2_API_KEY
```

Get API keys from: https://www.semanticscholar.org/product/api

### 4. Optional: Web Search API

For enhanced web search capabilities:

```bash
export YOUR_API_KEY=YOUR_YOU_COM_API_KEY
```

## Model Download

Models are hosted on HuggingFace:

- **Generator**: `OpenScholar/Llama-3.1_OpenScholar-8B`
- **Reranker**: `OpenScholar/OpenScholar_Reranker`
- **Datastore**: `OpenScholar/OpenScholar-DataStore-V3`

## Verification

Test installation:

```bash
python run.py \
  --input_file test_input.json \
  --model_name OpenScholar/Llama-3.1_OpenScholar-8B \
  --use_contexts \
  --output_file test_output.json \
  --top_n 5 --llama3 --zero_shot
```

## Docker Deployment (Optional)

For containerized deployment, see the project's Docker configuration.
