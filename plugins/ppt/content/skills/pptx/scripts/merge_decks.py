#!/usr/bin/env python3
"""merge_decks.py — Merge structural-base.pptx and content-only.pptx into a final deck.

Usage:
    uv run --with python-pptx merge_decks.py \
        --structural slides/output/structural-base.pptx \
        --content slides/output/content-only.pptx \
        --order slides/merge-order.json \
        --out slides/output/final.pptx

The merge-order.json specifies the final slide sequence:
[
  {"source": "structural", "slideIdx": 0},
  {"source": "content", "slideIdx": 0},
  {"source": "structural", "slideIdx": 1},
  ...
]

Implementation uses bytes-level XML manipulation to avoid namespace corruption
that xml.etree.ElementTree causes with OOXML default-namespace .rels files.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Low-level helpers: bytes-based XML manipulation (no ET parse→serialize)
# ---------------------------------------------------------------------------


def _insert_before_closing_tag(
    xml_bytes: bytes, closing_tag: bytes, new_elements: list[bytes]
) -> bytes:
    """Insert new XML elements just before a closing tag. Preserves original formatting."""
    insert_pos = xml_bytes.rfind(closing_tag)
    if insert_pos == -1:
        raise ValueError(f"Closing tag {closing_tag!r} not found in XML")
    insertion = b"".join(new_elements)
    return xml_bytes[:insert_pos] + insertion + xml_bytes[insert_pos:]


def _replace_sld_id_lst(pres_xml: bytes, new_entries: list[tuple[int, str]]) -> bytes:
    """Replace the <p:sldIdLst>...</p:sldIdLst> block with new entries."""
    new_content = "".join(
        f'<p:sldId id="{sid}" r:id="{rid}"/>' for sid, rid in new_entries
    )
    replacement = f"<p:sldIdLst>{new_content}</p:sldIdLst>".encode("utf-8")
    result = re.sub(
        rb"<p:sldIdLst>.*?</p:sldIdLst>", replacement, pres_xml, flags=re.DOTALL
    )
    return result


def _filter_rels_keep(rels_bytes: bytes, keep_slide_filenames: set[str]) -> bytes:
    """Remove slide Relationship entries whose Target is not in keep set.

    Non-slide relationships (slideMaster, notesMaster, theme, etc.) are always kept.
    """

    def should_keep(match: re.Match) -> bool:
        target_m = re.search(rb'Target="([^"]*)"', match.group(0))
        if target_m:
            target = target_m.group(1).decode("utf-8")
            if "slides/" in target:
                filename = os.path.basename(target)
                return filename in keep_slide_filenames
        return True

    # Match both self-closing <Relationship .../> and open/close pairs
    pattern = rb"<Relationship [^>]*?/>"
    result = re.sub(
        pattern, lambda m: m.group(0) if should_keep(m) else b"", rels_bytes
    )
    return result


def _add_rels_entries(
    rels_bytes: bytes, new_entries: list[tuple[str, str, str]]
) -> bytes:
    """Add new Relationship entries to a .rels file.

    new_entries: list of (rId, reltype, target) tuples.
    """
    elements = []
    for rid, reltype, target in new_entries:
        elements.append(
            f'<Relationship Id="{rid}" Type="{reltype}" Target="{target}"/>'.encode(
                "utf-8"
            )
        )
    return _insert_before_closing_tag(rels_bytes, b"</Relationships>", elements)


def _find_max_rid_in_bytes(rels_bytes: bytes) -> int:
    """Find the highest rId number in a rels file."""
    matches = re.findall(rb'Id="rId(\d+)"', rels_bytes)
    if not matches:
        return 0
    return max(int(m) for m in matches)


def _find_max_sld_id(pres_xml: bytes) -> int:
    """Find the highest sldId value in presentation.xml."""
    matches = re.findall(rb'<p:sldId id="(\d+)"', pres_xml)
    if not matches:
        return 255
    return max(int(m) for m in matches)


def _drop_notes_relationships(rels_bytes: bytes) -> bytes:
    """Remove notesSlide relationships from a slide relationship part.

    Imported content notes are intentionally written after final slide assembly
    from the final-order notes sidecar. Keeping their original target would either
    dangle or collide with a structural deck notesSlide of the same filename.
    """
    relationship_pattern = rb"<Relationship [^>]*?/>"

    def keep(entry: re.Match) -> bytes:
        if re.search(rb'Type="[^"]*/notesSlide"', entry.group(0)):
            return b""
        return entry.group(0)

    return re.sub(relationship_pattern, keep, rels_bytes)


def _remove_content_types_for_slides(
    ct_bytes: bytes, remove_slides: set[str], remove_dep_parts: list[str] | None = None
) -> bytes:
    """Remove Override entries for specific slide files and their dependent parts from [Content_Types].xml."""
    for slide_file in remove_slides:
        part_name = f"/ppt/slides/{slide_file}"
        pattern = (
            rb'<Override PartName="' + part_name.encode() + rb'"[^>]*?/>'
        )
        ct_bytes = re.sub(pattern, b"", ct_bytes)

    if remove_dep_parts:
        for part_name in remove_dep_parts:
            pattern = (
                rb'<Override PartName="' + part_name.encode() + rb'"[^>]*?/>'
            )
            ct_bytes = re.sub(pattern, b"", ct_bytes)

    return ct_bytes


def _add_content_types_for_slides(ct_bytes: bytes, slide_files: list[str]) -> bytes:
    """Add Override entries for new slide files to [Content_Types].xml."""
    slide_ct = "application/vnd.openxmlformats-officedocument.presentationml.slide+xml"
    elements = []
    for slide_file in slide_files:
        part_name = f"/ppt/slides/{slide_file}"
        elements.append(
            f'<Override PartName="{part_name}" ContentType="{slide_ct}"/>'.encode(
                "utf-8"
            )
        )
    return _insert_before_closing_tag(ct_bytes, b"</Types>", elements)


def _remove_missing_content_type_overrides(root_dir: str) -> list[str]:
    """Remove [Content_Types].xml overrides for parts that do not exist."""
    ct_path = os.path.join(root_dir, "[Content_Types].xml")
    if not os.path.exists(ct_path):
        return []

    ct_bytes = Path(ct_path).read_bytes()
    removed: list[str] = []

    def keep_override(match: re.Match) -> bytes:
        part_m = re.search(rb'PartName="([^"]*)"', match.group(0))
        if not part_m:
            return match.group(0)
        part_name = part_m.group(1).decode("utf-8")
        part_path = os.path.join(root_dir, part_name.lstrip("/"))
        if os.path.exists(part_path):
            return match.group(0)
        removed.append(part_name)
        return b""

    new_bytes = re.sub(rb"<Override [^>]*?/>", keep_override, ct_bytes)
    if removed:
        Path(ct_path).write_bytes(new_bytes)
    return removed


def _rels_source_dir(root_dir: str, rels_path: str) -> str:
    """Return the package source directory that relative relationship targets use."""
    rels_rel = os.path.relpath(rels_path, root_dir).replace(os.sep, "/")
    if rels_rel == "_rels/.rels":
        return ""

    rels_dir = os.path.dirname(rels_rel)
    if os.path.basename(rels_dir) != "_rels":
        return os.path.dirname(rels_rel)
    return os.path.dirname(os.path.dirname(rels_rel))


def _resolve_internal_target(root_dir: str, rels_path: str, target: str) -> tuple[str, str]:
    """Resolve an internal relationship target to (package part name, filesystem path)."""
    if target.startswith("/"):
        part_name = os.path.normpath(target.lstrip("/")).replace(os.sep, "/")
    else:
        source_dir = _rels_source_dir(root_dir, rels_path)
        part_name = os.path.normpath(os.path.join(source_dir, target)).replace(os.sep, "/")
    return part_name, os.path.join(root_dir, part_name)


def _remove_dangling_relationships(root_dir: str) -> list[tuple[str, str, str, str]]:
    """Remove internal Relationship entries whose target part is missing.

    Returns tuples of (rels file, rId, target, resolved part name). PowerPoint repairs
    decks with dangling internal relationships; removing them avoids the repair prompt.
    """
    removed: list[tuple[str, str, str, str]] = []
    rel_pattern = rb"<Relationship [^>]*?/>"

    for rels_path in Path(root_dir).rglob("*.rels"):
        rels_bytes = rels_path.read_bytes()

        def keep_relationship(match: re.Match) -> bytes:
            entry = match.group(0)
            if b'TargetMode="External"' in entry:
                return entry
            target_m = re.search(rb'Target="([^"]*)"', entry)
            if not target_m:
                return entry
            target = target_m.group(1).decode("utf-8")
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                return entry
            part_name, part_path = _resolve_internal_target(
                root_dir, str(rels_path), target
            )
            if os.path.exists(part_path):
                return entry
            rid_m = re.search(rb'Id="([^"]*)"', entry)
            rid = rid_m.group(1).decode("utf-8") if rid_m else ""
            removed.append(
                (
                    os.path.relpath(rels_path, root_dir).replace(os.sep, "/"),
                    rid,
                    target,
                    part_name,
                )
            )
            return b""

        new_bytes = re.sub(rel_pattern, keep_relationship, rels_bytes)
        if new_bytes != rels_bytes:
            rels_path.write_bytes(new_bytes)

    return removed


def _assert_no_dangling_relationships(root_dir: str) -> None:
    """Fail if any internal Relationship target is still missing after repair."""
    dangling = _remove_dangling_relationships(root_dir)
    if dangling:
        details = "; ".join(
            f"{rels}:{rid}->{part}" for rels, rid, _target, part in dangling[:5]
        )
        raise RuntimeError(
            f"Unresolved dangling relationship(s) remained after repair: {details}"
        )


def repair_ooxml_package(root_dir: str) -> None:
    """Repair simple OOXML package integrity issues before packing the final PPTX."""
    removed_rels = _remove_dangling_relationships(root_dir)
    if removed_rels:
        print(f"  Repaired {len(removed_rels)} dangling relationship(s)")
        for rels_file, rid, target, part_name in removed_rels[:5]:
            print(f"    - {rels_file} {rid}: {target} -> missing {part_name}")

    removed_overrides = _remove_missing_content_type_overrides(root_dir)
    if removed_overrides:
        print(f"  Removed {len(removed_overrides)} stale content type override(s)")

    _assert_no_dangling_relationships(root_dir)


# ---------------------------------------------------------------------------
# File-level helpers
# ---------------------------------------------------------------------------


def unpack_pptx(pptx_path: str, dest_dir: str) -> None:
    """Extract PPTX zip to a directory."""
    with zipfile.ZipFile(pptx_path, "r") as zf:
        zf.extractall(dest_dir)


def pack_pptx(source_dir: str, out_path: str) -> None:
    """Repack a directory into a PPTX zip file."""
    tmp_path = out_path + ".tmp"
    with zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(source_dir):
            for f in files:
                file_path = os.path.join(root, f)
                arcname = os.path.relpath(file_path, source_dir)
                zf.write(file_path, arcname)
    shutil.move(tmp_path, out_path)


def get_slide_files(unpacked_dir: str) -> list[str]:
    """Get sorted list of slide XML filenames in ppt/slides/."""
    slides_dir = os.path.join(unpacked_dir, "ppt", "slides")
    if not os.path.exists(slides_dir):
        return []
    files = [f for f in os.listdir(slides_dir) if re.match(r"slide\d+\.xml", f)]
    files.sort(key=lambda x: int(re.search(r"\d+", x).group()))
    return files


def find_max_slide_number(unpacked_dir: str) -> int:
    """Find the highest slide number in the slides directory."""
    files = get_slide_files(unpacked_dir)
    if not files:
        return 0
    numbers = [int(re.search(r"\d+", f).group()) for f in files]
    return max(numbers)


def validate_merge_order(
    order: list[dict[str, Any]],
    structural_count: int,
    content_count: int,
) -> list[dict[str, Any]]:
    """Validate merge-order entries before mutating or writing the output deck.

    Legacy orders may omit slideId entirely. A mixed order is rejected because a
    partially stable identity is more dangerous than a clearly legacy one.
    """
    if not isinstance(order, list) or not order:
        raise ValueError("merge-order must be a non-empty JSON array")

    has_slide_id = ["slideId" in entry for entry in order if isinstance(entry, dict)]
    if any(has_slide_id) and not all(has_slide_id):
        raise ValueError("merge-order must either provide slideId for every entry or none")

    normalized: list[dict[str, Any]] = []
    seen_slide_ids: set[str] = set()
    for position, entry in enumerate(order):
        if not isinstance(entry, dict):
            raise ValueError(f"merge-order[{position}] must be an object")

        source = entry.get("source")
        if source not in {"structural", "content"}:
            raise ValueError(
                f"merge-order[{position}].source must be structural or content"
            )

        slide_idx = entry.get("slideIdx")
        if isinstance(slide_idx, bool) or not isinstance(slide_idx, int):
            raise ValueError(f"merge-order[{position}].slideIdx must be an integer")
        source_count = structural_count if source == "structural" else content_count
        if slide_idx < 0 or slide_idx >= source_count:
            raise ValueError(
                f"merge-order[{position}].slideIdx {slide_idx} is outside {source} "
                f"deck bounds (0..{source_count - 1})"
            )

        raw_slide_id = entry.get("slideId")
        if all(has_slide_id):
            if not isinstance(raw_slide_id, str) or not raw_slide_id.strip():
                raise ValueError(f"merge-order[{position}].slideId must be a non-empty string")
            slide_id = raw_slide_id.strip()
        else:
            # Compatibility identity for callers without explicit slide IDs. It
            # is based on final position so repeated source slides remain unique.
            slide_id = f"legacy-slide-{position + 1:02d}"

        if slide_id in seen_slide_ids:
            raise ValueError(f"Duplicate merge-order slideId: {slide_id}")
        seen_slide_ids.add(slide_id)
        normalized.append(
            {"source": source, "slideIdx": slide_idx, "slideId": slide_id}
        )

    return normalized


def write_json_atomic(path: str, payload: dict[str, Any]) -> None:
    """Write a UTF-8 JSON file with replace semantics."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(
        prefix=f".{target.name}.", suffix=".tmp", dir=str(target.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temp_path, target)
    except Exception:
        try:
            os.unlink(temp_path)
        except FileNotFoundError:
            pass
        raise


