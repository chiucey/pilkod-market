#!/usr/bin/env python3
"""
Markdown to DOCX Converter
Convert Markdown files to Microsoft Word (DOCX) format

Usage:
    python md_to_docx.py <input.md> [output.docx]
    python md_to_docx.py --batch <input_dir> [output_dir]

Dependencies:
    pip install pymdown-extensions

    Also requires pandoc to be installed:
    - macOS: brew install pandoc
    - Linux: sudo apt install pandoc
    - Windows: Download from https://pandoc.org/installing.html
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

    Raises:
        FileNotFoundError: When input file does not exist
        subprocess.CalledProcessError: When pandoc conversion fails
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
        error_msg = e.stderr if e.stderr else "Unknown error"
        print(f"Conversion failed: {error_msg}")
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

    success_count = 0
    for md_file in md_files:
        output_file = Path(output_dir) / md_file.with_suffix('.docx').name
        try:
            md_to_docx(md_file, output_file)
            success_count += 1
        except Exception as e:
            print(f"Error converting {md_file.name}: {e}")

    print(f"\nBatch conversion complete: {success_count}/{len(md_files)} successful")


def main():
    """Main function, handles command line arguments"""
    if len(sys.argv) < 2:
        print("Markdown to DOCX Converter")
        print("=" * 40)
        print("Usage:")
        print("  Single file: python md_to_docx.py <input.md> [output.docx]")
        print("  Batch:       python md_to_docx.py --batch <input_dir> [output_dir]")
        print("\nExamples:")
        print("  python md_to_docx.py readme.md readme.docx")
        print("  python md_to_docx.py --batch ./docs/ ./output/")
        sys.exit(1)

    if sys.argv[1] == '--batch':
        input_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
        output_dir = sys.argv[3] if len(sys.argv) > 3 else None
        batch_convert(input_dir, output_dir)
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        md_to_docx(input_file, output_file)


if __name__ == '__main__':
    main()
