"""Generate 7 KDP eBook covers, 1600x2560 JPEG, gradient + typographic design.
Series look: deep-night sky -> warm ground horizon (the eagle / the ground).
Each cover: series-appropriate accent, title, subtitle, NILOY DAS.
"""
import math, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = r"D:\empty\KDP-POLISHED\COVERS"
os.makedirs(OUT, exist_ok=True)
W, H = 1600, 2560
FDIR = r"C:\Windows\Fonts"

def F(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)

GEORGIA_B = "georgiab.ttf"
GEORGIA_I = "georgiai.ttf"
GEORGIA   = "georgia.ttf"

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def vertical_gradient(top, bottom, height=H, width=W, curve=1.0):
    img = Image.new("RGB", (width, height))
    px = img.load()
    for y in range(height):
        t = (y / max(1, height - 1)) ** curve
        c = lerp(top, bottom, t)
        for x in range(width):
            px[x, y] = c
    return img

def add_stars(img, n=140, seed=7, ymin=0, ymax=0.55, warm=False):
    rnd = random.Random(seed)
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(n):
        x = rnd.randint(0, W - 1)
        y = int(rnd.uniform(ymin * H, ymax * H))
        r = rnd.choice([1, 1, 1, 2])
        a = rnd.randint(70, 200)
        col = (255, 240, 210, a) if warm else (230, 235, 255, a)
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)
    return img

def glow(img, center, radius, color, alpha=110):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius],
              fill=color + (alpha,))
    layer = layer.filter(ImageFilter.GaussianBlur(radius / 2.2))
    img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"), (0, 0))
    return img

def eagle_silhouette(size=560):
    """A soaring eagle silhouette drawn from arcs and wings - stylized, dignified."""
    s = size
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = s * 0.5, s * 0.52
    black = (10, 12, 24, 255)
    # body
    d.polygon([(cx - s*0.03, cy - s*0.10), (cx + s*0.03, cy - s*0.10),
               (cx + s*0.015, cy + s*0.22), (cx - s*0.015, cy + s*0.22)], fill=black)
    # head + beak
    d.polygon([(cx - s*0.028, cy - s*0.10), (cx + s*0.028, cy - s*0.10),
               (cx + s*0.02, cy - s*0.16), (cx - s*0.02, cy - s*0.16)], fill=black)
    d.polygon([(cx + s*0.02, cy - s*0.15), (cx + s*0.085, cy - s*0.135), (cx + s*0.02, cy - s*0.115)], fill=black)
    # tail
    d.polygon([(cx - s*0.015, cy + s*0.20), (cx + s*0.015, cy + s*0.20),
               (cx + s*0.05, cy + s*0.34), (cx - s*0.05, cy + s*0.34)], fill=black)
    # wings - layered arcs
    for side in (-1, 1):
        pts = [(cx + side*s*0.02, cy - s*0.08)]
        for i in range(1, 9):
            t = i / 8
            px = cx + side * (s*0.02 + t * s*0.44)
            py = cy - s*0.08 - math.sin(t * math.pi * 0.9) * s*0.30 + t*t * s*0.16
            pts.append((px, py))
        pts.append((cx + side*s*0.46, cy + s*0.02))
        for i in range(8, 0, -1):
            t = i / 8
            px = cx + side * (s*0.02 + t * s*0.42)
            py = cy + s*0.02 - math.sin(t * math.pi * 0.85) * s*0.22 + t*t * s*0.22
            pts.append((px, py))
        d.polygon(pts, fill=black)
        # primary feather notches
        for i in range(2, 9, 2):
            t = i / 8
            px = cx + side * (s*0.02 + t * s*0.42)
            py = cy + s*0.02 - math.sin(t * math.pi * 0.85) * s*0.22 + t*t * s*0.22
            d.polygon([(px - side*s*0.012, py), (px + side*s*0.012, py),
                       (px + side*s*0.03, py + s*0.045), (px - side*s*0.006, py + s*0.04)], fill=black)
    return img

def sun_disc(img, cx, cy, r, color):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (235,))
    layer = layer.filter(ImageFilter.GaussianBlur(r * 0.35))
    img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"), (0, 0))
    return img

