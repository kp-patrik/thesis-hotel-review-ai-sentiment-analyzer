from __future__ import annotations

from pathlib import Path
from textwrap import wrap
from typing import Iterable, Sequence

from docx import Document
from docx.enum.section import WD_SECTION_START
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "artifacts" / "diploma_documentation"
IMG_DIR = OUT_DIR / "figures"
DOCX_PATH = OUT_DIR / "Documentatie_licenta_Hotel_Review_NLP.docx"

BLUE = RGBColor(31, 77, 120)
LIGHT_BLUE = "E8EEF5"
LIGHT_GRAY = "F4F6F9"
GRID = "D7DBE2"
MUTED = RGBColor(89, 89, 89)
BLACK = RGBColor(0, 0, 0)


def ensure_dirs() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    IMG_DIR.mkdir(parents=True, exist_ok=True)


def set_run_font(run, name: str = "Times New Roman", size: float | None = None,
                 color: RGBColor | None = None, bold: bool | None = None,
                 italic: bool | None = None) -> None:
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:ascii"), name)
    run._element.rPr.rFonts.set(qn("w:hAnsi"), name)
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    if size is not None:
        run.font.size = Pt(size)
    if color is not None:
        run.font.color.rgb = color
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_width(cell, width_dxa: int) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_w = tc_pr.find(qn("w:tcW"))
    if tc_w is None:
        tc_w = OxmlElement("w:tcW")
        tc_pr.append(tc_w)
    tc_w.set(qn("w:w"), str(width_dxa))
    tc_w.set(qn("w:type"), "dxa")


def set_cell_margins(cell, top=80, bottom=80, start=120, end=120) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.find(qn("w:tcMar"))
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for m, val in (("top", top), ("bottom", bottom), ("start", start), ("end", end)):
        node = tc_mar.find(qn(f"w:{m}"))
        if node is None:
            node = OxmlElement(f"w:{m}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")


def set_table_geometry(table, widths_dxa: Sequence[int]) -> None:
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.allow_autofit = False
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(sum(widths_dxa)))
    tbl_w.set(qn("w:type"), "dxa")

    tbl_ind = tbl_pr.find(qn("w:tblInd"))
    if tbl_ind is None:
        tbl_ind = OxmlElement("w:tblInd")
        tbl_pr.append(tbl_ind)
    tbl_ind.set(qn("w:w"), "120")
    tbl_ind.set(qn("w:type"), "dxa")

    grid = tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for w in widths_dxa:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(w))
        grid.append(col)

    for row in table.rows:
        for i, cell in enumerate(row.cells):
            set_cell_width(cell, widths_dxa[min(i, len(widths_dxa) - 1)])
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def add_page_number(paragraph) -> None:
    run = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_end)


def add_toc(paragraph) -> None:
    run = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = r'TOC \o "1-3" \h \z \u'
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    display = OxmlElement("w:t")
    display.text = "Cuprinsul se actualizează automat în Word prin Update Field."
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_sep)
    run._r.append(display)
    run._r.append(fld_end)


def set_update_fields_on_open(doc: Document) -> None:
    settings = doc.settings._element
    update = settings.find(qn("w:updateFields"))
    if update is None:
        update = OxmlElement("w:updateFields")
        settings.append(update)
    update.set(qn("w:val"), "true")


def setup_document() -> Document:
    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)
    section.header_distance = Cm(1.25)
    section.footer_distance = Cm(1.25)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Times New Roman"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    normal.font.size = Pt(12)
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    normal.paragraph_format.line_spacing = 1.3
    normal.paragraph_format.space_after = Pt(6)

    for name, size, color, before, after in [
        ("Heading 1", 15, BLUE, 14, 8),
        ("Heading 2", 13, BLUE, 10, 6),
        ("Heading 3", 12, RGBColor(37, 74, 105), 8, 4),
    ]:
        st = styles[name]
        st.font.name = "Times New Roman"
        st._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
        st._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = color
        st.paragraph_format.space_before = Pt(before)
        st.paragraph_format.space_after = Pt(after)
        st.paragraph_format.keep_with_next = True

    caption = styles.add_style("CaptionAcademic", 1)
    caption.base_style = styles["Normal"]
    caption.font.name = "Times New Roman"
    caption._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
    caption._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    caption.font.size = Pt(10)
    caption.font.italic = True
    caption.font.color.rgb = MUTED
    caption.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption.paragraph_format.space_after = Pt(8)

    code = styles.add_style("CodeAcademic", 1)
    code.base_style = styles["Normal"]
    code.font.name = "Consolas"
    code._element.rPr.rFonts.set(qn("w:ascii"), "Consolas")
    code._element.rPr.rFonts.set(qn("w:hAnsi"), "Consolas")
    code.font.size = Pt(8.5)
    code.paragraph_format.line_spacing = 1.05
    code.paragraph_format.space_after = Pt(2)
    code.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

    bib = styles.add_style("BibliographySmall", 1)
    bib.base_style = styles["Normal"]
    bib.font.name = "Times New Roman"
    bib._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
    bib._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    bib.font.size = Pt(9)
    bib.paragraph_format.line_spacing = 1.0
    bib.paragraph_format.space_after = Pt(2)

    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = header.add_run("Documentație licență - Hotel Review NLP")
    set_run_font(r, size=9, color=MUTED, italic=True)

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run_font(footer.add_run("Pagina "), size=9, color=MUTED)
    add_page_number(footer)

    set_update_fields_on_open(doc)
    return doc


def add_para(doc: Document, text: str, style: str | None = None,
             align: WD_ALIGN_PARAGRAPH | None = None,
             bold_lead: str | None = None) -> None:
    p = doc.add_paragraph(style=style)
    if align is not None:
        p.alignment = align
    if bold_lead and text.startswith(bold_lead):
        r1 = p.add_run(bold_lead)
        set_run_font(r1, bold=True)
        r2 = p.add_run(text[len(bold_lead):])
        set_run_font(r2)
    else:
        r = p.add_run(text)
        set_run_font(r)


def add_bullets(doc: Document, items: Iterable[str]) -> None:
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.left_indent = Cm(0.75)
        p.paragraph_format.first_line_indent = Cm(-0.25)
        run = p.add_run(item)
        set_run_font(run)


def add_numbered(doc: Document, items: Iterable[str]) -> None:
    for item in items:
        p = doc.add_paragraph(style="List Number")
        p.paragraph_format.left_indent = Cm(0.75)
        p.paragraph_format.first_line_indent = Cm(-0.25)
        run = p.add_run(item)
        set_run_font(run)


def add_caption(doc: Document, text: str) -> None:
    p = doc.add_paragraph(style="CaptionAcademic")
    run = p.add_run(text)
    set_run_font(run, size=10, color=MUTED, italic=True)


def add_table(doc: Document, headers: Sequence[str], rows: Sequence[Sequence[str]],
              widths_dxa: Sequence[int] | None = None) -> None:
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    if widths_dxa is None:
        widths_dxa = [int(9360 / len(headers))] * len(headers)
    set_table_geometry(table, widths_dxa)
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        set_cell_shading(hdr[i], LIGHT_BLUE)
        p = hdr[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        set_run_font(r, size=10.5, bold=True)
    for row in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            p = cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(str(val))
            set_run_font(r, size=10)
            set_cell_margins(cells[i])
    doc.add_paragraph()


def add_code(doc: Document, code: str, title: str | None = None) -> None:
    if title:
        add_para(doc, title, bold_lead=title.split(":")[0] + ":" if ":" in title else None)
    table = doc.add_table(rows=1, cols=1)
    table.style = "Table Grid"
    set_table_geometry(table, [9360])
    cell = table.cell(0, 0)
    set_cell_shading(cell, "F7F9FB")
    p = cell.paragraphs[0]
    p.style = "CodeAcademic"
    for i, line in enumerate(code.strip("\n").splitlines()):
        if i:
            p.add_run("\n")
        r = p.add_run(line)
        set_run_font(r, name="Consolas", size=8.5)
    doc.add_paragraph()


def add_explanation_table(doc: Document, rows: Sequence[Sequence[str]]) -> None:
    add_table(doc, ["Element de cod", "Explicație"], rows, [2300, 7060])


def font(size=28, bold=False):
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/calibri.ttf"),
    ]
    for p in candidates:
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def draw_wrapped(draw: ImageDraw.ImageDraw, xy, text: str, fnt, fill, width_px: int, line_gap: int = 5) -> int:
    x, y = xy
    lines: list[str] = []
    for raw in text.split("\n"):
        current = ""
        for word in raw.split():
            test = f"{current} {word}".strip()
            if draw.textbbox((0, 0), test, font=fnt)[2] <= width_px:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += draw.textbbox((0, 0), line, font=fnt)[3] + line_gap
    return y


def arrow(draw: ImageDraw.ImageDraw, start, end, fill="#34495e", width=3) -> None:
    import math

    draw.line([start, end], fill=fill, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    size = 14
    pts = [
        end,
        (end[0] - size * math.cos(angle - math.pi / 6), end[1] - size * math.sin(angle - math.pi / 6)),
        (end[0] - size * math.cos(angle + math.pi / 6), end[1] - size * math.sin(angle + math.pi / 6)),
    ]
    draw.polygon(pts, fill=fill)


def box(draw: ImageDraw.ImageDraw, xy, label: str, fill="#ffffff", outline="#2f6f9f") -> None:
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=18, fill=fill, outline=outline, width=3)
    f = font(24, bold=True)
    tf = font(18)
    title, *rest = label.split("\n")
    tw = draw.textbbox((0, 0), title, font=f)[2]
    draw.text((x1 + (x2 - x1 - tw) / 2, y1 + 18), title, font=f, fill="#12263a")
    if rest:
        draw_wrapped(draw, (x1 + 18, y1 + 60), "\n".join(rest), tf, "#34495e", x2 - x1 - 36)


def make_diagram(name: str, title: str, nodes: Sequence[tuple[int, int, int, int, str]],
                 arrows: Sequence[tuple[int, int, int, int]]) -> Path:
    img = Image.new("RGB", (1400, 880), "#ffffff")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, 1400, 92), fill="#e8eef5")
    draw.text((44, 28), title, font=font(34, bold=True), fill="#1f4d78")
    for n in nodes:
        box(draw, n[:4], n[4])
    for a in arrows:
        arrow(draw, (a[0], a[1]), (a[2], a[3]))
    path = IMG_DIR / f"{name}.png"
    img.save(path, quality=95)
    return path


def make_placeholder(name: str, title: str, description: str) -> Path:
    img = Image.new("RGB", (1300, 700), "#fbfbfb")
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((30, 30, 1270, 670), radius=20, fill="#ffffff", outline="#b8c4d3", width=4)
    draw.rectangle((30, 30, 1270, 112), fill="#e8eef5", outline="#b8c4d3")
    draw.text((60, 54), title, font=font(32, bold=True), fill="#1f4d78")
    draw_wrapped(draw, (70, 170), description, font(24), "#333333", 1160, line_gap=10)
    draw.text((70, 590), "[SCREENSHOT PLACEHOLDER]", font=font(28, bold=True), fill="#7a5a00")
    path = IMG_DIR / f"{name}.png"
    img.save(path, quality=95)
    return path


