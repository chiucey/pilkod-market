#!/usr/bin/env python3
"""
Push papers from Google Scholar to Zotero via Zotero Connector API.

Usage:
    python push_to_zotero.py <json_file>

The JSON file should contain an array of paper objects with fields:
    - title: str
    - authors: list of {"lastName": str, "firstName": str}
    - journal: str
    - pubdate: str (year)
    - volume: str (optional)
    - issue: str (optional)
    - pages: str (optional)
    - doi: str (optional)
    - pdfUrl: str (optional) - will attempt to download and attach PDF
    - abstract: str (optional)
    - language: str (default: "en")
    - pubtype: list of str (default: ["Journal Article"])

Requirements:
    - Zotero desktop app running with Zotero Connector enabled
    - requests library: pip install requests
"""

import json
import sys
import os
import time
import re
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: 'requests' library not found. Install it with: pip install requests")
    sys.exit(1)

ZOTERO_API_PORT = 23119
ZOTERO_CHILD_PORT = 24155


def check_zotero_running():
    """Check if Zotero is running."""
    try:
        response = requests.get(f"http://localhost:{ZOTERO_API_PORT}/version", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def save_item(item_data):
    """Save an item to Zotero via the Connector API."""
    try:
        response = requests.post(
            f"http://localhost:{ZOTERO_API_PORT}/connector/saveItems",
            json={"items": [item_data]},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"  Save item failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"  Error saving item: {e}")
        return None


def download_pdf(pdf_url, temp_dir):
    """Download PDF from URL to temp file."""
    if not pdf_url:
        return None

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(pdf_url, headers=headers, timeout=30, stream=True)

        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            if 'pdf' in content_type.lower() or pdf_url.lower().endswith('.pdf'):
                temp_path = os.path.join(temp_dir, 'temp_paper.pdf')
                with open(temp_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return temp_path

        print(f"  PDF download skipped (status: {response.status_code}, type: {content_type})")
        return None
    except Exception as e:
        print(f"  PDF download error: {e}")
        return None


def save_attachment(attachment_path, parent_key):
    """Save PDF attachment to Zotero via the Connector API."""
    if not attachment_path or not os.path.exists(attachment_path):
        return None

    try:
        with open(attachment_path, 'rb') as f:
            files = {
                'file': ('paper.pdf', f, 'application/pdf')
            }
            data = {
                'parentKey': parent_key
            }
            response = requests.post(
                f"http://localhost:{ZOTERO_API_PORT}/connector/saveAttachment",
                files=files,
                data=data,
                timeout=60
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"  Save attachment failed: {response.status_code}")
                return None
    except Exception as e:
        print(f"  Error saving attachment: {e}")
        return None


def parse_bibtex_author(author_str):
    """Parse BibTeX author string into lastName and firstName."""
    if not author_str:
        return {"lastName": "", "firstName": ""}

    # BibTeX format: "LastName, FirstName" or "FirstName LastName"
    if ',' in author_str:
        parts = author_str.split(',', 1)
        return {"lastName": parts[0].strip(), "firstName": parts[1].strip() if len(parts) > 1 else ""}
    else:
        parts = author_str.split()
        if len(parts) >= 2:
            return {"lastName": parts[-1], "firstName": " ".join(parts[:-1])}
        return {"lastName": author_str, "firstName": ""}


def create_zotero_item(paper):
    """Convert paper data to Zotero item format."""
    item_type = "journalArticle"
    pubtype = paper.get("pubtype", [])
    if pubtype:
        type_mapping = {
            "Journal Article": "journalArticle",
            "Conference Paper": "conferencePaper",
            "Book": "book",
            "Book Section": "bookSection",
            "Thesis": "thesis",
            "Report": "report",
            "Web Page": "webpage"
        }
        item_type = type_mapping.get(pubtype[0], "journalArticle")

    creators = []
    for author in paper.get("authors", []):
        creators.append({
            "creatorType": "author",
            "lastName": author.get("lastName", ""),
            "firstName": author.get("firstName", "")
        })

    item = {
        "itemType": item_type,
        "title": paper.get("title", ""),
        "creators": creators,
        "abstractNote": paper.get("abstract", ""),
        "date": paper.get("pubdate", ""),
        "volume": paper.get("volume", ""),
        "issue": paper.get("issue", ""),
        "pages": paper.get("pages", ""),
        "doi": paper.get("doi", ""),
        "language": paper.get("language", "en")
    }

    if item_type == "journalArticle":
        item["journalAbbreviation"] = paper.get("journalAbbr", "")
        item["publicationTitle"] = paper.get("journal", "")

    return item


def main():
    if len(sys.argv) < 2:
        print("Usage: python push_to_zotero.py <json_file>")
        sys.exit(1)

    json_file = sys.argv[1]

    if not os.path.exists(json_file):
        print(f"Error: File not found: {json_file}")
        sys.exit(1)

    with open(json_file, 'r', encoding='utf-8') as f:
        papers = json.load(f)

    if not isinstance(papers, list):
        print("Error: JSON file should contain an array of papers")
        sys.exit(1)

    if not check_zotero_running():
        print("Error: Zotero is not running. Please start Zotero desktop app.")
        sys.exit(1)

    print(f"Starting export of {len(papers)} paper(s) to Zotero...")

    temp_dir = os.path.join(os.path.dirname(json_file), 'temp_pdfs')
    os.makedirs(temp_dir, exist_ok=True)

    success_count = 0
    pdf_count = 0

    for i, paper in enumerate(papers, 1):
        print(f"\n[{i}/{len(papers)}] Processing: {paper.get('title', 'Untitled')[:60]}...")

        # Create Zotero item
        item_data = create_zotero_item(paper)
        result = save_item(item_data)

        if result:
            success_count += 1
            parent_key = result.get('key', '')

            # Try to attach PDF
            pdf_url = paper.get('pdfUrl', '')
            if pdf_url:
                print(f"  Downloading PDF...")
                pdf_path = download_pdf(pdf_url, temp_dir)

                if pdf_path:
                    print(f"  Attaching PDF...")
                    attach_result = save_attachment(pdf_path, parent_key)
                    if attach_result:
                        pdf_count += 1
                        print(f"  PDF attached successfully")
                    os.remove(pdf_path)
                else:
                    print(f"  PDF skipped")

            time.sleep(0.5)  # Rate limiting
        else:
            print(f"  Failed to save item")

    # Cleanup
    if os.path.exists(temp_dir):
        try:
            os.rmdir(temp_dir)
        except:
            pass

    print(f"\nExport complete!")
    print(f"  Items saved: {success_count}/{len(papers)}")
    print(f"  PDFs attached: {pdf_count}")


if __name__ == "__main__":
    main()