# ---------------------------------------------------------------------------
# Media / chart copy helpers (file-level only, no XML rewrite)
# ---------------------------------------------------------------------------


def copy_media_files(
    source_dir: str,
    dest_dir: str,
    media_refs: set[str],
    media_remap: dict[str, str],
) -> None:
    """Copy media files from source to dest, handling name collisions."""
    source_media = os.path.join(source_dir, "ppt", "media")
    dest_media = os.path.join(dest_dir, "ppt", "media")
    os.makedirs(dest_media, exist_ok=True)

    existing_media = set(os.listdir(dest_media)) if os.path.exists(dest_media) else set()

    for media_file in media_refs:
        source_path = os.path.join(source_media, media_file)
        if not os.path.exists(source_path):
            continue

        if media_file in existing_media:
            base, ext = os.path.splitext(media_file)
            counter = 1
            new_name = f"{base}_m{counter}{ext}"
            while new_name in existing_media:
                counter += 1
                new_name = f"{base}_m{counter}{ext}"
            media_remap[media_file] = new_name
            dest_path = os.path.join(dest_media, new_name)
        else:
            media_remap[media_file] = media_file
            dest_path = os.path.join(dest_media, media_file)

        shutil.copy2(source_path, dest_path)
        existing_media.add(os.path.basename(dest_path))


