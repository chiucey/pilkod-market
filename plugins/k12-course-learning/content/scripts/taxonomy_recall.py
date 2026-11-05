#!/usr/bin/env python3
"""Offline retrieval over the bundled Marble Skill Taxonomy.

Uses only the Python standard library. It never calls the network and never
stores learner state.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import defaultdict, deque
from pathlib import Path
from typing import Any


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PLUGIN_ROOT / "data" / "os-taxonomy" / "data"
ALIASES_PATH = PLUGIN_ROOT / "data" / "query-aliases.zh-CN.json"
SOURCE_PATH = PLUGIN_ROOT / "data" / "SOURCE.json"


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise SystemExit(f"Missing bundled data file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc


def normalize(value: str) -> str:
    folded = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(re.findall(r"[a-z0-9]+|[\u3400-\u9fff]+", folded))


def tokens(value: str) -> list[str]:
    return [part for part in normalize(value).split() if len(part) > 1]


def expand_query(query: str, aliases: dict[str, Any]) -> str:
    additions: list[str] = []
    for phrase, english in aliases.get("phrases", {}).items():
        if phrase in query:
            additions.append(english)
    return " ".join([query, *additions]).strip()


def canonical_subject(subject: str | None, aliases: dict[str, Any]) -> str | None:
    if not subject:
        return None
    return aliases.get("subjects", {}).get(subject, subject)


def topic_text(topic: dict[str, Any]) -> dict[str, str]:
    return {
        "name": normalize(topic.get("name", "")),
        "domain": normalize(topic.get("domain", "")),
        "description": normalize(topic.get("description", "")),
        "evidence": normalize(" ".join(topic.get("evidence", []))),
        "standards": normalize(" ".join(topic.get("standards", []))),
    }


def score_topic(topic: dict[str, Any], query: str) -> float:
    if not query:
        return float(topic.get("centrality", 0)) * 10

    fields = topic_text(topic)
    phrase = normalize(query)
    query_tokens = tokens(query)
    score = 0.0

    if phrase == fields["name"]:
        score += 120
    elif phrase and phrase in fields["name"]:
        score += 70
    if phrase and phrase in fields["description"]:
        score += 24

    weights = {
        "name": 22,
        "domain": 11,
        "description": 5,
        "evidence": 3,
        "standards": 1,
    }
    for token in query_tokens:
        for field, weight in weights.items():
            if token in fields[field]:
                score += weight

    matched = sum(1 for token in query_tokens if any(token in value for value in fields.values()))
    if query_tokens and matched == len(query_tokens):
        score += 15
    score += float(topic.get("centrality", 0)) * 4
    return score


def topic_matches(
    topic: dict[str, Any],
    *,
    subject: str | None,
    domain: str | None,
    age: int | None,
    topic_type: str | None,
) -> bool:
    if subject and normalize(subject) not in normalize(topic.get("subject", "")):
        return False
    if domain and normalize(domain) not in normalize(topic.get("domain", "")):
        return False
    if age is not None and not (
        int(topic.get("ageRangeStart", -1)) <= age <= int(topic.get("ageRangeEnd", 10_000))
    ):
        return False
    if topic_type and normalize(topic_type) != normalize(topic.get("type", "")):
        return False
    return True


def concise_topic(topic: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "id",
        "type",
        "subject",
        "domain",
        "name",
        "description",
        "ageRangeStart",
        "ageRangeEnd",
        "centrality",
        "evidence",
        "assessmentPrompt",
        "standards",
    )
    return {key: topic.get(key) for key in keys if key in topic}


def build_graph(
    dependencies: list[dict[str, Any]],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[dict[str, Any]]]]:
    prerequisites: dict[str, list[dict[str, Any]]] = defaultdict(list)
    unlocks: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in dependencies:
        prerequisites[edge["topicId"]].append(edge)
        unlocks[edge["prerequisiteId"]].append(edge)
    return prerequisites, unlocks


def walk_graph(
    start_id: str,
    adjacency: dict[str, list[dict[str, Any]]],
    by_id: dict[str, dict[str, Any]],
    *,
    direction: str,
    max_depth: int,
) -> list[dict[str, Any]]:
    if max_depth <= 0:
        return []
    queue: deque[tuple[str, int]] = deque([(start_id, 0)])
    visited = {start_id}
    found: list[dict[str, Any]] = []
    while queue:
        current, depth = queue.popleft()
        if depth >= max_depth:
            continue
        for edge in adjacency.get(current, []):
            next_id = edge["prerequisiteId"] if direction == "prerequisite" else edge["topicId"]
            if next_id in visited:
                continue
            visited.add(next_id)
            related = by_id.get(next_id)
            if related is None:
                continue
            found.append(
                {
                    "depth": depth + 1,
                    "strength": edge.get("strength"),
                    "reason": edge.get("reason"),
                    "topic": concise_topic(related),
                }
            )
            queue.append((next_id, depth + 1))
    return found


def attribution() -> dict[str, Any]:
    return load_json(SOURCE_PATH)


def search(args: argparse.Namespace) -> dict[str, Any]:
    topics = load_json(DATA_ROOT / "topics.json").get("topics", [])
    dependencies = load_json(DATA_ROOT / "dependencies.json").get("dependencies", [])
    aliases = load_json(ALIASES_PATH)
    subject = canonical_subject(args.subject, aliases)
    expanded = expand_query(args.query or "", aliases)
    prerequisites, unlocks = build_graph(dependencies)

    ranked: list[tuple[float, dict[str, Any]]] = []
    for topic in topics:
        if not topic_matches(
            topic,
            subject=subject,
            domain=args.domain,
            age=args.age,
            topic_type=args.topic_type,
        ):
            continue
        score = score_topic(topic, expanded)
        if expanded and score <= 0:
            continue
        ranked.append((score, topic))
    ranked.sort(key=lambda item: (item[0], item[1].get("centrality", 0)), reverse=True)

    results = []
    for score, topic in ranked[: args.limit]:
        item = concise_topic(topic)
        item["score"] = round(score, 3)
        item["directPrerequisiteCount"] = len(prerequisites.get(topic["id"], []))
        item["directUnlockCount"] = len(unlocks.get(topic["id"], []))
        results.append(item)
    return {
        "mode": "search",
        "query": args.query or "",
        "expandedQuery": expanded,
        "filters": {
            "subject": subject,
            "domain": args.domain,
            "age": args.age,
            "type": args.topic_type,
        },
        "count": len(results),
        "results": results,
        "source": attribution(),
    }


def inspect_topic(args: argparse.Namespace) -> dict[str, Any]:
    topics = load_json(DATA_ROOT / "topics.json").get("topics", [])
    dependencies = load_json(DATA_ROOT / "dependencies.json").get("dependencies", [])
    by_id = {topic["id"]: topic for topic in topics}
    topic = by_id.get(args.topic_id)
    if topic is None:
        raise SystemExit(f"Unknown topic id: {args.topic_id}")
    prerequisites, unlocks = build_graph(dependencies)
    return {
        "mode": "topic",
        "topic": concise_topic(topic),
        "prerequisites": walk_graph(
            args.topic_id,
            prerequisites,
            by_id,
            direction="prerequisite",
            max_depth=args.depth,
        ),
        "unlocks": walk_graph(
            args.topic_id,
            unlocks,
            by_id,
            direction="unlock",
            max_depth=args.depth,
        ),
        "source": attribution(),
    }


def list_subjects() -> dict[str, Any]:
    topics = load_json(DATA_ROOT / "topics.json").get("topics", [])
    summary: dict[str, dict[str, Any]] = {}
    for topic in topics:
        subject = topic["subject"]
        item = summary.setdefault(subject, {"subject": subject, "topics": 0, "domains": set()})
        item["topics"] += 1
        item["domains"].add(topic["domain"])
    results = []
    for item in sorted(summary.values(), key=lambda value: value["subject"]):
        results.append(
            {
                "subject": item["subject"],
                "topics": item["topics"],
                "domains": sorted(item["domains"]),
            }
        )
    return {"mode": "subjects", "results": results, "source": attribution()}


def print_text(payload: dict[str, Any]) -> None:
    if payload["mode"] == "subjects":
        for item in payload["results"]:
            print(f"{item['subject']}: {item['topics']} topics")
            print("  " + ", ".join(item["domains"]))
        return

    if payload["mode"] == "search":
        print(f"Query: {payload['query'] or '(all)'}")
        if payload["expandedQuery"] != payload["query"]:
            print(f"Expanded: {payload['expandedQuery']}")
        print(f"Results: {payload['count']}")
        for index, topic in enumerate(payload["results"], 1):
            ages = f"{topic['ageRangeStart']}-{topic['ageRangeEnd']}"
            print(f"\n{index}. {topic['name']} [{topic['id']}]")
            print(f"   {topic['subject']} / {topic['domain']} / ages {ages} / score {topic['score']}")
            print(f"   {topic['description']}")
            print(
                "   graph: "
                f"{topic['directPrerequisiteCount']} prerequisites, "
                f"{topic['directUnlockCount']} unlocks"
            )
        return

    topic = payload["topic"]
    print(f"{topic['name']} [{topic['id']}]")
    print(f"{topic['subject']} / {topic['domain']} / ages {topic['ageRangeStart']}-{topic['ageRangeEnd']}")
    print(topic["description"])
    for label, key in (("Prerequisites", "prerequisites"), ("Unlocks", "unlocks")):
        print(f"\n{label}:")
        if not payload[key]:
            print("  (none in selected depth)")
        for item in payload[key]:
            print(
                f"  d{item['depth']} {item['topic']['name']} [{item['topic']['id']}] "
                f"({item['strength']}): {item['reason']}"
            )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Search the bundled K12 taxonomy without network access or authentication."
    )
    parser.add_argument("-q", "--query", help="Keyword query; common Chinese terms are expanded locally.")
    parser.add_argument("--subject", help="Subject filter, e.g. Mathematics, Science, 数学, 科学.")
    parser.add_argument("--domain", help="Case-insensitive domain filter.")
    parser.add_argument("--age", type=int, help="Keep topics whose age range contains this age.")
    parser.add_argument("--type", dest="topic_type", help="CONCEPTUAL, PROCEDURAL, REPRESENTATIONAL, LANGUAGE, or META.")
    parser.add_argument("--topic-id", help="Inspect one topic and its graph instead of searching.")
    parser.add_argument("--depth", type=int, default=1, choices=range(0, 6), help="Graph depth for --topic-id (0-5).")
    parser.add_argument("--limit", type=int, default=8, choices=range(1, 51), help="Maximum search results (1-50).")
    parser.add_argument("--list-subjects", action="store_true", help="List subjects and domains.")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.list_subjects:
        payload = list_subjects()
    elif args.topic_id:
        payload = inspect_topic(args)
    else:
        payload = search(args)
    if args.format == "json":
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        print()
    else:
        print_text(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
