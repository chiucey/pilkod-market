#!/usr/bin/env python3
"""
Minimal example demonstrating mck-ppt-design skill capabilities.
Run: python minimal_example.py
"""

import sys
import os

# Add skill directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from mck_ppt import MckEngine
    from mck_ppt.constants import *
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Install dependencies: pip install python-pptx lxml")
    sys.exit(1)

# Create presentation
eng = MckEngine(total_slides=8)

# 1. Cover slide
eng.cover(
    title='2026 Q1 Strategy Review',
    subtitle='Board Presentation',
    author='Strategy Department',
    date='March 2026'
)

# 2. Table of Contents
eng.toc(items=[
    ('1', 'Market Overview', 'Current competitive landscape'),
    ('2', 'Financial Analysis', 'Revenue and profit trends'),
    ('3', 'Strategic Recommendations', 'Three core actions')
])

# 3. Section Divider
eng.section_divider(section_label='Part 1', title='Market Overview')

# 4. Big Number
eng.big_number(
    title='Total Addressable Market',
    number='¥850B',
    description='2026 projected market size',
    detail_items=['YoY growth: +23%', 'Online channel: 60%+'],
    source='Source: Industry Report 2026'
)

# 5. Donut Chart
eng.donut_chart(
    title='Market Share Distribution',
    segments=[
        (0.35, NAVY, 'We'),
        (0.25, ACCENT_BLUE, 'Competitor A'),
        (0.20, ACCENT_GREEN, 'Competitor B'),
        (0.20, ACCENT_ORANGE, 'Others')
    ],
    center_label='35%',
    center_sub='Our Share',
    source='Source: Market Research 2026'
)

# 6. Grouped Bar Chart
eng.grouped_bar(
    title='Quarterly Revenue Trend',
    categories=['Q1', 'Q2', 'Q3', 'Q4'],
    series=[('Product', NAVY), ('Service', ACCENT_BLUE)],
    data=[[120, 80], [145, 95], [160, 110], [180, 130]],
    max_val=200,
    source='Source: Finance Department'
)

# 7. Section Divider
eng.section_divider(section_label='Part 3', title='Strategic Recommendations')

# 8. Closing
eng.closing(title='Thank You', message='Looking forward to your feedback')

# Save
output_path = 'example_output.pptx'
os.makedirs('output', exist_ok=True)
eng.save(f'output/{output_path}')

print(f"✅ Generated: output/{output_path}")
print(f"📊 Total slides: {eng._page}")
