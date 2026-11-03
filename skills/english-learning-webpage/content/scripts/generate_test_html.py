from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"
TEMPLATE_PATH = TEMPLATES / "listening_page_template.html"
TEST_PAGES = [
    (TEMPLATES / "pronunciation_hint_test.html", "voyage-293-pronunciation-test"),
    (TEMPLATES / "chunk_cut_test.html", "voyage-293-chunk-cut-test"),
]


def extract(pattern: str, html: str, fallback: str | None = None) -> str:
    match = re.search(pattern, html, re.DOTALL)
    if match:
        return match.group(1).strip()
    if fallback is not None:
        return fallback
    raise ValueError(f"Pattern not found: {pattern}")


def main() -> None:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    for path, page_id in TEST_PAGES:
        old = path.read_text(encoding="utf-8")
        title = extract(r"<title>(.*?)</title>", old, path.stem)
        data_json = extract(
            r'<script id="DATA" type="application/json">(.*?)</script>',
            old,
        )
        output = (
            template.replace("{{TITLE}}", title)
            .replace("{{ID}}", page_id)
            .replace("{{DATA_JSON}}", data_json)
        )
        path.write_text(output, encoding="utf-8")
        print(f"Updated {path}")


if __name__ == "__main__":
    main()
