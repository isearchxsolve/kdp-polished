"""Build KDP-ready EPUBs (v3 nav + NCX) from the @-markup masters.
EPUB TOC is native - KDP always detects it, links always navigate.
"""
import io, os, re, uuid, zipfile
from xml.sax.saxutils import escape
from datetime import datetime, timezone

SRC = r"D:\empty\KDP-POLISHED"
OUT = os.path.join(SRC, "EPUB")
COV = os.path.join(SRC, "COVERS")
os.makedirs(OUT, exist_ok=True)

CSS = """body{font-family:Georgia,'Times New Roman',serif;line-height:1.55;margin:5%;}
h1{text-align:center;font-size:1.5em;margin:1.2em 0 .8em;}
h2{text-align:center;font-size:1.15em;margin:1.1em 0 .6em;}
h3{font-size:1.05em;margin:1em 0 .5em;}
p{margin:.45em 0;text-align:justify;text-indent:0;}
p.center{text-align:center;font-style:italic;}
p.quote{text-align:center;font-style:italic;margin:1em 8%;}
pre.code{font-family:Consolas,monospace;font-size:.85em;text-align:center;white-space:pre-wrap;}
p.copyright{font-size:.85em;margin:.3em 0;}
.title1{font-size:2em;font-weight:bold;text-align:center;margin-top:22%;}
.subtitle{text-align:center;font-style:italic;font-size:1.15em;margin-top:1.5em;}
.author{text-align:center;font-weight:bold;font-size:1.1em;margin-top:3.5em;}
.series{text-align:center;font-size:.95em;margin-top:.6em;}
.toc1{font-weight:bold;margin:.5em 0 .2em;}
.toc2{margin:.15em 0 .15em 1.6em;font-size:.95em;}
hr.thin{width:33%;margin:1.2em auto;border:0;border-top:1px solid #b09a62;}
"""

def esc(s):
    return escape(s)

def smartify(s):
    for a, b in {" -- ": " \u2014 ", "---": "\u2014", "--": "\u2013", "...": "\u2026",
                 "\ufeff": ""}.items():
        s = s.replace(a, b)
    return s

def parse_master(path):
    """Yield tokens: ('title',block) ('copy',block) ('tocbreak',) ('h1',t)
    ('h2',t) ('h3',t) ('p',t) ('center',t) ('quote',t) ('code',lines) ('rule',)"""
    lines = io.open(path, encoding="utf-8-sig").read().splitlines()
    n = len(lines)
    i = 0
    out = []
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
            i += 1; out.append(("title", block)); continue
        if s == "@COPY":
            block = []
            i += 1
            while i < n and lines[i].strip() != "@ENDCOPY":
                if lines[i].strip(): block.append(lines[i].strip())
                i += 1
            i += 1; out.append(("copy", block)); continue
        if s == "@PAGEBREAK":
            out.append(("tocbreak", None)); i += 1; continue
        if s == "@CODE":
            block = []
            i += 1
            while i < n and lines[i].strip() != "@ENDCODE":
                block.append(lines[i].rstrip()); i += 1
            i += 1; out.append(("code", [b for b in block if b])); continue
        if s == "@CENTER":
            i += 1
            while i < n and lines[i].strip() == "@CENTER": i += 1
            block = []
            while i < n and lines[i].strip() and not lines[i].strip().startswith("@"):
                block.append(lines[i].strip()); i += 1
            for t in block: out.append(("center", t))
            continue
        if s.startswith("@CENTER "):
            out.append(("center", s[8:].strip())); i += 1; continue
        if s.startswith("## "):
            out.append(("h2", s[3:].strip())); i += 1; continue
        if s.startswith("### "):
            out.append(("h3", s[4:].strip())); i += 1; continue
        if s.startswith("# ") and not s.startswith("## "):
            out.append(("h1", s[2:].strip())); i += 1; continue
        if s.startswith("> "):
            out.append(("quote", s[2:].strip())); i += 1; continue
        if s == "---":
            out.append(("rule", None)); i += 1; continue
        out.append(("p", smartify(s))); i += 1
    return out

