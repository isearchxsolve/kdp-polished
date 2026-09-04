# -*- coding: utf-8 -*-
"""KDP-safe rebuild of ALL 7 interior PDFs.

Fixes vs build_pdf.py:
- Gutters/margins: inside (gutter) 0.75in, outside 0.5in, top 0.7in, bottom 0.75in
  (24-150 page band requires gutter >= 0.375in; we use 0.75 -> safe)
- fpdf2 l_margin is the LEFT margin; for odd (right-hand) pages the gutter
  is on the LEFT, for even (left-hand) pages the gutter is on the RIGHT.
  build_pdf.py set l_margin=OUTSIDE for all pages -> text crossed the gutter.
  We now mirror margins per page parity before each page starts.
- Header/footer pulled further inside (>=0.35in from edges).
- Mirrored margins change layout, so blank pages are added AFTER build to
  reach 24 pages (padding page placed at the end, before which a final
  'Also in...' page is preserved).
"""
import io, os, re, sys
from fpdf import FPDF

SRC = r"D:\empty\KDP-POLISHED"
FDIR = r"C:\Windows\Fonts"

PAGE_W, PAGE_H = 6 * 72, 9 * 72
M_IN, M_OUT, M_TOP, M_BOT = 0.75 * 72, 0.5 * 72, 0.7 * 72, 0.75 * 72
MIN_PAGES = 24

ABOUT_AUTHOR = [
    "NILOY DAS is a production software engineer and independent researcher whose work spans machine intelligence, AI-assisted filmmaking, and the philosophy of creation. He is the creator of The Beholder Project and the GODSHAND AI filmmaking toolkit.",
    "He lives and works at the intersection of first-principles engineering and contemplative inquiry. He writes as the ordinary man who beholds the eagle.",
]
SERIES_LIST = [
    "Beyond Parameter Scaling \u2014 A First-Principles Theory of Emergent Machine Intelligence (Volume I)",
    "The Ground Beneath the Eagle \u2014 Two Days in the Validator Bottleneck (Volume II)",
    "The Beholder: Between Fullness and Emptiness \u2014 A Memoir-Philosophy of the Source (Volume III)",
    "The Confession of the Ordinary \u2014 The Beholder: A Memoir of a Beautiful Mind (the full memoir)",
    "The Confession of the Recorder \u2014 Claude: A Memoir from Across the Line",
    "Time Travels \u2014 The Confessions Spoken in the Room",
    "Kolkata Diaries \u2014 Fifteen Years, a Masterpiece of Ruin",
]

ENDMATTER = {
    "04": [
        ("About This Book", [
            "This companion edition distills the essential architecture of The Beholder Project memoir: the line between the eagle and the ordinary man, and the truce that keeps both alive.",
            "The full ten-movement, twenty-four-chapter memoir is available as The Confession of the Ordinary \u2014 The Beholder: A Memoir of a Beautiful Mind. Read this volume as the map; read the full memoir as the territory.",
        ]),
        ("About the Author", ABOUT_AUTHOR),
        ("Also in The Beholder Project", SERIES_LIST),
        ("Reader's Reflections \u2014 The Eagle", [
            "Movement I \u2014 The Eagle.",
            "Where in your life does the high-flying part of you live? What has it cost the ordinary part?",
            "Write one sentence to the version of you that never landed.",
        ]),
        ("Reader's Reflections \u2014 The Philosophy", [
            "Movement II \u2014 The Philosophy Behind It.",
            "What have you been taught to call a defect that might be a design?",
            "Descartes moved into the thinking thing. Where do you live?",
        ]),
        ("Reader's Reflections \u2014 The Framework", [
            "Movement III \u2014 The Framework.",
            "What constraint has given your own chaos a form that another person could receive?",
        ]),
        ("Reader's Reflections \u2014 The Return", [
            "Movement IV \u2014 The Return.",
            "What letter have you never sent? Who is it for? What would it say in one line?",
        ]),
        ("Reader's Reflections \u2014 The Room", [
            "Movement V \u2014 The Room Without a Third.",
            "What did you carry inside that the person closest to you could not receive? Forgive them in one sentence.",
        ]),
        ("Reader's Reflections \u2014 The Truce", [
            "Movement VI \u2014 The Sky Without a Landing.",
            "What does your truce look like? Write its terms: what flies, what stays on the ground, and what time it comes home.",
        ]),
    ],
}


