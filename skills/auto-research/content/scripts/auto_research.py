#!/usr/bin/env python3
"""
auto_research.py — 研究迭代循环配置器
用法: python3 auto_research.py [topic] [rounds]
"""
import json
import sys
import os
from datetime import datetime

def main():
    topic = sys.argv[1] if len(sys.argv) > 1 else "未指定课题"
    rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    
    config = {
        "topic": topic,
        "rounds": rounds,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "strategy": "progressive_deepening",
        "scoring": {
            "relevance_threshold": 0.6,
            "keep_top_n": 5,
            "decay_factor": 0.85
        },
        "search_config": {
            "queries_per_round": 3,
            "sources_per_query": 5,
            "use_breadth_first": False
        },
        "output_format": "markdown",
        "workspace": os.path.expanduser("~/.openclaw/auto_research/")
    }
    
    print(json.dumps(config, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
