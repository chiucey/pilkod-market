#!/usr/bin/env python3
"""
OpenClaw Model Selector - Automatically selects optimal AI model based on task type
"""

import argparse
import json
import re
import sys
from typing import Dict, List, Tuple, Optional


# Model capabilities configuration
MODEL_CAPABILITIES = {
    "sonnet": {
        "name": "Claude Sonnet",
        "strengths": ["code", "analysis", "reasoning", "technical docs"],
        "speed": "medium",
        "context_window": 200000,
        "best_for": ["complex analysis", "code review", "technical writing"]
    },
    "opus": {
        "name": "Claude Opus",
        "strengths": ["deep reasoning", "complex tasks", "long text", "technical docs"],
        "speed": "slow",
        "context_window": 200000,
        "best_for": ["deep research", "complex programming", "system design"]
    },
    "haiku": {
        "name": "Claude Haiku",
        "strengths": ["fast response", "simple Q&A", "daily tasks"],
        "speed": "fast",
        "context_window": 200000,
        "best_for": ["quick queries", "simple translation", "info retrieval"]
    },
    "gpt-4": {
        "name": "GPT-4",
        "strengths": ["creative writing", "code", "analysis", "math"],
        "speed": "slow",
        "context_window": 128000,
        "best_for": ["creative writing", "complex reasoning", "multilingual tasks"]
    },
    "gpt-3.5-turbo": {
        "name": "GPT-3.5 Turbo",
        "strengths": ["fast response", "simple tasks", "daily conversation"],
        "speed": "fast",
        "context_window": 16385,
        "best_for": ["quick Q&A", "simple writing", "translation"]
    },
    "claude-code": {
        "name": "Claude Code",
        "strengths": ["code generation", "code debugging", "code review", "technical implementation"],
        "speed": "medium",
        "context_window": 200000,
        "best_for": ["programming tasks", "code optimization", "bug fixing"]
    }
}

# Task keyword mapping (with priority levels)
TASK_KEYWORDS = {
    "code-programming": {
        "keywords": {
            "high": ["python", "java", "javascript", "code", "programming", "function", "def", "class ", "bug", "debug", "algorithm", "compile", "syntax", "quicksort", "sorting", "开发", "代码", "编程", "函数", "程序"],
            "medium": ["write", "implement", "create", "写", "写程序", "实现"],
            "low": []
        },
        "weight": 0.9,
        "models": ["claude-code", "sonnet", "opus", "gpt-4"]
    },
    "creative-writing": {
        "keywords": {
            "high": ["story", "novel", "poem", "essay", "creative", "fiction", "故事", "小说", "诗歌", "散文", "剧本"],
            "medium": ["write", "create", "compose", "写", "创作", "文案", "广告", "宣传"],
            "low": ["article", "文章"]
        },
        "weight": 0.8,
        "models": ["gpt-4", "sonnet", "opus"]
    },
    "technical-analysis": {
        "keywords": {
            "high": ["analyze", "explain", "principle", "why", "how", "compare", "analyze", "分析", "解释", "原理"],
            "medium": ["compare", "evaluate", "assess", "对比", "比较", "评估", "原因"],
            "low": []
        },
        "weight": 0.85,
        "models": ["opus", "sonnet", "gpt-4"]
    },
    "quick-qa": {
        "keywords": {
            "high": ["what is", "how to", "how many", "who", "what", "when", "where", "weather", "什么是", "怎么", "多少", "天气"],
            "medium": ["time", "date", "definition", "时间", "日期", "定义"],
            "low": []
        },
        "weight": 0.7,
        "models": ["haiku", "gpt-3.5-turbo", "sonnet"]
    },
    "math-calculation": {
        "keywords": {
            "high": ["calculate", "math", "equation", "formula", "solve", "proof", "计算", "数学", "公式", "解题", "证明", "2+2"],
            "medium": [],
            "low": []
        },
        "weight": 0.85,
        "models": ["opus", "gpt-4", "sonnet"]
    },
    "translation": {
        "keywords": {
            "high": ["translate", "translation", "convert to", "翻译", "translate", "英译", "中译", "翻译成", "语言转换"],
            "medium": ["convert"],
            "low": []
        },
        "weight": 0.75,
        "models": ["gpt-4", "sonnet", "haiku"]
    },
    "data-processing": {
        "keywords": {
            "high": ["data", "statistics", "table", "csv", "excel", "database", "sales data", "data analysis", "数据分析", "数据处理", "统计", "表格", "销售数据", "数据库", "sales"],
            "medium": ["analyze", "query", "analysis", "分析", "查询"],
            "low": []
        },
        "weight": 0.8,
        "models": ["sonnet", "opus", "gpt-4"]
    },
    "system-design": {
        "keywords": {
            "high": ["design", "architecture", "system", "架构", "系统", "架构设计"],
            "medium": ["plan", "scheme", "design", "方案", "login system", "登录系统"],
            "low": []
        },
        "weight": 0.9,
        "models": ["opus", "sonnet", "gpt-4"]
    }
}


