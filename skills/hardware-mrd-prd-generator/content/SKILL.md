---
name: hardware-mrd-prd-generator
description: "硬件产品市场需求与产品规划技能。当用户需要进行市场分析、用户研究、痛点挖掘、场景定义、功能规划、定价策略、商业分析、销售预测、ROI评估，或需要生成MRD/PRD文档时触发此技能。适用场景：智能硬件新品立项、产品规划会议、市场调研、竞品分析、定价策略制定。"
---

## 1. Skill Overview

### 1.1 Purpose

This skill provides a comprehensive methodology for creating professional **Market Requirements Documents (MRD)** and **Product Requirements Documents (PRD)** for hardware products, with special focus on smart hardware, IoT devices, and sports technology products.

### 1.2 When to Use

- Creating new hardware product from concept stage
- Product line extension or platform strategy
- Entering new market with existing technology
- Companion product development for existing ecosystem
- Business case development for hardware startup

### 1.3 Trigger Keywords

```
MRD, PRD, 市场分析, 产品规划, 需求文档, 硬件产品,
产品定位, 用户画像, 痛点分析, 商业分析, 销售预测,
智能硬件, IoT产品
```

---

## 2. Required Input

### 2.1 User Must Provide

| Information | Required | Description |
|-------------|----------|-------------|
| Product Type | Required | Hardware category |
| Target Market | Required | Geographic focus |
| Competitor Information | Optional | Known competitors |
| Price Range | Optional | Target price or margin |
| Integration Requirements | Optional | Ecosystem needs |

### 2.2 Input Examples

**Example 1 - Full Input**:
```
产品类型: 智能硬件产品
目标市场: 中国+海外
竞品信息: 行业竞品
集成需求: 生态整合
```

**Example 2 - Minimal Input**:
```
产品类型: IoT设备
目标市场: 全球
```

---

## 3. Output Specification

### 3.1 Document Structure

| Document | Language | Format |
|----------|----------|--------|
| MRD Document | Chinese/English | Markdown + Word |
| PRD Document | Chinese/English | Markdown + Word |
| Business Analysis | Chinese/English | Markdown + Excel |

### 3.2 Document Contents

**MRD Document Contents**:

1. Executive Summary
2. Market Analysis
   - Market Size (TAM/SAM/SOM)
   - Market Trends
   - Competitive Landscape
3. Target User Analysis
   - User Segmentation
   - User Personas (3-5 profiles)
   - User Needs Summary
4. Core Scenarios (5-8 scenarios)
5. Pain Points Analysis
6. Emotional Needs Analysis
7. Market Recommendations

**PRD Document Contents**:

1. Product Overview
2. Product Features
3. Feature Specifications
4. Technical Requirements
5. User Benefits Mapping
6. Pricing Strategy
7. Business Model
8. Success Metrics

---

## 4. Methodology Framework

### 4.1 MRD Framework

```
Market Research → User Research → Competitive Analysis
         ↓              ↓              ↓
    Scenario Mining → Pain Point Analysis → Emotional Analysis
         ↓              ↓              ↓
              Opportunity Synthesis
                     ↓
              Market Recommendations
```

### 4.2 PRD Framework

```
Product Vision → Feature Definition → Technical Specification
       ↓              ↓              ↓
  User Benefit Mapping → Pricing Strategy → Business Model
       ↓              ↓              ↓
           Success Metrics Definition
```

### 4.3 Pricing Calculation

**Target Profit Margin: User-defined (default 45%)**

| Market | Formula |
|--------|---------|
| Domestic | 成本 ÷ (1 - 目标利润率) |
| Overseas | (成本 + 物流成本) ÷ (1 - 目标利润率) |

### 4.4 BOM Cost Structure Template

| Component | Notes |
|-----------|-------|
| Core Modules | WiFi/BT, MIC, Speaker |
| Power Module | Charging circuit |
| Main Board | PCB + power management |
| Housing | Structure + finish |
| Other | Connectors, etc. |

*Note: Specific costs should be filled based on actual product*

### 4.5 Total Cost Structure Template

| Cost Item | Percentage |
|-----------|------------|
| Material Cost | ~70% |
| Manufacturing | ~10% |
| Quality Control | ~5% |
| Overhead | ~10% |
| License | ~5% |

