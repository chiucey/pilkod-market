---
name: doc-to-image
description: Document to image conversion skill. Use when users ask to convert text, Word documents, or PDF files to images. Triggers include: convert text to image, convert document to image, word to image, pdf to image, text to image, document to image, txt to image. Supported input: txt, pdf, word; output: jpg, jpeg, png, gif.
---

# Document to Image Skill

## Overview

Convert text, Word documents, or PDF files to image formats.

## Supported Formats

### Input Formats
- **Plain text**: `.txt`
- **Word documents**: `.docx`, `.doc`
- **PDF files**: `.pdf`

### Output Formats
- **Image formats**: `.jpg`, `.jpeg`, `.png`, `.gif`
- **Default format**: `.jpg` if not specified

## Size Limits

- **Text input**: Max 200KB
- **Document input**: Max 200KB

## Output Filename Rules

1. **With document**: Use original document name (max 30 chars) + image extension
2. **Text only**: Use `pic_YYYYMMDD` format + image extension

## Workflow

### Step 1: Format Validation
- Check if input format is supported (txt, pdf, word)
- Check if output format is supported (jpg, jpeg, png, gif)
- Return error if format not supported

### Step 2: Size Validation
- Text content must be under 200KB
- Document files must be under 200KB
- Return error if limit exceeded

### Step 3: Content Extraction
- **txt files**: Read text directly
- **word files**: Extract all text paragraphs
- **pdf files**: Extract all text content

### Step 4: Image Generation
- Use Python script to generate image
- Save in specified format
- Return image path to user

## Error Handling

| Error Type | Handling |
|-----------|----------|
| Unsupported input format | List supported formats |
| Unsupported output format | List supported formats |
| Content too large | Explain size limit |
| File read failure | Request user check file |
| Image generation failure | Request retry |

## Usage Examples

### Example 1: Text to Image
```
User: Convert this text to image: "Hello World"
Result: Generate pic_20260430.jpg
```

### Example 2: Word to JPG
```
User: Convert this word doc to jpg [upload file.docx]
Result: Generate document.jpg
```

### Example 3: PDF to PNG
```
User: Convert this PDF to png [upload file.pdf]
Result: Generate file_name.png
```

### Example 4: Specify Output Format
```
User: Convert document to jpeg image
Result: Generate [original_name].jpeg
```

## Technical Implementation

Uses Python script `doc_to_image.py` for conversion:
- Pillow for image creation
- python-docx for Word document parsing
- pdfplumber for PDF parsing
- Auto text wrapping
- Supports mixed Chinese and English
