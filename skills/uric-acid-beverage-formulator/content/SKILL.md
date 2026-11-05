---
name: uric-acid-beverage-formulator
description: |
  Uric acid beverage formulation expert system. Use when users request:
  - Generate uric acid-lowering beverage formulas
  - Develop functional beverages based on academic research
  - Scan 30 years of uric acid research achievements
  - Hold formula optimization meetings
  - Output perfect formulas and rankings
---

# Uric Acid Beverage Formulation Expert System

## System Architecture

### 1. Expert Team Configuration

**30 World-Class Expert Matrix:**

| Domain | Count | Core Responsibilities |
|--------|-------|----------------------|
| Natural Product Chemistry | 5 | Active ingredient extraction, stability research |
| Food Nutrition | 5 | Nutritional ratio, synergistic effects |
| Pharmacology & Toxicology | 4 | Safety assessment, dose validation |
| Functional Evaluation | 4 | Efficacy verification, clinical evaluation |
| Traditional Chinese Medicine | 3 | TCM theory, traditional applications |
| Food Engineering | 3 | Process optimization, production feasibility |
| China Regulations & IP | 2 | Compliance review, patent strategy |
| Supply Chain Management | 2 | Raw material supply, cost control |
| Sensory Evaluation | 1 | Taste optimization, consumer acceptance |
| Market Analysis | 1 | Commercialization potential |

**20 World-Class Institutions:**

```
Academic Journals (5):
- Nature Medicine
- Food Chemistry
- Journal of Functional Foods
- Phytomedicine
- Chinese Journal of TCM

Research Institutes (6):
- Shanghai Institute of Materia Medica, CAS
- Institute of Medicinal Plant Development, CAMS
- NIH NCCIH (USA)
- NIN (Japan)
- EFSA (EU)
- University of Queensland (Australia)

Testing & Certification (4):
- SGS
- Intertek
- NIFDC (China)
- USP (USA)

Supply Chain Enterprises (5):
- Chenguang Biotech
- Kingpu Co.
- Amway (China) R&D
- DuPont Nutrition
- DSM (China)
```

## 2. Core Ingredient Database

### 2.1 Uric Acid-Lowering Mechanism Classification

| Category | Mechanism | Representative Compounds |
|----------|-----------|-------------------------|
| XOD Inhibitors | Inhibit xanthine oxidase | Apigenin, Quercetin, Puerarin |
| UA Excretion Promotion | Increase uric acid excretion | Psyllium polysaccharide |
| UA Synthesis Inhibition | Inhibit purine metabolism | Tea polyphenols, Curcumin |
| Antioxidant/Anti-inflammatory | Reduce oxidative stress | Lycopene, Astaxanthin, Anthocyanins |
| Renal Protection | Improve kidney function | Arctiin, Mulberry leaf alkaloids |

### 2.2 Core Ingredients and Dose Ranges (Literature-Based)

```python
CORE_INGREDIENTS = {
    # Natural Flavonoids
    "Apigenin": {"dose_range": "50-200mg", "evidence_level": "A", "sources": "Celery, Chamomile"},
    "Quercetin": {"dose_range": "100-500mg", "evidence_level": "A", "sources": "Onion, Apple peel"},
    "Puerarin": {"dose_range": "100-300mg", "evidence_level": "A", "sources": "Kudzu root"},
    "Rutin": {"dose_range": "100-250mg", "evidence_level": "B", "sources": "Buckwheat, Sophora"},

    # Polyphenols
    "Tea Polyphenols": {"dose_range": "200-500mg", "evidence_level": "A", "sources": "Green tea"},
    "Curcumin": {"dose_range": "100-300mg", "evidence_level": "B", "sources": "Turmeric"},
    "Proanthocyanidins": {"dose_range": "100-200mg", "evidence_level": "B", "sources": "Grape seed"},

    # Alkaloids
    "Mulberry Alkaloids (DNJ)": {"dose_range": "50-150mg", "evidence_level": "A", "sources": "Mulberry leaf"},
    "Nuciferine": {"dose_range": "20-50mg", "evidence_level": "B", "sources": "Lotus leaf"},

    # Polysaccharides
    "Psyllium Husk": {"dose_range": "500-1500mg", "evidence_level": "A", "sources": "Plantago ovata"},
    "Laminaran": {"dose_range": "200-500mg", "evidence_level": "B", "sources": "Kelp"},

    # Other Active Compounds
    "Cherry Extract": {"dose_range": "500-1000mg", "evidence_level": "A", "sources": "Tart cherry"},
    "Tart Cherry Powder": {"dose_range": "400-800mg", "evidence_level": "A", "sources": "Montmorency"},
    "Vitamin C": {"dose_range": "100-300mg", "evidence_level": "A", "sources": "Ascorbic acid"},
}

# Evidence Level Guidelines:
# A: Supported by multiple RCTs or high-quality Meta-analyses
# B: Preliminary clinical evidence or high-quality animal studies
# C: In vitro studies or traditional use experience
```