def analyze_task(task_text: str) -> Dict[str, any]:
    """
    Analyze task text and return task characteristics
    Supports keyword priority: high > medium > low
    """
    task_lower = task_text.lower()
    task_scores = {}

    for task_type, config in TASK_KEYWORDS.items():
        score = 0
        high_matches = 0
        medium_matches = 0
        low_matches = 0

        # High priority keywords
        for keyword in config["keywords"]["high"]:
            if keyword.lower() in task_lower:
                high_matches += 1
                score += config["weight"] * 3  # High priority weight

        # Medium priority keywords
        for keyword in config["keywords"]["medium"]:
            if keyword.lower() in task_lower:
                medium_matches += 1
                score += config["weight"] * 2  # Medium priority weight

        # Low priority keywords
        for keyword in config["keywords"]["low"]:
            if keyword.lower() in task_lower:
                low_matches += 1
                score += config["weight"]  # Low priority weight

        total_matches = high_matches + medium_matches + low_matches
        if total_matches > 0:
            task_scores[task_type] = {
                "score": score,
                "high_matches": high_matches,
                "medium_matches": medium_matches,
                "low_matches": low_matches,
                "total_matches": total_matches,
                "recommended_models": config["models"]
            }

    # Determine primary task type
    if task_scores:
        primary_task = max(task_scores.items(), key=lambda x: x[1]["score"])
        primary_task_type = primary_task[0]
        recommended_models = primary_task[1]["recommended_models"]
    else:
        primary_task_type = "general"
        recommended_models = ["sonnet", "gpt-4"]

    # Complexity assessment
    complexity_indicators = {
        "complex": ["detailed", "complete", "thorough", "comprehensive", "full", "详细", "完整", "深入", "全面", "详细说明", "完整地", "implement a"],
        "simple": ["simple", "quick", "brief", "fast", "帮我", "just", "only", "简单", "快速", "一下", "只要"]
    }

    complexity = "medium"
    if any(ind in task_lower for ind in complexity_indicators["complex"]):
        complexity = "high"
    elif any(ind in task_lower for ind in complexity_indicators["simple"]):
        complexity = "low"

    # Speed requirement assessment
    speed_keywords = {
        "fast": ["fast", "immediately", "asap", "urgent", "quickly", "快速", "马上", "立刻", "尽快", "紧急", "快一点"],
        "slow": ["detailed", "thorough", "comprehensive", "slowly", "详细", "深入", "全面", "慢慢", "详细地"]
    }

    speed_preference = "balanced"
    if any(ind in task_lower for ind in speed_keywords["fast"]):
        speed_preference = "fast"
    elif any(ind in task_lower for ind in speed_keywords["slow"]):
        speed_preference = "quality"

    return {
        "primary_task": primary_task_type,
        "task_scores": task_scores,
        "complexity": complexity,
        "speed_preference": speed_preference,
        "recommended_models": recommended_models
    }


def select_best_model(task_analysis: Dict, available_models: Optional[List[str]] = None) -> str:
    """
    Select optimal model based on task analysis
    """
    recommended = task_analysis["recommended_models"]
    complexity = task_analysis["complexity"]
    speed_pref = task_analysis["speed_preference"]

    if available_models is None:
        available_models = list(MODEL_CAPABILITIES.keys())

    # Priority ranking
    candidates = []

    for model_id in recommended:
        if model_id not in available_models:
            continue

        model = MODEL_CAPABILITIES[model_id]
        score = 100

        # Speed matching
        if speed_pref == "fast" and model["speed"] == "fast":
            score += 30
        elif speed_pref == "quality" and model["speed"] == "slow":
            score += 20

        # Complexity matching
        if complexity == "high" and model["speed"] in ["medium", "slow"]:
            score += 20
        elif complexity == "low" and model["speed"] == "fast":
            score += 25

        candidates.append((model_id, score, model))

    # Sort by score
    candidates.sort(key=lambda x: x[1], reverse=True)

    if candidates:
        return candidates[0][0]

    # Default selection
    return "sonnet"


def generate_switch_command(model_id: str) -> str:
    """
    Generate model switch command
    """
    return f"/set model {model_id}"


def main():
    parser = argparse.ArgumentParser(description="OpenClaw Model Auto-Selector")
    parser.add_argument("--task", "-t", required=True, help="Task description")
    parser.add_argument("--list-models", "-l", action="store_true", help="List available models")
    parser.add_argument("--explain", "-e", action="store_true", help="Show selection reasoning")
    parser.add_argument("--command", "-c", action="store_true", help="Output switch command")

    args = parser.parse_args()

    if args.list_models:
        print("Available models:")
        print("-" * 60)
        for model_id, model in MODEL_CAPABILITIES.items():
            print(f"\n{model['name']} ({model_id})")
            print(f"  Strengths: {', '.join(model['strengths'])}")
            print(f"  Speed: {model['speed']}")
            print(f"  Best for: {', '.join(model['best_for'])}")
        return 0

    # Analyze task
    task_analysis = analyze_task(args.task)

    # Select model
    best_model = select_best_model(task_analysis)
    model_info = MODEL_CAPABILITIES.get(best_model, MODEL_CAPABILITIES["sonnet"])

    print(f"\nTask Analysis Result:")
    print(f"  Primary task type: {task_analysis['primary_task']}")
    print(f"  Complexity: {task_analysis['complexity']}")
    print(f"  Speed preference: {task_analysis['speed_preference']}")

    if args.explain:
        print(f"\nSelection Reasoning:")
        print(f"  Recommended model: {model_info['name']} ({best_model})")
        print(f"  Strengths: {', '.join(model_info['strengths'])}")
        print(f"  Best scenarios: {', '.join(model_info['best_for'])}")
    else:
        print(f"\nRecommended model: {model_info['name']} ({best_model})")

    if args.command:
        cmd = generate_switch_command(best_model)
        print(f"\nSwitch command: {cmd}")

    # Return JSON format for programmatic use
    result = {
        "model_id": best_model,
        "model_name": model_info["name"],
        "analysis": task_analysis,
        "command": generate_switch_command(best_model)
    }

    # Output JSON if requested (for script integration)
    if "--json" in sys.argv:
        print("\n" + json.dumps(result, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
