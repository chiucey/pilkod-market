---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: cd00375dab6ce4f4fa4240444e833af5
    PropagateID: cd00375dab6ce4f4fa4240444e833af5
    ReservedCode1: 3046022100f47f6047b64797f356a7d34fb2d6cc39f29812c187c52310353b971af0be18f7022100f92464de0f257073da011527daff891adc08debd7c49347888daf589d32259b2
    ReservedCode2: 3046022100a07f41cb82dea41ec2617b88f35a25b0c363c2b6334de24439b1ab355b897d00022100d9ef2f8806566f91467ea86087212d2a922b6ff7ad6b8cf748465450fb3915ce
description: Convert Markdown (MD) files to Microsoft Word (DOCX) format. Use when users ask to convert md files to word, convert markdown to docx, or export markdown as office documents.
name: md-to-docx
---

# MD to DOCX Converter

A professional tool for converting Markdown files to Microsoft Word (DOCX) format.

## Features

- Convert standard Markdown syntax to DOCX
- Preserve heading hierarchy (H1-H6)
- Support code blocks, lists, tables, blockquotes and other elements
- Support image embedding (requires local image paths)
- Customizable output filename and styles

## Technical Solution

Uses `pandoc` for conversion - the most professional document format converter supporting high-quality Markdown to DOCX conversion.

## Dependencies

```bash
pip install pymdown-extensions
```

## Conversion Script

```python
#!/usr/bin/env python3
"""
Markdown to DOCX Converter
Usage: python md_to_docx.py <input.md> [output.docx]
"""

import subprocess
import sys
import os
from pathlib import Path


def md_to_docx(input_file, output_file=None, reference_file=None):
    """
    Convert Markdown file to DOCX format

    Args:
        input_file: Input Markdown file path
        output_file: Output DOCX file path (optional, defaults to input filename)
        reference_file: Reference style file path (optional, for custom styles)

    Returns:
        Path to the converted DOCX file
    """
    input_path = Path(input_file)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # If output not specified, use input filename
    if output_file is None:
        output_file = input_path.with_suffix('.docx')
    else:
        output_file = Path(output_file)

    # Build pandoc command
    cmd = [
        'pandoc',
        str(input_path),
        '-o', str(output_file),
        '--from=markdown',
        '--to=docx'
    ]

    # Add reference style file if provided
    if reference_file and os.path.exists(reference_file):
        cmd.extend(['--reference-doc', reference_file])

    # Execute conversion
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"Conversion successful: {output_file}")
        return str(output_file)
    except subprocess.CalledProcessError as e:
        print(f"Conversion failed: {e.stderr}")
        raise


def batch_convert(input_dir, output_dir=None, pattern='*.md'):
    """
    Batch convert Markdown files

    Args:
        input_dir: Input directory
        output_dir: Output directory (defaults to input directory)
        pattern: File matching pattern
    """
    input_path = Path(input_dir)

    if output_dir is None:
        output_dir = input_dir
    else:
        os.makedirs(output_dir, exist_ok=True)

    md_files = list(input_path.glob(pattern))

    if not md_files:
        print(f"No Markdown files found in {input_dir}")
        return

    print(f"Found {len(md_files)} Markdown files")

    for md_file in md_files:
        output_file = Path(output_dir) / md_file.with_suffix('.docx').name
        try:
            md_to_docx(md_file, output_file)
        except Exception as e:
            print(f"Error converting {md_file.name}: {e}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python md_to_docx.py <input.md> [output.docx]")
        print("Or: python md_to_docx.py --batch <input_dir> [output_dir]")
        sys.exit(1)

    if sys.argv[1] == '--batch':
        input_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
        output_dir = sys.argv[3] if len(sys.argv) > 3 else None
        batch_convert(input_dir, output_dir)
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        md_to_docx(input_file, output_file)
```

## Usage

### Single File Conversion

```bash
python md_to_docx.py input.md output.docx
```

### Batch Conversion

```bash
python md_to_docx.py --batch ./markdown_files/ ./output_files/
```

### In Python Code

```python
from md_to_docx import md_to_docx

# Single file conversion
docx_path = md_to_docx('input.md', 'output.docx')

# With custom style
docx_path = md_to_docx('input.md', 'output.docx', 'custom-reference.docx')
```

## Advanced Usage

### Custom DOCX Styles

Create a reference style file to define output document styles:

1. Create a document with custom styles in Word
2. Save it as `reference.docx`
3. Use the reference file for conversion:

```python
md_to_docx('input.md', 'output.docx', 'reference.docx')
```

### Supported Markdown Features

| Markdown Element | DOCX Output |
|-----------------|-------------|
| `# Heading` | Heading 1-6 |
| `**Bold**` | Bold |
| `*Italic*` | Italic |
| `- List` | Bullet list |
| `1. List` | Numbered list |
| `> Quote` | Block quote |
| `` `Code` `` | Inline code |
| ``` ```code block``` ``` | Code block |
| `[Link](url)` | Hyperlink |
| `![Image](path)` | Image |
| `\| Table \|` | Word table |

## Notes

1. **Image Handling**: Ensure images use relative paths and are in the same directory as the MD file
2. **Encoding**: Use UTF-8 encoded Markdown files for best compatibility
3. **Pandoc Installation**: Ensure pandoc is installed (`brew install pandoc` or download from official site)

## Troubleshooting

- **Conversion Failed**: Check if pandoc is installed
- **Style Lost**: Try using a reference style file
- **Images Not Displaying**: Ensure image paths are correct and files exist
