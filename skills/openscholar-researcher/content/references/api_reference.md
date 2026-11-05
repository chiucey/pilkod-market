# OpenScholar API Reference

## Main Inference Script

```bash
python run.py [OPTIONS]
```

### Required Arguments

| Argument | Type | Description |
|----------|------|-------------|
| `--input_file` | str | Path to input JSON file with queries |
| `--output_file` | str | Path to save output results |
| `--model_name` | str | Model name or path |

### Optional Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--top_n` | int | 10 | Number of passages for LM |
| `--use_contexts` | flag | False | Enable context usage |
| `--zero_shot` | flag | False | Zero-shot inference |
| `--ranking_ce` | flag | False | Enable reranking |
| `--reranker` | str | None | Reranker model path |
| `--feedback` | flag | False | Self-feedback loop |
| `--posthoc` | flag | False | Post-hoc citation attribution |
| `--ss_retriever` | flag | False | Use Semantic Scholar API |
| `--use_abstract` | flag | False | Include abstract in reranking |
| `--max_per_paper` | int | None | Max passages per paper |
| `--min_citation` | int | None | Min citation threshold |
| `--llama3` | flag | False | Use Llama 3 chat format |
| `--api` | str | None | API provider (openai) |
| `--api_key_fp` | str | None | Path to API key file |

## Input File Format

```json
{
  "queries": [
    {
      "id": "q1",
      "question": "What are the latest advances in protein folding?"
    }
  ]
}
```

## Output Format

```json
{
  "results": [
    {
      "id": "q1",
      "question": "What are the latest advances in protein folding?",
      "answer": "Recent advances include AlphaFold2...",
      "citations": [
        {
          "paper_id": "s2:xxx",
          "title": "Improved Protein Structure Prediction...",
          "authors": ["Jumper, J.", "..."],
          "year": 2021,
          "venue": "Nature",
          "relevance": 0.95
        }
      ],
      "passages": [...]
    }
  ]
}
```

## Semantic Scholar API

### Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/paper/search` | Search papers by query |
| `/paper/{paper_id}` | Get paper details |
| `/paper/{paper_id}/abstract` | Get paper abstract |

### Rate Limits

- Free tier: 100 requests/day
- Pro tier: 1000 requests/day
- Enterprise: Higher limits available

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `S2_API_KEY` | Yes | Semantic Scholar API key |
| `YOUR_API_KEY` | No | Web search API key |

## Error Handling

| Error Code | Description | Resolution |
|------------|-------------|------------|
| 401 | Invalid API key | Check S2_API_KEY |
| 429 | Rate limit exceeded | Add delay between requests |
| 500 | Server error | Retry with exponential backoff |
| 503 | Service unavailable | Check Semantic Scholar status |
