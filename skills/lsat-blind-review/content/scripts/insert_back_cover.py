"""
Insert back cover PNG as last page of the workbook, only if page count is odd.

Usage:
    python insert_back_cover.py <workbook.docx> <back_cover.png> [--force]

Logic:
    1. Detect workbook page count via soffice headless → PDF → /Pages
    2. If odd (or --force): append back_cover.png as last page
    3. Else: skip with informational message

Page-count detection fallback chain:
    - soffice + pikepdf (preferred; reliable)
    - docx2pdf + pypdf
    - lastRenderedPageBreak count + content density heuristic (last resort)
"""
from __future__ import annotations
import argparse
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from docx import Document
from docx.shared import Cm
from docx.enum.text import WD_BREAK


def _page_count_via_soffice(docx_path: Path) -> int | None:
    """Convert docx to PDF via soffice and read /Pages from the PDF."""
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        return None
    try:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            subprocess.run(
                [soffice, "--headless", "--convert-to", "pdf",
                 "--outdir", str(tmp), str(docx_path)],
                capture_output=True, timeout=120, check=True,
            )
            pdfs = list(tmp.glob("*.pdf"))
            if not pdfs:
                return None
            pdf = pdfs[0]
            try:
                from pypdf import PdfReader
                return len(PdfReader(str(pdf)).pages)
            except ImportError:
                # Fallback: pikepdf
                import pikepdf
                with pikepdf.open(str(pdf)) as p:
                    return len(p.pages)
    except Exception as e:
        print(f"  [warn] soffice path failed: {e}", file=sys.stderr)
        return None


def _page_count_via_lastRendered(docx_path: Path) -> int | None:
    """Heuristic: count <w:lastRenderedPageBreak> + 1.

    NOTE: only set after Word/LibreOffice has opened the file and saved it.
    For freshly built docx (e.g. python-docx output), this often returns 1.
    Approximate; prefer soffice+pypdf path.
    """
    with zipfile.ZipFile(str(docx_path)) as z:
        try:
            xml = z.read("word/document.xml").decode("utf-8", errors="ignore")
        except KeyError:
            return None
    return xml.count("w:lastRenderedPageBreak") + 1


def _page_count_via_docx2pdf(docx_path: Path) -> int | None:
    """Try docx2pdf → pypdf on the produced PDF (requires Word/LibreOffice)."""
    try:
        from docx2pdf import convert as docx2pdf_convert
        from pypdf import PdfReader
        with tempfile.TemporaryDirectory() as td:
            docx2pdf_convert(str(docx_path), td)
            pdfs = list(Path(td).glob("*.pdf"))
            if not pdfs:
                return None
            return len(PdfReader(str(pdfs[0])).pages)
    except Exception as e:
        print(f"  [warn] docx2pdf path failed: {e}", file=sys.stderr)
        return None


def detect_page_count(docx_path: Path) -> int:
    """Try soffice → PDF first; then docx2pdf; fall back to heuristic."""
    n = _page_count_via_soffice(docx_path)
    if n is not None and n > 0:
        return n
    n = _page_count_via_docx2pdf(docx_path)
    if n is not None and n > 0:
        return n
    n = _page_count_via_lastRendered(docx_path)
    if n is not None and n > 0:
        print(f"  [warn] using lastRenderedPageBreak heuristic "
              f"(unreliable for freshly built docx; install LibreOffice "
              f"soffice for accurate count)", file=sys.stderr)
        return n
    raise RuntimeError(
        "Cannot detect page count. Install one of: soffice (LibreOffice) "
        "+ pypdf/pikepdf, or Microsoft Word + docx2pdf."
    )


def insert_back_cover(docx_path: Path, back_cover_path: Path) -> Path:
    """Append back_cover.png as last page of the workbook."""
    doc = Document(str(docx_path))
    back_p = doc.add_paragraph()
    run = back_p.add_run()
    run.add_picture(str(back_cover_path), width=Cm(17.0))
    doc.save(str(docx_path))
    return docx_path


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Insert back cover PNG as last page (only if odd page count)."
    )
    ap.add_argument("docx", type=Path)
    ap.add_argument("back_cover", type=Path)
    ap.add_argument("--force", action="store_true",
                    help="Insert even if page count is even")
    args = ap.parse_args()

    if not args.docx.exists():
        print(f"FAIL: docx not found: {args.docx}", file=sys.stderr)
        return 1
    if not args.back_cover.exists():
        print(f"FAIL: back_cover not found: {args.back_cover}", file=sys.stderr)
        return 1

    pages = detect_page_count(args.docx)
    odd = (pages % 2 == 1)

    print(f"[detect] {args.docx.name}: {pages} page(s) → "
          f"{'odd' if odd else 'even'}")

    if not odd and not args.force:
        print(f"SKIP: workbook has even page count ({pages}); "
              f"back cover not added (per skill rule).")
        print(f"  Use --force to override.")
        return 0

    insert_back_cover(args.docx, args.back_cover)
    print(f"[insert] back cover appended. {args.docx.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())