def make_figures() -> dict[str, Path]:
    figs: dict[str, Path] = {}
    figs["project_structure"] = make_placeholder(
        "screenshot_project_structure",
        "SCREENSHOT 1 - Structura proiectului",
        "Marcaj pentru captura cu directoarele backend, frontend, fișierele de configurare și resursele principale ale aplicației.",
    )
    figs["dependencies"] = make_placeholder(
        "screenshot_dependencies",
        "SCREENSHOT 2 - Dependențe și biblioteci",
        "Marcaj pentru captura cu requirements.txt și package.json, unde sunt evidențiate FastAPI, Transformers, SQLAlchemy, React, Vite, Axios și Recharts.",
    )
    figs["config"] = make_placeholder(
        "screenshot_config",
        "SCREENSHOT 3 - Configurații importante",
        "Marcaj pentru captura cu vite.config.js, .env.example și setările de rulare pentru backend și frontend.",
    )
    for key, title in [
        ("login", "SCREENSHOT - Pagina Login"),
        ("register", "SCREENSHOT - Pagina Înregistrare"),
        ("dashboard", "SCREENSHOT - Dashboard / Listă hoteluri"),
        ("profile", "SCREENSHOT - Profil Utilizator"),
        ("add_review", "SCREENSHOT - Formular Adăugare Review"),
        ("data_admin", "SCREENSHOT - Administrare Date / Date persistente"),
        ("settings", "SCREENSHOT - Setări / Configurații"),
        ("details", "SCREENSHOT - Vizualizare Detalii Hotel"),
        ("full_flow", "SCREENSHOT - Flux complet de utilizare"),
        ("test_auth", "SCREENSHOT - Test autentificare"),
        ("test_main", "SCREENSHOT - Test funcționalitate principală"),
        ("test_validation", "SCREENSHOT - Test validare"),
        ("database", "SCREENSHOT - Baza de date"),
    ]:
        figs[key] = make_placeholder(key, title, "Loc rezervat pentru captura de ecran corespunzătoare. Fiecare captură se va insera aici în etapa de predare finală, cu titlu și explicație asociată.")

    figs["use_case"] = make_diagram(
        "diagram_use_case",
        "Diagramă Use Case",
        [
            (70, 165, 310, 285, "Vizitator\nExplorează hoteluri\nCitește detalii"),
            (70, 380, 310, 520, "Utilizator autentificat\nScrie review\nRulează analiză\nGenerează sumar"),
            (540, 145, 860, 255, "Aplicație web\nHotel Reviews"),
            (1030, 150, 1280, 250, "Autentificare\nRegister / Login / Me"),
            (1030, 315, 1280, 415, "Review-uri\nCreate + sentiment"),
            (1030, 480, 1280, 580, "Sumarizare\nT5 / fallback"),
        ],
        [(310, 225, 540, 205), (310, 450, 540, 220), (860, 200, 1030, 200), (860, 230, 1030, 365), (860, 250, 1030, 530)],
    )
    figs["component"] = make_diagram(
        "diagram_component",
        "Diagramă Component",
        [
            (60, 170, 310, 310, "React UI\nPages + Components"),
            (430, 170, 680, 310, "Service Layer\nAxios + fetch adapters"),
            (800, 170, 1080, 310, "FastAPI Backend\nRoutes + Pydantic"),
            (800, 450, 1080, 610, "SQLAlchemy ORM\nHotel / Review / User"),
            (1130, 450, 1340, 610, "SQLite DB\nhotel_reviews.db"),
            (1130, 170, 1340, 310, "NLP Models\nDistilBERT + T5"),
        ],
        [(310, 240, 430, 240), (680, 240, 800, 240), (940, 310, 940, 450), (1080, 530, 1130, 530), (1080, 240, 1130, 240)],
    )
    figs["deployment"] = make_diagram(
        "diagram_deployment",
        "Diagramă Deployment",
        [
            (80, 170, 390, 340, "Client browser\nhttp://localhost:5173\nReact + Vite"),
            (560, 170, 900, 340, "Backend server\nhttp://localhost:8000\nUvicorn + FastAPI"),
            (1040, 170, 1300, 340, "Local storage\nSQLite database"),
            (560, 500, 900, 660, "Model cache\nTransformers models"),
            (1040, 500, 1300, 660, "SMTP service\noptional / console fallback"),
        ],
        [(390, 255, 560, 255), (900, 255, 1040, 255), (730, 340, 730, 500), (900, 590, 1040, 590)],
    )
    figs["architecture"] = make_diagram(
        "diagram_architecture",
        "Architecture Overview",
        [
            (70, 150, 310, 300, "Interfață\nHeader, pagini,\nformulare"),
            (430, 150, 700, 300, "Orchestrare UI\nAuthProvider,\nProtectedRoute"),
            (820, 150, 1080, 300, "API REST\nFastAPI endpoints"),
            (430, 470, 700, 620, "Procesare NLP\nsentiment + summary"),
            (820, 470, 1080, 620, "Persistență\nORM + SQLite"),
            (1160, 310, 1350, 450, "Email\nverificare/resetare"),
        ],
        [(310, 225, 430, 225), (700, 225, 820, 225), (950, 300, 560, 470), (950, 300, 950, 470), (1080, 240, 1160, 365)],
    )
    figs["erd"] = make_diagram(
        "diagram_erd",
        "ERD - Modelul bazei de date",
        [
            (60, 170, 400, 430, "users\nPK id\nusername UNIQUE\nemail\nhashed_password\ncreated_at"),
            (520, 170, 880, 500, "hotels\nPK id\nname\nlocation\ndescription\nrating\naverage_sentiment\ntotal_reviews\ncategory\nprice_range\namenities"),
            (1010, 170, 1360, 500, "reviews\nPK id\nFK hotel_id\nreviewer_name\nreview_text\nsentiment_label\nsentiment_score\ncreated_at\nuser_name"),
        ],
        [(880, 330, 1010, 330)],
    )
    figs["navigation"] = make_diagram(
        "diagram_navigation_flow",
        "Navigation Flow",
        [
            (65, 155, 270, 265, "Home"),
            (390, 155, 600, 265, "Hotels"),
            (720, 155, 930, 265, "Hotel Detail"),
            (1050, 155, 1270, 265, "Review Form"),
            (390, 430, 600, 540, "Login/Register"),
            (720, 430, 930, 540, "Profile"),
            (1050, 430, 1270, 540, "My Reviews"),
            (720, 650, 930, 760, "Analyze / Summaries"),
        ],
        [(270, 210, 390, 210), (600, 210, 720, 210), (930, 210, 1050, 210), (470, 265, 470, 430), (600, 485, 720, 485), (930, 485, 1050, 485), (820, 265, 820, 650)],
    )
    figs["journey"] = make_diagram(
        "diagram_user_journey",
        "User Journey",
        [
            (70, 170, 260, 300, "1. Intrare\nHome"),
            (330, 170, 520, 300, "2. Explorare\nListă hoteluri"),
            (590, 170, 780, 300, "3. Detaliu\nReview-uri"),
            (850, 170, 1040, 300, "4. Login\nToken JWT"),
            (1110, 170, 1300, 300, "5. Review\nAnaliză NLP"),
            (460, 520, 650, 660, "6. Sumar\nT5/fallback"),
            (740, 520, 930, 660, "7. Profil\nReview-uri recente"),
        ],
        [(260, 235, 330, 235), (520, 235, 590, 235), (780, 235, 850, 235), (1040, 235, 1110, 235), (1205, 300, 650, 520), (650, 590, 740, 590)],
    )
    figs["seq_auth"] = make_diagram(
        "diagram_sequence_auth",
        "Sequence - Autentificare",
        [
            (70, 150, 270, 260, "Utilizator"),
            (390, 150, 600, 260, "Login.jsx"),
            (720, 150, 930, 260, "authApi.login"),
            (1050, 150, 1280, 260, "FastAPI /login"),
            (1050, 520, 1280, 650, "JWT + /me"),
            (390, 520, 600, 650, "AuthProvider"),
        ],
        [(270, 205, 390, 205), (600, 205, 720, 205), (930, 205, 1050, 205), (1165, 260, 1165, 520), (1050, 585, 600, 585)],
    )
    figs["seq_crud"] = make_diagram(
        "diagram_sequence_crud",
        "Sequence - Creare Review",
        [
            (60, 160, 260, 270, "Utilizator"),
            (370, 160, 590, 270, "ReviewForm"),
            (700, 160, 920, 270, "POST /reviews"),
            (1020, 160, 1320, 270, "FastAPI + get_current_user"),
            (1020, 430, 1320, 560, "SentimentAnalyzer"),
            (700, 430, 920, 560, "SQLAlchemy"),
            (370, 430, 590, 560, "UI refresh"),
        ],
        [(260, 215, 370, 215), (590, 215, 700, 215), (920, 215, 1020, 215), (1170, 270, 1170, 430), (1020, 500, 920, 500), (700, 500, 590, 500)],
    )
    figs["activity"] = make_diagram(
        "diagram_activity_main",
        "Activity - Flux principal",
        [
            (90, 160, 300, 270, "Start"),
            (420, 160, 680, 270, "Încarcă hoteluri"),
            (800, 160, 1060, 270, "Selectează hotel"),
            (420, 420, 680, 540, "Autentificare?"),
            (800, 420, 1060, 540, "Trimite review"),
            (1110, 420, 1340, 540, "Analiză + salvare"),
            (620, 650, 900, 760, "Actualizează scoruri"),
        ],
        [(300, 215, 420, 215), (680, 215, 800, 215), (930, 270, 550, 420), (680, 480, 800, 480), (1060, 480, 1110, 480), (1225, 540, 760, 650)],
    )
    figs["class"] = make_diagram(
        "diagram_class",
        "Class Diagram",
        [
            (70, 150, 330, 340, "User\nid\nusername\nemail\nhashed_password\ncreated_at"),
            (500, 150, 820, 420, "Hotel\nid\nname\nlocation\ndescription\nrating\naverage_sentiment\ntotal_reviews\ncategory\nprice_range\namenities"),
            (1010, 150, 1340, 420, "Review\nid\nhotel_id\nreviewer_name\nreview_text\nsentiment_label\nsentiment_score\ncreated_at"),
            (260, 560, 560, 735, "SentimentAnalyzer\nclassifier\nanalyze_sentiment(text)"),
            (760, 560, 1080, 735, "ReviewSummarizer\nsummarizer\nsummarize_reviews(list)"),
        ],
        [(820, 285, 1010, 285), (560, 640, 760, 640), (670, 420, 430, 560), (1170, 420, 930, 560)],
    )
    figs["state"] = make_diagram(
        "diagram_state_machine",
        "State Machine - Review",
        [
            (80, 190, 300, 300, "Formular gol"),
            (430, 190, 650, 300, "Validare client"),
            (780, 190, 1000, 300, "Cerere trimisă"),
            (1130, 190, 1320, 300, "Persistat"),
            (430, 520, 650, 640, "Eroare\n401/404/500"),
            (780, 520, 1000, 640, "Actualizare UI"),
        ],
        [(300, 245, 430, 245), (650, 245, 780, 245), (1000, 245, 1130, 245), (890, 300, 890, 520), (780, 580, 650, 580), (650, 520, 780, 300)],
    )
    return figs


def add_figure(doc: Document, image_path: Path, caption: str, width_in: float = 5.85) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(str(image_path), width=Inches(width_in))
    add_caption(doc, caption)


def page_break(doc: Document) -> None:
    doc.add_page_break()


def add_cover(doc: Document) -> None:
    for text, size, bold, after in [
        ("UNIVERSITATEA DIN ORADEA", 14, True, 2),
        ("FACULTATEA DE INGINERIE ELECTRICĂ ȘI TEHNOLOGIA INFORMAȚIEI", 13, True, 2),
        ("PROGRAMUL DE STUDIU: CALCULATOARE", 12, True, 2),
        ("FORMA DE ÎNVĂȚĂMÂNT: ÎNVĂȚĂMÂNT CU FRECVENȚĂ", 12, True, 42),
        ("Proiect de diplomă", 20, True, 16),
        ("SISTEM WEB PENTRU ANALIZA SENTIMENTULUI ÎN REVIEW-URI HOTELIERE", 16, True, 60),
    ]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(after)
        r = p.add_run(text)
        set_run_font(r, size=size, bold=bold)
    table = doc.add_table(rows=2, cols=2)
    table.style = "Table Grid"
    set_table_geometry(table, [4680, 4680])
    rows = [
        ("COORDONATOR ȘTIINȚIFIC", "ABSOLVENT"),
        ("________________________", "Patrik Kiraly"),
    ]
    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            set_cell_shading(cell, "FFFFFF")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            rr = p.add_run(val)
            set_run_font(rr, size=11, bold=(r_idx == 0))
    doc.add_paragraph()
    for text in ["ORADEA", "2026"]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text)
        set_run_font(r, size=12, bold=True)


