---
name: tech-roadmap-generator
description: Tech Roadmap Generator. Generate professional technical roadmaps for grant applications (NSFC/NSSFC) and research papers. Choose from 20 mature frameworks and automatically create draw.io-compatible XML technical roadmaps based on your research content. Triggers: technical roadmap, research framework, methodology diagram.
---

# Tech Roadmap Generator

## Overview

Provides professional, editable technical roadmap generation services for grant applications (NSFC/NSSFC) and research paper writing.

## Workflow

### Step 1: Framework Selection

Users provide basic research information (research direction, methodology type, discipline field) and choose from 20 mature frameworks:

#### NSFC Common Frameworks (10)

| ID | Framework Name | Applicable Disciplines | Core Structure |
|----|----------------|----------------------|---------------|
| NSFC-01 | Basic Research | Math, Physics, Chemistry, Biology | Problem → Theory → Experiment → Verification |
| NSFC-02 | Applied Basic | Engineering, Materials, IT | Demand → Mechanism → Method → Application |
| NSFC-03 | Technical Breakthrough | Information, Automation | Goal → Technology → Implementation → Testing |
| NSFC-04 | Interdisciplinary Innovation | Biomedical, Nano | Multi-discipline → Intersection → Integration → Innovation |
| NSFC-05 | Equipment R&D | Mechanical, Aerospace | Requirement Analysis → Design → Manufacturing → Testing |
| NSFC-06 | Method Innovation | Chemistry, Biology | Traditional Method → Innovation Point → New Method → Verification |
| NSFC-07 | Data-Driven | Computer Science, Big Data | Data → Features → Model → Application |
| NSFC-08 | Theoretical Modeling | Physics, Mathematics | Physical Model → Mathematical Derivation → Numerical Simulation |
| NSFC-09 | System Integration | Electronics, Environment | Module → System → Integration → Optimization |
| NSFC-10 | Validation & Evaluation | Medicine, Pharmacy | Hypothesis → Verification → Evaluation → Conclusion |

#### NSSFC Common Frameworks (10)

| ID | Framework Name | Applicable Disciplines | Core Structure |
|----|----------------|----------------------|---------------|
| NSSFC-01 | Empirical Research | Economics, Management | Theory → Hypothesis → Data → Verification |
| NSSFC-02 | Case Study | Law, Education | Case → Analysis → Comparison → Conclusion |
| NSSFC-03 | Historical Research | History, Philosophy | Literature → Historical Sources → Analysis → Interpretation |
| NSSFC-04 | Policy Research | Public Administration, Sociology | Problem → Policy → Implementation → Evaluation |
| NSSFC-05 | Field Survey | Anthropology, Ethnology | Field Site → Interview → Record → Analysis |
| NSSFC-06 | Comparative Study | Political Science, Literature | Domestic → Foreign → Comparison → Reference |
| NSSFC-07 | Quantitative Research | Psychology, Sociology | Questionnaire → Statistics → Model → Interpretation |
| NSSFC-08 | Qualitative Research | Education, Nursing | Interview → Coding → Theme → Theory |
| NSSFC-09 | Action Research | Education, Management | Problem → Plan → Action → Reflection |
| NSSFC-10 | Literature Review | Library Science, Information Science | Literature → Review → Evaluation → Prospect |

### Step 2: Collect User Research Information

Use GenUI form to collect:

1. **Basic Research Information**
   - Research Title
   - Research Type (Basic/Applied/Development)
   - Discipline Field

2. **Research Content Overview**
   - Research Objectives
   - Main Research Content (3-5 points)
   - Research Methods Used
   - Expected Outcomes

3. **Special Requirements**
   - Whether to mark timeline milestones
   - Whether to mark phase achievements
   - Special processes or nodes

### Step 3: Generate Technical Roadmap

Based on the user's selected framework and provided research information, generate a draw.io-compatible XML format technical roadmap.

## XML Format Specification

The generated XML follows draw.io's mxGraph specification:

```xml
<mxGraphModel>
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <!-- Node Definition -->
    <mxCell id="2" value="Research Objective" style="rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
      <mxGeometry x="200" y="50" width="120" height="40" as="geometry"/>
    </mxCell>
    <!-- Connection Definition -->
    <mxCell id="3" edge="1" parent="1" source="2" target="4">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>
  </root>
</mxGraphModel>
```

## Output Format

1. **XML Code Block**: Complete draw.io importable XML
2. **Preview Description**: Describes the structure and content of the roadmap
3. **Usage Guide**: How to import and edit in draw.io

## Style Guidelines

- Node Shape: Rounded Rectangle
- Start/End Nodes: Ellipse
- Decision Nodes: Diamond
- Process Nodes: Rectangle
- Color Scheme:
  - Main Process: Blue (#dae8fc → #6c8ebf)
  - Key Nodes: Green (#d5e8d4 → #82b366)
  - Branch Decisions: Yellow (#fff2cc → #d6b656)
