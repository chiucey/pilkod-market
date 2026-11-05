# MedSAM Training Guide

## Data Preparation

### Download Demo Dataset

Dataset: https://zenodo.org/record/7860267
- 50 abdomen CT scans
- 13 organ annotations each
- Unzip to: `data/FLARE22Train/`

### Data Preprocessing

```bash
python pre_CT_MR.py
```

Preprocessing pipeline:
1. Train/test split (80/20)
2. CT windowing: level 40, width 400 (soft tissue)
3. Max-min normalization
4. Resample to 1024x1024
5. Save as .npy files

## Training Configuration

### Multi-GPU Training (Recommended)

Hardware: 5 A100 nodes, 4 GPUs each (20 A100 GPUs total, 80GB per GPU)

```bash
sbatch train_multi_gpus.sh
```

### Single GPU Training

```bash
python train_one_gpu.py
```

### Training Parameters

Key parameters in `train_one_gpu.py`:
- Learning rate
- Batch size
- Number of epochs
- Image size
- Data augmentation settings

## Checkpoint Management

### Convert Checkpoint Format

After training, convert to SAM format:
```bash
python utils/ckpt_convert.py
```

### Load Pretrained MedSAM

```python
import torch
from segment_anything import sam_model_registry

sam = sam_model_registry['vit_b'](checkpoint='work_dir/MedSAM/medsam_vit_b/medsam_vit_b.pth')
```

## Fine-tuning Tips

1. Start with MedSAM pretrained weights
2. Use lower learning rate for fine-tuning
3. Apply data augmentation
4. Monitor validation metrics
5. Use early stopping

## Performance Optimization

- Enable mixed precision training (FP16)
- Use gradient checkpointing
- Optimize data loading with multiple workers
- Enable channel last memory format
