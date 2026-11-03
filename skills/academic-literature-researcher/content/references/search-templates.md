# Academic Literature Search Templates

## Database-Specific Search Strategies

### arXiv Search
- **URL**: https://arxiv.org
- **API Endpoint**: https://export.arxiv.org/api/query
- **Search Pattern**: `site:arxiv.org [keywords]` or direct API query
- **Best for**: CS, physics, mathematics, quantitative biology/finance, statistics
- **Fields**: title, abstract, authors, categories, dates

### Elsevier (ScienceDirect) Search
- **URL**: https://www.sciencedirect.com
- **Search Pattern**: `site:sciencedirect.com [keywords]`
- **Best for**: Science, technology, medicine, social sciences
- **Access**: Many papers require subscription

### IEEE Xplore Search
- **URL**: https://ieeexplore.ieee.org
- **Search Pattern**: `site:ieeexplore.ieee.org [keywords]`
- **Best for**: Electrical engineering, computer science, electronics
- **Access**: Many papers require subscription

### Springer Nature Search
- **URL**: https://link.springer.com
- **Search Pattern**: `site:link.springer.com [keywords]`
- **Best for**: Science, technology, medicine, humanities, social sciences
- **Access**: Some open access papers available

## Recommended Search Queries

### Basic Search
```
arxiv [topic] 2024 2025
site:arxiv.org [topic] abs:"[specific term]"
site:sciencedirect.com [topic] research
site:ieeexplore.ieee.org [topic] conference journal
site:link.springer.com [topic] article
```

### Advanced Search with Filters
```
# For recent papers
arxiv [topic] submitted:2024 OR submitted:2025

# For high-impact papers
arxiv [topic] (impact OR breakthrough OR state-of-the-art)

# For methodology papers
"research methodology" [topic] site:elsevier.com
```

## Paper Analysis Prompt Template

```
Analyze the following paper and provide:

1. **Summary** (2-3 sentences):
   What is the main contribution?

2. **Innovation Points**:
   - What is novel compared to prior work?
   - What techniques or approaches are new?

3. **Methodology**:
   - How was the research conducted?
   - What data/benchmarks were used?

4. **Key Findings**:
   - What are the main results?
   - How do they compare to baselines?

5. **Limitations**:
   - What are the weaknesses?
   - What remains unsolved?

6. **Relevance Score** (1-10):
   How relevant is this to [user's specific topic]?
```

## Paper Optimization Checklist

### Structure
- [ ] Clear problem statement in introduction
- [ ] Well-organized methodology section
- [ ] Logical flow between sections
- [ ] Strong conclusion with future work

### Writing Quality
- [ ] Precise technical language
- [ ] Active voice where appropriate
- [ ] Proper academic tone
- [ ] No redundancies

### Citations
- [ ] Recent references (last 5 years)
- [ ] Diverse source types (journals, conferences, arxiv)
- [ ] Proper formatting (APA/IEEE/MLA)
- [ ] No over-reliance on single source

### Methodology Clarity
- [ ] Step-by-step description
- [ ] Sufficient detail for reproducibility
- [ ] Appropriate use of figures/tables
- [ ] Statistical significance noted

### Innovation Emphasis
- [ ] Clear contribution statement
- [ ] Comparison with related work
- [ ] Limitations acknowledged
- [ ] Future directions suggested
