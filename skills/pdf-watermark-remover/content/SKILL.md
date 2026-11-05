---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: b39905cd9ef41bf5c0356f5ab45368c9
    PropagateID: b39905cd9ef41bf5c0356f5ab45368c9
    ReservedCode1: 3044022006fd8b05f41e9edc16cc63bea4484e6fc70e9cb79eeef3a5c418cfe3b2a195cc02200b0f0cb88fc983a5a7652c075b2088b2f92cd7429a9b5bfc1caae4142554bf99
    ReservedCode2: 3046022100edaa991ac48e45b27a039e5eac1f74bb680ea091a602e875302f07142b4940f00221009ffdb89bd287abe9e92cff4cdc2a2dccb4fa8c47c124437c0cfb67d02fef8274
description: Remove watermarks from PDF files. Use when users ask to remove watermark from PDF, remove watermarks, clear PDF watermark, or similar requests.
name: pdf-watermark-remover
---

# PDF Watermark Remover

Remove watermarks from PDF files using pypdf library with regex pattern matching.

## Workflow

1. **Input Validation**
   - Verify input file exists and is PDF format
   - Confirm output path is valid

2. **Watermark Removal Processing**
   - Read PDF using `pypdf.PdfReader`
   - Iterate through each page's `/Contents` objects
   - Match watermark patterns using regex:
     - `/Artifact <<Subtype /Watermark.*>> BDC...EMC`
     - `Watermark /Type /Pagination >> BDC...EMC`
   - Remove matched watermark code via `re.sub`
   - Write new PDF using `pypdf.PdfWriter`

3. **Output Confirmation**
   - Verify output file generated successfully
   - Report number of pages processed

## Dependencies

```
pypdf>=3.0.0
```

## Usage

### Command Line

```bash
python remove_watermark.py input.pdf output.pdf
```

### Python API

```python
from remove_watermark import remove_watermark

remove_watermark("input.pdf", "output.pdf")
```

## Limitations

- Only processes Artifact-type watermarks
- Only processes PDF content stream watermarks
- Cannot remove image watermarks or vector graphics watermarks
