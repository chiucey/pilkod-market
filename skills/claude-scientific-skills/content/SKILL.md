---
name: claude-scientific-skills
description: A comprehensive collection of 170+ scientific and research skills for AI agents. Use when users need help with bioinformatics, cheminformatics, drug discovery, clinical research, machine learning, data visualization, scientific writing, literature review, and other scientific computing tasks. Covers genomics, proteomics, metabolomics, medical imaging, quantum computing, materials science, geospatial analysis, and more.
license: MIT license
metadata:
    skill-author: K-Dense Inc.
    repository: https://github.com/K-Dense-AI/claude-scientific-skills
---

# Claude Scientific Skills

## Overview

Claude Scientific Skills is a comprehensive collection of **170+ ready-to-use scientific and research skills** that transform an AI agent into a powerful research assistant capable of executing complex multi-step scientific workflows. Created by K-Dense, this collection covers all major scientific domains.

## Skill Categories

### Bioinformatics & Genomics (20+ skills)
- **Sequence Analysis**: BioPython, pysam, scikit-bio, BioServices
- **Single-Cell Analysis**: Scanpy, AnnData, scvi-tools, scVelo, Arboreto, Cellxgene Census
- **Genomic Tools**: gget, geniml, gtars, deepTools, FlowIO, Zarr, TileDB-VCF
- **Phylogenetics**: ETE Toolkit, Phylogenetics (MAFFT, IQ-TREE 2, FastTree)

### Cheminformatics & Drug Discovery (13+ skills)
- **Molecular Manipulation**: RDKit, Datamol, Molfeat
- **Deep Learning**: DeepChem, TorchDrug
- **Docking & Screening**: DiffDock
- **Molecular Dynamics**: OpenMM + MDAnalysis
- **Cloud Quantum Chemistry**: Rowan
- **Drug-likeness**: MedChem
- **Binding Affinities**: BindingDB
- **Benchmarks**: PyTDC

### Proteomics & Mass Spectrometry (2 skills)
- **Spectral Processing**: matchms, pyOpenMS

### Clinical Research & Precision Medicine (16+ skills)
- **Clinical Databases**: ClinicalTrials.gov, ClinVar, ClinPGx, COSMIC, FDA Databases
- **Cancer Genomics**: cBioPortal, DepMap
- **Disease-Gene Associations**: Monarch Initiative
- **Healthcare AI**: PyHealth, NeuroKit2, Clinical Decision Support
- **Clinical Documentation**: Clinical Reports, Treatment Plans

### Medical Imaging & Digital Pathology (3 skills)
- **DICOM Processing**: pydicom
- **Whole Slide Imaging**: histolab, PathML

### Machine Learning & AI (16+ skills)
- **Deep Learning**: PyTorch Lightning, Transformers, Stable Baselines3, PufferLib
- **Classical ML**: scikit-learn, scikit-survival, SHAP
- **Time Series**: aeon, TimesFM
- **Bayesian Methods**: PyMC
- **Optimization**: PyMOO
- **Graph ML**: Torch Geometric
- **Dimensionality Reduction**: UMAP-learn

### Materials Science, Chemistry & Physics (7 skills)
- **Materials**: Pymatgen
- **Metabolic Modeling**: COBRApy
- **Astronomy**: Astropy
- **Quantum Computing**: Cirq, PennyLane, Qiskit, QuTiP

### Data Analysis & Visualization (17+ skills)
- **Visualization**: Matplotlib, Seaborn, Plotly, Scientific Visualization
- **Geospatial Analysis**: GeoPandas, GeoMaster
- **Network Analysis**: NetworkX
- **Symbolic Math**: SymPy
- **Document Processing**: Document Skills (PDF, DOCX, PPTX, XLSX)

### Laboratory Automation (4 skills)
- **Liquid Handling**: PyLabRobot
- **Cloud Lab**: Ginkgo Cloud Lab
- **Protocol Management**: Protocols.io
- **LIMS Integration**: Benchling, LabArchives