*Note: Actual percentages vary by product*

---

## 5. Sales Projection Model

### 5.1 Model Framework

**Year 1 Projection Template**:

| Quarter | Units | ASP | Revenue |
|---------|-------|-----|---------|
| Q1 | X | X | X |
| Q2 | X | X | X |
| Q3 | X | X | X |
| Q4 | X | X | X |
| **Total** | **X** | **X** | **X** |

*Note: Fill based on market analysis and business planning*

### 5.2 Multi-Year Framework

| Metric | Year 1 | Year 2 | Year 3 |
|--------|--------|--------|--------|
| Units | X | X | X |
| Revenue | X | X | X |
| Growth Rate | - | X% | X% |

*Note: Projections based on conservative, base, aggressive scenarios*

---

## 6. Core Selling Points Framework

### 6.1 Selling Point Matrix

| Selling Point | Description | Target User | Impact |
|---------------|-------------|-------------|--------|
| Innovation | 产品差异化优势 | 目标用户 | High/Medium/Low |
| Ecosystem | 生态整合能力 | 存量用户 | High/Medium/Low |
| Experience | 用户体验优化 | 所有用户 | High/Medium/Low |

### 6.2 Competitive Differentiation

| Dimension | Your Product | Competitor | Differentiation |
|-----------|--------------|------------|-----------------|
| Price | 待定 | - | 性价比 |
| Features | 待定 | - | 功能优势 |
| Ecosystem | 待定 | - | 生态协同 |
| AI/Capability | 待定 | - | 智能化 |

---

## 7. Document Templates

### 7.1 MRD Template

```markdown
# [Product Name] 市场需求文档
# MRD - Market Requirements Document

## 1. Executive Summary
## 2. Market Overview
   2.1 Market Size
   2.2 Market Trends
   2.3 Competitive Landscape
## 3. Target User Analysis
   3.1 User Segmentation
   3.2 User Personas
   3.3 User Needs Summary
## 4. Core Scenarios
## 5. Pain Points & Opportunities
## 6. Emotional Needs
## 7. Market Recommendations
```

### 7.2 PRD Template

```markdown
# [Product Name] 产品需求文档
# PRD - Product Requirements Document

## 1. Product Overview
## 2. Product Features
## 3. Feature Specifications
## 4. Technical Requirements
## 5. User Benefits
## 6. Pricing Strategy
## 7. Business Model
## 8. Success Metrics
```

---

## 8. Quality Checklist

### 8.1 MRD Quality Checklist

- [ ] Market size quantified with data sources cited
- [ ] Target users clearly defined with 3+ personas
- [ ] Pain points validated with evidence
- [ ] Competitive landscape comprehensively analyzed
- [ ] Core scenarios mapped to user journeys
- [ ] Emotional needs identified and prioritized

### 8.2 PRD Quality Checklist

- [ ] Product differentiation clearly articulated
- [ ] Feature priority aligned with user needs
- [ ] Technical specifications feasible and testable
- [ ] Cost model detailed with BOM breakdown
- [ ] Pricing justified with margin targets
- [ ] Sales projections grounded in assumptions
- [ ] Success metrics defined with measurable KPIs

---

## 9. Glossary

| Term | Chinese | Definition |
|------|---------|------------|
| MRD | 市场需求文档 | Market Requirements Document |
| PRD | 产品需求文档 | Product Requirements Document |
| TAM | 总体可及市场 | Total Addressable Market |
| SAM | 可服务市场 | Serviceable Available Market |
| SOM | 可获得市场 | Serviceable Obtainable Market |
| BOM | 物料清单 | Bill of Materials |
| ROI | 投资回报率 | Return on Investment |
| ASP | 平均售价 | Average Selling Price |

---

## 10. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | XXXX-04-14 | MiniMax Agent | Initial version |
| 1.1 | XXXX-04-16 | MiniMax Agent | Sanitized - removed real company references and specific business data |

---

**Sanitization Note**: This version has been processed to remove:
- Specific company names
- Real financial projections
- Detailed user personas with specific attributes
- Industry-specific case study data

All templates and frameworks remain intact for general hardware product planning use.
