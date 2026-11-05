# Medical Research Chart Generation Guide

## Mermaid Chart Code Reference

### CONSORT Flowchart

```mermaid
flowchart TD
    A[["Eligibility Assessed<br>n = XXX"]] --> B{Randomized}
    B --> C["Intervention Group<br>n = XXX"]
    B --> D["Control Group<br>n = XXX"]

    C --> E["Completed Intervention<br>n = XXX"]
    C --> F["Discontinued<br>n = XXX"]
    D --> G["Completed Intervention<br>n = XXX"]
    D --> H["Discontinued<br>n = XXX"]

    E --> I["Analyzed<br>n = XXX"]
    G --> I

    F --> J["Discontinuation reasons:<br>- Adverse events<br>- Lost to follow-up<br>- Other"]
    H --> J

    style A fill:#e1f5fe
    style I fill:#c8e6c9
    style J fill:#ffcdd2
```

### Study Design Diagram

```mermaid
flowchart LR
    subgraph Screening["Screening Phase"]
        S1[Inclusion Criteria] --> S2[Exclusion Criteria] --> S3[Informed Consent]
    end

    subgraph Randomization["Randomization"]
        R[Computer Randomization] --> RA[Intervention A]
        R --> RB[Control B]
    end

    subgraph Treatment["Treatment Phase"]
        TA[Intervention A<br>4 weeks] --> TAF[Follow-up 2 weeks]
        TB[Intervention B<br>4 weeks] --> TBF[Follow-up 2 weeks]
    end

    subgraph Followup["Follow-up Phase"]
        F1[Efficacy Assessment] --> F2[Safety Assessment] --> F3[Final Assessment]
    end

    S3 --> R
    RA --> TA
    RB --> TB
    TAF --> F1
    TBF --> F1
```

### Forest Plot Structure

```mermaid
graph LR
    subgraph ForestPlotElements
        A[Study Name] --> B[Effect Size]
        B --> C[95% CI]
        C --> D[Weight]
    end

    subgraph ReferenceLine
        E[Line of No Effect<br>OR=1/RR=1] --- F[Effect Region]
    end

    F --> G["Effect Region<br>Left: Beneficial/Harmful"]
    F --> H["Effect Region<br>Right: No Benefit/No Harm"]
```

### Patient Enrollment Flowchart

```mermaid
flowchart TD
    A["Potential Participants<br>n = XXX"] --> B["Did Not Meet Criteria<br>n = XXX"]
    A --> C["Met Criteria<br>n = XXX"]
    C --> D{Consented}
    D -->|Yes| E["Randomized<br>n = XXX"]
    D -->|No| F["Declined Participation<br>n = XXX"]

    E --> G["Intervention Group<br>n = XXX"]
    E --> H["Control Group<br>n = XXX"]

    G --> I["Completed Study<br>n = XXX"]
    G --> J["Discontinued<br>n = XXX"]
    H --> K["Completed Study<br>n = XXX"]
    H --> L["Discontinued<br>n = XXX"]

    I --> M["Analyzed<br>n = XXX"]
    K --> M

    style M fill:#c8e6c9
```

## Data Visualization Best Practices

### Chart Selection Guide

| Data Type | Relationship | Recommended Chart |
|-----------|-------------|-------------------|
| Categorical | Part-to-whole | Pie Chart, Donut Chart |
| Categorical | Discrete comparison | Bar Chart, Column Chart |
| Continuous | Distribution | Histogram, Box Plot |
| Continuous | Trend over time | Line Chart |
| Two variables | Correlation | Scatter Plot |
| Multivariate | Complex comparison | Heat Map |

### Chart Design Principles

1. **Clarity**
   - Titles should be concise and clear
   - Axis labels should be readable
   - Legend positioning should be appropriate

2. **Accuracy**
   - Proportions should be correct
   - Scales should be reasonable
   - Data should not be distorted

3. **Aesthetics**
   - Colors should be coordinated
   - White space should be appropriate
   - Fonts should be consistent

4. **Standards**
   - Meet journal requirements
   - Sufficient resolution
   - Uniform format

### Common Mistakes to Avoid

X Avoid:
- 3D effects that distort data
- Dual Y-axes causing confusion
- Truncated axes
- Excessive colors
- Missing necessary labels

X Avoid:
- 3D effects that distort data
- Dual Y-axes causing confusion
- Truncated axes
- Excessive colors
- Missing necessary labels

Check Mark Recommended:
- Simple 2D charts
- Single axis
- Complete axis ranges
- Limited color schemes
- Complete legends and labels