def build_epub(txt_path, cover_path, out_path, book_title):
    toks = parse_master(txt_path)
    uid = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, "beholder-project/" + book_title))
    title_block = next(t for k, t in toks if k == "title")
    copy_block = next(t for k, t in toks if k == "copy")

    # split body into sections at H1 boundaries
    sections = []  # list of dicts {title, tokens:[(kind, payload)], sub:[(id,h2title)]}
    preface = {"title": None, "tokens": []}
    cur = None
    body_started = False
    for kind, payload in toks:
        if kind in ("title", "copy"):
            continue
        if kind == "h1" and payload != "Contents":
            body_started = True
            cur = {"title": payload, "tokens": [], "subs": []}
            sections.append(cur)
            continue
        if kind == "tocbreak":
            continue
        if not body_started:
            preface["tokens"].append((kind, payload))
        else:
            if cur is None:
                cur = {"title": None, "tokens": [], "subs": []}
                sections.append(cur)
            if kind == "h2":
                cur["subs"].append(("pending", payload))
                cur["tokens"].append(("h2", payload))
            else:
                cur["tokens"].append((kind, payload))

    files = {}  # filename -> xhtml string
    toc_entries = []  # (level, label, href)

    def render_tokens(tokens, anchor_base):
        html = []
        for kind, payload in tokens:
            if kind == "h2":
                sid = f"{anchor_base}_s{len(html):03d}"
                html.append((sid, f'<h2 id="{sid}">{esc(payload)}</h2>'))
            elif kind == "h3":
                html.append((None, f"<h3>{esc(payload)}</h3>"))
            elif kind == "p":
                html.append((None, f"<p>{esc(payload)}</p>"))
            elif kind == "center":
                html.append((None, f'<p class="center">{esc(payload)}</p>'))
            elif kind == "quote":
                html.append((None, f'<p class="quote">{esc(payload)}</p>'))
            elif kind == "rule":
                html.append((None, '<hr class="thin"/>'))
            elif kind == "code":
                body = "\n".join(esc(x) for x in payload)
                html.append((None, f'<pre class="code">{body}</pre>'))
        return html

    def xhtml(title, inner, cls=""):
        return ('<?xml version="1.0" encoding="utf-8"?>\n'
                '<!DOCTYPE html>\n'
                '<html xmlns="http://www.w3.org/1999/xhtml">\n<head>'
                f'<title>{esc(title)}</title><link rel="stylesheet" type="text/css" href="style.css"/>'
                '</head><body>\n' + inner + "\n</body></html>")

    # title page
    tb = title_block
    inner = f'<p class="title1">{esc(tb[0])}</p>'
    if len(tb) > 1: inner += f'<p class="subtitle">{esc(tb[1])}</p>'
    if len(tb) > 2: inner += f'<p class="author">{esc(tb[2])}</p>'
    for t in tb[3:]:
        inner += f'<p class="series">{esc(t)}</p>'
    files["title.xhtml"] = xhtml("Title", inner)

    # copyright page
    inner = "".join(f'<p class="copyright">{esc(t)}</p>' for t in copy_block)
    files["copyright.xhtml"] = xhtml("Copyright", inner)

    # epigraph / preface (before first H1)
    if preface["tokens"]:
        parts = render_tokens(preface["tokens"], "pre")
        inner = "".join(x for _, x in parts)
        files["epigraph.xhtml"] = xhtml("Epigraph", inner)

    # chapters
    for ci, sec in enumerate(sections):
        fname = f"ch{ci:02d}.xhtml"
        anchor_base = f"c{ci:02d}"
        parts = render_tokens(sec["tokens"], anchor_base)
        inner = f"<h1>{esc(sec['title'])}</h1>"
        subs = []
        # second pass: attach ids to h2s
        h2count = 0
        fixed = []
        for sid, x in parts:
            if x.startswith("<h2 "):
                sub_title = sec["subs"][h2count][1]
                subs.append((sid, sub_title)); h2count += 1
            fixed.append(x)
        inner += "".join(fixed)
        files[fname] = xhtml(sec["title"], inner)
        toc_entries.append((1, sec["title"], fname))
        for sid, sub_title in subs:
            toc_entries.append((2, sub_title, f"{fname}#{sid}"))

    # contents page (linked, mirrors nav)
    inner = "<h1>Contents</h1>"
    for lv, label, href in toc_entries:
        cl = "toc1" if lv == 1 else "toc2"
        inner += f'<p class="{cl}"><a href="{href}">{esc(label)}</a></p>'
    files["contents.xhtml"] = xhtml("Contents", inner)

    # cover page
    files["cover.xhtml"] = xhtml(
        "Cover",
        '<div style="text-align:center;"><img src="images/cover.jpg" alt="Cover" '
        'style="max-width:100%;max-height:100%;"/></div>')

    # CSS
    files["style.css"] = CSS

    # ---- manifest / spine / nav / ncx ----
    doc_files = ["cover.xhtml", "title.xhtml", "copyright.xhtml"]
    if "epigraph.xhtml" in files: doc_files.append("epigraph.xhtml")
    doc_files.append("contents.xhtml")
    doc_files += [f"ch{ci:02d}.xhtml" for ci in range(len(sections))]

    manifest = ('<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>\n'
                '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>\n'
                '<item id="css" href="style.css" media-type="text/css"/>\n'
                '<item id="cover-image" href="images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>\n')
    for f in doc_files:
        fid = os.path.splitext(f)[0].replace(".", "-")
        manifest += f'<item id="{fid}" href="{f}" media-type="application/xhtml+xml"/>\n'

    spine = ['<itemref idref="cover"/>', '<itemref idref="title"/>',
             '<itemref idref="copyright"/>']
    if "epigraph.xhtml" in files: spine.append('<itemref idref="epigraph"/>')
    spine.append('<itemref idref="contents"/>')
    for ci in range(len(sections)):
        spine.append(f'<itemref idref="ch{ci:02d}"/>')

    # nav.xhtml (EPUB3)
    nav_items = []
    nav_items.append('<li><a href="title.xhtml">Title Page</a></li>')
    nav_items.append('<li><a href="copyright.xhtml">Copyright</a></li>')
    if "epigraph.xhtml" in files: nav_items.append('<li><a href="epigraph.xhtml">Epigraph</a></li>')
    nav_items.append('<li><a href="contents.xhtml">Contents</a></li>')
    for lv, label, href in toc_entries:
        if lv == 1:
            nav_items.append(f'<li><a href="{href}">{esc(label)}</a></li>')
        else:
            nav_items.append(f'<li class="sub"><a href="{href}">{esc(label)}</a></li>')
    nav = ('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n'
           '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">\n'
           '<head><title>Table of Contents</title><link rel="stylesheet" type="text/css" href="style.css"/></head>\n'
           '<body><nav epub:type="toc" id="toc"><h1>Table of Contents</h1>\n<ol>\n'
           + "\n".join(nav_items) + "\n</ol></nav>\n"
           '<nav epub:type="landmarks" id="landmarks" hidden="hidden"><ol>\n'
           '<li><a epub:type="cover" href="cover.xhtml">Cover</a></li>\n'
           '<li><a epub:type="toc" href="contents.xhtml">Table of Contents</a></li>\n'
           '<li><a epub:type="bodymatter" href="' + (toc_entries[0][2].split("#")[0] if toc_entries else "title.xhtml") + '">Start of Content</a></li>\n'
           '</ol></nav>\n</body></html>')
    files["nav.xhtml"] = nav

    # toc.ncx (EPUB2 compatibility)
    np = []
    order = 0
    for lv, label, href in [("1", "Title Page", "title.xhtml"), ("1", "Copyright", "copyright.xhtml")] + \
                           ([("1", "Epigraph", "epigraph.xhtml")] if "epigraph.xhtml" in files else []) + \
                           [("1", "Contents", "contents.xhtml")] + toc_entries:
        order += 1
        src = href
        np.append(f'<navPoint id="np{order}" playOrder="{order}"><navLabel><text>{esc(label)}</text></navLabel>'
                  f'<content src="{src}"/></navPoint>')
    ncx = ('<?xml version="1.0" encoding="utf-8"?>\n'
           '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">\n'
           '<head><meta name="dtb:uid" content="' + uid + '"/>'
           '<meta name="dtb:depth" content="1"/><meta name="dtb:totalPageCount" content="0"/>'
           '<meta name="dtb:maxPageNumber" content="0"/></head>\n'
           f'<docTitle><text>{esc(book_title)}</text></docTitle>\n'
           '<navMap>' + "".join(np) + '</navMap></ncx>')
    files["toc.ncx"] = ncx

    modified = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    opf = ('<?xml version="1.0" encoding="utf-8"?>\n'
           '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="en">\n'
           '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
           f'<dc:identifier id="bookid">{uid}</dc:identifier>\n'
           f'<dc:title>{esc(book_title)}</dc:title>\n'
           '<dc:creator id="creator">Niloy Das</dc:creator>\n'
           '<dc:language>en</dc:language>\n'
           '<dc:publisher>The Beholder Project</dc:publisher>\n'
           f'<meta property="dcterms:modified">{modified}</meta>\n'
           '<meta name="cover" content="cover-image"/>\n'
           '</metadata>\n<manifest>\n' + manifest + '</manifest>\n'
           '<spine toc="ncx">\n' + "\n".join(spine) + '\n</spine>\n'
           '<guide>\n<reference type="toc" title="Contents" href="contents.xhtml"/>\n'
           '<reference type="text" title="Begin Reading" href="'
           + (toc_entries[0][2].split("#")[0] if toc_entries else "title.xhtml") + '"/>\n'
           '</guide>\n</package>')
    files["content.opf"] = opf

    # ---- zip ----
    if os.path.exists(out_path): os.remove(out_path)
    zf = zipfile.ZipFile(out_path, "w")
    zf.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", compress_type=zipfile.ZIP_STORED)
    zf.writestr("META-INF/container.xml",
                '<?xml version="1.0" encoding="utf-8"?>\n'
                '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
                '<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>'
                '</rootfiles></container>')
    for name, content in files.items():
        zf.writestr("OEBPS/" + name, content, compress_type=zipfile.ZIP_DEFLATED)
    zf.write(cover_path, "OEBPS/images/cover.jpg", compress_type=zipfile.ZIP_DEFLATED)
    zf.close()
    return len(toc_entries)

