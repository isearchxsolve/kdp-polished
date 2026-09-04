import io, os, re
from fpdf import FPDF

SRC = r"D:\empty\KDP-POLISHED"
FDIR = r"C:\Windows\Fonts"

PAGE_W, PAGE_H = 6 * 72, 9 * 72          # KDP 6x9 inch trim
MARGIN_IN, MARGIN_OUT, MARGIN_TB = 0.75, 0.6, 0.7

def smartify(s):
    repl = {
        " -- ": " \u2014 ", "---": "\u2014", "--": "\u2013",
        "...": "\u2026", '"': '"', '"': '"', "'": "\u2019",
        "''": '"', "``": '"', "\ufeff": "",
    }
    for a, b in repl.items():
        s = s.replace(a, b)
    return s

class Book(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="pt", format=(PAGE_W, PAGE_H))
        self.set_margins(MARGIN_OUT, MARGIN_TB, MARGIN_IN)
        self.set_auto_page_break(True, MARGIN_TB)
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
        self.set_y(-0.5 * 72)
        self.set_font("G", "", 9)
        self.set_text_color(90, 90, 90)
        self.cell(0, 12, str(self.page_no()), align="C")
        self.set_text_color(0, 0, 0)

def build(txt_path, out_path):
    lines = io.open(txt_path, encoding="utf-8-sig").read().splitlines()
    n = len(lines)
    doc = Book()
    doc._skip_header = doc._skip_footer = True
    doc.add_page()
    doc._skip_header = doc._skip_footer = False
    W = PAGE_W - MARGIN_OUT - MARGIN_IN
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
        doc.add_page()

    def copy_block(block):
        doc.set_font("G", "", 8.8)
        doc.set_y(PAGE_H - MARGIN_TB - len(block) * 14 - 20)
        for t in block:
            doc.multi_cell(W, 14, smartify(t))
        doc.add_page()

    def contents_page(h1s):
        doc.foot = "Contents"
        doc.set_font("G", "B", 17)
        doc.set_x(CX); doc.cell(W, 24, "Contents", align="C"); doc.ln(30)
        doc.set_font("G", "", 10.5)
        for h in h1s:
            if h == "Contents": continue
            doc.set_x(CX + 30)
            doc.multi_cell(W - 60, 19, smartify(h))
        doc.add_page()

    def heading1(t):
        doc.foot = t
        doc.add_page()
        doc.ln(28)
        doc.set_font("G", "B", 16.5)
        doc.set_x(CX)
        doc.multi_cell(W, 22, smartify(t))
        doc.ln(12)

    def heading2(t):
        doc.ln(8)
        doc.set_font("G", "B", 12.5)
        doc.set_x(CX)
        doc.multi_cell(W, 17, smartify(t))
        doc.ln(6)

    def heading3(t):
        doc.ln(6)
        doc.set_font("G", "BI", 10.8)
        doc.set_x(CX)
        doc.multi_cell(W, 15, smartify(t))
        doc.ln(4)

    def quote(t):
        doc.ln(4)
        doc.set_x(CX + 24)
        doc.set_font("G", "I", 11)
        doc.multi_cell(W - 48, 17, smartify(t), align="C")
        doc.ln(8)

    def codeblock(block):
        doc.set_font("M", "", 8.6)
        for ln in block:
            doc.set_x(CX)
            doc.multi_cell(W, 13, smartify(ln), align="C")
        doc.ln(6)

    i = 0
    h1s = [l[2:].strip() for l in lines if l.strip().startswith("# ") and not l.strip().startswith("## ")]
    contents_done = False
    while i < n:
        s = lines[i].strip()
        if not s:
            i += 1; continue
        if s == "@TITLE":
            block = []
            i += 1
            while i < n and lines[i].strip() != "@ENDTITLE":
                if lines[i].strip(): block.append(lines[i].strip())
                i += 1
            i += 1; title_block(block); continue
        if s == "@COPY":
            block = []
            i += 1
            while i < n and lines[i].strip() != "@ENDCOPY":
                if lines[i].strip(): block.append(lines[i].strip())
                i += 1
            i += 1; copy_block(block)
            if h1s and not contents_done:
                contents_page(h1s); contents_done = True
            continue
        if s == "@PAGEBREAK":
            doc.add_page(); i += 1; continue
        if s == "@CODE":
            block = []
            i += 1
            while i < n and lines[i].strip() != "@ENDCODE":
                block.append(lines[i].rstrip()); i += 1
            i += 1; codeblock([b for b in block if b]); continue
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
            doc.cell(W, 14, "\u2726   \u2726   \u2726", align="C"); doc.ln(10); i += 1; continue
        t = smartify(s)
        doc.set_font("G", "", 10.8)
        doc.set_x(CX)
        doc.multi_cell(W, 16.2, t, align="J")
        doc.ln(5)
        i += 1

    doc.output(out_path)
    return doc.page_no()

if __name__ == "__main__":
    for f in sorted(os.listdir(SRC)):
        if not re.match(r"^0[1-7]_.*\.txt$", f):
            continue
        src = os.path.join(SRC, f)
        out = os.path.join(SRC, os.path.splitext(f)[0] + ".pdf")
        pages = build(src, out)
        print("built", os.path.basename(out), f"{os.path.getsize(out):,} bytes,", pages, "pages")
