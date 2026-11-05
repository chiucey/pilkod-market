# MedSAM Inference Guide

## Basic Inference

### Command Line

```bash
# Segment demo image
python MedSAM_Inference.py

# With custom image
python MedSAM_Inference.py -i <input_image> -o <output_path>

# With bounding box
python MedSAM_Inference.py -i <input_image> -o <output_path> --box x1 y1 x2 y2
```

### Python API

```python
import numpy as np
import torch
from segment_anything import sam_model_registry, SamPredictor

# Load model
sam = sam_model_registry['vit_b'](
    checkpoint='work_dir/MedSAM/medsam_vit_b/medsam_vit_b.pth'
)
predictor = SamPredictor(sam)

# Set image
image = np.array(...)  # Your medical image
predictor.set_image(image)

# Get segmentation with bounding box prompt
box = np.array([x1, y1, x2, y2])
masks, scores, logits = predictor.predict(
    point_coords=None,
    point_labels=None,
    box=box,
    multimask_output=False
)
```

## Medical Image Formats

### CT/MRI Loading

```python
import SimpleITK as sitk

# Load CT/MRI
image = sitk.ReadImage('path/to/image.nii.gz')
image_array = sitk.GetArrayFromImage(image)

# Preprocess
image_array = preprocess_medical_image(image_array)
```

### Supported Formats

- DICOM (.dcm)
- NIfTI (.nii, .nii.gz)
- NRRD (.nrrd)
- PNG/JPEG for 2D images
- Medical formats via SimpleITK

## Advanced Usage

### Multiple Points Prompt

```python
# Multiple foreground points
point_coords = np.array([[x1, y1], [x2, y2], [x3, y3]])
point_labels = np.array([1, 1, 1])

masks, scores, logits = predictor.predict(
    point_coords=point_coords,
    point_labels=point_labels,
    multimask_output=True
)
```

### Mask Refinement

```python
# Use low confidence mask areas as new prompts
uncertain_mask = mask_scores < threshold
# Extract center points from uncertain regions
# Re-predict with new points
```

## Batch Processing

```python
import os
from pathlib import Path

input_dir = 'path/to/images/'
output_dir = 'path/to/output/'

for img_path in Path(input_dir).glob('*'):
    # Process each image
    result = process_single_image(img_path)
    save_result(result, output_dir / img_path.name)
```

## GUI Usage

```bash
pip install PyQt5
python gui.py
```

Features:
- Load medical images
- Draw bounding boxes
- Interactive segmentation
- Export masks

## Output Formats

### Mask Export

```python
import numpy as np

# Binary mask
mask = masks[0].astype(np.uint8)

# Save as PNG
from PIL import Image
Image.fromarray(mask * 255).save('mask.png')

# Save as NPY for further processing
np.save('mask.npy', mask)
```

## Performance Tips

1. Use GPU for faster inference
2. Resize large images to optimal size
3. Use LiteMedSAM for real-time applications
4. Batch process multiple images
5. Cache model in memory
