#!/usr/bin/env python3
"""Run deterministic structural checks on a detective-fiction project."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
from typing import Any


REQUIRED_FILES = (
    "project-charter.md",
    "case-bible.md",
    "outline.md",
    "mystery-ledger.md",
    "style-guide.md",
    "notes.md",
    "audit-report.md",
)
LEDGER_STATUSES = {"计划中", "已埋设", "已强化", "已回收", "已废弃"}
CHAPTER_STATUSES = {"draft", "canonical", "superseded"}
CHECK_STATUSES = {"pending", "pass", "fail"}
OUTLINE_DEVIATIONS = {"none", "accepted", "change_required"}
USER_APPROVALS = {"not_required", "pending", "approved"}
ACTION_NAMES = ("seed", "reinforce", "pay_off", "retire")
REQUIRED_CHECKS = ("pov", "continuity", "ledger_synced", "notes_synced")
CHECK_KEYS = REQUIRED_CHECKS + ("outline_deviation", "user_approval")

LEDGER_ID_RE = re.compile(r"\b([CFR]-\d{3})\b")
LEDGER_ID_FULL_RE = re.compile(r"^[CFR]-\d{3}$")
LEDGER_ID_LIKE_RE = re.compile(r"(?i)^[cfr]-\S+$")
Q_ID_RE = re.compile(r"\b(Q-\d{3})\b")
Q_ID_FULL_RE = re.compile(r"^Q-\d{3}$")
Q_ID_LIKE_RE = re.compile(r"(?i)^q-\S+$")
Q_ID_TOKEN_RE = re.compile(r"(?i)\bq-[A-Za-z0-9_-]+\b")
# Reader-facing leak check. Only C/F/R/Q-### are workflow IDs that can appear
# in chapters; A/H/M-### live in audit-report.md and collide with real-world
# doorplate/plate/model numbers (e.g. A-301, M-208, H-115), so they stay out.
INTERNAL_ID_RE = re.compile(r"\b(?:C|F|R|Q)-\d{3}\b", re.IGNORECASE)
TEMPLATE_TOKEN_RE = re.compile(r"\{\{[^{}\r\n]+\}\}", re.IGNORECASE)
BRACKET_PLACEHOLDER_RE = re.compile(
    r"\[(?:正文|待定|todo|tbd|placeholder)(?:[^\]\r\n]*)\]", re.IGNORECASE
)
TODO_RE = re.compile(r"\bTODO\b", re.IGNORECASE)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
# Lone `<!--` always signals a broken internal container; a closing `-->`
# only counts at line start, so prose like "草稿 --> 定稿" stays clean.
HTML_COMMENT_DELIMITER_RE = re.compile(r"<!--|^[ \t]*-->", re.MULTILINE)
INTERNAL_MARKER_RE = re.compile(
    r"\bINTERNAL(?:[-_ ][A-Z0-9]+)+\b", re.IGNORECASE
)
CHAPTER_FILE_RE = re.compile(r"chapter-(\d+)\.md$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check mystery project files, IDs, chapter gates, and exports."
    )
    parser.add_argument("project_dir", help="Project directory to audit")
    parser.add_argument(
        "--chapter",
        metavar="chapter-XX.md",
        help="Run the canonical-candidate completion gate for one chapter",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return a non-zero status when warnings are present",
    )
    return parser.parse_args()


def is_blank(value: str) -> bool:
    return value.strip() in {"", "—", "-", "无", "待定"}


def table_cells(line: str) -> list[str] | None:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    return [cell.strip() for cell in stripped[1:-1].split("|")]


def frontmatter(text: str) -> str | None:
    normalized = text.replace("\r\n", "\n")
    if normalized.startswith("\ufeff"):
        normalized = normalized[1:]
    if not normalized.startswith("---\n"):
        return None
    end = normalized.find("\n---\n", 4)
    if end == -1:
        return None
    return normalized[4:end]


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _strip_comment(value: str) -> str:
    """Drop a trailing ` # comment`; quoted values are left untouched."""
    if value[:1] in {"'", '"'}:
        return value
    return re.sub(r"\s+#.*$", "", value).rstrip()


def read_project_text(path: Path, errors: list[str], label: str) -> str | None:
    """Read a project file as UTF-8; report instead of crashing on bad input."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        errors.append(f"{label} is not readable as UTF-8; save the file as UTF-8")
        return None


