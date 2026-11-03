---
name: jpg-to-webp-converter
description: Batch convert JPG/JPEG images to WEBP format. Use when users request batch image format conversion, JPG to WEBP, image compression optimization, or quality-preserving conversion.
---

# JPG to WEBP Batch Converter

Batch convert JPG/JPEG images to high-quality WEBP format.

## Usage

Provide JPG image files to convert, and the skill will automatically batch convert them to WEBP format.

## Processing Flow

1. **Receive Images** - Get JPG/JPEG files from user
2. **Quality Settings** - Use high-quality parameters (95% quality) to ensure clarity
3. **Batch Convert** - Convert each to WEBP format
4. **Output Results** - Generate .webp files with the same name

## Quality Assurance

- **Quality Parameter**: 95% quality retention
- **Lossless Conversion**: Preserve all details of original images
- **Metadata Retention**: Keep EXIF and other important metadata

## Conversion Script Usage

```bash
python scripts/jpg_to_webp.py <input-directory-or-file> [output-directory]
```

## Parameters

- `<input-directory-or-file>`: JPG file path or directory containing JPG files
- `[output-directory]`: Optional, WEBP file output directory (default: same location as source file)