def add_theme_page(doc: Document) -> None:
    doc.add_heading("TEMA LUCRĂRII", level=1)
    add_para(doc, "Lucrare de finalizare a studiilor pentru proiectul: Sistem web pentru analiza sentimentului în review-uri hoteliere.")
    rows = [
        ("Tema lucrării", "Proiectarea și implementarea unei aplicații full-stack care permite explorarea hotelurilor, autentificarea utilizatorilor, adăugarea de review-uri și analiza automată a sentimentului pe baza unor modele NLP."),
        ("Elemente inițiale", "Cod sursă Python/FastAPI, React/Vite, SQLAlchemy, SQLite, Hugging Face Transformers, JWT, servicii SMTP și date locale pentru hoteluri și review-uri."),
        ("Conținutul lucrării", "Introducere; tehnologii utilizate; analiza și proiectarea sistemului; implementarea aplicației; testarea; concluzii; bibliografie; anexe."),
        ("Material grafic", "Diagrame de cazuri de utilizare, componente, deployment, ERD, fluxuri de navigare, secvențe, activități, clasă și capturi de ecran marcate pentru interfața aplicației."),
        ("Loc de documentare", "Documentații oficiale, articole științifice despre modele Transformer și analiza sentimentului, codul sursă al aplicației și structura bazei de date locale."),
    ]
    add_table(doc, ["Element", "Descriere"], rows, [2300, 7060])
    add_para(doc, "Lucrarea este redactată în limba română, în stil academic, și urmărește explicarea detaliată a fiecărui modul existent în proiect, fără a introduce funcționalități care nu sunt susținute de codul sursă.")


def add_toc_page(doc: Document) -> None:
    doc.add_heading("CUPRINS AUTOMAT", level=1)
    add_para(doc, "Câmpul de mai jos este un cuprins Word automat. La deschiderea documentului în Microsoft Word, se poate folosi comanda Update Field pentru actualizarea numerelor de pagină.")
    p = doc.add_paragraph()
    add_toc(p)
    add_para(doc, "Structura urmărește cerința lucrării: introducere, tehnologii, analiză și proiectare, implementare, testare, concluzii, bibliografie și anexe.")


def add_page_block(doc: Document, heading: str, paragraphs: Sequence[str],
                   bullets: Sequence[str] | None = None,
                   figure: tuple[Path, str] | None = None,
                   table: tuple[Sequence[str], Sequence[Sequence[str]], Sequence[int] | None, str | None] | None = None,
                   code: tuple[str, str | None, Sequence[Sequence[str]] | None] | None = None,
                   break_after: bool = True) -> None:
    level = 1 if heading.startswith("CAPITOLUL") or heading in ["INTRODUCERE", "CONCLUZII", "BIBLIOGRAFIE", "ANEXE"] else 2
    doc.add_heading(heading, level=level)
    for text in paragraphs:
        add_para(doc, text)
    if bullets:
        add_bullets(doc, bullets)
    if table:
        headers, rows, widths, caption = table
        add_table(doc, headers, rows, widths)
        if caption:
            add_caption(doc, caption)
    if code:
        snippet, title, explanations = code
        add_code(doc, snippet, title)
        if explanations:
            add_explanation_table(doc, explanations)
    if figure:
        add_figure(doc, figure[0], figure[1])
    if break_after:
        page_break(doc)


def emit_page_block(doc: Document, item) -> None:
    if len(item) == 3 and isinstance(item[2], dict):
        add_page_block(doc, item[0], item[1], **item[2])
    else:
        add_page_block(doc, *item)


