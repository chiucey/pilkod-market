---
name: model-training
description: 本地LLM模型训练技能，支持预训练、LoRA/QLoRA微调、云端API数据增强和Web服务。当用户要求训练语言模型、微调模型、数据增强、模型推理或启动训练服务时使用。
---

# Model Training Skill

A comprehensive local LLM training framework supporting pre-training, LoRA/QLoRA fine-tuning, and cloud API integration for data augmentation.

## Core Capabilities

- **Pre-training**: Train models from scratch with custom architectures
- **LoRA Fine-tuning**: Parameter-efficient fine-tuning with configurable rank
- **QLoRA Fine-tuning**: 4-bit quantized fine-tuning for low-memory environments
- **Cloud API Integration**: OpenAI/Anthropic API for synthetic data generation
- **Web Service**: FastAPI-based REST API for remote control and monitoring
- **Multi-format Support**: Safetensors, GGUF, GPTQ, AWQ model formats

## Configuration Management

### Basic Configuration

```yaml
model:
  name_or_path: "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
  trust_remote_code: true

training:
  mode: "lora"  # pretrain | lora | qlora
  num_train_epochs: 3
  per_device_train_batch_size: 2
  gradient_accumulation_steps: 8
  learning_rate: 2e-4
  fp16: true
  bf16: false
  gradient_checkpointing: true

lora:
  r: 16
  lora_alpha: 32
  lora_dropout: 0.05
  target_modules: ["q_proj", "v_proj"]

data:
  train_path: "data/train.txt"
  validation_path: "data/val.txt"
  max_length: 2048
```

### Cloud API Configuration

```yaml
cloud_training:
  enable: true
  api:
    provider: "openai"  # openai | anthropic
    api_key: "${OPENAI_API_KEY}"
    model_name: "gpt-3.5-turbo"
  enable_data_augmentation: true
  enable_quality_filter: true
  generate_synthetic_data: true
```

## Training Modes

### Pre-training from Scratch

```python
from core.config import AppConfig, TrainingMode
from core.trainer import PretrainRunner

config = AppConfig()
config.model.vocab_size = 32000
config.model.hidden_size = 512
config.model.num_hidden_layers = 8
config.training.mode = TrainingMode.PRETRAIN

runner = PretrainRunner(config)
runner.train()
```

### LoRA Fine-tuning

```python
from core.config import LoRAConfig
from core.trainer import FinetuneRunner

config = AppConfig()
config.lora = LoRAConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
)

runner = FinetuneRunner(config)
runner.train()
```

### QLoRA Fine-tuning (Low Memory)

```python
from core.config import QuantizationConfig

config = AppConfig()
config.training.mode = TrainingMode.QLORA
config.quantization.enable = true
config.quantization.load_in_4bit = true
config.lora.r = 8

runner = FinetuneRunner(config)
runner.train()
```

## Data Formats

### Raw Text Format

```
这是第一段文本
这是第二段文本
这是第三段文本
```

### Alpaca JSON Format

```json
[
    {
        "instruction": "请介绍...",
        "input": "",
        "output": "..."
    }
]
```

### ChatML Format

```json
[
    {
        "messages": [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好，有什么可以帮你的吗？"}
        ]
    }
]
```

## Cloud API Integration

### Data Augmentation Pipeline

```python
from core.api_client import CloudAPIClient, DataAugmentationPipeline
from core.config import CloudTrainingConfig, APIConfig

cloud_config = CloudTrainingConfig(
    enable=True,
    api=APIConfig(
        provider="openai",
        api_key="your-api-key",
        model_name="gpt-3.5-turbo"
    ),
    enable_data_augmentation=True,
    enable_quality_filter=True,
    generate_synthetic_data=True
)

client = CloudAPIClient(cloud_config)

# Generate training samples
samples = await client.generate_samples(
    topic="人工智能",
    count=100,
    style="informative"
)

# Data augmentation
augmented = await client.augment_data(original_texts, augmentation_ratio=0.5)

# Quality filtering
filtered = await client.filter_quality(all_texts)

# Full pipeline
pipeline = DataAugmentationPipeline(client)
result = await pipeline.process_dataset(
    input_path="raw_data.txt",
    output_path="augmented_data.txt",
    augment_ratio=0.3,
    filter_threshold=7.0
)
```

## Inference Engine

### Basic Generation

```python
from core.inference import InferenceEngine

engine = InferenceEngine(config)

# Single generation
result = engine.generate("你好，请介绍一下自己")

# Streaming generation
for token in engine.generate_stream("写一首诗"):
    print(token, end="", flush=True)

# Chat completion
messages = [
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好，有什么可以帮你的吗？"},
    {"role": "user", "content": "介绍一下你自己"},
]
response = engine.chat(messages)
```

## Web API Service

### Start Server

```bash
python -m api.server --config config.yaml --host 0.0.0.0 --port 8000
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/config` | GET/POST | Get/Update configuration |
| `/api/train` | POST | Start training |
| `/api/train/status` | GET | Get training status |
| `/api/train/stop` | POST | Stop training |
| `/api/generate` | POST | Text generation |
| `/api/data/augment` | POST | Data augmentation |
| `/api/data/synthetic` | POST | Generate synthetic data |
| `/api/data/upload` | POST | Upload data file |
| `/api/models` | GET | List available models |

