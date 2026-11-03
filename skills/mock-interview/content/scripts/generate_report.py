#!/usr/bin/env python3
"""Turn an interview debrief into a self-contained HTML report.

Usage:
    python scripts/generate_report.py --input debrief.json --output report.html

Input JSON shape:

{
  "role": "Product Manager Intern, Summer 2027",
  "company": "Example Co",
  "date": "2026-07-27",
  "track": "product",
  "questions": [
    {
      "question": "Tell me about a time you influenced without authority.",
      "answer_summary": "Described a group project where the team adopted her plan.",
      "followups": ["What did you personally do?"],
      "scores": {"structure": 3, "specificity": 2, "impact": 2, "fit": 4},
      "missing": [
        "No outcome — the project shipped, but nothing about what changed",
        "Said 'we' throughout; your own contribution never became clear"
      ],
      "rewrite": "In my sophomore year I... [your number here]"
    }
  ],
  "patterns": ["Strong stories, consistently missing the result"],
  "priorities": ["Add one number to every story", "Cut setup to 20 seconds"],
  "strong_stories": ["The dining hall project — reuse for ownership questions"],
  "language": "zh"
}

Everything except "questions" is optional. Scores are 1-5. Language accepts
"zh" or "en" and only affects the report's own labels.
"""

import argparse
import html
import json
import sys
from datetime import date
from pathlib import Path

DIMENSIONS = ["structure", "specificity", "impact", "fit"]

LABELS = {
    "en": {
        "title": "Mock Interview Debrief",
        "overall": "Overall",
        "structure": "Structure",
        "specificity": "Specificity",
        "impact": "Impact",
        "fit": "Role fit",
        "questions": "Question by question",
        "asked": "Question",
        "you_said": "What you said",
        "followups": "Follow-ups asked",
        "missing": "What was missing",
        "rewrite": "Stronger version",
        "patterns": "Patterns across the round",
        "priorities": "Fix these first",
        "strong": "Stories worth reusing",
        "avg": "avg",
        "note": "Scores are 1-5, where 3 is an average real candidate.",
    },
    "zh": {
        "title": "模拟面试复盘",
        "overall": "总览",
        "structure": "结构",
        "specificity": "具体度",
        "impact": "结果影响",
        "fit": "岗位匹配",
        "questions": "逐题复盘",
        "asked": "问题",
        "you_said": "你的回答",
        "followups": "追问",
        "missing": "缺了什么",
        "rewrite": "更强的版本",
        "patterns": "整体模式",
        "priorities": "优先修这几点",
        "strong": "值得复用的故事",
        "avg": "平均",
        "note": "评分 1–5 分，3 分 = 真实面试中的平均水平。",
    },
}

CSS = """
*, *::before, *::after { box-sizing: border-box; }
body {
  margin: 0; padding: 48px 24px 96px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
               "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  background: #faf9f7; color: #1c1a17; line-height: 1.65;
  -webkit-font-smoothing: antialiased;
}
.wrap { max-width: 780px; margin: 0 auto; }
header { margin-bottom: 44px; }
h1 { font-size: 30px; letter-spacing: -0.4px; margin: 0 0 6px; font-weight: 650; }
.meta { color: #7a736a; font-size: 14px; }
h2 {
  font-size: 13px; text-transform: uppercase; letter-spacing: 1.4px;
  color: #96897a; font-weight: 600; margin: 52px 0 18px;
}
.scores { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.score {
  background: #fff; border: 1px solid #eae5de; border-radius: 12px;
  padding: 18px 16px; text-align: center;
}
.score .n { font-size: 30px; font-weight: 640; letter-spacing: -1px; line-height: 1.1; }
.score .l { font-size: 12px; color: #8a8177; margin-top: 5px; }
.bar { height: 4px; background: #ece7e0; border-radius: 99px; margin-top: 12px; overflow: hidden; }
.bar span { display: block; height: 100%; border-radius: 99px; }
.g5, .g4 { background: #4f7a52; }
.g3 { background: #c08a3e; }
.g2, .g1 { background: #b3563f; }
.card {
  background: #fff; border: 1px solid #eae5de; border-radius: 14px;
  padding: 26px 28px; margin-bottom: 18px;
}
.q { font-size: 17px; font-weight: 600; margin: 0 0 4px; letter-spacing: -0.2px; }
.qnum { font-size: 12px; color: #a89d90; font-weight: 600; letter-spacing: 0.6px; }
.sub {
  font-size: 11px; text-transform: uppercase; letter-spacing: 1.1px;
  color: #a89d90; font-weight: 600; margin: 22px 0 7px;
}
.said { color: #5f584f; font-size: 15px; }
.pills { display: flex; flex-wrap: wrap; gap: 7px; margin-top: 16px; }
.pill {
  font-size: 12px; padding: 4px 11px; border-radius: 99px;
  background: #f3efe9; color: #6b6259; font-weight: 500;
}
.pill b { font-weight: 680; }
ul { margin: 0; padding-left: 19px; }
li { margin-bottom: 7px; }
.rewrite {
  background: #f6f4ef; border-left: 3px solid #4f7a52; border-radius: 0 8px 8px 0;
  padding: 16px 18px; font-size: 15px; white-space: pre-wrap; margin-top: 8px;
}
.rewrite mark { background: #e4dcc9; padding: 1px 4px; border-radius: 3px; }
.fu { color: #6b6259; font-size: 14px; font-style: italic; }
.note { color: #a89d90; font-size: 13px; margin-top: 10px; }
footer { margin-top: 64px; color: #b0a698; font-size: 12px; text-align: center; }
footer a { color: #8a8177; }
@media (max-width: 600px) {
  body { padding: 28px 16px 64px; }
  .scores { grid-template-columns: repeat(2, 1fr); }
  .card { padding: 20px; }
}
@media print {
  body { background: #fff; padding: 0; }
  .card, .score { break-inside: avoid; }
}
"""


