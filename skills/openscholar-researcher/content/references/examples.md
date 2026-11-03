# OpenScholar Usage Examples

## Example 1: Basic Literature Search

**Query**: "What are the key advances in large language model reasoning?"

**Command**:
```bash
python run.py \
  --input_file queries.json \
  --model_name OpenScholar/Llama-3.1_OpenScholar-8B \
  --use_contexts \
  --output_file results.json \
  --top_n 10 --llama3 --zero_shot
```

**Output**:
```
## Answer

Recent advances in LLM reasoning have focused on several key areas:

1. **Chain-of-Thought Prompting**: Models like PaLM and GPT-4 demonstrate improved reasoning through step-by-step explanation generation [1][2].

2. **Self-Consistency**: Wang et al. show that sampling multiple reasoning paths and selecting the most consistent answer improves accuracy by 15-20% on math benchmarks [3].

3. **Tool Use**: Models augmented with external tools (calculators, code interpreters) show enhanced mathematical and logical reasoning capabilities [4].

## References

[1] Wei et al. "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models" (NeurIPS 2022)
[2] Chowdhery et al. "PaLM: Scaling Language Modeling with Pathways" (JMLR 2023)
[3] Wang et al. "Self-Consistency Improves Chain of Thought Reasoning in Language Models" (ICLR 2023)
[4] Schick et al. "Toolformer: Language Models Can Teach Themselves to Use Tools" (ICLR 2023)
```

## Example 2: Reranked Retrieval for Precision

**Query**: "Compare BERT and GPT architectures for text classification"

**Command**:
```bash
python run.py \
  --input_file queries.json \
  --model_name OpenScholar/Llama-3.1_OpenScholar-8B \
  --use_contexts \
  --ranking_ce \
  --reranker OpenScholar/OpenScholar_Reranker \
  --output_file results.json \
  --top_n 10 --llama3 --zero_shot
```

**Output**:
```
## Answer

BERT and GPT represent two fundamentally different approaches to transformer architecture:

| Aspect | BERT | GPT |
|--------|------|-----|
| Architecture | Encoder-only | Decoder-only |
| Training | Masked LM | Next token prediction |
| Fine-tuning | Required | Minimal |
| Best for | Classification, NER | Generation |

Recent benchmarks show BERT variants achieve 2-3% higher accuracy on standard classification tasks, while GPT models excel in zero-shot scenarios [1][2].

## References

[1] Devlin et al. "BERT: Pre-training of Deep Bidirectional Transformers..." (NAACL 2019)
[2] Brown et al. "Language Models are Few-Shot Learners" (NeurIPS 2020)
```

## Example 3: Self-Reflective Synthesis

**Query**: "What is the current state of AI alignment research?"

**Command**:
```bash
python run.py \
  --input_file queries.json \
  --model_name OpenScholar/Llama-3.1_OpenScholar-8B \
  --use_contexts --output_file results.json \
  --top_n 10 --llama3 \
  --ranking_ce --reranker OpenScholar/OpenScholar_Reranker \
  --posthoc --feedback --ss_retriever \
  --use_abstract --norm_cite --zero_shot --max_per_paper 3
```

**Output**:
```
## Answer

AI alignment research addresses the challenge of ensuring AI systems behave in ways intended by their designers...

### Current Research Themes

1. **Scalable Oversight**: Developing methods to supervise AI on complex tasks [1]
2. **Interpretability**: Understanding model internals [2]
3. **Robustness**: Ensuring reliable behavior under distribution shift [3]

### Open Problems

- Scalability of human feedback
- Formal verification of safety properties
- Handling goal misgeneralization

**Confidence**: High - supported by multiple recent publications from major AI labs

## References

[1] Amodei et al. "Concrete Problems in AI Safety" (2016)
[2] Olah et al. "Zoom In: An Introduction to Circuits" (2020)
[3] Dinan et al. "Build, Break, and Check: Specification Testing..." (2022)
```

## Example 4: Using Proprietary LMs

**Command**:
```bash
python run.py \
  --input_file queries.json \
  --model_name "gpt-4o" \
  --api "openai" \
  --api_key_fp /path/to/openai_key \
  --use_contexts \
  --output_file results.json \
  --top_n 10 --llama3 --zero_shot
```

## Example 5: Batch Processing

**Input file (queries.json)**:
```json
{
  "queries": [
    {"id": "q1", "question": "What is attention mechanism?"},
    {"id": "q2", "question": "Explain transformers architecture"},
    {"id": "q3", "question": "What is transfer learning in NLP?"}
  ]
}
```

**Execution**:
```bash
python run.py \
  --input_file queries.json \
  --model_name OpenScholar/Llama-3.1_OpenScholar-8B \
  --use_contexts \
  --output_file batch_results.json \
  --top_n 10 --llama3 --zero_shot
```
