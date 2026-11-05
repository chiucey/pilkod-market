# Test Case Template Reference

## Complete Field Specifications

| Field Name | Data Type | Required | Description | Example |
|------------|-----------|----------|-------------|---------|
| Test Case ID | Text | Y | TC-Module-Type-Sequence | TC-SAF-CONF-001 |
| Test Project | Text | Y | Test content summary | Hazard Identification Completeness Verification |
| Test Reference Standard | Text | Y | Based standard and clauses | GB/T 28001-2011 4.3.1 |
| Standard Section | Text | Y | Corresponding requirement section | STD-GB28001-431-001 |
| Test Purpose | Text | Y | Verification objective | Verify organization has established complete hazard identification procedures |
| Test Sample | Text | Y | Sample specifications and quantity | Hazard identification procedure document v2.1 |
| Test Preconditions | Text | Y | Environment/Equipment/Preparation | 1. Hazard identification procedure issued<br>2. Hazard list established<br>3. Auditor trained in hazard identification |
| Test Steps | Multi-line Text | Y | Detailed operation process | See guidelines below |
| Test Pass Criteria | Text | Y | Acceptance criteria | Meet all conditions: <br>1. Procedure covers all activities<br>2. Hazard list contains >= N records<br>3. Major hazards identified and marked |
| Test Equipment | Text | N | Instruments and accuracy requirements | Document management system, Audit checklist |
| Remarks | Text | N | Special notes | Alternative methods/Safety precautions |

## Test Step Writing Guidelines

### Structure Requirements
1. Each step independent and verifiable
2. Step numbers sequential
3. Include expected results

### Format Example
```
Test Steps:
1. Collect hazard identification procedure document
   Expected result: Document signed and within validity period
2. Verify completeness of hazard list
   Expected result: List contains hazards from all departments/areas
3. Sample verify hazard identification methods
   Expected result: Methods comply with procedure requirements
4. Check major hazard markings
   Expected result: Major hazards clearly identified and marked
5. Review timeliness of hazard updates
   Expected result: Update records within last 12 months
```

## Test Case Classification

| Type | Description | ID Prefix |
|------|-------------|-----------|
| Compliance test | Verify compliance with standard requirements | TC-xxx-CONF |
| Performance test | Verify performance indicators | TC-xxx-PERF |
| Safety test | Verify safety functions | TC-xxx-SAFE |
| Durability test | Verify lifetime/reliability | TC-xxx-DURA |
| Environmental test | Verify environmental adaptability | TC-xxx-ENVI |
| EMC test | EMC related tests | TC-xxx-EMC |

## Test Precondition Templates

### Personnel Requirements
- Tester qualifications
- Special certification requirements

### Environmental Requirements
- Temperature/humidity range
- Electromagnetic environment
- Cleanliness requirements

### Equipment Requirements
- Measuring instruments and calibration status
- Fixtures and tooling
- Software tool versions

### Sample Requirements
- Sample status (prototype/pilot production/mass production)
- Sample quantity
- Sample pre-treatment requirements

### Document Requirements
- Procedure documents
- Record forms
- Reference samples

## Test Pass Criteria Writing Principles

1. **Quantitative preference**: Use specific values
   - Wrong: Temperature too high
   - Correct: Temperature <= 85 deg C

2. **Complete and unambiguous**:
   - Wrong: Performance good
   - Correct: Response time <= 100ms, error <= +/-2%

3. **Repeatably verifiable**:
   - Clear test conditions
   - Clear acceptance thresholds
   - Clear acceptance logic (AND/OR)

## Typical Test Case Examples

### Example 1: Document Review Type

```
Test Case ID: TC-SAF-CONF-001
Test Project: Hazard Identification Procedure Completeness Verification
Test Reference Standard: GB/T 28001-2011 4.3.1
Standard Section: STD-GB28001-431-001
Test Purpose: Verify completeness and compliance of hazard identification procedure
Test Sample: Hazard identification procedure document (HZ-GL-001) and hazard list
Test Preconditions:
  1. Hazard identification procedure issued (document number: HZ-GL-001)
  2. Hazard list established (contains at least 50 records)
  3. Test personnel have hazard identification audit qualifications
Test Steps:
  1. Obtain hazard identification procedure document, confirm document version and approval status
  2. Verify procedure content covers standard requirements (scope, methods, update requirements)
  3. Obtain latest hazard list, count total records
  4. Sample verify 5 departments for hazard identification coverage
  5. Verify major hazard identification and assessment records
  6. Check hazard list update dates and update records
Test Pass Criteria:
  All conditions below must be met for PASS:
  1. Procedure document version >= V1.0, complete approval records
  2. Procedure contains three core elements: scope definition, identification methods, update requirements
  3. Hazard list total records >= 50
  4. 100% coverage of hazard identification across sampled departments
  5. Major hazards have clear identification and risk assessment
  6. Update records within last 12 months
Test Equipment: Document management system, Audit checklist
Remarks: Sample ratio can be adjusted based on actual situation
```

### Example 2: Functional Test Type

```
Test Case ID: TC-PERF-001
Test Project: System Response Time Performance Test
Test Reference Standard: XXX Product Technical Specification 5.3.2
Standard Section: STD-XXX-532-001
Test Purpose: Verify system response time meets technical requirements under normal load
Test Sample: System under test hardware platform + software version V2.1.0 (2 sets)
Test Preconditions:
  1. Test environment built (temperature 25 deg C +/- 2 deg C)
  2. Test equipment calibration valid
  3. System completed power-on initialization
  4. Test scripts deployed
Test Steps:
  1. Start system, confirm system status normal
  2. Execute standard load script (100 concurrent requests)
  3. Record system response time data (sample size >= 100)
  4. Calculate average response time and maximum response time
  5. Repeat steps 2-4, total 3 test rounds
Test Pass Criteria:
  1. Average response time <= 100ms
  2. Maximum response time <= 200ms
  3. 3-round test result consistency <= 10%
Test Equipment: Load tester (Keysight N4X), Oscilloscope, Thermometer
Remarks: If test fails, allow 1 retest
```
