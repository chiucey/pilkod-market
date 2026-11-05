# Example Research Topic Format

Below is an example of a research topic file for AI Scientist-v2:

```markdown
# It's Not (Always) Better: An Investigation of the Law of Large Neurons

## Keywords
scaling laws, neural network efficiency, lottery ticket hypothesis, network compression

## TL;DR
We investigate whether larger networks always outperform smaller ones, challenging conventional wisdom about scaling in neural networks.

## Abstract
Deep learning practitioners typically assume that larger neural networks with more parameters consistently outperform smaller ones given sufficient training time. In this work, we challenge this assumption by conducting a systematic investigation of the relationship between network size and final performance across multiple domains. We discover surprising cases where smaller, more efficient networks match or exceed their larger counterparts. Our findings have implications for efficient model design and resource allocation in ML research.
```

## Idea File Output Format

The ideation script generates a JSON file with research ideas:

```json
{
  "ideas": [
    {
      "id": 1,
      "title": "Title of Research Idea",
      "description": "Detailed description of the approach",
      "novelty_score": 0.85,
      "feasibility_score": 0.7,
      "potential_impact": "High"
    }
  ]
}
```

## BFTS Configuration

The `bfts_config.yaml` controls the experiment tree search:

```yaml
bfts:
  num_workers: 4           # Parallel exploration paths
  steps: 50                # Max nodes to explore
  num_seeds: 3             # Independent trees

stage1:
  num_drafts: 5             # Initial root nodes

debugging:
  max_debug_depth: 3       # Max debugging attempts
  debug_prob: 0.5          # Probability of debugging
```

## API Key Configuration

### OpenAI
```bash
export OPENAI_API_KEY="sk-..."
```

### Google Gemini
```bash
export GEMINI_API_KEY="..."
```

### Claude via AWS Bedrock
```bash
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION_NAME="us-west-2"
pip install anthropic[bedrock]
```

### Semantic Scholar
```bash
export S2_API_KEY="..."
```

## Hardware Requirements

- **GPU**: NVIDIA GPU with CUDA support (16GB+ VRAM recommended)
- **RAM**: 32GB+ recommended
- **Storage**: 50GB+ for experiments and generated papers
- **OS**: Linux (Ubuntu 20.04+ recommended)

## Docker Setup (Recommended)

```dockerfile
FROM nvidia/cuda:12.4.0-devel-ubuntu22.04

RUN apt-get update && apt-get install -y \
    python3.11 \
    conda \
    poppler \
    chktex \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
COPY requirements.txt .
RUN pip install -r requirements.txt

# Set API keys
ENV OPENAI_API_KEY="your-key"
ENV S2_API_KEY="your-key"
```
