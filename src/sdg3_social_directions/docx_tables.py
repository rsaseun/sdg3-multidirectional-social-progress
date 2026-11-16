"""Write publication tables to an editable Word file: black text, horizontal rules only, no shading.

Captions follow Springer Nature style: bold "Table 1" followed by the caption text."""
from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

FONT = "Times New Roman"


def _border(cell, **kw):
    tcPr = cell._tc.get_or_add_tcPr()
    b = tcPr.find(qn("w:tcBorders"))
    if b is None:
        b = OxmlElement("w:tcBorders"); tcPr.append(b)
    for edge, sz in kw.items():
        el = OxmlElement(f"w:{edge}"); el.set(qn("w:val"), "single"); el.set(qn("w:sz"), str(sz))
        el.set(qn("w:color"), "000000"); el.set(qn("w:space"), "0"); b.append(el)


def add_table(doc, label, title, df, note=None, widths=None, size=9, symbol_cols=(), sep=" "):
    p = doc.add_paragraph(); p.paragraph_format.keep_with_next = True
    r = p.add_run(label + sep); r.bold = True; p.add_run(title)
    t = doc.add_table(rows=1 + len(df), cols=df.shape[1]); t.autofit = False
    for j, c in enumerate(df.columns):
        cell = t.cell(0, j); cell.text = ""; rr = cell.paragraphs[0].add_run(str(c)); rr.bold = True; rr.font.size = Pt(size)
    for i, row in enumerate(df.itertuples(index=False), 1):
        for j, v in enumerate(row):
            cell = t.cell(i, j); cell.text = ""
            rr = cell.paragraphs[0].add_run("" if (not isinstance(v, str) and pd.isna(v)) else str(v)); rr.font.size = Pt(size)
            if j in symbol_cols and str(v) in ("●", "•", "⊗", "⊘"):
                rr.font.name = "Segoe UI Symbol"
    for row in t.rows:
        for cell in row.cells:
            for pp in cell.paragraphs:
                pp.paragraph_format.space_after = Pt(1)
    for j in range(df.shape[1]):
        _border(t.cell(0, j), top=8, bottom=6)
        _border(t.cell(len(df), j), bottom=8)
    if widths:
        for j, gc in enumerate(t._tbl.tblGrid.findall(qn("w:gridCol"))):
            gc.set(qn("w:w"), str(int(widths[j] * 567)))
        for row in t.rows:
            for j, cell in enumerate(row.cells):
                cell.width = Cm(widths[j])
        lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); t._tbl.tblPr.append(lay)
    if note:
        p = doc.add_paragraph(); r = p.add_run(note); r.font.size = Pt(8.5)
    doc.add_paragraph()
    return t


def write_tables_docx(tables, path, landscape=True):
    """tables: list of dicts with label, title, df, note, widths (cm) and optional symbol_cols."""
    doc = Document()
    st = doc.styles["Normal"]; st.font.name = FONT; st.font.size = Pt(10)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    sec = doc.sections[0]
    if landscape:
        sec.orientation = WD_ORIENT.LANDSCAPE; sec.page_width, sec.page_height = Cm(29.7), Cm(21.0)
    for m in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(sec, m, Cm(2.0))
    for tb in tables:
        add_table(doc, tb["label"], tb["title"], tb["df"], tb.get("note"), tb.get("widths"), symbol_cols=tb.get("symbol_cols", ()))
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    doc.save(path)
