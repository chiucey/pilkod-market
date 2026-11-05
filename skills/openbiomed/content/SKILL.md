---
name: openbiomed
description: OpenBioMed is a comprehensive deep learning toolkit for biomedical discovery. Use when users ask about molecular property prediction, protein analysis, drug discovery, single-cell omics, BioMedGPT models, pharmaceutical research, biomedical AI workflows, or need to work with molecules, proteins, and biomedical data. Also use for tasks involving drug candidate discovery, ADMET prediction, protein structure prediction, mutation analysis, or any biomedical AI research tasks.
---

# OpenBioMed - AI-Driven Biomedical Discovery Toolkit

## Overview

OpenBioMed is a comprehensive deep learning toolkit and skillset for biomedical discovery, developed by Tsinghua University AIR and PharMolix. It provides **45 skills** and **20+ tools** that enable researchers to build and use AI-driven workflows for solving complicated biomedical research tasks.

## Key Capabilities

### 1. Multimodal Data Support
- **Molecules**: Small molecules with SMILES notation
- **Proteins**: Amino acid sequences and 3D structures
- **Single Cells**: Transcriptomics and multi-omics data
- **Biomedical Text**: Literature and knowledge graphs

### 2. Available Models

| Model | Description | Release Date |
|-------|-------------|--------------|
| **BioMedGPT-R1** | Multimodal biomedical reasoning model (17B) | 2025/02/20 |
| **BioMedGPT-Mol** | Multimodal molecular language model | 2026/02/02 |
| **PharmolixFM** | All-atom molecular foundation model | 2025/03/07 |
| **BioMedGPT-10B** | First commercial-friendly multimodal biomedical model | 2023/08/14 |
| **MolFM** | Multi-modal molecular foundation model | 2023/06/12 |
| **LangCell** | Language-Cell multimodal model for single-cell | 2024/05/16 |
| **MutaPLM** | Protein language model for mutation analysis | 2025 |

### 3. Core Tools

- **Molecular Property Prediction**: Predict BBB penetration, side effects
- **Molecule QA**: Answer textual queries about molecules using BioT5
- **Molecule Visualization**: Visualize molecular structures
- **Protein Folding**: Predict 3D protein structures with ESMFold
- **Protein Pocket Prediction**: Predict binding sites with P2Rank
- **Mutation Analysis**: Explain and design mutations with MutaPLM
- **Protein-Molecule Docking**: Generate binding poses with PharmolixFM
- **Structure-based Drug Design**: Generate molecules with PharmolixFM/MolCRAFT

## Installation

```bash
# Create conda environment
conda create -n OpenBioMed python=3.9
conda activate OpenBioMed

# Install PyTorch with CUDA
pip install torch==1.13.1+{cuda_version} torchvision==0.14.1+{cuda_version} torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/{cuda_version}

# Install PyG dependencies
pip install pyg_lib torch_scatter torch_sparse torch_cluster torch_spline_conv -f https://data.pyg.org/whl/torch-1.13.1+{cuda_version}.html

# Install OpenBioMed
pip install -r requirements.txt
pip install -e .
```

## Quick Start

### Basic API Usage

```python
from open_biomed.data import Molecule

# Load and analyze molecules
molecule = Molecule(smiles="CC(=O)OC1=CC=CC=C1C(=O)O")
print(molecule.calc_logp())
```

### Molecule Processing

```python
from open_biomed.data import Molecule, Protein

# Load molecule from SMILES
mol = Molecule(smiles="CCO")  # Ethanol

# Load protein from sequence
protein = Protein(sequence="MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSH")
```

### Using ML Tools

```python
from open_biomed.tools import MoleculePropertyPredictor, ProteinFolding

# Predict molecule properties
predictor = MoleculePropertyPredictor()
properties = predictor.predict(mol)
```

## Skill Categories

### Drug Discovery Skills
- `drug-candidate-discovery`: Generate diverse druggable molecules
- `drug-lead-analysis`: Analyze drug-likeness (QED, Lipinski)
- `admet-prediction`: Predict ADMET properties
- `retrosynthesis-planning`: Retrosynthetic planning
- `target-drug-report`: Generate drug development reports

### Protein Engineering Skills
- `protein-mutation-analysis`: Analyze mutations with MutaPLM
- `functional-protein-design`: Generate protein sequences
- `protein-function-prediction`: Predict protein functions
- `structure-prediction-boltz-2`: Predict protein complex structures

### Single-Cell Analysis Skills
- `single-cell-foundation-model-scrna-seq-geneformer`: Geneformer workflows
- `single-cell-scrna-seq-analysis-scanpy`: Complete scRNA-seq analysis
- `cellxgene-census-query`: Query 61M+ cell database

### Data Retrieval Skills
- `pubchem-query`: Query chemical structures
- `uniprot-query`: Query protein sequences
- `chembl-query`: Query bioactivity data
- `biomedical-literature-search`: Search PubMed

## Use Cases

### 1. Drug Candidate Discovery

```python
# Generate molecules for a target protein
from open_biomed.tools import StructureBasedDrugDesign

sbd = StructureBasedDrugDesign()
candidates = sbd.generate(protein=target_protein, pocket=predicted_pocket)
```

### 2. Protein Mutation Analysis

```python
# Analyze mutation effects
from open_biomed.tools import MutationAnalyzer

analyzer = MutationAnalyzer()
explanation = analyzer.explain(protein=protein, mutation="A123G")
```

### 3. Single-Cell Analysis

```python
# Analyze scRNA-seq data
from open_biomed.tools import ScanpyAnalysis

analysis = ScanpyAnalysis()
results = analysis.process(count_matrix=counts, normalize=True)
```

## Technical Details

### Architecture
- **Foundation Layer**: Scientific data and knowledge graphs
- **Model Layer**: Vertical large models and core algorithms
- **Agent Layer**: Base LLMs and agent design platform

### Data Modalities
- Molecular structures (SMILES, SDF)
- Protein sequences and structures (FASTA, PDB)
- Single-cell transcriptomics (MatrixMarket, H5AD)
- Biomedical text and knowledge graphs

### Evaluation Metrics
- Protein-molecule docking: RMSD < 2A (PharmolixFM vs AlphaFold3)
- Cross-modal retrieval: 12.03% improvement (MolFM)
- Biomedical QA: Parity with human experts (BioMedGPT)

## Resources

- **GitHub**: https://github.com/PharMolix/OpenBioMed
- **Platform**: https://openbiomed.pharmolix.com
- **Models**: https://wisemodel.cn/organization/PharMolix

## Citation

```bibtex
@misc{OpenBioMed_code,
  author={Luo, Yizhen and Yang, Kai and Fan, Siqi and Hong, Massimo and Zhao, Suyuan and Chen, Xinrui and Nie, Zikun and Luo, Wen and Xie, Ailin and Liu, Xing Yi and Zhang, Jiahuan and Wu, Yushuai and Nie, Zaiqing},
  title={Code of OpenBioMed},
  year={2023},
  howpublished={\url{https://github.com/Pharmolix/OpenBioMed.git}}
}
```

## Limitations

- BioMedGPT should NOT be used to provide services to the general public
- Generating content that violates applicable laws is strictly prohibited
- Commercial use of BioMedGPT-LM models requires accepting the Acceptable Use Policy