def parse_inline_list(value: str) -> tuple[list[str], str | None]:
    value = value.strip()
    if not (value.startswith("[") and value.endswith("]")):
        return [], "must be an inline YAML list such as [] or [C-001]"
    inner = value[1:-1].strip()
    if not inner:
        return [], None
    return [_unquote(item) for item in inner.split(",")], None


def parse_chapter_metadata(metadata: str) -> tuple[dict[str, Any], list[str]]:
    """Parse the small, deliberately constrained chapter frontmatter schema.

    Lists accept both inline form (`key: [C-001]`) and block sequences
    (`key:` followed by indented `- C-001` lines); both are standard YAML.
    """
    values: dict[str, Any] = {}
    issues: list[str] = []
    section: str | None = None
    subsection: str | None = None

    for lineno, raw_line in enumerate(metadata.splitlines(), start=2):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        if line.startswith("[") and indent in {2, 4}:
            # Flow-style list on its own indented line (`seed:` then `[]`).
            parsed, problem = parse_inline_list(_strip_comment(line))
            if problem:
                issues.append(f"frontmatter line {lineno} {problem}")
                continue
            if (
                indent == 2
                and section is not None
                and subsection is None
                and isinstance(values.get(section), dict)
                and not values[section]
            ):
                values[section] = parsed
            elif (
                indent == 4
                and section is not None
                and subsection is not None
                and isinstance(values.get(section), dict)
                and isinstance(values[section].get(subsection), dict)
                and not values[section][subsection]
            ):
                values[section][subsection] = parsed
            else:
                issues.append(
                    f"frontmatter line {lineno} is not a supported key/value"
                )
            continue

        if line.startswith("- "):
            item = _unquote(_strip_comment(line[2:].strip()))
            target: Any = None
            if indent == 2 and section is not None and subsection is None:
                target = values.get(section)
                if isinstance(target, dict) and not target:
                    target = values[section] = []
            elif (
                indent == 4
                and section is not None
                and subsection is not None
                and isinstance(values.get(section), dict)
            ):
                target = values[section].get(subsection)
                if isinstance(target, dict) and not target:
                    target = values[section][subsection] = []
            if isinstance(target, list):
                target.append(item)
            else:
                issues.append(
                    f"frontmatter line {lineno} is not a supported key/value"
                )
            continue

        match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_-]*):(?:\s*(.*))?", line)
        if not match:
            issues.append(f"frontmatter line {lineno} is not a supported key/value")
            continue
        key, raw_value = match.group(1), _strip_comment(match.group(2) or "")
        if indent == 0:
            section, subsection = None, None
            if raw_value == "":
                values[key] = {}
                section = key
            elif raw_value.startswith("["):
                parsed, problem = parse_inline_list(raw_value)
                if problem:
                    issues.append(f"frontmatter {key} {problem}")
                values[key] = parsed
            else:
                values[key] = _unquote(raw_value)
            continue

        if indent != 2 or section is None or not isinstance(values.get(section), dict):
            issues.append(f"frontmatter line {lineno} has unsupported indentation")
            continue
        subsection = None
        if raw_value == "":
            values[section][key] = {}
            subsection = key
        elif raw_value.startswith("["):
            parsed, problem = parse_inline_list(raw_value)
            if problem:
                issues.append(f"frontmatter {section}.{key} {problem}")
            values[section][key] = parsed
        else:
            values[section][key] = _unquote(raw_value)

    return values, issues


def clean_manuscript_issues(text: str) -> list[str]:
    """Return reader-facing cleanliness violations for an export."""
    issues: list[str] = []
    normalized = text.replace("\r\n", "\n")
    if normalized.startswith("---\n") and "\n---\n" in normalized[4:]:
        issues.append("contains YAML frontmatter")

    ids = sorted(set(INTERNAL_ID_RE.findall(normalized)))
    if ids:
        issues.append(f"contains internal IDs: {', '.join(ids)}")
    tokens = sorted(set(TEMPLATE_TOKEN_RE.findall(normalized)))
    if tokens:
        issues.append(f"contains template tokens: {', '.join(tokens)}")
    bracket_tokens = sorted(set(BRACKET_PLACEHOLDER_RE.findall(normalized)))
    if bracket_tokens:
        issues.append(f"contains bracket placeholders: {', '.join(bracket_tokens)}")
    if "待定" in normalized:
        issues.append("contains unresolved '待定' markers")
    if TODO_RE.search(normalized):
        issues.append("contains TODO markers")
    if HTML_COMMENT_RE.search(normalized) or HTML_COMMENT_DELIMITER_RE.search(normalized):
        issues.append("contains HTML comments or unmatched comment delimiters")
    if INTERNAL_MARKER_RE.search(normalized):
        issues.append("contains internal workflow markers")
    return issues