def build_content(doc: Document, figs: dict[str, Path]) -> None:
    # Front matter: pages 1-3
    add_cover(doc)
    page_break(doc)
    add_theme_page(doc)
    page_break(doc)
    add_toc_page(doc)
    page_break(doc)

    # Introduction: 4 pages
    intro_pages = [
        ("INTRODUCERE", [
            "Aplicația analizată în această lucrare este un sistem web destinat colectării, afișării și interpretării review-urilor hoteliere. Contextul proiectului este reprezentat de creșterea volumului de feedback digital, în special în domeniul turismului, unde decizia de rezervare este influențată de opiniile altor clienți. Într-un astfel de context, simpla afișare a review-urilor nu mai este suficientă, deoarece utilizatorul trebuie să citească texte multe, eterogene și uneori contradictorii.",
            "Soluția propusă combină o interfață React cu un backend FastAPI și cu modele NLP din familia Transformer. Utilizatorii pot explora hoteluri, pot consulta detalii, pot autentifica o sesiune, pot trimite review-uri, iar sistemul calculează automat sentimentul textului. În plus, aplicația poate genera sumarizări ale review-urilor existente pentru un hotel, folosind modelul T5-small sau o metodă extractivă de rezervă.",
            "Din punct de vedere aplicativ, proiectul se situează la intersecția dintre dezvoltarea web full-stack și procesarea limbajului natural. El demonstrează cum o aplicație obișnuită de gestionare a datelor poate fi îmbogățită cu servicii inteligente, fără a separa complet experiența de utilizare de logica de analiză."
        ]),
        ("Introducere - problema rezolvată și motivația", [
            "Problema principală rezolvată de proiect este interpretarea rapidă a opiniilor clienților despre hoteluri. În absența unei analize automate, un utilizator trebuie să citească manual fiecare review pentru a decide dacă impresia generală despre un hotel este pozitivă, negativă sau neutră. Această operație consumă timp și poate deveni imprecisă atunci când numărul review-urilor crește.",
            "Motivația dezvoltării constă în necesitatea unui instrument care să reducă zgomotul informațional și să scoată la suprafață semnalele relevante. Aplicația nu înlocuiește judecata utilizatorului, ci îi oferă un indicator numeric și textual care simplifică analiza. Modelul DistilBERT este utilizat pentru clasificarea sentimentului, iar scorul rezultat este agregat la nivelul hotelului prin câmpul average_sentiment.",
            "Un alt motiv al dezvoltării este caracterul educațional al proiectului. Codul conține atât concepte backend, precum rute REST, modele Pydantic, sesiuni SQLAlchemy și autentificare JWT, cât și concepte frontend, precum rutare declarativă, context React, componente reutilizabile și adaptare responsive."
        ]),
        ("Introducere - obiective, public țintă și beneficii", [
            "Obiectivul general al aplicației este realizarea unui sistem coerent pentru review-uri hoteliere, în care datele introduse de utilizatori sunt persistate și analizate automat. Obiectivele specifice includ afișarea unei liste de hoteluri, vizualizarea detaliilor unui hotel, crearea de conturi, autentificarea utilizatorilor, trimiterea de review-uri protejate prin token, analiza sentimentului și generarea de sumarizări.",
            "Publicul țintă este format din turiști, persoane interesate de cazare, administratori sau dezvoltatori care doresc să studieze un prototip de aplicație NLP integrată în fluxuri web. Pentru utilizatorul final, beneficiul principal este reducerea timpului de analiză. Pentru dezvoltator, proiectul oferă un exemplu compact de integrare între modele de inteligență artificială și API-uri web.",
            "Beneficiile tehnice includ separarea responsabilităților între frontend și backend, reutilizarea componentelor, date persistente prin SQLite și posibilitatea extinderii către baze de date relaționale mai robuste. Totodată, existența fișierelor de configurare și a scripturilor de seed/migrare facilitează rularea locală și reproducerea mediului de dezvoltare."
        ]),
        ("Introducere - structura lucrării", [
            "Lucrarea este structurată în patru capitole principale, completate de concluzii, bibliografie și anexe. Primul capitol prezintă tehnologiile utilizate, pornind de la limbajele de programare și framework-uri până la bibliotecile NLP, mecanismele de autentificare, baza de date și instrumentele de dezvoltare.",
            "Capitolul al doilea tratează analiza și proiectarea sistemului. Sunt descrise cerințele funcționale și nefuncționale, actorii, arhitectura aplicației, comunicarea între componente, proiectarea bazei de date și proiectarea interfeței. Diagramele inserate explică atât structura statică, cât și fluxurile dinamice.",
            "Capitolul al treilea detaliază implementarea aplicației. Sunt analizate directoarele, modulele backend, modelele, rutele, componentele React, serviciile API, hook-urile și paginile. Capitolul al patrulea descrie testarea, iar concluziile sintetizează rezultatele, dificultățile, limitările și direcțiile de dezvoltare viitoare."
        ]),
    ]
    for title, paras in intro_pages:
        add_page_block(doc, title, paras)

    # Chapter I: 10 pages
    tech_pages = [
        ("CAPITOLUL I. TEHNOLOGII UTILIZATE", [
            "Aplicația este construită pe o arhitectură full-stack modernă. Backend-ul este scris în Python și folosește FastAPI pentru expunerea rutelor REST, SQLAlchemy pentru accesul la baza de date și biblioteci Hugging Face Transformers pentru procesarea textului. Frontend-ul este dezvoltat în React, cu Vite ca instrument de build și dezvoltare.",
            "Alegerea acestor tehnologii urmărește un compromis între expresivitate, performanță și simplitate. FastAPI oferă validare automată prin modele Pydantic și documentație OpenAPI, React facilitează interfețe declarative pe componente, iar SQLite permite persistarea locală a datelor fără configurarea unui server separat.",
            "Figura I.1 marchează structura proiectului și indică separarea clară între directoarele backend și frontend."
        ], {"figure": (figs["project_structure"], "Figura I.1. Structura proiectului și separarea pe backend/frontend.")}),
        ("I.1. Python și FastAPI", [
            "Python este limbajul principal al backend-ului. El este utilizat în fișierele main.py, database.py, models.py, sentiment.py, summarization.py, email_utils.py și scripturile de migrare sau generare de date. Avantajul său major este ecosistemul bogat pentru web, baze de date și procesare de limbaj natural.",
            "FastAPI este framework-ul care definește aplicația HTTP. În main.py, obiectul app este instanțiat cu titlu și versiune, iar rutele sunt declarate prin decoratori precum @app.post sau @app.get. FastAPI folosește tipuri Python și modele Pydantic pentru a valida cererile și a serializa răspunsurile.",
            "Un dezavantaj al acestei alegeri este dependența de runtime-ul Python și de instalarea unor biblioteci mari pentru NLP. Totuși, pentru un proiect de diplomă, avantajele de claritate, documentație automată și integrare rapidă cu modele AI sunt decisive."
        ], {"code": ("""app = FastAPI(title=\"Hotel Review Sentiment Analysis API\", version=\"1.0.0\")\n\napp.add_middleware(\n    CORSMiddleware,\n    allow_origins=[\"*\"],\n    allow_credentials=True,\n    allow_methods=[\"*\"],\n    allow_headers=[\"*\"],\n)""", "Fragment I.1: Inițializarea aplicației FastAPI și CORS.", [
            ("app = FastAPI(...)", "Creează aplicația backend și expune metadatele folosite în documentația OpenAPI."),
            ("CORSMiddleware", "Permite comunicarea frontend-backend în mediul local de dezvoltare."),
            ("allow_origins=['*']", "Este util pentru dezvoltare, dar trebuie restrâns într-o implementare de producție.")
        ])}),
        ("I.2. SQLAlchemy și SQLite", [
            "Baza de date este gestionată prin SQLAlchemy ORM, iar motorul folosit este SQLite. Fișierul database.py definește engine-ul, SessionLocal, Base și clasele User, Hotel și Review. Aceste clase nu sunt simple structuri de date, ci descrieri ORM care se transformă în tabele relaționale.",
            "SQLite este potrivit pentru dezvoltare locală deoarece nu necesită server separat. În proiect există fișierul hotel_reviews.db, iar inspecția acestuia arată tabelele users, hotels și reviews. În starea curentă a bazei de date există 600 hoteluri, 60.009 review-uri și 5 utilizatori, dar lucrarea nu include date personale din rândurile tabelei users.",
            "Avantajul SQLAlchemy constă în faptul că aplicația poate fi extinsă mai ușor către PostgreSQL sau MySQL, lucru anticipat și de database_config.py. Dezavantajul SQLite este scalabilitatea limitată pentru trafic concurent ridicat."
        ], {"table": (["Tabel", "Rol", "Câmpuri principale"], [
            ("users", "Stochează conturile", "id, username, email, hashed_password, created_at"),
            ("hotels", "Stochează unitățile hoteliere", "id, name, location, description, rating, average_sentiment, total_reviews"),
            ("reviews", "Stochează opiniile", "id, hotel_id, reviewer_name, review_text, sentiment_label, sentiment_score, created_at"),
        ], [1700, 2600, 5060], "Tabelul I.1. Entitățile relaționale implementate în SQLite.")}),
        ("I.3. Hugging Face Transformers și modelele NLP", [
            "Componenta de inteligență artificială este implementată cu biblioteca Transformers. În sentiment.py se folosește pipeline-ul sentiment-analysis cu modelul distilbert-base-uncased-finetuned-sst-2-english. Modelul întoarce etichete POSITIVE sau NEGATIVE și o probabilitate asociată.",
            "În summarization.py se încearcă încărcarea modelului t5-small pentru sumarizarea textelor. Dacă modelul nu poate fi încărcat, aplicația trece la o metodă extractivă simplă, bazată pe selectarea propozițiilor cu termeni pozitivi sau negativi. Această strategie de rezervă crește robustețea aplicației în medii unde descărcarea modelului sau memoria sunt problematice.",
            "Avantajul modelelor Transformer este calitatea superioară a reprezentărilor lingvistice. Dezavantajele sunt dimensiunea modelului, timpul de inițializare și dependența de text în limba engleză, deoarece modelul SST-2 este antrenat pentru sentiment binar în engleză."
        ], {"code": ("""self.classifier = pipeline(\n    \"sentiment-analysis\",\n    model=\"distilbert-base-uncased-finetuned-sst-2-english\",\n    return_all_scores=True\n)""", "Fragment I.2: Încărcarea modelului de sentiment.", [
            ("pipeline('sentiment-analysis')", "Construiește un obiect de inferență pentru clasificarea sentimentului."),
            ("model=...", "Selectează modelul DistilBERT fine-tuned pe SST-2."),
            ("return_all_scores=True", "Cere scoruri pentru toate etichetele, pentru alegerea rezultatului cu probabilitate maximă.")
        ])}),
        ("I.4. Autentificare, JWT, Passlib și PyJWT", [
            "Autentificarea este implementată în main.py prin rutele /register, /login și /me. Parolele sunt procesate cu Passlib CryptContext, folosind schema pbkdf2_sha256. Alegerea PBKDF2 este justificată în comentariu prin evitarea problemelor de platformă ale unor wheel-uri bcrypt în mediul de dezvoltare.",
            "După autentificare, backend-ul creează un token JWT semnat cu cheia SECRET_KEY și algoritmul HS256. Tokenul include subiectul, id-ul utilizatorului și data de expirare. Rutele protejate, precum POST /reviews, folosesc OAuth2PasswordBearer și funcția get_current_user pentru a identifica utilizatorul curent.",
            "Avantajul JWT este caracterul stateless: serverul nu trebuie să păstreze sesiuni în memorie. Limitarea proiectului este că cheia implicită change-this-secret este acceptată dacă variabila de mediu lipsește, deci în producție SECRET_KEY trebuie obligatoriu configurată."
        ], {"code": ("""def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):\n    to_encode = data.copy()\n    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))\n    to_encode.update({\"exp\": expire})\n    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)""", "Fragment I.3: Crearea tokenului JWT.", [
            ("data.copy()", "Păstrează informațiile utilizatorului fără a modifica obiectul inițial."),
            ("exp", "Adaugă expirarea tokenului pentru limitarea duratei sesiunii."),
            ("jwt.encode", "Semnează payload-ul cu cheia secretă și algoritmul HS256.")
        ])}),
        ("I.5. Servicii email, variabile de mediu și configurare", [
            "email_utils.py gestionează două tipuri de mesaje: verificarea adresei de email și resetarea parolei. Modulul citește SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, EMAIL_FROM și FRONTEND_URL din variabile de mediu. Dacă SMTP_HOST nu este configurat, mesajele sunt afișate în consolă, ceea ce permite testarea fără infrastructură externă.",
            "Fișierul .env.example descrie valorile așteptate pentru baza de date, modul debug, portul API, modelul de sentiment, directorul de cache și setările de securitate. Lucrarea nu expune fișierul .env real, deoarece acesta poate conține valori sensibile.",
            "Figura I.3 marchează configurațiile importante ale proiectului. Acestea sunt relevante pentru reproducerea mediului și pentru diferențierea între dezvoltare și producție."
        ], {"figure": (figs["config"], "Figura I.2. Marcaj pentru configurațiile principale ale aplicației.")}),
        ("I.6. React, Vite și structura frontend", [
            "React este biblioteca principală pentru interfața utilizator. Aplicația pornește din main.jsx, unde ReactDOM.createRoot montează componenta App. App.jsx definește rutele și integrează AuthProvider, Header și Footer. Vite oferă server de dezvoltare rapid, hot reload și build pentru producție.",
            "Componentizarea React este vizibilă în directoarele pages, components, services și auth. Paginile definesc ecrane complete, în timp ce componentele reutilizabile, precum HotelCard, ReviewForm, SentimentBadge sau Header, encapsulează părți mai mici ale interfeței.",
            "Avantajul React constă în declarativitate și reutilizare. Dezavantajul este complexitatea crescută atunci când apar mai multe straturi de servicii API. În acest proiect există atât un serviciu Axios, cât și adaptoare fetch, ceea ce documentația tratează ca o particularitate de implementare."
        ], {"code": ("""ReactDOM.createRoot(document.getElementById('root')).render(\n  <React.StrictMode>\n    <App />\n  </React.StrictMode>,\n)""", "Fragment I.4: Punctul de intrare al frontend-ului.", [
            ("createRoot", "Inițializează aplicația React în elementul HTML root."),
            ("React.StrictMode", "Activează verificări suplimentare în dezvoltare."),
            ("<App />", "Montează componenta care conține rutarea și layout-ul global.")
        ])}),
        ("I.7. React Router, Axios și adaptoarele fetch", [
            "Navigarea este gestionată cu react-router-dom. App.jsx definește rutele /, /hotels, /hotel/:id, /analyze, /summaries, /profile, /my-reviews, /login, /register, /request-password-reset și /reset-password. Pentru rutele protejate se folosește componenta ProtectedRoute.",
            "api.js creează o instanță Axios cu baseURL http://localhost:8000 și expune servicii pentru hoteluri, review-uri, sentiment, sumarizare și autentificare. În paralel, authApi.js și reviewsApi.js folosesc fetch direct, pentru a controla explicit anteturile Authorization și pentru a trata fallback-uri.",
            "O observație importantă este diferența de nume pentru token în localStorage: api.js folosește access_token, iar AuthProvider/authApi/ReviewForm folosesc token. Această diferență poate produce comportamente inconsistente și este notată în capitolul de limitări."
        ], {"table": (["Serviciu", "Rol", "Observații"], [
            ("hotelService", "GET /hotels și GET /hotels/{id}", "Folosește Axios."),
            ("sentimentService", "POST /analyze", "Folosește Axios."),
            ("summarizationService", "POST /summarize", "Folosește Axios."),
            ("authApi", "login și /me", "Folosește fetch și token localStorage."),
            ("reviewsApi", "fallback-uri pentru review-uri", "Clientul încearcă endpoint-uri care nu toate există în backend."),
        ], [2100, 3000, 4260], "Tabelul I.2. Stratul de comunicare frontend-backend.")}),
        ("I.8. Recharts, CSS și experiența vizuală", [
            "package.json include Recharts, bibliotecă destinată vizualizărilor de date în React. În codul curent nu există însă o diagramă Recharts montată efectiv în paginile analizate; statisticile de sentiment sunt afișate prin carduri numerice. Prin urmare, Recharts este documentat ca dependență disponibilă, nu ca funcționalitate vizuală finalizată.",
            "Stilizarea este realizată prin fișiere CSS: index.css pentru stiluri globale, Home.css pentru pagina principală, Header.css pentru navigația sticky și Footer.css pentru subsol. CSS-ul folosește grid, flexbox, media queries și animații ușoare. Home.css include și regulă prefers-reduced-motion, relevantă pentru accesibilitate.",
            "Interfața include carduri de hotel, badge-uri de sentiment, formulare, mesaje de eroare și succes, statistici și placeholder-e pentru sumarizare. Designul este responsive, iar containerul principal limitează lățimea conținutului la 1200px."
        ], {"figure": (figs["dependencies"], "Figura I.3. Marcaj pentru dependențele frontend și backend.")}),
        ("I.9. Instrumente de dezvoltare, versionare și medii", [
            "Proiectul include setup.sh pentru instalarea dependențelor, DEVELOPMENT.md pentru pașii de rulare și .gitignore pentru excluderea mediilor virtuale, node_modules, fișierelor .env, bazelor de date și modelelor ML. Nu există metadate .git în folderul analizat, așadar documentația nu poate extrage istoric de commit-uri.",
            "Backend-ul se rulează cu Uvicorn, iar frontend-ul cu npm run dev, pe portul 5173 conform vite.config.js. requirements.txt listează FastAPI, Uvicorn, SQLAlchemy, Transformers, Torch, sentencepiece, accelerate, PyJWT, passlib, python-dotenv și faker.",
            "Instrumentele de dezvoltare facilitează separarea mediului local de cel de producție. Totuși, pentru producție ar fi necesare configurarea strictă a CORS, o cheie secretă robustă, migrații controlate și, probabil, o bază de date server-based."
        ]),
    ]
    for item in tech_pages:
        emit_page_block(doc, item)

    # Chapter II: 12 pages
    analysis_pages = [
        ("CAPITOLUL II. ANALIZA ȘI PROIECTAREA SISTEMULUI", [
            "Analiza sistemului pornește de la actorii principali și de la fluxurile pe care codul le implementează efectiv. Sistemul are un vizitator neautentificat, care poate consulta pagina principală, lista de hoteluri, detaliile și pagina About. Utilizatorul autentificat poate accesa în plus analiza sentimentului, sumarizările, profilul, pagina My Reviews și formularul protejat de trimitere a review-urilor.",
            "Din perspectiva backend-ului, actorul este reprezentat prin tokenul JWT trimis în antetul Authorization. Din perspectiva frontend-ului, starea actorului este menținută în AuthProvider, care citește tokenul din localStorage și încearcă să obțină datele utilizatorului prin /me.",
            "Analiza distinge între funcționalități finalizate și extensii începute. De exemplu, clientul conține încercări pentru actualizare și ștergere review-uri, însă backend-ul nu definește rute PATCH, PUT sau DELETE pentru review-uri."
        ], {"figure": (figs["use_case"], "Figura II.1. Diagramă Use Case pentru actorii aplicației.")}),
        ("II.1. Cerințe funcționale", [
            "Cerințele funcționale derivă direct din rutele backend și din paginile frontend. Sistemul trebuie să permită afișarea hotelurilor, afișarea detaliilor unui hotel, înregistrarea conturilor, autentificarea, citirea profilului curent, resetarea parolei, verificarea emailului, crearea unui review, analiza sentimentului unui text și sumarizarea review-urilor unui hotel.",
            "Pentru utilizatorul public, cerința centrală este consultarea informațiilor. Pentru utilizatorul autentificat, cerința centrală este contribuția: scrierea review-ului și folosirea instrumentelor NLP. Pentru sistem, cerința este ca fiecare review creat să declanșeze analiza sentimentului și actualizarea statisticilor hotelului.",
            "Cerințele se reflectă în componentele HotelList, HotelDetail, ReviewForm, SentimentAnalyzer, ReviewSummaryPage, Login, Register, Profile și MyReviews."
        ], {"table": (["ID", "Cerință funcțională", "Implementare"], [
            ("CF1", "Listarea hotelurilor", "GET /hotels + HotelList/HotelCard"),
            ("CF2", "Detalii hotel și review-uri", "GET /hotels/{hotel_id} + HotelDetail"),
            ("CF3", "Autentificare", "POST /login + AuthProvider"),
            ("CF4", "Creare review", "POST /reviews protejat + ReviewForm"),
            ("CF5", "Analiză text", "POST /analyze + SentimentAnalyzer"),
            ("CF6", "Sumarizare review-uri", "POST /summarize + ReviewSummary"),
        ], [1100, 3600, 4660], "Tabelul II.1. Cerințe funcționale corelate cu implementarea.")}),
        ("II.2. Cerințe nefuncționale", [
            "Cerințele nefuncționale vizează performanța, securitatea, mentenabilitatea, portabilitatea și accesibilitatea. Performanța este influențată de inițializarea modelelor NLP, care poate fi costisitoare, dar apelurile ulterioare sunt simple la nivel de API. Pentru sumarizare, codul limitează textul la aproximativ 600 de caractere înainte de inferență, pentru a evita depășirea capacității modelului t5-small.",
            "Securitatea este abordată prin parole hash-uite și tokenuri JWT. Există însă aspecte de îmbunătățit: CORS permite orice origine, cheia implicită poate rămâne slabă dacă nu este configurată, iar email verification are un câmp is_verified în răspuns, dar nu există coloană asociată în modelul User.",
            "Mentenabilitatea este susținută de separarea modulelor, dar ar crește dacă serviciile API frontend ar folosi un singur mecanism de stocare a tokenului și dacă rutele clientului ar fi perfect aliniate cu backend-ul."
        ], {"table": (["Categorie", "Cerință", "Observație"], [
            ("Performanță", "Timp acceptabil pentru listări și review-uri", "Listările folosesc query-uri ORM simple."),
            ("Securitate", "Acces protejat la creare review", "OAuth2PasswordBearer + JWT."),
            ("Disponibilitate", "Fallback pentru email și sumarizare", "Console fallback / extractive fallback."),
            ("Portabilitate", "Rulare locală simplă", "SQLite, Vite, Uvicorn."),
            ("Accesibilitate", "Interfață responsive", "Media queries și reduced motion."),
        ], [1900, 3500, 3960], "Tabelul II.2. Cerințe nefuncționale.")}),
        ("II.3. Arhitectura aplicației", [
            "Arhitectura aplicației este stratificată. Frontend-ul React este responsabil pentru interacțiunea cu utilizatorul și pentru afișarea stărilor. Stratul de servicii comunică prin HTTP cu API-ul FastAPI. Backend-ul validează cererile, accesează baza de date prin SQLAlchemy, apelează modelele NLP și întoarce răspunsuri JSON.",
            "Comunicarea este sincronă prin REST. Nu există WebSocket sau procesare în coadă. Emailurile sunt trimise prin BackgroundTasks, ceea ce decuplează parțial răspunsul HTTP de operația de trimitere. Datele persistente sunt păstrate în SQLite, iar modelele NLP sunt încărcate ca instanțe globale sentiment_analyzer și review_summarizer.",
            "Figura II.2 prezintă componentele principale și relațiile dintre ele."
        ], {"figure": (figs["component"], "Figura II.2. Diagramă Component pentru aplicația full-stack.")}),
        ("II.4. Deployment și comunicare între componente", [
            "În mediul local, frontend-ul rulează pe http://localhost:5173, iar backend-ul pe http://localhost:8000. Vite servește aplicația React și redă interfața în browser. Uvicorn rulează aplicația FastAPI ca server ASGI. SQLite este accesat direct de procesul backend.",
            "Comunicarea între browser și backend se face prin cereri HTTP JSON. Pentru rutele protejate se transmite Authorization: Bearer <token>. Modelele Transformers rulează local pe CPU conform setării device=-1 pentru sumarizare, iar modelul de sentiment este creat prin pipeline.",
            "Serviciul SMTP este opțional. Dacă nu există configurație SMTP, email_utils.py afișează mesajele în consolă. Această decizie este utilă pentru dezvoltare, dar în producție trebuie înlocuită cu un provider real."
        ], {"figure": (figs["deployment"], "Figura II.3. Diagramă Deployment pentru rularea locală a aplicației.")}),
        ("II.5. Architecture Overview", [
            "Privită global, aplicația poate fi descrisă ca o succesiune de responsabilități: interfața colectează intenția utilizatorului, serviciile frontend serializează cererea, API-ul validează datele, modelele de domeniu citesc sau scriu în baza de date, iar modulele NLP atașează interpretarea semantică a textului.",
            "Autentificarea și autorizarea traversează toate straturile. Login.jsx obține tokenul, AuthProvider îl păstrează în stare, ProtectedRoute blochează accesul la rutele private, iar FastAPI verifică tokenul înainte de POST /reviews. În acest fel, aplicația nu se bazează doar pe ascunderea butoanelor în UI, ci verifică și la nivel de server.",
            "Figura II.4 oferă o vedere de ansamblu asupra fluxului arhitectural."
        ], {"figure": (figs["architecture"], "Figura II.4. Architecture Overview pentru sistemul Hotel Reviews.")}),
        ("II.6. Proiectarea bazei de date", [
            "Baza de date are trei entități principale. User reprezintă contul autentificat și conține username unic, email opțional, parolă hash-uită și data creării. Hotel reprezintă unitatea evaluată și conține date descriptive, scor mediu de sentiment și număr total de review-uri. Review reprezintă opinia individuală și are o cheie străină hotel_id către Hotel.",
            "Relația dintre Hotel și Review este una de tip one-to-many: un hotel poate avea mai multe review-uri, iar un review aparține unui singur hotel. În modelul ORM, această relație este exprimată prin relationship('Review', back_populates='hotel') și relationship('Hotel', back_populates='reviews').",
            "În cod există un câmp user_name în Review, dar fluxul de creare folosește reviewer_name și nu leagă review-ul de user_id. Astfel, pagina MyReviews filtrează client-side după nume și folosește un cache local pentru review-urile recente."
        ], {"figure": (figs["erd"], "Figura II.5. ERD complet al bazei de date implementate.")}),
        ("II.7. Relații, chei și cardinalități", [
            "Cheia primară pentru fiecare tabel este id. Tabela users are constrângere de unicitate pe username. Tabela reviews are cheie străină hotel_id către hotels.id. În SQLite, relația este declarată în schema creată de SQLAlchemy, iar în cod accesul la review-uri pentru un hotel se face prin filtrarea Review.hotel_id == hotel_id.",
            "Cardinalitatea principală este Hotel 1 - N Review. Nu există în schema actuală o cardinalitate User 1 - N Review, deoarece Review nu conține user_id. Această absență este importantă pentru proiectare: autentificarea este cerută la creare, dar persistarea nu salvează id-ul utilizatorului în review.",
            "Figura II.6 marchează locul în care captura bazei de date poate fi inserată pentru verificarea vizuală a tabelelor."
        ], {"figure": (figs["database"], "Figura II.6. Marcaj pentru captura bazei de date SQLite.")}),
        ("II.8. Proiectarea interfeței", [
            "Interfața este proiectată în jurul unui header persistent, al unui corp de pagină rutat și al unui footer. Header.jsx afișează brandul, linkurile principale, linkurile către funcționalități NLP și un meniu de profil pentru utilizatorul autentificat. Footer.jsx oferă linkuri și informații de contact.",
            "Pagina Home are rol de intrare și folosește animații ușoare, carduri și un preview vizual. HotelList oferă lista hotelurilor în grid, iar HotelDetail combină informații despre hotel, statistici de sentiment, sumarizare și formularul de review. Pagina SentimentAnalyzer este un instrument separat pentru testarea modelului.",
            "Responsive design-ul este realizat prin media queries. La lățimi reduse, anumite elemente ale headerului sunt ascunse, iar gridurile se transformă în layout pe o singură coloană."
        ], {"figure": (figs["navigation"], "Figura II.7. Diagramă Navigation Flow pentru rutele frontend.")}),
        ("II.9. User Journey", [
            "Parcursul principal al utilizatorului începe în Home, continuă cu lista de hoteluri, selectarea unui hotel și citirea review-urilor. Dacă utilizatorul dorește să contribuie, se autentifică sau creează un cont. După autentificare, poate trimite un review, iar backend-ul calculează automat sentimentul și actualizează scorurile hotelului.",
            "Un parcurs secundar este folosirea instrumentelor NLP fără legare directă de un hotel: SentimentAnalyzer permite testarea oricărui text, iar ReviewSummaryPage poate genera sumarizări pentru hotelurile cu review-uri. Aceste pagini sunt protejate de ProtectedRoute, deci solicită token local.",
            "Figura II.8 prezintă drumul utilizatorului de la intrare până la feedback-ul inteligent generat de sistem."
        ], {"figure": (figs["journey"], "Figura II.8. Diagramă User Journey pentru utilizatorul autentificat.")}),
        ("II.10. Autentificare și autorizare", [
            "Autentificarea se bazează pe username și parolă. La înregistrare, parola este verificată pentru lungime minimă, hash-uită și salvată. La login, parola introdusă este verificată cu hash-ul stocat, iar utilizatorul primește un token. /me decodează tokenul și întoarce datele utilizatorului curent.",
            "Autorizarea este implementată explicit pentru POST /reviews. Funcția get_current_user decodează tokenul, caută utilizatorul în baza de date și oprește fluxul prin HTTPException dacă utilizatorul nu există sau tokenul este invalid. Frontend-ul are și o protecție de rută, însă protecția reală rămâne cea de server.",
            "Verificarea emailului și resetarea parolei folosesc tokenuri JWT cu tipuri diferite: verify și password_reset. Această separare previne folosirea unui token de resetare pentru verificare sau invers."
        ], {"figure": (figs["seq_auth"], "Figura II.9. Diagramă Sequence pentru autentificare.")}),
        ("II.11. Fluxul operațiilor CRUD", [
            "În codul curent, operația complet implementată pentru review-uri este crearea. Formularul trimite hotel_id, reviewer_name și review_text. Backend-ul verifică hotelul, obține utilizatorul curent, rulează analiza sentimentului, creează review-ul și actualizează media sentimentului pentru hotel.",
            "Citirea review-urilor se face prin GET /hotels/{hotel_id}, care întoarce hotelul împreună cu lista review-urilor asociate. Nu există endpoint public GET /reviews în backend, deși MyReviews și reviewsApi încearcă mai multe variante. Nu există nici update sau delete implementat pe server.",
            "Această diferență este importantă pentru evaluare: aplicația are CRUD parțial pentru entitatea Review, nu CRUD complet. Figura II.10 reflectă fluxul real al operației create."
        ], {"figure": (figs["seq_crud"], "Figura II.10. Diagramă Sequence pentru operația de creare review.")}),
        ("II.12. Activitate și stări relevante", [
            "Fluxul principal al aplicației combină activități UI, apeluri API și actualizări de date. Utilizatorul selectează un hotel, completează formularul, iar sistemul validează datele la client și la server. Dacă tokenul lipsește sau hotelul nu există, se întoarce eroare. Dacă modelul NLP eșuează, se întoarce eroare 500 sau se folosește fallback în cazul sumarizării.",
            "Pentru review, stările relevante sunt formular gol, date validate, cerere trimisă, analiză sentiment, persistare, actualizare UI sau eroare. Această modelare ajută la identificarea testelor: câmpuri goale, utilizator neautentificat, hotel invalid, text valid și răspuns NLP.",
            "Figurile II.11 și II.12 sintetizează activitatea principală și starea review-ului."
        ], {"figure": (figs["activity"], "Figura II.11. Diagramă Activity pentru fluxul principal.")}),
    ]
    for item in analysis_pages:
        emit_page_block(doc, item)

    # Add state figure as a compact continuation page before implementation.
    add_page_block(doc, "II.13. State Machine pentru review", [
        "Starea review-ului este relevantă deoarece formularul este punctul în care datele introduse de utilizator intră în sistem. Înainte de trimitere, aplicația verifică existența numelui și a textului. După trimitere, serverul verifică autentificarea, hotelul și rezultatul modelului de sentiment.",
        "Dacă toate condițiile sunt îndeplinite, review-ul este persistat, iar HotelDetail se reîncarcă pentru a afișa scorurile actualizate. Dacă apare o eroare, ReviewForm afișează un mesaj explicit, de exemplu mesajul pentru lipsa autentificării."
    ], figure=(figs["state"], "Figura II.12. Diagramă State Machine pentru entitatea Review."))

    # Chapter III: 20 pages
    impl_pages = [
        ("CAPITOLUL III. IMPLEMENTAREA APLICAȚIEI", [
            "Implementarea este împărțită în două zone majore: backend și frontend. Backend-ul conține aplicația FastAPI, modelele ORM, logica de acces la date, analiza sentimentului, sumarizarea, utilitarele email și scripturile pentru date. Frontend-ul conține aplicația React, paginile, componentele, serviciile API, contextul de autentificare și stilurile.",
            "Structura directoarelor susține separarea responsabilităților. backend/main.py este punctul central pentru rute, dar delegă lucrul cu hoteluri și review-uri către models.py, configurarea bazei către database.py și procesarea NLP către sentiment.py și summarization.py.",
            "Pe partea frontend, App.jsx orchestrează rutele, Header.jsx și Footer.jsx asigură layout-ul comun, iar paginile gestionează fluxurile majore."
        ]),
        ("III.1. Structura directoarelor și fișiere importante", [
            "Directorul backend include main.py, models.py, database.py, database_config.py, sentiment.py, summarization.py, email_utils.py, migrations.py, seed_data.py, check_dependencies.py, requirements.txt și data/hotels.json. Fiecare fișier are o responsabilitate clară, deși unele date de seed sunt duplicate între models.py, database_config.py și migrations.py.",
            "Directorul frontend include index.html, package.json, vite.config.js și src. În src se găsesc App.jsx, main.jsx, index.css, auth/AuthProvider.jsx, services și directoarele pages/components. Logo-ul este în src/assets/logo.png.",
            "Marcajele de captură pentru Login, Register, Dashboard, Profil, Formular, Administrare date, Setări, Detalii și Flux complet sunt plasate în secțiunile relevante ale capitolului."
        ], {"table": (["Zonă", "Fișiere", "Responsabilitate"], [
            ("Backend API", "main.py", "Rute, autentificare, validare, răspunsuri."),
            ("Backend date", "database.py, models.py", "Schema ORM și operații pe entități."),
            ("Backend NLP", "sentiment.py, summarization.py", "Clasificare sentiment și sumarizare."),
            ("Frontend rutare", "App.jsx, main.jsx", "Montare aplicație și rute."),
            ("Frontend UI", "pages, components, CSS", "Ecrane, componente și stilizare."),
        ], [1900, 3000, 4460], "Tabelul III.1. Structura logică a proiectului.")}),
        ("III.2. Modele Pydantic și contracte API", [
            "În main.py sunt definite clase Pydantic pentru cereri și răspunsuri: RegisterRequest, LoginRequest, TokenResponse, UserResponse, SentimentAnalysisRequest, SentimentAnalysisResponse, ReviewCreateRequest, ReviewResponse, HotelResponse, HotelDetailResponse, SummarizationRequest și SummarizationResponse.",
            "Aceste clase asigură contractul dintre frontend și backend. De exemplu, ReviewCreateRequest cere hotel_id și review_text, iar reviewer_name este opțional. ReviewResponse include id, hotel_id, reviewer_name, review_text, sentiment_label, sentiment_score și created_at.",
            "Avantajul Pydantic este validarea automată a tipurilor și generarea schemelor OpenAPI. Totuși, unele validări de conținut, precum lungimea minimă a textului review-ului, sunt realizate manual în endpoint sau în UI, nu prin constrângeri Pydantic explicite."
        ], {"code": ("""class ReviewCreateRequest(BaseModel):\n    hotel_id: int\n    reviewer_name: Optional[str] = None\n    review_text: str\n\nclass ReviewResponse(BaseModel):\n    id: int\n    hotel_id: int\n    reviewer_name: str\n    review_text: str\n    sentiment_label: str\n    sentiment_score: float\n    created_at: str""", "Fragment III.1: Contractul Pydantic pentru review-uri.", [
            ("hotel_id", "Identifică hotelul pentru care se creează review-ul."),
            ("reviewer_name", "Este opțional, iar backend-ul poate folosi username-ul utilizatorului curent."),
            ("sentiment_label/score", "Sunt completate de backend după analiza NLP.")
        ])}),
        ("III.3. Înregistrare și autentificare", [
            "Endpoint-ul /register verifică existența username-ului, hash-uiește parola și creează un User. Dacă emailul este prezent, se generează un token de verificare și se trimite email în background. Endpoint-ul /login verifică parola și întoarce access_token. Endpoint-ul /me decodează tokenul și întoarce datele utilizatorului.",
            "Frontend-ul are pagina Login.jsx, care apelează authApi.login, salvează tokenul în localStorage și redirecționează către /. Register.jsx apelează authService.register și, după succes, navighează către login.",
            "Figura III.1 și Figura III.2 sunt marcaje pentru capturile de ecran ale celor două pagini."
        ], {"figure": (figs["login"], "Figura III.1. Marcaj pentru pagina Login.")}),
        ("III.4. Pagina de înregistrare și verificare email", [
            "Pagina Register are un formular cu username, email opțional și parolă. Ea verifică local existența username-ului și parolei, apoi trimite datele către authService.register. Backend-ul creează utilizatorul și trimite email de verificare dacă adresa este furnizată.",
            "Fluxul de verificare email este definit prin GET /verify-email?token=..., unde tokenul trebuie să aibă type='verify'. În modelul User nu există coloană is_verified, deși răspunsul UserResponse include is_verified opțional. Din acest motiv, verificarea este mai degrabă un flux pregătit decât o proprietate persistentă completă.",
            "Această observație este importantă pentru documentarea onestă a sistemului: codul include intenția funcționalității, dar schema bazei de date nu o finalizează."
        ], {"figure": (figs["register"], "Figura III.2. Marcaj pentru pagina Înregistrare.")}),
        ("III.5. Resetarea parolei", [
            "RequestPasswordReset.jsx permite introducerea unui username sau email. Backend-ul caută utilizatorul și, pentru a evita enumerarea conturilor, întoarce același mesaj indiferent dacă utilizatorul există. Dacă există și are email, trimite un token de resetare valabil o oră.",
            "ResetPassword.jsx citește tokenul din query string, validează local lungimea parolei și confirmarea, apoi apelează authService.resetPassword. Backend-ul verifică type='password_reset', caută utilizatorul și actualizează hashed_password.",
            "Această funcționalitate demonstrează utilizarea JWT pentru acțiuni temporare, nu doar pentru sesiuni de autentificare."
        ], {"code": ("""@app.post(\"/request-password-reset\")\ndef request_password_reset(request: PasswordResetRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):\n    uoe = request.username_or_email.strip()\n    user = db.query(User).filter((User.username == uoe) | (User.email == uoe)).first()\n    if user and getattr(user, \"email\", None):\n        token = create_access_token({\"sub\": user.username, \"type\": \"password_reset\"}, expires_delta=timedelta(hours=1))\n        background_tasks.add_task(send_password_reset_email, user.email, user.username, token)\n    return {\"detail\": \"If an account exists with that email/username, a password reset link has been sent.\"}""", "Fragment III.2: Cererea de resetare a parolei.", [
            ("username_or_email.strip()", "Normalizează valoarea introdusă de utilizator."),
            ("filter(... | ...)", "Permite identificarea contului după username sau email."),
            ("mesaj constant", "Reduce riscul de enumerare a utilizatorilor.")
        ])}),
        ("III.6. Modelele ORM User, Hotel și Review", [
            "database.py definește cele trei clase ORM. User are id, username, email, hashed_password și created_at. Hotel are câmpuri descriptive și statistice, inclusiv average_sentiment și total_reviews. Review are hotel_id, reviewer_name, review_text, sentiment_label, sentiment_score și created_at.",
            "Relația Hotel-Review este bidirecțională prin relationship. În momentul creării unui review, models.create_review calculează noua medie de sentiment folosind vechea medie, numărul existent de review-uri și scorul nou.",
            "Figura III.3 prezintă diagrama de clasă, iar codul de mai jos explică structura ORM."
        ], {"figure": (figs["class"], "Figura III.3. Diagramă Class pentru entități și servicii NLP.")}),
        ("III.7. Funcțiile de acces la date din models.py", [
            "models.py conține funcțiile get_hotels, get_hotel, create_hotel, create_review, get_hotel_reviews, get_hotel_by_name și seed_sample_hotels. Aceste funcții izolează interogările și actualizările, astfel încât main.py nu manipulează direct toate detaliile ORM.",
            "create_review este funcția cu cel mai mare impact deoarece persistă review-ul și actualizează câmpurile statistice ale hotelului. Formula folosită păstrează media fără recalcularea tuturor review-urilor, ceea ce este eficient pentru adăugări succesive.",
            "Limitarea formulei este că ea presupune că total_reviews și average_sentiment sunt corecte înainte de adăugare. Dacă baza de date ar fi modificată manual, statisticile ar putea necesita recalculare."
        ], {"code": ("""total_score = hotel.average_sentiment * hotel.total_reviews\ntotal_score += sentiment_score\nhotel.total_reviews += 1\nhotel.average_sentiment = total_score / hotel.total_reviews""", "Fragment III.3: Actualizarea incrementală a mediei de sentiment.", [
            ("total_score inițial", "Reconstruiește suma veche pornind de la medie și număr."),
            ("sentiment_score", "Adaugă scorul review-ului nou."),
            ("împărțire finală", "Calculează media actualizată după incrementarea numărului de review-uri.")
        ])}),
        ("III.8. Analiza sentimentului", [
            "SentimentAnalyzer încearcă să încarce pipeline-ul Transformers la inițializare. Dacă încărcarea eșuează, classifier devine None, iar analyze_sentiment întoarce etichetă NEUTRAL, scor 0.5, confidence 0.0 și mesaj de eroare. Această abordare previne blocarea completă a aplicației.",
            "Când modelul funcționează, rezultatele sunt parcurse pentru a alege eticheta cu scor maxim. Codul mapează POSITIVE și NEGATIVE către etichetele interne și transformă probabilitatea într-un scor pe intervalul 0-1, unde 0.5 este neutru.",
            "În cazul pozitiv, scorul este 0.5 + confidence * 0.5; în cazul negativ, 0.5 - confidence * 0.5. Astfel, scorurile apropiate de 1 reprezintă opinii pozitive puternice, iar scorurile apropiate de 0 opinii negative puternice."
        ], {"code": ("""if sentiment_label == \"POSITIVE\":\n    score = 0.5 + (confidence * 0.5)\nelif sentiment_label == \"NEGATIVE\":\n    score = 0.5 - (confidence * 0.5)\nelse:\n    score = 0.5""", "Fragment III.4: Conversia probabilității modelului în scor intern.", [
            ("POSITIVE", "Mută scorul în intervalul 0.5-1.0."),
            ("NEGATIVE", "Mută scorul în intervalul 0.0-0.5."),
            ("NEUTRAL", "Păstrează centrul scalei, deși modelul folosit este binar.")
        ])}),
        ("III.9. Sumarizarea review-urilor", [
            "ReviewSummarizer încearcă încărcarea modelului t5-small prin pipeline('summarization'). Pentru compatibilitate, device=-1 forțează CPU. Dacă modelul nu se încarcă, modulul folosește sumarizare extractivă, selectând propoziții reprezentative pe baza unor indicatori lexicali.",
            "_preprocess_reviews filtrează review-urile scurte, normalizează spațiile și trunchiază textul combinat la 600 de caractere. Această limită este conservatoare și reduce riscul de depășire a ferestrei modelului sau de timp mare de inferență.",
            "Endpoint-ul /summarize acceptă hotel_id sau hotel_name. Dacă nu există review-uri, răspunsul precizează că nu sunt disponibile opinii pentru hotel."
        ], {"code": ("""summary_result = self.summarizer(\n    combined_text,\n    max_length=max_length,\n    min_length=min_length,\n    do_sample=False,\n    clean_up_tokenization_spaces=True\n)""", "Fragment III.5: Apelul modelului de sumarizare.", [
            ("combined_text", "Conține review-urile curățate și concatenate."),
            ("max_length/min_length", "Controlează lungimea rezumatului generat."),
            ("do_sample=False", "Face generarea deterministă pentru rezultate mai stabile.")
        ])}),
        ("III.10. Rutele publice și protejate", [
            "Rutele publice includ /, /hotels, /hotels/{hotel_id}, /analyze, /summarize, /register, /login, /request-password-reset, /reset-password și /verify-email. Dintre acestea, /analyze și /summarize sunt protejate doar la nivel de frontend prin ProtectedRoute, nu prin token la server.",
            "Ruta POST /reviews este protejată la server prin Depends(get_current_user). Această rută verifică hotelul, stabilește reviewer_name, rulează sentiment_analyzer și apelează create_review.",
            "Rutele lipsă față de unele încercări frontend sunt GET /reviews, GET /my-reviews, GET /users/{id}/reviews, PATCH/PUT /reviews/{id} și DELETE /reviews/{id}. Acestea sunt candidate pentru dezvoltări viitoare."
        ], {"table": (["Metodă", "Endpoint", "Status implementare"], [
            ("GET", "/", "Implementat - health/root message"),
            ("GET", "/hotels", "Implementat - listare hoteluri"),
            ("GET", "/hotels/{hotel_id}", "Implementat - detalii + review-uri"),
            ("POST", "/reviews", "Implementat și protejat"),
            ("POST", "/analyze", "Implementat"),
            ("POST", "/summarize", "Implementat"),
            ("PATCH/DELETE", "/reviews/{id}", "Nu este implementat în backend"),
        ], [1300, 3000, 5060], "Tabelul III.2. Rute API și acoperire.")}),
        ("III.11. App.jsx și rutarea frontend", [
            "App.jsx învelește aplicația în AuthProvider și Router. Header apare înaintea conținutului rutat, Footer după conținut, iar main ocupă spațiul flexibil disponibil. Rutele /analyze, /summaries, /profile și /my-reviews sunt învelite în ProtectedRoute.",
            "Această structură face ca paginile publice să fie disponibile fără token, în timp ce instrumentele avansate cer autentificare. Totuși, pentru /analyze și /summarize, backend-ul nu cere token, deci protecția este doar client-side.",
            "Navigation.jsx există în directorul components, dar nu este montat în App.jsx. Navigația activă este Header.jsx, care include brand, linkuri și meniu de profil."
        ], {"code": ("""<Route\n  path=\"/analyze\"\n  element={\n    <ProtectedRoute>\n      <SentimentAnalyzer />\n    </ProtectedRoute>\n  }\n/>""", "Fragment III.6: Protejarea unei rute React.", [
            ("path='/analyze'", "Definește ruta pentru instrumentul de analiză."),
            ("ProtectedRoute", "Verifică existența tokenului în contextul de autentificare."),
            ("SentimentAnalyzer", "Este redat doar dacă utilizatorul trece verificarea client-side.")
        ])}),
        ("III.12. AuthProvider și starea sesiunii", [
            "AuthProvider este un context React care păstrează token, user și loading. La încărcare, citește tokenul și userul din localStorage. Dacă există token, apelează authApi.me(token) pentru a obține datele curente ale utilizatorului.",
            "Funcția login apelează authApi.login, extrage access_token sau token, îl salvează în localStorage sub cheia token și actualizează starea. Funcția logout șterge tokenul și userul. refreshUser permite reîncărcarea manuală a datelor de profil.",
            "Această componentă este critică pentru toate rutele private. În cazul în care tokenul expiră sau /me eșuează, user devine null, iar aplicația pierde sesiunea vizuală."
        ], {"code": ("""const [token, setToken] = useState(() => {\n  try { return localStorage.getItem(\"token\") || null; } catch { return null; }\n});\n\nuseEffect(() => {\n  if (!token) { setUser(null); setLoading(false); return; }\n  authApi.me(token).then(setUser).finally(() => setLoading(false));\n}, [token]);""", "Fragment III.7: Persistența tokenului în AuthProvider.", [
            ("useState inițial", "Reface sesiunea după refresh-ul browserului."),
            ("if (!token)", "Tratează cazul utilizatorului neautentificat."),
            ("authApi.me(token)", "Validează tokenul și încarcă profilul de la backend.")
        ])}),
        ("III.13. Header, Footer și navigație", [
            "Header.jsx construiește navigația principală. Componenta afișează logo-ul din assets, linkurile Hotels și About, linkurile funcționale Review Summaries și Sentiment Analyzer, plus acțiuni de autentificare. Dacă user există, afișează un buton de profil cu inițiale și un meniu dropdown.",
            "Meniul se închide la click în afara sa printr-un listener document.addEventListener('mousedown', onDocClick). Această interacțiune îmbunătățește experiența utilizatorului, deoarece dropdown-ul nu rămâne blocat pe ecran.",
            "Footer.jsx oferă linkuri către About, Hotels, Summaries, Analyze, Privacy și Terms. Ultimele două rute nu sunt definite în App.jsx, deci ele trebuie fie implementate, fie eliminate pentru consistență."
        ], {"figure": (figs["profile"], "Figura III.4. Marcaj pentru pagina Profil Utilizator și meniul asociat.")}),
        ("III.14. Home, About și pagini publice", [
            "Home.jsx este pagina de intrare. Ea folosește o stare loaded pentru a declanșa animații după montare și conține secțiuni de tip hero, beneficii și CTA. Home.css controlează layout-ul responsive, animațiile și prevenirea overflow-ului orizontal.",
            "About.jsx descrie proiectul ca lucrare de licență și enumeră funcționalități generale: colectarea review-urilor, sumarizarea opiniilor și scoruri de sentiment. Textul About este orientativ și menționează că backend-ul este FastAPI/Python, frontend-ul React/Vite și autentificarea JWT.",
            "Aceste pagini creează contextul aplicației și oferă acces către fluxurile principale, dar nu manipulează date complexe."
        ], {"figure": (figs["dashboard"], "Figura III.5. Marcaj pentru Dashboard / lista hotelurilor.")}),
        ("III.15. HotelList și HotelCard", [
            "HotelList.jsx folosește useEffect pentru a apela hotelService.getAllHotels la montarea componentei. Stările locale hotels, loading și error controlează afișarea. Dacă datele sunt încărcate, se afișează un grid de HotelCard.",
            "HotelCard primește un obiect hotel, afișează numele, locația, descrierea, un SentimentBadge și numărul de review-uri. La click, folosește useNavigate pentru a deschide /hotel/{id}. Sentimentul general este calculat local: peste 0.6 pozitiv, sub 0.4 negativ, altfel neutru.",
            "Această componentă este un exemplu de reutilizare UI: cardul nu face cereri API și nu cunoaște detaliile backend-ului, ci doar prezintă datele primite."
        ], {"code": ("""const getOverallSentiment = (score) => {\n  if (score > 0.6) return 'POSITIVE';\n  if (score < 0.4) return 'NEGATIVE';\n  return 'NEUTRAL';\n};""", "Fragment III.8: Pragurile UI pentru sentimentul hotelului.", [
            ("> 0.6", "Consideră scorul suficient de pozitiv pentru badge verde."),
            ("< 0.4", "Consideră scorul negativ pentru badge roșu."),
            ("altfel", "Încadrează zona intermediară ca neutră.")
        ])}),
        ("III.16. HotelDetail, statistici și ReviewSummary", [
            "HotelDetail.jsx folosește useParams pentru a citi id-ul hotelului și apelează hotelService.getHotelById. Pagina afișează informații despre hotel, SentimentBadge pentru scorul mediu, statistici pozitive/neutre/negative, componenta ReviewSummary, formularul ReviewForm și lista ReviewItem.",
            "getSentimentStats parcurge review-urile și le clasifică după sentiment_score. ReviewSummary poate genera un rezumat pentru hotel, afișând total_reviews, processed_reviews și model_used. Această componentă este ascunsă dacă totalReviews este zero.",
            "Figura III.6 marchează ecranul de detalii hotel, unde se concentrează cele mai multe interacțiuni ale utilizatorului."
        ], {"figure": (figs["details"], "Figura III.6. Marcaj pentru Vizualizare Detalii Hotel.")}),
        ("III.17. ReviewForm și ReviewItem", [
            "ReviewForm este componenta care trimite date către POST /reviews. Ea construiește payload-ul cu hotel_id, reviewer_name și review_text, citește tokenul din localStorage și îl trimite în antetul Authorization. Dacă răspunsul este 401, afișează mesajul că utilizatorul trebuie să se autentifice.",
            "După succes, componenta golește textul, apelează onReviewAdded, emite un eveniment review:created și salvează review-ul recent într-un cache local per utilizator. ReviewItem afișează reviewer_name, review_text, data formatată și SentimentBadge.",
            "Această implementare oferă feedback rapid în UI, dar nu înlocuiește necesitatea unui endpoint server-side pentru listarea review-urilor utilizatorului."
        ], {"figure": (figs["add_review"], "Figura III.7. Marcaj pentru Formular Adăugare Review.")}),
        ("III.18. SentimentAnalyzer", [
            "SentimentAnalyzer.jsx este un instrument de testare a modelului. Componenta are stări pentru text, result, loading și error. La submit, verifică textul gol, apelează sentimentService.analyzeSentiment și afișează eticheta, confidence și score.",
            "Pagina include texte de probă pozitive, negative și mixte, care pot fi copiate în textarea prin apăsarea unui buton. Rezultatul este afișat într-un card intern cu SentimentBadge și explicația pragurilor.",
            "Funcționalitatea este utilă pentru validarea manuală a modelului și pentru demonstrarea diferenței dintre confidence și sentiment_score."
        ], {"code": ("""const data = await sentimentService.analyzeSentiment(text.trim());\nsetResult(data);""", "Fragment III.9: Apelul frontend pentru analiza sentimentului.", [
            ("text.trim()", "Elimină spațiile inutile înainte de trimitere."),
            ("analyzeSentiment", "Trimite POST /analyze cu payload { text }."),
            ("setResult", "Declanșează redarea cardului de rezultat.")
        ])}),
        ("III.19. ReviewSummaryPage", [
            "ReviewSummaryPage afișează hotelurile cu total_reviews mai mare decât zero și permite generarea rezumatelor individuale sau în serie. generateAllSummaries parcurge hotelurile și introduce o pauză de o secundă între cereri, pentru a evita aglomerarea modelului.",
            "Pentru fiecare hotel, pagina afișează nume, locație, numărul de review-uri și scorul mediu. Dacă rezumatul există, se afișează textul, numărul de review-uri procesate și modelul folosit. Dacă generarea eșuează, se salvează un mesaj de eroare în starea summaries.",
            "Această pagină demonstrează o integrare NLP de nivel agregat, diferită de analiza pe text individual."
        ], {"figure": (figs["data_admin"], "Figura III.8. Marcaj pentru Administrare Date / sumarizări și date persistente.")}),
        ("III.20. Profile, MyReviews și limitări client-server", [
            "Profile.jsx afișează datele utilizatorului curent din AuthProvider: username, id, email și member since. Componenta include un link /profile/edit, dar această rută nu există în App.jsx și nu are endpoint backend asociat. Prin urmare, editarea profilului este doar o intenție UI.",
            "MyReviews.jsx încearcă mai multe endpoint-uri: /users/{id}/reviews, /reviews?user_id=..., /my-reviews și /reviews. Backend-ul nu implementează aceste rute, deci componenta se bazează pe fallback-uri și pe review-urile recente salvate în localStorage. Dacă primește o listă generală, încearcă filtrarea după numele utilizatorului.",
            "Această secțiune marchează clar limitele aplicației curente și propune extinderea cu user_id în Review și rute server-side pentru listare, editare și ștergere."
        ], {"figure": (figs["settings"], "Figura III.9. Marcaj pentru Setări / configurări viitoare.")}),
        ("III.21. Flux complet și tratarea erorilor", [
            "Fluxul complet de utilizare combină Home, Hotels, HotelDetail, Login/Register, ReviewForm, backend NLP și actualizarea statisticilor. Erorile sunt tratate în fiecare zonă: backend-ul folosește HTTPException, iar frontend-ul afișează mesaje în componentele error sau success.",
            "În HotelList și HotelDetail, erorile de încărcare sunt afișate prin mesaje simple. În ReviewForm, erorile 401 sunt interpretate explicit. În AuthProvider, eșecul /me duce la curățarea userului, dar tokenul poate rămâne dacă nu se decide ștergerea lui.",
            "Figura III.10 marchează locul pentru captura fluxului complet de utilizare."
        ], {"figure": (figs["full_flow"], "Figura III.10. Marcaj pentru fluxul complet de utilizare.")}),
    ]
    for item in impl_pages:
        emit_page_block(doc, item)

    # Chapter IV: 5 pages
    test_pages = [
        ("CAPITOLUL IV. TESTAREA APLICAȚIEI", [
            "Testarea aplicației trebuie să acopere backend-ul, frontend-ul, validarea datelor, securitatea de bază, performanța și scenariile de eroare. În codul analizat nu există un director de teste automatizate, deci metodologia propusă combină testare manuală, apeluri API și verificări funcționale în browser.",
            "Pentru backend, testarea se poate realiza prin documentația OpenAPI generată de FastAPI sau prin curl/Postman. Pentru frontend, se verifică navigarea între rute, stările de loading, formularele, mesajele de eroare și actualizarea datelor după acțiuni.",
            "Pentru modelele NLP, testarea trebuie să includă texte pozitive, negative și neutre/mixte, observând eticheta, confidence și scorul intern."
        ], {"table": (["Nivel", "Obiectiv", "Metodă"], [
            ("API", "Validarea rutelor și codurilor HTTP", "Swagger/curl/Postman"),
            ("UI", "Navigare și formulare", "Testare manuală în browser"),
            ("Date", "Persistență și agregări", "Verificare SQLite/API"),
            ("Securitate", "Token și parole", "Teste login, /me, POST /reviews"),
            ("NLP", "Clasificare și sumarizare", "Texte de probă și review-uri reale"),
        ], [1600, 3500, 4260], "Tabelul IV.1. Metodologia de testare.")}),
        ("IV.1. Testare funcțională", [
            "Testele funcționale urmăresc ca fiecare cerință principală să producă rezultatul așteptat. Listarea hotelurilor trebuie să întoarcă elemente cu id, name, location, description, average_sentiment și total_reviews. Detaliile hotelului trebuie să includă lista de review-uri.",
            "Crearea review-ului trebuie testată cu utilizator autentificat și hotel valid. Rezultatul așteptat este un ReviewResponse cu etichetă de sentiment și scor numeric. După creare, total_reviews și average_sentiment ale hotelului trebuie să se actualizeze.",
            "Testarea sumarizării trebuie să includă hoteluri cu review-uri și hoteluri fără review-uri, pentru a confirma răspunsul special No reviews available."
        ], {"table": (["Caz de test", "Pași", "Rezultat așteptat", "Rezultat obținut"], [
            ("Listare hoteluri", "GET /hotels", "Listă JSON cu hoteluri", "De completat după rulare"),
            ("Detalii hotel", "GET /hotels/1", "Hotel + reviews[]", "De completat după rulare"),
            ("Analiză sentiment", "POST /analyze cu text pozitiv", "label POSITIVE și score > 0.5", "De completat după rulare"),
            ("Creare review", "Login, apoi POST /reviews", "Review salvat și scor actualizat", "De completat după rulare"),
        ], [1700, 3000, 3100, 1560], "Tabelul IV.2. Cazuri de test funcționale.")}),
        ("IV.2. Testare UI și validare date", [
            "Testarea UI verifică dacă paginile se încarcă, dacă butoanele declanșează acțiunile corecte și dacă mesajele de eroare sunt vizibile. Login trebuie testat cu parolă greșită și parolă corectă. Register trebuie testat cu username lipsă, parolă lipsă, username duplicat și cont valid.",
            "ReviewForm validează local câmpurile reviewer_name și review_text. SentimentAnalyzer validează textul gol. ResetPassword validează lungimea parolei și confirmarea. Aceste validări client-side trebuie dublate de verificări backend pentru câmpurile critice.",
            "Figurile IV.1-IV.3 marchează capturi pentru testarea autentificării, funcționalității principale și validării."
        ], {"figure": (figs["test_auth"], "Figura IV.1. Marcaj pentru test autentificare.")}),
        ("IV.3. Testare securitate și scenarii negative", [
            "Testele de securitate de bază includ accesarea /me fără token, trimiterea POST /reviews fără token, folosirea unui token expirat și resetarea parolei cu token de tip greșit. Rezultatele așteptate sunt coduri 401 sau 400, în funcție de situație.",
            "Un alt test este verificarea CORS. În dezvoltare, allow_origins este setat la '*', deci orice origine este permisă. Pentru producție, testarea trebuie reluată după restrângerea originilor la domeniile aplicației.",
            "Parolele trebuie testate pentru lungime minimă. Codul impune minim 6 caractere și tratează defensiv parolele peste 72 de bytes, pentru compatibilitate cu istoricul bcrypt, deși schema folosită este pbkdf2_sha256."
        ], {"figure": (figs["test_validation"], "Figura IV.2. Marcaj pentru test validare date.")}),
        ("IV.4. Testare performanță și robustețe NLP", [
            "Performanța aplicației este influențată de două zone: accesul la baza de date și inferența NLP. Query-urile pentru hoteluri sunt simple, dar baza curentă conține zeci de mii de review-uri, deci paginarea și indexarea devin importante pentru extinderi. Endpoint-ul /hotels acceptă skip și limit, însă frontend-ul cere lista completă implicită.",
            "Pentru sentiment, testele trebuie să măsoare timpul primei cereri după pornirea backend-ului și timpul cererilor ulterioare. Pentru sumarizare, trebuie testate hoteluri cu multe review-uri și verificat fallback-ul dacă modelul nu se poate încărca.",
            "Figura IV.3 marchează captura pentru testarea funcționalității principale în flux complet."
        ], {"figure": (figs["test_main"], "Figura IV.3. Marcaj pentru test funcționalitate principală.")}),
    ]
    for item in test_pages:
        emit_page_block(doc, item)

    # Conclusions: 3 pages
    conclusions = [
        ("CONCLUZII", [
            "Proiectul realizat demonstrează dezvoltarea unei aplicații full-stack care integrează procesarea limbajului natural în fluxuri web reale. Rezultatul principal este un sistem care permite explorarea hotelurilor, autentificarea utilizatorilor, introducerea review-urilor și obținerea automată a sentimentului și sumarizărilor.",
            "Din punct de vedere tehnic, aplicația utilizează tehnologii moderne și relevante: FastAPI pentru backend, SQLAlchemy și SQLite pentru date, Hugging Face Transformers pentru NLP, React și Vite pentru frontend, JWT pentru autentificare și CSS responsive pentru interfață.",
            "Un rezultat important este legarea directă dintre review-ul introdus și actualizarea scorului agregat al hotelului. Această integrare transformă feedback-ul textual într-o informație numerică utilă pentru decizie."
        ]),
        ("Concluzii - dificultăți și soluții implementate", [
            "Dificultățile principale apar din integrarea modelelor NLP în aplicația web. Modelele sunt mari, pot necesita cache și pot eșua la încărcare dacă mediul nu are resurse suficiente. Pentru sumarizare, proiectul implementează o soluție de rezervă extractivă, iar pentru sentiment returnează un rezultat neutru cu eroare dacă modelul nu se încarcă.",
            "O altă dificultate este alinierea completă a frontend-ului cu backend-ul. Unele componente client încearcă endpoint-uri care nu există încă, precum rute pentru review-urile utilizatorului sau editarea profilului. Documentarea acestor diferențe este importantă pentru evoluția proiectului.",
            "Pe zona de securitate, soluția implementată include hashing de parole, tokenuri JWT, expirare și separarea tokenurilor pentru verificare email și resetare parolă. Pentru producție sunt necesare întăriri suplimentare."
        ]),
        ("Concluzii - limitări și dezvoltări viitoare", [
            "Limitările actuale includ lipsa unei relații persistente User-Review prin user_id, lipsa endpoint-urilor de listare/editare/ștergere review-uri, lipsa unei coloane is_verified în tabela users, CORS permisiv și folosirea unui model de sentiment specializat pe limba engleză.",
            "Dezvoltările viitoare pot include migrarea către PostgreSQL, introducerea Alembic pentru migrații, autentificare cu refresh token, dashboard-uri Recharts reale, paginare frontend, cache pentru răspunsurile NLP, suport multilingv și teste automate cu pytest și Playwright.",
            "În concluzie, aplicația oferă o bază solidă pentru o platformă de analiză a review-urilor hoteliere și ilustrează modul în care AI-ul poate fi integrat pragmatic într-un sistem web accesibil utilizatorilor."
        ]),
    ]
    for item in conclusions:
        emit_page_block(doc, item)

    add_bibliography(doc)
    add_annexes(doc)


