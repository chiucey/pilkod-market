#!/usr/bin/env python3
"""Extract text from PDF file(s) and output as JSON."""

import argparse
import json
import os
import sys


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from a single PDF file using pdfplumber.

    Args:
        pdf_path: Absolute path to the PDF file.

    Returns:
        Extracted text content as a single string, with pages separated by double newlines.
    """
    try:
        import pdfplumber
    except ImportError:
        print(
            "Error: pdfplumber is not installed. Install with: pip install pdfplumber",
            file=sys.stderr,
        )
        sys.exit(1)

    text_parts = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
    except Exception as e:
        print(f"Warning: Failed to extract from {pdf_path}: {e}", file=sys.stderr)
        return ""

    return "\n\n".join(text_parts)


def extract_single_file(pdf_path: str, output_path: str) -> dict:
    """Extract text from a single PDF file and save to JSON.

    Args:
        pdf_path: Path to the single PDF file.
        output_path: Path to the output JSON file.

    Returns:
        The extraction result dict.
    """
    if not os.path.isfile(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    filename = os.path.basename(pdf_path)
    print(f"Extracting: {filename}...", file=sys.stderr)
    text = extract_text_from_pdf(pdf_path)

    char_count = len(text) if text else 0
    status = "OK" if char_count > 0 else "EMPTY"
    print(f"  -> {status} ({char_count} characters)", file=sys.stderr)

    result = {
        "filename": filename,
        "filepath": os.path.abspath(pdf_path),
        "text": text,
        "char_count": char_count,
    }

    output_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Saved to: {output_path}", file=sys.stderr)
    return result


def extract_folder(folder: str, output_path: str) -> list:
    """Extract text from all PDF files in a folder and save to JSON.

    Args:
        folder: Path to the folder containing PDF files.
        output_path: Path to the output JSON file.

    Returns:
        List of extraction result dicts.
    """
    if not os.path.isdir(folder):
        print(f"Error: '{folder}' is not a valid directory", file=sys.stderr)
        sys.exit(1)

    pdf_files = sorted(
        [f for f in os.listdir(folder) if f.lower().endswith(".pdf")]
    )

    if not pdf_files:
        print(f"Error: No PDF files found in '{folder}'", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(pdf_files)} PDF file(s) in '{folder}'", file=sys.stderr)

    results = []
    for i, pdf_file in enumerate(pdf_files, 1):
        pdf_path = os.path.join(folder, pdf_file)
        print(f"[{i}/{len(pdf_files)}] Extracting: {pdf_file}...", file=sys.stderr)
        text = extract_text_from_pdf(pdf_path)

        char_count = len(text) if text else 0
        status = "OK" if char_count > 0 else "EMPTY"
        print(f"  -> {status} ({char_count} characters)", file=sys.stderr)

        results.append(
            {
                "filename": pdf_file,
                "filepath": os.path.abspath(pdf_path),
                "text": text,
                "char_count": char_count,
            }
        )

    output_data = {"total_files": len(results), "patents": results}

    output_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    ok_count = sum(1 for r in results if r["char_count"] > 0)
    print(
        f"\nDone: {ok_count}/{len(results)} files extracted successfully. Output: {output_path}",
        file=sys.stderr,
    )
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Extract text from PDF file(s) and output as JSON"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--folder",
        help="Path to the folder containing PDF files (extract all PDFs)",
    )
    group.add_argument(
        "--file",
        help="Path to a single PDF file (extract one PDF)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to the output JSON file",
    )
    args = parser.parse_args()

    if args.file:
        extract_single_file(args.file, args.output)
    else:
        extract_folder(args.folder, args.output)


if __name__ == "__main__":
    main()
