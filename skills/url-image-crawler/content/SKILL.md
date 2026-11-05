---
name: url-image-crawler
description: |
  Extract and download all images from any URL (webpages, PDFs, Word docs, PPTs, etc.). Supports HTML webpages, PDF documents, Word documents, and PPT presentations.
  Use when users ask to:
  - Crawl images, download webpage images, extract document images
  - Provide a link and ask to save images
  - Image collection, batch download images
  - Download all images from a webpage or document
---

# URL Image Crawler Skill

Extract and download all images from a specified URL to a local directory.

## Usage

```bash
# Basic usage
bash scripts/crawl_images.sh <URL> [target-directory]

# Example: Crawl webpage images
bash scripts/crawl_images.sh "https://example.com/article"

# Example: Crawl PDF images
bash scripts/crawl_images.sh "https://example.com/doc.pdf"

# Example: Specify save directory
bash scripts/crawl_images.sh "https://example.com" ~/Downloads/images
```

## Output Rules

- **Directory naming**: Automatically creates subdirectory named after URL (e.g., `example_com_article`)
- **File naming**: `sequence_source-type.jpg` (e.g., `01_img.jpg`, `03_pdf.png`)
- Supported formats: jpg, jpeg, png, gif, webp, svg, ico

## Supported Document Types

| Type | Extension | Description |
|------|-----------|-------------|
| Webpage | .html, .htm | Parses all `<img>`, CSS background images, base64 images |
| PDF | .pdf | Extracts embedded images |
| Word | .docx | Parses images from document.xml |
| PPT | .pptx | Parses images from slide*.xml |

## Dependencies

- `curl` - Download webpage content
- `python3` - Process documents and images
- `unzip` - Decompress Office documents
- `pdfimages` (optional) - PDF image extraction, falls back to Python if not installed
