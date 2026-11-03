"""
Insert cover PNG as page 1 of the workbook.

Usage:
    python insert_cover.py <workbook.docx> <cover.png>
"""
from __future__ import annotations
import sys
from pathlib import Path
from docx import Document
from docx.shared import Cm
from docx.enum.text import WD_BREAK


def insert_cover(docx_path: Path, cover_path: Path) -> Path:
    doc = Document(str(docx_path))
    first_p = doc.paragraphs[0]
    cover_p = first_p.insert_paragraph_before("")
    run = cover_p.add_run()
    run.add_picture(str(cover_path), width=Cm(17.0))
    cover_p.add_run().add_break(WD_BREAK.PAGE)
    doc.save(str(docx_path))
    return docx_path


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python insert_cover.py <workbook.docx> <cover.png>")
        sys.exit(1)
    p = insert_cover(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"Cover inserted. {p.stat().st_size} bytes")