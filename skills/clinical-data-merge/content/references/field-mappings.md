# Clinical Data Field Mapping Reference

## Patient Demographics Field Mapping

| Standard Field | Common Aliases |
|---------------|----------------|
| patient_id | patient_id, PATIENT_ID, patientid, PatientID, ID, medical_record_no, outpatient_no, inpatient_no |
| patient_name | patient_name, PatientName, name, Name, NAME |
| gender | gender, Gender, GENDER, sex, Sex, M/F |
| birth_date | birth_date, BirthDate, birthday, Birthday, dob, DOB |
| age | age, Age, AGE |
| phone | phone, Phone, telephone, Tel |
| id_card | id_card, IDCard, idnumber, ID_number |
| address | address, Address |

## Laboratory Test Field Mapping

| Standard Field | Common Aliases |
|---------------|----------------|
| test_date | test_date, TestDate, report_date, exam_date |
| test_item | test_item, TestItem, item, test_name |
| test_result | test_result, Result, result_value, value, result |
| unit | unit, Unit |
| reference_range | reference_range, RefRange, ref, normal_range |
| abnormal_flag | abnormal, AbnormalFlag, flag |

## Common Laboratory Test Items

- **CBC (Complete Blood Count)**: WBC (White Blood Cells), RBC (Red Blood Cells), HGB (Hemoglobin), PLT (Platelets)
- **Biochemistry**: ALT, AST, CRE (Creatinine), UREA (Blood Urea Nitrogen)
- **Blood Glucose**: GLU (Fasting Blood Glucose), HbA1c (Glycated Hemoglobin)
- **Lipid Panel**: TC (Total Cholesterol), TG (Triglycerides), HDL, LDL

## Diagnosis Record Field Mapping

| Standard Field | Common Aliases |
|---------------|----------------|
| diagnosis_code | diagnosis_code, ICD, ICD10, icd_code |
| diagnosis_name | diagnosis_name, Diagnosis, diagnosis |
| diagnosis_type | diagnosis_type, Type, type |
| diagnosis_date | diagnosis_date, Date |

## Date Format Standardization Rules

Supported input formats:
- `YYYY-MM-DD` (2024-01-15)
- `YYYY/MM/DD` (2024/01/15)
- `DD-MM-YYYY` (15-01-2024)
- `YYYYMMDD` (20240115)

Standardized output format: `YYYY-MM-DD`

## Gender Encoding Reference

| Standard Value | Supported Inputs |
|---------------|------------------|
| Male | M, m, Male, male, 1, TRUE |
| Female | F, f, Female, female, 0, FALSE |