### Scientific Databases (37+ skills -> 250+ databases)
- **Protein**: UniProt, PDB, AlphaFold DB, InterPro
- **Chemical**: PubChem, ChEMBL, DrugBank, ZINC, HMDB, BindingDB
- **Genomic**: Ensembl, NCBI Gene, GEO, ENA, GWAS Catalog, gnomAD, GTEx, JASPAR
- **Clinical**: ClinVar, COSMIC, ClinicalTrials.gov, Monarch Initiative
- **Literature**: PubMed, bioRxiv, OpenAlex
- **Pathways**: KEGG, Reactome, STRING
- **Financial**: Alpha Vantage, FRED, EDGAR, USPTO

### Scientific Communication (24+ skills)
- **Literature**: Literature Review, Peer Review, Citation Management
- **Writing**: Scientific Writing, Scientific Brainstorming
- **Presentations**: Scientific Slides, LaTeX Posters, PPTX Posters
- **Visualization**: Scientific Schematics, Infographics, Scientific Visualization
- **Publishing**: Paper-2-Web, Venue Templates

### Research Methodology (11+ skills)
- **Ideation**: Scientific Brainstorming, Hypothesis Generation
- **Critical Analysis**: Scientific Critical Thinking, Scholar Evaluation
- **Funding**: Research Grants
- **Market Analysis**: Market Research Reports

## Quick Examples

### Drug Discovery Pipeline
```
Query ChEMBL for EGFR inhibitors, analyze structure-activity relationships with RDKit,
generate improved analogs with datamol, perform virtual screening with DiffDock against
AlphaFold EGFR structure, and create visualizations.
```

### Single-Cell RNA-seq Analysis
```
Load 10X dataset with Scanpy, perform QC, integrate with Cellxgene Census data,
identify cell types using marker genes, run differential expression with PyDESeq2,
infer gene regulatory networks with Arboreto, and enrich pathways via Reactome/KEGG.
```

### Clinical Variant Interpretation
```
Parse VCF with pysam, annotate variants with Ensembl VEP, query ClinVar for pathogenicity,
check COSMIC for cancer mutations, retrieve gene info from NCBI Gene, and generate
clinical report with document processing tools.
```

## Installation

The skills are designed to work with any AI agent that supports the [Agent Skills](https://agentskills.io/) standard. Individual skills can be copied to your skills directory:
- **Cursor**: `~/.cursor/skills/` or `.cursor/skills/`
- **Claude Code**: `~/.claude/skills/` or `.claude/skills/`
- **Codex**: `~/.codex/skills/` or `.codex/skills/`

## Dependencies

Many skills require Python packages. Install `uv` as the package manager:
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Individual skills specify their requirements in their SKILL.md files.

## Key Features

- **170+ Skills**: Extensive coverage across all major scientific domains
- **250+ Databases**: Collective access through dedicated and multi-database packages
- **Production-Ready Code**: Tested, validated examples following scientific best practices
- **Multi-Step Workflows**: Execute complex pipelines with a single prompt
- **Well Documented**: Each skill includes examples, use cases, and best practices

## Documentation Structure

Each individual skill includes:
- Comprehensive `SKILL.md` documentation
- Practical code examples
- Use cases and best practices
- Integration guides
- Reference materials

## Resources

- **GitHub Repository**: https://github.com/K-Dense-AI/claude-scientific-skills
- **K-Dense Web**: https://k-dense.ai (hosted platform with cloud GPUs)
- **Documentation**: See individual skill folders for detailed documentation
- **Examples**: `docs/examples.md` for comprehensive workflow examples

## Citation

If you use Claude Scientific Skills in your research:
```bibtex
@software{claude_scientific_skills_2026,
  author = {{K-Dense Inc.}},
  title = {Claude Scientific Skills: A Comprehensive Collection of Scientific Tools},
  year = {2026},
  url = {https://github.com/K-Dense-AI/claude-scientific-skills}
}
```

## License

MIT License. Individual skills may have their own licenses specified in their SKILL.md files.
