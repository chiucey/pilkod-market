---
name: book-cataloging-assistant
description: Automated library cataloging skill based on CIP data. Use when users need to catalog books, recognize CIP data from copyright pages, generate CNMARC/USMARC format records, or validate cataloging data quality. Supports AI image recognition to automatically extract copyright page information and complete cataloging.
---

# Book Cataloging Assistant

## Skill Overview

This skill enables automated book cataloging by leveraging AI image recognition to extract Cataloging in Publication (CIP) data from book copyright pages. It then generates compliant CNMARC or USMARC cataloging records and validates data quality.

## Capabilities

### Core Functions

1. **CIP Data Recognition**
   - Upload/book capture book copyright page images
   - AI-powered text extraction from copyright pages
   - Intelligent parsing of CIP bibliographic data

2. **MARC Record Generation**
   - Generate CNMARC records for Chinese publications
   - Generate USMARC records for international publications
   - Support for various publication types

3. **Cataloging Quality Validation**
   - Verify MARC field completeness
   - Check data format compliance
   - Identify missing required fields
   - Validate indicator usage

### Supported Triggers

- "Help me catalog this book"
- "Recognize CIP data from copyright page"
- "Generate CNMARC record"
- "Generate USMARC record"
- "Validate cataloging data"
- "Book cataloging"
- "MARC format conversion"

## Workflow

### Step 1: Image Input

Accept book copyright page image through:
- Direct image upload (JPG, PNG, WEBP)
- Camera capture
- Image URL

### Step 2: AI Recognition

Process image through multi-modal AI to extract:
- Title (200$a / 245$a)
- Author(s) (200$f / 245$c)
- Publisher (210$c / 260$b)
- Publication year (210$d / 260$c)
- ISBN (010$a / 020$a)
- Classification number (690$a / 082$a)
- Copies/pages info

### Step 3: MARC Record Generation

Generate MARC record based on:
- Chinese publications → CNMARC format
- Foreign publications → USMARC format
- Institutional preference settings

### Step 4: Quality Validation

Perform automated validation checks:
- Required fields presence (Leader, 001, 005, 008, etc.)
- Field content format compliance
- Indicator accuracy
- Subfield usage correctness
- Data completeness score

## CNMARC Field Reference

### Essential Fields

| Field | Description | Indicators |
|-------|-------------|------------|
| 001 | Control Number | - |
| 005 | Transaction Date/Time | - |
| 008 | Fixed-Length Data Elements | - |
| 100 | General Processing Data | - |
| 101 | Language of Material | 0/1 |
| 102 | Source of Publication | - |
| 106 | Physical Description Form | - |
| 170 | Chinese Character Script | - |
| 200 | Title and Statement of Responsibility | 0/1/2 |
| 210 | Publication, Distribution, etc. | - |
| 215 | Physical Description | - |
| 225 | Series | 0/1/2 |
| 690 | Classification Numbers (Chinese) | - |
| 701 | Personal Name - Alternative Entry | 0/1 |
| 702 | Personal Name - Added Entry | 0/1 |
| 711 | Corporate Body - Alternative Entry | 0/1/2 |
| 712 | Corporate Body - Added Entry | 0/1/2 |
| 801 | Originating Source | - |
| 905 | Local Holdings Data | - |

### Field Indicators Guide

**200 Title Field Indicators:**
- Position 1: Title significance
  - 0 = No title added entry
  - 1 = Title is significant
- Position 2: Title type
  - 0 = No transliteration
  - 1 = Transliterated title

**210 Publication Field:**
- $a: Publication place
- $c: Publisher name
- $d: Publication year

**690 Classification Number:**
- $a: Classification number (e.g., "I247.57")
- $v: Volume/work number

### CNMARC Example

```
LEADER 00000nam  2200229   4500
001 0123456789
005 20240422000000.0
008 240422s2024    cn adn     b    101 0 chi d
100  ^a20240422d2024    em y0chiy0121    ea
101 0  ^achi
102  ^aCN
106  ^ar
170 0  ^bzh
200 1 ^aDream of the red chamber$eannotated edition$fCao Xueqin, Gao E$gannotated by Zhiyanzhai
210  ^aBeijing$cPeople's Literature Publishing House$d2024
215  ^a2 volumes (4, 654 pages) $d21cm
690  ^aI247.57$v3
690  ^aI242.47
701 0 $aCao Xueqin$f(Qing)
701 0 $aGao E$f(Qing)
702 0 $aZhiyanzhai
801  0$aCN$bU0865
905  ^aU0865$bModern Literature$I247.57
```

## USMARC Field Reference

### Essential Fields

