# PDF Detection Standard Extraction Reference Guide

## Extraction Examples

### Example 1: Standard Name Extraction

**Original Text**:
> GB/T 5750.4-2023
> Standard Examination Methods for Drinking Water
> Part 4: Sensory Characteristics and Physical Indicators
> Issued 2023-03-17, Effective 2023-10-01

**Correct Extraction**:
```json
{
  "standard_number": "GB/T 5750.4-2023",
  "standard_title": "Standard Examination Methods for Drinking Water Part 4: Sensory Characteristics and Physical Indicators",
  "issue_date": "2023-03-17",
  "effective_date": "2023-10-01"
}
```

### Example 2: Formula Extraction

**Original Text**:
> Mass concentration calculation formula:
> ρ = (A - Ab) × V × D / (Vs × K)
> Where:
> ρ — Mass concentration of the analyte, unit: milligrams per liter (mg/L);
> A — Peak area (or peak height) of the sample;
> Ab — Peak area (or peak height) of the blank sample;
> V — Extract volume, unit: milliliters (mL);
> D — Dilution factor;
> Vs — Sampling volume, unit: liters (L);
> K — Conversion factor.

**Correct Extraction**:
```json
{
  "formulas": [
    {
      "id": null,
      "content": "ρ = (A - Ab) × V × D / (Vs × K)",
      "symbols": [
        {"symbol": "ρ", "meaning": "Mass concentration of the analyte", "unit": "mg/L"},
        {"symbol": "A", "meaning": "Peak area (or peak height) of the sample", "unit": "-"},
        {"symbol": "Ab", "meaning": "Peak area (or peak height) of the blank sample", "unit": "-"},
        {"symbol": "V", "meaning": "Extract volume", "unit": "mL"},
        {"symbol": "D", "meaning": "Dilution factor", "unit": "-"},
        {"symbol": "Vs", "meaning": "Sampling volume", "unit": "L"},
        {"symbol": "K", "meaning": "Conversion factor", "unit": "-"}
      ]
    }
  ]
}
```

### Example 3: Sample Pretreatment Steps Extraction

**Original Text**:
> 4.2.1 Sampling
> Collect samples using hard glass bottles or polyethylene plastic bottles. Rinse the container 2~3 times with sample water before collection. Fill the bottle completely with sample water, leaving no air bubbles. If collecting deep water layer samples, use a dedicated water sampler.
>
> 4.2.2 Preservation
> Preserve collected samples at 4°C and analyze within 24 hours. If analysis cannot be performed promptly, add 0.5 mL concentrated sulfuric acid per liter of sample (pH<2), cap tightly, and shake well.
>
> 4.2.3 Pretreatment
> Transfer 100 mL of sample water to a separatory funnel, add 2 mL dichloromethane, shake for 3 minutes, allow to settle, and collect the organic phase. Repeat extraction 3 times, combine organic phases, dry over anhydrous sodium sulfate, and use for chromatographic analysis.

**Correct Extraction**:
```json
{
  "sample_handling": {
    "sampling": {
      "container_requirement": "Hard glass bottles or polyethylene plastic bottles",
      "sample_volume": "Not explicitly stated in original",
      "sampling_points_time": "Not explicitly stated in original",
      "sampling_method": "Rinse the container 2~3 times with sample water before collection. Fill the bottle completely with sample water, leaving no air bubbles. If collecting deep water layer samples, use a dedicated water sampler."
    },
    "preservation": {
      "conditions": "Preserve at 4°C",
      "container_requirement": "Hard glass bottles or polyethylene plastic bottles",
      "storage_period": "Analyze within 24 hours",
      "preservatives": "Add 0.5 mL concentrated sulfuric acid per liter of sample (pH<2)"
    },
    "pretreatment": {
      "steps": [
        "Transfer 100 mL of sample water to a separatory funnel",
        "Add 2 mL dichloromethane",
        "Shake for 3 minutes",
        "Allow to settle and collect the organic phase",
        "Repeat extraction 3 times",
        "Combine organic phases",
        "Dry over anhydrous sodium sulfate, use for chromatographic analysis"
      ],
      "reagents": [
        {"name": "Dichloromethane", "specification": "-", "concentration": "-", "volume": "2 mL"},
        {"name": "Anhydrous sodium sulfate", "specification": "-", "concentration": "-", "volume": "Sufficient amount"}
      ],
      "conditions": "Shake for 3 minutes",
      "equipment": "Separatory funnel",
      "notes": "Not explicitly stated in original"
    }
  }
}
```

## Common Problem Handling

### Q1: Ellipsis or Incomplete Content in Original

**Handling**: Preserve the original ellipsis form and clearly mark content as incomplete.

**Example**:
```json
{
  "note": "Original content is incomplete: parameter requirement states 'sample volume no less than...', subsequent content is truncated"
}
```

### Q2: Same Term with Slightly Different Expressions

**Handling**: Use the first occurrence as reference, note "see section x.x" in parentheses.

### Q3: Table Content Extraction

**Handling**: Convert tables to Markdown table format, preserving all row and column information.

**Original Table**:
| Parameter | Requirement |
|-----------|-------------|
| Sample Volume | 500 mL |
| Storage Temperature | 4°C |

**Extraction Result**:
| Parameter | Requirement |
|-----------|-------------|
| Sample Volume | 500 mL |
| Storage Temperature | 4°C |

### Q4: Quality Control Measures Scattered Across Multiple Sections

**Handling**: Summarize content from various sections while maintaining original citations and noting source sections.

### Q5: Formula Number Missing or Duplicate

**Handling**: If no number exists, leave the number field blank; if numbers are duplicated, keep the original numbering and note the duplication.

## Prohibited Actions Checklist

| ❌ Prohibited | ✅ Correct Practice |
|---------------|---------------------|
| Converting "room temperature storage" to "ambient temperature storage" | Keep original "room temperature storage" |
| Converting "shake 2-3 min" to "shake for several minutes" | Keep original "shake 2-3 min" |
| Merging 3 steps into 1 step | List all steps individually |
| Omitting limiting conditions like "if necessary", "as appropriate" | Preserve all conditions verbatim |
| Replacing original text with your own interpretation | Copy original text exactly |
| Adding information not mentioned in original | Do not add if not in original |

## Extraction Completeness Self-Check

After completing extraction, answer the following:

1. **Standard Name**: Does it include the complete standard number and title?
2. **Parameter Information**: Are detection limit, quantification limit, and scope complete?
3. **Sampling**: Are container, sample volume, and sampling method all included?
4. **Preservation**: Are temperature, time, and preservative clearly specified?
5. **Pretreatment**: Is every step and every reagent complete?
6. **Formulas**: Does each symbol correspond correctly to its meaning and unit?
7. **Quality Control**: Are blank, recovery, duplicate, and reference material requirements complete?
8. **No Deletions**: Have multi-sentence items been merged into one sentence? Has any content been deleted?
9. **No Fabrication**: Has any information not in the original been added?