def add_bibliography(doc: Document) -> None:
    doc.add_heading("BIBLIOGRAFIE", level=1)
    sources = [
        "Python Software Foundation, Python 3 Documentation, https://docs.python.org/3/",
        "FastAPI, FastAPI Documentation, https://fastapi.tiangolo.com/",
        "Uvicorn, Uvicorn Documentation, https://www.uvicorn.org/",
        "Pydantic, Pydantic Documentation, https://docs.pydantic.dev/",
        "SQLAlchemy, SQLAlchemy ORM Documentation, https://docs.sqlalchemy.org/",
        "SQLite, SQLite Documentation, https://www.sqlite.org/docs.html",
        "Hugging Face, Transformers Documentation, https://huggingface.co/docs/transformers/",
        "Hugging Face, Pipelines Documentation, https://huggingface.co/docs/transformers/main_classes/pipelines",
        "Sanh, V. et al., DistilBERT, arXiv:1910.01108, https://arxiv.org/abs/1910.01108",
        "Devlin, J. et al., BERT, arXiv:1810.04805, https://arxiv.org/abs/1810.04805",
        "Raffel, C. et al., Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer, https://arxiv.org/abs/1910.10683",
        "Socher, R. et al., Recursive Deep Models for Semantic Compositionality Over a Sentiment Treebank, https://aclanthology.org/D13-1170/",
        "React, React Documentation, https://react.dev/",
        "React Router, React Router Documentation, https://reactrouter.com/",
        "Vite, Vite Guide, https://vitejs.dev/guide/",
        "Axios, Axios Documentation, https://axios-http.com/docs/intro",
        "Recharts, Recharts Documentation, https://recharts.org/en-US/",
        "PyJWT, PyJWT Documentation, https://pyjwt.readthedocs.io/",
        "Passlib, Passlib Documentation, https://passlib.readthedocs.io/",
        "python-dotenv, python-dotenv Documentation, https://saurabh-kumar.com/python-dotenv/",
        "MDN Web Docs, JavaScript Guide, https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
        "MDN Web Docs, CSS Reference, https://developer.mozilla.org/en-US/docs/Web/CSS",
        "Git, Git Documentation, https://git-scm.com/doc",
    ]
    for i, src in enumerate(sources, start=1):
        p = doc.add_paragraph(style="BibliographySmall")
        r = p.add_run(f"[{i}] {src}")
        set_run_font(r, size=9)
    page_break(doc)


