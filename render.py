#!/usr/bin/env python3
"""Render the make.fun news-image entry: a 1024x1024 front-page collage
summing up world news of Thursday 26 November 2026.

Layout reused from the 25 November entry (same masthead / lead / 6-tile
grid / ticker structure); only the date and the stories changed.

Deterministic: fixed layout, fixed text, no randomness, no network.
Run: python3 render.py  -> writes entry.png next to this script.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

# ---------- fonts ----------
def font(path_candidates, size):
    for p in path_candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

SERIF_B = ["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"]
SANS_B = ["/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
SANS_R = ["/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]

# ---------- palette ----------
NAVY = (14, 42, 71)
NAVY_D = (9, 30, 52)
CREAM = (245, 240, 230)
CARD = (255, 255, 255)
INK = (22, 22, 22)
GREY = (88, 88, 84)
LINE = (201, 194, 178)
AMBER = (232, 179, 75)
RED = (192, 57, 43)
BLUE = (46, 90, 136)
BROWN = (183, 121, 31)
GREEN = (46, 125, 50)
ORANGE = (211, 84, 0)
PURPLE = (108, 52, 131)
RUST = (178, 72, 46)
TEAL = (42, 122, 120)

img = Image.new("RGB", (W, H), CREAM)
d = ImageDraw.Draw(img)

# ---------- helpers ----------
def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def center_text(draw, cx, y, text, fnt, fill):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)

def spaced(draw, cx, y, text, fnt, fill, gap=6):
    """Draw letterspaced caps text centred at cx."""
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + gap * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + gap

# ---------- outer frame ----------
d.rectangle([8, 8, W - 9, H - 9], outline=NAVY, width=3)

# ---------- masthead ----------
d.rectangle([14, 14, 1010, 128], fill=NAVY)
f_date = font(SERIF_B, 60)
center_text(d, 512, 26, "26 NOVEMBER 2026", f_date, (255, 255, 255))
f_sub = font(SANS_B, 19)
spaced(d, 512, 96, "THURSDAY  •  THE WORLD IN ONE PAGE", f_sub, AMBER, gap=4)

# ---------- lead story: US tariffs, day two ----------
LX0, LY0, LX1, LY1 = 14, 140, 1010, 344
d.rectangle([LX0, LY0, LX1, LY1], fill=CARD, outline=NAVY, width=2)
f_kick = font(SANS_B, 18)
d.text((34, 156), "TRADE  •  LEAD STORY", font=f_kick, fill=RED)
f_lead = font(SERIF_B, 47)
lead_lines = wrap(d, "Tariff storm hits 14 economies", f_lead, 640)
y = 182
for ln in lead_lines:
    d.text((34, y), ln, font=f_lead, fill=INK)
    y += 56
f_leadsub = font(SANS_R, 24)
sub_lines = wrap(d, "India faces 17-25% as backlash grows.",
                 f_leadsub, 640)
y += 4
for ln in sub_lines:
    d.text((34, y), ln, font=f_leadsub, fill=GREY)
    y += 32
# right panel: big 14 badge
d.rectangle([716, 156, 990, 328], fill=RUST)
f_pct = font(SANS_B, 84)
center_text(d, 853, 168, "14", f_pct, (255, 255, 255))
f_pctsub = font(SANS_B, 20)
center_text(d, 853, 262, "ECONOMIES", f_pctsub, (255, 235, 200))
center_text(d, 853, 288, "IN THE FIRING LINE", f_pctsub, (255, 235, 200))

# ---------- story tiles ----------
tiles = [
    # kicker, accent, headline, sub, icon
    ("SECURITY", RED, "Kim vows to expand nuclear arsenal",
     "After Trump outreach, Pyongyang doubles down", "atom"),
    ("MIDDLE EAST", BROWN, "Israeli strikes kill nine in Gaza",
     "Deputy education minister among dead", "burst"),
    ("UKRAINE", BLUE, "Russia hits Kyiv with ballistic missiles",
     "Seven hurt; grain ships struck near Odesa", "rocket"),
    ("THAILAND", ORANGE, "Blast at Bangkok oil depot injures nine",
     "Residents told to evacuate; three critical", "flame"),
    ("BRITAIN", TEAL, "UK net migration falls to 77,000",
     "Lowest in nearly 30 years", "chart"),
    ("TECH", PURPLE, "Memory chip shortage triples RAM prices",
     "PC buyers squeezed before Black Friday", "chip"),
]

def icon_phone(cx, cy, col):
    d.rounded_rectangle([cx - 34, cy - 46, cx + 34, cy + 46], radius=8, fill=NAVY)
    d.rectangle([cx - 26, cy - 34, cx + 26, cy + 22], fill=(235, 240, 245))
    d.rectangle([cx - 12, cy - 24, cx + 12, cy + 12], fill=col)
    for dx in (-18, 0, 18):
        d.rectangle([cx + dx - 2, cy - 30, cx + dx + 2, cy - 26], fill=col)
        d.rectangle([cx + dx - 2, cy + 16, cx + dx + 2, cy + 20], fill=col)
    d.ellipse([cx - 5, cy + 30, cx + 5, cy + 40], fill=(255, 255, 255))

def icon_rocket(cx, cy, col):
    d.polygon([(cx, cy - 48), (cx - 20, cy - 8), (cx + 20, cy - 8)], fill=col)
    d.rectangle([cx - 20, cy - 10, cx + 20, cy + 30], fill=col)
    d.ellipse([cx - 8, cy - 2, cx + 8, cy + 14], outline=(255, 255, 255), width=3)
    d.polygon([(cx - 20, cy + 18), (cx - 34, cy + 40), (cx - 20, cy + 30)], fill=col)
    d.polygon([(cx + 20, cy + 18), (cx + 34, cy + 40), (cx + 20, cy + 30)], fill=col)
    d.polygon([(cx - 10, cy + 30), (cx + 10, cy + 30), (cx, cy + 52)], fill=ORANGE)

def icon_tower(cx, cy, col):
    d.rectangle([cx - 26, cy - 10, cx + 26, cy + 46], fill=col)
    d.rectangle([cx - 19, cy - 34, cx + 19, cy - 10], fill=col)
    d.rectangle([cx - 12, cy - 50, cx + 12, cy - 34], fill=col)
    d.line([cx, cy - 50, cx, cy - 62], fill=col, width=4)
    for wy in (-2, 14, 30):
        for wx in (-18, -6, 6, 18):
            d.rectangle([cx + wx - 3, cy + wy, cx + wx + 3, cy + wy + 8], fill=(255, 235, 180))

def icon_shirt(cx, cy, col):
    d.polygon([(cx - 14, cy - 40), (cx + 14, cy - 40), (cx + 14, cy - 30),
               (cx + 40, cy - 14), (cx + 40, cy + 6), (cx + 22, cy - 2),
               (cx + 22, cy + 46), (cx - 22, cy + 46), (cx - 22, cy - 2),
               (cx - 40, cy + 6), (cx - 40, cy - 14), (cx - 14, cy - 30)], fill=col)
    d.arc([cx - 14, cy - 42, cx + 14, cy - 18], start=0, end=180, fill=(255, 255, 255), width=3)

def icon_flame(cx, cy, col):
    d.polygon([(cx, cy - 52), (cx + 16, cy - 20), (cx + 30, cy + 6),
               (cx + 22, cy + 34), (cx - 22, cy + 34), (cx - 30, cy + 6),
               (cx - 16, cy - 20)], fill=col)
    d.polygon([(cx, cy - 18), (cx + 12, cy + 4), (cx + 8, cy + 26),
               (cx - 8, cy + 26), (cx - 12, cy + 4)], fill=(255, 200, 60))

def icon_court(cx, cy, col):
    d.polygon([(cx - 44, cy - 30), (cx + 44, cy - 30), (cx, cy - 52)], fill=col)
    for dx in (-32, 0, 32):
        d.rectangle([cx + dx - 5, cy - 28, cx + dx + 5, cy + 30], fill=col)
    d.rectangle([cx - 46, cy + 30, cx + 46, cy + 42], fill=col)
    d.rectangle([cx - 50, cy + 42, cx + 50, cy + 48], fill=col)

def icon_atom(cx, cy, col):
    import math
    d.ellipse([cx - 34, cy - 20, cx + 34, cy + 20], outline=col, width=4)
    d.ellipse([cx - 20, cy - 34, cx + 20, cy + 34], outline=col, width=4)
    d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=col)
    d.ellipse([cx + 26, cy - 26, cx + 36, cy - 16], fill=col)

def icon_burst(cx, cy, col):
    import math
    pts = []
    for i in range(16):
        ang = math.pi * i / 8
        r = 48 if i % 2 == 0 else 20
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    d.polygon(pts, fill=col)
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(255, 200, 60))

def icon_chart(cx, cy, col):
    d.line([cx - 40, cy + 40, cx + 40, cy + 40], fill=INK, width=4)
    d.line([cx - 40, cy + 40, cx - 40, cy - 44], fill=INK, width=4)
    for i, h in enumerate((26, 44, 62)):
        x0 = cx - 32 + i * 26
        d.rectangle([x0, cy + 36 - h, x0 + 18, cy + 36], fill=col)

def icon_chip(cx, cy, col):
    d.rounded_rectangle([cx - 34, cy - 34, cx + 34, cy + 34], radius=8, fill=col)
    d.rectangle([cx - 18, cy - 18, cx + 18, cy + 18], fill=(255, 255, 255))
    d.rectangle([cx - 8, cy - 8, cx + 8, cy + 8], fill=col)
    for dx in (-22, 0, 22):
        d.rectangle([cx + dx - 3, cy - 46, cx + dx + 3, cy - 34], fill=col)
        d.rectangle([cx + dx - 3, cy + 34, cx + dx + 3, cy + 46], fill=col)
    for dy in (-22, 0, 22):
        d.rectangle([cx - 46, cy + dy - 3, cx - 34, cy + dy + 3], fill=col)
        d.rectangle([cx + 34, cy + dy - 3, cx + 46, cy + dy + 3], fill=col)

ICONS = {"phone": icon_phone, "rocket": icon_rocket, "tower": icon_tower,
         "shirt": icon_shirt, "flame": icon_flame, "court": icon_court,
         "atom": icon_atom, "burst": icon_burst, "chart": icon_chart,
         "chip": icon_chip}

TILE_W, TILE_H, GAP = 324, 288, 12
GX0, GY0 = 14, 356
for i, (kick, accent, head, sub, icon) in enumerate(tiles):
    col = i % 3
    row = i // 3
    x0 = GX0 + col * (TILE_W + GAP)
    y0 = GY0 + row * (TILE_H + GAP)
    x1, y1 = x0 + TILE_W, y0 + TILE_H
    d.rectangle([x0, y0, x1, y1], fill=CARD, outline=LINE, width=2)
    d.rectangle([x0, y0, x1, y0 + 7], fill=accent)
    # icon on tinted disc
    icx, icy = x0 + 56, y0 + 62
    d.ellipse([icx - 48, icy - 48, icx + 48, icy + 48], fill=(238, 236, 228))
    ICONS[icon](icx, icy, accent)
    # kicker right of icon
    f_tkick = font(SANS_B, 17)
    d.text((x0 + 118, y0 + 40), kick, font=f_tkick, fill=accent)
    # headline
    f_th = font(SANS_B, 27)
    lines = wrap(d, head, f_th, TILE_W - 28)
    y = y0 + 128
    for ln in lines[:3]:
        d.text((x0 + 14, y), ln, font=f_th, fill=INK)
        y += 33
    # sub
    f_ts = font(SANS_R, 19)
    slines = wrap(d, sub, f_ts, TILE_W - 28)
    y += 6
    for ln in slines[:2]:
        d.text((x0 + 14, y), ln, font=f_ts, fill=GREY)
        y += 25

# ---------- bottom ticker ----------
d.rectangle([14, 960, 1010, 1010], fill=NAVY_D)
ticker = ("ALSO:  FedEx plane overshoots Miami runway   •   "
          "Bangladesh police tear gas protesters   •   "
          "Trump calls GDP figures 'fake'")
tick_size = 19
while tick_size > 14:
    f_tick = font(SANS_B, tick_size)
    if d.textlength(ticker, font=f_tick) <= 980:
        break
    tick_size -= 1
tw = d.textlength(ticker, font=f_tick)
d.text(((1024 - tw) / 2, 974), ticker, font=f_tick, fill=(255, 255, 255))

img.save(OUT, "PNG", optimize=True)
print("saved", OUT, os.path.getsize(OUT), "bytes")
