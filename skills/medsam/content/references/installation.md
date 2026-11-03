# MedSAM Installation Guide

## Full Installation Steps

### 1. Environment Setup

```bash
# Create conda environment
conda create -n medsam python=3.10 -y
conda activate medsam

# Install PyTorch 2.0+ with CUDA support
# Visit https://pytorch.org/get-started/locally/
# Example command:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 2. Clone Repository

```bash
git clone https://github.com/bowang-lab/MedSAM
cd MedSAM
```

### 3. Install Package

```bash
pip install -e .
```

### 4. Install Additional Dependencies

```bash
# For GUI
pip install PyQt5

# For training
pip install connected-components-3d

# For data processing
pip install SimpleITK nibabel
```

### 5. Download Models

**MedSAM Model:**
- URL: https://drive.google.com/drive/folders/1ETWmi4AiniJeWOt6HAsYgTjYv_fkgzoN
- Save to: `work_dir/MedSAM/medsam_vit_b`

**SAM Checkpoint (for training):**
- URL: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth
- Save to: `work_dir/SAM/sam_vit_b_01ec64.pth`

### 6. Verify Installation

```bash
python MedSAM_Inference.py
```

## Troubleshooting

### Common Issues

**1. CUDA Out of Memory**
- Reduce batch size
- Use LiteMedSAM for faster inference

**2. PyQt5 Installation Failed**
- Try: `conda install -c anaconda pyqt`

**3. Model Download Failed**
- Use wget or browser to download
- Ensure sufficient disk space

**4. Import Errors**
- Verify all dependencies installed
- Check Python version (3.10+)
