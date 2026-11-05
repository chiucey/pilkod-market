# Requirements Management Table Template

## Complete Field Specifications

| Field Name | Data Type | Required | Description | Example |
|------------|-----------|----------|-------------|---------|
| Requirement ID | Text | Y | Standard abbreviation-Section-Sequence | STD-GB28001-431-001 |
| Standard Number | Text | Y | Original standard number | GB/T 28001-2011 |
| Standard Section | Text | Y | Section number + title | 4.3.1 Hazard Identification |
| Requirement Category | Dropdown | Y | Requirement nature classification | Mandatory/Technical recommendation/Information reference |
| Requirement Description | Text | Y | Original text + technical understanding | See standard original text |
| Priority | Dropdown | Y | Importance level | Mandatory/High/Medium/Low/Information |
| Applicable Product Types | Multi-select | Y | Applicable product scope | Industrial controller/Motor drive/Complete equipment |
| Inspection Method | Dropdown | Y | Verification method | Document review/On-site inspection/Test verification/Process monitoring |
| Requirement Assigned Module | Multi-select | Y | Technical responsible direction | System/Structure/Power distribution/Simulation/Thermal management/Hardware/Embedded software/Testing/Manufacturing/Quality system/Cloud services |
| Remarks | Text | N | Supplementary notes | Associated standards/Implementation difficulties/Exemption conditions |

## Requirement Category Definitions

| Category | Description | Determination Basis |
|----------|-------------|--------------------|
| Mandatory requirement | Legal or contractual requirements that must be met | "Shall", "Must" expressions in standards |
| Technical recommendation | Recommended but not mandatory | "Should", "Recommended" expressions in standards |
| Information reference | Informational content for reference only | "May", "Reference" expressions in standards |

## Priority Definitions

| Priority | Description | Handling Requirement |
|----------|-------------|----------------------|
| Mandatory | Must pass for acceptance | Prioritize test resource allocation |
| High | Important but negotiable | Complete before project milestone |
| Medium | Regular requirement | Progress as planned |
| Low | Optimization item | Complete when resources allow |
| Information | Reference information | Optional execution |

## Requirement Description Writing Guidelines

1. **Retain original text elements**: Quote key phrases from standard original text
2. **Add technical understanding**: Explain requirement meaning in plain language
3. **Clarify scope boundaries**: Explain applicable conditions and exceptions
4. **Measurability**: Quantify indicators where possible (values, ratios, time, etc.)

### Example

```
Requirement ID: STD-GB28001-431-001
Standard Number: GB/T 28001-2011
Standard Section: 4.3.1 Hazard Identification
Requirement Category: Mandatory requirement
Requirement Description:
  Original elements: The organization shall establish and maintain procedures for continual hazard identification...
  Technical understanding: Need to establish hazard register, covering physical, chemical, biological, mechanical, human engineering hazards
  Scope boundaries: Applies to all company's activities, products and services
  Measurability: Hazard identification coverage rate 100%
```

## Inspection Method Definitions

| Method | Applicable Scenario | Outputs |
|--------|-------------------|---------|
| Document review | System documents, management records | Audit records, checklists |
| On-site inspection | Physical status, operational practices | Inspection reports, nonconformities |
| Test verification | Technical indicators, performance parameters | Test reports, data records |
| Process monitoring | Process control, operational status | Monitoring records, trend analysis |
