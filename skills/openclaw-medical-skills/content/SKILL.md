---
name: openclaw-medical-skills
description: Access and coordinate 872+ AI medical skills for clinical research, drug discovery, bioinformatics, and healthcare tasks. Use when users ask for medical literature search, drug research, clinical reports, bioinformatics analysis (variant calling, scRNA-seq, proteomics), PubMed queries, FDA database access, protein structure prediction, medical regulatory compliance, or any biomedical/scientific research task. Triggers on "medical skills", "OpenClaw", "clinical research", "drug discovery", "bioinformatics", "PubMed", "ChEMBL", "AlphaFold", "scRNA-seq", "clinical trials", "pharmacovigilance", "medical reports", "healthcare AI".
---

# OpenClaw Medical Skills Hub

A comprehensive coordinator for **872+ AI agent medical skills** covering clinical research, drug discovery, bioinformatics, and healthcare applications.

## Repository Overview

**OpenClaw Medical Skills** is a curated collection of AI agent skills designed for medical and scientific research. Each skill transforms the agent into a specialized domain expert with access to real databases, APIs, and computational tools.

- **Repository**: https://github.com/FreedomIntelligence/OpenClaw-Medical-Skills
- **Total Skills**: 872 curated skills
- **License**: MIT

## Skill Categories

### 1. Clinical & Medical (30+ skills)

| Skill Name | Purpose |
|------------|---------|
| `pubmed-search` | Search PubMed for scientific literature using BioPython Entrez |
| `medical-research-toolkit` | Query 14+ biomedical databases (ChEMBL, PubMed, ClinicalTrials.gov, OpenTargets, OpenFDA, OMIM, Reactome, KEGG, UniProt) |
| `clinical-reports` | Write clinical reports (CARE guidelines, SOAP, H&P, discharge summaries) |
| `clinicaltrials-database` | Query ClinicalTrials.gov via API v2 |
| `usmle` | USMLE exam preparation with progress tracking |
| `fhir-developer-skill` | FHIR API development guide |
| `prior-auth-review-skill` | Automate payer review of prior authorization requests |

### 2. Drug Discovery & Safety (20+ skills)

| Skill Name | Purpose |
|------------|---------|
| `tooluniverse-drug-research` | Comprehensive drug research reports |
| `tooluniverse-drug-drug-interaction` | Drug-drug interaction prediction and risk assessment |
| `tooluniverse-pharmacovigilance` | Analyze drug safety signals from FDA adverse event reports |
| `tooluniverse-drug-repurposing` | Identify drug repurposing candidates |
| `tooluniverse-adverse-event-detection` | Detect and analyze adverse drug event signals |
| `rdkit` | Cheminformatics toolkit for molecular analysis |
| `diffdock` | Diffusion-based molecular docking |
| `deepchem` | Molecular machine learning toolkit |

### 3. Bioinformatics & Genomics (228+ skills)

| Skill Name | Purpose |
|------------|---------|
| `bio-variant-calling` | GATK-based germline variant calling pipeline |
| `bio-variant-annotation` | Annotate VCF files with functional, population, and clinical data |
| `bio-single-cell-batch-integration` | Integrate scRNA-seq datasets (Harmony, BBKNN, scVI) |
| `bio-atac-seq-atac-peak-calling` | Call ATAC-seq chromatin accessibility peaks |
| `bio-methylation-dmr-detection` | Identify differentially methylated regions |
| `bio-metagenomics-abundance` | Estimate microbial taxon abundances |
| `bio-chipseq-peak-calling` | Call ChIP-seq peaks with MACS2 |

### 4. Protein Design & Structure (15+ skills)

| Skill Name | Purpose |
|------------|---------|
| `esm` | ESM3 generative multimodal protein design |
| `alphafold` | Validate protein designs using AlphaFold2 |
| `boltz` | Structure prediction using Boltz-1/Boltz-2 |
| `rfdiffusion` | Generate protein backbones using RFdiffusion |
| `bindcraft` | End-to-end binder design with BindCraft |
| `proteinmpnn` | Design protein sequences using ProteinMPNN |
| `foldseek` | Structure similarity search |

### 5. Single-Cell & Spatial Omics (50+ skills)

| Skill Name | Purpose |
|------------|---------|
| `scanpy` | Single-cell RNA-seq analysis |
| `scvi-tools` | Deep learning for single-cell analysis |
| `single-cell-rna-qc` | Quality control on scRNA-seq data |
| `spatial-tutorials` | Spatial transcriptomics tutorials |
| `single-trajectory` | Trajectory workflows (PAGA, Palantir, VIA) |

### 6. Scientific Databases (35+ skills)

| Skill Name | Purpose |
|------------|---------|
| `clinvar-database` | Query NCBI ClinVar for variant clinical significance |
| `chembl-database` | Query ChEMBL bioactive molecules |
| `uniprot-database` | Direct REST API access to UniProt |
| `string-database` | Query STRING API for protein-protein interactions |
| `kegg-database` | KEGG pathway analysis |
| `gwas-database` | Query NHGRI-EBI GWAS Catalog |
| `drugbank-database` | Access comprehensive drug information |
| `pubmed-database` | Direct REST API access to PubMed |