## 3. Scoring Model

### 3.1 Multi-Dimensional Scoring System (100-point)

| Primary Dimension | Weight | Secondary Metrics |
|-------------------|--------|-------------------|
| Scientific Evidence (25%) | 25 | Literature count (8), Evidence level (7), Mechanism clarity (5), Human studies (5) |
| Safety (20%) | 20 | Acute toxicity (5), Subchronic toxicity (5), Contraindications (5), Interactions (5) |
| Sensory Quality (15%) | 15 | Taste score (8), Color (4), Stability (3) |
| Process Feasibility (15%) | 15 | Extraction difficulty (5), Solubility (5), Shelf life (5) |
| Cost Efficiency (10%) | 10 | Raw material cost (5), Processing cost (5) |
| Innovation (8%) | 8 | Formula uniqueness (4), IP potential (4) |
| Market Potential (7%) | 7 | Target population (3), Market size (2), Competition (2) |

### 3.2 Entrepreneurship Adaptability Scoring (100-point)

| Dimension | Weight | Scoring Criteria |
|-----------|--------|-----------------|
| Startup Cost | 30% | <100K CNY (100), 100-300K (80), 300-500K (60), >500K (40) |
| Supply Stability | 25% | Domestic abundant (100), Import but stable (70), Tight supply (40) |
| Compliance Barrier | 25% | Regular food (100), Health food (60), Drug (20) |
| Market Acceptance | 20% | Good taste (100), Needs education (60), Low awareness (30) |

## 4. Execution Process

### 4.1 Phase 1: Academic Scanning (Output: Ingredient Database)

```
Step 1.1: Scan 10 Major Academic Platforms (2016-2026)
- PubMed, Web of Science, CNKI, ScienceDirect
- Wiley Online Library, SpringerLink, ACS Publications
- RSC Publishing, Taylor & Francis, Google Scholar

Step 1.2: Search Strategy
- "uric acid" AND ("gout" OR "hyperuricemia")
- "xanthine oxidase inhibitor"
- "urate lowering" AND ("natural product" OR "food")
- Chinese search: hyperuricemia, gout, xanthine oxidase inhibitor

Step 1.3: Evidence Level Assessment
- Level A: >=3 RCTs or high-quality Meta-analysis
- Level B: >=1 RCT or multiple high-quality animal studies
- Level C: In vitro studies or traditional use
```

### 4.2 Phase 2: Formula Generation (Output: Initial Formula Set)

```
Step 2.1: Generate Candidate Formulas (30) Based on Scan Results
- Follow medicinal food catalog restrictions
- Comply with GB 2760 food additive standards
- Comply with GB 14880 nutritional fortification standards

Step 2.2: Standardize Formula Structure
- Base solvent: Water/purified water
- Active group: 2-5 core functional ingredients
- Auxiliary group: Solubilizers, stabilizers, flavor correctors
- Flavoring group: Sweeteners, acidulants, flavors (optional)
```

### 4.3 Phase 3: Expert Review (10 Rounds of Comparative Experiments)

```
Review Dimensions:
- Pharmacology experts: Efficacy mechanism verification
- Nutrition experts: Nutritional ratio rationality
- Toxicology experts: Safety assessment
- Engineering experts: Production process feasibility
- Regulatory experts: Compliance review
- Market experts: Commercialization potential
- Sensory experts: Taste testing

Scoring Output: Each expert/institution submits scoring matrix
```

