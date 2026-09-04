# -*- coding: utf-8 -*-
"""Wraparound cover v2 - proper panel layout.
Back panel: designed blurb. Spine: solid dark. Front: original art intact.
Trim 6x9, 20 pages -> spine 0.045in, bleed 0.125in.
"""
import os
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import Color, black, white
from PIL import Image

SRC = r"D:\empty\KDP-POLISHED\COVERS\01_Beyond_Parameter_Scaling.jpg"
OUT = r"D:\empty\KDP-POLISHED\COVERS\01_Beyond_Parameter_Scaling_WRAPAROUND.pdf"

TRIM_W, TRIM_H = 6.0, 9.0          # inches
BLEED = 0.125
PAGES = 20
SPINE_W = PAGES * 0.002252          # 0.045in

FULL_W = 2 * TRIM_W + SPINE_W + 2 * BLEED   # 12.295
FULL_H = TRIM_H + 2 * BLEED                 # 9.25

# x offsets (inches): back cover starts at 0 (bleed included), front starts after back+spine
BACK_X0 = 0.0
FRONT_X0 = BLEED + TRIM_W + SPINE_W          # 6.27
FRONT_W = TRIM_W + BLEED                     # 6.125

BG = Color(14/255, 19/255, 39/255)           # art background navy
GOLD = Color(196/255, 164/255, 100/255)
CREAM = Color(237/255, 230/255, 211/255)
GREY = Color(0.72, 0.73, 0.78)

c = canvas.Canvas(OUT, pagesize=(FULL_W * inch, FULL_H * inch))
c.setTitle("Beyond Parameter Scaling - Paperback Cover")
c.setAuthor("NILOY DAS")

# ---------- base fill (whole sheet) ----------
c.setFillColor(BG)
c.rect(0, 0, FULL_W * inch, FULL_H * inch, stroke=0, fill=1)

# ---------- FRONT panel: original art, preserved aspect, fill crop ----------
# Front visible area: FRONT_X0..FRONT_X0+TRIM_W wide, BLEED..BLEED+TRIM_H tall
# Art is 1600x2560 (aspect 0.625); front box with bleed is 6.125 x 9.25 (aspect 0.662)
# -> crop art vertically to match box aspect, then draw.
im = Image.open(SRC)
box_ar = FRONT_W / FULL_H
art_ar = im.size[0] / im.size[1]
if art_ar < box_ar:   # art too narrow -> crop top/bottom
    new_h = int(im.size[0] / box_ar)
    top = (im.size[1] - new_h) // 2
    im_f = im.crop((0, top, im.size[0], top + new_h))
else:
    new_w = int(im.size[1] * box_ar)
    left = (im.size[0] - new_w) // 2
    im_f = im.crop((left, 0, left + new_w, im.size[1]))
tmp_f = OUT.replace(".pdf", "_front.png")
im_f.save(tmp_f, "PNG", quality=95)
c.drawImage(tmp_f, FRONT_X0 * inch, 0, width=FRONT_W * inch, height=FULL_H * inch,
            preserveAspectRatio=False, mask=None)
os.remove(tmp_f)

# ---------- SPINE: solid band (no text under 79 pages) ----------
c.setFillColor(BG)
c.rect(BLEED * inch, 0, SPINE_W * inch, FULL_H * inch, stroke=0, fill=1)

# ---------- BACK panel design ----------
BW = TRIM_W + BLEED   # 6.125
# subtle border frame on back visible area
c.setStrokeColor(GOLD); c.setLineWidth(0.8)
c.rect((BLEED + 0.28) * inch, (FULL_H - BLEED - 8.72) * inch,
       (TRIM_W - 0.56) * inch, (TRIM_H - 0.56) * inch, stroke=1, fill=0)

bcx = (BACK_X0 + BLEED + TRIM_W / 2) * inch

# series line
c.setFillColor(GOLD); c.setFont("Helvetica", 8.5)
c.drawCentredString(bcx, (FULL_H - 0.62) * inch, "T H E   B E H O L D E R   P R O J E C T")
c.setFont("Helvetica-Oblique", 9)
c.drawCentredString(bcx, (FULL_H - 0.80) * inch, "Volume I")

# title
c.setFillColor(CREAM); c.setFont("Times-Bold", 25)
c.drawCentredString(bcx, (FULL_H - 1.55) * inch, "BEYOND")
c.drawCentredString(bcx, (FULL_H - 2.02) * inch, "PARAMETER")
c.drawCentredString(bcx, (FULL_H - 2.49) * inch, "SCALING")
c.setStrokeColor(GOLD); c.setLineWidth(1.2)
c.line((bcx - 0.9 * inch), (FULL_H - 2.75) * inch, (bcx + 0.9 * inch), (FULL_H - 2.75) * inch)

# subtitle
c.setFillColor(GOLD); c.setFont("Times-Italic", 11.5)
c.drawCentredString(bcx, (FULL_H - 3.10) * inch, "A First-Principles Theory of")
c.drawCentredString(bcx, (FULL_H - 3.32) * inch, "Emergent Machine Intelligence")

# blurb
c.setFillColor(GREY)
blurb = [
    ("Parameter scaling built the machines that changed the", 8.8),
    ("world. This book asks the next question: is bigger the", 8.8),
    ("only axis?", 8.8),
]
y = FULL_H - 3.85
for line, _ in blurb:
    c.setFont("Times-Roman", 9.5)
    c.drawCentredString(bcx, y * inch, line)
    y -= 0.165

blurb2 = [
    "Volume I of The Beholder Project proposes a falsifiable",
    "research program - an ecology of agents, validators,",
    "contradiction-preserving synthesis, and evolutionary",
    "selection - built around a fixed neural core. Grounded in",
    "real published work (FunSearch, AlphaEvolve, XLand,",
    "paraconsistent belief revision), with pre-registered",
    "metrics, refutation conditions, and a mathematical",
    "appendix. No hype. No claims of consciousness. A research",
    "program that invites you to break it.",
]
for line in blurb2:
    c.setFont("Times-Roman", 9.5)
    c.drawCentredString(bcx, y * inch, line)
    y -= 0.165

# pull quote
y -= 0.12
c.setFillColor(CREAM); c.setFont("Times-BoldItalic", 10.5)
c.drawCentredString(bcx, y * inch, '"Do not believe it. Build it."')
y -= 0.18
c.drawCentredString(bcx, y * inch, '"Measure it. Break it. Improve it."')

# author
c.setFillColor(GOLD); c.setFont("Helvetica", 11)
c.drawCentredString(bcx, 1.85 * inch, "NILOY DAS")

# ---------- barcode safe zone (white box, bottom-right of back) ----------
bw, bh = 2.0, 1.2
c.setFillColor(white)
c.rect((BACK_X0 + BLEED + TRIM_W - bw - 0.25) * inch, 0.25 * inch,
       bw * inch, bh * inch, stroke=0, fill=1)

c.showPage()
c.save()
print("built v2:", OUT)