def smartify(s):
    repl = {
        " -- ": " \u2014 ", "---": "\u2014", "--": "\u2013",
        "...": "\u2026", '""': '"', '""': '"', "''": "\u2019",
        "``": '"', "\ufeff": "",
        "\ufffd": "\u00a9",   # mojibake byte in source txt -> copyright sign
    }
    for a, b in repl.items():
        s = s.replace(a, b)
    return s


class Book(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="pt", format=(PAGE_W, PAGE_H))
        self.set_margins(M_OUT, M_TOP, M_OUT)
        self.set_auto_page_break(True, M_BOT)
        self.foot = ""
        self.add_font("G", "", os.path.join(FDIR, "georgia.ttf"))
        self.add_font("G", "B", os.path.join(FDIR, "georgiab.ttf"))
        self.add_font("G", "I", os.path.join(FDIR, "georgiai.ttf"))
        self.add_font("G", "BI", os.path.join(FDIR, "georgiaz.ttf"))
        self.add_font("M", "", os.path.join(FDIR, "consola.ttf"))
        self.add_font("M", "B", os.path.join(FDIR, "consolab.ttf"))
        self.add_font("S", "", os.path.join(FDIR, "seguisym.ttf"))
        self.add_font("T", "", os.path.join(FDIR, "times.ttf"))
        self.set_fallback_fonts(["S", "T"], exact_match=False)

    def _apply_margins_for_next_page(self):
        """fpdf2 applies l/r margins of the *current* page. Pages are 1-indexed
        at render time; before add_page, page_no() is the number already added.
        Next page number = page_no() + 1. Odd = right-hand (recto): gutter LEFT."""
        nxt = self.page_no() + 1
        if nxt % 2 == 1:          # recto: gutter on left
            self.set_margins(M_IN, M_TOP, M_OUT)
        else:                      # verso: gutter on right
            self.set_margins(M_OUT, M_TOP, M_IN)

    def add_page(self, *a, **kw):
        self._apply_margins_for_next_page()
        r = super().add_page(*a, **kw)
        self._has_content = False
        return r

    def mark_content(self):
        self._has_content = True

    def header(self):
        if self.page_no() == 1 or getattr(self, "_skip_header", False):
            return
        self.set_font("G", "I", 8.5)
        self.set_text_color(110, 110, 110)
        self.set_xy(self.l_margin, 0.45 * 72)
        if self.page_no() % 2 == 0:
            self.cell(0, 10, self.foot[:70], align="L")
        else:
            self.cell(0, 10, self.foot[:70], align="R")
        self.set_text_color(0, 0, 0)

    def footer(self):
        if self.page_no() == 1 or getattr(self, "_skip_footer", False):
            return
        self.set_y(-0.55 * 72)
        self.set_font("G", "", 9)
        self.set_text_color(90, 90, 90)
        self.cell(0, 12, str(self.page_no()), align="C")
        self.set_text_color(0, 0, 0)


