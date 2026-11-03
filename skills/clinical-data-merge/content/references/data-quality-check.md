# Clinical Data Quality Check Standards

## Data Completeness Check

### Required Field Check

The following fields typically should not be empty:
- patient_id (unique patient identifier)
- examination date/time
- test results or diagnosis information

### Missing Value Handling Strategies

| Strategy | Description | Applicable Scenario |
|----------|-------------|---------------------|
| Keep Original | Keep empty or mark with NA/null | Requires manual review later |
| Delete Records | Remove rows with missing values | Missing rate <5% and non-critical fields |
| Fill Default | Use mean/mode/median | Numeric fields |
| Mark Source | Add field to mark data source/quality | Need to trace original data |

## Data Consistency Check

### Numeric Range Reasonableness

| Indicator | Reasonable Range | Abnormal Threshold |
|-----------|-------------------|-------------------|
| Age | 0-120 years | <0 or >120 |
| Temperature | 35.0-42.0°C | <35 or >42 |
| Blood Pressure (Systolic) | 60-250 mmHg | <60 or >250 |
| Blood Pressure (Diastolic) | 40-150 mmHg | <40 or >150 |
| Heart Rate | 30-200 bpm | <30 or >200 |
| Hemoglobin (HGB) | 30-200 g/L | <30 or >200 |
| White Blood Cells (WBC) | 1-50 ×10⁹/L | <1 or >50 |
| Platelets (PLT) | 10-800 ×10⁹/L | <10 or >800 |

### Date Logic Check

- Birth date should not be later than examination date
- Examination date should not be earlier than birth date
- Multiple records from the same visit should have consistent dates
- Discharge date should not be earlier than admission date

### Inter-field Logic Check

- Females should not have prostate-related diagnoses
- Males should not have cervical-related diagnoses
- Children (<14 years) generally should not have adult disease diagnoses

## Data Duplicate Check

### Complete Duplicates

Records where all field values are completely identical

### Partial Duplicates (Based on Primary Key)

Determine duplicates based on patient_id + examination date combination

### Approximate Duplicates

Records with matching key fields but subtle differences
- Similar names but different IDs (requires manual confirmation)
- Duplicate records with dates differing by 1 day

## Data Standardization Check

### Encoding Consistency

- ICD code versions unified (ICD-10 as primary)
- Test items use standard codes (e.g., LOINC)
- Medications use standard names (e.g., generic names)

### Unit Standardization

| Indicator | Standard Unit |
|-----------|--------------|
| Blood Glucose | mmol/L |
| Hemoglobin | g/L |
| Temperature | °C |
| Blood Pressure | mmHg |

## Output Report Template

### Data Quality Report Structure

```
# Data Quality Report

## Basic Information
- Number of files: X
- Total records: X
- Processing time: XXXX

## Completeness Statistics
- Overall completeness rate: XX%
- Missing rate by field

## Consistency Check
- Number of outliers
- Number of logic conflicts

## Duplicate Records
- Complete duplicates: X
- Partial duplicates: X
- Deduplicated: X

## Standardization Results
- Date format unification rate
- Gender encoding unification rate
- Field mapping completion rate
```