def add_annexes(doc: Document) -> None:
    doc.add_heading("ANEXE", level=1)
    add_para(doc, "Anexa A. Structura completă a proiectului analizat, excluzând directoarele de dependențe node_modules, venv și __pycache__:")
    structure = """hotel-review-nlp-master/
  backend/
    main.py, database.py, models.py, sentiment.py, summarization.py
    email_utils.py, migrations.py, seed_data.py, check_dependencies.py
    requirements.txt, hotel_reviews.db, data/hotels.json
  frontend/
    index.html, package.json, vite.config.js
    src/App.jsx, src/main.jsx, src/index.css
    src/auth/AuthProvider.jsx
    src/services/api.js, authApi.js, reviewsApi.js
    src/pages/*.jsx
    src/components/*.jsx, *.css
  README.md, DEVELOPMENT.md, setup.sh, .gitignore"""
    add_code(doc, structure, "Anexa A: Structura proiectului.")
    add_para(doc, "Anexa B. Funcționalități identificate automat din codul sursă:")
    add_bullets(doc, [
        "Listare hoteluri și vizualizare detalii hotel.",
        "Înregistrare, login, profil curent, verificare email și resetare parolă.",
        "Creare review protejată prin JWT și analiză automată a sentimentului.",
        "Sumarizare review-uri pe hotel cu T5-small sau fallback extractiv.",
        "Pagină de testare a sentimentului pentru texte introduse manual.",
        "Header cu profil, footer, pagini Home/About și layout responsive.",
    ])
    add_para(doc, "Anexa C. Surse Mermaid orientative pentru diagramele inserate:")
    mermaid = """flowchart LR
  Browser[React/Vite Browser] --> Services[Axios/fetch services]
  Services --> API[FastAPI REST API]
  API --> ORM[SQLAlchemy ORM]
  ORM --> DB[(SQLite)]
  API --> NLP[Transformers NLP]
  API --> Email[SMTP or console fallback]

erDiagram
  HOTELS ||--o{ REVIEWS : contains
  HOTELS {
    int id PK
    string name
    float average_sentiment
    int total_reviews
  }
  REVIEWS {
    int id PK
    int hotel_id FK
    text review_text
    string sentiment_label
    float sentiment_score
  }
  USERS {
    int id PK
    string username UK
    string hashed_password
  }"""
    add_code(doc, mermaid, "Anexa C: Fragmente Mermaid pentru arhitectură și ERD.")
    add_para(doc, "Anexa D. Observații de predare: capturile marcate în document trebuie înlocuite cu imagini reale din aplicație după rularea backend-ului și frontend-ului. Marcajele au fost lăsate intenționat, conform cerinței, și includ titlu și explicație.")


def main() -> None:
    ensure_dirs()
    figs = make_figures()
    doc = setup_document()
    build_content(doc, figs)
    doc.core_properties.title = "Documentație licență - Hotel Review NLP"
    doc.core_properties.author = "Patrik Kiraly"
    doc.core_properties.subject = "Proiect de diplomă în limba română"
    doc.core_properties.keywords = "FastAPI, React, NLP, sentiment analysis, SQLite, SQLAlchemy"
    doc.save(DOCX_PATH)
    print(DOCX_PATH)


if __name__ == "__main__":
    main()
