#!/usr/bin/env python3
"""Build the exact Weread Atlas single HTML from normalized real data."""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path


COLORS = (
    "#6b4c8f",
    "#f0c33c",
    "#c84a3e",
    "#2a8a7a",
    "#f4a8b8",
    "#8eb4d4",
    "#a8c8a0",
    "#b8a4d4",
)
YEAR_CLIPS = (
    "clip-4-lamp.png",
    "clip-3-magnifier.png",
    "clip-9-journal.png",
    "clip-2-book-stack.png",
    "clip-7-cup.png",
    "clip-12-coffee.png",
)
STICKERS = (
    ("c-pink", "SLOW"),
    ("c-blue", "BUILD"),
    ("c-yellow", "CARE"),
    ("c-green", "FOCUS"),
    ("c-blue", "QUIET"),
    ("c-green", "FIRST"),
)
CANONICAL_CATEGORIES = (
    ("c-lit", "文学"),
    ("c-edu", "教育学习"),
    ("c-hist", "历史"),
    ("c-sci", "科技"),
    ("c-med", "医学健康"),
    ("c-eco", "经济商业"),
    ("c-bio", "人物传记"),
    ("c-life", "生活百科"),
)
ASSET_TOKEN_PREFIX = "__MRC_ASSET_DATA_URI__/"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Normalized atlas-data.json")
    parser.add_argument("--output", required=True, help="Output single HTML")
    parser.add_argument("--template", help="Optional exact-template override")
    return parser.parse_args()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def hydrate_template_assets(template: str, template_path: Path) -> str:
    """Inline deduplicated template images so the deliverable stays single-file."""
    asset_dir = template_path.parent / "template-images"
    text_bundles = sorted(template_path.parent.glob("template-images-data-*.json"))
    if ASSET_TOKEN_PREFIX not in template:
        return template

    if text_bundles:
        bundled_assets: dict[str, str] = {}
        for bundle_path in text_bundles:
            bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
            require(isinstance(bundle, dict), f"invalid template image bundle: {bundle_path}")
            assets = bundle.get("assets", bundle)
            require(isinstance(assets, dict), f"invalid template image map: {bundle_path}")
            bundled_assets.update({str(key): str(value) for key, value in assets.items()})
        for token, data_uri in bundled_assets.items():
            if token in template:
                template = template.replace(token, data_uri)
    else:
        require(asset_dir.is_dir(), f"template image resources are missing: {asset_dir}")
        for asset_path in sorted(asset_dir.iterdir()):
            if not asset_path.is_file():
                continue
            token = ASSET_TOKEN_PREFIX + asset_path.name
            if token not in template:
                continue
            suffix = asset_path.suffix.lower()
            mime = "image/png" if suffix == ".png" else "image/jpeg"
            encoded = base64.b64encode(asset_path.read_bytes()).decode("ascii")
            template = template.replace(token, f"data:{mime};base64,{encoded}")

    require(ASSET_TOKEN_PREFIX not in template, "unresolved template image token remains")
    return template


