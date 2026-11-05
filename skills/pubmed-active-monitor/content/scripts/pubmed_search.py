#!/usr/bin/env python3
"""
PubMed Active Monitor - Literature Search and Abstract Generation

Features:
1. Search PubMed via NCBI Entrez API
2. Fetch article details
3. Generate structured summary reports
"""

import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time


class PubMedSearcher:
    """PubMed literature searcher"""

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(self, email: str = "research@example.com"):
        """Initialize searcher

        Args:
            email: User email (required by NCBI API)
        """
        self.email = email
        self.api_key = None  # Optional: add API key for higher rate limit

    def _make_request(self, url: str, max_retries: int = 3) -> Optional[dict]:
        """Send HTTP request and return JSON response

        Args:
            url: Request URL
            max_retries: Maximum retry attempts

        Returns:
            JSON response dict, or None on failure
        """
        for attempt in range(max_retries):
            try:
                request = urllib.request.Request(url)
                with urllib.request.urlopen(request, timeout=30) as response:
                    return json.loads(response.read().decode('utf-8'))
            except urllib.error.HTTPError as e:
                if e.code == 429:  # Rate limit
                    wait_time = (attempt + 1) * 2
                    print(f"Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"HTTP Error: {e.code}")
                    return None
            except Exception as e:
                print(f"Request failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
        return None

    def search(
        self,
        query: str,
        max_results: int = 20,
        days_back: int = 7,
        sort: str = "date"
    ) -> List[str]:
        """Search PubMed literature

        Args:
            query: PubMed search query (supports MeSH terms and boolean logic)
            max_results: Maximum number of results to return
            days_back: Search literature from recent days
            sort: Sort order (date/relevance)

        Returns:
            List of PMIDs
        """
        # Build date filter
        date_range = f'("{datetime.now().date() - timedelta(days=days_back)}"[Date - Publication] : "{datetime.now().date()}"[Date - Publication])'
        full_query = f"({query}) AND {date_range}"

        params = {
            "db": "pubmed",
            "term": full_query,
            "retmax": max_results,
            "retmode": "json",
            "sort": sort,
            "tool": "PubMedActiveMonitor",
            "email": self.email
        }

        if self.api_key:
            params["api_key"] = self.api_key

        url = f"{self.BASE_URL}/esearch.fcgi?{urllib.parse.urlencode(params)}"
        result = self._make_request(url)

        if result and "esearchresult" in result:
            id_list = result["esearchresult"].get("idlist", [])
            print(f"Found {len(id_list)} articles")
            return id_list

        return []

    def get_article_details(self, pmids: List[str]) -> List[Dict]:
        """Fetch article details

        Args:
            pmids: List of PMIDs

        Returns:
            List of article details
        """
        if not pmids:
            return []

        # Use EFetch to get detailed information
        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
            "rettype": "abstract"
        }

        if self.api_key:
            params["api_key"] = self.api_key

        url = f"{self.BASE_URL}/efetch.fcgi?{urllib.parse.urlencode(params)}"

        try:
            request = urllib.request.Request(url)
            with urllib.request.urlopen(request, timeout=60) as response:
                return self._parse_xml_response(response.read().decode('utf-8'))
        except Exception as e:
            print(f"Failed to fetch article details: {e}")
            return []

    def _parse_xml_response(self, xml_content: str) -> List[Dict]:
        """Parse XML response

        Args:
            xml_content: XML formatted response content

        Returns:
            Parsed article list
        """
        import xml.etree.ElementTree as ET

        articles = []
        try:
            root = ET.fromstring(xml_content)
            for article in root.findall(".//PubmedArticle"):
                article_data = {}

                # Get PMID
                pmid_elem = article.find(".//PMID")
                article_data["pmid"] = pmid_elem.text if pmid_elem is not None else ""

                # Get title
                title_elem = article.find(".//ArticleTitle")
                article_data["title"] = title_elem.text if title_elem is not None else "N/A"

                # Get author list
                authors = []
                for author in article.findall(".//Author"):
                    last_name = author.find("LastName")
                    fore_name = author.find("ForeName")
                    if last_name is not None and fore_name is not None:
                        authors.append(f"{fore_name.text} {last_name.text}")
                    elif last_name is not None:
                        authors.append(last_name.text)
                article_data["authors"] = authors

                # Get journal info
                journal_elem = article.find(".//Journal/Title")
                article_data["journal"] = journal_elem.text if journal_elem is not None else "N/A"

                # Get publication date
                pub_date = article.find(".//PubDate")
                if pub_date is not None:
                    year = pub_date.find("Year")
                    month = pub_date.find("Month")
                    day = pub_date.find("Day")
                    article_data["pub_date"] = "-".join([
                        year.text if year is not None else "",
                        month.text if month is not None else "01",
                        day.text if day is not None else "01"
                    ]).strip("-")
                else:
                    article_data["pub_date"] = "N/A"

                # Get abstract
                abstracts = []
                for abstract in article.findall(".//AbstractText"):
                    if abstract.text:
                        abstracts.append(abstract.text)
                article_data["abstract"] = "\n".join(abstracts) if abstracts else "N/A"

                # Get DOI
                article_id_list = article.findall(".//ArticleId")
                for article_id in article_id_list:
                    if article_id.get("IdType") == "doi":
                        article_data["doi"] = article_id.text
                        break
                else:
                    article_data["doi"] = "N/A"

                # Get keywords
                keywords = []
                for keyword in article.findall(".//Keyword"):
                    if keyword.text:
                        keywords.append(keyword.text)
                article_data["keywords"] = keywords

                # Get Publication Type
                pub_types = []
                for pub_type in article.findall(".//PublicationType"):
                    if pub_type.text:
                        pub_types.append(pub_type.text)
                article_data["pub_types"] = pub_types

                articles.append(article_data)

        except ET.ParseError as e:
            print(f"XML parsing error: {e}")

        return articles


def generate_summary_report(articles: List[Dict], topic: str) -> str:
    """Generate literature summary report

    Args:
        articles: List of articles
        topic: Monitoring topic

    Returns:
        Formatted report text
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""## New Literature Push Report

**Topic**: {topic}
**Search Time**: {timestamp}
**Articles Found**: {len(articles)}

---

"""

    for i, article in enumerate(articles, 1):
        authors_str = ", ".join(article.get("authors", [])[:3])
        if len(article.get("authors", [])) > 3:
            authors_str += " et al."

        pub_types_str = "; ".join(article.get("pub_types", [])[:3])

        report += f"""### {i}. {article.get('title', 'N/A')}

- **PMID**: {article.get('pmid', 'N/A')}
- **Authors**: {authors_str}
- **Journal**: {article.get('journal', 'N/A')} ({article.get('pub_date', 'N/A')})
- **Type**: {pub_types_str}
- **DOI**: {article.get('doi', 'N/A')}
- **Abstract**: {article.get('abstract', 'N/A')[:500]}{'...' if len(article.get('abstract', '')) > 500 else ''}

**Link**: https://pubmed.ncbi.nlm.nih.gov/{article.get('pmid', '')}/

---

"""

    return report


def main():
    """Main function - demo usage"""
    searcher = PubMedSearcher(email="research@example.com")

    # Example queries
    queries = [
        ("CSCO Guidelines", "CSCO[Title/Abstract] AND (guideline[Title/Abstract] OR consensus[Title/Abstract])"),
        ("Cancer Immunotherapy", "immunotherapy[Title/Abstract] AND (cancer[Title/Abstract] OR oncology[MeSH Terms])"),
        ("Precision Medicine Biomarkers", "biomarker[Title/Abstract] AND (precision medicine[Title/Abstract] OR personalized medicine[Title/Abstract])"),
    ]

    for topic, query in queries:
        print(f"\n{'='*60}")
        print(f"Topic: {topic}")
        print(f"Query: {query}")
        print('='*60)

        pmids = searcher.search(query, max_results=10, days_back=30)
        if pmids:
            articles = searcher.get_article_details(pmids)
            report = generate_summary_report(articles, topic)
            print(report)
        else:
            print("No relevant literature found")


if __name__ == "__main__":
    main()
