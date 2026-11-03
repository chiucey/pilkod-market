#!/usr/bin/env python3
"""
ArXiv Paper Search Script
Search and export academic papers from arXiv.org to CSV format.
"""

import csv
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Optional


def search_arxiv(
    query: str,
    max_results: int = 10,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    sort_by: str = "relevance",
    sort_order: str = "descending"
) -> List[Dict]:
    """
    Search arXiv for papers matching the query.

    Args:
        query: Search keywords
        max_results: Maximum number of results (default: 10)
        date_from: Start date filter (YYYY-MM-DD format)
        date_to: End date filter (YYYY-MM-DD format)
        sort_by: Sort by 'relevance', 'lastUpdatedDate', or 'submittedDate'
        sort_order: 'ascending' or 'descending'

    Returns:
        List of paper dictionaries
    """
    base_url = "http://export.arxiv.org/api/query"

    # Build search query
    search_query = urllib.parse.quote(query)

    # Build URL parameters
    params = [
        f"search_query=all:{search_query}",
        f"start=0",
        f"max_results={max_results}",
        f"sortBy={sort_by}",
        f"sortOrder={sort_order}"
    ]

    if date_from:
        params.append(f"datefrom={date_from}")
    if date_to:
        params.append(f"dateto={date_to}")

    url = f"{base_url}?{'&'.join(params)}"

    # Fetch and parse results
    papers = []
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            xml_content = response.read().decode("utf-8")

        root = ET.fromstring(xml_content)
        ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

        for entry in root.findall("atom:entry", ns):
            paper = {
                "arxiv_id": "",
                "title": "",
                "authors": "",
                "abstract": "",
                "published": "",
                "updated": "",
                "categories": "",
                "pdf_url": "",
                "doi": ""
            }

            # Extract arXiv ID from ID URL
            id_url = entry.find("atom:id", ns)
            if id_url is not None and id_url.text:
                paper["arxiv_id"] = id_url.text.split("/")[-1]

            # Extract title
            title = entry.find("atom:title", ns)
            if title is not None:
                paper["title"] = " ".join(title.text.split())

            # Extract authors
            authors = []
            for author in entry.findall("atom:author", ns):
                name = author.find("atom:name", ns)
                if name is not None and name.text:
                    authors.append(name.text)
            paper["authors"] = ", ".join(authors)

            # Extract abstract
            summary = entry.find("atom:summary", ns)
            if summary is not None:
                paper["abstract"] = " ".join(summary.text.split())

            # Extract dates
            published = entry.find("atom:published", ns)
            if published is not None and published.text:
                paper["published"] = published.text[:10]

            updated = entry.find("atom:updated", ns)
            if updated is not None and updated.text:
                paper["updated"] = updated.text[:10]

            # Extract categories
            categories = []
            for category in entry.findall("atom:category", ns):
                term = category.get("term")
                if term:
                    categories.append(term)
            paper["categories"] = ", ".join(categories)

            # Extract PDF link
            for link in entry.findall("atom:link", ns):
                if link.get("title") == "pdf":
                    paper["pdf_url"] = link.get("href")
                    break

            # Extract DOI
            doi = entry.find("arxiv:doi", ns)
            if doi is not None and doi.text:
                paper["doi"] = doi.text

            papers.append(paper)

    except Exception as e:
        print(f"Error searching arXiv: {e}")
        raise

    return papers


def export_to_csv(papers: List[Dict], output_path: str) -> None:
    """
    Export papers to CSV file.

    Args:
        papers: List of paper dictionaries
        output_path: Path to output CSV file
    """
    if not papers:
        print("No papers to export")
        return

    fieldnames = ["arxiv_id", "title", "authors", "abstract", "published", "updated", "categories", "pdf_url", "doi"]

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(papers)

    print(f"Exported {len(papers)} papers to {output_path}")


def main():
    """Main function for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Search arXiv and export to CSV")
    parser.add_argument("--query", required=True, help="Search keywords")
    parser.add_argument("--max-results", type=int, default=10, help="Maximum results")
    parser.add_argument("--date-from", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--date-to", help="End date (YYYY-MM-DD)")
    parser.add_argument("--output", required=True, help="Output CSV path")
    parser.add_argument("--sort-by", default="relevance", choices=["relevance", "lastUpdatedDate", "submittedDate"])
    parser.add_argument("--sort-order", default="descending", choices=["ascending", "descending"])

    args = parser.parse_args()

    papers = search_arxiv(
        query=args.query,
        max_results=args.max_results,
        date_from=args.date_from,
        date_to=args.date_to,
        sort_by=args.sort_by,
        sort_order=args.sort_order
    )

    export_to_csv(papers, args.output)


if __name__ == "__main__":
    main()
