---
name: pdf-detection-standard-extractor
description: Extract key information from detection standard method PDF files. Use when users upload detection standard PDFs and request extraction of standard name, parameters, sampling/preservation/pretreatment/preparation, formula symbols and units, and quality control measures.
---

# PDF Detection Standard Key Information Extraction Skill

## Trigger Conditions

When users upload a PDF file of detection standard methods and request extraction of the following key information:
- Standard name
- Parameter information
- Sample collection, preservation, pretreatment and preparation procedures
- Formula content, symbol meanings and corresponding units
- Quality control measures

## Core Principles

**Faithful to original text, absolutely prohibit deletion, omission, or fabrication**:
- Extract what exists in the original; do not add what is not in the original
- Preserve the original wording, terminology, and format
- Preserve all details and condition descriptions from the original
- For tables, formulas, flowcharts, etc., extract them verbatim
- If the original text is ambiguous or missing, clearly mark "not explicitly stated in original text"

## Extraction Workflow

### Step 1: PDF Content Reading

Use `extract_pdfs_full_content` tool to read the complete PDF content, save the original extraction results for subsequent processing.

### Step 2: Section-by-Section Extraction

Extract content from the original text **word by word, sentence by sentence**, without summarization or paraphrasing:

#### 2.1 Standard Name
- Complete standard number (e.g., GB/T xxx-xxxx)
- Full standard title
- Issue date, effective date (if available)

#### 2.2 Parameter Information
- Detection indicator names
- Method principle
- Scope of application
- Detection limit/quantification limit (if available)

#### 2.3 Sample Handling Procedures

**Sampling Section**:
- Sampling container/material requirements
- Sample volume requirements
- Sampling point/time/frequency specifications
- Detailed sampling method description

**Preservation Section**:
- Preservation conditions (temperature, light protection, etc.)
- Preservation container requirements
- Storage period/maximum storage time
- Specific preservative addition requirements

**Pretreatment Section**:
- Detailed pretreatment procedure steps
- Reagent names, specifications, concentrations
- Reagent volumes
- Operating conditions (temperature, time, pH, etc.)
- Container/equipment requirements
- Precautions/warning information

**Preparation Section**:
- Sample preparation method
- Dilution factor/concentration factor
- Volume for final solution
- Standard solution/working solution preparation method

#### 2.4 Formulas and Symbols

**Formula Content**:
- Complete mathematical formulas (preserve original symbols)
- Formula number (if available)

**Symbol Meanings and Units**:
| Symbol | Meaning | Unit |
|--------|---------|------|
| (original symbol) | (original definition) | (original unit) |

Extract every symbol definition from the original text line by line without omission.

#### 2.5 Quality Control Measures

- Blank sample requirements
- Spike recovery rate requirements
- Duplicate sample requirements
- Reference material/quality control sample requirements
- Calibration curve requirements (r value, number of points, etc.)
- Precision requirements
- Inter-laboratory comparison requirements (if available)
- Other quality control requirements

### Step 3: Structured Output

Organize extracted content in the following JSON structure:

```json
{
  "standard_name": {
    "standard_number": "Original standard number",
    "standard_title": "Full original standard title",
    "issue_date": "Issue date",
    "effective_date": "Effective date"
  },
  "parameters": {
    "detection_indicators": ["Detection indicator list"],
    "method_principle": "Original method principle description",
    "scope": "Original scope of application",
    "detection_limit": "Original detection limit",
    "quantification_limit": "Original quantification limit"
  },
  "sample_handling": {
    "sampling": {
      "container_requirement": "Original sampling container requirement",
      "sample_volume": "Original sample volume",
      "sampling_points_time": "Original sampling point/time specification",
      "sampling_method": "Original sampling method detailed description"
    },
    "preservation": {
      "conditions": "Original preservation conditions",
      "container_requirement": "Original preservation container requirement",
      "storage_period": "Original storage period",
      "preservatives": "Original preservative requirements"
    },
    "pretreatment": {
      "steps": ["Original pretreatment step 1", "Original pretreatment step 2", ...],
      "reagents": [{"name": "Reagent name", "specification": "Specification", "concentration": "Concentration", "volume": "Volume"}, ...],
      "conditions": "Original operating conditions",
      "equipment": "Original container/equipment requirements",
      "notes": "Original precautions"
    },
    "preparation": {
      "method": "Original preparation method",
      "dilution_factor": "Original dilution factor",
      "volume": "Original volume for final solution",
      "standard_solution_preparation": "Original standard solution preparation method"
    }
  },
  "formulas": {
    "formulas": [
      {
        "id": "Formula number (if available)",
        "content": "Complete formula from original",
        "symbols": [
          {"symbol": "Symbol", "meaning": "Original meaning", "unit": "Original unit"},
          ...
        ]
      }
    ]
  },
  "quality_control": {
    "blank_samples": "Original blank sample requirements",
    "spike_recovery": "Original spike recovery rate requirements",
    "duplicates": "Original duplicate sample requirements",
    "reference_materials": "Original reference material requirements",
    "calibration_curve": "Original calibration curve requirements",
    "precision": "Original precision requirements",
    "inter_lab_comparison": "Original inter-laboratory comparison requirements",
    "other_measures": "Other quality control requirements"
  },
  "extraction_notes": {
    "completeness": "Extraction completeness statement",
    "ambiguous_items": ["List of items with unclear original text"],
    "missing_items": ["List of missing items from original"]
  }
}
```

## Output Format Requirements

1. **JSON Output**: Main output in structured JSON format
2. **Original Text Citation**: Append `(Original: ...)` citations after key content
3. **Completeness Marking**: Clearly mark items not included in original as `"not explicitly stated in original text"`
4. **Table Format**: Use Markdown table format for formula symbols

## Verification Checklist

After completing extraction, verify each item:
- [ ] Standard number and name are complete and accurate
- [ ] All parameters are extracted verbatim
- [ ] Each step of sampling/preservation/pretreatment/preparation is complete
- [ ] Reagent information (name, concentration, volume) is complete
- [ ] All formulas are presented completely
- [ ] Each symbol's meaning and unit correspond accurately
- [ ] All quality control measures are listed
- [ ] No deletion, summarization, or paraphrasing occurred
- [ ] Items not stated in original are marked accordingly

## Important Notes

1. **Prohibit Summarization**: Even long paragraphs must be extracted sentence by sentence
2. **Preserve Original Structure**: Use the same numbering and hierarchy as in the original
3. **Preserve Terminology**: Use professional terms from the original without translation or replacement
4. **Preserve Special Formatting**: Superscripts, subscripts, Greek letters, etc. must be preserved
5. **Table Handling**: Preserve tables from the original, convert to Markdown table format if needed
