#!/usr/bin/env python3
"""
Template: calibrate word-level subtitles with official subtitles by timestamp.

The word-level subtitle is the backbone:
  - final content range comes only from word-level words
  - official-only words are never inserted into the learning data
  - official subtitles only correct nearby word-level words by timestamp

Inputs:
  --word-level  Whisper JSON or word-level SRT/VTT/TXT
  --official    Official SRT/VTT/TXT
  --out         Intermediate aligned JSON
  --diff-xlsx   Optional Excel report for words actually changed

Outputs:
  1. Intermediate JSON:
     {"sentences": [{"index", "text", "start", "end", "words"}], "quality": {...}}
  2. Excel report of actual changes:
     columns = time, word-level word, official word
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import zipfile
from html import escape
from pathlib import Path


TIME_RE = re.compile(
    r"(?:(?P<h>\d{1,2}):)?(?P<m>\d{1,2}):(?P<s>\d{2})[,.](?P<ms>\d{1,3})"
)
NOISE_RE = re.compile(r"\[.*?\]|\(.*?\)|<.*?>|[\u266a\u266b\u266c]")
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?(?:%|[.!?,;:])?")
NORM_RE = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?")
SENTENCE_END_RE = re.compile(r"[.!?][\"')\]]?$")


def parse_time(text: str) -> float:
    match = TIME_RE.search(text)
    if not match:
        raise ValueError(f"Cannot parse timestamp: {text!r}")
    hours = int(match.group("h") or 0)
    ms = match.group("ms").ljust(3, "0")[:3]
    return (
        hours * 3600
        + int(match.group("m")) * 60
        + int(match.group("s"))
        + int(ms) / 1000
    )


def normalize(text: str) -> str:
    text = NOISE_RE.sub(" ", text.lower())
    return "".join(NORM_RE.findall(text))


def format_timestamp(start: float | None, end: float | None = None) -> str:
    if start is None:
        return ""

    def one(value: float) -> str:
        minutes = int(value // 60)
        seconds = value - minutes * 60
        return f"{minutes}:{seconds:05.2f}"

    if end is None:
        return one(start)
    return f"{one(start)}-{one(end)}"


def parse_word_json(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    words = []
    for seg in data.get("segments", []):
        for item in seg.get("words", []):
            text = str(item.get("word", "")).strip()
            norm = normalize(text)
            if not norm:
                continue
            words.append(
                {
                    "text": text,
                    "norm": norm,
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
        text = " ".join(
            line
            for i, line in enumerate(lines)
            if "-->" not in line and not (i == 0 and line.isdigit())
        )
        cue_words = WORD_RE.findall(NOISE_RE.sub(" ", text))
        if not cue_words:
            continue
        step = max((end - start) / len(cue_words), 0.01)
        for i, word in enumerate(cue_words):
            norm = normalize(word)
            if not norm:
                continue
            words.append(
                {
                    "text": word,
                    "norm": norm,
                    "start": round(start + i * step, 3),
                    "end": round(start + (i + 1) * step, 3),
                }
            )
    return words


def parse_word_level(path: Path) -> list[dict]:
    if path.suffix.lower() == ".json":
        return parse_word_json(path)
    return parse_word_srt_like(path)


def clean_official_text(text: str) -> str:
    text = NOISE_RE.sub(" ", text)
    text = re.sub(r"\b[A-Z][A-Za-z]+:\s*", " ", text)
    text = re.sub(r"\bAll:\s*", " ", text, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", text).strip()


def parse_official_cues(path: Path) -> list[dict]:
    raw = path.read_text(encoding="utf-8-sig")
    blocks = re.split(r"\n\s*\n", raw.replace("\r\n", "\n").replace("\r", "\n"))
    cues = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        time_line = next((line for line in lines if "-->" in line), None)
        if not time_line:
            continue
        start_text, end_text = time_line.split("-->", 1)
        start = parse_time(start_text)
        end = parse_time(end_text)
        text = " ".join(
            line
            for i, line in enumerate(lines)
            if "-->" not in line and not (i == 0 and line.isdigit())
        )
        text = clean_official_text(text)
        tokens = []
        for token in WORD_RE.findall(text):
            norm = normalize(token)
            if norm:
                tokens.append({"text": token, "norm": norm})
        if tokens:
            cues.append({"start": start, "end": end, "tokens": tokens, "text": text})
    return cues


def official_tokens_near(cues: list[dict], start: float, end: float, pad: float) -> list[dict]:
    tokens = []
    for cue in cues:
        if cue["end"] < start - pad or cue["start"] > end + pad:
            continue
        tokens.extend(cue["tokens"])
    return tokens


def add_anomaly(rows: list[dict], start: float, end: float, asr_word: str, official_word: str) -> None:
    rows.append(
        {
            "timestamp": format_timestamp(start, end),
            "asr_word": asr_word,
            "official_word": official_word,
        }
    )


def is_low_risk_correction(asr_word: str, official_word: str) -> bool:
    """Only allow conservative official-text corrections."""
    asr_norm = normalize(asr_word)
    off_norm = normalize(official_word)
    if not asr_norm or not off_norm:
        return False
    if asr_norm == off_norm:
        return True
    # Possessive/apostrophe punctuation differences such as kids vs kid's.
    if asr_norm.replace("'", "") == off_norm.replace("'", ""):
        return True
    # Avoid semantic replacements. One-edit spelling fixes are allowed only
    # for words long enough that the risk is low.
    if min(len(asr_norm), len(off_norm)) >= 6:
        ratio = difflib.SequenceMatcher(None, asr_norm, off_norm, autojunk=False).ratio()
        return ratio >= 0.9
    return False


def calibrate_window(asr_window: list[dict], official_tokens: list[dict], anomalies: list[dict]) -> list[dict]:
    if not official_tokens:
        return [
            {
                "text": word["text"],
                "start": word["start"],
                "end": word["end"],
                "status": "uncalibrated",
            }
            for word in asr_window
        ]

    matcher = difflib.SequenceMatcher(
        None,
        [w["norm"] for w in asr_window],
        [w["norm"] for w in official_tokens],
        autojunk=False,
    )
    output: list[dict | None] = [None] * len(asr_window)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        asr_chunk = asr_window[i1:i2]
        off_chunk = official_tokens[j1:j2]
        if tag == "equal":
            for offset, word in enumerate(asr_chunk):
                official = off_chunk[offset]
                output[i1 + offset] = {
                    "text": official["text"],
                    "start": word["start"],
                    "end": word["end"],
                    "status": "ok",
                }
        elif tag == "replace":
            pairs = min(len(asr_chunk), len(off_chunk))
            equal_length_replacement = len(asr_chunk) == len(off_chunk)
            for offset in range(pairs):
                asr_word = asr_chunk[offset]
                official = off_chunk[offset]
                use_official = equal_length_replacement or is_low_risk_correction(asr_word["text"], official["text"])
                status = "ok" if asr_word["norm"] == official["norm"] else ("corrected" if use_official else "conflict_kept_word_level")
                if status == "corrected":
                    add_anomaly(anomalies, asr_word["start"], asr_word["end"], asr_word["text"], official["text"])
                output[i1 + offset] = {
                    "text": official["text"] if use_official else asr_word["text"],
                    "start": asr_word["start"],
                    "end": asr_word["end"],
                    "status": status,
                }
            for offset in range(pairs, len(asr_chunk)):
                asr_word = asr_chunk[offset]
                output[i1 + offset] = {
                    "text": asr_word["text"],
                    "start": asr_word["start"],
                    "end": asr_word["end"],
                    "status": "official_missing",
                }
            # Extra official words are intentionally ignored.
        elif tag == "delete":
            for offset, asr_word in enumerate(asr_chunk):
                output[i1 + offset] = {
                    "text": asr_word["text"],
                    "start": asr_word["start"],
                    "end": asr_word["end"],
                    "status": "official_missing",
                }
        elif tag == "insert":
            # Official-only words are not part of the word-level backbone.
            continue

    for idx, item in enumerate(output):
        if item is None:
            word = asr_window[idx]
            output[idx] = {
                "text": word["text"],
                "start": word["start"],
                "end": word["end"],
                "status": "uncalibrated",
            }
    return [item for item in output if item is not None]


def group_asr_windows(asr_words: list[dict], max_gap: float) -> list[list[dict]]:
    windows = []
    current = []
    for word in asr_words:
        if current and word["start"] - current[-1]["end"] > max_gap:
            windows.append(current)
            current = []
        current.append(word)
        if SENTENCE_END_RE.search(word["text"]):
            windows.append(current)
            current = []
    if current:
        windows.append(current)
    return windows


def split_on_calibrated_sentence_end(words: list[dict]) -> list[list[dict]]:
    """Split after official punctuation has been applied to word-level words."""
    chunks: list[list[dict]] = []
    current: list[dict] = []
    for word in words:
        current.append(word)
        if SENTENCE_END_RE.search(word["text"]):
            chunks.append(current)
            current = []
    if current:
        chunks.append(current)
    return chunks


def regroup_parent_sentences(chunks: list[list[dict]]) -> list[list[dict]]:
    """Merge trailing fragments until a complete parent sentence is formed."""
    sentences: list[list[dict]] = []
    current: list[dict] = []
    for chunk in chunks:
        current.extend(chunk)
        if current and SENTENCE_END_RE.search(current[-1]["text"]):
            sentences.append(current)
            current = []
    if current:
        sentences.append(current)
    return sentences


def make_sentence(index: int, words: list[dict]) -> dict:
    return {
        "index": index,
        "text": " ".join(word["text"] for word in words),
        "start": round(words[0]["start"], 2),
        "end": round(words[-1]["end"], 2),
        "words": [
            {
                "text": word["text"],
                "start": round(word["start"], 3),
                "end": round(word["end"], 3),
                "status": word["status"],
            }
            for word in words
        ],
    }


def calibrate(asr_words: list[dict], cues: list[dict], max_gap: float, official_pad: float) -> tuple[list[dict], dict, list[dict]]:
    anomalies: list[dict] = []
    sentence_chunks: list[list[dict]] = []
    raw_windows = 0
    corrected = 0
    ok = 0
    uncalibrated = 0
    official_missing = 0
    conflict_kept = 0

    for window in group_asr_windows(asr_words, max_gap=max_gap):
        raw_windows += 1
        official_tokens = official_tokens_near(cues, window[0]["start"], window[-1]["end"], pad=official_pad)
        words = calibrate_window(window, official_tokens, anomalies)
        for word in words:
            if word["status"] == "ok":
                ok += 1
            elif word["status"] == "corrected":
                corrected += 1
            elif word["status"] == "official_missing":
                official_missing += 1
            elif word["status"] == "conflict_kept_word_level":
                conflict_kept += 1
            else:
                uncalibrated += 1
        sentence_chunks.extend(split_on_calibrated_sentence_end(words))

    parent_sentence_words = regroup_parent_sentences(sentence_chunks)
    sentences = [make_sentence(index, words) for index, words in enumerate(parent_sentence_words)]

    quality = {
        "word_level_words": len(asr_words),
        "sentences": len(sentences),
        "raw_windows": raw_windows,
        "sentence_boundary_delta": len(sentences) - raw_windows,
        "ok": ok,
        "corrected": corrected,
        "official_missing": official_missing,
        "conflict_kept_word_level": conflict_kept,
        "uncalibrated": uncalibrated,
        "anomaly_rows": len(anomalies),
        "official_only_words_inserted": 0,
    }
    return sentences, quality, anomalies


def write_anomaly_xlsx(rows: list[dict], path: Path) -> None:
    headers = ["\u65f6\u95f4\u6233", "\u8bcd\u7ea7\u5b57\u5e55\u5355\u8bcd", "\u5b98\u65b9\u5b57\u5e55\u5355\u8bcd"]
    table = [headers] + [
        [row.get("timestamp", ""), row.get("asr_word", ""), row.get("official_word", "")]
        for row in rows
    ]
    sheet_rows = []
    for r_idx, row in enumerate(table, 1):
        cells = []
        for c_idx, value in enumerate(row, 1):
            col = chr(ord("A") + c_idx - 1)
            cells.append(
                f'<c r="{col}{r_idx}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'
            )
        sheet_rows.append(f'<row r="{r_idx}">{"".join(cells)}</row>')

    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        "<sheetData>"
        + "".join(sheet_rows)
        + "</sheetData></worksheet>"
    )
    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="\u5bf9\u9f50\u5f02\u5e38" sheetId="1" r:id="rId1"/></sheets></workbook>'
    )
    rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        "</Relationships>"
    )
    workbook_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
        "</Relationships>"
    )
    content_types_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        "</Types>"
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as xlsx:
        xlsx.writestr("[Content_Types].xml", content_types_xml.encode("utf-8"))
        xlsx.writestr("_rels/.rels", rels_xml.encode("utf-8"))
        xlsx.writestr("xl/workbook.xml", workbook_xml.encode("utf-8"))
        xlsx.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml.encode("utf-8"))
        xlsx.writestr("xl/worksheets/sheet1.xml", sheet_xml.encode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--word-level", required=True)
    parser.add_argument("--official", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--diff-xlsx", default=None)
    parser.add_argument("--max-gap", type=float, default=1.4)
    parser.add_argument("--official-pad", type=float, default=0.8)
    args = parser.parse_args()

    asr_words = parse_word_level(Path(args.word_level))
    official_cues = parse_official_cues(Path(args.official))
    sentences, quality, anomalies = calibrate(
        asr_words,
        official_cues,
        max_gap=args.max_gap,
        official_pad=args.official_pad,
    )

    diff_xlsx = Path(args.diff_xlsx) if args.diff_xlsx else Path(args.out).with_name("alignment_anomalies.xlsx")
    result = {
        "source": "word_level_with_official_timestamp_calibration",
        "sentences": sentences,
        "quality": quality,
        "reports": {"alignment_anomalies_xlsx": str(diff_xlsx)},
    }
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    write_anomaly_xlsx(anomalies, diff_xlsx)
    print(json.dumps(quality, ensure_ascii=False, indent=2))
    print(f"Anomaly Excel: {diff_xlsx}")


if __name__ == "__main__":
    main()
