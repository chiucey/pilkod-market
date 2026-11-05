#!/usr/bin/env python3
"""
Template: build intermediate sentence JSON from word-level subtitles only.

Use this when no official subtitle is available. Text is not officially
calibrated; add that caveat to the final delivery note.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


TIME_RE = re.compile(
    r"(?P<h>\d{1,2}):(?P<m>\d{2}):(?P<s>\d{2})[,.](?P<ms>\d{1,3})"
)
TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?|[.!?]")
NOISE_RE = re.compile(r"\[.*?\]|\(.*?\)|<.*?>|♪")


def parse_time(text: str) -> float:
    m = TIME_RE.search(text)
    if not m:
        raise ValueError(f"Cannot parse timestamp: {text!r}")
    ms = m.group("ms").ljust(3, "0")[:3]
    return (
        int(m.group("h")) * 3600
        + int(m.group("m")) * 60
        + int(m.group("s"))
        + int(ms) / 1000
    )


def parse_word_json(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    words = []
    for seg in data.get("segments", []):
        for item in seg.get("words", []):
            word = str(item.get("word", "")).strip()
            if not word:
                continue
            words.append(
                {
                    "text": word,
                    "start": float(item["start"]),
                    "end": float(item["end"]),
                }
            )
    return words


def parse_word_srt_like(path: Path) -> list[dict]:
    raw = path.read_text(encoding="utf-8-sig")
    blocks = re.split(r"\n\s*\n", raw.replace("\r\n", "\n").replace("\r", "\n"))
    words = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        time_line = next((line for line in lines if "-->" in line), None)
        if not time_line:
            continue
        start_text, end_text = time_line.split("-->", 1)
        start = parse_time(start_text)
        end = parse_time(end_text)
        text = " ".join(line for line in lines if "-->" not in line and not line.isdigit())
        cue_words = re.findall(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?", NOISE_RE.sub(" ", text))
        if not cue_words:
            continue
        step = max((end - start) / len(cue_words), 0.01)
        for i, word in enumerate(cue_words):
            words.append(
                {
                    "text": word,
                    "start": round(start + i * step, 3),
                    "end": round(start + (i + 1) * step, 3),
                }
            )
    return words


def parse_word_level(path: Path) -> list[dict]:
    if path.suffix.lower() == ".json":
        return parse_word_json(path)
    return parse_word_srt_like(path)


def group_by_sentence(words: list[dict], max_gap: float = 1.4) -> list[dict]:
    sentences = []
    current: list[dict] = []
    for word in words:
        if current and word["start"] - current[-1]["end"] > max_gap:
            sentences.append(current)
            current = []
        current.append(word)
        if re.search(r"[.!?][\"')\]]?$", word["text"]):
            sentences.append(current)
            current = []
    if current:
        sentences.append(current)

    out = []
    for idx, sent_words in enumerate(sentences):
        text = " ".join(w["text"] for w in sent_words)
        out.append(
            {
                "index": idx,
                "text": text,
                "start": round(sent_words[0]["start"], 2),
                "end": round(sent_words[-1]["end"], 2),
                "words": [
                    {
                        "text": w["text"],
                        "start": round(w["start"], 3),
                        "end": round(w["end"], 3),
                        "status": "uncalibrated",
                    }
                    for w in sent_words
                ],
            }
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--word-level", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--max-gap", type=float, default=1.4)
    args = parser.parse_args()

    words = parse_word_level(Path(args.word_level))
    sentences = group_by_sentence(words, max_gap=args.max_gap)
    result = {
        "source": "word_level_only",
        "note": "Text is generated from word-level subtitles and was not calibrated by official subtitles.",
        "sentences": sentences,
        "quality": {
            "word_count": sum(len(s["words"]) for s in sentences),
            "sentence_count": len(sentences),
            "official_calibrated": False,
        },
    }
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(sentences)} sentences to {args.out}")


if __name__ == "__main__":
    main()
