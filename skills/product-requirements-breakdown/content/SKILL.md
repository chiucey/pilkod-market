---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 3fdbfe8171d7404f460371508491b10a
    PropagateID: 3fdbfe8171d7404f460371508491b10a
    ReservedCode1: 3046022100e4a806263a7cf0ab1d8c406136f0ffd71c8dc57f1b7f5c93245c204a33f9a2b20221008dec9c465cae4e416fc3a1b630cc1e5716a77fb5ac0b23c0035214aef21bf810
    ReservedCode2: 3045022100a41d37c377347100bc29da9bbf74d836218fd775ce93825ba981e78897f0d79802203ebad586bf9492182a291e45784cd0b7c236e4b63f922a64db12f873e904c6cb
description: Used when users request product requirements analysis, feature breakdown, PRD (Product Requirements Document) generation, hardware specification analysis, or product specification development.
name: product-requirements-breakdown
---

# Product Requirements Breakdown Skill

Break down product requirement descriptions into core functional modules and hardware specifications, generating structured Product Requirements Documents (PRD).

## Core Workflow

### 1. Requirements Parsing

**Input**: User-provided requirement description (text, keywords, or scenario description)

**Processing**:
- Identify product type (consumer electronics, industrial equipment, IoT device, etc.)
- Extract key requirements
- Identify target users and use cases

### 2. Feature Breakdown

Break down features by the following dimensions:

| Dimension | Description |
|------------|-------------|
| Core Features | Primary product purpose, must implement |
| Supporting Features | Enhance user experience, secondary priority |
| Extended Features | Future scalability, not required for this release |
| Safety Features | Safety-related requirements |

**Output Format**:
```
## Feature Breakdown

### Core Features
1. [Feature Name] - [Brief Description]
   - Input: [Trigger Condition]
   - Output: [Expected Result]
   - Priority: P0

### Supporting Features
...
```

### 3. Hardware Specification Analysis

Based on product type, analyze and determine:

| Category | Specification Items |
|----------|---------------------|
| Processor | CPU model, computing requirements |
| Storage | RAM, ROM capacity |
| Communication | WiFi/BT/Cellular/Ethernet |
| Sensors | Required sensor types |
| Power | Battery capacity, power supply method |
| Physical | Dimensions, weight, environmental requirements |

**Output Format**:
```
## Hardware Specifications

### Core Hardware
| Component | Specification | Notes |
|-----------|---------------|-------|
| MCU | ARM Cortex-M4 | Main controller |
| RAM | 256KB+ | Support OTA |
| ... | ... | ... |

### Interface Definitions
| Interface | Type | Purpose |
|-----------|------|---------|
| USB-C | Power/Debug | 5V/3A |
| ... | ... | ... |
```

### 4. Generate PRD Document

Output complete Product Requirements Document including:

1. **Document Information**
   - Product Name
   - Document Version
   - Creation Date
   - Status (Draft/Review/Approved)

2. **Overview**
   - Product Background
   - Product Objectives
   - Target Users
   - Use Cases

3. **Functional Requirements**
   - Feature List
   - Feature Detailed Descriptions
   - User Stories (optional)

4. **Hardware Requirements**
   - Hardware Specification Table
   - Interface Definitions
   - Certification Requirements (if applicable)

5. **Non-Functional Requirements**
   - Performance Requirements
   - Reliability Requirements
   - Security Requirements
   - Compatibility Requirements

6. **Constraints**
   - Cost Constraints
   - Time Constraints
   - Technical Constraints

7. **Appendices**
   - Glossary
   - References

## Output Template

See `references/prd-template.md`

## Execution Example

**User Input**:
```
I want to create a smart water bottle that can display water temperature,
track water intake, and remind users to drink water
```

**Execution Flow**:
1. Parse as product type: IoT consumer electronics
2. Break down features: temperature detection, intake tracking, reminder notifications
3. Determine hardware: temperature sensor, accelerometer, Bluetooth module, Li-ion battery
4. Generate complete PRD document

## Quality Standards

- Feature breakdown clear with explicit priorities
- Hardware specifications concrete and procureable
- PRD structure complete with logical flow
- All technical terminology accurate
