#!/usr/bin/env python3
"""
JPG to WEBP Batch Converter
Batch convert JPG/JPEG images to high-quality WEBP format
Preserving original clarity and quality
"""

import os
import sys
from pathlib import Path
from PIL import Image


def convert_jpg_to_webp(input_path, output_path=None, quality=95):
    """
    Convert a single JPG image to WEBP format

    Args:
        input_path: Input JPG file path
        output_path: Output WEBP file path (optional)
        quality: Quality parameter 1-100, default 95 for high clarity

    Returns:
        bool: Whether conversion was successful
    """
    try:
        # Open the image
        with Image.open(input_path) as img:
            # Convert to RGB mode (WEBP doesn't support some RGBA modes)
            if img.mode in ('RGBA', 'LA', 'P'):
                # For images with alpha channel, convert to RGB
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # Determine output path
            if output_path is None:
                output_path = str(Path(input_path).with_suffix('.webp'))

            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

            # Save as WEBP format with high quality settings
            img.save(
                output_path,
                'WEBP',
                quality=quality,
                method=6  # Highest quality compression method
            )

            return True

    except Exception as e:
        print(f"Conversion failed {input_path}: {e}")
        return False


def batch_convert(input_path, output_dir=None, quality=95):
    """
    Batch convert JPG images to WEBP format

    Args:
        input_path: Input file or directory path
        output_dir: Output directory (optional)
        quality: Quality parameter 1-100

    Returns:
        tuple: (success_count, fail_count)
    """
    input_path = Path(input_path)
    jpg_files = []

    # Collect all JPG files
    if input_path.is_file():
        if input_path.suffix.lower() in ['.jpg', '.jpeg']:
            jpg_files = [input_path]
    elif input_path.is_dir():
        for ext in ['.jpg', '.jpeg', '.JPG', '.JPEG']:
            jpg_files.extend(input_path.glob(f'*{ext}'))

    if not jpg_files:
        print(f"No JPG files found: {input_path}")
        return 0, 0

    # Batch convert
    success_count = 0
    fail_count = 0

    for jpg_file in jpg_files:
        # Determine output path
        if output_dir:
            output_path = Path(output_dir) / jpg_file.with_suffix('.webp').name
        else:
            output_path = jpg_file.with_suffix('.webp')

        print(f"Converting: {jpg_file.name} -> {output_path.name}")

        if convert_jpg_to_webp(str(jpg_file), str(output_path), quality):
            success_count += 1
        else:
            fail_count += 1

    return success_count, fail_count


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python jpg_to_webp.py <input-directory-or-file> [output-directory] [quality]")
        print("  input-directory-or-file: JPG file or directory containing JPG files")
        print("  output-directory: Optional, directory for WEBP output files")
        print("  quality: Optional, 1-100, default 95 (high clarity)")
        print("\nExamples:")
        print("  python jpg_to_webp.py ./photos")
        print("  python jpg_to_webp.py ./photos ./output")
        print("  python jpg_to_webp.py photo.jpg ./output 90")
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    quality = int(sys.argv[3]) if len(sys.argv) > 3 else 95

    # Validate quality parameter
    if quality < 1 or quality > 100:
        print("Error: Quality parameter must be between 1-100")
        sys.exit(1)

    print(f"Starting batch conversion JPG to WEBP (quality: {quality}%)")
    print("-" * 50)

    success, fail = batch_convert(input_path, output_dir, quality)

    print("-" * 50)
    print(f"Conversion complete: {success} succeeded, {fail} failed")

    if success > 0:
        print(f"\nWEBP files saved to: {output_dir or 'source directory'}")


if __name__ == '__main__':
    main()
