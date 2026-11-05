#!/usr/bin/env python3
"""structural_fill.py — Clone structural slides from a template and fill text slots.

Usage:
    uv run --with python-pptx structural_fill.py template.pptx \
        --classification slides/template-classification.json \
        --content slides/structural-fill-content.json \
        --out slides/output/structural-base.pptx

Workflow:
1. Open template PPTX.
2. Read classification to identify structural vs content-example slides.
3. Clone section-divider slides to match the required count.
4. Delete all content-example slides.
5. Fill structural slide text slots using run-level replacement (preserves formatting).
6. Clean orphan media files.
7. Save output.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from lxml import etree
from pptx import Presentation
from pptx.opc.constants import RELATIONSHIP_TYPE as RT


NSMAP = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}


def find_shape_by_name(slide, shape_name: str):
    """Find a shape on the slide by its name attribute."""
    for shape in slide.shapes:
        if shape.name == shape_name:
            return shape
    return None


def fill_shape_text(shape, new_text: str) -> None:
    """Replace shape text content while preserving the first run's formatting.

    Strategy: keep the first paragraph's first run (with all its rPr formatting),
    set its text to new_text, and remove all subsequent runs and paragraphs.
    """
    if not shape.has_text_frame:
        return

    tf = shape.text_frame
    paragraphs = tf.paragraphs

    if not paragraphs:
        return

    first_para = paragraphs[0]
    p_elem = first_para._p
    ns_a = NSMAP["a"]

    runs = list(p_elem.findall(f"{{{ns_a}}}r"))
    if not runs:
        # No runs — create one preserving paragraph properties
        r_elem = etree.SubElement(p_elem, f"{{{ns_a}}}r")
        t_elem = etree.SubElement(r_elem, f"{{{ns_a}}}t")
        t_elem.text = new_text
        return

    # Keep first run, set text
    first_r = runs[0]
    t_elem = first_r.find(f"{{{ns_a}}}t")
    if t_elem is None:
        t_elem = etree.SubElement(first_r, f"{{{ns_a}}}t")
    t_elem.text = new_text

    # Remove extra runs in first paragraph
    for r in runs[1:]:
        p_elem.remove(r)

    # Remove line breaks in first paragraph
    for br in list(p_elem.findall(f"{{{ns_a}}}br")):
        p_elem.remove(br)

    # Remove all subsequent paragraphs
    txBody = p_elem.getparent()
    all_paras = list(txBody.findall(f"{{{ns_a}}}p"))
    for para in all_paras[1:]:
        txBody.remove(para)


def clone_slide(prs, source_slide_idx: int) -> int:
    """Clone a slide by index and append it. Returns the new slide index."""
    source_slide = prs.slides[source_slide_idx]
    slide_layout = source_slide.slide_layout

    # Add a blank slide with the same layout
    new_slide = prs.slides.add_slide(slide_layout)
    new_slide_idx = len(prs.slides) - 1

    # Replace default placeholder shapes with the complete source spTree.
    spTree = new_slide.shapes._spTree
    for child in list(spTree):
        spTree.remove(child)
    for child in prs.slides[source_slide_idx].shapes._spTree:
        spTree.append(copy.deepcopy(child))

    # Copy slide background if set
    source_bg = source_slide._element.find(f"{{{NSMAP['p']}}}cSld/{{{NSMAP['p']}}}bg")
    if source_bg is not None:
        cSld = new_slide._element.find(f"{{{NSMAP['p']}}}cSld")
        existing_bg = cSld.find(f"{{{NSMAP['p']}}}bg")
        if existing_bg is not None:
            cSld.remove(existing_bg)
        cSld.insert(0, copy.deepcopy(source_bg))

    # Copy relationships (images, charts, etc.) from the source slide part.
    # Notes are copied as text into a new notes part so the two slides never share
    # ownership of one notesSlide.
    source_part = source_slide.part
    new_part = new_slide.part
    for rel in source_part.rels.values():
        if rel.reltype == RT.NOTES_SLIDE:
            continue
        if rel.is_external:
            new_part.rels.get_or_add_ext_rel(rel.reltype, rel.target_ref)
        else:
            # For internal targets (images, charts), relate to the same target part
            try:
                new_part.relate_to(rel.target_part, rel.reltype)
            except Exception:
                continue  # Relationship may already exist

    if source_slide.has_notes_slide:
        new_slide.notes_slide.notes_text_frame.text = (
            source_slide.notes_slide.notes_text_frame.text or ""
        )

    return new_slide_idx


def delete_slide(prs, slide_idx: int) -> None:
    """Delete a slide by its current index."""
    rId = prs.slides._sldIdLst[slide_idx].get(
        f"{{{NSMAP['r']}}}id"
    )
    # Remove from sldIdLst
    sldId_elem = prs.slides._sldIdLst[slide_idx]
    prs.slides._sldIdLst.remove(sldId_elem)

    # Remove the relationship
    if rId:
        prs.part.drop_rel(rId)


def delete_slides_by_indices(prs, indices: list[int]) -> None:
    """Delete slides by their original indices (handles index shifting)."""
    # Sort descending to avoid index shift issues
    for idx in sorted(indices, reverse=True):
        if idx < len(prs.slides):
            delete_slide(prs, idx)


def collect_media_references(prs) -> set[str]:
    """Collect all media file paths referenced by remaining slides."""
    media_refs = set()
    for slide in prs.slides:
        for rel in slide.part.rels.values():
            if not rel.is_external and hasattr(rel, "target_partname"):
                partname = str(rel.target_partname)
                if "/media/" in partname:
                    media_refs.add(partname)
    # Also check slide masters and layouts
    for master in prs.slide_masters:
        for rel in master.part.rels.values():
            if not rel.is_external and hasattr(rel, "target_partname"):
                partname = str(rel.target_partname)
                if "/media/" in partname:
                    media_refs.add(partname)
        for layout in master.slide_layouts:
            for rel in layout.part.rels.values():
                if not rel.is_external and hasattr(rel, "target_partname"):
                    partname = str(rel.target_partname)
                    if "/media/" in partname:
                        media_refs.add(partname)
    return media_refs


def clean_orphan_media(pptx_path: str) -> None:
    """Remove media files not referenced by any slide, master, or layout.

    Operates on the PPTX as a zip file (post-save cleanup pass).
    """
    import shutil

    # Read all entries
    with zipfile.ZipFile(pptx_path, "r") as zf:
        all_entries = zf.namelist()

    # Find media files
    media_files = [e for e in all_entries if e.startswith("ppt/media/")]
    if not media_files:
        return

    # Find all rels files and collect referenced media
    referenced_media = set()
    with zipfile.ZipFile(pptx_path, "r") as zf:
        rels_files = [e for e in all_entries if e.endswith(".rels")]
        for rels_file in rels_files:
            content = zf.read(rels_file).decode("utf-8")
            for media in media_files:
                # Check if the media filename appears in any rels
                media_filename = os.path.basename(media)
                if media_filename in content:
                    referenced_media.add(media)

    orphans = set(media_files) - referenced_media
    if not orphans:
        return

    # Rebuild zip without orphans
    tmp_path = pptx_path + ".tmp"
    with zipfile.ZipFile(pptx_path, "r") as zf_in:
        with zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zf_out:
            for item in zf_in.namelist():
                if item not in orphans:
                    zf_out.writestr(item, zf_in.read(item))

    shutil.move(tmp_path, pptx_path)
    print(f"  Cleaned {len(orphans)} orphan media file(s)")


def _write_json_atomic(path: str, payload: dict[str, Any]) -> None:
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


def _default_slide_id(slide_type: str, ordinal: int) -> str:
    if slide_type in {"cover", "toc", "ending"} and ordinal == 1:
        return slide_type
    return f"{slide_type}-{ordinal}"


def _shape_kind(shape) -> str:
    if getattr(shape, "has_chart", False):
        return "chart"
    if getattr(shape, "has_text_frame", False):
        return "text"
    return "shape"


def _build_structural_artifacts(
    prs,
    records_by_part: dict[int, dict[str, Any]],
    out_path: str,
) -> dict[str, Any]:
    """Build the structural element map from the final slide order."""
    width_in = prs.slide_width / 914400
    height_in = prs.slide_height / 914400
    map_slides: list[dict[str, Any]] = []
    seen_element_ids: set[str] = set()

    for slide_number, slide in enumerate(prs.slides, start=1):
        record = records_by_part.get(id(slide.part))
        if record is None:
            raise ValueError(
                f"No structural identity record for final slide {slide_number}"
            )
        slide_id = record["slideId"]
        elements: list[dict[str, Any]] = []
        for slot in record["entry"].get("fillSlots", []):
            shape_name = slot["shapeName"]
            shape = find_shape_by_name(slide, shape_name)
            if shape is None:
                print(
                    f"  WARNING: shape '{shape_name}' missing while building structural map"
                )
                continue
            element_id = slot.get("elementId") or f"{slide_id}.{slot['role']}"
            if element_id in seen_element_ids:
                raise ValueError(f"Duplicate structural elementId: {element_id}")
            seen_element_ids.add(element_id)
            x = round(shape.left / 914400, 4)
            y = round(shape.top / 914400, 4)
            w = round(shape.width / 914400, 4)
            h = round(shape.height / 914400, 4)
            elements.append(
                {
                    "elementId": element_id,
                    "kind": _shape_kind(shape),
                    "role": slot.get("role"),
                    "sourceName": shape_name,
                    "pptShapeId": shape.shape_id,
                    "rectIn": {"x": x, "y": y, "w": w, "h": h},
                    "normalizedRect": {
                        "x": round(x / width_in, 4),
                        "y": round(y / height_in, 4),
                        "w": round(w / width_in, 4),
                        "h": round(h / height_in, 4),
                    },
                }
            )
        map_slides.append(
            {
                "slideNumber": slide_number,
                "slideId": slide_id,
                "pageType": record["entry"].get("type"),
                "sourceSlideIdx": record["sourceSlideIdx"],
                "elements": elements,
            }
        )
    element_map = {
        "schema": "mavis.ppt_element_map.v1",
        "artifact": {
            "fileName": Path(out_path).name,
            "filePath": out_path,
            "generator": "structural_fill.py",
        },
        "layout": {
            "name": "TEMPLATE",
            "widthIn": round(width_in, 4),
            "heightIn": round(height_in, 4),
        },
        "slides": map_slides,
    }
    return element_map


def process(
    template_path: str,
    classification: dict[str, Any],
    content: dict[str, Any],
    out_path: str,
    element_map_out: str | None = None,
) -> None:
    """Main processing logic.

    Order of operations:
    1. Fill text on structural slides (indices still valid from original template)
    2. Delete content example slides (reverse order to avoid index shift)
    3. Clone section-dividers if we need more than what the template provides
    4. Fill text on cloned dividers
    5. Save + clean orphan media
    """
    prs = Presentation(template_path)

    structural = classification["structural"]
    content_examples = classification["contentExamples"]

    # Bind stable slide identity to the underlying slide part so index changes
    # caused by deletion/cloning cannot break the final element map.
    records_by_part: dict[int, dict[str, Any]] = {}
    type_counts: dict[str, int] = {}
    seen_slide_ids: set[str] = set()
    divider_ordinal = 0
    for entry in structural:
        slide_type = entry["type"]
        type_counts[slide_type] = type_counts.get(slide_type, 0) + 1
        ordinal = type_counts[slide_type]
        content_slide_id = None
        if slide_type == "section-divider":
            if divider_ordinal < len(content.get("sectionDividers", [])):
                content_slide_id = content["sectionDividers"][divider_ordinal].get(
                    "slideId"
                )
            divider_ordinal += 1
        slide_id = (
            entry.get("slideId")
            or content_slide_id
            or _default_slide_id(slide_type, ordinal)
        )
        if slide_id in seen_slide_ids:
            raise ValueError(f"Duplicate structural slideId: {slide_id}")
        seen_slide_ids.add(slide_id)
        source_slide = prs.slides[entry["idx"]]
        records_by_part[id(source_slide.part)] = {
            "slideId": slide_id,
            "sourceSlideIdx": entry["idx"],
            "entry": entry,
        }

    # --- Phase 1: Fill structural slide text (original indices are valid) ---

    # Fill cover
    if "cover" in content:
        cover_entries = [s for s in structural if s["type"] == "cover"]
        for entry in cover_entries:
            slide = prs.slides[entry["idx"]]
            for slot in entry.get("fillSlots", []):
                shape = find_shape_by_name(slide, slot["shapeName"])
                if shape is None:
                    print(f"  WARNING: shape '{slot['shapeName']}' not found on slide {entry['idx']}")
                    continue
                text_value = content["cover"].get(slot["role"], "")
                if text_value:
                    fill_shape_text(shape, text_value)
                    print(f"  Filled cover.{slot['role']} = '{text_value[:30]}...'")

    # Fill TOC
    if "toc" in content:
        toc_entries = [s for s in structural if s["type"] == "toc"]
        toc_items = content["toc"].get("items", [])
        for entry in toc_entries:
            slide = prs.slides[entry["idx"]]
            for slot in entry.get("fillSlots", []):
                shape = find_shape_by_name(slide, slot["shapeName"])
                if shape is None:
                    continue
                role = slot["role"]
                if role.startswith("item"):
                    item_idx = int(role.replace("item", "")) - 1
                    if item_idx < len(toc_items):
                        fill_shape_text(shape, toc_items[item_idx])
                        print(f"  Filled toc.{role} = '{toc_items[item_idx]}'")

    # Fill existing section dividers
    divider_entries = [s for s in structural if s["type"] == "section-divider"]
    section_dividers_content = content.get("sectionDividers", [])

    for i, entry in enumerate(divider_entries):
        if i >= len(section_dividers_content):
            break
        div_content = section_dividers_content[i]
        slide = prs.slides[entry["idx"]]
        for slot in entry.get("fillSlots", []):
            shape = find_shape_by_name(slide, slot["shapeName"])
            if shape is None:
                continue
            role = slot["role"]
            text_value = div_content.get(role, "")
            if text_value:
                fill_shape_text(shape, text_value)
                print(f"  Filled divider[{i}].{role} = '{text_value}'")

    # --- Phase 2: Delete content example slides ---
    delete_slides_by_indices(prs, content_examples)
    print(f"  Deleted {len(content_examples)} content example slide(s)")

    # --- Phase 3: Clone section-dividers if more are needed ---
    dividers_needed = len(section_dividers_content)
    dividers_available = len(divider_entries)

    if dividers_needed > dividers_available and dividers_available > 0:
        # After deletion, the first divider's position has shifted.
        # Find it by iterating remaining slides and matching the shape name.
        first_divider_slots = divider_entries[0].get("fillSlots", [])
        source_divider_idx = _find_divider_slide_idx(prs, first_divider_slots)

        if source_divider_idx is not None:
            for j in range(dividers_available, dividers_needed):
                new_idx = clone_slide(prs, source_divider_idx)
                print(f"  Cloned section-divider -> slide {new_idx}")
                # Fill the cloned divider
                div_content = section_dividers_content[j]
                cloned_slide = prs.slides[new_idx]
                source_record = records_by_part[id(prs.slides[source_divider_idx].part)]
                clone_slide_id = div_content.get("slideId") or f"section-divider-{j + 1}"
                if clone_slide_id in seen_slide_ids:
                    raise ValueError(f"Duplicate structural slideId: {clone_slide_id}")
                seen_slide_ids.add(clone_slide_id)
                clone_entry = copy.deepcopy(source_record["entry"])
                clone_entry["slideId"] = clone_slide_id
                for clone_slot in clone_entry.get("fillSlots", []):
                    clone_slot["elementId"] = (
                        f"{clone_slide_id}.{clone_slot['role']}"
                    )
                records_by_part[id(cloned_slide.part)] = {
                    "slideId": clone_slide_id,
                    "sourceSlideIdx": source_record["sourceSlideIdx"],
                    "entry": clone_entry,
                }
                for slot in first_divider_slots:
                    shape = find_shape_by_name(cloned_slide, slot["shapeName"])
                    if shape is None:
                        continue
                    role = slot["role"]
                    text_value = div_content.get(role, "")
                    if text_value:
                        fill_shape_text(shape, text_value)
                        print(f"  Filled divider[{j}].{role} = '{text_value}'")

    # --- Phase 4: Save ---
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    prs.save(out_path)
    print(f"  Saved structural base: {out_path}")

    # --- Phase 5: Clean orphan media ---
    clean_orphan_media(out_path)

    if element_map_out:
        element_map = _build_structural_artifacts(prs, records_by_part, out_path)
        _write_json_atomic(element_map_out, element_map)
        print(f"  Structural element map: {element_map_out}")


def _find_divider_slide_idx(prs, fill_slots: list[dict]) -> int | None:
    """Find a section-divider slide by matching its expected shape names."""
    if not fill_slots:
        return None
    target_names = {slot["shapeName"] for slot in fill_slots}
    for i, slide in enumerate(prs.slides):
        slide_names = {shape.name for shape in slide.shapes}
        if target_names.issubset(slide_names):
            return i
    return None


def main():
    parser = argparse.ArgumentParser(description="Clone and fill structural slides from a PPTX template")
    parser.add_argument("template", help="Path to the template PPTX file")
    parser.add_argument("--classification", required=True, help="Path to template-classification.json")
    parser.add_argument("--content", required=True, help="Path to structural-fill-content.json")
    parser.add_argument("--out", required=True, help="Output path for structural-base.pptx")
    parser.add_argument(
        "--element-map-out",
        help="Optional mavis.ppt_element_map.v1 output for structural slides",
    )
    args = parser.parse_args()

    with open(args.classification, "r", encoding="utf-8") as f:
        classification = json.load(f)

    with open(args.content, "r", encoding="utf-8") as f:
        content = json.load(f)

    print(f"structural_fill: {args.template}")
    print(f"  Structural slides: {len(classification['structural'])}")
    print(f"  Content examples to remove: {len(classification['contentExamples'])}")

    process(
        args.template,
        classification,
        content,
        args.out,
        args.element_map_out,
    )
    print("Done.")


if __name__ == "__main__":
    main()
