---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304502206b20c299f15a8c2ff7ac56235454d7b37993bf8be9fdb2578595a7c425270e24022100aa8c5c11d0c7340e2cb60e370268be5f9aa6ca159550b6156753282a7a2f66a0
    ReservedCode2: 3046022100d558fcda86e90227637abbb9e8d8799de61b3a446e65238f3ba50902ebb66c51022100801393bc4ba388ad6657d0bbfa3b11cda1a92f1939ee079b11a48a2dbc4b9c4a
---

# Watermark Remover

Remove watermarks from images and videos using advanced AI-powered inpainting and detection techniques.

## Supported Capabilities

| Type | Operations |
|------|------------|
| **Image Watermarks** | Logo removal, text overlay removal, signature removal, corner watermarks, transparent watermarks |
| **Video Watermarks** | Frame-by-frame removal, moving watermark tracking, timestamp removal |
| **Hidden Watermarks** | Steganography detection, forensic analysis, invisible watermarks identification |

## Image Watermark Removal Workflow

### Step 1: Analyze Watermark Type

**Detection Prompts:**
- `"Identify all watermarks in the image"`
- `"Find text overlays and logos"`
- `"Detect transparent/semi-transparent watermarks"`

**Watermark Types:**
- `text`: Text-based watermarks (copyright notices, timestamps)
- `logo`: Logo or brand marks (usually in corners)
- `semi_transparent`: Semi-transparent overlays (TV channel logos)
- `pattern`: Repeated pattern watermarks

### Step 2: Select Removal Method

| Watermark Type | Primary Method | Fallback Method |
|----------------|----------------|-----------------|
| Small text/logo | Localized inpainting | Content-aware fill |
| Large text overlay | Generative AI fill | Background texture synthesis |
| Semi-transparent | Alpha blending removal | Frequency domain filtering |
| Pattern watermark | Fourier transform filtering | Template matching + removal |

### Step 3: Execute Removal

**Using Image Inpainting:**
```python
# For visible watermarks - use inpainting
result = await image_inpaint(
    image_path=input_path,
    mask_path=watermark_mask,
    prompt="original image without watermark"
)
```

**Using Frequency Domain (Pattern Watermarks):**
```python
# For repeated pattern watermarks
from scipy.fft import fft2, ifft2

def remove_pattern_watermark(image):
    f_transform = fft2(image)
    f_shift = np.fft.fftshift(f_transform)
    # Filter out watermark frequencies
    # ...
    return np.real(ifft2(np.fft.ifftshift(filtered)))
```

### Step 4: Post-Processing

- **Quality check**: Verify watermark removal is complete
- **Color correction**: Match surrounding areas if color shift occurred
- **Seam blending**: Ensure natural transitions at edges

## Video Watermark Removal Workflow

### Step 1: Analyze Video Content

**Detection Prompts:**
- `"Locate all watermarks across video frames"`
- `"Track moving watermarks"`
- `"Identify static and dynamic watermarks"`

### Step 2: Select Video Removal Strategy

| Scenario | Strategy |
|----------|----------|
| Static watermark (all frames same position) | Batch inpainting |
| Moving watermark (tracked position) | Optical flow + temporal consistency |
| Timestamp (clock-style) | Regenerate clean timestamp |
| Channel logo (semi-transparent) | Alpha matting + blending |

### Step 3: Frame-by-Frame Processing

```python
# Video watermark removal pipeline
def remove_video_watermark(video_path, watermark_regions):
    cap = cv2.VideoCapture(video_path)
    frames = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        for region in watermark_regions:
            # Apply inpainting per frame
            inpainted_frame = inpaint_frame(frame, region)

        frames.append(inpainted_frame)

    cap.release()
    return frames  # Re-encode to video
```

### Step 4: Temporal Consistency

- **Inter-frame smoothing**: Prevent flickering
- **Motion compensation**: Match inpainting across frames
- **Final encode**: Apply codec (H.264/H.265) with quality settings

## Hidden Watermark Workflow

### Step 1: Steganography Detection

**Tools & Techniques:**
- LSB (Least Significant Bit) analysis
- DCT coefficient analysis (JPEG)
- Frequency domain analysis
- Metadata inspection

### Step 2: Watermark Extraction/Identification

```python
# LSB Steganography Detection
def detect_lsb_watermark(image_path):
    image = Image.open(image_path)
    pixels = np.array(image)

    # Extract LSBs
    lsb_bits = pixels & 1

    # Analyze for hidden patterns
    hidden_data = []
    for bit_plane in range(3):  # RGB channels
        # Check for non-random patterns
        pass

    return hidden_data
```

### Step 3: Hidden Watermark Removal (If Requested)

**Note:** Hidden watermark removal may not be feasible without knowing the embedding algorithm. Provide:
- Watermark identification report
- Removal feasibility assessment
- Alternative: Watermark visibility reduction

## Quality Validation

### Image Validation Checklist
- [ ] Watermark fully removed (visual inspection)
- [ ] No visible artifacts at removal site
- [ ] Color consistency with surrounding areas
- [ ] No resolution loss or blurring
- [ ] File integrity preserved (format, metadata)

### Video Validation Checklist
- [ ] All watermark instances removed
- [ ] No frame-to-frame flickering
- [ ] Smooth motion maintained
- [ ] Audio sync preserved
- [ ] Consistent bitrate/quality

## Usage Examples

### Example 1: Remove Logo from Photo
```
User: Remove the logo from the corner of this image
→ Analyze image → Detect logo type → Apply inpainting → Output clean image
```

### Example 2: Remove Timestamp from Video
```
User: Clear all timestamps from this video
→ Analyze video frames → Identify timestamp positions → Batch removal → Output clean video
```

### Example 3: Detect Hidden Watermark
```
User: Check if this image contains hidden watermarks
→ Perform steganography analysis → Generate detection report → Present findings
```

## Limitations & Notes

1. **Irreversible Operations**: Watermark removal is destructive; keep original files
2. **Complex Backgrounds**: Intricate backgrounds may show artifacts after removal
3. **Hidden Watermarks**: Removal may not always be possible without original algorithm
4. **Legal Considerations**: Ensure you have rights to modify the content
5. **Quality Degradation**: Some removal operations may affect image/video quality

## Reference Scripts

- `scripts/image_watermark_remover.py` - Image processing utilities
- `scripts/video_watermark_remover.py` - Video processing pipeline
- `scripts/steganography_detector.py` - Hidden watermark detection
- `references/techniques.md` - Detailed removal techniques