def copy_chart_files(
    source_dir: str,
    dest_dir: str,
    chart_refs: set[str],
    chart_remap: dict[str, str],
) -> None:
    """Copy chart XML files from source to dest, handling name collisions."""
    source_charts = os.path.join(source_dir, "ppt", "charts")
    dest_charts = os.path.join(dest_dir, "ppt", "charts")

    if not os.path.exists(source_charts):
        return

    os.makedirs(dest_charts, exist_ok=True)
    existing_charts = set(os.listdir(dest_charts)) if os.path.exists(dest_charts) else set()

    for chart_file in chart_refs:
        source_path = os.path.join(source_charts, chart_file)
        if not os.path.exists(source_path):
            continue

        if chart_file in existing_charts:
            base, ext = os.path.splitext(chart_file)
            counter = 1
            new_name = f"{base}_m{counter}{ext}"
            while new_name in existing_charts:
                counter += 1
                new_name = f"{base}_m{counter}{ext}"
            chart_remap[chart_file] = new_name
        else:
            chart_remap[chart_file] = chart_file

        dest_path = os.path.join(dest_charts, chart_remap[chart_file])
        shutil.copy2(source_path, dest_path)
        existing_charts.add(chart_remap[chart_file])

        source_chart_rels = os.path.join(source_charts, "_rels", f"{chart_file}.rels")
        if os.path.exists(source_chart_rels):
            dest_chart_rels_dir = os.path.join(dest_charts, "_rels")
            os.makedirs(dest_chart_rels_dir, exist_ok=True)
            dest_chart_rels = os.path.join(
                dest_chart_rels_dir, f"{chart_remap[chart_file]}.rels"
            )
            shutil.copy2(source_chart_rels, dest_chart_rels)


