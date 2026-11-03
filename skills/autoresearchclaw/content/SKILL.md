---
name: autoresearchclaw
description: Fully autonomous research pipeline that turns research ideas into conference-ready papers. Use when users want to automate academic research, generate papers from topics, conduct literature review, run sandbox experiments, and produce LaTeX documents targeting NeurIPS/ICML/ICLR conferences.
---

# AutoResearchClaw - Autonomous Research Pipeline

## Overview

AutoResearchClaw is a fully autonomous 23-stage research pipeline that transforms a single research idea into a conference-ready academic paper with no human intervention required.

## Key Capabilities

### 23-Stage Pipeline (8 Phases)

| Phase | Stages | Description |
|-------|--------|-------------|
| **Phase A: Research Scoping** | 1-2 | Topic initialization and problem decomposition |
| **Phase B: Literature Discovery** | 3-5 | Multi-source literature search (arXiv, Semantic Scholar) |
| **Phase C: Knowledge Synthesis** | 6-8 | Knowledge extraction, synthesis, hypothesis generation via debate |
| **Phase D: Experiment Design** | 9-11 | Experiment planning, hardware-aware code generation |
| **Phase E: Experiment Execution** | 12-13 | Sandbox experiments with self-healing repair |
| **Phase F: Analysis & Decision** | 14-15 | Multi-agent analysis with PIVOT/REFINE decision |
| **Phase G: Paper Writing** | 16-19 | Outline, drafting, peer review, revision |
| **Phase H: Finalization** | 20-23 | Quality gate, knowledge archive, LaTeX export |

### Core Features

- **Multi-Source Literature**: Real papers from arXiv + Semantic Scholar with query expansion and deduplication
- **4-Layer Citation Verification**: arXiv ID → CrossRef/DataCite DOI → Semantic Scholar title match → LLM relevance scoring
- **Hardware-Aware Execution**: Auto-detects GPU (NVIDIA CUDA / Apple MPS / CPU-only)
- **Sandbox Experiments**: AST-validated code, NaN/Inf fast-fail, self-healing repair, up to 10 refinement rounds
- **Conference-Grade Writing**: NeurIPS/ICML/ICLR LaTeX templates, 5,000-6,500 words
- **Multi-Agent Debate**: Structured multi-perspective debates for hypothesis and peer review
- **Self-Learning**: Lessons extracted with 30-day time-decay
- **Sentinel Watchdog**: Background quality monitoring

### Output Artifacts

| Artifact | Description |
|----------|-------------|
| `paper_draft.md` | Full academic paper |
| `paper.tex` | Conference-ready LaTeX |
| `references.bib` | Verified BibTeX references |
| `verification_report.json` | Citation integrity verification |
| `experiment_runs/` | Generated code + results + metrics |
| `charts/` | Auto-generated comparison charts |
| `reviews.md` | Multi-agent peer review |
| `evolution/` | Self-learning lessons |
| `deliverables/` | All final outputs |

## Usage Instructions

### Installation

```bash
git clone https://github.com/aiming-lab/AutoResearchClaw.git
cd AutoResearchClaw
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

### Configuration

Create `config.arc.yaml`:

```yaml
project:
  name: "my-research"

research:
  topic: "Your research topic here"

llm:
  base_url: "https://api.openai.com/v1"
  api_key_env: "OPENAI_API_KEY"
  primary_model: "gpt-4o"
  fallback_models: ["gpt-4o-mini"]

experiment:
  mode: "sandbox"

sandbox:
  python_path: ".venv/bin/python"
```

### Running the Pipeline

```bash
export OPENAI_API_KEY="sk-..."
researchclaw run --config config.arc.yaml --topic "Your research idea" --auto-approve
```

### Python API

```python
from researchclaw.pipeline import Runner

Runner(config).run()
```

## Configuration Reference

| Section | Key Options |
|---------|-------------|
| **project** | name, mode (docs-first/semi-auto/full-auto) |
| **research** | topic, domains (ml/nlp/physics/chem/econ/math/eng/bio) |
| **llm** | provider, base_url, api_key_env, primary_model, fallback_models |
| **experiment** | mode (simulated/sandbox/docker/ssh_remote), time_budget_sec |
| **sandbox** | python_path, gpu_required, allowed_imports, max_memory_mb |
| **export** | target_conference (neurips_2025/iclr_2026/icml_2026) |
| **security** | hitl_required_stages ([5, 9, 20]) |

## Quality Gates

Three human-in-the-loop checkpoints at Stages 5, 9, and 20 with rollback capability. Use `--auto-approve` for fully autonomous execution.

## Multi-Agent Subsystems

- **CodeAgent**: 4-phase code generation with static analysis and iterative repair
- **BenchmarkAgent**: Domain-aware dataset/baseline selection from 13-domain knowledge base
- **FigureAgent**: Academic-quality chart generation (300 DPI, colorblind-safe)

## Integration

Works with OpenClaw, Claude Code, Codex, Gemini CLI, OpenCode, and Kimi CLI via ACP (Agent Client Protocol).

## References

- GitHub: https://github.com/aiming-lab/AutoResearchClaw
- License: MIT
