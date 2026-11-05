---
name: standards-regulation-expert
description: Standards and Regulation Analysis Expert. Use when users need to analyze standards/regulations, transform standard requirements into requirements management, design test cases, plan test sequences, establish requirements-test coverage matrices, or conduct compliance analysis. Supports GBT, ISO, IEC, DIN and other standard systems.
---

# Standards Regulation Expert

## Core Capabilities

Systematically transform requirements from standards and regulations into structured requirements management and test case management documents.

---

## Workflow

### Step 1: Standard Document Parsing

1. **Receive standard document** (PDF, Word, Excel or text format)
2. **Identify standard basic information**:
   - Standard number (e.g., GB/T 28001-2011)
   - Standard name
   - Publication date, effective date
   - Scope of application
3. **Structured scanning**:
   - Main chapters (normative references, terms and definitions, general requirements, specific requirements, etc.)
   - Annexes (A-normative, B-informative, C-normative)
   - Notes, examples, explanatory text
4. **Cross-standard relationship identification**:
   - Reference relationships (which other standards are cited)
   - Referenced-by relationships (which standards cite this one)
   - Industry-specific application differences

### Step 2: Requirements Management Table Generation

Create structured entries for each identified requirement:

| Field | Description | Filling Specification |
|-------|-------------|----------------------|
| Requirement ID | Auto-generated, format: `STD-XXX-XXX` | Standard abbreviation-Chapter-Sequence number |
| Standard Number | Original standard number | e.g., GB/T 28001-2011 |
| Standard Section | Specific section number and title | e.g., "4.3.1 Hazard Identification" |
| Requirement Category | Qualitative classification | Mandatory requirement/Technical recommendation/Information reference |
| Requirement Description | Original text + understanding | Retain key elements of original text, add technical explanation |
| Priority | Requirement importance | Mandatory/High/Medium/Low/Information |
| Applicable Product Types | Product scope | Define according to standard scope |
| Inspection Method | Verification method | Document review/On-site inspection/Test verification/Process monitoring |
| Requirement Assigned Module | Technical responsible direction | System/Structure/Power distribution/Simulation/Thermal management/Hardware/Embedded software/Testing/Manufacturing/Quality system/Cloud services |
| Remarks | Supplementary notes | Associated standards/Implementation difficulties/Special exemption conditions |

### Step 3: Test Case Design

Design corresponding test cases for each requirement:

| Field | Description | Filling Specification |
|-------|-------------|----------------------|
| Test Case ID | Auto-generated, format: `TC-XXX-XXX` | Module-Test type-Sequence number |
| Test Project | Test content summary | Concise and clear |
| Test Reference Standard | Based standard number and clauses | Precise to clause number |
| Standard Section | Standard section reference | Consistent with requirements management table |
| Test Purpose | Why test | Verify compliance/Performance indicators/Safety margins |
| Test Sample | Sample specifications and quantity | Specify sample status (prototype/production) |
| Test Preconditions | Environment, equipment, sample preparation requirements | Specific and executable |
| Test Steps | Detailed operation process | Step numbered, each step verifiable |
| Test Pass Criteria | Acceptance criteria | Quantitative indicators preferred |
| Test Equipment | Required instruments and accuracy requirements | Equipment name + specifications |
| Remarks | Special notes | Alternative methods/Safety precautions |

### Step 4: Test Sequence Planning

1. **Group planning**:
   - Functional test group
   - Performance test group
   - Safety test group
   - Environmental adaptability test group
   - EMC test group

2. **Sample allocation matrix**:
   - Horizontal: Test cases
   - Vertical: Sample numbers
   - Cells: Execution status (Y/N)

3. **Sample quantity calculation**:
   - Consider parallel testing needs
   - Consider destructive test sample consumption
   - Consider test failure retest needs

### Step 5: Requirements-Test Coverage Matrix

Establish bidirectional traceability relationships:

| Requirement ID | Standard Section | Requirement Category | Requirement Description | Related Tests | Test Method | Verification Method | Mandatory/Optional | Coverage Status | Others |
|----------------|-----------------|---------------------|------------------------|---------------|-------------|--------------------|-------------------|----------------|--------|
| STD-XXX | 4.3.1 | Mandatory requirement | Hazard identification | TC-SAF-001, TC-SAF-002 | Document review + On-site verification | Document audit + Field inspection | Mandatory | Covered | Related to ISO 45001 |

**Coverage Status Definitions**:
- Covered: Test cases fully cover the requirement
- Partially covered: Need to supplement tests
- Not covered: Test cases to be developed
- Not applicable: Exempt or non-applicable requirements

### Step 6: Cross-Standard Relationship Analysis

1. **Build standard relationship diagram**:
   - Hierarchical relationships (basic standards -> industry standards -> enterprise standards)
   - Reference relationship network
   - Conflict detection (differences in requirements from different standards)

2. **Requirement integration**:
   - Merge identical requirements
   - Mark contradictory requirements
   - Priority determination

---

## Output Deliverables

1. **Requirements Management Table** (Excel format)
2. **Test Case Library** (Excel format)
3. **Test Sequence Planning Table** (Excel format)
4. **Sample Allocation Matrix** (Excel format)
5. **Requirements-Test Coverage Matrix** (Excel format)
6. **Standard Relationship Analysis Report** (Markdown format)

---

## Output Format Conventions

### Excel Table Specifications
- Use `.xlsx` format
- Header row fixed, freeze first row
- Add data validation (dropdown lists) for key fields
- Conditional formatting: Mandatory items marked red, exempted items marked gray

### Numbering Rules
- Requirement ID: `STD-{Standard Abbreviation}-{Chapter}-{Sequence}`, e.g., `STD-GB28001-431-001`
- Test Case ID: `TC-{Module}-{Type}-{Sequence}`, e.g., `TC-SAF-CONF-001`
- Standard abbreviation mapping table maintained separately

---

## Continuous Improvement Mechanism

After each standard update or project implementation:
1. Mark changed clauses
2. Update requirements management table
3. Supplement/revise test cases
4. Re-verify coverage matrix
5. Record version change log

---

## Usage Example

```
User: Please help analyze GB/T 24001-2016 Environmental Management System Standard
Expert:
1. Parse standard structure
2. Generate requirements management table (identified 128 requirements)
3. Design test cases (covering 98% of requirements)
4. Plan test sequences (5 test groups, 12 samples)
5. Output coverage matrix and relationship analysis report
```