def canonical_metadata_issues(metadata: dict[str, Any]) -> list[str]:
    """Return completion-gate failures encoded in chapter metadata."""
    issues: list[str] = []
    raw_checks = metadata.get("checks")
    checks = raw_checks if isinstance(raw_checks, dict) else {}
    for name in REQUIRED_CHECKS:
        if checks.get(name) != "pass":
            issues.append(f"canonical gate requires checks.{name}: pass")
    if checks.get("outline_deviation") not in {"none", "accepted"}:
        issues.append(
            "canonical gate requires checks.outline_deviation: none or accepted"
        )
    if checks.get("user_approval") not in {"not_required", "approved"}:
        issues.append(
            "canonical gate requires checks.user_approval: not_required or approved"
        )
    return issues


def _parse_ledger(path: Path, errors: list[str]) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    if not path.is_file():
        return records

    text = read_project_text(path, errors, path.name)
    if text is None:
        return records

    for lineno, line in enumerate(text.splitlines(), start=1):
        cells = table_cells(line)
        if not cells:
            continue
        raw_id = cells[0]
        if raw_id in {"ID", "---"} or set(raw_id) <= {"-", ":"}:
            continue
        if LEDGER_ID_LIKE_RE.fullmatch(raw_id) and not LEDGER_ID_FULL_RE.fullmatch(raw_id):
            errors.append(f"mystery-ledger.md:{lineno} has malformed ledger ID '{raw_id}'")
            continue
        if not LEDGER_ID_FULL_RE.fullmatch(raw_id):
            continue
        if raw_id in records:
            errors.append(
                f"mystery-ledger.md:{lineno} duplicates {raw_id} "
                f"from line {records[raw_id]['line']}"
            )
            continue
        if len(cells) != 12:
            errors.append(
                f"mystery-ledger.md:{lineno} has {len(cells)} columns; expected 12"
            )
            continue

        record = {
            "line": lineno,
            "kind": cells[1],
            "support": cells[3],
            "actual_occurrence": cells[5],
            "real_meaning": cells[7],
            "actual_payoff": cells[9],
            "status": cells[10],
        }
        records[raw_id] = record
        expected_kind = {"C": "线索", "F": "伏笔", "R": "红鲱鱼"}[raw_id[0]]
        if expected_kind not in record["kind"]:
            errors.append(
                f"mystery-ledger.md:{lineno} {raw_id} type should include '{expected_kind}'"
            )
        if record["status"] not in LEDGER_STATUSES:
            errors.append(
                f"mystery-ledger.md:{lineno} {raw_id} has invalid status "
                f"'{record['status']}'"
            )
        if raw_id.startswith("R-") and is_blank(record["real_meaning"]):
            errors.append(
                f"mystery-ledger.md:{lineno} {raw_id} lacks a truthful explanation"
            )
        if record["status"] in {"已埋设", "已强化", "已回收"} and is_blank(
            record["actual_occurrence"]
        ):
            errors.append(
                f"mystery-ledger.md:{lineno} {raw_id} is {record['status']} "
                "but has no actual occurrence"
            )
        if record["status"] == "已回收" and is_blank(record["actual_payoff"]):
            errors.append(
                f"mystery-ledger.md:{lineno} {raw_id} is paid off but has no payoff location"
            )
    return records


