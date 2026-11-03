#!/usr/bin/env python3
"""
Document to Image Converter
Supports: txt, docx, doc, pdf -> jpg, jpeg, png, gif
"""

import os
import sys
import json
import argparse
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Import document processing libraries
try:
    import docx
except ImportError:
    docx = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None


SUPPORTED_INPUT_FORMATS = ['.txt', '.docx', '.doc', '.pdf']
SUPPORTED_OUTPUT_FORMATS = ['.jpg', '.jpeg', '.png', '.gif']
DEFAULT_OUTPUT_FORMAT = 'jpg'
MAX_SIZE_BYTES = 200 * 1024  # 200KB


def validate_input_format(file_path):
    """Validate input file format"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_INPUT_FORMATS:
        return False, f"Unsupported input format: {ext}. Supported: {', '.join(SUPPORTED_INPUT_FORMATS)}"
    return True, None


def validate_output_format(format_str):
    """Validate output format"""
    fmt = format_str.lower()
    if not fmt.startswith('.'):
        fmt = '.' + fmt
    if fmt not in SUPPORTED_OUTPUT_FORMATS:
        return False, f"Unsupported output format: {format_str}. Supported: {', '.join(SUPPORTED_OUTPUT_FORMATS)}"
    return True, fmt


def validate_file_size(file_path):
    """Validate file size"""
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        if size > MAX_SIZE_BYTES:
            size_kb = size / 1024
            max_kb = MAX_SIZE_BYTES / 1024
            return False, f"File size ({size_kb:.1f}KB) exceeds limit ({max_kb:.0f}KB)"
    return True, None


def validate_text_size(text):
    """Validate text size"""
    size_bytes = len(text.encode('utf-8'))
    if size_bytes > MAX_SIZE_BYTES:
        size_kb = size_bytes / 1024
        max_kb = MAX_SIZE_BYTES / 1024
        return False, f"Text size ({size_kb:.1f}KB) exceeds limit ({max_kb:.0f}KB)"
    return True, None


def extract_text_from_txt(file_path):
    """Extract text from txt file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read(), None
    except Exception as e:
        return None, f"Failed to read txt file: {str(e)}"


def extract_text_from_docx(file_path):
    """Extract text from docx file"""
    if docx is None:
        return None, "python-docx library not installed"
    try:
        doc = docx.Document(file_path)
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return '\n'.join(paragraphs), None
    except Exception as e:
        return None, f"Failed to read docx file: {str(e)}"


def extract_text_from_pdf(file_path):
    """Extract text from pdf file"""
    if pdfplumber is None:
        return None, "pdfplumber library not installed"
    try:
        text_parts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        return '\n\n'.join(text_parts), None
    except Exception as e:
        return None, f"Failed to read pdf file: {str(e)}"


def extract_text(file_path):
    """Extract text based on file type"""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.txt':
        return extract_text_from_txt(file_path)
    elif ext in ['.docx', '.doc']:
        return extract_text_from_docx(file_path)
    elif ext == '.pdf':
        return extract_text_from_pdf(file_path)
    else:
        return None, f"Unsupported file format: {ext}"


def get_font():
    """Get available font"""
    font_paths = [
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttk',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        '/System/Library/Fonts/PingFang.ttc',  # macOS
        'C:/Windows/Fonts/msyh.ttc',  # Windows
    ]

    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, 24)
            except:
                try:
                    return ImageFont.truetype(path, 20)
                except:
                    continue

    return ImageFont.load_default()


def text_to_image(text, output_path, output_format='jpg', width=1200):
    """Convert text to image"""
    font = get_font()

    # Create temp image for measurement
    temp_img = Image.new('RGB', (1, 1), color='white')
    temp_draw = ImageDraw.Draw(temp_img)

    # Calculate required image height
    margin = 40
    line_spacing = 10
    max_width = width - 2 * margin

    lines = []
    for paragraph in text.split('\n'):
        if not paragraph.strip():
            lines.append('')
            continue

        # Smart line wrapping
        words = paragraph
        current_line = ''

        for char in words:
            test_line = current_line + char
            bbox = temp_draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]

            if text_width > max_width:
                if current_line:
                    lines.append(current_line)
                    current_line = char
                else:
                    # Single char too wide, force wrap
                    lines.append(char)
                    current_line = ''
            else:
                current_line = test_line

        if current_line:
            lines.append(current_line)

    # Calculate total height
    line_height = temp_draw.textbbox((0, 0), 'Test', font=font)[3] - temp_draw.textbbox((0, 0), 'Test', font=font)[1] + line_spacing
    total_height = len(lines) * line_height + 2 * margin

    # Ensure minimum height
    total_height = max(total_height, 200)

    # Create final image
    img = Image.new('RGB', (width, total_height), color='white')
    draw = ImageDraw.Draw(img)

    # Draw text
    y = margin
    for line in lines:
        if line:  # Draw non-empty lines
            draw.text((margin, y), line, fill='black', font=font)
        y += line_height

    # Save image
    fmt = output_format.upper().replace('.', '')
    if fmt == 'JPG':
        fmt = 'JPEG'
    img.save(output_path, fmt)
    return True


def generate_output_name(input_path, output_format):
    """Generate output filename"""
    if input_path:
        # Use original document name
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        # Limit name length
        if len(base_name) > 30:
            base_name = base_name[:27] + '...'
    else:
        # Use date format
        date_str = datetime.now().strftime('%Y%m%d')
        base_name = f'pic_{date_str}'

    return f"{base_name}.{output_format.lstrip('.')}"


def convert(input_source, output_path=None, output_format=None, text_input=None):
    """
    Main conversion function

    Args:
        input_source: Input file path (str) or None (text input)
        output_path: Output file path (optional)
        output_format: Output format (optional, default jpg)
        text_input: Direct text content

    Returns:
        (success, result, error)
    """
    # Handle output format
    if output_format:
        valid, fmt = validate_output_format(output_format)
        if not valid:
            return False, None, fmt
        output_format = fmt
    else:
        output_format = '.jpg'

    text = None

    # Handle input
    if text_input is not None:
        # Text input
        text = text_input
        valid, error = validate_text_size(text)
        if not valid:
            return False, None, error
        input_source = None
    elif input_source:
        # File input
        if not os.path.exists(input_source):
            return False, None, f"File not found: {input_source}"

        # Validate format
        valid, error = validate_input_format(input_source)
        if not valid:
            return False, None, error

        # Validate size
        valid, error = validate_file_size(input_source)
        if not valid:
            return False, None, error

        # Extract text
        text, error = extract_text(input_source)
        if error:
            return False, None, error
    else:
        return False, None, "Please provide input file or text content"

    # Generate output path
    if not output_path:
        output_path = generate_output_name(input_source, output_format)

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Convert to image
    try:
        success = text_to_image(text, output_path, output_format.lstrip('.'))
        if success:
            return True, output_path, None
        else:
            return False, None, "Image generation failed"
    except Exception as e:
        return False, None, f"Conversion failed: {str(e)}"


def main():
    parser = argparse.ArgumentParser(description='Document to Image Tool')
    parser.add_argument('--input', '-i', help='Input file path')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--format', '-f', default='jpg', help='Output format (jpg, png, gif)')
    parser.add_argument('--text', '-t', help='Direct text input')

    args = parser.parse_args()

    success, result, error = convert(
        input_source=args.input,
        output_path=args.output,
        output_format=args.format,
        text_input=args.text
    )

    output = {
        'success': success,
        'result': result,
        'error': error
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
