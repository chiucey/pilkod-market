---
name: deepscientist-research
description: DeepScientist 自主科学发现助手。当用户需要进行AI科学研究、自动化论文生成、科学假设验证、贝叶斯优化研究、AI任务优化、超越SOTA方法、或需要类似DeepScientist系统的科学发现工作流时使用。
---

# DeepScientist Research Assistant

## Overview

DeepScientist is an autonomous scientific discovery system that transforms the research process into a formalized Bayesian Optimization problem. This skill provides guidance for conducting goal-oriented, fully autonomous scientific discovery.

## Core Methodology

### Problem Formulation

Scientific discovery is modeled as searching for an optimal solution within a vast space of candidate research methods:

```
I* = arg max_{I∈ℐ} f(I)
```

Where `f(I)` represents the latent value function mapping a method to its empirical impact.

### Three-Stage Exploration Cycle

1. **Strategize & Hypothesize**: Analyze Findings Memory, identify limitations in existing knowledge, generate hypotheses, evaluate using Surrogate Model (LLM Reviewer)

2. **Implement & Verify**: Use Upper Confidence Bound (UCB) algorithm to select promising candidates, execute implementation in sandboxed environment

3. **Analyze & Report**: Design and execute deeper analytical experiments, collate results into reproducible research papers

## Key Features

### Multi-Agent Architecture
- **Findings Memory**: Stores frontier human knowledge (papers, codes) and system's historical findings
- **Retrieval Model**: Selects Top-K Findings for context
- **Surrogate Model**: LLM Reviewer for value approximation
- **Coding Agent**: Executes in sandboxed Docker containers with full permissions
- **MCP Tools**: Manages experimental lifecycle and data collection

### Discovery Loop
The system implements a closed-loop iterative process that:
- Learns from both human knowledge and its own experiments
- Progressively promotes promising findings to higher-fidelity validation
- Balances exploration of novel hypotheses with exploitation of promising directions

## Usage Patterns

### For Hypothesis Generation
- Analyze current SOTA limitations
- Query Findings Memory for related work
- Generate novel hypothesis collections
- Evaluate with structured valuation vectors (utility, quality, exploration value)

### For Experimental Validation
- Select promising candidates using UCB acquisition function
- Implement in sandboxed environment with internet access
- Execute automated experiments and collect results
- Perform ablation studies and deeper analysis

### For Paper Generation
- Synthesize experimental results
- Create reproducible research documentation
- Format findings into structured scientific papers

## Performance Metrics

| Task | Human SOTA | DeepScientist | Improvement |
|------|------------|---------------|-------------|
| Agent Failure Attribution | 12.07% | 29.31% (A2P) | +142.8% |
| LLM Inference Acceleration | 190.25 tokens/s | 193.90 tokens/s | +1.9% |
| AI Text Detection | 0.800 AUROC | 0.863 AUROC | +7.9% |

## Scaling Guidelines

Near-linear relationship between computational resources and valuable discoveries:
- 1 GPU: ~0 Progress Findings
- 4 GPUs: ~1 Progress Finding
- 16 GPUs: ~11 Progress Findings

## Limitations

- ~60% of failed trials terminated due to implementation errors
- Success rate of 1-5% mirrors frontier research reality
- Human expert supervision recommended for output verification

## Reference Resources

- Project: https://ai-researcher.net
- GitHub: https://github.com/ResearAI/DeepScientist
- arXiv: 2509.26603v1