def _parse_conclusions(path: Path, errors: list[str]) -> dict[str, int]:
    conclusions: dict[str, int] = {}
    if not path.is_file():
        return conclusions

    text = read_project_text(path, errors, path.name)
    if text is None:
        return conclusions

    for lineno, line in enumerate(text.splitlines(), start=1):
        cells = table_cells(line)
        if not cells:
            continue
        raw_id = cells[0]
        if raw_id in {"结论编号", "---"} or set(raw_id) <= {"-", ":"}:
            continue
        if Q_ID_LIKE_RE.fullmatch(raw_id) and not Q_ID_FULL_RE.fullmatch(raw_id):
            errors.append(f"case-bible.md:{lineno} has malformed conclusion ID '{raw_id}'")
            continue
        if not Q_ID_FULL_RE.fullmatch(raw_id):
            continue
        if raw_id in conclusions:
            errors.append(
                f"case-bible.md:{lineno} duplicates {raw_id} "
                f"from line {conclusions[raw_id]}"
            )
            continue
        conclusions[raw_id] = lineno
        if len(cells) != 6:
            errors.append(f"case-bible.md:{lineno} has {len(cells)} columns; expected 6")
    return conclusions


def _validate_conclusion_links(
    ledger: dict[str, dict[str, Any]], conclusions: dict[str, int], errors: list[str]
) -> None:
    for item_id, record in ledger.items():
        if not item_id.startswith("C-"):
            continue
        support = record["support"]
        tokens = Q_ID_TOKEN_RE.findall(support)
        malformed = sorted({token for token in tokens if not Q_ID_FULL_RE.fullmatch(token)})
        for token in malformed:
            errors.append(
                f"mystery-ledger.md:{record['line']} {item_id} has malformed "
                f"conclusion ID '{token}'"
            )
        q_ids = sorted(set(Q_ID_RE.findall(support)))
        if not q_ids:
            errors.append(
                f"mystery-ledger.md:{record['line']} {item_id} lacks a Q-### conclusion reference"
            )
        for q_id in q_ids:
            if q_id not in conclusions:
                errors.append(
                    f"mystery-ledger.md:{record['line']} {item_id} references "
                    f"unknown conclusion ID {q_id}"
                )


def _chapter_reference_matches(value: str, chapter_name: str) -> bool:
    match = CHAPTER_FILE_RE.fullmatch(chapter_name)
    if not match:
        return False
    number = int(match.group(1))
    patterns = (
        rf"(?i)(?<![A-Za-z0-9])chapter[-_ ]*0*{number}(?:\.md)?(?!\d)",
        rf"(?i)(?<![A-Za-z0-9])ch[-_ ]*0*{number}(?!\d)",
        rf"第\s*0*{number}\s*章",
    )
    return any(re.search(pattern, value) for pattern in patterns)


def _validate_action_reconciliation(
    chapter_label: str,
    action_ids: dict[str, list[str]],
    ledger: dict[str, dict[str, Any]],
    errors: list[str],
) -> None:
    actions_by_id: dict[str, set[str]] = {}
    for action, ids in action_ids.items():
        for item_id in ids:
            actions_by_id.setdefault(item_id, set()).add(action)

    for item_id, actions in sorted(actions_by_id.items()):
        record = ledger.get(item_id)
        if record is None:
            continue
        if actions & {"seed", "reinforce"} and not _chapter_reference_matches(
            record["actual_occurrence"], chapter_label
        ):
            errors.append(
                f"chapters/{chapter_label} ledger action for {item_id} is not recorded "
                "in the ledger's actual occurrence"
            )
        if "pay_off" in actions and not _chapter_reference_matches(
            record["actual_payoff"], chapter_label
        ):
            errors.append(
                f"chapters/{chapter_label} pay_off for {item_id} is not recorded "
                "in the ledger's actual payoff"
            )

        status = record["status"]
        if "retire" in actions:
            allowed = {"已废弃"}
        elif "pay_off" in actions:
            allowed = {"已回收"}
        elif "reinforce" in actions:
            allowed = {"已强化", "已回收"}
        else:
            allowed = {"已埋设", "已强化", "已回收"}
        if status not in allowed:
            errors.append(
                f"chapters/{chapter_label} actions for {item_id} are not reconciled: "
                f"ledger status is '{status}', expected one of {', '.join(sorted(allowed))}"
            )


