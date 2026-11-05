#!/usr/bin/env python3
"""
Template: inject final data JSON into the listening-page HTML template.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def slugify(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_-]+", "_", text.strip()).strip("_")
    return slug or "study_page"


def to_template_data(data: dict | list) -> list[dict]:
    sentences = data["sentences"] if isinstance(data, dict) else data
    out = []
    for sentence in sentences:
        item = {
            "t": sentence.get("text") or sentence.get("t", ""),
            "z": sentence.get("translation") or sentence.get("z", ""),
            "s": round(float(sentence.get("s", sentence.get("start", 0))), 2),
            "e": round(float(sentence.get("e", sentence.get("end", 0))), 2),
            "a": sentence.get("a", ""),
            "w": [
                {
                    "t": word.get("text") or word.get("t", ""),
                    "s": round(float(word.get("s", word.get("start", 0))), 2),
                    "e": round(float(word.get("e", word.get("end", 0))), 2),
                }
                for word in sentence.get("words", sentence.get("w", []))
            ],
        }
        if sentence.get("rh"):
            item["rh"] = sentence["rh"]
        if sentence.get("r"):
            item["r"] = sentence["r"]
        if sentence.get("c"):
            item["c"] = sentence["c"]
        out.append(item)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--id", default=None)
    args = parser.parse_args()

    template = Path(args.template).read_text(encoding="utf-8")
    raw_data = json.loads(Path(args.data).read_text(encoding="utf-8"))
    template_data = to_template_data(raw_data)
    page_id = args.id or slugify(args.title)

    html = template
    html = html.replace("{{TITLE}}", args.title)
    html = html.replace("{{ID}}", page_id)
    html = html.replace(
        "{{DATA_JSON}}",
        json.dumps(template_data, ensure_ascii=False, separators=(",", ":")),
    )
    Path(args.out).write_text(html, encoding="utf-8")
    print(f"Wrote HTML to {args.out}")


if __name__ == "__main__":
    main()
