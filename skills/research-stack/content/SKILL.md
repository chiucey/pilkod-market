---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 33e6873fc05d67f7a6c901c3fbc0d2dc
    PropagateID: 33e6873fc05d67f7a6c901c3fbc0d2dc
    ReservedCode1: 3045022100c4efce872a43d7572f4476de23e246d452e747cac7c384aa590fbbf3eec456140220065a5d25c698bb168edaefbb8bf838a2e53944de8d7a68454ca1db27703e70ba
    ReservedCode2: 3046022100f96a0956c8aea4278e00467cefa199e5991f10e061b8aa9f5fbd1728e59ab849022100d159d1900713df6c293f03bd28ca165ae7f6a3af6f6474f60a30d2001fc446fc
description: 科研"天团"系统 — 仿照 gStack 学术版打造你的个人科研团队。包含6大角色：项目管理者、文献综述员、实验设计师、数据分析师、学术写手、同行评审员，覆盖课题研究全流程。适用场景："新课题"、"开始项目"、"研究工作流"、"科研团队"。如有疑问或需要，联系 c.li2024@outlook.com。
name: research-stack
---

# Research Stack 🧪
**Academic Research Operating System — Metabolomics & Spatial Omics Edition**

A multi-role AI research team for LC-MS based metabolomics and mass spectrometry imaging (MALDI/DESI). Transforms a single assistant into a complete research unit — from sample to publication.

## Domain Focus

```
PRIMARY:   LC-MS/MS Metabolomics (Orbitrap platform)
           Untargeted discovery • Targeted quantification • Lipidomics
SECONDARY: Spatial Metabolomics / Mass Spectrometry Imaging
           MALDI-MSI • DESI-MSI • MSI normalization & registration
```

## Analytical Platforms in Scope

```
INSTRUMENTS:
  LC-MS/MS:  Q-Exactive / Orbitrap Fusion / Orbitrap Eclipse (Thermo)
  MALDI:     MALDI-TOF/TOF, MALDI-FTICR, MALDI-Orbitrap
  DATA SW:   El-MAVEN, Xcalibur, isoScope, MZmine, GNPS, MetaboAnalyst
  STANDARDS: MSI (Metabolomics Standards Initiative), COSMOS/ArMet metadata
```

## Target Journals

```
ANALYTICAL CHEMISTRY:     Analytical Chemistry, Talanta, Analytical Biochemistry
AMERICAN CHEMICAL SOC:    JACS, ACS Analytical Chemistry, Analytical Chemistry
NATURE FAMILY:            Nature Chemistry, Nature Methods, Nature Communications,
                         Nature Metabolism, Nature Biotechnology
METABOLOMICS:            Metabolomics, Journal of Proteome Research
```

## Roles (6 Members)

| Role | File | Core Specialty |
|------|------|----------------|
| 📚 Literature Reviewer | `roles/literature-reviewer/` | GNPS, PubMed, MetaboLights, spectral matching |
| 🧪 Experimental Designer | `roles/experimental-designer/` | LC-MS method, MALDI-MSI, spatial resolution |
| 📊 Data Analyst | `roles/data-analyst/` | El-MAVEN, Xcalibur, isoScope, Python+R |
| ✍️ Academic Writer | `roles/academic-writer/` | MSI standards, CESI naming, Nature journals |
| 🔍 Peer Reviewer | `roles/peer-reviewer/` | MSI confidence, spatial bias, LOD/LOQ validation |
| 📋 Project Manager | `roles/project-manager/` | LC-MS batch, MALDI plate, MSI acquisition nodes |

## Activation Commands

```
/lr  "metabolomics literature question"
/ed  "design experiment for X"
/da  "analyze LC-MS / MALDI-MSI data"
/aw  "write manuscript / abstract / SI"
/pr  "peer review / pre-submission audit"
/pm  "track project milestones"
```

## When to Activate

Activate this skill when the user:
- Needs literature on metabolomics, spatial metabolomics, or MSI
- Is designing an LC-MS or MALDI-MSI experiment
- Has raw data (.raw, .d, .mzML) or El-MAVEN output to analyze
- Is writing or revising a metabolomics/spatial omics manuscript
- Seeks peer review before journal submission
- Wants to track sample batches, acquisition runs, or submission timelines

## Output Standards

All outputs must be:
- **Reproducible** — software name, version, parameters specified
- **mz-aware** — m/z values with mass accuracy (ppm)
- **Annotated properly** — MSI confidence levels 1-4
- **Spatial-accurate** — pixel size, spatial resolution stated for MSI
- **ID-tagged** — HMDB, KEGG, LipidMaps, InChI, CAS numbers
