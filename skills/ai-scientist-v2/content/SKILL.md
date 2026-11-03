---
name: ai-scientist-v2
description: >
  Use when users ask to generate research hypotheses, run ML experiments autonomously,
  write scientific papers, conduct literature review, perform novelty checking, or
  generate academic manuscripts automatically. This is a fully autonomous scientific
  research agent that generates ideas, runs experiments, and produces LaTeX papers.
  Triggers on: run AI scientist, autonomous research, generate research ideas,
  automated paper writing, AI-driven experiments, scientific manuscript generation.
---

# AI Scientist-v2

An end-to-end autonomous scientific research system that generates hypotheses, runs experiments, analyzes data, and writes scientific manuscripts.

## Capabilities

- **Hypothesis Generation**: Generate novel research ideas from a topic description
- **Autonomous Experimentation**: Execute ML experiments using agentic tree search (BFTS)
- **Paper Writing**: Generate LaTeX scientific manuscripts with visualizations
- **Literature Search**: Semantic Scholar API integration for novelty checking
- **Multi-Model Support**: OpenAI, Gemini, Claude via AWS Bedrock

## Workflow

### 1. Prepare Research Topic

Create a markdown file with your research topic:

```markdown
# Title
Your research title here

## Keywords
machine learning, optimization, neural networks

## TL;DR
Brief summary of your research direction

## Abstract
Detailed description of the research area and goals
```

### 2. Generate Research Ideas

Run the ideation script:

```bash
python ai_scientist/perform_ideation_temp_free.py \
  --workshop-file "path/to/your_topic.md" \
  --model gpt-4o-2024-05-13 \
  --max-num-generations 20 \
  --num-reflections 5
```

### 3. Run Experiments & Generate Paper

Execute the main pipeline:

```bash
python launch_scientist_bfts.py \
  --load_ideas "path/to/generated_ideas.json" \
  --load_code \
  --add_dataset_ref \
  --model_writeup o1-preview-2024-09-12 \
  --model_citation gpt-4o-2024-11-20 \
  --model_review gpt-4o-2024-11-20 \
  --model_agg_plots o3-mini-2025-01-31 \
  --num_cite_rounds 20
```

### 4. Configuration Options

Edit `bfts_config.yaml` to customize:

- `num_workers`: Parallel exploration paths
- `steps`: Maximum nodes to explore
- `num_seeds`: Independent tree count
- `max_debug_depth`: Debugging attempts
- `num_drafts`: Initial root nodes in Stage 1

## Environment Setup

```bash
# Create environment
conda create -n ai_scientist python=3.11
conda activate ai_scientist

# Install PyTorch with CUDA
conda install pytorch torchvision torchaudio pytorch-cuda=12.4 -c pytorch -c nvidia

# Install LaTeX tools
conda install anaconda::poppler
conda install conda-forge::chktex

# Install dependencies
pip install -r requirements.txt

# Optional: Claude via Bedrock
pip install anthropic[bedrock]
```

## API Keys

```bash
export OPENAI_API_KEY="your-key"
export S2_API_KEY="your-semantic-scholar-key"

# Optional: AWS Bedrock for Claude
export AWS_ACCESS_KEY_ID="your-aws-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret"
export AWS_REGION_NAME="us-west-2"
```

## Output

Results are saved in `experiments/timestamp_ideaname/`:
- PDF paper with LaTeX
- Experiment logs
- Tree visualization (`unified_tree_viz.html`)
- Generated code and plots

## Safety Warning

[WARNING] This system executes LLM-generated code. Run in a controlled sandbox (Docker container) to prevent unintended system access.

## Model Recommendations

| Task | Recommended Model |
|------|-------------------|
| Writing | o1-preview, Claude 3.5 Sonnet |
| Citation | GPT-4o |
| Review | GPT-4o |
| Plots | o3-mini |

## Cost Estimates

- Ideation: ~$2-5
- Main experiment: ~$15-20
- Writing phase: ~$5

**Estimated Total**: $20-30 per successful paper

## References

- Paper: https://pub.sakana.ai/ai-scientist-v2/paper
- Blog: https://sakana.ai/ai-scientist-first-publication/
