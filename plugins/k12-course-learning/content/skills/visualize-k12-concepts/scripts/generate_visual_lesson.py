#!/usr/bin/env python3
"""Validate a lesson specification and render one standalone HTML file."""

from __future__ import annotations

import argparse
from html import escape
import json
import re
import sys
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = SKILL_ROOT / "assets" / "lesson-template.html"
TEMPLATE_TOKEN = "__LESSON_DATA__"
TITLE_TOKEN = "__LESSON_TITLE__"
VISUAL_KINDS = {
    "ray-reflection",
    "number-line",
    "fraction",
    "process",
    "comparison",
    "concept-map",
}
REQUIRED_SECTIONS = (
    "meta",
    "hero",
    "goal",
    "map",
    "hook",
    "visual",
    "analogy",
    "steps",
    "misconceptions",
    "checks",
    "recall",
    "sources",
)


class SpecError(ValueError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except FileNotFoundError as exc:
        raise SpecError(f"Spec file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SpecError(f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise SpecError("The lesson spec root must be an object.")
    return payload


def need_object(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SpecError(f"{path} must be an object.")
    return value


def need_list(value: Any, path: str, minimum: int = 0, maximum: int | None = None) -> list[Any]:
    if not isinstance(value, list):
        raise SpecError(f"{path} must be an array.")
    if len(value) < minimum:
        raise SpecError(f"{path} must contain at least {minimum} item(s).")
    if maximum is not None and len(value) > maximum:
        raise SpecError(f"{path} must contain at most {maximum} item(s).")
    return value


def need_text(value: Any, path: str, maximum: int | None = None) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SpecError(f"{path} must be a non-empty string.")
    if maximum is not None and len(value) > maximum:
        raise SpecError(f"{path} must be at most {maximum} characters.")
    return value.strip()


def need_number(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SpecError(f"{path} must be a number.")
    return float(value)


def validate_text_list(value: Any, path: str, minimum: int = 0, maximum: int | None = None) -> list[str]:
    items = need_list(value, path, minimum, maximum)
    for index, item in enumerate(items):
        need_text(item, f"{path}[{index}]")
    return items


def validate_visual(visual: dict[str, Any]) -> None:
    kind = need_text(visual.get("kind"), "visual.kind")
    if kind not in VISUAL_KINDS:
        raise SpecError(f"visual.kind must be one of: {', '.join(sorted(VISUAL_KINDS))}.")
    for field in ("title", "instruction", "observation"):
        need_text(visual.get(field), f"visual.{field}")

    if kind in {"ray-reflection", "number-line"}:
        minimum = need_number(visual.get("min"), "visual.min")
        maximum = need_number(visual.get("max"), "visual.max")
        value = need_number(visual.get("value"), "visual.value")
        if minimum >= maximum:
            raise SpecError("visual.min must be smaller than visual.max.")
        if not minimum <= value <= maximum:
            raise SpecError("visual.value must fall between visual.min and visual.max.")
        need_text(visual.get("controlLabel"), "visual.controlLabel")
        need_text(visual.get("unit"), "visual.unit")
        if kind == "number-line":
            step = need_number(visual.get("step"), "visual.step")
            if step <= 0:
                raise SpecError("visual.step must be greater than zero.")
            markers = visual.get("markers", [])
            for index, marker in enumerate(need_list(markers, "visual.markers", 0, 12)):
                marker = need_object(marker, f"visual.markers[{index}]")
                need_number(marker.get("value"), f"visual.markers[{index}].value")
                need_text(marker.get("label"), f"visual.markers[{index}].label")

    elif kind == "fraction":
        numerator = need_number(visual.get("numerator"), "visual.numerator")
        denominator = need_number(visual.get("denominator"), "visual.denominator")
        if not numerator.is_integer() or not denominator.is_integer():
            raise SpecError("visual.numerator and visual.denominator must be integers.")
        if not 1 <= numerator <= denominator <= 20:
            raise SpecError("fraction visual requires 1 <= numerator <= denominator <= 20.")

    elif kind == "process":
        stages = need_list(visual.get("stages"), "visual.stages", 3, 7)
        for index, stage in enumerate(stages):
            stage = need_object(stage, f"visual.stages[{index}]")
            need_text(stage.get("title"), f"visual.stages[{index}].title")
            need_text(stage.get("body"), f"visual.stages[{index}].body")

    elif kind == "comparison":
        items = need_list(visual.get("items"), "visual.items", 2, 4)
        for index, item in enumerate(items):
            item = need_object(item, f"visual.items[{index}]")
            need_text(item.get("title"), f"visual.items[{index}].title")
            validate_text_list(item.get("facts"), f"visual.items[{index}].facts", 1, 6)

    elif kind == "concept-map":
        nodes = need_list(visual.get("nodes"), "visual.nodes", 3, 9)
        node_ids: set[str] = set()
        for index, node in enumerate(nodes):
            node = need_object(node, f"visual.nodes[{index}]")
            node_id = need_text(node.get("id"), f"visual.nodes[{index}].id")
            if node_id in node_ids:
                raise SpecError(f"visual.nodes has duplicate id: {node_id}")
            node_ids.add(node_id)
            need_text(node.get("label"), f"visual.nodes[{index}].label")
            role = need_text(node.get("role"), f"visual.nodes[{index}].role")
            if role not in {"prerequisite", "core", "unlock"}:
                raise SpecError("concept-map node role must be prerequisite, core, or unlock.")
        for index, node in enumerate(nodes):
            for target in node.get("connectsTo", []):
                if target not in node_ids:
                    raise SpecError(f"visual.nodes[{index}] connects to unknown id: {target}")


def validate_spec(spec: dict[str, Any]) -> None:
    for section in REQUIRED_SECTIONS:
        if section not in spec:
            raise SpecError(f"Missing required section: {section}")

    meta = need_object(spec["meta"], "meta")
    for field in ("title", "subject", "age", "duration", "language"):
        need_text(meta.get(field), f"meta.{field}")

    hero = need_object(spec["hero"], "hero")
    for field in ("eyebrow", "question", "promise"):
        need_text(hero.get(field), f"hero.{field}")

    need_text(spec["goal"], "goal")
    validate_text_list(spec.get("assumptions", []), "assumptions", 0, 8)

    lesson_map = need_object(spec["map"], "map")
    validate_text_list(lesson_map.get("prerequisites"), "map.prerequisites", 1, 6)
    need_text(lesson_map.get("core"), "map.core")
    validate_text_list(lesson_map.get("unlocks"), "map.unlocks", 1, 6)

    hook = need_object(spec["hook"], "hook")
    for field in ("title", "body", "prompt"):
        need_text(hook.get(field), f"hook.{field}")

    visual = need_object(spec["visual"], "visual")
    validate_visual(visual)

    analogy = need_object(spec["analogy"], "analogy")
    for field in ("title", "body", "limit"):
        need_text(analogy.get(field), f"analogy.{field}")

    steps = need_list(spec["steps"], "steps", 3, 5)
    for index, step in enumerate(steps):
        step = need_object(step, f"steps[{index}]")
        for field in ("label", "title", "body"):
            need_text(step.get(field), f"steps[{index}].{field}")

    misconceptions = need_list(spec["misconceptions"], "misconceptions", 1, 4)
    for index, misconception in enumerate(misconceptions):
        misconception = need_object(misconception, f"misconceptions[{index}]")
        for field in ("myth", "correction", "why"):
            need_text(misconception.get(field), f"misconceptions[{index}].{field}")

    checks = need_list(spec["checks"], "checks", 2, 4)
    for index, check in enumerate(checks):
        check = need_object(check, f"checks[{index}]")
        need_text(check.get("question"), f"checks[{index}].question")
        options = validate_text_list(check.get("options"), f"checks[{index}].options", 2, 5)
        for option_index, option in enumerate(options):
            need_text(option, f"checks[{index}].options[{option_index}]", 80)
        answer = check.get("answer")
        if isinstance(answer, bool) or not isinstance(answer, int) or not 0 <= answer < len(options):
            raise SpecError(f"checks[{index}].answer must index an existing option.")
        need_text(check.get("explanation"), f"checks[{index}].explanation", 240)

    recall = need_object(spec["recall"], "recall")
    for field in ("prompt", "hint", "answer"):
        need_text(recall.get(field), f"recall.{field}")

    sources = need_list(spec["sources"], "sources", 1, 8)
    for index, source in enumerate(sources):
        source = need_object(source, f"sources[{index}]")
        need_text(source.get("label"), f"sources[{index}].label")
        need_text(source.get("detail"), f"sources[{index}].detail")
        if "url" in source and source["url"]:
            need_text(source["url"], f"sources[{index}].url")


def safe_json(spec: dict[str, Any]) -> str:
    payload = json.dumps(spec, ensure_ascii=False, separators=(",", ":"))
    return payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def validate_template(template: str) -> None:
    if template.count(TEMPLATE_TOKEN) != 1:
        raise SpecError(f"Template must contain exactly one {TEMPLATE_TOKEN} token.")
    if template.count(TITLE_TOKEN) != 1:
        raise SpecError(f"Template must contain exactly one {TITLE_TOKEN} token.")
    external_runtime = re.compile(
        r"<(?:script|link|iframe|img|source)\b[^>]*(?:src|href)=[\"'](?:https?:)?//",
        re.IGNORECASE,
    )
    if external_runtime.search(template):
        raise SpecError("Template contains an external runtime dependency.")
    forbidden = ("localStorage", "sessionStorage", "document.cookie", "fetch(", "XMLHttpRequest")
    for token in forbidden:
        if token in template:
            raise SpecError(f"Template uses forbidden persistent or network API: {token}")


def render(spec: dict[str, Any], template_path: Path, output_path: Path) -> None:
    try:
        template = template_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SpecError(f"Template file not found: {template_path}") from exc
    validate_template(template)
    title = escape(spec["meta"]["title"], quote=False)
    rendered = template.replace(TITLE_TOKEN, title).replace(TEMPLATE_TOKEN, safe_json(spec))
    if TEMPLATE_TOKEN in rendered or TITLE_TOKEN in rendered:
        raise SpecError("Template token replacement failed.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate one offline interactive K12 lesson page.")
    parser.add_argument("--spec", required=True, type=Path, help="UTF-8 JSON lesson specification.")
    parser.add_argument("--output", type=Path, help="Destination HTML file.")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE, help="Override HTML template.")
    parser.add_argument("--validate-only", action="store_true", help="Validate without writing HTML.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        spec = read_json(args.spec.resolve())
        validate_spec(spec)
        if args.validate_only:
            print(f"VALID: {args.spec.resolve()}")
            return 0
        if args.output is None:
            raise SpecError("--output is required unless --validate-only is used.")
        output = args.output.resolve()
        render(spec, args.template.resolve(), output)
        print(f"GENERATED: {output}")
        print(f"TITLE: {spec['meta']['title']}")
        print(f"VISUAL: {spec['visual']['kind']}")
        return 0
    except SpecError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
