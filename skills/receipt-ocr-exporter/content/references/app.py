"""
Receipt OCR Exporter
A minimalist web application for scanning receipts and exporting to spreadsheet format.
"""

import streamlit as st
import easyocr
import pandas as pd
from PIL import Image
import io
import re
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Receipt OCR Exporter",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for minimalist design
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #F5F5F5;
    }

    /* Upload zone styling */
    .upload-zone {
        border: 2px dashed #CCCCCC;
        border-radius: 16px;
        padding: 60px 40px;
        text-align: center;
        background: white;
        transition: all 0.3s ease;
    }

    .upload-zone:hover {
        border-color: #666666;
        background: #FAFAFA;
    }

    /* Centered content */
    .main-content {
        max-width: 700px;
        margin: 0 auto;
        padding: 20px;
    }

    /* Result card */
    .result-card {
        background: white;
        border-radius: 12px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    /* Hidden by default */
    .hidden {
        display: none;
    }

    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 500;
    }

    /* Title styling */
    .main-title {
        text-align: center;
        color: #333333;
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .subtitle {
        text-align: center;
        color: #888888;
        font-size: 1rem;
        margin-bottom: 32px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = None
if 'image_display' not in st.session_state:
    st.session_state.image_display = None

# Title
st.markdown('<p class="main-title">Receipt OCR Exporter</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Upload a receipt to extract data and export to spreadsheet</p>', unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader(
    "",
    type=['png', 'jpg', 'jpeg', 'webp'],
    help="Drop receipt image here or click to upload"
)

# Process uploaded file
if uploaded_file is not None:
    st.session_state.uploaded_file = uploaded_file

    # Display image preview
    image = Image.open(uploaded_file)
    st.image(image, caption="Receipt Preview", use_container_width=True)

    # Reset button
    if st.button("🔄 Reset"):
        st.session_state.uploaded_file = None
        st.session_state.extracted_data = None
        st.rerun()

    # Extract button
    if st.button("📋 Extract Data", type="primary"):
        with st.spinner("Processing OCR..."):
            try:
                # Initialize EasyOCR reader
                @st.cache_resource
                def load_reader():
                    return easyocr.Reader(['en', 'ch_sim'], gpu=False)

                reader = load_reader()

                # Convert to bytes for OCR
                img_bytes = io.BytesIO()
                image.save(img_bytes, format='PNG')
                img_bytes = img_bytes.getvalue()

                # Perform OCR
                results = reader.readtext(img_bytes)

                # Extract all text
                full_text = "\n".join([text for _, text, _ in results])

                # Parse receipt data
                def parse_receipt(text):
                    data = {
                        'date': '',
                        'merchant': '',
                        'total': '',
                        'currency': 'USD'
                    }

                    lines = text.split('\n')

                    # Extract merchant (usually first non-empty line)
                    for line in lines:
                        if line.strip() and len(line.strip()) > 2:
                            # Filter out lines that look like addresses or phone numbers
                            if not re.match(r'^[\d\-\+\(\)\s]+$', line.strip()):
                                if not any(kw in line.lower() for kw in ['address', 'tel', 'phone', 'www', 'http']):
                                    data['merchant'] = line.strip()[:50]
                                    break

                    # Extract date patterns
                    date_patterns = [
                        r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
                        r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                        r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})',
                    ]

                    for pattern in date_patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            data['date'] = match.group(1)
                            break

                    # Extract total amount
                    total_patterns = [
                        r'(?:total|amount|sum|grand\s*total)[:\s]*([\d,]+\.?\d*)',
                        r'(?:TOTA[L]?)[:\s]*\$?\s*([\d,]+\.?\d*)',
                        r'\$?\s*([\d,]+\.\d{2})',
                    ]

                    amounts = []
                    for pattern in total_patterns:
                        matches = re.findall(pattern, text, re.IGNORECASE)
                        for match in matches:
                            try:
                                val = float(match.replace(',', ''))
                                if 0 < val < 1000000:
                                    amounts.append(val)
                            except:
                                pass

                    if amounts:
                        data['total'] = f"{max(amounts):.2f}"

                    # Detect currency
                    if any(sym in text for sym in ['¥', 'CNY', 'RMB']):
                        data['currency'] = 'CNY'
                    elif any(sym in text for sym in ['HK$', 'HKD']):
                        data['currency'] = 'HKD'
                    elif any(sym in text for sym in ['€', 'EUR']):
                        data['currency'] = 'EUR'
                    elif any(sym in text for sym in ['£', 'GBP']):
                        data['currency'] = 'GBP'
                    elif '$' in text:
                        data['currency'] = 'USD'

                    return data

                st.session_state.extracted_data = parse_receipt(full_text)

            except Exception as e:
                st.error(f"OCR Error: {str(e)}")

# Display extracted data
if st.session_state.extracted_data:
    st.markdown("---")
    st.markdown("### 📊 Extracted Data")

    data = st.session_state.extracted_data

    # Editable fields
    col1, col2 = st.columns(2)

    with col1:
        date = st.text_input("Date", value=data.get('date', ''))
        merchant = st.text_input("Merchant", value=data.get('merchant', ''))

    with col2:
        total = st.text_input("Total Amount", value=data.get('total', ''))
        currency = st.selectbox(
            "Currency",
            ['USD', 'CNY', 'HKD', 'EUR', 'GBP', 'JPY', 'TWD'],
            index=['USD', 'CNY', 'HKD', 'EUR', 'GBP', 'JPY', 'TWD'].index(data.get('currency', 'USD')) if data.get('currency', 'USD') in ['USD', 'CNY', 'HKD', 'EUR', 'GBP', 'JPY', 'TWD'] else 0
        )

    # Update session state
    updated_data = {
        'date': date,
        'merchant': merchant,
        'total': total,
        'currency': currency
    }
    st.session_state.extracted_data.update(updated_data)

    # Raw text collapsible
    with st.expander("📝 Raw OCR Text"):
        if uploaded_file:
            try:
                @st.cache_resource
                def load_reader():
                    return easyocr.Reader(['en', 'ch_sim'], gpu=False)

                reader = load_reader()
                img_bytes = io.BytesIO()
                Image.open(uploaded_file).save(img_bytes, format='PNG')
                img_bytes = img_bytes.getvalue()
                results = reader.readtext(img_bytes)
                raw_text = "\n".join([text for _, text, _ in results])
                st.text_area("", value=raw_text, height=200, label_visibility="collapsed")
            except:
                st.info("Unable to display raw text")

    # Export buttons
    st.markdown("---")
    st.markdown("### 📤 Export")

    col1, col2 = st.columns(2)

    # Prepare export data
    export_df = pd.DataFrame([{
        'Date': st.session_state.extracted_data.get('date', ''),
        'Merchant': st.session_state.extracted_data.get('merchant', ''),
        'Total Amount': st.session_state.extracted_data.get('total', ''),
        'Currency': st.session_state.extracted_data.get('currency', 'USD')
    }])

    # CSV Export
    csv_data = export_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📊 Download CSV (Numbers)",
        data=csv_data,
        file_name="receipt_export.csv",
        mime="text/csv",
        use_container_width=True
    )

    # XLSX Export
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        export_df.to_excel(writer, sheet_name='Receipt', index=False)
    buffer.seek(0)

    st.download_button(
        "📗 Download XLSX (Excel/Numbers)",
        data=buffer.getvalue(),
        file_name="receipt_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #888888; font-size: 0.85rem;'>"
    "Supports PNG, JPG, JPEG, WebP formats • EasyOCR powered"
    "</p>",
    unsafe_allow_html=True
)
