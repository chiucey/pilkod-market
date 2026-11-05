#!/usr/bin/env python3
"""
Citation Fact-Checker Script
Verify the authenticity and reliability of academic paper citations through multiple channels
"""

import re
import json
import argparse
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import urllib.request
import urllib.parse
import urllib.error


class VerificationStatus(Enum):
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"
    UNKNOWN = "unknown"


@dataclass
class CitationInfo:
    """Parsed citation information"""
    doi: Optional[str] = None
    title: Optional[str] = None
    authors: List[str] = None
    year: Optional[int] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    publisher: Optional[str] = None
    raw_citation: str = ""


@dataclass
class VerificationResult:
    """Verification result"""
    status: VerificationStatus
    confidence: int  # 0-100
    message: str
    issues: List[str]
    evidence: Dict
    matched_info: Dict


class CitationParser:
    """Citation information parser"""

    # DOI regex pattern
    DOI_PATTERN = r'10\.\d{4,}/[^\s]+'

    @classmethod
    def parse(cls, citation_text: str) -> CitationInfo:
        """Parse citation text"""
        info = CitationInfo(raw_citation=citation_text)

        # Extract DOI
        doi_match = re.search(cls.DOI_PATTERN, citation_text)
        if doi_match:
            info.doi = doi_match.group(0).rstrip('.,;')

        # Extract year
        year_match = re.search(r'\((\d{4})\)|\b(19|20)\d{2}\b', citation_text)
        if year_match:
            year_group = year_match.group(1) or year_match.group(2)
            if year_group:
                info.year = int(year_group)

        # Extract title (common formats)
        title_match = re.search(r'"([^"]+)"|《([^》]+)》|(?:In\s+)?([A-Z][^.]+)', citation_text)
        if title_match:
            info.title = title_match.group(1) or title_match.group(2) or title_match.group(3)

        # Extract journal information
        journal_patterns = [
            r'(?:In\s+)?([A-Z][a-zA-Z\s&:]+)(?:,|\.)\s*\d+',  # Journal Name, vol
            r'(?:In\s+)?Proceedings\s+of\s+([A-Z][^,]+)',     # Proceedings of...
            r'(?:IEEE|ACM|Springer|Elsevier)\s+([A-Z][^,]+)',   # Publisher Journal
        ]
        for pattern in journal_patterns:
            match = re.search(pattern, citation_text)
            if match:
                info.journal = match.group(1).strip()
                break

        # Extract authors
        author_match = re.search(r'^([A-Z][a-z]+(?:,\s*[A-Z]\.?)?(?:\s*(?:et\s+al\.|,|&|and)\s*[A-Z][a-z]+)*)', citation_text)
        if author_match:
            authors_str = author_match.group(1)
            info.authors = [a.strip() for a in re.split(r',|&|and', authors_str) if a.strip()]

        return info


class DOIVerifier:
    """DOI verifier using CrossRef API"""

    CROSSREF_API = "https://api.crossref.org/works/"

    @classmethod
    def verify(cls, doi: str) -> Tuple[bool, Dict]:
        """Verify DOI and get metadata"""
        try:
            url = cls.CROSSREF_API + urllib.parse.quote(doi)
            req = urllib.request.Request(url, headers={'User-Agent': 'CitationValidator/1.0'})

            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))

                if data.get('status') == 'ok':
                    message = data.get('message', {})
                    return True, {
                        'title': message.get('title', [''])[0] if message.get('title') else None,
                        'authors': cls._parse_authors(message.get('author', [])),
                        'year': message.get('published-print', {}).get('date-parts', [[0]])[0][0],
                        'journal': message.get('container-title', [''])[0] if message.get('container-title') else None,
                        'volume': message.get('volume'),
                        'issue': message.get('issue'),
                        'pages': message.get('page'),
                        'publisher': message.get('publisher'),
                        'doi': message.get('DOI'),
                        'type': message.get('type'),
                    }
                return False, {}

        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, Exception) as e:
            return False, {'error': str(e)}

    @classmethod
    def _parse_authors(cls, authors: List[Dict]) -> List[str]:
        """Parse author list"""
        return [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in authors]


