---
name: pdf-merge-split
description: Merge multiple PDF files into one or split a PDF into separate files. Use when the user wants to combine PDFs, split a PDF apart, extract page ranges, or reorganize PDF pages.
---

# PDF Merge & Split

## Quick Start

Use `pypdf` for all PDF merge and split operations.

```bash
pip install pypdf
```

## Merge Multiple PDFs

```python
from pypdf import PdfWriter, PdfReader

output = PdfWriter()
sources = ["file1.pdf", "file2.pdf", "file3.pdf"]

for src in sources:
    reader = PdfReader(src)
    for page in reader.pages:
        output.add_page(page)

with open("merged.pdf", "wb") as dest:
    output.write(dest)
```

## Split PDF into Individual Pages

```python
from pypdf import PdfWriter, PdfReader

source = PdfReader("input.pdf")
for idx, page in enumerate(source.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{idx + 1}.pdf", "wb") as dest:
        writer.write(dest)
```

## Extract Page Range

```python
from pypdf import PdfWriter, PdfReader

source = PdfReader("input.pdf")
output = PdfWriter()

# Extract pages 1-5 (0-indexed: 0 to 4)
for i in range(0, 5):
    output.add_page(source.pages[i])

with open("extracted.pdf", "wb") as dest:
    output.write(dest)
```

## CLI Alternative (qpdf)

For simple merges without Python:

```bash
# Merge
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf

# Extract pages 1-5
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf
```

## Workflow Checklist

```
Task Progress:
- [ ] Identify source files
- [ ] Determine merge order or split range
- [ ] Execute merge/split operation
- [ ] Verify output file exists and has correct page count
```

## Verification

After any merge or split operation, verify the result:

```python
from pypdf import PdfReader

result = PdfReader("output.pdf")
print(f"Total pages: {len(result.pages)}")
```
