#!/usr/bin/env python3
"""Build CSV (and optional XLSX) artifacts for a multi-topic marginal tracker.

The tracker is organized as a set of *topics*. Each topic carries a single
chain of *events* (an append-only timeline). Each event points at its
predecessor via ``prev_event_id`` so the chain is reconstructible from the
flat list.

The script is deterministic: a given input JSON always yields the same set
of files on disk. It does not interpret events, score them, or rewrite an
existing tracker — it only stamps out the scaffolding tables that downstream
analysts populate.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


# ---------------------------------------------------------------------------
# Schema definition
# ---------------------------------------------------------------------------


# Per-topic metadata recorded once on the topic header.
TOPIC_COLUMNS: tuple[str, ...] = (
    "topic_id",
    "topic",
    "summary",
    "status",
    "created_at",
    "last_updated",
    "tags",
    "event_count",
    "head_event_id",
    "tail_event_id",
)


# Per-event row inside a topic chain. Each event records what happened, how
# it relates to prior events, and what it implies on the margin.
EVENT_COLUMNS: tuple[str, ...] = (
    "event_id",
    "prev_event_id",
    "date",
    "sequence",
    "headline",
    "fact",
    "source",
    "source_type",
    "signal",                  # confirming / weakening / neutral / mixed / break / untested
    "marginal_change",         # the *delta* this event introduces vs the prior state
    "interpretation",
    "evidence_quality",
    "impact",
    "linked_event_ids",        # comma-separated ids if this event also depends on siblings
    "follow_up",
)


# Aliases tolerated on input so legacy payloads still load.
TOPIC_ALIASES: tuple[str, ...] = ("threads", "chains", "tracks")
EVENT_ALIASES: tuple[str, ...] = ("timeline", "history", "entries", "items")


# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------


@dataclass
class TopicChain:
    """One topic header + its ordered event chain."""

    topic_id: str
    meta: dict[str, Any]
    events: list[dict[str, Any]]

    @property
    def event_count(self) -> int:
        return sum(1 for e in self.events if _row_has_payload(e))


# ---------------------------------------------------------------------------
# Key + row helpers
# ---------------------------------------------------------------------------


_SAFE_SLUG = re.compile(r"[^a-z0-9]+")


def _slugify(key: str) -> str:
    """Lowercase a header into snake_case for tolerant key matching."""

    buffer = []
    for ch in str(key):
        buffer.append(ch.lower() if ch.isalnum() else "_")
    return "".join(buffer).strip("_")


def _file_slug(value: str, fallback: str) -> str:
    """Filesystem-safe slug for use in CSV filenames."""

    slug = _SAFE_SLUG.sub("-", str(value).lower()).strip("-")
    return slug or fallback


def _row_has_payload(row: dict[str, Any]) -> bool:
    return any(v not in ("", None) for v in row.values())


def _coerce_row(raw: dict[str, Any], columns: Iterable[str]) -> dict[str, Any]:
    """Re-key one input dict so it lines up with the declared columns."""

    by_slug = {_slugify(k): v for k, v in raw.items()}
    return {col: by_slug.get(col, "") for col in columns}


def _empty_row(columns: Iterable[str]) -> dict[str, Any]:
    return {col: "" for col in columns}


# ---------------------------------------------------------------------------
# Payload extraction
# ---------------------------------------------------------------------------


def _lookup(payload: dict[str, Any], key: str, aliases: Iterable[str]) -> Any:
    """Return the bucket for a key, falling back to aliases."""

    if key in payload:
        return payload[key]
    for alias in aliases:
        if alias in payload:
            return payload[alias]
    return None


def _extract_events(raw_events: Any) -> list[dict[str, Any]]:
    """Coerce a topic's events bucket into a list of event rows.

    Each event is re-keyed onto ``EVENT_COLUMNS``. ``prev_event_id`` is
    auto-filled to chain consecutive events when the caller omits it, so a
    plain time-ordered list still produces a valid chain.
    """

    if raw_events is None:
        return [_empty_row(EVENT_COLUMNS)]
    if isinstance(raw_events, dict):
        raw_events = [raw_events]
    if not isinstance(raw_events, list):
        return [_empty_row(EVENT_COLUMNS)]

    rows: list[dict[str, Any]] = []
    for idx, item in enumerate(raw_events):
        if not isinstance(item, dict):
            continue
        row = _coerce_row(item, EVENT_COLUMNS)
        if not row.get("sequence"):
            row["sequence"] = idx + 1
        # Auto-link if the caller did not specify prev_event_id but the
        # previous row has an event_id — keeps the chain coherent for the
        # common case of a plain time-ordered list.
        if not row.get("prev_event_id") and idx > 0:
            prev_id = rows[-1].get("event_id") if rows else ""
            if prev_id:
                row["prev_event_id"] = prev_id
        rows.append(row)

    if not rows:
        rows = [_empty_row(EVENT_COLUMNS)]
    return rows


def _extract_topic(raw_topic: Any, index: int) -> TopicChain:
    """Materialize one topic dict into a TopicChain."""

    if not isinstance(raw_topic, dict):
        raw_topic = {}

    by_slug = {_slugify(k): v for k, v in raw_topic.items()}

    topic_name = str(by_slug.get("topic") or by_slug.get("name") or "")
    topic_id = str(
        by_slug.get("topic_id")
        or by_slug.get("id")
        or _file_slug(topic_name, "topic-{}".format(index + 1))
    )

    raw_events = _lookup(by_slug, "events", EVENT_ALIASES)
    events = _extract_events(raw_events)

    populated = [e for e in events if _row_has_payload(e)]
    head_id = populated[0].get("event_id", "") if populated else ""
    tail_id = populated[-1].get("event_id", "") if populated else ""

    meta = {
        "topic_id": topic_id,
        "topic": topic_name,
        "summary": by_slug.get("summary", ""),
        "status": by_slug.get("status", ""),
        "created_at": by_slug.get("created_at", ""),
        "last_updated": by_slug.get("last_updated", ""),
        "tags": _format_tags(by_slug.get("tags", "")),
        "event_count": len(populated),
        "head_event_id": head_id,
        "tail_event_id": tail_id,
    }

    return TopicChain(topic_id=topic_id, meta=meta, events=events)


def _format_tags(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(v) for v in value if v not in ("", None))
    return str(value) if value not in ("", None) else ""


def extract_topics(payload: dict[str, Any]) -> list[TopicChain]:
    """Top-level: pull the topic list out of any tolerated payload shape."""

    raw_topics = _lookup(payload, "topics", TOPIC_ALIASES)

    # Tolerate a single-topic payload like {topic: "...", events: [...]}.
    if raw_topics is None and ("topic" in payload or "events" in payload):
        raw_topics = [payload]

    if raw_topics is None:
        return [_extract_topic({}, 0)]
    if isinstance(raw_topics, dict):
        raw_topics = [raw_topics]
    if not isinstance(raw_topics, list):
        return [_extract_topic({}, 0)]

    if not raw_topics:
        return [_extract_topic({}, 0)]

    # Ensure unique topic_ids so output files don't collide.
    chains: list[TopicChain] = []
    seen: set[str] = set()
    for i, raw in enumerate(raw_topics):
        chain = _extract_topic(raw, i)
        base = chain.topic_id
        suffix = 2
        while chain.topic_id in seen:
            chain.topic_id = "{}-{}".format(base, suffix)
            chain.meta["topic_id"] = chain.topic_id
            suffix += 1
        seen.add(chain.topic_id)
        chains.append(chain)
    return chains


# ---------------------------------------------------------------------------
# Cover construction
# ---------------------------------------------------------------------------


COVER_COLUMNS: tuple[str, ...] = ("section", "metric", "value", "notes")


def build_cover_rows(chains: list[TopicChain]) -> list[dict[str, Any]]:
    """Synthesize a Cover sheet summarizing the topics in this workbook."""

    total_topics = len(chains)
    total_events = sum(c.event_count for c in chains)
    rows: list[dict[str, Any]] = [
        {
            "section": "Header",
            "metric": "Tracker type",
            "value": "Marginal tracker (topic-chained events)",
            "notes": "Each topic carries one append-only event chain.",
        },
        {
            "section": "Header",
            "metric": "Topics / events",
            "value": "{} / {}".format(total_topics, total_events),
            "notes": "Empty chains still show one placeholder row.",
        },
    ]

    for chain in chains:
        m = chain.meta
        rows.append(
            {
                "section": "Topic",
                "metric": m.get("topic") or chain.topic_id,
                "value": "{} events · head {} · tail {}".format(
                    m.get("event_count", 0) or 0,
                    m.get("head_event_id") or "—",
                    m.get("tail_event_id") or "—",
                ),
                "notes": m.get("summary", ""),
            }
        )

    rows.append(
        {
            "section": "Workbook map",
            "metric": "topics.csv",
            "value": "Topic index",
            "notes": "One row per topic with chain head/tail and counts.",
        }
    )
    rows.append(
        {
            "section": "Workbook map",
            "metric": "events__<topic_id>.csv",
            "value": "Per-topic event chain",
            "notes": "Each row is one event; prev_event_id links the chain.",
        }
    )
    return rows


# ---------------------------------------------------------------------------
# Writers
# ---------------------------------------------------------------------------


def write_csv(path: Path, columns: Iterable[str], rows: Iterable[dict[str, Any]]) -> None:
    cols = list(columns)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        for row in rows:
            writer.writerow({c: row.get(c, "") for c in cols})


def event_csv_name(topic_id: str) -> str:
    return "events__{}.csv".format(_file_slug(topic_id, "topic"))


def write_xlsx_workbook(path: Path, chains: list[TopicChain]) -> None:
    """Emit a single XLSX file containing Cover + topics index + one tab per chain."""

    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill
    except ImportError as exc:  # pragma: no cover - exercised via runtime check
        raise RuntimeError(
            "openpyxl is required for --xlsx-out. CSV outputs were still created."
        ) from exc

    wb = Workbook()
    wb.remove(wb.active)

    header_fill = PatternFill("solid", fgColor="1F4E78")
    header_font = Font(color="FFFFFF", bold=True)

    def _style_header(ws_obj) -> None:
        for cell in ws_obj[1]:
            cell.fill = header_fill
            cell.font = header_font

    # Cover sheet first.
    cover = wb.create_sheet("Cover")
    cover.append(list(COVER_COLUMNS))
    _style_header(cover)
    for row in build_cover_rows(chains):
        cover.append([row.get(c, "") for c in COVER_COLUMNS])
    cover.freeze_panes = "A2"
    for col_letter, width in {"A": 18, "B": 36, "C": 46, "D": 70}.items():
        cover.column_dimensions[col_letter].width = width

    # Topic index.
    topics_ws = wb.create_sheet("topics")
    topics_ws.append(list(TOPIC_COLUMNS))
    _style_header(topics_ws)
    for chain in chains:
        topics_ws.append([chain.meta.get(c, "") for c in TOPIC_COLUMNS])
    topics_ws.freeze_panes = "A2"

    # One sheet per topic chain.
    used_names: set[str] = {"Cover", "topics"}
    for chain in chains:
        base = _file_slug(chain.topic_id, "topic")[:25] or "topic"
        name = base
        suffix = 2
        while name in used_names or len(name) > 31:
            name = "{}-{}".format(base[: max(1, 28 - len(str(suffix)))], suffix)
            suffix += 1
        used_names.add(name)

        ws = wb.create_sheet(name)
        ws.append(list(EVENT_COLUMNS))
        _style_header(ws)
        for row in chain.events:
            ws.append([row.get(c, "") for c in EVENT_COLUMNS])
        ws.freeze_panes = "A2"

    wb.save(path)


# ---------------------------------------------------------------------------
# Run log + manifest
# ---------------------------------------------------------------------------


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def compute_output_paths(
    output_dir: Path, chains: list[TopicChain], xlsx_out: Path | None
) -> dict[str, str]:
    """All artifact paths the run is responsible for, keyed by purpose."""

    paths: dict[str, str] = {
        "topics": str(output_dir / "topics.csv"),
    }
    for chain in chains:
        paths["events:{}".format(chain.topic_id)] = str(
            output_dir / event_csv_name(chain.topic_id)
        )
    paths["run_log"] = str(output_dir / "run_log.json")
    paths["manifest"] = str(output_dir / "manifest.json")
    if xlsx_out is not None:
        paths["xlsx"] = str(xlsx_out)
    return paths


def build_output_manifest(
    paths: dict[str, str],
    *,
    require_xlsx: bool,
    xlsx_is_primary: bool,
) -> list[dict[str, Any]]:
    """One manifest row per artifact, tagged with delivery role."""

    manifest: list[dict[str, Any]] = []
    machine_only = {"run_log", "manifest"}

    for key, p in paths.items():
        is_xlsx = key == "xlsx"
        is_primary = is_xlsx and xlsx_is_primary
        if is_primary:
            role = "primary_human_deliverable"
        elif key in machine_only:
            role = "machine_support"
        else:
            role = "support_artifact"

        manifest.append(
            {
                "key": key,
                "path": p,
                "required": (not is_xlsx) or require_xlsx,
                "written": key in machine_only or Path(p).exists(),
                "description": "Marginal tracker artifact.",
                "artifact_role": role,
                "hidden_unless_requested": not is_primary,
            }
        )
    return manifest


def write_run_artifacts(output_dir: Path, run_log: dict[str, Any]) -> None:
    """Persist run_log.json and manifest.json next to the CSVs."""

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "run_log.json").write_text(
        json.dumps(run_log, indent=2) + "\n", encoding="utf-8"
    )

    primary = run_log.get("primary_human_deliverable")
    manifest = {
        "outputs": run_log["output_manifest"],
        "primary_human_deliverable": primary,
        "human_deliverables": [primary] if primary else [],
        "support_artifacts": [
            entry["path"]
            for entry in run_log["output_manifest"]
            if entry.get("artifact_role") != "primary_human_deliverable"
        ],
        "support_artifacts_user_visible_default": False,
        "final_response_guidance": {
            "lead_with": "primary_human_deliverable" if primary else "concise_status",
            "mention_support_artifacts": "only_briefly_unless_requested",
        },
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Payload loading
# ---------------------------------------------------------------------------


def load_payload(path: Path | None) -> dict[str, Any]:
    """Read the optional input JSON; empty payload is a valid no-op."""

    if path is None:
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("input JSON must be an object")
    return raw


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


@dataclass
class RunContext:
    input_json: Path | None
    output_dir: Path
    xlsx_out: Path | None


def _base_run_log(
    status: str, ctx: RunContext, paths: dict[str, str], **extra: Any
) -> dict[str, Any]:
    log: dict[str, Any] = {
        "status": status,
        "model_status": "senior-review-ready"
        if status == "completed"
        else "not-decision-ready",
        "artifact_level": "marginal_tracker_bundle",
        "workbook_mode": "marginal_tracker_bundle",
        "artifact_mode": "marginal_tracker_bundle",
        "generated_at": _now_utc_iso(),
        "input_json": str(ctx.input_json) if ctx.input_json else None,
        "outputs": paths,
        "xlsx_requested": ctx.xlsx_out is not None,
        "xlsx_written": False,
        "hard_failures": [],
        "warnings": [],
        "topics": [],
    }
    log.update(extra)
    return log


def _emit_failure(
    ctx: RunContext, paths: dict[str, str], message: str
) -> int:
    log = _base_run_log("failed", ctx, paths)
    log["hard_failures"].append(message)
    log["output_manifest"] = build_output_manifest(
        paths, require_xlsx=ctx.xlsx_out is not None, xlsx_is_primary=False
    )
    write_run_artifacts(ctx.output_dir, log)
    print("ERROR: {}".format(message), file=sys.stderr)
    return 1


def run(ctx: RunContext) -> int:
    """Top-level orchestration; returns the process exit code."""

    ctx.output_dir.mkdir(parents=True, exist_ok=True)

    # Step 1 — load input.
    try:
        payload = load_payload(ctx.input_json)
    except Exception as exc:
        # We don't know chains yet; emit a minimal failure manifest.
        paths = {
            "topics": str(ctx.output_dir / "topics.csv"),
            "run_log": str(ctx.output_dir / "run_log.json"),
            "manifest": str(ctx.output_dir / "manifest.json"),
        }
        if ctx.xlsx_out is not None:
            paths["xlsx"] = str(ctx.xlsx_out)
        return _emit_failure(ctx, paths, str(exc))

    # Step 2 — pull topics + events.
    try:
        chains = extract_topics(payload)
    except Exception as exc:
        paths = {
            "topics": str(ctx.output_dir / "topics.csv"),
            "run_log": str(ctx.output_dir / "run_log.json"),
            "manifest": str(ctx.output_dir / "manifest.json"),
        }
        return _emit_failure(ctx, paths, "could not parse topics: {}".format(exc))

    paths = compute_output_paths(ctx.output_dir, chains, ctx.xlsx_out)

    # Step 3 — write the topics index + one CSV per topic chain.
    try:
        write_csv(
            ctx.output_dir / "topics.csv",
            TOPIC_COLUMNS,
            [chain.meta for chain in chains],
        )
        for chain in chains:
            write_csv(
                ctx.output_dir / event_csv_name(chain.topic_id),
                EVENT_COLUMNS,
                chain.events,
            )
    except Exception as exc:
        return _emit_failure(ctx, paths, "could not write output: {}".format(exc))

    # Step 4 — success log + optional XLSX.
    log = _base_run_log(
        "completed",
        ctx,
        paths,
        topics=[chain.meta for chain in chains],
    )

    if ctx.xlsx_out is not None:
        try:
            write_xlsx_workbook(ctx.xlsx_out, chains)
        except Exception as exc:
            log["status"] = "failed"
            log["model_status"] = "not-decision-ready"
            log["hard_failures"].append(str(exc))
            log["warnings"].append(str(exc))
            log["output_manifest"] = build_output_manifest(
                paths, require_xlsx=True, xlsx_is_primary=False
            )
            write_run_artifacts(ctx.output_dir, log)
            print("ERROR: {}".format(exc), file=sys.stderr)
            return 1
        log["xlsx_written"] = True
        log["xlsx_path"] = str(ctx.xlsx_out)

    if log["xlsx_written"]:
        log["primary_human_deliverable"] = str(ctx.xlsx_out)
        log["artifact_mode"] = "workbook"
        log["workbook_mode"] = "xlsx_marginal_workbook"
    else:
        log["primary_human_deliverable"] = None

    log["output_manifest"] = build_output_manifest(
        paths,
        require_xlsx=ctx.xlsx_out is not None,
        xlsx_is_primary=bool(log["xlsx_written"]),
    )
    write_run_artifacts(ctx.output_dir, log)
    print("Wrote marginal tracker bundle to {}".format(ctx.output_dir))
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Materialize a multi-topic marginal tracker CSV bundle "
            "(plus an optional XLSX workbook). Each topic carries a "
            "single append-only event chain."
        ),
    )
    parser.add_argument(
        "input_json",
        nargs="?",
        type=Path,
        help="Optional JSON file holding topics and their event chains.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Directory to write the CSV bundle and run artifacts into.",
    )
    parser.add_argument(
        "--xlsx-out",
        type=Path,
        default=None,
        help="If set, also write a single-file XLSX workbook to this path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argparser().parse_args(argv)
    ctx = RunContext(
        input_json=args.input_json,
        output_dir=args.output_dir,
        xlsx_out=args.xlsx_out,
    )
    return run(ctx)


if __name__ == "__main__":
    raise SystemExit(main())