def _validate_chapter(
    chapter: Path,
    project: Path,
    ledger: dict[str, dict[str, Any]],
    gate: bool,
    selected: bool,
    errors: list[str],
    warnings: list[str],
) -> None:
    relative = chapter.relative_to(project)
    text = read_project_text(chapter, errors, str(relative))
    if text is None:
        return
    metadata_text = frontmatter(text)
    if metadata_text is None:
        errors.append(f"{relative} has no valid YAML frontmatter")
        return
    metadata, parse_issues = parse_chapter_metadata(metadata_text)
    errors.extend(f"{relative} {issue}" for issue in parse_issues)

    file_match = CHAPTER_FILE_RE.fullmatch(chapter.name)
    if not file_match:
        warnings.append(f"{relative} does not use chapter-XX.md naming")
    chapter_value = str(metadata.get("chapter", ""))
    if not re.fullmatch(r"\d+", chapter_value):
        errors.append(f"{relative} has missing or invalid chapter number '{chapter_value}'")
    elif file_match and int(file_match.group(1)) != int(chapter_value):
        errors.append(f"{relative} chapter number disagrees with filename")

    status = str(metadata.get("status", ""))
    if status not in CHAPTER_STATUSES:
        errors.append(f"{relative} has invalid status '{status}'")
    if selected and status == "superseded":
        errors.append(f"{relative} is superseded and cannot be a canonical candidate")

    raw_actions = metadata.get("ledger_actions")
    action_ids: dict[str, list[str]] = {name: [] for name in ACTION_NAMES}
    if not isinstance(raw_actions, dict):
        if gate:
            errors.append(f"{relative} lacks ledger_actions mapping")
    else:
        unknown_actions = sorted(set(raw_actions) - set(ACTION_NAMES))
        for action in unknown_actions:
            errors.append(f"{relative} has unknown ledger action '{action}'")
        for action in ACTION_NAMES:
            raw_ids = raw_actions.get(action)
            if raw_ids is None:
                if gate:
                    errors.append(f"{relative} lacks ledger_actions.{action}")
                continue
            if not isinstance(raw_ids, list):
                errors.append(
                    f"{relative} ledger_actions.{action} must be a list "
                    "(inline [C-001] or indented - C-001 lines)"
                )
                continue
            for item_id in raw_ids:
                if not LEDGER_ID_FULL_RE.fullmatch(item_id):
                    errors.append(
                        f"{relative} ledger_actions.{action} has malformed ID '{item_id}'"
                    )
                elif item_id not in ledger:
                    errors.append(
                        f"{relative} ledger_actions.{action} references unknown ledger ID {item_id}"
                    )
                else:
                    action_ids[action].append(item_id)

    raw_dependencies = metadata.get("continuity_dependencies")
    if raw_dependencies is None:
        if gate:
            errors.append(f"{relative} lacks continuity_dependencies")
    elif not isinstance(raw_dependencies, list):
        errors.append(
            f"{relative} continuity_dependencies must be a list "
            "(inline [chapter-01.md] or indented - chapter-01.md lines)"
        )
    else:
        for dependency in raw_dependencies:
            if not CHAPTER_FILE_RE.fullmatch(dependency):
                errors.append(
                    f"{relative} has malformed continuity dependency '{dependency}'"
                )
                continue
            if dependency == chapter.name:
                errors.append(f"{relative} cannot depend on itself")
            elif not (project / "chapters" / dependency).is_file():
                errors.append(
                    f"{relative} references missing continuity dependency {dependency}"
                )

    raw_checks = metadata.get("checks")
    if raw_checks is not None and not isinstance(raw_checks, dict):
        errors.append(f"{relative} checks must be a mapping")
        raw_checks = {}
    checks = raw_checks if isinstance(raw_checks, dict) else {}
    for name, value in checks.items():
        if name not in CHECK_KEYS:
            errors.append(f"{relative} has unknown completion check '{name}'")
        elif name in REQUIRED_CHECKS and value not in CHECK_STATUSES:
            errors.append(f"{relative} checks.{name} has invalid value '{value}'")
    outline_deviation = str(checks.get("outline_deviation", ""))
    if outline_deviation and outline_deviation not in OUTLINE_DEVIATIONS:
        errors.append(
            f"{relative} has invalid checks.outline_deviation '{outline_deviation}'"
        )
    user_approval = str(checks.get("user_approval", ""))
    if user_approval and user_approval not in USER_APPROVALS:
        errors.append(
            f"{relative} has invalid checks.user_approval '{user_approval}'"
        )

    if not gate:
        return
    errors.extend(
        f"{relative} {issue}" for issue in canonical_metadata_issues(metadata)
    )
    _validate_action_reconciliation(chapter.name, action_ids, ledger, errors)