# ---------------------------------------------------------------------------
# SlideLayout detection
# ---------------------------------------------------------------------------


def find_blank_layout(structural_dir: str) -> str:
    """Find a blank slideLayout in the structural deck.

    Scans ppt/slideLayouts/ for one with type="blank".
    Falls back to the first available layout if no blank is found.
    Returns the relative path like "../slideLayouts/slideLayout7.xml".
    """
    layouts_dir = os.path.join(structural_dir, "ppt", "slideLayouts")
    if not os.path.exists(layouts_dir):
        return "../slideLayouts/slideLayout1.xml"

    layout_files = sorted(
        [f for f in os.listdir(layouts_dir) if re.match(r"slideLayout\d+\.xml", f)],
        key=lambda x: int(re.search(r"\d+", x).group()),
    )
    if not layout_files:
        return "../slideLayouts/slideLayout1.xml"

    # Prefer a layout with type="blank"
    for lf in layout_files:
        content = Path(os.path.join(layouts_dir, lf)).read_bytes()
        if re.search(rb'type="blank"', content):
            return f"../slideLayouts/{lf}"

    # Fallback: use the first layout
    return f"../slideLayouts/{layout_files[0]}"


# ---------------------------------------------------------------------------
# Slide import
# ---------------------------------------------------------------------------