### API Usage Examples

```bash
# Start training
curl -X POST http://localhost:8000/api/train \
  -H "Content-Type: application/json" \
  -d '{"mode": "finetune", "model_name": "TinyLlama/TinyLlama-1.1B-Chat-v1.0"}'

# Get training status
curl http://localhost:8000/api/train/status

# Text generation
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "你好，请介绍一下自己", "max_new_tokens": 512}'

# Data augmentation
curl -X POST http://localhost:8000/api/data/augment \
  -H "Content-Type: application/json" \
  -d '{"input_path": "data/train.txt", "output_path": "data/augmented.txt"}'
```

## Hardware Optimization

### RTX 5060 (8GB VRAM) Recommended Settings

```yaml
training:
  per_device_train_batch_size: 2
  gradient_accumulation_steps: 8
  fp16: true
  bf16: false

lora:
  r: 8
  lora_alpha: 16

quantization:
  enable: true
  load_in_4bit: true
```

### Memory Optimization Techniques

- **Mixed Precision**: FP16/BF16 to reduce VRAM usage
- **Gradient Checkpointing**: Trade compute for memory
- **QLoRA Quantization**: 4-bit quantization significantly reduces memory requirements
- **Gradient Accumulation**: Simulate larger batch sizes with smaller ones

## Interactive CLI

### Setup Wizard

```bash
python -m cli.interface init
```

The wizard guides through:
1. Path configuration (data, model directories)
2. Hardware detection (GPU, recommended batch size)
3. Training mode selection (pretrain, LoRA, QLoRA)
4. Model configuration (architecture or open-source model)
5. Data configuration (training data or sample datasets)
6. Optimizer configuration (learning rate, batch size)
7. Cloud training (optional API-assisted training)

### CLI Commands

```bash
# View system information
python -m cli.interface info

# Train model
python -m cli.interface train config.yaml --mode finetune

# Run inference
python -m cli.interface infer config.yaml "你好，请介绍一下自己"

# Start web service
python -m cli.interface serve config.yaml --host 0.0.0.0 --port 8000

# View supported formats
python -m cli.interface formats

# Get model info
python -m cli.interface model-info /path/to/model
```

## Model Formats

| Format | Description | Quantization | Use Case | VRAM |
|--------|-------------|--------------|----------|------|
| Safetensors | HuggingFace native, fast loading | No | Training, fine-tuning | High |
| PyTorch | Standard .bin/.pt format | No | General | High |
| GGUF | llama.cpp quantization, CPU-efficient | Yes | Local inference, low VRAM | Low |
| GPTQ | 4/8bit quantization | Yes | Efficient inference | Medium |
| AWQ | Activation-aware quantization | Yes | Efficient inference | Medium |

### Install Format Support

```bash
# GGUF format (recommended for inference)
pip install llama-cpp-python

# GPU acceleration (NVIDIA CUDA)
pip install llama-cpp-python --force-reinstall --no-cache-dir

# GPTQ format support
pip install auto-gptq

# AWQ format support
pip install autoawq
```

## Requirements

```
# Core deep learning
torch>=2.0.0
torchvision>=0.15.0

# Hugging Face ecosystem
transformers>=4.35.0
datasets>=2.14.0
tokenizers>=0.15.0
accelerate>=0.25.0
peft>=0.7.0
trl>=0.7.0

# Model quantization
bitsandbytes>=0.41.0
auto-gptq>=0.4.0

# Web service
fastapi>=0.104.0
uvicorn[standard]>=0.24.0

# Data processing
numpy>=1.24.0
pandas>=2.0.0

# Training monitoring
tensorboard>=2.15.0
wandb>=0.16.0

# Configuration
pydantic>=2.5.0
pyyaml>=6.0

# CLI
click>=8.1.0
inquirer>=3.1.0
```

## Troubleshooting

### Out of Memory (OOM)

1. Enable QLoRA quantization: `quantization.enable = true`
2. Reduce batch size: `per_device_train_batch_size = 1`
3. Reduce max_length: `tokenizer.max_length = 1024`
4. Enable gradient checkpointing: `gradient_checkpointing = true`

### Training Recovery

Training automatically saves checkpoints. Resume with:

```bash
python -m cli.interface train config.yaml
```

### Custom Model

```python
from core.config import FinetuneModelConfig

config.finetune_model = FinetuneModelConfig(
    name_or_path="your-model-path-or-name"
)
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Local Training Environment              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │   CLI/Web   │    │   Trainer   │    │  Inference  │      │
│  │   Interface │    │   Engine    │    │   Engine    │      │
│  └─────────────┘    └─────────────┘    └─────────────┘      │
│                            │                                 │
│  ┌─────────────────────────┴─────────────────────────────┐  │
│  │              Configuration Management                  │  │
│  │                  (AppConfig)                           │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ API Calls
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Cloud API Services                      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │  Synthetic  │    │   Quality   │    │  Augment    │      │
│  │    Data     │    │   Filter    │    │    Data     │      │
│  └─────────────┘    └─────────────┘    └─────────────┘      │
│         Supports: OpenAI GPT-3.5/GPT-4, Anthropic Claude   │
└─────────────────────────────────────────────────────────────┘
```