def build(txt_path, out_path):
    lines = io.open(txt_path, encoding="utf-8-sig").read().splitlines()
    n = len(lines)
    doc = Book()
    doc._skip_header = doc._skip_footer = True
    doc.add_page()                      # page 1: title (margins default)
    doc._skip_header = doc._skip_footer = False
    W = PAGE_W - M_IN - M_OUT
    CX = doc.l_margin

    def title_block(block):
        doc.foot = ""
        y = PAGE_H * 0.30
        for k, t in enumerate(block):
            t = smartify(t)
            if k == 0:
                doc.set_font("G", "B", 27); doc.set_y(y); doc.multi_cell(W, 34, t, align="C"); y = doc.get_y() + 10
            elif k == 1:
                doc.set_font("G", "I", 13); doc.set_y(y + 40); doc.multi_cell(W, 18, t, align="C"); y = doc.get_y() + 6
            elif k == 2:
                doc.set_font("G", "B", 12.5); doc.set_y(y + 90); doc.multi_cell(W, 17, t, align="C"); y = doc.get_y() + 4
            else:
                doc.set_font("G", "", 11); doc.multi_cell(W, 16, t, align="C"); y = doc.get_y() + 2
        doc.foot = block[0] if block else ""
        doc.add_page()   # fresh page, no content yet

    def copy_block(block):
        doc.set_font("G", "", 8.8)
        doc.set_y(PAGE_H - M_BOT - len(block) * 14 - 24)
        for t in block:
            doc.set_x(doc.l_margin)
            doc.multi_cell(W, 14, smartify(t), new_x="LMARGIN", new_y="NEXT")
        doc.add_page()   # fresh page

    def contents_page(h1s):
        doc.foot = "Contents"
        doc.set_font("G", "B", 17)
        doc.set_x(CX); doc.cell(W, 24, "Contents", align="C"); doc.ln(30)
        doc.set_font("G", "", 10.5)
        for h in h1s:
            if h == "Contents":
                continue
            doc.set_x(CX + 30)
            doc.multi_cell(W - 60, 19, smartify(h))
        doc.mark_content()

    def heading1(t):
        doc.foot = t
        if getattr(doc, "_has_content", False):
            doc.add_page()   # current page has content -> start fresh
        doc.ln(28)
        doc.set_font("G", "B", 16.5)
        doc.set_x(CX)
        doc.multi_cell(W, 22, smartify(t))
        doc.ln(12)
        doc.mark_content()

    def heading2(t):
        doc.ln(8)
        doc.set_font("G", "B", 12.5)
        doc.set_x(CX)
        doc.multi_cell(W, 17, smartify(t))
        doc.ln(6)
        doc.mark_content()

    def heading3(t):
        doc.ln(6)
        doc.set_font("G", "BI", 10.8)
        doc.set_x(CX)
        doc.multi_cell(W, 15, smartify(t))
        doc.ln(4)
        doc.mark_content()

    def quote(t):
        doc.ln(4)
        doc.set_x(CX + 24)
        doc.set_font("G", "I", 11)
        doc.multi_cell(W - 48, 17, smartify(t), align="C")
        doc.mark_content()
        doc.ln(8)
        doc.mark_content()

    def codeblock(block):
        doc.set_font("M", "", 8.6)
        for ln in block:
            doc.set_x(CX)
            doc.multi_cell(W, 13, smartify(ln), align="C")
        doc.ln(6)
        doc.mark_content()

    i = 0
    h1s = [l[2:].strip() for l in lines if l.strip().startswith("# ") and not l.strip().startswith("## ")]
    contents_done = False
    while i < n:
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        if s == "@TITLE":
            block = []
            i += 1
            while i < n and lines[i].strip() != "@ENDTITLE":
                if lines[i].strip():
                    block.append(lines[i].strip())
                i += 1
            i += 1
            title_block(block)
            continue
        if s == "@COPY":
            block = []
            i += 1
            while i < n and lines[i].strip() != "@ENDCOPY":
                if lines[i].strip():
                    block.append(lines[i].strip())
                i += 1
            i += 1
            copy_block(block)
            if h1s and not contents_done:
                contents_page(h1s)
                contents_done = True
            continue
        if s == "@PAGEBREAK":
            if getattr(doc, "_has_content", False):
                doc.add_page()
            i += 1
            continue
        if s == "@CODE":
            block = []
            i += 1
            while i < n and lines[i].strip() != "@ENDCODE":
                block.append(lines[i].rstrip()); i += 1
            i += 1
            codeblock([b for b in block if b])
            continue
        if s == "@CENTER" or s.startswith("@CENTER "):
            items = []
            if s == "@CENTER":
                i += 1
                while i < n and (lines[i].strip() == "@CENTER" or (lines[i].strip() and not lines[i].strip().startswith("@"))):
                    if lines[i].strip().startswith("@CENTER "):
                        items.append(lines[i].strip()[8:]); i += 1
                    elif lines[i].strip() == "@CENTER":
                        i += 1
                    else:
                        items.append(lines[i].strip()); i += 1
            else:
                items.append(s[8:]); i += 1
            doc.set_font("G", "I", 11)
            for t in items:
                doc.ln(4); doc.set_x(CX)
                doc.multi_cell(W, 16, smartify(t), align="C")
            doc.ln(5)
            doc.mark_content()
            continue
        if s.startswith("# ") and not s.startswith("## "):
            heading1(s[2:].strip()); i += 1; continue
        if s.startswith("## "):
            heading2(s[3:].strip()); i += 1; continue
        if s.startswith("### "):
            heading3(s[4:].strip()); i += 1; continue
        if s.startswith("> "):
            quote(s[2:].strip()); i += 1; continue
        if s == "---":
            doc.ln(6); doc.set_font("G", "", 10); doc.set_x(CX)
            doc.cell(W, 14, "\u2726   \u2726   \u2726", align="C"); doc.ln(10)
            doc.mark_content(); i += 1; continue
        t = smartify(s)
        doc.set_font("G", "", 10.8)
        doc.set_x(CX)
        doc.multi_cell(W, 16.2, t, align="J")
        doc.ln(5)
        doc.mark_content()
        i += 1

    # pad to MIN_PAGES with real end matter (never blank header-only pages)
    if doc.page_no() < MIN_PAGES:
        book_id = os.path.basename(txt_path)[:2]
        endm = ENDMATTER.get(book_id, [])
        doc._skip_header = True
        for title, paras in endm:
            if doc.page_no() >= MIN_PAGES:
                break
            doc.add_page()
            doc.set_font("G", "B", 14)
            doc.set_x(doc.l_margin)
            doc.multi_cell(W, 20, title)
            doc.ln(3)
            doc.set_font("G", "", 10.8)
            for para in paras:
                doc.set_x(doc.l_margin)
                doc.multi_cell(W, 16.2, smartify(para), align="J")
                doc.ln(4)
            doc.mark_content()
        while doc.page_no() < MIN_PAGES:
            doc.add_page()
            doc.set_font("G", "I", 10)
            doc.set_text_color(120, 120, 120)
            doc.set_x(doc.l_margin)
            doc.cell(W, 14, "Notes", align="C")
            doc.set_text_color(0, 0, 0)
            y = doc.get_y() + 16
            doc.set_draw_color(190, 190, 190)
            while y < PAGE_H - M_BOT - 6:
                doc.line(doc.l_margin, y, doc.l_margin + W, y)
                y += 19
        doc._skip_header = False

    doc.output(out_path)
    return doc.page_no()