def number(value: object, default: float = 0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def slug_category(name: str, index: int) -> str:
    text = name or ""
    rules = (
        ("文学", "c-lit"),
        ("小说", "c-lit"),
        ("教育", "c-edu"),
        ("学习", "c-edu"),
        ("历史", "c-hist"),
        ("社会", "c-hist"),
        ("科技", "c-sci"),
        ("科幻", "c-sci"),
        ("医学", "c-med"),
        ("健康", "c-med"),
        ("心理", "c-med"),
        ("经济", "c-eco"),
        ("商业", "c-eco"),
        ("理财", "c-eco"),
        ("传记", "c-bio"),
        ("人物", "c-bio"),
        ("生活", "c-life"),
        ("艺术", "c-life"),
    )
    for keyword, category_id in rules:
        if keyword in text:
            return category_id
    return CANONICAL_CATEGORIES[index % len(CANONICAL_CATEGORIES)][0]


def validate(data: dict) -> None:
    meta = data.get("meta")
    require(isinstance(meta, dict), "meta must be an object")
    for key in ("title",):
        require(key in meta, f"meta.{key} is required")

    years = data.get("years", [])
    require(isinstance(years, list) and years, "years must contain reading years")
    year_values = []
    for year in years:
        require(isinstance(year.get("year"), int), "year.year must be an integer")
        year_values.append(year["year"])
        require(isinstance(year.get("stats"), dict), "year.stats must be an object")
        books = year.get("books", [])
        require(isinstance(books, list), "year.books must be an array")
        require(len(books) <= 8, "each year supports at most eight representative books")
    require(len(year_values) == len(set(year_values)), "years must not contain duplicates")

    notes = data.get("notes", [])
    require(isinstance(notes, list), "notes must be an array")
    require(len(notes) <= 32, "notes supports at most 32 representative highlights")
    require(notes, "the exact themes and capsule modules require representative highlights")

    categories = data.get("categories", [])
    require(isinstance(categories, list) and categories, "categories must contain real data")
    require(len(categories) <= 8, "the exact template supports at most eight categories")
    share_total = sum(number(category.get("share", category.get("pct"))) for category in categories)
    require(99 <= share_total <= 101, f"category shares must total about 100, got {share_total}")

def distribute_counts(total: int, shares: list[float]) -> list[int]:
    raw = [total * share / 100 for share in shares]
    result = [int(value) for value in raw]
    remaining = total - sum(result)
    order = sorted(range(len(raw)), key=lambda index: raw[index] - result[index], reverse=True)
    for index in order[:remaining]:
        result[index] += 1
    return result


def normalize_categories(data: dict) -> tuple[list[dict], dict[str, str]]:
    source = data.get("categories", [])[:8]
    shares = [number(item.get("share", item.get("pct"))) for item in source]
    counts = distribute_counts(int(number(data["meta"]["totalBooks"])), shares)
    categories = []
    id_map = {}
    used_ids = set()
    for index, item in enumerate(source):
        category_id = slug_category(str(item.get("name", "")), index)
        if category_id in used_ids:
            category_id = next(
                canonical_id
                for canonical_id, _ in CANONICAL_CATEGORIES
                if canonical_id not in used_ids
            )
        used_ids.add(category_id)
        old_id = str(item.get("id", category_id))
        id_map[old_id] = category_id
        share = shares[index]
        categories.append(
            {
                "id": category_id,
                "name": str(item.get("name", CANONICAL_CATEGORIES[index][1])),
                "pct": round(share, 1),
                "color": str(item.get("color", COLORS[index])),
                "hours": round(
                    number(item.get("hours"), number(data["meta"]["totalHours"]) * share / 100),
                    1,
                ),
                "count": int(number(item.get("count"), counts[index])),
            }
        )
    return categories, id_map


def normalize_network(data: dict, categories: list[dict], id_map: dict[str, str]) -> dict:
    source = data.get("network") or {}
    authors = []
    for index, item in enumerate(source.get("authors", [])[:12]):
        authors.append(
            {
                "id": str(item.get("id", f"a-{index + 1}")),
                "name": str(item.get("name", f"作者 {index + 1}")),
                "read": max(1, int(number(item.get("read"), 1))),
            }
        )
    category_ids = {item["id"] for item in categories}
    edges = []
    for item in source.get("edges", []):
        target = id_map.get(str(item.get("to")), str(item.get("to")))
        if target in category_ids:
            edges.append(
                {
                    "from": str(item.get("from")),
                    "to": target,
                    "w": max(1, int(number(item.get("w", item.get("weight")), 1))),
                }
            )
    if not edges and authors and categories:
        edges = [
            {
                "from": author["id"],
                "to": categories[index % len(categories)]["id"],
                "w": author["read"],
            }
            for index, author in enumerate(authors)
        ]
    return {
        "authors": authors,
        "categories": [
            {
                "id": item["id"],
                "name": item["name"],
                "color": item["color"],
                "share": item["pct"],
            }
            for item in categories
        ],
        "edges": edges,
    }


def normalize_years(data: dict) -> list[dict]:
    years = sorted(data.get("years", []), key=lambda item: item["year"], reverse=True)
    result = []
    for index, year in enumerate(years):
        books = []
        for book_index, book in enumerate(year.get("books", [])):
            books.append(
                {
                    "cat": str(book.get("cat", book.get("categoryCode", "READ"))).upper()[:6],
                    "pubYear": int(number(book.get("pubYear"), year["year"])),
                    "title": str(book.get("title", "")),
                    "author": str(book.get("author", "")),
                    "categoryId": slug_category(
                        str(book.get("category", book.get("cat", ""))),
                        book_index,
                    ),
                    "bg": str(book.get("bg", COLORS[(index + book_index) % len(COLORS)])),
                    "rating": max(0, min(5, int(number(book.get("rating"), 4)))),
                    "hours": round(number(book.get("hours")), 1),
                    "sum": str(book.get("sum", book.get("summary", ""))),
                    "cover": str(book.get("cover", "")),
                }
            )
        top_category = str(year.get("topCategory", year["stats"].get("topCategory", "")))
        sticker = STICKERS[index % len(STICKERS)]
        result.append(
            {
                "year": year["year"],
                "color": str(year.get("color", COLORS[index % len(COLORS)])),
                "mbti": str(year.get("mbti", f"READING YEAR · {top_category or 'ARCHIVE'}")),
                "mood": str(year.get("mood", top_category or "这一年的阅读")),
                "desc": str(year.get("desc", year.get("description", ""))),
                "books": books,
                "clip": YEAR_CLIPS[index % len(YEAR_CLIPS)],
                "sticker": {
                    "color": sticker[0],
                    "label": str(year.get("stickerLabel", top_category[:8] or "READ")),
                    "foot": sticker[1],
                },
                "stats": {
                    "hours": round(number(year["stats"].get("hours")), 1),
                    "books": int(number(year["stats"].get("books"))),
                    "days": int(number(year["stats"].get("days"))),
                    "notes": int(number(year["stats"].get("notes"))),
                    "topCategory": top_category,
                },
            }
        )
    return result


def adapt(data: dict) -> dict:
    validate(data)
    selected_years = data["years"]
    year_numbers = sorted(year["year"] for year in selected_years)
    derived_meta = {
        **data["meta"],
        "range": (
            str(year_numbers[0])
            if len(year_numbers) == 1
            else f"{year_numbers[0]}—{year_numbers[-1]}"
        ),
        "yearCount": len(year_numbers),
        "totalBooks": sum(
            int(number(year["stats"].get("books"))) for year in selected_years
        ),
        "totalHours": round(
            sum(number(year["stats"].get("hours")) for year in selected_years),
            1,
        ),
        "totalNotes": sum(
            int(number(year["stats"].get("notes"))) for year in selected_years
        ),
        "readDays": sum(
            int(number(year["stats"].get("days"))) for year in selected_years
        ),
    }
    normalized_source = {**data, "meta": derived_meta}
    categories, id_map = normalize_categories(normalized_source)
    years = normalize_years(normalized_source)
    year_stats = [
        {
            "year": year["year"],
            "hours": year["stats"]["hours"],
            "books": year["stats"]["books"],
            "notes": year["stats"]["notes"],
            "partial": bool(
                next(
                    (
                        source["stats"].get("partial")
                        for source in data["years"]
                        if source["year"] == year["year"]
                    ),
                    False,
                )
            ),
        }
        for year in sorted(years, key=lambda item: item["year"])
    ]
    notes = [
        {
            "book": str(item.get("book", "")),
            "date": str(item.get("date", "")),
            "text": str(item.get("text", "")),
            "theme": str(item.get("theme", "阅读")),
            "bookId": str(item.get("bookId", "")),
        }
        for item in data.get("notes", [])[:32]
    ]
    profile = data.get("profile") or data.get("aiProfile") or {}
    traits = [
        {
            "tag": str(item.get("tag", item.get("name", "阅读习惯"))),
            "detail": str(item.get("detail", "")),
        }
        for item in profile.get("traits", [])[:4]
    ]
    meta = derived_meta
    return {
        "meta": {
            "name": str(meta.get("name", "读者")),
            "range": str(meta["range"]),
            "yearCount": int(meta["yearCount"]),
            "totalBooks": int(number(meta["totalBooks"])),
            "totalHours": round(number(meta["totalHours"]), 1),
            "totalNotes": int(number(meta["totalNotes"])),
            "totalCategories": len(categories),
            "earliestRead": str(meta.get("earliestRead", "")),
            "latestRead": str(meta.get("latestRead", "")),
            "readDays": int(number(meta["readDays"])),
            "mbti": str(profile.get("mbti", profile.get("label", "READING PROFILE"))),
            "archetype": str(profile.get("archetype", "个人阅读侧写")),
            "isMock": bool(meta.get("isMock")),
        },
        "categories": categories,
        "preferTime": data.get("preferTime", [0] * 24),
        "preferTimeWord": str(data.get("preferTimeWord", "")),
        "preferAuthor": data.get("preferAuthor", []),
        "years": years,
        "yearStats": year_stats,
        "aiProfile": {
            "archetype": str(profile.get("archetype", "个人阅读侧写")),
            "summary": str(profile.get("summary", "")),
            "mbti": str(profile.get("mbti", profile.get("label", "READING PROFILE"))),
            "traits": traits,
        },
        "network": normalize_network(data, categories, id_map),
        "notes": notes,
        "timeCapsuleSeal": "A LETTER FROM {date} · 真实划过的一行",
        "hero": {
            "eyebrow": f"A FIELD GUIDE TO YOUR READING LIFE · {meta['range']}",
            "title": str(
                data.get("hero", {}).get(
                    "title",
                    "你读过的，\n都印在了 memory 里。",
                )
            ),
            "titleEm": "memory",
            "sub": (
                f"{number(meta['totalHours']):.1f} 小时，"
                f" {int(number(meta['readDays']))} 个阅读日，"
                f" {int(number(meta['totalNotes']))} 条笔记，"
                f" {int(number(meta['totalBooks']))} 本书。"
            ),
        },
    }


def main() -> None:
    args = parse_args()
    skill_root = Path(__file__).resolve().parent.parent
    template_path = (
        Path(args.template).expanduser().resolve()
        if args.template
        else skill_root / "assets" / "halftone-template.html"
    )
    data_path = Path(args.data).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    source_data = json.loads(data_path.read_text(encoding="utf-8"))
    atlas = adapt(source_data)
    template = hydrate_template_assets(
        template_path.read_text(encoding="utf-8"),
        template_path,
    )
    require("__ATLAS_DATA_JSON__" in template, "template data placeholder is missing")
    encoded = json.dumps(atlas, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = template.replace("__ATLAS_DATA_JSON__", encoded)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"Built exact reading corner: {output_path}")


if __name__ == "__main__":
    main()
