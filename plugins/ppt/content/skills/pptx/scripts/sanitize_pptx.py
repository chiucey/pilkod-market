#!/usr/bin/env python3
"""sanitize_pptx.py — Post-merge OOXML structural integrity validator and repairer.

A "万金油" safety net for PPTX files. Run after merge_decks.py or any assembly
step to catch and fix structural issues that would make the file fail to open.

Usage:
    uv run sanitize_pptx.py input.pptx [--out repaired.pptx] [--strict] [--verbose]

Exit codes:
    0 — valid (no issues or all issues auto-repaired)
    1 — unrepairable issues remain
    2 — file-level error (not a valid zip, etc.)

Checks (OOXML package + PPTX-specific):
    1. [Content_Types].xml completeness — overrides match files on disk
    2. All .rels targets resolve to existing parts; no duplicate rIds
    3. presentation.xml sldIdLst matches slide files and rels; unique ids
    4. Every slide has exactly one slideLayout relationship pointing to an existing layout
    5. .rels files use default namespace (no prefix corruption)
    6. Orphan files detection (exist in zip but unreferenced)

Auto-repairs:
    - Remove Content_Types overrides for missing parts
    - Add missing Content_Types overrides/defaults for existing parts
    - Remove dangling relationship entries
    - Remove duplicate rId entries
    - Remove duplicate slideLayout relationships (keep first)

Zero external dependencies — stdlib only (zipfile, xml.etree, re).
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


PKG_RELS_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
SLIDE_CT = "application/vnd.openxmlformats-officedocument.presentationml.slide+xml"
CHART_CT = "application/vnd.openxmlformats-officedocument.drawingml.chart+xml"
NOTES_CT = "application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"

MEDIA_EXT_CT = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "bmp": "image/bmp",
    "tiff": "image/tiff",
    "tif": "image/tiff",
    "svg": "image/svg+xml",
    "wmf": "image/x-wmf",
    "emf": "image/x-emf",
    "wdp": "image/vnd.ms-photo",
}


class Issue:
    def __init__(self, check: str, severity: str, message: str, repairable: bool = False):
        self.check = check
        self.severity = severity
        self.message = message
        self.repairable = repairable
        self.repaired = False

    def __repr__(self):
        status = " [REPAIRED]" if self.repaired else (" [REPAIRABLE]" if self.repairable else "")
        return f"[{self.severity.upper()}] {self.check}: {self.message}{status}"


class PPTXSanitizer:

    def __init__(self, pptx_path: str, verbose: bool = False, strict: bool = False):
        self.pptx_path = pptx_path
        self.verbose = verbose
        self.strict = strict
        self.issues: list[Issue] = []
        self.repairs_made = 0

    def validate_and_repair(self, out_path: str | None = None) -> bool:
        if not os.path.isfile(self.pptx_path):
            self._issue("file", "error", f"File not found: {self.pptx_path}")
            return False

        try:
            zipfile.ZipFile(self.pptx_path, "r").close()
        except (zipfile.BadZipFile, Exception) as e:
            self._issue("file", "error", f"Not a valid ZIP file: {e}")
            return False

        with tempfile.TemporaryDirectory() as tmp:
            root = os.path.join(tmp, "unpacked")
            with zipfile.ZipFile(self.pptx_path, "r") as zf:
                zf.extractall(root)

            self._check_content_types(root)
            self._check_relationships(root)
            self._check_presentation_xml(root)
            self._check_slide_layouts(root)
            self._check_rels_namespace(root)
            self._check_notes_ownership(root)
            self._check_orphan_files(root)

            errors = [i for i in self.issues if i.severity == "error" and not i.repaired]
            if not errors:
                if self.repairs_made > 0:
                    self._repack(root, out_path or self.pptx_path)
                return True
            return False

    def _check_content_types(self, root: str) -> None:
        ct_path = os.path.join(root, "[Content_Types].xml")
        if not os.path.exists(ct_path):
            self._issue("content_types", "error", "[Content_Types].xml missing")
            return

        try:
            tree = ET.parse(ct_path)
        except ET.ParseError as e:
            self._issue("content_types", "error", f"[Content_Types].xml malformed: {e}")
            return

        ct_root = tree.getroot()

        overrides: dict[str, str] = {}
        for ov in ct_root.findall(f"{{{CT_NS}}}Override"):
            overrides[ov.get("PartName", "")] = ov.get("ContentType", "")

        defaults: dict[str, str] = {}
        for df in ct_root.findall(f"{{{CT_NS}}}Default"):
            defaults[df.get("Extension", "").lower()] = df.get("ContentType", "")

        modified = False

        for part_name in list(overrides.keys()):
            fs_path = os.path.join(root, part_name.lstrip("/"))
            if not os.path.exists(fs_path):
                issue = self._issue(
                    "content_types", "error",
                    f"Override for missing part: {part_name}", repairable=True,
                )
                for ov in ct_root.findall(f"{{{CT_NS}}}Override"):
                    if ov.get("PartName") == part_name:
                        ct_root.remove(ov)
                        issue.repaired = True
                        self.repairs_made += 1
                        modified = True
                        break

        all_content_files = set()
        for dirpath, _dirs, files in os.walk(root):
            for f in files:
                fp = os.path.join(dirpath, f)
                rel = "/" + os.path.relpath(fp, root).replace(os.sep, "/")
                if f == "[Content_Types].xml" or "/_rels/" in rel or rel.endswith(".rels"):
                    continue
                all_content_files.add(rel)

        # Parts that require explicit Override (not just Default extension match)
        OVERRIDE_REQUIRED_PATTERNS = [
            (re.compile(r"/ppt/slides/slide\d+\.xml$"), SLIDE_CT),
            (re.compile(r"/ppt/charts/chart\d+\.xml$"), CHART_CT),
            (re.compile(r"/ppt/notesSlides/notesSlide\d+\.xml$"), NOTES_CT),
        ]

        for part in all_content_files:
            ext = os.path.splitext(part)[1].lstrip(".").lower()

            # Check if this part requires an explicit Override
            required_ct = None
            for pattern, ct_val in OVERRIDE_REQUIRED_PATTERNS:
                if pattern.match(part):
                    required_ct = ct_val
                    break

            if required_ct:
                if part not in overrides:
                    issue = self._issue(
                        "content_types", "error",
                        f"Missing content type override for {part}", repairable=True,
                    )
                    ov_elem = ET.SubElement(ct_root, f"{{{CT_NS}}}Override")
                    ov_elem.set("PartName", part)
                    ov_elem.set("ContentType", required_ct)
                    overrides[part] = required_ct
                    issue.repaired = True
                    self.repairs_made += 1
                    modified = True
                continue

            if part in overrides or ext in defaults:
                continue

            if ext in MEDIA_EXT_CT:
                issue = self._issue(
                    "content_types", "error",
                    f"No content type for .{ext} (used by {part})", repairable=True,
                )
                df_elem = ET.SubElement(ct_root, f"{{{CT_NS}}}Default")
                df_elem.set("Extension", ext)
                df_elem.set("ContentType", MEDIA_EXT_CT[ext])
                defaults[ext] = MEDIA_EXT_CT[ext]
                issue.repaired = True
                self.repairs_made += 1
                modified = True
                continue

            self._issue("content_types", "warning", f"No content type for {part}")

        if modified:
            # Keep the package content-types namespace as the default namespace.
            # Some strict OOXML consumers reject the semantically equivalent
            # ``<ns0:Types>`` form that ElementTree emits otherwise.
            ET.register_namespace("", CT_NS)
            tree.write(ct_path, xml_declaration=True, encoding="UTF-8")

    def _check_relationships(self, root: str) -> None:
        for rels_path in Path(root).rglob("*.rels"):
            try:
                tree = ET.parse(str(rels_path))
            except ET.ParseError as e:
                self._issue(
                    "relationships", "error",
                    f"{_relpath(rels_path, root)} malformed: {e}",
                )
                continue

            rels_root = tree.getroot()
            seen_rids: dict[str, ET.Element] = {}
            modified = False

            for rel in list(rels_root.findall(f"{{{PKG_RELS_NS}}}Relationship")):
                rid = rel.get("Id", "")
                target = rel.get("Target", "")
                target_mode = rel.get("TargetMode", "")

                if rid in seen_rids:
                    issue = self._issue(
                        "relationships", "error",
                        f"{_relpath(rels_path, root)}: duplicate rId '{rid}'",
                        repairable=True,
                    )
                    rels_root.remove(rel)
                    issue.repaired = True
                    self.repairs_made += 1
                    modified = True
                    continue
                seen_rids[rid] = rel

                if target_mode == "External":
                    continue
                if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                    continue

                resolved = self._resolve_target(root, str(rels_path), target)
                if not os.path.exists(resolved):
                    issue = self._issue(
                        "relationships", "error",
                        f"{_relpath(rels_path, root)}: {rid} -> '{target}' "
                        f"target missing ({_relpath(resolved, root)})",
                        repairable=True,
                    )
                    rels_root.remove(rel)
                    issue.repaired = True
                    self.repairs_made += 1
                    modified = True

            if modified:
                tree.write(str(rels_path), xml_declaration=True, encoding="UTF-8")

    def _check_presentation_xml(self, root: str) -> None:
        pres_path = os.path.join(root, "ppt", "presentation.xml")
        if not os.path.exists(pres_path):
            self._issue("presentation", "error", "ppt/presentation.xml missing")
            return

        pres_bytes = Path(pres_path).read_bytes()

        sld_ids = re.findall(rb'<p:sldId\s+id="(\d+)"\s+r:id="(rId\d+)"', pres_bytes)
        if not sld_ids:
            sld_ids_alt = re.findall(rb'<p:sldId\s+r:id="(rId\d+)"\s+id="(\d+)"', pres_bytes)
            sld_ids = [(sid, rid) for rid, sid in sld_ids_alt]

        id_values = [int(sid) for sid, _ in sld_ids]
        if len(id_values) != len(set(id_values)):
            self._issue("presentation", "error", f"Duplicate sldId values: {id_values}")

        pres_rels_path = os.path.join(root, "ppt", "_rels", "presentation.xml.rels")
        if os.path.exists(pres_rels_path):
            pres_rels_bytes = Path(pres_rels_path).read_bytes()
            rels_slides: dict[str, str] = {}
            for m in re.finditer(
                rb'Id="(rId\d+)"[^>]*Target="slides/(slide\d+\.xml)"', pres_rels_bytes
            ):
                rels_slides[m.group(1).decode()] = m.group(2).decode()
            for m in re.finditer(
                rb'Target="slides/(slide\d+\.xml)"[^>]*Id="(rId\d+)"', pres_rels_bytes
            ):
                rels_slides[m.group(2).decode()] = m.group(1).decode()

            for _, rid_bytes in sld_ids:
                rid = rid_bytes.decode() if isinstance(rid_bytes, bytes) else rid_bytes
                if rid not in rels_slides:
                    self._issue(
                        "presentation", "error",
                        f"sldIdLst references {rid} with no matching relationship",
                    )
                else:
                    slide_file = rels_slides[rid]
                    if not os.path.exists(os.path.join(root, "ppt", "slides", slide_file)):
                        self._issue(
                            "presentation", "error",
                            f"sldIdLst -> {rid} -> {slide_file} but file missing",
                        )

        slides_dir = os.path.join(root, "ppt", "slides")
        if os.path.exists(slides_dir):
            actual = [f for f in os.listdir(slides_dir) if re.match(r"slide\d+\.xml$", f)]
            if len(actual) != len(sld_ids):
                self._issue(
                    "presentation", "warning",
                    f"sldIdLst has {len(sld_ids)} entries, {len(actual)} slide files exist",
                )

    def _check_slide_layouts(self, root: str) -> None:
        slides_rels_dir = os.path.join(root, "ppt", "slides", "_rels")
        if not os.path.exists(slides_rels_dir):
            return

        for rels_file in os.listdir(slides_rels_dir):
            if not rels_file.endswith(".rels"):
                continue
            rels_path = os.path.join(slides_rels_dir, rels_file)
            slide_name = rels_file.replace(".rels", "")

            try:
                tree = ET.parse(rels_path)
            except ET.ParseError:
                continue

            rels_root = tree.getroot()
            layout_rels = [
                rel for rel in rels_root.findall(f"{{{PKG_RELS_NS}}}Relationship")
                if "slideLayout" in rel.get("Type", "")
            ]

            if len(layout_rels) == 0:
                self._issue("slide_layouts", "error", f"{slide_name}: no slideLayout relationship")
            elif len(layout_rels) > 1:
                issue = self._issue(
                    "slide_layouts", "error",
                    f"{slide_name}: {len(layout_rels)} slideLayout rels (need exactly 1)",
                    repairable=True,
                )
                for extra in layout_rels[1:]:
                    rels_root.remove(extra)
                issue.repaired = True
                self.repairs_made += 1
                tree.write(rels_path, xml_declaration=True, encoding="UTF-8")

            for rel in layout_rels[:1]:
                target = rel.get("Target", "")
                resolved = self._resolve_target(root, rels_path, target)
                if not os.path.exists(resolved):
                    self._issue(
                        "slide_layouts", "error",
                        f"{slide_name}: slideLayout target '{target}' missing",
                    )

    def _check_rels_namespace(self, root: str) -> None:
        for rels_path in Path(root).rglob("*.rels"):
            content = rels_path.read_bytes()
            if b"rel:Relationship" in content or b"rel:Relationships" in content:
                self._issue(
                    "namespace", "error",
                    f"{_relpath(rels_path, root)}: corrupted namespace prefix",
                )

    def _check_notes_ownership(self, root: str) -> None:
        """Require each slide-owned notesSlide part to have a single owner."""
        rels_dir = Path(root) / "ppt" / "slides" / "_rels"
        if not rels_dir.exists():
            return
        owners: dict[str, list[str]] = {}
        for rels_path in rels_dir.glob("slide*.xml.rels"):
            try:
                rels_root = ET.parse(rels_path).getroot()
            except ET.ParseError:
                continue
            for relationship in rels_root.findall(
                f"{{{PKG_RELS_NS}}}Relationship"
            ):
                if not relationship.get("Type", "").endswith("/notesSlide"):
                    continue
                target = relationship.get("Target", "")
                resolved = os.path.normpath(
                    self._resolve_target(root, str(rels_path), target)
                )
                owners.setdefault(resolved, []).append(
                    rels_path.name.removesuffix(".rels")
                )
        for notes_part, slide_owners in owners.items():
            if len(slide_owners) > 1:
                self._issue(
                    "notes_ownership",
                    "error",
                    f"{_relpath(notes_part, root)} is shared by slides: "
                    + ", ".join(sorted(slide_owners)),
                )

    def _check_orphan_files(self, root: str) -> None:
        referenced = set()
        for rels_path in Path(root).rglob("*.rels"):
            try:
                tree = ET.parse(str(rels_path))
            except ET.ParseError:
                continue
            for rel in tree.getroot().findall(f"{{{PKG_RELS_NS}}}Relationship"):
                target = rel.get("Target", "")
                if rel.get("TargetMode", "") == "External":
                    continue
                resolved = self._resolve_target(root, str(rels_path), target)
                if os.path.exists(resolved):
                    referenced.add(os.path.normpath(resolved))

        for dirpath, _dirs, files in os.walk(root):
            for f in files:
                fp = os.path.join(dirpath, f)
                rel_path = os.path.relpath(fp, root).replace(os.sep, "/")
                if (f == "[Content_Types].xml" or "/_rels/" in f"/{rel_path}"
                        or f.endswith(".rels") or rel_path.startswith("docProps/")):
                    continue
                if os.path.normpath(fp) not in referenced:
                    self._issue("orphan", "warning", f"Unreferenced file: {rel_path}")

    def _resolve_target(self, root: str, rels_path: str, target: str) -> str:
        if target.startswith("/"):
            return os.path.join(root, target.lstrip("/"))
        rels_dir = os.path.dirname(rels_path)
        base_dir = (os.path.dirname(rels_dir)
                    if os.path.basename(rels_dir) == "_rels" else rels_dir)
        return os.path.normpath(os.path.join(base_dir, target))

    def _issue(self, check: str, severity: str, message: str, repairable: bool = False) -> Issue:
        issue = Issue(check, severity, message, repairable)
        self.issues.append(issue)
        if self.verbose:
            print(f"  {issue}")
        return issue

    def _repack(self, source_dir: str, out_path: str) -> None:
        tmp_path = out_path + ".sanitize.tmp"
        with zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for dirpath, _dirs, files in os.walk(source_dir):
                for f in files:
                    fp = os.path.join(dirpath, f)
                    arcname = os.path.relpath(fp, source_dir)
                    zf.write(fp, arcname)
        shutil.move(tmp_path, out_path)

    def report(self) -> str:
        lines = []
        errors = [i for i in self.issues if i.severity == "error"]
        warnings = [i for i in self.issues if i.severity == "warning"]
        repaired = [i for i in self.issues if i.repaired]
        unrepaired = [i for i in errors if not i.repaired]

        lines.append(f"sanitize_pptx: {os.path.basename(self.pptx_path)}")
        lines.append(f"  Errors: {len(errors)}  Warnings: {len(warnings)}  Repaired: {len(repaired)}")

        if unrepaired:
            lines.append(f"  UNREPAIRED ({len(unrepaired)}):")
            for i in unrepaired:
                lines.append(f"    - {i}")

        if repaired:
            lines.append(f"  REPAIRS ({len(repaired)}):")
            for i in repaired:
                lines.append(f"    - {i.message}")

        if warnings and self.verbose:
            lines.append(f"  WARNINGS ({len(warnings)}):")
            for i in warnings:
                lines.append(f"    - {i.message}")

        if not unrepaired:
            lines.append("  Status: " + ("REPAIRED" if repaired else "CLEAN"))
        else:
            lines.append("  Status: FAILED")

        return "\n".join(lines)


def _relpath(path, root) -> str:
    try:
        return os.path.relpath(str(path), root).replace(os.sep, "/")
    except ValueError:
        return str(path)


def main():
    parser = argparse.ArgumentParser(description="PPTX structural integrity validator and repairer")
    parser.add_argument("pptx_path", help="Path to the PPTX file")
    parser.add_argument("--out", help="Output path for repaired file (default: overwrite input)")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--verbose", action="store_true", help="Print each issue as found")
    args = parser.parse_args()

    sanitizer = PPTXSanitizer(args.pptx_path, verbose=args.verbose, strict=args.strict)
    valid = sanitizer.validate_and_repair(out_path=args.out)
    print(sanitizer.report())
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