def import_content_slide(
    content_dir: str,
    structural_dir: str,
    content_slide_filename: str,
    new_slide_number: int,
    blank_layout_target: str,
    dependent_policy: str = "drop-notes",
) -> str:
    """Import a single content slide into the structural deck.

    Copies slide XML, its rels, and associated media/charts.
    Remaps media/chart targets in the rels if files were renamed.
    Re-points slideLayout relationship to blank_layout_target from the structural deck.
    Returns the new slide filename.
    """
    new_slide_filename = f"slide{new_slide_number}.xml"

    # Copy slide XML
    src_slide = os.path.join(content_dir, "ppt", "slides", content_slide_filename)
    dst_slide = os.path.join(structural_dir, "ppt", "slides", new_slide_filename)
    shutil.copy2(src_slide, dst_slide)

    # Process slide rels
    src_rels_dir = os.path.join(content_dir, "ppt", "slides", "_rels")
    dst_rels_dir = os.path.join(structural_dir, "ppt", "slides", "_rels")
    os.makedirs(dst_rels_dir, exist_ok=True)

    src_rels_path = os.path.join(src_rels_dir, f"{content_slide_filename}.rels")
    dst_rels_path = os.path.join(dst_rels_dir, f"{new_slide_filename}.rels")

    if os.path.exists(src_rels_path):
        rels_bytes = Path(src_rels_path).read_bytes()

        if dependent_policy == "drop-notes":
            rels_bytes = _drop_notes_relationships(rels_bytes)
        else:
            raise ValueError(f"Unsupported dependent part policy: {dependent_policy}")

        # Find media and chart references (relative ../X/ and absolute /ppt/X/)
        media_refs: set[str] = set()
        chart_refs: set[str] = set()
        for m in re.finditer(rb'Target="([^"]*)"', rels_bytes):
            target = m.group(1).decode("utf-8")
            if "../media/" in target or "/ppt/media/" in target:
                media_refs.add(os.path.basename(target))
            elif "../charts/" in target or "/ppt/charts/" in target:
                chart_refs.add(os.path.basename(target))

        # Copy media and charts
        media_remap: dict[str, str] = {}
        chart_remap: dict[str, str] = {}
        if media_refs:
            copy_media_files(content_dir, structural_dir, media_refs, media_remap)
        if chart_refs:
            copy_chart_files(content_dir, structural_dir, chart_refs, chart_remap)

        # Update rels targets: rename collisions + normalize absolute to relative
        for old_name, new_name in media_remap.items():
            for prefix in (f"../media/{old_name}", f"/ppt/media/{old_name}"):
                rels_bytes = rels_bytes.replace(
                    prefix.encode(), f"../media/{new_name}".encode()
                )
        for old_name, new_name in chart_remap.items():
            for prefix in (f"../charts/{old_name}", f"/ppt/charts/{old_name}"):
                rels_bytes = rels_bytes.replace(
                    prefix.encode(), f"../charts/{new_name}".encode()
                )

        # Re-point slideLayout relationship to the structural deck's blank layout
        rels_bytes = re.sub(
            rb'(<Relationship [^>]*?Target=")[^"]*slideLayout[^"]*("[^/]*/>)',
            rb"\1" + blank_layout_target.encode() + rb"\2",
            rels_bytes,
        )
        # If no slideLayout relationship existed, add one
        if b"slideLayout" not in rels_bytes:
            layout_rel_type = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout"
            # Find next available rId
            max_local_rid = _find_max_rid_in_bytes(rels_bytes)
            new_local_rid = f"rId{max_local_rid + 1}"
            layout_entry = (
                f'<Relationship Id="{new_local_rid}" '
                f'Type="{layout_rel_type}" '
                f'Target="{blank_layout_target}"/>'.encode("utf-8")
            )
            rels_bytes = _insert_before_closing_tag(
                rels_bytes, b"</Relationships>", [layout_entry]
            )

        Path(dst_rels_path).write_bytes(rels_bytes)
    else:
        # No rels file — create a minimal empty one
        Path(dst_rels_path).write_bytes(
            b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>'
        )

    return new_slide_filename


