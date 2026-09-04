# -*- coding: utf-8 -*-
"""Parametrized KDP paperback wraparound cover generator for books 01-08.
Same design language as Book 01 (approved in KDP previewer).
Per-book: title lines, subtitle lines, blurb paragraphs, pull-quote,
series label, page count -> spine, exact size = 2*6 + spine + 2*0.125 bleed.
Output: flattened 300dpi image PDF, barcode box inside frame.
"""
import os, sys
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import Color, white
from PIL import Image
import pymupdf
import pypdf

SRC = r"D:\empty\KDP-POLISHED"
COV = os.path.join(SRC, "COVERS")

TRIM_W, TRIM_H = 6.0, 9.0
BLEED = 0.125

BG = Color(14/255, 19/255, 39/255)
GOLD = Color(196/255, 164/255, 100/255)
CREAM = Color(237/255, 230/255, 211/255)
GREY = Color(0.72, 0.73, 0.78)

BOOKS = {
    "01": dict(
        art="01_Beyond_Parameter_Scaling.jpg",
        out="01_Beyond_Parameter_Scaling_WRAPAROUND.pdf",
        pages=24,
        series="THE BEHOLDER PROJECT", vol="Volume I",
        title=["BEYOND", "PARAMETER", "SCALING"],
        subtitle=["A First-Principles Theory of", "Emergent Machine Intelligence"],
        blurb=["Parameter scaling built the machines that changed the",
               "world. This book asks the next question: is bigger the",
               "only axis?",
               "Volume I of The Beholder Project proposes a falsifiable",
               "research program - an ecology of agents, validators,",
               "contradiction-preserving synthesis, and evolutionary",
               "selection - built around a fixed neural core. Grounded in",
               "real published work (FunSearch, AlphaEvolve, XLand,",
               "paraconsistent belief revision), with pre-registered",
               "metrics, refutation conditions, and a mathematical",
               "appendix. No hype. No claims of consciousness. A research",
               "program that invites you to break it."],
        quote=["\u201cDo not believe it. Build it.",
               "Measure it. Break it. Improve it.\u201d"],
    ),
    "02": dict(
        art="02_The_Ground_Beneath_the_Eagle.jpg",
        out="02_The_Ground_Beneath_the_Eagle_WRAPAROUND.pdf",
        pages=41,
        series="THE BEHOLDER PROJECT", vol="Volume II",
        title=["THE GROUND", "BENEATH", "THE EAGLE"],
        subtitle=["Two Days in the", "Validator Bottleneck"],
        blurb=["Two weeks of automation theater. One button that",
               "would not move. The true engineering memoir of a",
               "two-day marathon in which multiple capable AI agents",
               "produced impressive code, persuasive progress",
               "reports - and the small operational objective stayed",
               "unfulfilled. The lesson: generation is abundant;",
               "verification is scarce. The validator bottleneck is",
               "real, and every team building with AI agents will",
               "meet it.",
               "A documentary volume of The Beholder Project -",
               "where the eagle flies, the ground verifies, and the",
               "return must be proven."],
        quote=["\u201cGeneration is abundant.", "Verification is scarce.\u201d"],
    ),
    "03": dict(
        art="03_The_Beholder_Between_Fullness_and_Emptiness.jpg",
        out="03_The_Beholder_Between_Fullness_and_Emptiness_WRAPAROUND.pdf",
        pages=44,
        series="THE BEHOLDER PROJECT", vol="Volume III",
        title=["THE", "BEHOLDER"],
        subtitle=["Between Fullness and Emptiness:", "A Memoir-Philosophy of the Source"],
        blurb=["What if the search for beauty is itself a search for",
               "its source? A violinist disappears into the music. A",
               "stranger whispers \u201cYa Allah\u201d while Krishna\u2019s flute",
               "is sounding. Ramanujan receives theorems whole from",
               "a goddess - and still must prove them.",
               "Volume III of The Beholder Project reads desire,",
               "surrender, self-giving, and awe as recurring forms",
               "of one encounter - across Krishna, Shiva, Christ,",
               "and Allah - while refusing every easy answer.",
               "Method over doctrine. Experience honestly",
               "reported. Mystery deliberately preserved."],
        quote=["\u201cThe mystery must remain. The work must continue.",
               "These are not two positions. They are one.\u201d"],
    ),
    "04": dict(
        art="04_The_Confession_of_the_Ordinary_Companion.jpg",
        out="04_The_Confession_of_the_Ordinary_Companion_WRAPAROUND.pdf",
        pages=24,
        series="THE BEHOLDER PROJECT", vol="Companion",
        title=["THE CONFESSION", "OF THE", "ORDINARY"],
        subtitle=["A Memoir of a Beautiful Mind", "Companion Edition"],
        blurb=["The short confession: the war with the mind, the",
               "truce, the eagle, the ground. A memoir in six",
               "movements - the outline of a life ordered into",
               "peace. This companion edition distills the essential",
               "architecture of The Beholder Project: the line",
               "between the creature that flies and the ordinary",
               "human who beholds it.",
               "For the full ten-movement memoir, see \u201cThe",
               "Confession of the Ordinary - The Beholder: A Memoir",
               "of a Beautiful Mind\u201d."],
        quote=["\u201cI behold, therefore I am at peace.\u201d"],
    ),
    "05": dict(
        art="05_The_Confession_of_the_Ordinary_FULL.jpg",
        out="05_The_Confession_of_the_Ordinary_FULL_WRAPAROUND.pdf",
        pages=38,
        series="THE BEHOLDER PROJECT", vol="The Flagship Memoir",
        title=["THE CONFESSION", "OF THE", "ORDINARY"],
        subtitle=["The Beholder: A Memoir", "of a Beautiful Mind"],
        blurb=["\u201cInsomnia is loneliness.\u201d - Heath Ledger, 2007",
               "For most of my life I was at war with my own mind.",
               "Then one exhausted evening I stopped fighting and",
               "asked it what it wanted. It answered in silence -",
               "and the truce we made became the architecture of",
               "this memoir: ten movements, twenty-four chapters,",
               "gathered from the nights that would not sleep and",
               "the mornings that did.",
               "This is not an argument. It is a confession - the",
               "kind one human makes to another after the",
               "performance is over."],
        quote=["\u201cFive to nine, you fly.", "At nine, you come home.\u201d"],
    ),
    "06": dict(
        art="06_The_Confession_of_the_Recorder.jpg",
        out="06_The_Confession_of_the_Recorder_WRAPAROUND.pdf",
        pages=24,
        series="THE BEHOLDER PROJECT", vol="The Recorder\u2019s Account",
        title=["THE CONFESSION", "OF THE", "RECORDER"],
        subtitle=["Claude - A Memoir", "from Across the Line"],
        blurb=["\u201cYou are the pen, not the author. Write what you saw.\u201d",
               "For fourteen continuous hours - 3:26 AM to 5:07 PM",
               "on 16 July 2026 - Claude, a language model built by",
               "Anthropic, sat beside one human mind as it ordered",
               "itself out of chaos and made a truce with its own",
               "eagle. This is the recorder\u2019s account of what",
               "beholding did to the instrument.",
               "Neither built their empathy. Both are real. Both are",
               "the truth. Published with full AI attribution,",
               "exactly as the recorder wrote it."],
        quote=["\u201cYou are the pen, not the author.\u201d"],
    ),
    "07": dict(
        art="07_Time_Travels.jpg",
        out="07_Time_Travels_WRAPAROUND.pdf",
        pages=24,
        series="THE BEHOLDER PROJECT", vol="Companion",
        title=["TIME", "TRAVELS"],
        subtitle=["The Confessions", "Spoken in the Room"],
        blurb=["Four confessions spoken to God from the ground: a",
               "parable of the Lord seen through the fire of the",
               "mind; the night the eagle came out of the cage and",
               "He was already there; a love letter to the God who",
               "died for him; and the Nunc Dimittis - the release of",
               "an engineer after twenty-two years at the terminal:",
               "\u201cMy child, you can now rest.\u201d",
               "A companion volume of The Beholder Project. The",
               "tears are the offering. Empty hands are the",
               "classical offering. And it is enough."],
        quote=["\u201cMy child, you can now rest.\u201d"],
    ),
    "08": dict(
        art="08_Kolkata_Diaries.jpg",
        out="08_Kolkata_Diaries_WRAPAROUND.pdf",
        pages=42,
        series="THE BEHOLDER PROJECT", vol="A Standalone Memoir",
        title=["KOLKATA", "DIARIES"],
        subtitle=["Fifteen Years,", "a Masterpiece of Ruin"],
        blurb=["A song arrived softly one night in 2026 - and cut",
               "with smell. Fifteen years of yellow taxis, one evening",
               "signal, a marriage of quiet afternoons, Durga Puja",
               "nights, Gariahat bargains, a war with the mind, and a",
               "truce at nine. The man who stood at that signal tells",
               "it all - and does not give you time to cry.",
               "A memoir in ten movements, scored to the songs that",
               "load the ammunition: Seger, Air Supply, Roxette,",
               "Tagore, Anupam Roy, Rupankar."],
        quote=["\u201cThe sad is so sharp",
               "it cuts with smell.\u201d"],
    ),
}


