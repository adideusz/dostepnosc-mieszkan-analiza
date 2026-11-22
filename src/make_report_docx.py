"""Konwersja raport/sprawozdanie.md → raport/sprawozdanie.docx (python-docx).

Obsługuje: nagłówki #/##/###, akapity z **pogrubieniem**, listy (-, 1.), tabele markdown,
obrazy ![opis](ścieżka) oraz linie poziome (---).

Uruchomienie (z katalogu projektu):  .venv/bin/python src/make_report_docx.py
"""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "raport" / "sprawozdanie.md"
OUT = ROOT / "raport" / "sprawozdanie.docx"


def add_runs(paragraph, text: str) -> None:
    """Dodaje tekst z obsługą **pogrubienia** i `kodu`."""
    for part in re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            paragraph.add_run(part[2:-2]).bold = True
        elif part.startswith("`") and part.endswith("`"):
            run = paragraph.add_run(part[1:-1])
            run.font.name = "Consolas"
            run.font.size = Pt(9.5)
        else:
            paragraph.add_run(part)


def add_table(doc: Document, rows: list[str]) -> None:
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    cells = [r for r in cells if not all(re.fullmatch(r":?-{2,}:?", c) for c in r)]
    table = doc.add_table(rows=len(cells), cols=len(cells[0]))
    table.style = "Light Grid Accent 1"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(cells):
        for j, value in enumerate(row[: len(cells[0])]):
            cell = table.cell(i, j)
            cell.text = ""
            p = cell.paragraphs[0]
            add_runs(p, value)
            for run in p.runs:
                run.font.size = Pt(9)
                if i == 0:
                    run.bold = True
    doc.add_paragraph()


def main() -> None:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)
    for section in doc.sections:
        section.left_margin = section.right_margin = Cm(2.2)
        section.top_margin = section.bottom_margin = Cm(2)

    lines = SRC.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line or line == "---":
            i += 1
            continue
        if line.startswith("|"):
            block = []
            while i < len(lines) and lines[i].startswith("|"):
                block.append(lines[i])
                i += 1
            add_table(doc, block)
            continue
        img = re.fullmatch(r"!\[(.*?)\]\((.*?)\)", line)
        if img:
            path = (SRC.parent / img.group(2)).resolve()
            if path.exists():
                doc.add_picture(str(path), width=Cm(16))
                doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                cap = doc.add_paragraph(img.group(1))
                cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                cap.runs[0].italic = True
                cap.runs[0].font.size = Pt(9)
            i += 1
            continue
        heading = re.match(r"^(#{1,3})\s+(.*)", line)
        if heading:
            level = len(heading.group(1))
            h = doc.add_heading(heading.group(2), level=0 if level == 1 else level - 1)
            if level == 1:
                h.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif re.match(r"^\s*-\s+", line):
            add_runs(doc.add_paragraph(style="List Bullet"), re.sub(r"^\s*-\s+", "", line))
        elif re.match(r"^\d+\.\s+", line):
            add_runs(doc.add_paragraph(style="List Number"), re.sub(r"^\d+\.\s+", "", line))
        else:
            add_runs(doc.add_paragraph(), line)
        i += 1

    doc.save(OUT)
    print(f"Zapisano {OUT}")


if __name__ == "__main__":
    main()