# ---------------------------------------------------------------------------
# Orphan cleanup
# ---------------------------------------------------------------------------


def _remove_dependent_parts(
    structural_dir: str, slides_dir: str, rels_path: str
) -> list[str]:
    """Parse a slide .rels and delete non-shared dependent parts (notesSlides, tags, comments).

    Returns list of removed part names (e.g. "/ppt/notesSlides/notesSlide1.xml")
    for Content_Types cleanup.
    """
    removed_parts: list[str] = []
    if not os.path.exists(rels_path):
        return removed_parts

    rels_content = Path(rels_path).read_bytes()
    dep_dirs = ("notesSlides", "tags", "comments")

    for target_match in re.finditer(rb'Target="([^"]*)"', rels_content):
        target = target_match.group(1).decode("utf-8")
        if not any(d in target for d in dep_dirs):
            continue
        dep_path = os.path.normpath(os.path.join(slides_dir, target))
        if os.path.exists(dep_path):
            os.remove(dep_path)
            rel_from_ppt = os.path.relpath(dep_path, os.path.join(structural_dir, "ppt"))
            removed_parts.append(f"/ppt/{rel_from_ppt}")
            dep_rels = os.path.join(
                os.path.dirname(dep_path), "_rels",
                os.path.basename(dep_path) + ".rels",
            )
            if os.path.exists(dep_rels):
                os.remove(dep_rels)

    return removed_parts