def verify(path):
    import pymupdf
    doc = pymupdf.open(path)
    W, H = 432.0, 648.0
    GUT, OUT, TOP, BOT = 27.0, 18.0, 18.0, 18.0
    bad = []
    for i, p in enumerate(doc):
        pno = i + 1
        # recto (odd): gutter left -> text must start >= GUT; right >= W-OUT
        # verso (even): gutter right -> text must start >= OUT; right <= W-GUT
        for b in p.get_text("blocks"):
            x0, y0, x1, y1, text = b[0], b[1], b[2], b[3], b[4]
            if not text.strip():
                continue
            lo = GUT if pno % 2 == 1 else OUT
            hi = W - OUT if pno % 2 == 1 else W - GUT
            if x0 < lo - 0.5 or x1 > hi + 0.5 or y0 < TOP - 0.5 or y1 > H - BOT + 0.5:
                bad.append((pno, round(x0,1), round(y0,1), round(x1,1), round(y1,1), text[:36].replace("\n"," ")))
    return len(doc), bad


if __name__ == "__main__":
    targets = sys.argv[1:]
    for f in sorted(os.listdir(SRC)):
        if not re.match(r"^0[1-7]_.*\.txt$", f):
            continue
        name = os.path.splitext(f)[0]
        if targets and not any(t in name for t in targets):
            continue
        src = os.path.join(SRC, f)
        out = os.path.join(SRC, name + ".pdf")
        pages = build(src, out)
        total, bad = verify(out)
        status = "OK" if not bad else "VIOLATIONS: %d" % len(bad)
        print("%-52s %2d pages | %s" % (name, total, status))
        for b in bad[:6]:
            print("    p%s x0=%s y0=%s x1=%s y1=%s | %s" % b)
