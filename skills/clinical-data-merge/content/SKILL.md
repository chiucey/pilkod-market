---
name: clinical-data-merge
description: Merge and consolidate clinical data. Use when users want to merge clinical data, consolidate patient records, combine lab results, process diagnostic reports, unify multi-source clinical information, or deduplicate patient data.
---

# Clinical Data Merge Skill

## Overview

This skill helps users organize, merge, and standardize clinical data from different sources, ensuring data quality and consistency.

## Supported Data Types

- **Patient Demographics**: ID, name, gender, age, date of birth, etc.
- **Laboratory Results**: CBC, biochemistry, blood glucose, lipid panel, etc.
- **Diagnosis Records**: ICD codes, primary diagnosis, secondary diagnosis
- **Treatment Records**: medications, surgeries, nursing notes
- **Imaging Reports**: X-ray, CT, MRI, ultrasound, etc.
- **Clinical Notes**: admission notes, discharge summaries, progress notes

## Workflow

### Step 1: Data Collection and Analysis

Collect raw clinical data files provided by the user:

- **Supported Formats**: CSV, Excel (.xlsx/.xls), JSON, XML, TSV
- **Multi-file Support**: Process multiple files simultaneously
- **Data Preview**: Auto-analyze data structure, identify field types

### Step 2: Data Cleaning and Standardization

Standardize collected data:

1. **Field Mapping**: Unify synonymous fields from different sources (e.g., "Patient Name", "Name", "name" → "patient_name")
2. **Format Uniformity**:
   - Standardize date formats to YYYY-MM-DD
   - Unify gender encoding (Male/Female, M/F, 1/0)
   - Standardize numeric units
3. **Missing Value Handling**:
   - Mark missing data
   - Optional: Fill with defaults or flags
4. **Outlier Detection**: Identify clearly unreasonable data values

### Step 3: Data Merging

Execute multi-source data merge operations:

1. **Primary Key Identification**: Identify unique patient identifiers (e.g., patient_id, ID card number)
2. **Merge Strategies**:
   - One-to-one merge: Direct merge for matching patient records
   - One-to-many merge: Merge multiple visits/tests for the same patient
   - Many-to-one merge: Summarize multiple records into single consolidated record
3. **Conflict Resolution**: Strategies for handling multiple values in the same field

### Step 4: Deduplication and Validation

1. **Duplicate Detection**: Identify complete and partial duplicates
2. **Deduplication Rules**: Dedupe based on primary key or key field combinations
3. **Cross-validation**: Check data logic consistency

### Step 5: Output Generation

Generate final organized data:

- **Output Formats**: CSV, Excel, JSON
- **Report Generation**: Output data quality report (missing rate, outlier statistics, etc.)
- **Optional**: Generate data dictionary explaining field meanings

## Usage Examples

### Example 1: Merge Multiple CSV Files

```
User: Merge these 3 clinical data CSV files, deduplicate by patient_id, output to merged_data.csv
```

### Example 2: Standardize Date Formats

```
User: Standardize all date formats in these Excel files to YYYY-MM-DD
```

### Example 3: Integrate Multi-source Patient Data

```
User: I have outpatient and inpatient data, merge by patient ID, generate complete patient profiles
```

## Notes

1. **Privacy Protection**: Handle with de-identification requirements, do not persist raw sensitive data
2. **Data Backup**: Recommend users keep original data copies
3. **Field Confirmation**: Confirm field mapping before complex merges
4. **Error Feedback**: Promptly alert users when obvious data issues are found

## Quick Commands

| Operation | Command/Trigger |
|-----------|----------------|
| Merge Data | `merge` + file paths |
| Clean Data | `clean` + data description |
| Deduplicate | `dedup` + primary key field |
| Standardize | `standardize` + target format |
| Generate Report | `report` + output options |
