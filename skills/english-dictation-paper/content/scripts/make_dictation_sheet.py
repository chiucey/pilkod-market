#!/usr/bin/env python3
"""Generate an English dictation worksheet (HTML + optional PDF).

Input formats
- TXT: each non-empty line is `word<TAB>meaning` or `word - meaning`.
- CSV: headers must include `word` and `meaning`.

Example
python scripts/make_dictation_sheet.py \
  --input words.txt \
  --out-dir ./out \
  --title "英语词汇默写纸 - 双栏对照版" \
  --header "英 语 词 汇 默 写 纸" \
  --pdf
"""

from __future__ import annotations

import argparse
import csv
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass
class Item:
    word: str
    meaning: str


_SPLIT_RE = re.compile(r"\s*(?:\t+|\s+-\s+|\s+—\s+|\s+–\s+)\s*")


def read_items(input_path: Path) -> List[Item]:
    if not input_path.exists():
        raise FileNotFoundError(str(input_path))

    ext = input_path.suffix.lower()
    if ext in {".csv"}:
        with input_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise ValueError("CSV has no header")
            fields = {c.strip().lower(): c for c in reader.fieldnames}
            if "word" not in fields or "meaning" not in fields:
                raise ValueError("CSV must include headers: word, meaning")
            out: List[Item] = []
            for row in reader:
                w = (row.get(fields["word"]) or "").strip()
                m = (row.get(fields["meaning"]) or "").strip()
                if w and m:
                    out.append(Item(word=w, meaning=m))
            return out

    # default: treat as txt
    lines = input_path.read_text(encoding="utf-8").splitlines()
    out: List[Item] = []
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#"):
            continue
        parts = [p.strip() for p in _SPLIT_RE.split(s, maxsplit=1) if p.strip()]
        if len(parts) < 2:
            # allow `word meaning` fallback (last resort)
            parts = s.split(None, 1)
        if len(parts) < 2:
            raise ValueError(f"Cannot parse line (need word + meaning): {ln}")
        out.append(Item(word=parts[0], meaning=parts[1]))
    return out


def html_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def build_rows(items: Iterable[Item]) -> tuple[str, str]:
    left_rows: List[str] = []
    right_rows: List[str] = []

    for i, it in enumerate(items, start=1):
        w = html_escape(it.word)
        m = html_escape(it.meaning)
        left_rows.append(
            f'<div class="word-row">'
            f'<div class="num">{i}</div>'
            f'<div class="word-cell">{w}</div>'
            f'<div class="meaning-cell"><span class="blank-lines"></span></div>'
            f'<div class="check-box">□</div>'
            f"</div>"
        )
        right_rows.append(
            f'<div class="word-row right">'
            f'<div class="num">{i}</div>'
            f'<div class="meaning-cell"><span class="blank-word"></span></div>'
            f'<div class="meaning-text">{m}</div>'
            f"</div>"
        )

    return "\n                ".join(left_rows), "\n                ".join(right_rows)


def load_template(template_path: Path) -> str:
    if not template_path.exists():
        raise FileNotFoundError(str(template_path))
    return template_path.read_text(encoding="utf-8")


def render_html(template: str, *, title: str, header_h1: str, footer_text: str, left_rows: str, right_rows: str) -> str:
    return (
        template.replace("{{TITLE}}", html_escape(title))
        .replace("{{HEADER_H1}}", html_escape(header_h1))
        .replace("{{FOOTER_TEXT}}", html_escape(footer_text))
        .replace("{{LEFT_ROWS}}", left_rows)
        .replace("{{RIGHT_ROWS}}", right_rows)
    )


def html_to_pdf(html_file: Path, pdf_file: Path) -> None:
    """Render HTML to PDF using Playwright (Chromium)."""
    from playwright.sync_api import sync_playwright

    pdf_file.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html_file.resolve().as_uri(), wait_until="networkidle")
        page.emulate_media(media="print")
        page.pdf(
            path=str(pdf_file),
            format="A4",
            print_background=True,
            margin={"top": "15mm", "right": "15mm", "bottom": "15mm", "left": "15mm"},
        )
        browser.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate English dictation worksheet (HTML/PDF).")
    parser.add_argument("--input", required=True, help="Path to words TXT/CSV")
    parser.add_argument("--out-dir", default="./out", help="Output directory")
    parser.add_argument("--template", default=str(Path(__file__).resolve().parents[1] / "assets" / "template.html"))
    parser.add_argument("--title", default="英语词汇默写纸 - 双栏对照版")
    parser.add_argument("--header", default="英 语 词 汇 默 写 纸")
    parser.add_argument(
        "--footer",
        default="使用说明：左栏看英文写中文，右栏可看中文回忆英文单词，用于双向巩固记忆 | 打印设置：A4纸张，边距默认，建议双面打印",
    )
    parser.add_argument("--name", default="英语词汇默写纸", help="Base filename (no extension)")
    parser.add_argument("--pdf", action="store_true", help="Also export to PDF")

    args = parser.parse_args()

    input_path = Path(args.input)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    items = read_items(input_path)
    if not items:
        raise ValueError("No items parsed from input")

    tpl = load_template(Path(args.template))
    left_rows, right_rows = build_rows(items)
    html = render_html(
        tpl,
        title=args.title,
        header_h1=args.header,
        footer_text=args.footer,
        left_rows=left_rows,
        right_rows=right_rows,
    )

    html_path = out_dir / f"{args.name}.html"
    html_path.write_text(html, encoding="utf-8")

    print(str(html_path))

    if args.pdf:
        pdf_path = out_dir / f"{args.name}.pdf"
        html_to_pdf(html_path, pdf_path)
        print(str(pdf_path))


if __name__ == "__main__":
    main()