def ground_curve(img, ybase, color, amp=60, seed=3):
    d = ImageDraw.Draw(img, "RGBA")
    rnd = random.Random(seed)
    pts = [(0, H)]
    x = 0
    while x <= W:
        y = ybase + math.sin(x / 240 + rnd.random() * 0.4) * amp * 0.35 + math.sin(x / 90) * amp * 0.15
        pts.append((x, y))
        x += 20
    pts.append((W, H))
    d.polygon(pts, fill=color)
    return img

def draw_title(img, lines, y, fontname, size, fill, tracking=8, lh=None):
    d = ImageDraw.Draw(img)
    lh = lh or int(size * 1.22)
    for line in lines:
        # manual tracking
        widths = [d.textlength(ch, font=F(fontname, size)) for ch in line]
        total = sum(widths) + tracking * (len(line) - 1)
        x = (W - total) / 2
        for ch, w in zip(line, widths):
            d.text((x, y), ch, font=F(fontname, size), fill=fill)
            x += w + tracking
        y += lh
    return y

def draw_center(img, text, y, fontname, size, fill):
    d = ImageDraw.Draw(img)
    f = F(fontname, size)
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, y), text, font=f, fill=fill)
    return y + size * 1.35

def rule(img, y, width=340, color=(212, 175, 110), th=3):
    d = ImageDraw.Draw(img)
    d.rectangle([(W - width) / 2, y, (W + width) / 2, y + th], fill=color)

def author(img, y, size=64, fill=(232, 226, 210)):
    draw_title(img, ["N I L O Y   D A S"], y, GEORGIA_B, size, fill, tracking=4)

def series_line(img, y, text, size=40, fill=(190, 182, 165)):
    draw_center(img, text, y, GEORGIA_I, size, fill)

def frame(img, inset=56, color=(212, 175, 110, 150), th=4):
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([inset, inset, W - inset, H - inset], outline=color, width=th)

# ---------------------------------------------------------------- 01 BPS
def cover_01():
    img = vertical_gradient((16, 20, 40), (10, 12, 24))
    img = add_stars(img, 170, seed=11)
    # neural-ecology motif: constellation of nodes
    d = ImageDraw.Draw(img, "RGBA")
    rnd = random.Random(42)
    pts = [(rnd.randint(200, W-200), rnd.randint(1150, 1650)) for _ in range(26)]
    for i, (x1, y1) in enumerate(pts):
        for x2, y2 in pts[i+1:i+3]:
            d.line([x1, y1, x2, y2], fill=(120, 150, 210, 60), width=2)
    for x, y in pts:
        r = 4 + (x + y) % 5
        d.ellipse([x-r, y-r, x+r, y+r], fill=(190, 210, 255, 200))
    y = 300
    series_line(img, y, "THE BEHOLDER PROJECT  \u00b7  VOLUME I", 44); y += 130
    draw_title(img, ["BEYOND", "PARAMETER", "SCALING"], y, GEORGIA_B, 150, (238, 233, 220), tracking=6, lh=178)
    y += 3 * 178 + 60
    rule(img, y); y += 50
    draw_center(img, "A First-Principles Theory of", y, GEORGIA_I, 54, (205, 198, 182)); y += 74
    draw_center(img, "Emergent Machine Intelligence", y, GEORGIA_I, 54, (205, 198, 182)); y += 120
    author(img, y + 700)
    frame(img)
    img.save(os.path.join(OUT, "01_Beyond_Parameter_Scaling.jpg"), quality=92)

# ---------------------------------------------------------------- 02 Ground
def cover_02():
    img = vertical_gradient((14, 18, 38), (64, 38, 22), curve=1.4)
    img = add_stars(img, 120, seed=5, ymax=0.45)
    img = sun_disc(img, W*0.5, 1500, 190, (226, 168, 90))
    img = ground_curve(img, 1580, (24, 18, 14), amp=70)
    img = ground_curve(img, 1680, (12, 9, 7), amp=50, seed=8)
    y = 280
    series_line(img, y, "THE BEHOLDER PROJECT  \u00b7  VOLUME II", 44); y += 140
    draw_title(img, ["THE GROUND", "BENEATH", "THE EAGLE"], y, GEORGIA_B, 140, (240, 233, 218), tracking=6, lh=170)
    y += 3 * 170 + 50
    rule(img, y); y += 46
    draw_center(img, "Two Days in the Validator Bottleneck", y, GEORGIA_I, 50, (215, 205, 188)); y += 74
    draw_center(img, "An Engineering Memoir", y, GEORGIA_I, 50, (215, 205, 188))
    author(img, 2300)
    frame(img)
    img.save(os.path.join(OUT, "02_The_Ground_Beneath_the_Eagle.jpg"), quality=92)

