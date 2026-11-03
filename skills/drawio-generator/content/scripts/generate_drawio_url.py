#!/usr/bin/env python3
"""
Generate draw.io URL from Mermaid, XML, or CSV diagram code.

This script compresses and encodes diagram content to create a draw.io URL
that users can open directly in their browser.
"""

import argparse
import gzip
import base64
import urllib.parse
import re
import sys


def compress_and_encode(content: str) -> str:
    """Compress and encode content using gzip + base64."""
    # Compress the content
    compressed = gzip.compress(content.encode('utf-8'))
    # Encode as URL-safe base64 and replace characters
    encoded = base64.urlsafe_b64encode(compressed).decode('ascii')
    # Remove padding
    encoded = encoded.rstrip('=')
    return encoded


def validate_xml(xml_content: str) -> bool:
    """Validate XML content for common draw.io issues."""
    # Check for double hyphens in comments (invalid in XML)
    if '--' in re.sub(r'<!--[\s\S]*?-->', '', xml_content):
        print("Warning: Double hyphens (--) found in XML content may cause issues.", file=sys.stderr)
        return False
    return True


def generate_drawio_url(diagram_type: str, code: str) -> str:
    """
    Generate a draw.io URL from diagram code.

    Args:
        diagram_type: Type of diagram (mermaid, xml, csv)
        code: The diagram code content

    Returns:
        A markdown-formatted link to open the diagram
    """
    # Encode the code
    encoded = compress_and_encode(code)

    # Determine the URL parameters based on diagram type
    if diagram_type == 'mermaid':
        # Mermaid diagrams
        params = urllib.parse.urlencode({
            'encode': 'true',
            'dio': '1',
            'ses': 'U',
        })
        # Add Mermaid as the format
        url = f"https://app.diagrams.net/?{params}#Mermaid:{encoded}"
    elif diagram_type == 'xml':
        # XML/draw.io native format
        params = urllib.parse.urlencode({
            'encode': 'true',
        })
        url = f"https://app.diagrams.net/?{params}#G1Z{encoded}"
    elif diagram_type == 'csv':
        # CSV format
        params = urllib.parse.urlencode({
            'encode': 'true',
            'csv': '1',
        })
        url = f"https://app.diagrams.net/?{params}#CSV:{encoded}"
    else:
        raise ValueError(f"Unknown diagram type: {diagram_type}")

    return f"[Click to view diagram]({url})"


def main():
    parser = argparse.ArgumentParser(
        description='Generate draw.io URL from diagram code'
    )
    parser.add_argument(
        '-t', '--type',
        required=True,
        choices=['mermaid', 'xml', 'csv'],
        help='Diagram type'
    )
    parser.add_argument(
        '-c', '--code',
        required=True,
        help='Diagram code content'
    )

    args = parser.parse_args()

    # For XML, validate the content
    if args.type == 'xml':
        if not validate_xml(args.code):
            sys.exit(1)

    # Generate and print the URL
    result = generate_drawio_url(args.type, args.code)
    print(result)


if __name__ == '__main__':
    main()
