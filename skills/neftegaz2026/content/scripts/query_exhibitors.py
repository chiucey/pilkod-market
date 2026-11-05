#!/usr/bin/env python3
"""
Query NEFTEGAZ 2026 exhibitor data.

Usage:
    python3 query_exhibitors.py --list                    # List all exhibitors
    python3 query_exhibitors.py --search "keyword"        # Search by name
    python3 query_exhibitors.py --country "China"         # Filter by country
    python3 query_exhibitors.py --letter "A"              # Filter by first letter
    python3 query_exhibitors.py --stats                   # Show statistics
    python3 query_exhibitors.py --export csv              # Export to CSV
    python3 query_exhibitors.py --export excel            # Export to Excel
"""

import json
import argparse
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, '..', 'references', 'exhibitors.json')


def load_data():
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def search_exhibitors(data, keyword):
    keyword = keyword.upper()
    return [e for e in data if keyword in e['company_name_en'].upper()
            or keyword in e.get('company_name_ru', '').upper()]


def filter_by_country(data, country):
    country = country.upper()
    return [e for e in data if country in e['country'].upper()]


def filter_by_letter(data, letter):
    letter = letter.upper()
    return [e for e in data if e['company_name_en'][0].upper() == letter]


def show_stats(data):
    from collections import Counter
    countries = Counter(e['country'] for e in data)
    letters = Counter(e['company_name_en'][0].upper() for e in data)

    print(f"NEFTEGAZ 2026 Exhibitor Statistics")
    print(f"{'=' * 50}")
    print(f"Total exhibitors: {len(data)}")
    print(f"\nBy Country:")
    for c, n in countries.most_common():
        print(f"  {c}: {n} ({n/len(data)*100:.1f}%)")
    print(f"\nBy First Letter:")
    for l in sorted(letters.keys()):
        print(f"  {l}: {letters[l]}")


def print_entries(entries):
    for e in entries:
        ru = f" / {e['company_name_ru']}" if e.get('company_name_ru') else ""
        print(f"  {e['no']:>3}. {e['company_name_en']}{ru} [{e['country']}] (p.{e['page']})")
    print(f"\n  Total: {len(entries)} exhibitors")


def export_csv(data, output_path):
    import csv
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['No.', 'Company Name (English)', 'Company Name (Russian)', 'Country', 'Catalog Page'])
        for e in data:
            writer.writerow([e['no'], e['company_name_en'], e.get('company_name_ru', ''), e['country'], e['page']])
    print(f"Exported {len(data)} entries to {output_path}")


def export_excel(data, output_path):
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "NEFTEGAZ 2026 Exhibitors"

    hf = Font(name='Arial', bold=True, size=11, color='FFFFFF')
    hfill = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
    ha = Alignment(horizontal='center', vertical='center', wrap_text=True)
    df = Font(name='Arial', size=10)
    tb = Border(left=Side(style='thin', color='CCCCCC'), right=Side(style='thin', color='CCCCCC'),
                top=Side(style='thin', color='CCCCCC'), bottom=Side(style='thin', color='CCCCCC'))

    ws.merge_cells('A1:E1')
    ws['A1'].value = 'NEFTEGAZ 2026 — Alphabetical List of Exhibitors (A–Z)'
    ws['A1'].font = Font(name='Arial', bold=True, size=14, color='1F4E79')
    ws['A1'].alignment = Alignment(horizontal='center', vertical='center')

    headers = ['No.', 'Company Name (English)', 'Company Name (Russian)', 'Country', 'Catalog Page']
    widths = [7, 55, 50, 25, 14]
    for ci, (h, w) in enumerate(zip(headers, widths), 1):
        c = ws.cell(row=3, column=ci, value=h)
        c.font, c.fill, c.alignment, c.border = hf, hfill, ha, tb
        ws.column_dimensions[get_column_letter(ci)].width = w

    lf = PatternFill(start_color='F2F7FB', end_color='F2F7FB', fill_type='solid')
    for i, e in enumerate(data, 1):
        r = i + 3
        ws.cell(row=r, column=1, value=e['no']).font = df
        ws.cell(row=r, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.cell(row=r, column=1).border = tb
        ws.cell(row=r, column=2, value=e['company_name_en']).font = Font(name='Arial', size=10, bold=True)
        ws.cell(row=r, column=2).border = tb
        ws.cell(row=r, column=3, value=e.get('company_name_ru', '')).font = df
        ws.cell(row=r, column=3).border = tb
        ws.cell(row=r, column=4, value=e['country']).font = df
        ws.cell(row=r, column=4).border = tb
        ws.cell(row=r, column=5, value=e['page']).font = df
        ws.cell(row=r, column=5).alignment = Alignment(horizontal='center', vertical='center')
        ws.cell(row=r, column=5).border = tb
        if i % 2 == 0:
            for col in range(1, 6):
                ws.cell(row=r, column=col).fill = lf

    ws.auto_filter.ref = f'A3:E{len(data) + 3}'
    ws.freeze_panes = 'A4'
    wb.save(output_path)
    print(f"Exported {len(data)} entries to {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Query NEFTEGAZ 2026 exhibitor data')
    parser.add_argument('--list', action='store_true', help='List all exhibitors')
    parser.add_argument('--search', type=str, help='Search by company name keyword')
    parser.add_argument('--country', type=str, help='Filter by country')
    parser.add_argument('--letter', type=str, help='Filter by first letter')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--export', type=str, choices=['csv', 'excel'], help='Export format')
    parser.add_argument('--output', type=str, default=None, help='Output file path')
    args = parser.parse_args()

    data = load_data()

    if args.stats:
        show_stats(data)
        return

    result = data

    if args.search:
        result = search_exhibitors(result, args.search)
    if args.country:
        result = filter_by_country(result, args.country)
    if args.letter:
        result = filter_by_letter(result, args.letter)

    if args.export:
        out = args.output or f'neftegaz2026_exhibitors.{args.export if args.export == "csv" else "xlsx"}'
        if args.export == 'csv':
            export_csv(result, out)
        else:
            export_excel(result, out)
        return

    if args.list or args.search or args.country or args.letter:
        print_entries(result)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