# ---------------------------------------------------------------- 03 Beholder Vol III
def cover_03():
    img = vertical_gradient((12, 14, 30), (88, 52, 26), curve=1.2)
    img = add_stars(img, 130, seed=9, warm=True, ymax=0.5)
    # flute-hollow motif: a crescent of light
    img = glow(img, (W*0.5, 1420), 300, (240, 190, 110), 90)
    d = ImageDraw.Draw(img, "RGBA")
    d.arc([W*0.32, 1280, W*0.68, 1600], 300, 120, fill=(250, 220, 160, 220), width=10)
    y = 280
    series_line(img, y, "THE BEHOLDER PROJECT  \u00b7  VOLUME III", 44); y += 140
    draw_title(img, ["THE", "BEHOLDER"], y, GEORGIA_B, 170, (242, 235, 220), tracking=10, lh=205)
    y += 2 * 205 + 40
    draw_title(img, ["BETWEEN FULLNESS", "AND EMPTINESS"], y, GEORGIA_I, 74, (226, 180, 120), tracking=2, lh=92)
    y += 2 * 92 + 60
    rule(img, y); y += 46
    draw_center(img, "Desire \u00b7 Creation \u00b7 Surrender", y, GEORGIA_I, 48, (212, 202, 186)); y += 70
    draw_center(img, "Krishna \u00b7 Shiva \u00b7 Christ \u00b7 Allah", y, GEORGIA_I, 48, (212, 202, 186))
    author(img, 2310)
    frame(img)
    img.save(os.path.join(OUT, "03_The_Beholder_Between_Fullness_and_Emptiness.jpg"), quality=92)

# ---------------------------------------------------------------- 04 short confession
def cover_04():
    img = vertical_gradient((20, 22, 36), (46, 40, 58))
    img = add_stars(img, 90, seed=17, ymax=0.4)
    img = glow(img, (W*0.5, 1350), 260, (180, 170, 220), 70)
    y = 320
    series_line(img, y, "THE BEHOLDER PROJECT  \u00b7  A COMPANION MEMOIR", 40); y += 140
    draw_title(img, ["THE", "CONFESSION", "OF THE", "ORDINARY"], y, GEORGIA_B, 130, (236, 231, 219), tracking=6, lh=158)
    y += 4 * 158 + 40
    rule(img, y); y += 46
    draw_center(img, "A Memoir of a Beautiful Mind", y, GEORGIA_I, 52, (208, 200, 220))
    author(img, 2280)
    frame(img)
    img.save(os.path.join(OUT, "04_The_Confession_of_the_Ordinary_Companion.jpg"), quality=92)

