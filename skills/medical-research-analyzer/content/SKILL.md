---
name: medical-research-analyzer
description: Medical Research Analyzer - Automatically collects medical information and generates analysis reports. Use when users ask about medical topics, disease research, treatment methods, drug information, latest medical advances, clinical trials, or medical guidelines.
---

# Medical Research Analyzer

## Core Capabilities

This skill automatically performs the following task chain:

1. **Intelligent Search**: Retrieve relevant topics from authoritative medical sources
2. **Content Extraction**: Extract key information from professional medical websites
3. **Quality Assessment**: Evaluate the reliability and timeliness of sources
4. **Analysis Integration**: Synthesize information from multiple sources for professional analysis
5. **Report Generation**: Output structured, readable medical analysis reports

## Source Priority

Graded retrieval by authority and professionalism:

| Priority | Source Type | Examples |
|----------|-------------|----------|
| 1 | Top-tier Medical Journals | NEJM, The Lancet, JAMA, BMJ |
| 2 | Medical Databases | PubMed, Cochrane Library, FDA |
| 3 | Professional Medical Sites | WHO, NIH, Mayo Clinic, WebMD |
| 4 | Clinical Guidelines | Clinical practice guidelines by specialty |
| 5 | Medical News | Medical News Today, Medscape |

## Workflow

### Step 1: Requirements Analysis

Parse user queries, clarifying the following elements:

- **Topic Type**: Disease, drug, treatment method, research progress, guideline interpretation
- **Medical Field**: Cardiovascular, oncology, neurology, pediatrics, etc.
- **Information Need**: Basic knowledge, latest advances, comparative analysis, practical advice
- **Target Audience**: Medical professionals, patients, researchers

### Step 2: Information Collection

#### Search Strategy

Choose search strategy based on topic type:

```
Disease Query:
- Search terms: [Disease name] + "symptoms" + "treatment" + "guidelines"
- Priority sources: Clinical guidelines, WHO, professional societies

Drug Query:
- Search terms: [Drug name] + "indications" + "dosage" + "side effects"
- Priority sources: FDA, drug databases, professional pharmacy sites

Research Progress Query:
- Search terms: [Disease/field] + "latest research" + "clinical trial" + "2024/2025"
- Priority sources: PubMed, top journals, medical news
```

#### Parallel Collection

Use `batch_web_search` tool for multi-source parallel search:

- Simultaneously search at least 3-5 different authoritative sources
- Cover different types (journals, guidelines, news, professional sites)
- Ensure breadth and reliability of information

### Step 3: Content Extraction

Use `extract_content_from_websites` tool to extract detailed information:

- Prioritize authoritative content published within the last 1-2 years
- Extract key data points: statistics, research conclusions, guideline recommendations
- Record source and publication time

### Step 4: Information Analysis and Integration

#### Reliability Scoring

Evaluate each information source based on these criteria:

| Score | Criteria |
|-------|----------|
| High | Peer-reviewed journals, government agencies, international organizations |
| Medium | Professional societies, renowned hospitals, authoritative medical databases |
| Low | Commercial websites, non-peer-reviewed content |

#### Information Categorization

Classify collected information:

- **Core Facts**: Definitions, mechanisms, standard treatments
- **Latest Advances**: New therapies, research breakthroughs, clinical trial results
- **Controversy Points**: Academic debates, differences between guidelines
- **Practical Advice**: Patient education, prevention measures, self-management

### Step 5: Report Generation

Generate structured analysis reports containing the following modules:

```
## 1. Overview
- Topic definition and background
- Clinical significance

## 2. Core Information
### 2.1 Basic Knowledge
### 2.2 Diagnostic Criteria
### 2.3 Mainstream Treatment Methods

## 3. Latest Research Advances
- Recent important studies
- Clinical trial updates
- Emerging therapies and technologies

## 4. Authority Guideline Interpretation
- Latest guideline key points
- Differences between guidelines

## 5. Practical Information
### 5.1 Common Patient Questions
### 5.2 Prevention and Screening Recommendations

## 6. Information Sources
- Citation list (with reliability and time annotations)

## 7. Summary and Recommendations
- Key takeaways
- Areas for follow-up attention
```

## Output Quality Standards

### Accuracy

- All medical statements must be based on reliable sources
- Clearly cite source information and evidence levels
- Do not provide unverified medical advice

### Timeliness

- Prioritize authoritative materials from the past 3 years
- Note publication dates
- Indicate possible future developments

### Readability

- Use accessible professional language
- Appropriately use lists and tables
- Avoid excessive use of technical abbreviations

## Important Notes

### Usage Limitations

- **Not a Substitute for Medical Advice**: Clearly remind users to consult professional doctors
- **No Diagnosis Provided**: Only provide general medical information
- **No Specific Drug Dosage Recommendations**: Cite official data but do not provide specific advice
- **Note Source Limitations**: Some content may require paid subscriptions

### Ethics and Compliance

- Do not spread unverified medical information
- Do not provide any form of medical diagnosis services
- Respect medical ethics and professional boundaries

## Trigger Examples

The following queries should trigger this skill:

- "Analyze the latest treatment methods for lung cancer"
- "I want to understand diabetes prevention and control"
- "What are the recent research advances in Alzheimer's disease?"
- "Help me compile the latest hypertension treatment guidelines"
- "Search for the latest CAR-T cell therapy clinical trial results"
- "I need a professional report on depression treatment"

## Tool Usage Strategy

### Search Phase

```python
batch_web_search(
    queries=[
        {"query": "[Topic] latest research 2024", "num_results": 10},
        {"query": "[Topic] clinical guidelines", "num_results": 8},
        {"query": "[Topic] treatment options", "num_results": 8}
    ],
    display_text="Searching medical authoritative sources"
)
```

### Extraction Phase

```python
extract_content_from_websites(
    tasks=[
        {"url": "[Authoritative website URL]", "prompt": "Extract key medical information"},
        {"url": "[Journal article URL]", "prompt": "Extract research conclusions and data"}
    ],
    display_text="Extracting professional medical content"
)
```

### Report Generation

Directly output structured Markdown format reports, ensuring:
- Each information point has source citation
- Use tables to display comparative data
- Provide clear conclusions and recommendations