class CitationValidator:
    """Main citation verification class"""

    def __init__(self):
        self.parser = CitationParser()
        self.doi_verifier = DOIVerifier()

    def validate(self, citation_text: str, paper_year: Optional[int] = None) -> VerificationResult:
        """Validate a single citation"""

        # 1. Parse citation
        parsed = self.parser.parse(citation_text)

        issues = []
        evidence = {}
        matched_info = {}
        confidence = 50  # Base confidence

        # 2. DOI verification (priority)
        if parsed.doi:
            is_valid, metadata = self.doi_verifier.verify(parsed.doi)

            if is_valid:
                confidence += 30
                matched_info = metadata
                evidence['doi_verified'] = True
                evidence['metadata'] = metadata

                # Check title
                if parsed.title and metadata.get('title'):
                    title_match = self._fuzzy_match(parsed.title.lower(), metadata['title'].lower())
                    if title_match < 0.7:
                        issues.append(f"Title may not match: input'{parsed.title}' vs API'{metadata['title']}'")
                        confidence -= 10

                # Check year
                if parsed.year and metadata.get('year'):
                    if parsed.year != metadata['year']:
                        issues.append(f"Year mismatch: input{parsed.year} vs API{metadata['year']}")
                        confidence -= 15
                    else:
                        confidence += 10

                # Check paper year vs citation year
                if paper_year and metadata.get('year'):
                    if metadata['year'] > paper_year:
                        issues.append(f"Warning: Citation published({metadata['year']}) after paper({paper_year})")
                        confidence -= 20

            else:
                issues.append(f"DOI cannot be verified: {parsed.doi}")
                if 'error' in metadata:
                    issues.append(f"API error: {metadata['error']}")
                confidence -= 30
                evidence['doi_verified'] = False
        else:
            issues.append("No DOI found, verification limited")
            confidence -= 20

        # 3. Basic format check
        format_issues = self._check_format(parsed)
        issues.extend(format_issues)
        if format_issues:
            confidence -= 5 * len(format_issues)

        # 4. Determine status
        confidence = max(0, min(100, confidence))

        if confidence >= 80 and not issues:
            status = VerificationStatus.PASS
            message = "Citation verified successfully"
        elif confidence >= 50:
            status = VerificationStatus.WARNING
            message = "Citation has concerns, manual review recommended"
        else:
            status = VerificationStatus.FAIL
            message = "Citation verification failed, further investigation needed"

        return VerificationResult(
            status=status,
            confidence=confidence,
            message=message,
            issues=issues,
            evidence=evidence,
            matched_info=matched_info
        )

    def _fuzzy_match(self, str1: str, str2: str) -> float:
        """Simple fuzzy matching (based on shared words)"""
        words1 = set(str1.split())
        words2 = set(str2.split())
        if not words1 or not words2:
            return 0.0
        intersection = words1 & words2
        return len(intersection) / max(len(words1), len(words2))

    def _check_format(self, parsed: CitationInfo) -> List[str]:
        """Check citation format"""
        issues = []

        # Check page format
        if parsed.pages:
            if not re.match(r'^\d+(-\d+)?$', parsed.pages.replace('–', '-')):
                issues.append(f"Page format may be non-standard: {parsed.pages}")

        # Check volume format
        if parsed.volume and not re.match(r'^\d+[A-Za-z]?$', parsed.volume):
            issues.append(f"Volume format may be non-standard: {parsed.volume}")

        return issues


def format_result(result: VerificationResult) -> str:
    """Format verification result"""
    status_icons = {
        VerificationStatus.PASS: "[OK]",
        VerificationStatus.WARNING: "[!]",
        VerificationStatus.FAIL: "[X]",
        VerificationStatus.UNKNOWN: "[?]"
    }

    lines = [
        f"{status_icons[result.status]} Status: {result.status.value.upper()}",
        f"Confidence: {result.confidence}%",
        f"Message: {result.message}",
    ]

    if result.issues:
        lines.append("\nIssues found:")
        for issue in result.issues:
            lines.append(f"  - {issue}")

    if result.matched_info:
        lines.append("\nAPI Matched Info:")
        for key, value in result.matched_info.items():
            if value:
                lines.append(f"  - {key}: {value}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Citation Fact-Checker - Academic Citation Verification Tool")
    parser.add_argument('citation', nargs='?', help='Citation text to verify')
    parser.add_argument('-f', '--file', help='File containing citations (one per line)')
    parser.add_argument('-y', '--year', type=int, help='Paper publication year (for timeliness check)')
    parser.add_argument('-j', '--json', action='store_true', help='JSON output format')

    args = parser.parse_args()

    validator = CitationValidator()
    citations = []

    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            citations = [line.strip() for line in f if line.strip()]
    elif args.citation:
        citations = [args.citation]
    else:
        print("Please provide citation text or file")
        return

    results = []
    for i, citation in enumerate(citations, 1):
        print(f"\nVerifying {i}/{len(citations)}: {citation[:60]}...")
        result = validator.validate(citation, args.year)
        results.append(result)

        if args.json:
            results[-1] = {
                'citation': citation,
                'status': result.status.value,
                'confidence': result.confidence,
                'message': result.message,
                'issues': result.issues,
                'matched_info': result.matched_info
            }
        else:
            print(format_result(result))

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
