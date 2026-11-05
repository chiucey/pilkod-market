#!/usr/bin/env python3
"""Write and verify PowerPoint speaker notes through native PPTX parts."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from pptx import Presentation


class NotesApplyFailure(RuntimeError):
    def __init__(self, code: str, message: str, exit_code: int = 1):
        super().__init__(message)
        self.code = code
        self.exit_code = exit_code


def _write_json_atomic(path: str, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=f".{target.name}.",
        suffix=".tmp",
        dir=str(target.parent),
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, target)
    except Exception:
        if os.path.exists(temporary):
            os.unlink(temporary)
        raise


def _load_notes(path: str) -> list[dict[str, Any]]:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise NotesApplyFailure("notes_invalid", f"Cannot read notes sidecar: {exc}", 2) from exc
    if not isinstance(payload, dict) or payload.get("schema") != "mavis.ppt_notes.v1":
        raise NotesApplyFailure(
            "notes_schema_invalid",
            "Notes sidecar schema must be mavis.ppt_notes.v1",
            2,
        )
    slides = payload.get("slides")
    if not isinstance(slides, list):
        raise NotesApplyFailure("notes_schema_invalid", "slides must be an array", 2)
    return slides


def _validate_slides(
    slides: list[dict[str, Any]], slide_count: int
) -> list[tuple[int, str]]:
    validated: list[tuple[int, str]] = []
    seen: set[int] = set()
    for index, item in enumerate(slides):
        if not isinstance(item, dict):
            raise NotesApplyFailure(
                "notes_schema_invalid", f"slides[{index}] must be an object", 2
            )
        slide_number = item.get("slideNumber")
        text = item.get("text")
        if isinstance(slide_number, bool) or not isinstance(slide_number, int):
            raise NotesApplyFailure(
                "notes_schema_invalid",
                f"slides[{index}].slideNumber must be an integer",
                2,
            )
        if slide_number < 1 or slide_number > slide_count:
            raise NotesApplyFailure(
                "slide_number_out_of_range",
                f"Slide number {slide_number} is outside 1..{slide_count}",
            )
        if slide_number in seen:
            raise NotesApplyFailure(
                "duplicate_slide_number",
                f"Slide number {slide_number} appears more than once",
                2,
            )
        if not isinstance(text, str):
            raise NotesApplyFailure(
                "notes_schema_invalid",
                f"slides[{index}].text must be a string",
                2,
            )
        seen.add(slide_number)
        validated.append((slide_number, text))
    return validated


def apply_notes(args: argparse.Namespace) -> int:
    report: dict[str, Any] = {
        "schema": "mavis.ppt_notes_apply_report.v1",
        "status": "running",
        "input": args.input,
        "output": args.out,
        "notes": args.notes,
    }
    temporary_output: str | None = None
    try:
        input_path = Path(args.input)
        output_path = Path(args.out)
        if not input_path.is_file():
            raise NotesApplyFailure("input_missing", f"Input PPTX not found: {input_path}", 2)
        if input_path.resolve() == output_path.resolve():
            raise NotesApplyFailure(
                "output_must_differ",
                "Speaker-note output must differ from the source PPTX",
                2,
            )

        source = Presentation(input_path)
        slides = _validate_slides(_load_notes(args.notes), len(source.slides))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary_output = tempfile.mkstemp(
            prefix=f".{output_path.stem}.notes.",
            suffix=".pptx",
            dir=str(output_path.parent),
        )
        os.close(fd)
        shutil.copy2(input_path, temporary_output)

        presentation = Presentation(temporary_output)
        for slide_number, text in slides:
            presentation.slides[slide_number - 1].notes_slide.notes_text_frame.text = text
        presentation.save(temporary_output)

        readback = Presentation(temporary_output)
        matched = 0
        for slide_number, expected_text in slides:
            actual_text = (
                readback.slides[slide_number - 1].notes_slide.notes_text_frame.text
            )
            if actual_text != expected_text:
                raise NotesApplyFailure(
                    "notes_readback_mismatch",
                    f"Speaker notes differ after writeback on slide {slide_number}",
                )
            matched += 1

        os.replace(temporary_output, output_path)
        temporary_output = None
        report["status"] = "success"
        report["summary"] = {
            "requestedSlides": len(slides),
            "writtenSlides": len(slides),
            "matchedSlides": matched,
        }
        _write_json_atomic(args.report, report)
        return 0
    except NotesApplyFailure as exc:
        report["status"] = "failed"
        report["errorCode"] = exc.code
        report["message"] = str(exc)
        _write_json_atomic(args.report, report)
        return exc.exit_code
    except Exception as exc:
        report["status"] = "failed"
        report["errorCode"] = "notes_apply_failed"
        report["message"] = str(exc)
        _write_json_atomic(args.report, report)
        return 2
    finally:
        if temporary_output and os.path.exists(temporary_output):
            os.unlink(temporary_output)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write and verify PowerPoint speaker notes through native PPTX parts"
    )
    parser.add_argument("--input", required=True, help="Source PPTX")
    parser.add_argument("--notes", required=True, help="mavis.ppt_notes.v1 sidecar")
    parser.add_argument("--out", required=True, help="Output PPTX")
    parser.add_argument("--report", required=True, help="JSON report path")
    return apply_notes(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
