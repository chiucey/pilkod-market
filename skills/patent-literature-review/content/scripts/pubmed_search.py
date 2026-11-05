#!/usr/bin/env python3
"""
PubMed文献检索脚本
用于根据关键词搜索PubMed数据库并获取文献信息
"""

import json
import urllib.request
import urllib.parse
import time
from typing import List, Dict, Optional

class PubMedSearcher:
    """PubMed文献检索器"""

    ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    def __init__(self, delay: float = 0.34):
        """
        初始化检索器

        Args:
            delay: 请求间隔（秒），避免触发API限制
        """
        self.delay = delay
        self.last_request_time = 0

    def _rate_limit(self):
        """请求频率限制"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_request_time = time.time()

    def _make_request(self, url: str) -> Optional[dict]:
        """发送HTTP请求"""
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"请求失败: {e}")
            return None

    def search(self, query: str, max_results: int = 20) -> List[str]:
        """
        搜索PubMed文献

        Args:
            query: 检索式
            max_results: 最大返回结果数

        Returns:
            PubMed ID列表
        """
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'json',
            'sort': 'relevance'
        }

        url = f"{self.ESEARCH_URL}?{urllib.parse.urlencode(params)}"
        self._rate_limit()

        result = self._make_request(url)
        if result and 'esearchresult' in result:
            return result['esearchresult'].get('idlist', [])
        return []

    def get_summaries(self, pmids: List[str]) -> List[Dict]:
        """
        获取文献摘要信息

        Args:
            pmids: PubMed ID列表

        Returns:
            文献摘要信息列表
        """
        if not pmids:
            return []

        params = {
            'db': 'pubmed',
            'id': ','.join(pmids),
            'retmode': 'json'
        }

        url = f"{self.ESUMMARY_URL}?{urllib.parse.urlencode(params)}"
        self._rate_limit()

        result = self._make_request(url)
        if result and 'result' in result:
            return [result['result'].get(pmid, {}) for pmid in pmids]
        return []

    def get_details(self, pmids: List[str]) -> List[Dict]:
        """
        获取文献详细信息（包括摘要）

        Args:
            pmids: PubMed ID列表

        Returns:
            文献详细信息列表
        """
        if not pmids:
            return []

        params = {
            'db': 'pubmed',
            'id': ','.join(pmids),
            'retmode': 'xml'
        }

        url = f"{self.EFETCH_URL}?{urllib.parse.urlencode(params)}"
        self._rate_limit()

        try:
            import xml.etree.ElementTree as ET
            with urllib.request.urlopen(url, timeout=30) as response:
                tree = ET.parse(response)
                root = tree.getroot()

                articles = []
                for article in root.findall('.//PubmedArticle'):
                    title = article.findtext('.//ArticleTitle', '')
                    abstract = article.findtext('.//AbstractText', '')
                    authors = [a.findtext('LastName', '') for a in article.findall('.//Author') if a.findtext('LastName', '')]
                    journal = article.findtext('.//Journal/Title', '')
                    year = article.findtext('.//PubDate/Year', '')

                    articles.append({
                        'title': title,
                        'abstract': abstract,
                        'authors': authors,
                        'journal': journal,
                        'year': year
                    })
                return articles
        except Exception as e:
            print(f"获取详情失败: {e}")
            return []


def build_search_query(keywords: Dict[str, List[str]]) -> str:
    """
    构建检索式

    Args:
        keywords: 关键词字典，包含 'main_terms', 'technical_features', 'restrictions'

    Returns:
        检索式字符串
    """
    parts = []

    if keywords.get('main_terms'):
        main = ' OR '.join(f'"{t}"' for t in keywords['main_terms'])
        parts.append(f"({main})")

    if keywords.get('technical_features'):
        features = ' OR '.join(f'"{t}"' for t in keywords['technical_features'])
        parts.append(f"({features})")

    if keywords.get('restrictions'):
        parts.append(f"({keywords['restrictions']})")

    return ' AND '.join(parts) if parts else ''


def main():
    """测试脚本"""
    searcher = PubMedSearcher()

    # 测试检索式
    test_query = "(CRISPR OR gene editing) AND (cancer therapy)"

    print(f"执行检索: {test_query}")
    pmids = searcher.search(test_query, max_results=5)

    print(f"找到 {len(pmids)} 篇文献")

    if pmids:
        print("\n获取摘要信息...")
        articles = searcher.get_details(pmids[:3])

        for i, article in enumerate(articles, 1):
            print(f"\n--- 文献 {i} ---")
            print(f"标题: {article.get('title', 'N/A')}")
            print(f"作者: {', '.join(article.get('authors', [])[:3])}...")
            print(f"期刊: {article.get('journal', 'N/A')}")
            print(f"年份: {article.get('year', 'N/A')}")
            print(f"摘要: {article.get('abstract', 'N/A')[:200]}...")


if __name__ == "__main__":
    main()