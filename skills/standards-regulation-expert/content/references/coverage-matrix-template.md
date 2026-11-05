# Requirements-Test Coverage Matrix Template

## Matrix Structure Description

The Requirements-Test Coverage Matrix bridges requirements management and test cases, ensuring every requirement has corresponding test verification.

### Core Fields

| Field Name | Data Type | Required | Description |
|------------|-----------|----------|-------------|
| Requirement ID | Text | Y | Unique identifier linked to requirements management table |
| Standard Number | Text | Y | Original standard number |
| Standard Section | Text | Y | Section number and title |
| Requirement Category | Dropdown | Y | Mandatory/Technical recommendation/Information reference |
| Requirement Description | Text | Y | Core content of requirement |
| Related Tests | Many-to-many | Y | List of test case IDs covering the requirement |
| Test Method | Dropdown | Y | Document review/On-site inspection/Test verification/Process monitoring |
| Verification Method | Dropdown | Y | Static verification/Dynamic test/Hybrid verification |
| Mandatory/Optional | Dropdown | Y | Whether test is mandatory |
| Coverage Status | Dropdown | Y | Covered/Partially covered/Not covered/Not applicable |
| Others | Text | N | Remarks, risks, improvement items |

## Coverage Status Definitions

| Status | Definition | Color Code |
|--------|------------|------------|
| Covered | Test cases fully cover all elements of requirement | Green |
| Partially covered | Test cases cover partial requirement elements, supplement needed | Yellow |
| Not covered | Test cases not yet designed or developed | Red |
| Not applicable | Requirement not applicable to current product or project | Gray |

## Matrix Filling Guidelines

### Requirement ID Linking
- Must match requirement ID in requirements management table
- Supports many-to-many relationships (one requirement -> multiple tests, one test -> multiple requirements)

### Related Tests Entry
- Enter test case numbers, separate multiple tests with semicolons
- Format: TC-XXX-001; TC-XXX-002

### Test Method Selection
| Method | Description |
|--------|-------------|
| Document review | Verification through reviewing documents and records |
| On-site inspection | Verification through field inspection |
| Test verification | Verification through executing tests and obtaining data |
| Process monitoring | Verification through monitoring process operation |

### Verification Method Selection
| Method | Description |
|--------|-------------|
| Static verification | Verification without running product (e.g., document review) |
| Dynamic test | Tests while running product (e.g., functional test) |
| Hybrid verification | Static + dynamic combined |

## Matrix Example

| Requirement ID | Standard Number | Standard Section | Requirement Category | Requirement Description | Related Tests | Test Method | Verification Method | Mandatory/Optional | Coverage Status | Others |
|----------------|-----------------|-----------------|---------------------|------------------------|---------------|-------------|--------------------|-------------------|----------------|--------|
| STD-GB28001-431-001 | GB/T 28001-2011 | 4.3.1 | Mandatory requirement | Organization shall establish hazard identification procedures | TC-SAF-CONF-001; TC-SAF-CONF-002 | Document review;On-site inspection | Static verification | Mandatory | Covered | Related to ISO 45001 |
| STD-GB28001-432-001 | GB/T 28001-2011 | 4.3.2 | Mandatory requirement | Organization shall conduct risk assessment | TC-SAF-CONF-003 | Document review | Static verification | Mandatory | Covered | - |

## Quality Check Points

1. **Completeness Check**
   - Every requirement has corresponding test
   - Every mandatory requirement has mandatory test

2. **Consistency Check**
   - Standards referenced by test cases match requirements
   - Acceptance criteria match requirement descriptions

3. **Traceability Check**
   - Traceable from requirements to tests
   - Traceable from tests to requirements

## Matrix Maintenance

### Version Control
- Record change log for each update
- Maintain version history traceability

### Change Triggers
- Standard update/revision
- Requirement change
- Test case added/modified/deleted
- Project scope change

### Review Process
1. Self-check after matrix update
2. Team cross review
3. Expert confirmation
4. Release new version
