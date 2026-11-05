#!/usr/bin/env python3
"""
PubMed Active Monitor - Active Monitoring and State Management

Features:
1. Maintain pushed article state
2. Detect new articles
3. Generate diff reports
4. Support scheduled task integration
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Set, Optional
from pathlib import Path

# Import search module
from pubmed_search import PubMedSearcher, generate_summary_report


class PubMedActiveMonitor:
    """PubMed Active Monitor"""

    def __init__(self, state_file: str = "monitor_state.json"):
        """Initialize monitor

        Args:
            state_file: State file path
        """
        self.state_file = state_file
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """Load state file"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Failed to load state: {e}")

        return {
            "pushed_pmids": [],
            "last_check": None,
            "monitored_topics": {}
        }

    def _save_state(self):
        """Save state file"""
        self.state["last_check"] = datetime.now().isoformat()
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to save state: {e}")

    def add_topic(self, topic: str, query: str, priority: int = 1):
        """Add monitoring topic

        Args:
            topic: Topic name
            query: PubMed query string
            priority: Priority (1=high, 2=medium, 3=low)
        """
        self.state["monitored_topics"][topic] = {
            "query": query,
            "priority": priority,
            "added_at": datetime.now().isoformat()
        }
        self._save_state()

    def remove_topic(self, topic: str):
        """Remove monitoring topic"""
        if topic in self.state["monitored_topics"]:
            del self.state["monitored_topics"][topic]
            self._save_state()

    def get_new_articles(
        self,
        topic: str,
        query: str,
        days_back: int = 7
    ) -> List[Dict]:
        """Get new articles

        Args:
            topic: Monitoring topic
            query: PubMed query string
            days_back: Search recent days

        Returns:
            List of new articles
        """
        searcher = PubMedSearcher()
        pmids = searcher.search(query, max_results=50, days_back=days_back)

        pushed_pmids: Set[str] = set(self.state["pushed_pmids"])
        new_pmids = [pmid for pmid in pmids if pmid not in pushed_pmids]

        if new_pmids:
            articles = searcher.get_article_details(new_pmids)
            return articles

        return []

    def check_all_topics(self, days_back: int = 7) -> Dict[str, List[Dict]]:
        """Check all monitoring topics

        Args:
            days_back: Search recent days

        Returns:
            Dict of new articles by topic
        """
        results = {}
        all_new_articles = []

        # Sort by priority
        sorted_topics = sorted(
            self.state["monitored_topics"].items(),
            key=lambda x: x[1].get("priority", 2)
        )

        for topic, config in sorted_topics:
            print(f"\nChecking topic: {topic}")
            articles = self.get_new_articles(
                topic,
                config["query"],
                days_back
            )

            if articles:
                results[topic] = articles
                all_new_articles.extend(articles)
                print(f"  Found {len(articles)} new articles")
            else:
                print(f"  No new articles found")

            # Mark as pushed
            for article in articles:
                if article["pmid"] not in self.state["pushed_pmids"]:
                    self.state["pushed_pmids"].append(article["pmid"])

        self._save_state()
        return results

    def generate_push_report(self, results: Dict[str, List[Dict]]) -> str:
        """Generate push report

        Args:
            results: Dict of new articles by topic

        Returns:
            Formatted push report
        """
        if not results:
            return "## Literature Push Report\n\nNo new articles found."

        total_count = sum(len(articles) for articles in results.values())

        report = f"""## PubMed Literature Active Push Report

**Push Time**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Monitored Topics**: {len(results)}
**Total New Articles**: {total_count}

---

"""

        for topic, articles in results.items():
            topic_report = generate_summary_report(articles, topic)
            # Remove title section (already in main report)
            topic_report = topic_report.split("---", 1)[-1] if "---" in topic_report else topic_report
            report += f"### 【{topic}】\n\n{topic_report}\n"

        return report

    def get_status(self) -> str:
        """Get monitoring status"""
        topics = self.state["monitored_topics"]
        pushed_count = len(self.state["pushed_pmids"])
        last_check = self.state.get("last_check", "Never")

        status = f"""## PubMed Active Monitor Status

**Last Check**: {last_check}
**Pushed Articles**: {pushed_count}
**Monitored Topics**: {len(topics)}

### Monitored Topics List

| Topic | Priority | Query |
|------|----------|-------|
"""
        for topic, config in topics.items():
            priority_map = {1: "High", 2: "Medium", 3: "Low"}
            priority = priority_map.get(config.get("priority", 2), "Medium")
            query = config.get("query", "")[:50] + "..." if len(config.get("query", "")) > 50 else config.get("query", "")
            status += f"| {topic} | {priority} | {query} |\n"

        return status


def main():
    """Main function - demo usage"""
    monitor = PubMedActiveMonitor()

    # Add monitoring topics
    monitor.add_topic(
        "CSCO Guidelines",
        'CSCO[Title/Abstract] AND (guideline[Title/Abstract] OR consensus[Title/Abstract])',
        priority=1
    )

    monitor.add_topic(
        "Cancer Immunotherapy",
        'immunotherapy[Title/Abstract] AND (cancer[Title/Abstract] OR oncology[MeSH Terms])',
        priority=2
    )

    monitor.add_topic(
        "Precision Medicine",
        'precision medicine[Title/Abstract] AND biomarker[Title/Abstract]',
        priority=2
    )

    # Check all topics
    results = monitor.check_all_topics(days_back=7)

    # Generate push report
    report = monitor.generate_push_report(results)
    print(report)

    # Show status
    print("\n" + monitor.get_status())


if __name__ == "__main__":
    main()