BOOKS = [
    ("01_Beyond_Parameter_Scaling_Vol_I.txt",
     "01_Beyond_Parameter_Scaling.jpg", "01_Beyond_Parameter_Scaling_Vol_I.epub",
     "Beyond Parameter Scaling: A First-Principles Theory of Emergent Machine Intelligence"),
    ("02_The_Ground_Beneath_the_Eagle_Vol_II.txt",
     "02_The_Ground_Beneath_the_Eagle.jpg", "02_The_Ground_Beneath_the_Eagle_Vol_II.epub",
     "The Ground Beneath the Eagle: Two Days in the Validator Bottleneck"),
    ("03_The_Beholder_Between_Fullness_and_Emptiness_Vol_III.txt",
     "03_The_Beholder_Between_Fullness_and_Emptiness.jpg",
     "03_The_Beholder_Between_Fullness_and_Emptiness_Vol_III.epub",
     "The Beholder: Between Fullness and Emptiness"),
    ("04_The_Confession_of_the_Ordinary_Companion_Memoir.txt",
     "04_The_Confession_of_the_Ordinary_Companion.jpg",
     "04_The_Confession_of_the_Ordinary_Companion_Memoir.epub",
     "The Confession of the Ordinary: A Memoir of a Beautiful Mind (Companion Edition)"),
    ("05_The_Confession_of_the_Ordinary_FULL_Memoir.txt",
     "05_The_Confession_of_the_Ordinary_FULL.jpg",
     "05_The_Confession_of_the_Ordinary_FULL_Memoir.epub",
     "The Confession of the Ordinary: The Beholder - A Memoir of a Beautiful Mind"),
    ("06_The_Confession_of_the_Recorder.txt",
     "06_The_Confession_of_the_Recorder.jpg", "06_The_Confession_of_the_Recorder.epub",
     "The Confession of the Recorder: Claude - A Memoir from Across the Line"),
    ("07_Time_Travels_Confessions_Spoken_in_the_Room.txt",
     "07_Time_Travels.jpg", "07_Time_Travels_Confessions_Spoken_in_the_Room.epub",
     "Time Travels: The Confessions Spoken in the Room"),
]

for txt, cov, epub, title in BOOKS:
    out = os.path.join(OUT, epub)
    n = build_epub(os.path.join(SRC, txt), os.path.join(COV, cov), out, title)
    print("built", epub, f"{os.path.getsize(out):,} bytes,", n, "nav entries")