### 4.4 Phase 4: Optimization Iteration (20 Rounds of Progressive Meetings)

```
Optimization Strategy:
- Rounds 1-5: Ingredient replacement optimization
- Rounds 6-10: Dose adjustment optimization (evidence-based)
- Rounds 11-15: Process optimization (extraction, stability)
- Rounds 16-20: Commercialization optimization (cost, taste, regulations)
```

### 4.5 Phase 5: Output & Ranking

```
Final Outputs:
1. 300ml Perfect Formula Sheet (Complete Formula Table)
2. Comprehensive Strength TOP10 Ranking
3. Entrepreneurship Recommendation TOP10 Ranking
4. Multi-dimensional Scoring Radar Chart for Each Formula
5. Expert Review Summary
6. IP Protection Recommendations
7. Supply Chain Feasibility Report
```

## 5. Formula Output Template

```markdown
## Uric Acid Beverage Formula (300ml)

### Formula ID: UA-2026-001
### Comprehensive Score: XX/100
### Entrepreneurship Index: XX/100

#### Formula Composition

| Ingredient | Amount | Specification | Supplier Reference |
|------------|--------|---------------|---------------------|
| Water | To 300ml | Purified | - |
| Celery Seed Extract | 150mg | 10:1 extract | Chenguang Biotech |
| Mulberry Leaf Extract | 200mg | DNJ>=1% | Mulberry Co. |
| Tart Cherry Powder | 500mg | 50:1 concentrate | Montmorency |
| Green Tea Polyphenols | 150mg | EGCG>=50% | DSM |
| Psyllium Husk | 800mg | DF>=85% | India import |
| Vitamin C | 100mg | Food grade | DSM |
| Citric Acid | 2g | GB 1886.39 | - |
| Sucralose | 0.05g | GB 25532 | - |

#### Nutrition Facts (Per 100ml)

| Item | Content | NRV% |
|------|---------|------|
| Energy | XkJ | X% |
| Protein | Xg | X% |
| Fat | Xg | X% |
| Carbohydrate | Xg | X% |
| Dietary Fiber | Xg | X% |

#### Functional Ingredient Content

| Functional | Content | Claim Basis |
|------------|---------|-------------|
| Total Flavonoids | >=50mg | Pharmacological research |
| DNJ | >=2mg | Mulberry-specific |
| Anthocyanins | >=10mg | Cherry-derived |

#### Production Process Summary
[Brief description of key process steps]

#### Expert Review Summary
[Summary of 30 experts' reviews]

#### Entrepreneurship Feasibility Analysis
- Startup cost: X万元 CNY
- Supply chain risk: Low/Medium/High
- Compliance path: Regular food/Health food
- Expected gross margin: XX%
```

## 6. Acceptance Criteria

### 6.1 Deliverable Completeness
- [ ] Complete scanning report from 10 academic platforms
- [ ] Output 30 candidate formulas
- [ ] Complete 10 rounds of expert comparative experiments
- [ ] Complete 20 rounds of progressive optimization
- [ ] Output TOP10 comprehensive ranking
- [ ] Output TOP10 entrepreneurship recommendation ranking
- [ ] Each formula includes complete scoring matrix

### 6.2 Quality Standards
- [ ] Formula ingredients comply with Chinese medicinal food catalog
- [ ] All ingredients comply with GB 2760/GB 14880
- [ ] Active ingredient doses have literature support
- [ ] Complete basic safety assessment
- [ ] Complete cost accounting

### 6.3 Scoring Transparency
- [ ] Each scoring item has clear criteria
- [ ] Scoring weights are publicly transparent
- [ ] Expert opinions are traceable
- [ ] Ranking logic is clear and explainable

## 7. Important Notes

1. **Regulations First**: All formulas must comply with current Chinese food regulations
2. **Dose Safety**: All ingredient doses must not exceed literature-reported safe doses
3. **Evidence-Based**: Scoring must be based on real academic evidence, not subjective assumptions
4. **Commercial Viability**: Formulas must consider actual production feasibility
5. **Continuous Update**: Academic database must be regularly updated with latest research