def main() -> int:
    args = parse_args()
    project = Path(args.project_dir).expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []

    if not project.is_dir():
        print(f"ERROR: project directory not found: {project}", file=sys.stderr)
        return 2

    selected_name: str | None = None
    if args.chapter:
        candidate = Path(args.chapter)
        if candidate.name != args.chapter or not CHAPTER_FILE_RE.fullmatch(args.chapter):
            errors.append("--chapter must be a chapter-XX.md filename, not a path")
        else:
            selected_name = args.chapter
            if not (project / "chapters" / selected_name).is_file():
                errors.append(f"selected chapter not found: chapters/{selected_name}")

    for relative in REQUIRED_FILES:
        if not (project / relative).is_file():
            errors.append(f"missing required file: {relative}")
    for relative in ("chapters", "exports"):
        if not (project / relative).is_dir():
            errors.append(f"missing required directory: {relative}/")

    for relative in REQUIRED_FILES:
        path = project / relative
        if not path.is_file():
            continue
        text = read_project_text(path, errors, relative)
        if text is None:
            continue
        tokens = sorted(set(TEMPLATE_TOKEN_RE.findall(text)))
        if tokens:
            errors.append(
                f"{relative} contains unresolved template tokens: {', '.join(tokens)}"
            )
        # notes.md is the sanctioned scratch space for unresolved items
        # (longform-workflow.md §2); its '待定' markers never warn, so they
        # cannot fail --strict. Authoritative files still warn.
        if relative == "notes.md":
            continue
        pending_count = text.count("待定")
        if pending_count:
            warnings.append(
                f"{relative} contains {pending_count} unresolved '待定' markers"
            )

    if args.strict:
        report_path = project / "audit-report.md"
        if report_path.is_file():
            report_text = read_project_text(report_path, errors, "audit-report.md")
            if report_text is not None:
                snapshot = re.search(
                    r"(?m)^>\s*快照状态：\s*([A-Za-z_]+)\s*$", report_text
                )
                if snapshot is None:
                    errors.append(
                        "audit-report.md lacks a machine-readable snapshot status"
                    )
                elif snapshot.group(1) != "current":
                    errors.append(
                        "audit-report.md snapshot status must be current in strict mode; "
                        "complete the audit, then set 快照状态：current"
                    )

    ledger = _parse_ledger(project / "mystery-ledger.md", errors)
    conclusions = _parse_conclusions(project / "case-bible.md", errors)
    _validate_conclusion_links(ledger, conclusions, errors)

    chapters_dir = project / "chapters"
    if chapters_dir.is_dir():
        for chapter in sorted(chapters_dir.glob("*.md")):
            if chapter.name.startswith("_"):
                continue
            text = read_project_text(
                chapter, errors, str(chapter.relative_to(project))
            )
            if text is None:
                continue
            metadata_text = frontmatter(text)
            status = ""
            if metadata_text is not None:
                parsed, _ = parse_chapter_metadata(metadata_text)
                status = str(parsed.get("status", ""))
            selected = chapter.name == selected_name
            gate = status == "canonical" or selected
            _validate_chapter(
                chapter, project, ledger, gate, selected, errors, warnings
            )

    exports_dir = project / "exports"
    if exports_dir.is_dir():
        for export in sorted(exports_dir.glob("*.md")):
            text = read_project_text(
                export, errors, str(export.relative_to(project))
            )
            if text is None:
                continue
            for issue in clean_manuscript_issues(text):
                errors.append(f"{export.relative_to(project)} {issue}")

    print(f"Mystery project audit: {project}")
    print(f"Ledger items: {len(ledger)}")
    print(f"Conclusion IDs: {len(conclusions)}")
    if selected_name:
        print(f"Canonical candidate: chapters/{selected_name}")
    if errors:
        print("\nERRORS")
        for item in errors:
            print(f"- {item}")
    if warnings:
        print("\nWARNINGS")
        for item in warnings:
            print(f"- {item}")
    if not errors and not warnings:
        print("\nPASS: no structural issues found")
    else:
        print(f"\nSummary: {len(errors)} error(s), {len(warnings)} warning(s)")

    if errors:
        return 1
    if warnings and args.strict:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