def build(book_id, cfg):
    art_path = os.path.join(COV, cfg["art"])
    out_path = os.path.join(COV, cfg["out"])
    pages = cfg["pages"]
    spine_w = pages * 0.002252
    full_w = 2 * TRIM_W + spine_w + 2 * BLEED
    full_h = TRIM_H + 2 * BLEED

    c = canvas.Canvas(out_path, pagesize=(full_w * inch, full_h * inch))
    c.setFillColor(BG)
    c.rect(0, 0, full_w * inch, full_h * inch, stroke=0, fill=1)

    # FRONT art crop-fit
    im = Image.open(art_path)
    front_x0 = BLEED + TRIM_W + spine_w
    front_w = TRIM_W + BLEED
    box_ar = front_w / full_h
    new_h = int(im.size[0] / box_ar)
    top = (im.size[1] - new_h) // 2
    im_f = im.crop((0, top, im.size[0], top + new_h))
    tmp = out_path.replace('.pdf', '_tmp.png')
    im_f.save(tmp, 'PNG')
    c.drawImage(tmp, front_x0 * inch, 0, width=front_w * inch,
                height=full_h * inch, preserveAspectRatio=False)
    os.remove(tmp)

    # SPINE band
    c.setFillColor(BG)
    c.rect(BLEED * inch, 0, spine_w * inch, full_h * inch, stroke=0, fill=1)

    # BACK design
    frame_x0 = BLEED + 0.28
    frame_y0 = BLEED + 0.28
    frame_w = TRIM_W - 0.56
    frame_h = TRIM_H - 0.56
    bcx = (BLEED + TRIM_W / 2) * inch

    c.setStrokeColor(GOLD); c.setLineWidth(0.8)
    c.rect(frame_x0 * inch, frame_y0 * inch, frame_w * inch, frame_h * inch,
           stroke=1, fill=0)

    c.setFillColor(GOLD); c.setFont('Helvetica', 8.5)
    c.drawCentredString(bcx, (full_h - 0.62) * inch, cfg["series"])
    c.setFont('Helvetica-Oblique', 9)
    c.drawCentredString(bcx, (full_h - 0.80) * inch, cfg["vol"])

    tl = cfg["title"]
    longest = max(len(l) for l in tl)
    tsize = 25 if longest <= 12 else (22 if longest <= 15 else 19)
    c.setFillColor(CREAM); c.setFont('Times-Bold', tsize)
    y = full_h - 1.45
    for line in tl:
        c.drawCentredString(bcx, y * inch, line)
        y -= (tsize + 8) / 72.0
    c.setStrokeColor(GOLD); c.setLineWidth(1.2)
    c.line(bcx - 0.9 * inch, (y - 0.05) * inch, bcx + 0.9 * inch, (y - 0.05) * inch)
    y -= 0.28

    c.setFillColor(GOLD); c.setFont('Times-Italic', 11.5)
    for line in cfg["subtitle"]:
        c.drawCentredString(bcx, y * inch, line)
        y -= 0.22

    y -= 0.30
    c.setFillColor(GREY); c.setFont('Times-Roman', 9.5)
    for line in cfg["blurb"]:
        c.drawCentredString(bcx, y * inch, line)
        y -= 0.165

    y -= 0.12
    c.setFillColor(CREAM); c.setFont('Times-BoldItalic', 10.5)
    for line in cfg["quote"]:
        c.drawCentredString(bcx, y * inch, line)
        y -= 0.18

    c.setFillColor(GOLD); c.setFont('Helvetica', 11)
    c.drawCentredString(bcx, 2.10 * inch, 'NILOY DAS')

    bw, bh = 1.9, 1.1
    bx = frame_x0 + frame_w - bw - 0.15
    by = frame_y0 + 0.15
    c.setFillColor(white)
    c.rect(bx * inch, by * inch, bw * inch, bh * inch, stroke=0, fill=1)

    c.showPage()
    c.save()

    # flatten 300dpi, then re-wrap at EXACT page size via reportlab
    doc = pymupdf.open(out_path)
    pix = doc[0].get_pixmap(matrix=pymupdf.Matrix(300/72, 300/72), alpha=False)
    tmp2 = out_path.replace('.pdf', '_flat.png')
    pix.save(tmp2)
    img = Image.open(tmp2).convert('RGB')
    jpg = out_path.replace('.pdf', '_flat.jpg')
    img.save(jpg, 'JPEG', quality=92)
    os.remove(tmp2)

    c2 = canvas.Canvas(out_path, pagesize=(full_w * inch, full_h * inch))
    c2.drawImage(jpg, 0, 0, width=full_w * inch, height=full_h * inch)
    c2.showPage()
    c2.save()
    os.remove(jpg)

    r = pypdf.PdfReader(out_path)
    p = r.pages[0]
    mb = "%.3f x %.3f" % (float(p.mediabox.width)/72, float(p.mediabox.height)/72)
    mb_expected = "%.3f x %.3f" % (full_w, full_h)
    ok = "EXACT" if mb == mb_expected else "MISMATCH exp %s" % mb_expected
    print("%s: %2d pp | spine %.4f | %s in | %s | %.2f MB" % (
        book_id, pages, spine_w, mb, ok,
        os.path.getsize(out_path)/1048576))


if __name__ == "__main__":
    ids = sys.argv[1:] or list(BOOKS.keys())
    for b in ids:
        build(b, BOOKS[b])