def esc(text) -> str:
    return html.escape(str(text if text is not None else ""))


def grade_class(value: float) -> str:
    return "g" + str(max(1, min(5, int(round(value)))))


def render_list(items) -> str:
    if not items:
        return ""
    return "<ul>" + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>"


def render_rewrite(text: str) -> str:
    """Escape, then re-highlight [placeholder] markers so they stand out."""
    safe = esc(text)
    out, depth, buf = [], 0, ""
    for ch in safe:
        if ch == "[":
            depth += 1
            buf = "["
        elif ch == "]" and depth:
            depth -= 1
            out.append(f"<mark>{buf}]</mark>")
            buf = ""
        elif depth:
            buf += ch
        else:
            out.append(ch)
    if buf:
        out.append(buf)
    return "".join(out)


def build(data: dict) -> str:
    lang = data.get("language", "zh")
    L = LABELS.get(lang, LABELS["zh"])
    questions = data.get("questions", [])

    averages = {}
    for dim in DIMENSIONS:
        vals = [
            q["scores"][dim]
            for q in questions
            if isinstance(q.get("scores"), dict) and dim in q["scores"]
        ]
        averages[dim] = sum(vals) / len(vals) if vals else 0

    score_cards = ""
    for dim in DIMENSIONS:
        avg = averages[dim]
        score_cards += (
            f'<div class="score"><div class="n">{avg:.1f}</div>'
            f'<div class="l">{L[dim]}</div>'
            f'<div class="bar"><span class="{grade_class(avg)}" '
            f'style="width:{avg / 5 * 100:.0f}%"></span></div></div>'
        )

    cards = ""
    for i, q in enumerate(questions, 1):
        scores = q.get("scores") or {}
        pills = "".join(
            f'<span class="pill">{L[d]} <b>{scores[d]}</b></span>'
            for d in DIMENSIONS
            if d in scores
        )

        followups = ""
        if q.get("followups"):
            items = "".join(f"<li>{esc(f)}</li>" for f in q["followups"])
            followups = f'<div class="sub">{L["followups"]}</div><ul class="fu">{items}</ul>'

        missing = ""
        if q.get("missing"):
            missing = f'<div class="sub">{L["missing"]}</div>{render_list(q["missing"])}'

        rewrite = ""
        if q.get("rewrite"):
            rewrite = (
                f'<div class="sub">{L["rewrite"]}</div>'
                f'<div class="rewrite">{render_rewrite(q["rewrite"])}</div>'
            )

        said = ""
        if q.get("answer_summary"):
            said = (
                f'<div class="sub">{L["you_said"]}</div>'
                f'<div class="said">{esc(q["answer_summary"])}</div>'
            )

        cards += f"""<div class="card">
  <div class="qnum">Q{i}</div>
  <p class="q">{esc(q.get('question', ''))}</p>
  <div class="pills">{pills}</div>
  {said}{followups}{missing}{rewrite}
</div>"""

    sections = ""
    for key, label in (
        ("patterns", L["patterns"]),
        ("priorities", L["priorities"]),
        ("strong_stories", L["strong"]),
    ):
        if data.get(key):
            sections += f'<h2>{label}</h2><div class="card">{render_list(data[key])}</div>'

    meta_bits = [b for b in (data.get("role"), data.get("company"), data.get("date") or str(date.today())) if b]
    meta = esc(" · ".join(meta_bits))

    return f"""<!DOCTYPE html>
<html lang="{esc(lang)}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{L['title']}</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>{L['title']}</h1>
    <div class="meta">{meta}</div>
  </header>

  <h2>{L['overall']}</h2>
  <div class="scores">{score_cards}</div>
  <div class="note">{L['note']}</div>

  <h2>{L['questions']}</h2>
  {cards}

  {sections}

  <footer>Generated by <a href="https://github.com/ameliapeng-gif/real-mock-interview-agent">real-mock-interview-agent</a></footer>
</div>
</body>
</html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an HTML interview debrief.")
    parser.add_argument("--input", required=True, help="Path to debrief JSON")
    parser.add_argument("--output", default="interview-report.html", help="Output HTML path")
    args = parser.parse_args()

    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"No such file: {args.input}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"Input isn't valid JSON: {exc}", file=sys.stderr)
        return 1

    if not data.get("questions"):
        print("Debrief has no questions — nothing to report.", file=sys.stderr)
        return 1

    out = Path(args.output)
    out.write_text(build(data), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
