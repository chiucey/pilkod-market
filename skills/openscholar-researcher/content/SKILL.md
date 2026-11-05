---
name: openscholar-researcher
description: "OpenScholar scientific literature synthesis assistant. Use when users need to synthesize scientific literature, conduct academic research, answer research questions with citations, perform literature review, analyze academic papers, or generate research-grounded responses. Triggers on: research papers, literature review, academic synthesis, scientific Q&A, paper citations, find papers about, what does research say about."
---

# OpenScholar Research Assistant

A retrieval-augmented language model (RAG-LM) designed to help scientists navigate and synthesize scientific literature. OpenScholar answers queries by searching for relevant papers and generating responses grounded in those sources.

## Core Capabilities

- **Literature Synthesis**: Generate comprehensive answers based on multiple scientific papers
- **Citation-Grounded Responses**: All claims are backed by specific paper citations
- **Multi-Pipeline Support**: Standard RAG, reranked retrieval, and self-reflective generation
- **Academic Search**: Leverages Semantic Scholar API for paper discovery
- **Multi-Model Support**: Works with OpenScholar-8B, GPT-4o, or other LLMs

## Workflow

### 1. Query Analysis
- Parse the user's research question or topic
- Identify key concepts and search terms
- Determine appropriate retrieval strategy

### 2. Literature Retrieval
- Search Semantic Scholar for relevant papers
- Retrieve passages from OpenScholar datastore (200M+ embeddings)
- Apply reranking if enabled (using OpenScholar_Reranker)

### 3. Response Generation
- Generate answer using selected passages as context
- Include inline citations to source papers
- Enable self-feedback loop for accuracy (optional)

### 4. Citation Formatting
- Format citations in academic style
- Provide paper metadata (title, authors, venue)
- Include confidence indicators for claims

## Inference Pipelines

Choose the appropriate pipeline based on requirements:

| Pipeline | Use Case | Command Flag |
|----------|----------|--------------|
| Standard RAG | Fast, baseline results | `--zero_shot --top_n 10` |
| Reranked | Higher accuracy | `--ranking_ce --reranker OpenScholar/OpenScholar_Reranker` |
| Self-Reflective | Complex synthesis | `--posthoc --feedback --ss_retriever --use_abstract` |

## Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `top_n` | Number of passages for LM | 10 |
| `max_per_paper` | Max passages per paper | None |
| `zero_shot` | Zero-shot inference mode | false |
| `ranking_ce` | Enable reranking | false |
| `feedback` | Self-feedback loop | false |
| `posthoc` | Post-hoc citation attribution | false |

## Example Usage Patterns

### Research Question Answering
```
Topic: "What are the latest advances in protein folding prediction?"
Output: Comprehensive answer with citations from recent papers
```

### Literature Review
```
Topic: "Compare transformer architectures for NLP"
Output: Structured comparison with references to key papers
```

### Claim Verification
```
Claim: "mRNA vaccines are safe for pregnant women"
Output: Evidence-based response citing relevant clinical studies
```

## API Integration

### Semantic Scholar API
- Primary source for paper metadata and abstracts
- Required: `S2_API_KEY`
- Get key at: https://www.semanticscholar.org/product/api

### OpenScholar Models (HuggingFace)
- Generator: `OpenScholar/Llama-3.1_OpenScholar-8B`
- Reranker: `OpenScholar/OpenScholar_Reranker`
- Datastore: `OpenScholar/OpenScholar-DataStore-V3`

## Output Format

Generate structured research responses:

```
## Answer
[Comprehensive answer based on retrieved papers]

## References
1. [Paper Title] et al. ([Year])
   - Key finding: [Brief description]
   - Confidence: [High/Medium/Low]
   - Link: [Paper URL]

2. ...
```

## Quality Guidelines

1. **Always cite sources**: Every factual claim must be attributed to a source
2. **Acknowledge limitations**: Note gaps in literature when relevant
3. **Distinguish confidence levels**: Clearly indicate certainty of claims
4. **Provide diverse perspectives**: Include papers with differing conclusions when available
5. **Link to primary sources**: Always provide paper links for further reading

## Resources

- Detailed API documentation: See `references/api_reference.md`
- Model information: `references/models.md`
- Installation guide: `references/installation.md`
- Example outputs: `references/examples.md`