| Field | Description | Indicators |
|-------|-------------|------------|
| 001 | Control Number | - |
| 005 | Transaction Date/Time | - |
| 008 | Fixed-Length Data Elements | - |
| 020 | ISBN | - |
| 050 | LC Classification | 0/1 |
| 082 | Dewey Classification | 0/1/2 |
| 100 | Main Entry - Personal Name | 1/2/3 |
| 245 | Title Statement | 0/1/2 |
| 250 | Edition | - |
| 260 | Publication, Distribution | - |
| 300 | Physical Description | - |
| 490 | Series Statement | 0/1 |
| 650 | Subject Added Entry | 0/4 |
| 700 | Added Entry - Personal Name | 1/2/3 |
| 710 | Added Entry - Corporate Name | 2 |
| 830 | Series Added Entry | - |

### USMARC Example

```
LEADER 00000cam  2200229   4500
001 .ocn123456789
005 20240422000000.0
008 240422s2024    nyu      b    001 0 eng d
020  ^a9780061120084
050 00^aPS3523.E833^bG47 2024
082 00^a813/.54$223
100 1^aFaulkner, William,$d1897-1962.
245 10$aThe great Gatsby /$cF. Scott Fitzgerald.
250  ^aScribner trade paperback edition.
260  ^aNew York :$bScribner,$c2024.
300  ^axii, 180 pages ;$c21 cm
650  0$aManhattan (New York, N.Y.)$vFiction.
650  0$aFirst editions$vFiction.
650  0$aRomance fiction.
700 1$aCallaghan, Morley,$eeditor.$4edt
830  0$aScribner classics edition.
```

## Quality Validation Rules

### Required Fields Check

**CNMARC Required:**
- [x] 001 - Control Number
- [x] 005 - Transaction Date
- [x] 008 - Fixed-Length Data
- [x] 100 - General Processing Data
- [x] 200 - Title (at minimum $a)
- [x] 210 - Publication info
- [x] 801 - Originating Source

**USMARC Required:**
- [x] 001 - Control Number
- [x] 005 - Transaction Date
- [x] 008 - Fixed-Length Data
- [x] 245 - Title and Statement of Responsibility

### Format Validation

1. **ISBN Format:**
   - ISBN-10: 10 digits (last can be X)
   - ISBN-13: 978/979 + 10 digits
   - Check digit validation

2. **Date Format:**
   - Format: YYYYMMDD or YYYYMMDDHHMMSS
   - Must be valid calendar date

3. **Indicator Validation:**
   - Each field has specific indicator requirements
   - Numeric indicators must be within valid range

4. **Subfield Delimiters:**
   - Must use $ (dollar sign) as delimiter
   - No empty subfields

### Quality Score Calculation

```
Quality Score = (Complete Fields / Required Fields) × 100%
```

| Score Range | Rating |
|-------------|--------|
| 90-100% | Excellent |
| 75-89% | Good |
| 60-74% | Acceptable |
| < 60% | Needs Improvement |

## Usage Examples

### Example 1: Basic Cataloging

**User Input:**
"Help me catalog this book, image is book_cover.jpg"

**Expected Output:**
- AI extracts CIP data from image
- Generates complete CNMARC record
- Shows quality validation results

### Example 2: MARC Format Conversion

**User Input:**
"Convert this CNMARC record to USMARC format"

**Input:**
```
LEADER 00000nam  2200229   4500
001 CIP2024001
005 20240422000000.0
008 240422s2024    cn adn     b    101 0 chi d
100  ^a20240422d2024    em y0chiy0121    ea
101 0  ^achi
200 1 ^aTo Live$fYu Hua
210  ^aBeijing$cWriter Publishing House$d2024
...
```

**Output:**
- Converted USMARC record with corresponding fields
- Field mapping documentation

### Example 3: Validation Only

**User Input:**
"Help me check the quality of this cataloging data"

**Output:**
- Validation checklist results
- Missing fields highlighted
- Format errors identified
- Quality score with recommendations

## Implementation Notes

### AI Recognition Pipeline

1. **Image Preprocessing**
   - Resolution optimization
   - Noise reduction
   - Orientation correction

2. **Text Recognition (OCR)**
   - Character recognition (multilingual support)
   - Number/digit recognition
   - Special character handling

3. **CIP Data Extraction**
   - Structured data parsing
   - Field mapping to MARC format
   - Confidence scoring

4. **Post-processing**
   - Data normalization
   - Duplicate detection
   - Format standardization

### Error Handling

| Error Type | Handling |
|------------|----------|
| Image too blurry | Request higher quality image |
| CIP data incomplete | Prompt user for missing fields |
| Format conversion error | Show specific field errors |
| Recognition failure | Allow manual entry mode |

## Best Practices

1. **Image Quality**
   - Minimum 300 DPI for text clarity
   - Ensure copyright page is fully visible
   - Avoid shadows and glare

2. **Data Verification**
   - Always verify AI-extracted data
   - Double-check ISBN check digit
   - Confirm classification with authority files

3. **Record Maintenance**
   - Keep original CIP data on file
   - Track modifications with 005 fields
   - Update records when reclassified

4. **Institution Adaptation**
   - Customize field requirements
   - Set local validation rules
   - Configure output formats
