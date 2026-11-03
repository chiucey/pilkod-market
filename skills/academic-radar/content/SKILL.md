---
name: academic-radar
description: Intelligent academic hotspot tracking tool for researchers. Use when users need to track latest research progress, search academic papers, generate research reports, understand field trends, or get paper recommendations. Trigger phrases include "track academic hotspots", "search latest papers", "generate research report", "understand field trends", "paper recommendations", etc.
---

# Academic Radar

Intelligent academic hotspot tracking tool designed for researchers, helping you easily track the latest developments in your research field.

## Core Features

### 1. Intelligent Paper Search

Automatically search for latest papers from multiple top academic sources:

- **arXiv**: Preprints in computer science, physics, mathematics, statistics, etc.
- **Nature**: Multidisciplinary coverage including biology, physics, chemistry
- **Science**: Top-tier comprehensive academic journal
- **PubMed**: Biomedical literature
- **Semantic Scholar**: Academic paper metadata

### 2. Multi-Dimensional Scoring & Filtering

Intelligent paper scoring based on 5 dimensions:

| Dimension | Weight | Evaluation Content |
|-----------|--------|-------------------|
| Keyword Match | 30% | Relevance to user's research field |
| Academic Impact | 25% | Citation count, journal impact factor, author h-index |
| Timeliness | 20% | Publication time, update time |
| Novelty | 15% | Innovation level, differentiation from existing research |
| Methodology Quality | 10% | Research design, data processing, experimental validation |

### 3. In-Depth Analysis Reports

Generate structured academic analysis reports:

- **Hotspot Summary**: Most popular research topics in the field this week/month
- **Paper Analysis**: Innovation points, methodology, conclusion interpretation of key papers
- **Trend Analysis**: Evolution of research directions in the field
- **Topic Suggestions**: Potential research topics based on frontier hotspots

### 4. Personalized Configuration

Flexible personalized settings:

- Research field (physics, computer science, biomedical, etc.)
- Keywords (multiple core keywords and expanded keywords)
- Score threshold (high/medium/low quality paper filtering)
- Time range (last week/month/quarter)
- Subscription source selection (arXiv, Nature, Science, etc.)

## Target Users

### Graduate Students

**Use Case**: Understanding latest field developments before thesis proposal

- Quickly grasp field fundamentals and development trends
- Identify current research hotspots and frontier directions
- Discover potential research entry points

### PhD Students

**Use Case**: Regular tracking of academic frontier progress

- Maintain sensitivity to latest field developments
- Assist with literature review and research background writing
- Discover interdisciplinary collaboration opportunities

### Researchers

**Use Case**: Finding innovative research topics

- Identify underexplored research gaps
- Discover new research methods and experimental techniques
- Track competitor and collaborator research dynamics

### Academic Enthusiasts

**Use Case**: Following latest developments in areas of interest

- Satisfy curiosity about scientific knowledge
- Understand technology development trends and social impact
- Expand knowledge boundaries and cognitive horizons

## Usage

### Zero-Threshold Usage

Simply provide the following information to automatically generate professional academic reports:

```
1. Research field/discipline direction
2. Core keywords (1-5)
3. Report type (weekly/monthly/special report)
4. Target subscription sources (optional)
```

### Usage Examples

**Example 1: Generate Computer Vision Weekly Report**
```
User: I want to understand the latest developments in computer vision, especially regarding Transformer architecture applications in image tasks

System: Generate academic weekly report including:
- Recent arXiv papers on Transformer+CV
- In-depth analysis of high-scoring papers
- Technology trend analysis
- Potential research topic suggestions
```

**Example 2: Track Latest Progress on Specific Topic**
```
User: Follow up on the latest experimental progress related to "quantum entanglement"

System: Provide:
- Latest Nature/Science papers on quantum entanglement experiments
- Innovation points in experimental methods
- Comparison with theoretical models
- Future research direction outlook
```

## Technical Implementation

### Paper Acquisition

- RSS subscription source timed crawling
- API interface direct calls (arXiv API, Semantic Scholar API)
- Webpage structured data extraction

### Intelligent Scoring Algorithm

```
Paper Score = Σ(Dimension Weight × Dimension Score) × Normalization Coefficient

Normalization Coefficient = Percentile conversion based on same batch paper scores
```

### Report Generation

- Structured data extraction and integration
- Key information summarization
- Trend chart visualization
- Multi-format output (Markdown, HTML, PDF)

## Notes

1. **Data Sources**: Prioritize official APIs and RSS to ensure data authority
2. **Timeliness**: Recommended weekly update, pay attention to data deduplication during long-term tracking
3. **Score Threshold**: Adjustable according to needs to avoid missing important papers
4. **Copyright Compliance**: Only analyze paper metadata and abstracts, not full-text copyrighted content

## Extended Features

- Email/message subscription push
- Paper collection and notes
- Sync with Zotero/EndNote and other reference management tools
- Academic social network dynamic tracking

---

**Author**: MiniMax Agent
**Version**: 1.0
**Updated**: 2026-04-10
