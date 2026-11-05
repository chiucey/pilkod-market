# Receipt OCR Exporter - Technical Reference

## Project Overview

A minimalist web application for scanning receipts and exporting data to spreadsheet format.

## Tech Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Web Framework | Streamlit | >= 1.28 |
| OCR Engine | EasyOCR | >= 1.7 |
| Data Processing | Pandas | >= 2.0 |
| Excel Export | Openpyxl | >= 3.1 |
| Image Processing | Pillow | >= 10.0 |

## Installation

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install streamlit easyocr pandas openpyxl pillow

# For GPU acceleration (optional, significantly faster)
# pip install torch torchvision
```

## Application Code

The complete application is in `references/app.py`.

### Key Components

#### 1. File Upload Handler
```python
uploaded_file = st.file_uploader(
    "Drop receipt image here or click to upload",
    type=['png', 'jpg', 'jpeg', 'webp'],
    accept_multiple_files=False
)
```

#### 2. OCR Processing
```python
import easyocr

reader = easyocr.Reader(['en', 'ch_sim'])  # English + Simplified Chinese

def extract_receipt_data(image):
    results = reader.readtext(image)
    # Parse and extract fields
    return {
        'date': ...,
        'merchant': ...,
        'total': ...,
        'currency': ...
    }
```

#### 3. Export Functions
```python
import pandas as pd

def export_to_csv(data, filename="receipt_export.csv"):
    df = pd.DataFrame([data])
    df.to_csv(filename, index=False)

def export_to_xlsx(data, filename="receipt_export.xlsx"):
    df = pd.DataFrame([data])
    df.to_excel(filename, index=False, engine='openpyxl')
```

## UI Design Principles

### Minimalist Layout
- Background: Light gray (#F5F5F5) or pure white
- Centered interaction zone
- Hidden elements until needed

### State Management
```
st.session_state = {
    'uploaded_file': None,
    'extracted_data': None,
    'processed': False
}
```

### Responsive Design
- Max content width: 800px
- Consistent padding: 2rem
- Clear visual hierarchy

## OCR Optimization Tips

1. **Image Quality**: Higher resolution images produce better results
2. **Lighting**: Well-lit receipts with clear text
3. **Language Settings**: Add relevant languages to EasyOCR reader
4. **Post-processing**: Validate extracted data before saving

## Output Format

### CSV Structure
```csv
Date,Merchant,Total Amount,Currency
2024-01-15,Starbucks,25.50,USD
```

### XLSX Structure
| Date | Merchant | Total Amount | Currency |
|------|----------|--------------|----------|
| 2024-01-15 | Starbucks | 25.50 | USD |

## Error Handling

- Invalid file type: Show warning message
- OCR failure: Display error with retry option
- Export failure: Provide error details

## Deployment

### Local Development
```bash
streamlit run app.py
```

### Streamlit Cloud
1. Push code to GitHub
2. Connect to [share.streamlit.io](https://share.streamlit.io)
3. Deploy with auto-build

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

## Performance Considerations

- EasyOCR model download: ~1GB first run
- Consider caching with `@st.cache_resource`
- GPU acceleration for faster processing
- Image compression for large files
