# -*- coding: utf-8 -*-
"""Wraparound v3: 24-page spine (0.054in), barcode box INSIDE frame, flatten 300dpi."""
import os
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import Color, white
from PIL import Image
import pymupdf
import pypdf

SRC_ART = r"D:\empty\KDP-POLISHED\COVERS\01_Beyond_Parameter_Scaling.jpg"
OUT = r"D:\empty\KDP-POLISHED\COVERS\01_Beyond_Parameter_Scaling_WRAPAROUND.pdf"

TRIM_W, TRIM_H = 6.0, 9.0
BLEED = 0.125
PAGES = 24
SPINE_W = PAGES * 0.002252   # 0.054
FULL_W = 2 * TRIM_W + SPINE_W + 2 * BLEED
FULL_H = TRIM_H + 2 * BLEED

BG = Color(14/255, 19/255, 39/255)
GOLD = Color(196/255, 164/255, 100/255)
CREAM = Color(237/255, 230/255, 211/255)
GREY = Color(0.72, 0.73, 0.78)

c = canvas.Canvas(OUT, pagesize=(FULL_W * inch, FULL_H * inch))
c.setFillColor(BG)
c.rect(0, 0, FULL_W * inch, FULL_H * inch, stroke=0, fill=1)

# ---- FRONT: art crop-fit ----
im = Image.open(SRC_ART)
FRONT_X0 = BLEED + TRIM_W + SPINE_W
FRONT_W = TRIM_W + BLEED
box_ar = FRONT_W / FULL_H
new_h = int(im.size[0] / box_ar)
top = (im.size[1] - new_h) // 2
im_f = im.crop((0, top, im.size[0], top + new_h))
tmp = OUT.replace('.pdf', '_tmp.png')
im_f.save(tmp, 'PNG')
c.drawImage(tmp, FRONT_X0 * inch, 0, width=FRONT_W * inch, height=FULL_H * inch,
            preserveAspectRatio=False)
os.remove(tmp)

# ---- SPINE band ----
c.setFillColor(BG)
c.rect(BLEED * inch, 0, SPINE_W * inch, FULL_H * inch, stroke=0, fill=1)

# ---- BACK design ----
frame_x0 = BLEED + 0.28
frame_y0 = BLEED + 0.28
frame_w = TRIM_W - 0.56
frame_h = TRIM_H - 0.56
bcx = (BLEED + TRIM_W / 2) * inch

c.setStrokeColor(GOLD); c.setLineWidth(0.8)
c.rect(frame_x0 * inch, frame_y0 * inch, frame_w * inch, frame_h * inch, stroke=1, fill=0)

c.setFillColor(GOLD); c.setFont('Helvetica', 8.5)
c.drawCentredString(bcx, (FULL_H - 0.62) * inch, 'T H E   B E H O L D E R   P R O J E C T')
c.setFont('Helvetica-Oblique', 9)
c.drawCentredString(bcx, (FULL_H - 0.80) * inch, 'Volume I')

c.setFillColor(CREAM); c.setFont('Times-Bold', 25)
c.drawCentredString(bcx, (FULL_H - 1.55) * inch, 'BEYOND')
c.drawCentredString(bcx, (FULL_H - 2.02) * inch, 'PARAMETER')
c.drawCentredString(bcx, (FULL_H - 2.49) * inch, 'SCALING')
c.setStrokeColor(GOLD); c.setLineWidth(1.2)
c.line(bcx - 0.9 * inch, (FULL_H - 2.75) * inch, bcx + 0.9 * inch, (FULL_H - 2.75) * inch)

c.setFillColor(GOLD); c.setFont('Times-Italic', 11.5)
c.drawCentredString(bcx, (FULL_H - 3.10) * inch, 'A First-Principles Theory of')
c.drawCentredString(bcx, (FULL_H - 3.32) * inch, 'Emergent Machine Intelligence')

c.setFillColor(GREY)
y = FULL_H - 3.85
for line in ['Parameter scaling built the machines that changed the',
             'world. This book asks the next question: is bigger the',
             'only axis?']:
    c.setFont('Times-Roman', 9.5)
    c.drawCentredString(bcx, y * inch, line)
    y -= 0.165
for line in ['Volume I of The Beholder Project proposes a falsifiable',
             'research program - an ecology of agents, validators,',
             'contradiction-preserving synthesis, and evolutionary',
             'selection - built around a fixed neural core. Grounded in',
             'real published work (FunSearch, AlphaEvolve, XLand,',
             'paraconsistent belief revision), with pre-registered',
             'metrics, refutation conditions, and a mathematical',
             'appendix. No hype. No claims of consciousness. A research',
             'program that invites you to break it.']:
    c.setFont('Times-Roman', 9.5)
    c.drawCentredString(bcx, y * inch, line)
    y -= 0.165
y -= 0.12
c.setFillColor(CREAM); c.setFont('Times-BoldItalic', 10.5)
c.drawCentredString(bcx, y * inch, '"Do not believe it. Build it."')
y -= 0.18
c.drawCentredString(bcx, y * inch, '"Measure it. Break it. Improve it."')

c.setFillColor(GOLD); c.setFont('Helvetica', 11)
c.drawCentredString(bcx, 2.10 * inch, 'NILOY DAS')

# ---- Barcode safe zone: INSIDE the frame, clear of it on all sides ----
bw, bh = 1.9, 1.1
bx = frame_x0 + frame_w - bw - 0.15   # 0.15in inside right frame edge
by = frame_y0 + 0.15                  # 0.15in inside bottom frame edge
c.setFillColor(white)
c.rect(bx * inch, by * inch, bw * inch, bh * inch, stroke=0, fill=1)

c.showPage()
c.save()

# ---- Flatten to single 300dpi image PDF ----
doc = pymupdf.open(OUT)
pix = doc[0].get_pixmap(matrix=pymupdf.Matrix(300/72, 300/72), alpha=False)
print('raster:', pix.width, 'x', pix.height)
tmp2 = OUT.replace('.pdf', '_flat.png')
pix.save(tmp2)
img = Image.open(tmp2).convert('RGB')
img.save(OUT, 'PDF', resolution=300.0, quality=92)
os.remove(tmp2)

r = pypdf.PdfReader(OUT)
p = r.pages[0]
print('final size in: %.3f x %.3f | MB: %.2f' % (
    float(p.mediabox.width)/72, float(p.mediabox.height)/72,
    os.path.getsize(OUT)/1048576))
print('spine in: %.4f' % SPINE_W)
