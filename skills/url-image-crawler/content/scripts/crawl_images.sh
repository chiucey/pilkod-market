#!/bin/bash
# URL Image Crawler Script
# Usage: bash crawl_images.sh <URL> [target-directory]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
OUTPUT_DIR="${2:-./downloads}"
COUNTER=1

# Check dependencies
check_dependencies() {
    local deps=("curl" "python3" "unzip")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            echo -e "${RED}Error: $dep is not installed${NC}"
            exit 1
        fi
    done
}

# Sanitize filename
sanitize_filename() {
    echo "$1" | sed 's/[^a-zA-Z0-9]/_/g' | cut -c1-50
}

# Download images from HTML
download_html_images() {
    local url="$1"
    local dir="$2"
    local html_file="$dir/temp.html"

    echo -e "${GREEN}Fetching HTML content...${NC}"
    curl -sL "$url" -o "$html_file"

    if [ ! -f "$html_file" ] || [ ! -s "$html_file" ]; then
        echo -e "${RED}Error: Failed to download content from $url${NC}"
        return 1
    fi

    # Extract and download images
    python3 << 'PYTHON_SCRIPT'
import os
import re
import urllib.parse
import base64

html_file = os.environ.get('HTML_FILE', 'temp.html')
output_dir = os.environ.get('OUTPUT_DIR', '.')
counter = int(os.environ.get('COUNTER', '1'))

with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

base_url = os.environ.get('URL', '')

# Extract <img> src attributes
img_pattern = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)
images = img_pattern.findall(content)

for img_src in images:
    try:
        if img_src.startswith('data:image'):
            # Handle base64 images
            match = re.match(r'data:image/(\w+);base64,(.+)', img_src)
            if match:
                ext = match.group(1)
                data = match.group(2)
                filename = f"{counter:02d}_base64.{ext}"
                with open(os.path.join(output_dir, filename), 'wb') as imgf:
                    imgf.write(base64.b64decode(data))
                print(f"Downloaded: {filename}")
                counter += 1
        elif img_src.startswith('http'):
            # External URL
            filename = f"{counter:02d}_img.jpg"
            os.system(f'curl -sL "{img_src}" -o "{os.path.join(output_dir, filename)}"')
            print(f"Downloaded: {filename}")
            counter += 1
        elif img_src.startswith('//'):
            # Protocol-relative URL
            filename = f"{counter:02d}_img.jpg"
            os.system(f'curl -sL "https:{img_src}" -o "{os.path.join(output_dir, filename)}"')
            print(f"Downloaded: {filename}")
            counter += 1
        else:
            # Relative URL
            abs_url = urllib.parse.urljoin(base_url, img_src)
            filename = f"{counter:02d}_img.jpg"
            os.system(f'curl -sL "{abs_url}" -o "{os.path.join(output_dir, filename)}"')
            print(f"Downloaded: {filename}")
            counter += 1
    except Exception as e:
        print(f"Error processing {img_src}: {e}")

print(f"TOTAL_IMAGES:{counter - 1}")
PYTHON_SCRIPT

    rm -f "$html_file"
}

# Download images from PDF
download_pdf_images() {
    local url="$1"
    local dir="$2"

    echo -e "${GREEN}Processing PDF...${NC}"

    local pdf_file="$dir/temp.pdf"
    curl -sL "$url" -o "$pdf_file"

    if [ ! -f "$pdf_file" ]; then
        echo -e "${RED}Error: Failed to download PDF${NC}"
        return 1
    fi

    # Try pdfimages first, fallback to Python
    if command -v pdfimages &> /dev/null; then
        cd "$dir"
        pdfimages -all "temp.pdf" "pdf_img"
        rm -f "temp.pdf"
        echo -e "${GREEN}PDF images extracted with pdfimages${NC}"
    else
        # Python fallback
        python3 << 'PYTHON_SCRIPT'
import os
import re

pdf_file = os.environ.get('PDF_FILE', 'temp.pdf')
output_dir = os.environ.get('OUTPUT_DIR', '.')
counter = int(os.environ.get('COUNTER', '1'))

with open(pdf_file, 'rb') as f:
    content = f.read()

# Extract JPEG images from PDF
jpeg_pattern = re.compile(b'\xff\xd8\xff')
positions = [m.start() for m in jpeg_pattern.finditer(content)]

for i, pos in enumerate(positions):
    try:
        # Find JPEG end marker
        end_pos = content.find(b'\xff\xd9', pos + 2)
        if end_pos != -1:
            jpeg_data = content[pos:end_pos + 2]
            filename = f"{counter:02d}_pdf.jpg"
            with open(os.path.join(output_dir, filename), 'wb') as imgf:
                imgf.write(jpeg_data)
            print(f"Extracted: {filename}")
            counter += 1
    except Exception as e:
        print(f"Error extracting JPEG at position {pos}: {e}")

os.remove(pdf_file)
print(f"TOTAL_IMAGES:{counter - 1}")
PYTHON_SCRIPT
    fi
}

# Download images from DOCX/PPTX
download_office_images() {
    local url="$1"
    local dir="$2"
    local ext="$3"

    echo -e "${GREEN}Processing $ext document...${NC}"

    local archive_file="$dir/temp.$ext"
    curl -sL "$url" -o "$archive_file"

    if [ ! -f "$archive_file" ]; then
        echo -e "${RED}Error: Failed to download $ext${NC}"
        return 1
    fi

    # Extract and find images
    local extract_dir="$dir/${ext}_content"
    mkdir -p "$extract_dir"
    unzip -q "$archive_file" -d "$extract_dir"

    # Find all image files
    local img_dir="$dir/images"
    mkdir -p "$img_dir"

    find "$extract_dir" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.gif" -o -iname "*.webp" \) | while read -r img; do
        filename=$(printf "%02d_%s_%s" "$COUNTER" "$ext" "$(basename "$img")")
        cp "$img" "$img_dir/$filename"
        echo "Extracted: $filename"
        ((COUNTER++))
    done

    rm -f "$archive_file"
    rm -rf "$extract_dir"
    echo -e "${GREEN}$ext images extracted successfully${NC}"
}

# Main execution
main() {
    local url="$1"

    if [ -z "$url" ]; then
        echo "Usage: $0 <URL> [目标目录]"
        echo "Example: $0 'https://example.com/page.html' ./images"
        exit 1
    fi

    echo -e "${YELLOW}URL Image Crawler${NC}"
    echo "Target: $url"
    echo "Output: $OUTPUT_DIR"

    # Check dependencies
    check_dependencies

    # Create output directory
    mkdir -p "$OUTPUT_DIR"

    # Determine URL type and process
    if [[ "$url" =~ \.pdf$ ]]; then
        download_pdf_images "$url" "$OUTPUT_DIR"
    elif [[ "$url" =~ \.docx$ ]]; then
        download_office_images "$url" "$OUTPUT_DIR" "docx"
    elif [[ "$url" =~ \.pptx$ ]]; then
        download_office_images "$url" "$OUTPUT_DIR" "pptx"
    else
        download_html_images "$url" "$OUTPUT_DIR"
    fi

    echo -e "${GREEN}Done! Images saved to $OUTPUT_DIR${NC}"
}

main "$@"
