---
name: medsam
description: MedSAM (Segment Anything in Medical Images) skill for medical image segmentation. Use when users request medical image segmentation, organ annotation, lesion detection, CT/MRI analysis, SAM-based medical image processing, or need to process medical images including CT scans and MRI. Supports command-line inference, Jupyter Notebook tutorials, GUI interface, multi-GPU training, and model fine-tuning.
---

# MedSAM - Medical Image Segmentation Skill

MedSAM is a foundation model for medical image segmentation published in Nature Communications (2024), based on SAM (Segment Anything Model) optimized for medical imaging.

## Core Capabilities

- **Medical Image Segmentation**: Supports organ and lesion segmentation for CT, MRI, and various medical imaging types
- **Interactive Segmentation**: Precise segmentation through bounding box prompts
- **Model Training**: Supports single GPU and multi-GPU training, fine-tuning with custom data
- **Multiple Deployment Options**: Command-line, Jupyter Notebook, GUI interface, and more

## Quick Start

### Environment Setup

```bash
# Create virtual environment
conda create -n medsam python=3.10 -y
conda activate medsam

# Install PyTorch 2.0+
# Visit https://pytorch.org/get-started/locally/ for installation commands

# Clone and install
git clone https://github.com/bowang-lab/MedSAM
cd MedSAM
pip install -e .
```

### Inference Methods

**1. Command Line Inference (Demo Image)**
```bash
python MedSAM_Inference.py
```

**2. Command Line Inference (Custom Image)**
```bash
python MedSAM_Inference.py -i <input_image_path> -o <output_directory> --box <bbox_coordinates>
```

**3. Jupyter Notebook**
- Google Colab: https://colab.research.google.com/drive/19WNtRMbpsxeqimBlmJwtd1dzpaIvK2FZ
- Local: See `tutorial_quickstart.ipynb`

**4. GUI Interface**
```bash
pip install PyQt5
python gui.py
```

### Model Download

Download pretrained model: https://drive.google.com/drive/folders/1ETWmi4AiniJeWOt6HAsYgTjYv_fkgzoN

Save to: `work_dir/MedSAM/medsam_vit_b`

## Training Pipeline

### Data Preprocessing

1. Download SAM checkpoint:
   https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth
   → `work_dir/SAM/sam_vit_b_01ec64.pth`

2. Download demo dataset:
   https://zenodo.org/record/7860267 (50 abdominal CT scans)
   → `data/FLARE22Train/`

3. Install dependencies and preprocess:
```bash
pip install connected-components-3d
python pre_CT_MR.py
```

Preprocessing includes:
- 80/20 train/test split
- CT windowing (level 40, width 400)
- Max-min normalization
- Resample to 1024x1024
- Save as .npy files

### Training Commands

**Multi-GPU Training (Recommended)**
```bash
sbatch train_multi_gpus.sh
```

**Single GPU Training**
```bash
python train_one_gpu.py
```

### Checkpoint Conversion

After training, convert to SAM format:
```bash
python utils/ckpt_convert.py
```

## Common Tasks

### Segment Specific Organs

1. Prepare medical images containing target organs
2. Use bounding box to annotate target region
3. Run inference to get segmentation results

### Batch Processing Medical Images

Modify `MedSAM_Inference.py` to iterate through image directory for batch inference

### Fine-tune with Custom Dataset

1. Prepare data following `pre_CT_MR.py` format
2. Adjust training parameters
3. Fine-tune model with custom data

## Related Resources

- MedSAM2 (3D/Video Segmentation): https://github.com/bowang-lab/MedSAM2
- LiteMedSAM (Accelerated Version): https://github.com/bowang-lab/LiteMedSAM
- 3D Slicer Plugin: https://github.com/bowang-lab/MedSAMSlicer

## Citation

```bibtex
@article{MedSAM,
  title={Segment Anything in Medical Images},
  author={Ma, Jun and He, Yuting and Li, Feifei and Han, Lin and You, Chenyu and Wang, Bo},
  journal={Nature Communications},
  volume={15},
  pages={654},
  year={2024}
}
```

## Technical Specifications

- **Base Model**: SAM ViT-B
- **Python Version**: 3.10+
- **Dependencies**: PyTorch 2.0+
- **Hardware**: CUDA-capable GPU (recommended)
- **License**: Apache-2.0