### 7. Health & Wellness (19 skills)

| Skill Name | Purpose |
|------------|---------|
| `nutrition-analyzer` | Comprehensive nutrition analysis |
| `mental-health-analyzer` | Mental health data analysis |
| `sleep-analyzer` | Sleep quality analysis |
| `fitness-analyzer` | Fitness performance analysis |
| `tcm-constitution-analyzer` | Traditional Chinese Medicine analysis |
| `travel-health-analyzer` | Travel medicine guidance |

### 8. Medical Device Regulatory (47 skills)

| Skill Name | Purpose |
|------------|---------|
| `iso-13485-certification` | ISO 13485 QMS documentation |
| `fda-*` | FDA regulatory compliance tools |
| `iec-62304-*` | IEC 62304 software lifecycle compliance |
| `iso-14971-*` | ISO 14971 risk management |
| `eu-mdr-*` | EU Medical Device Regulation compliance |

### 9. BioOS Extended Suite (285+ skills)

| Skill Name | Purpose |
|------------|---------|
| `autonomous-oncology-agent` | Autonomous oncology research |
| `precision-oncology-agent` | Precision oncology treatment recommendations |
| `clinical-ai-healthcare` | EHR, FHIR, clinical decision support |
| `bio-workflows-*` | End-to-end pipelines (RNA-seq, scRNA-seq, GWAS) |

### 10. Oncology & Precision Medicine (22+ skills)

| Skill Name | Purpose |
|------------|---------|
| `precision-oncology-agent` | Tumor molecular profiling to treatment recommendations |
| `liquid-biopsy-analytics-agent` | ctDNA detection, MRD monitoring |
| `tumor-mutational-burden-agent` | Compute TMB for immunotherapy response |
| `computational-pathology-agent` | WSI analysis, tissue segmentation |

## How to Use This Skill

### Step 1: Identify User Intent

Ask clarifying questions to determine the specific medical/scientific need:

- **Literature & Research**: PubMed searches, systematic reviews, clinical trial data
- **Drug Discovery**: Molecule analysis, drug interactions, pharmacovigilance
- **Bioinformatics**: Genomics, transcriptomics, proteomics analysis
- **Clinical Documentation**: Case reports, diagnostic reports, regulatory documents
- **Healthcare AI**: EHR integration, clinical decision support, FHIR development

### Step 2: Match to Appropriate Skills

Based on the user's request, recommend and activate the most relevant skill(s):

```
User: "Find recent papers on CRISPR delivery methods"
→ Activate: pubmed-search or medical-research-toolkit

User: "Analyze drug-drug interactions for these medications"
→ Activate: tooluniverse-drug-drug-interaction

User: "Run variant calling on this genomic data"
→ Activate: bio-variant-calling

User: "Write a clinical case report following CARE guidelines"
→ Activate: clinical-reports
```

### Step 3: Execute with Domain Expertise

For each skill category, apply specialized workflows:

#### Literature Search Workflow
```python
# Using BioPython Entrez for PubMed
from Bio import Entrez
Entrez.email = "researcher@example.com"

# Search PubMed
handle = Entrez.esearch(db="pubmed", term="your query", retmax=20, sort="date")
record = Entrez.read(handle)
handle.close()
id_list = record["IdList"]
```

#### Drug Research Workflow
```python
# Query drug databases for compound analysis
# Use RDKit for cheminformatics
from rdkit import Chem
mol = Chem.MolFromSmiles("your_smiles_string")
```

#### Bioinformatics Workflow
```python
# Single-cell analysis with Scanpy
import scanpy as sc
adata = sc.read_10x_mtx("cellranger_output/")
sc.pp.calculate_qc_metrics(adata)
```

### Step 4: Validate and Present Results

- Apply appropriate quality checks for medical/scientific accuracy
- Format outputs according to domain standards (CARE, ICH-GCP, HIPAA)
- Include visual elements when beneficial (schematics, diagrams)
- Provide proper citations and references

## Installation Methods

Users can install specific skills from the collection:

### Method 1: Clone and Copy
```bash
git clone https://github.com/FreedomIntelligence/OpenClaw-Medical-Skills.git
cp -r OpenClaw-Medical-Skills/skills/<skill-name> ~/.openclaw/skills/
```

### Method 2: Install Selected Skills
```bash
SKILLS=("pubmed-search" "clinical-reports" "tooluniverse-drug-research")
for skill in "${SKILLS[@]}"; do
    cp -r OpenClaw-Medical-Skills/skills/$skill ~/.openclaw/skills/
done
```

## Quality Standards

When executing medical skills:

1. **Accuracy**: Verify all medical/scientific claims against authoritative sources
2. **Compliance**: Adhere to HIPAA, FDA, ICH-GCP regulations as applicable
3. **Citations**: Provide proper references for all data and literature
4. **Transparency**: Clearly indicate limitations and uncertainty in outputs
5. **Privacy**: Never include identifiable patient information without proper consent

## Related Resources

- [OpenClaw Framework](https://github.com/MedClaw-Org)
- [NanoClaw](https://github.com/MedClaw-Org)
- [ClawHub](https://clawhub.com/)
- [Awesome LLM Resources](https://github.com/WangRongsheng/awesome-LLM-resources)