def remove_orphan_slides(structural_dir: str, used_slides: set[str]) -> tuple[list[str], list[str]]:
    """Delete slide files (and their rels) that are not in the used set.

    Also recursively removes dependent parts (notesSlides, tags, comments)
    that are exclusively owned by the orphan slide.

    Returns (removed_slide_filenames, removed_dependent_part_names).
    """
    slides_dir = os.path.join(structural_dir, "ppt", "slides")
    rels_dir = os.path.join(slides_dir, "_rels")
    removed = []
    removed_deps: list[str] = []

    for f in os.listdir(slides_dir):
        if re.match(r"slide\d+\.xml", f) and f not in used_slides:
            rels_path = os.path.join(rels_dir, f"{f}.rels")
            removed_deps.extend(
                _remove_dependent_parts(structural_dir, slides_dir, rels_path)
            )
            if os.path.exists(rels_path):
                os.remove(rels_path)
            os.remove(os.path.join(slides_dir, f))
            removed.append(f)

    return removed, removed_deps


# ---------------------------------------------------------------------------
# Main merge logic
# ---------------------------------------------------------------------------


def merge(
    structural_path: str,
    content_path: str,
    order: list[dict[str, Any]],
    out_path: str,
    manifest_out: str | None = None,
    dependent_policy: str = "drop-notes",
) -> None:
    """Main merge logic."""
    with tempfile.TemporaryDirectory() as tmp:
        structural_dir = os.path.join(tmp, "structural")
        content_dir = os.path.join(tmp, "content")

        unpack_pptx(structural_path, structural_dir)
        unpack_pptx(content_path, content_dir)

        structural_slides = get_slide_files(structural_dir)
        content_slides = get_slide_files(content_dir)

        print(f"  Structural slides: {len(structural_slides)}")
        print(f"  Content slides: {len(content_slides)}")

        normalized_order = validate_merge_order(
            order, len(structural_slides), len(content_slides)
        )

        # Detect blank layout for imported content slides
        blank_layout_target = find_blank_layout(structural_dir)
        print(f"  Blank layout target: {blank_layout_target}")

        # --- Import content slides into structural deck ---
        next_slide_num = find_max_slide_number(structural_dir) + 1
        content_idx_to_new_filename: dict[int, str] = {}

        for entry in normalized_order:
            if entry["source"] == "content":
                cidx = entry["slideIdx"]
                if cidx in content_idx_to_new_filename:
                    continue
                new_filename = import_content_slide(
                    content_dir,
                    structural_dir,
                    content_slides[cidx],
                    next_slide_num,
                    blank_layout_target,
                    dependent_policy,
                )
                content_idx_to_new_filename[cidx] = new_filename
                next_slide_num += 1
                print(f"  Imported content slide {cidx} -> {new_filename}")

        # --- Build final slide order ---
        final_slide_order: list[str] = []
        final_manifest_entries: list[dict[str, Any]] = []
        for entry in normalized_order:
            if entry["source"] == "structural":
                sidx = entry["slideIdx"]
                slide_file = structural_slides[sidx]
            elif entry["source"] == "content":
                cidx = entry["slideIdx"]
                slide_file = content_idx_to_new_filename[cidx]
            final_slide_order.append(slide_file)
            final_manifest_entries.append(
                {
                    "slideNumber": len(final_slide_order),
                    "slideId": entry["slideId"],
                    "source": entry["source"],
                    "sourceSlideIdx": entry["slideIdx"],
                    "slideFile": slide_file,
                }
            )

        print(f"  Final slide count: {len(final_slide_order)}")
        used_slides = set(final_slide_order)

        # --- Fix 2: Remove orphan slide files ---
        removed, removed_deps = remove_orphan_slides(structural_dir, used_slides)
        if removed:
            print(f"  Removed {len(removed)} orphan slide file(s)")
        if removed_deps:
            print(f"  Removed {len(removed_deps)} orphan dependent part(s)")

        # --- Fix 3: Clean presentation.xml.rels (remove unused slide rels) ---
        pres_rels_path = os.path.join(
            structural_dir, "ppt", "_rels", "presentation.xml.rels"
        )
        pres_rels_bytes = Path(pres_rels_path).read_bytes()
        pres_rels_bytes = _filter_rels_keep(pres_rels_bytes, used_slides)

        # Add rels for new content slides
        max_rid = _find_max_rid_in_bytes(pres_rels_bytes)
        slide_type = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"
        new_rels_entries: list[tuple[str, str, str]] = []

        # Build a map of existing filename->rId from the (now filtered) rels
        existing_filename_to_rid: dict[str, str] = {}
        for m in re.finditer(
            rb'Id="(rId\d+)"[^>]*Target="slides/([^"]+)"', pres_rels_bytes
        ):
            rid = m.group(1).decode()
            fname = m.group(2).decode()
            existing_filename_to_rid[fname] = rid

        filename_to_rid: dict[str, str] = dict(existing_filename_to_rid)
        for slide_file in final_slide_order:
            if slide_file not in filename_to_rid:
                max_rid += 1
                new_rid = f"rId{max_rid}"
                new_rels_entries.append((new_rid, slide_type, f"slides/{slide_file}"))
                filename_to_rid[slide_file] = new_rid

        if new_rels_entries:
            pres_rels_bytes = _add_rels_entries(pres_rels_bytes, new_rels_entries)

        Path(pres_rels_path).write_bytes(pres_rels_bytes)

        # --- Fix 1 & 4: Rewrite sldIdLst in presentation.xml ---
        pres_path = os.path.join(structural_dir, "ppt", "presentation.xml")
        pres_bytes = Path(pres_path).read_bytes()

        # Fix 4: find max existing sldId to avoid conflicts
        base_id = _find_max_sld_id(pres_bytes) + 1

        sld_id_entries: list[tuple[int, str]] = []
        for i, slide_file in enumerate(final_slide_order):
            rid = filename_to_rid[slide_file]
            sld_id_entries.append((base_id + i, rid))

        pres_bytes = _replace_sld_id_lst(pres_bytes, sld_id_entries)
        Path(pres_path).write_bytes(pres_bytes)

        # --- Fix 2 (cont): Clean Content_Types for removed slides ---
        ct_path = os.path.join(structural_dir, "[Content_Types].xml")
        ct_bytes = Path(ct_path).read_bytes()

        # Remove overrides for orphan slides and their dependent parts
        if removed:
            ct_bytes = _remove_content_types_for_slides(ct_bytes, set(removed), removed_deps)

        # Add overrides for new content slides
        new_slide_files = list(content_idx_to_new_filename.values())
        if new_slide_files:
            ct_bytes = _add_content_types_for_slides(ct_bytes, new_slide_files)

        Path(ct_path).write_bytes(ct_bytes)

        # --- Final package integrity repair ---
        repair_ooxml_package(structural_dir)

        # --- Pack final output ---
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        pack_pptx(structural_dir, out_path)
        print(f"  Merged output: {out_path}")

        if manifest_out:
            write_json_atomic(
                manifest_out,
                {
                    "schema": "mavis.ppt_merge_manifest.v1",
                    "artifact": {"fileName": os.path.basename(out_path)},
                    "slides": final_manifest_entries,
                },
            )
            print(f"  Merge manifest: {manifest_out}")


def main():
    parser = argparse.ArgumentParser(description="Merge structural and content PPTX decks")
    parser.add_argument("--structural", required=True, help="Path to structural-base.pptx")
    parser.add_argument("--content", required=True, help="Path to content-only.pptx")
    parser.add_argument("--order", required=True, help="Path to merge-order.json")
    parser.add_argument("--out", required=True, help="Output path for merged final.pptx")
    parser.add_argument(
        "--manifest-out",
        help="Optional output path for mavis.ppt_merge_manifest.v1 JSON",
    )
    parser.add_argument(
        "--dependent-policy",
        choices=["drop-notes"],
        default="drop-notes",
        help="Policy for imported slide-owned parts; notes are regenerated after assembly",
    )
    args = parser.parse_args()

    with open(args.order, "r", encoding="utf-8") as f:
        order = json.load(f)

    print(f"merge_decks: {args.structural} + {args.content}")
    merge(
        args.structural,
        args.content,
        order,
        args.out,
        args.manifest_out,
        args.dependent_policy,
    )
    print("Done.")


if __name__ == "__main__":
    main()
