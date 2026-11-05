---
name: receipt-ocr-exporter
description: Receipt OCR and Export Tool. Use when users ask to scan receipts, extract receipt data, convert receipts to spreadsheet, receipt to CSV/Excel/Numbers, or identify expenses from receipt images.
---

# Receipt OCR Exporter

A minimalist web application that uses OCR to automatically extract receipt data and export to Numbers-compatible spreadsheet format.

## Features

- **Drag & Drop Upload**: Upload receipt images via drag-and-drop or click
- **OCR Extraction**: Automatically extract Date, Merchant, Total Amount, Currency
- **Export to Numbers**: Export results as .csv or .xlsx (compatible with Apple Numbers)
- **Minimalist UI**: Clean, distraction-free interface with hidden complexity

## Tech Stack

- **Framework**: Python Streamlit
- **OCR Engine**: EasyOCR (supports multiple languages including Chinese, English)
- **Export**: pandas + openpyxl

## Quick Start

```bash
# Install dependencies
pip install streamlit easyocr pandas openpyxl pillow

# Run the application
streamlit run app.py
```

## Application Structure

The application follows a **hidden complexity** pattern:
- No tables or buttons visible before upload
- Results appear dynamically after processing
- Clean, centered interaction zone

## Data Extraction

The OCR engine extracts:
| Field | Description |
|-------|-------------|
| Date | Transaction date |
| Merchant | Store/vendor name |
| Total Amount | Final total value |
| Currency | Currency symbol/code |

## Export Format

- **CSV**: Universal compatibility with all spreadsheet apps
- **XLSX**: Native Excel/Numbers format with styling

## Receipt Categories

Optional classification categories:
- Administration and Equipment fee
- Advertising Materials to clients
- Business Registration fee
- Business Entertainment with clients
- Consumable
- Mobile & Broadband fee
- Postage & Express
- Stationery & Printing
- Vehicle cost
- Vehicle Recurring expenses
- Travelling expenses
- Business Trip

## Usage Flow

1. User drags image or clicks to upload
2. System displays preview
3. User clicks "Extract Data" button
4. OCR processes and displays extracted fields
5. User can edit results if needed
6. User clicks "Export to Numbers" button
7. File downloads automatically
