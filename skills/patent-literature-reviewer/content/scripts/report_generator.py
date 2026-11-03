#!/usr/bin/env python3
"""
Patent Literature Review Report Generator
Generates Word (.docx) format existing technology reports
"""

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from datetime import datetime
import json
import os


def create_report(output_path: str, report_data: dict) -> str:
    """
    Generate Word format patent literature review report

    Args:
        output_path: Output file path
        report_data: Dictionary containing:
            - patent_title: Patent title
            - technical_field: Technical field
            - key_techniques: List of key technical approaches
            - search_query: Search query used
            - current_tech_overview: Existing technology overview
            - literature_reviews: List of literature reviews
            - conclusion: Report conclusion

    Returns:
        Path to generated report file
    """
    doc = Document()

    # Set document title
    title = doc.add_heading('Patent Literature Prior Art Report', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Add basic report info
    doc.add_paragraph()
    info_para = doc.add_paragraph()
    info_para.add_run('Report Generated: ').bold = True
    info_para.add_run(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    doc.add_paragraph()

    # Section 1: Basic Information
    doc.add_heading('1. Basic Information', level=1)

    basic_info = [
        ('Patent Title', report_data.get('patent_title', 'Not provided')),
        ('Technical Field', report_data.get('technical_field', 'Not provided')),
        ('Key Technical Approaches', ', '.join(report_data.get('key_techniques', []))),
        ('Search Query', report_data.get('search_query', 'Not provided')),
    ]

    for key, value in basic_info:
        para = doc.add_paragraph()
        para.add_run(f'{key}: ').bold = True
        para.add_run(value)

    # Section 2: Existing Technology Overview
    doc.add_heading('2. Existing Technology Overview', level=1)
    overview_text = report_data.get('current_tech_overview', 'Not provided')
    doc.add_paragraph(overview_text)

    # Section 3: Literature Review
    doc.add_heading('3. Literature Review', level=1)

    literatures = report_data.get('literature_reviews', [])
    if not literatures:
        doc.add_paragraph('No relevant literature found')
    else:
        for i, lit in enumerate(literatures, 1):
            # Literature title
            doc.add_heading(f'Literature {i}: {lit.get("title", "Untitled")}', level=2)

            # Literature info
            info = lit.get('info', '')
            if info:
                para = doc.add_paragraph()
                para.add_run('Basic Info: ').bold = True
                para.add_run(info)

            # Relevance
            relevance = lit.get('relevance', 'Not assessed')
            para = doc.add_paragraph()
            para.add_run('Relevance: ').bold = True
            para.add_run(relevance)

            # Disclosed Content
            content = lit.get('content', 'Not provided')
            para = doc.add_paragraph()
            para.add_run('Disclosed Content: ').bold = True
            doc.add_paragraph(content)

    # Section 4: Report Conclusion
    doc.add_heading('4. Report Conclusion', level=1)
    conclusion = report_data.get('conclusion', 'Not provided')
    doc.add_paragraph(conclusion)

    # Add separator
    doc.add_paragraph()
    doc.add_paragraph('=' * 50)

    # Add footer note
    footer = doc.add_paragraph()
    footer.add_run('Note: This report is generated based on PubMed search results and is for reference only.').italic = True
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Save document
    doc.save(output_path)
    return output_path


def generate_filename() -> str:
    """Generate filename with timestamp"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f'Patent_Prior_Art_Report_{timestamp}.docx'


if __name__ == '__main__':
    # Test code
    sample_data = {
        'patent_title': 'Sample Patent Title',
        'technical_field': 'Biomarker Detection',
        'key_techniques': ['ELISA', 'Immunoassay', 'Biomarker'],
        'search_query': '(biomarker[Title/Abstract]) AND (ELISA[Title/Abstract])',
        'current_tech_overview': 'Overview of existing technology...',
        'literature_reviews': [
            {
                'title': 'Sample Literature 1',
                'info': 'Published 2023, Journal of...',
                'relevance': 'High',
                'content': 'This literature discloses...'
            }
        ],
        'conclusion': 'Conclusion content...'
    }

    output = generate_filename()
    result = create_report(output, sample_data)
    print(f'Report generated: {result}')