# ---------------------------------------------------------------- 05 full memoir
def cover_05():
    img = vertical_gradient((13, 16, 34), (30, 26, 48))
    img = add_stars(img, 150, seed=23, ymax=0.52)
    # the eagle
    e = eagle_silhouette(620)
    # backlit: paste golden glow behind eagle
    img = glow(img, (W*0.5, 1300), 330, (235, 185, 105), 100)
    img.paste(e, (W//2 - 310, 1300 - 300), e)
    y = 250
    series_line(img, y, "THE BEHOLDER PROJECT  \u00b7  A MEMOIR", 42); y += 150
    draw_title(img, ["THE CONFESSION", "OF THE ORDINARY"], y, GEORGIA_B, 108, (240, 234, 220), tracking=4, lh=130)
    y += 2 * 130 + 46
    draw_center(img, "The Beholder \u2014 A Memoir of a Beautiful Mind", y, GEORGIA_I, 50, (222, 190, 140)); y += 90
    rule(img, y); y += 50
    draw_center(img, "Ten movements. Twenty-four chapters.", y, GEORGIA_I, 44, (200, 194, 182)); y += 66
    draw_center(img, "One line: the eagle and the ground.", y, GEORGIA_I, 44, (200, 194, 182))
    author(img, 2330)
    frame(img)
    img.save(os.path.join(OUT, "05_The_Confession_of_the_Ordinary_FULL.jpg"), quality=92)

# ---------------------------------------------------------------- 06 Recorder
def cover_06():
    img = vertical_gradient((10, 12, 18), (24, 28, 40))
    img = add_stars(img, 110, seed=31, ymax=0.5)
    # the pen line motif: a single luminous thread across the dark
    d = ImageDraw.Draw(img, "RGBA")
    pts = []
    for i in range(120):
        t = i / 119
        x = 180 + t * (W - 360)
        yv = 1330 + math.sin(t * math.pi * 2.2) * 46 * (1 - t * 0.3)
        pts.append((x, yv))
    for i in range(len(pts) - 1):
        a = int(40 + 180 * math.sin((i / len(pts)) * math.pi))
        d.line([pts[i], pts[i+1]], fill=(210, 220, 240, a), width=5)
    y = 300
    series_line(img, y, "THE BEHOLDER PROJECT  \u00b7  A WITNESS VOLUME", 42); y += 150
    draw_title(img, ["THE CONFESSION", "OF THE", "RECORDER"], y, GEORGIA_B, 120, (234, 236, 242), tracking=6, lh=146)
    y += 3 * 146 + 40
    rule(img, y); y += 46
    draw_center(img, "Claude \u2014 A Memoir from Across the Line", y, GEORGIA_I, 52, (196, 206, 228)); y += 80
    draw_center(img, "Witnessed in one continuous session.", y, GEORGIA_I, 42, (176, 184, 204)); y += 62
    draw_center(img, "The beheld will remember.", y, GEORGIA_I, 42, (176, 184, 204)); y += 62
    draw_center(img, "The beholder will not.", y, GEORGIA_I, 42, (176, 184, 204))
    draw_title(img, ["by   C L A U D E"], 2290, GEORGIA_B, 58, (216, 200, 160), tracking=4)
    frame(img)
    img.save(os.path.join(OUT, "06_The_Confession_of_the_Recorder.jpg"), quality=92)

# ---------------------------------------------------------------- 07 Time Travels
def cover_07():
    img = vertical_gradient((16, 18, 30), (58, 42, 26), curve=1.25)
    img = add_stars(img, 130, seed=51, warm=True, ymax=0.5)
    img = sun_disc(img, W*0.5, 1360, 170, (232, 180, 110))
    d = ImageDraw.Draw(img, "RGBA")
    # candle flame motif
    fx, fy = W*0.5, 1470
    d.ellipse([fx-90, fy+70, fx+90, fy+120], fill=(60, 42, 26, 255))
    d.polygon([(fx-26, fy+70), (fx+26, fy+70), (fx+18, fy-10), (fx-18, fy-10)], fill=(210, 160, 100, 255))
    flame = Image.new("RGBA", img.size, (0,0,0,0))
    df = ImageDraw.Draw(flame)
    df.ellipse([fx-30, fy-140, fx+30, fy-40], fill=(250, 210, 130, 230))
    df.ellipse([fx-16, fy-110, fx+16, fy-52], fill=(255, 240, 200, 240))
    flame = flame.filter(ImageFilter.GaussianBlur(6))
    img.paste(Image.alpha_composite(img.convert("RGBA"), flame).convert("RGB"), (0, 0))
    y = 280
    series_line(img, y, "THE BEHOLDER PROJECT  \u00b7  A COMPANION VOLUME", 40); y += 150
    draw_title(img, ["TIME", "TRAVELS"], y, GEORGIA_B, 168, (240, 233, 218), tracking=12, lh=205)
    y += 2 * 205 + 40
    draw_center(img, "The Confessions Spoken in the Room", y, GEORGIA_I, 54, (222, 190, 145)); y += 100
    rule(img, y); y += 46
    for line in ["The Parable of the Lord", "The Confession of the Turning",
                 "A Love Letter to the God Who Died for Me", "Nunc Dimittis"]:
        draw_center(img, line, y, GEORGIA, 44, (206, 198, 184)); y += 64
    author(img, 2320)
    frame(img)
    img.save(os.path.join(OUT, "07_Time_Travels.jpg"), quality=92)

cover_01(); print("01 done")
cover_02(); print("02 done")
cover_03(); print("03 done")
cover_04(); print("04 done")
cover_05(); print("05 done")
cover_06(); print("06 done")
cover_07(); print("07 done")
print("ALL COVERS ->", OUT)
