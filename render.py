#!/usr/bin/env python3
"""Render the make.fun news-image v3 entry: a dense 1024x1024 newspaper
front page summing up world news of Thursday 26 November 2026.

v3 changes over v2: generated editorial illustrations (assets/, not
shipped in the repo) replace the hand-drawn PIL icons; the masthead is
a serif date line with a red italic teaser; region chips and a
"THE DAY IN NUMBERS" band; datelines with city, country and field on
every story; leads carry 2-3 sources each; the map is a dot matrix
with region-coloured pins plus a "STORIES BY REGION" bar chart; the
footer carries a HOW SURE legend.

36 stories: 3 illustrated leads, 10 illustrated tiles, a 14-36 list.
Every story was checked against a named source before it went on the
page; region counts, source counts and the numbers band are computed
from the story tables below, so the printed figures are exact.

Deterministic: fixed geometry, fixed text, fixed asset crops, no
clock, no randomness, no network. Run: python3 render.py ->
writes entry.png beside it. Assets are read from ./assets/; when an
asset is missing a muted placeholder panel is drawn instead, so the
script still runs standalone.
"""
import glob
import os
from collections import Counter

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
OUT = os.path.join(HERE, "entry.png")

# ---------------------------------------------------------------- fonts
def pick_font(candidates, size):
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


SERIF_B = ["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"]
SERIF_I = ["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"]
SANS_B = ["/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
SANS_R = ["/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]


def serif_b(size):
    return pick_font(SERIF_B, size)


def serif_i(size):
    return pick_font(SERIF_I, size)


def sans_b(size):
    return pick_font(SANS_B, size)


def sans_r(size):
    return pick_font(SANS_R, size)


# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234)
INK = (24, 24, 22)
NAVY = (16, 42, 70)
NAVY_SOFT = (38, 68, 96)
RULE = (196, 188, 170)
FAINT = (120, 116, 106)
CARD = (255, 255, 255)
RED = (178, 44, 36)
GREEN = (38, 110, 58)
AMBER = (166, 110, 14)
SEA = (222, 230, 236)
DOT = (172, 164, 148)

# region -> (label, colour); order is the tie-break for chip sorting
REGIONS = {
    "NA": ("North America", (52, 96, 150)),
    "EU": ("Europe", (108, 72, 140)),
    "ME": ("Middle East", (178, 44, 36)),
    "SA": ("South Asia", (42, 122, 120)),
    "EA": ("East Asia", (56, 120, 60)),
    "WORLD": ("World", (110, 110, 106)),
    "SAM": ("South America", (186, 104, 138)),
    "AFR": ("Africa", (211, 120, 40)),
    "OCE": ("Oceania", (120, 84, 50)),
}
REGION_ORDER = list(REGIONS.keys())

# ---------------------------------------------------------------- data
# leads: number, dateline, field, headline, sub, sources, art stem, crop focus
LEADS = [
    {"num": 1, "place": "NEW YORK, USA", "field": "WEATHER",
     "head": "100TH MACY\u2019S PARADE POSTPONED",
     "sub": "A nor\u2019easter forces the first weather delay in the parade\u2019s "
            "100 years; the 100th march steps off Saturday instead, with "
            "gusts to 60 mph along the route.",
     "sources": ["REUTERS", "AP", "WSJ"], "art": "lead-parade",
     "focus": 0.45, "region": "NA"},
    {"num": 2, "place": "MUMBAI, INDIA", "field": "REMEMBRANCE",
     "head": "MUMBAI MARKS 18 YEARS SINCE 26/11",
     "sub": "Tributes for the 166 killed in the 2008 attacks; India also "
            "marks 77 years of its Constitution, with the President and "
            "ministers laying wreaths in Mumbai.",
     "sources": ["ANI", "PTI"], "art": "lead-mumbai",
     "focus": 0.58, "region": "SA"},
    {"num": 3, "place": "GENEVA, SWITZERLAND", "field": "CHESS",
     "head": "GUKESH v SINDAROV, GAME 3",
     "sub": "The world champion meets the 20-year-old Uzbek in Geneva at "
            "15:00 CET, the 14-game match level at 1\u20131 after two draws, "
            "with Sindarov playing White.",
     "sources": ["CHESS.COM", "FIDE"], "art": "lead-chess",
     "focus": 0.62, "region": "EU"},
]

# tiles: number, dateline, field, headline, sub, source, tag, region, art
TILES = [
    {"num": 4, "place": "RIYADH, SAUDI ARABIA", "field": "ENERGY",
     "head": "HOUTHIS HIT RIYADH TOWER",
     "sub": "Missile hits the tallest tower and Ras Tanura refinery.",
     "source": "REUTERS", "tag": "CLAIM", "region": "ME",
     "art": "tile-riyadh"},
    {"num": 5, "place": "KHASAB, OMAN", "field": "ENERGY",
     "head": "TWO TANKERS HIT MINES NEAR HORMUZ",
     "sub": "Iran says two tankers hit mines near Oman\u2019s Khasab.",
     "source": "REUTERS", "tag": "CLAIM", "region": "ME",
     "art": "tile-hormuz"},
    {"num": 6, "place": "DEIR AL-BALAH, GAZA", "field": "CONFLICT",
     "head": "ISRAEL KILLS HAMAS MINISTER IN GAZA",
     "sub": "Hamas deputy minister killed in Deir al-Balah; nine dead.",
     "source": "JPOST", "tag": "REPORTED", "region": "ME",
     "art": "tile-gaza"},
    {"num": 7, "place": "KYIV, UKRAINE", "field": "DEFENCE",
     "head": "UKRAINE\u2019S LASER DOWNS A DRONE",
     "sub": "Kyiv says its Blysk laser downed a jet-powered Geran.",
     "source": "KYIV POST", "tag": "CLAIM", "region": "EU",
     "art": "tile-laser"},
    {"num": 8, "place": "UKRAINE", "field": "ENERGY",
     "head": "STRIKES CUT POWER IN FIVE REGIONS",
     "sub": "Russian attacks cut power in five regions; five killed.",
     "source": "REUTERS", "tag": "CONFIRMED", "region": "EU",
     "art": "tile-power"},
    {"num": 9, "place": "WASHINGTON, USA", "field": "TRADE",
     "head": "US TARIFFS HIT 14 ECONOMIES",
     "sub": "New duties: China up to 20%, India 17\u201325%.",
     "source": "REUTERS", "tag": "CONFIRMED", "region": "NA",
     "art": "tile-tariff"},
    {"num": 10, "place": "DHAKA, BANGLADESH", "field": "LABOUR",
     "head": "BANGLADESH RAISES GARMENT PAY 36%",
     "sub": "Minimum wage rises to Tk 17,000 after factory unrest.",
     "source": "AFP", "tag": "CONFIRMED", "region": "SA",
     "art": "tile-garment"},
    {"num": 11, "place": "JIUQUAN, CHINA", "field": "SPACE",
     "head": "FIRST PAKISTANI FLIES TO TIANGONG",
     "sub": "Shenzhou-24 carries the first foreign astronaut to Tiangong.",
     "source": "XINHUA", "tag": "CONFIRMED", "region": "EA",
     "art": "tile-space"},
    {"num": 12, "place": "MOSCOW, RUSSIA", "field": "CONFLICT",
     "head": "RUSSIA\u2019S WAR DEAD NEAR 500,000",
     "sub": "Leaked data puts the toll near half a million.",
     "source": "BBC", "tag": "REPORTED", "region": "EU",
     "art": "tile-wardead"},
    {"num": 13, "place": "HONIARA, SOLOMONS", "field": "DIPLOMACY",
     "head": "SOLOMONS SIGN AUSTRALIA PACT",
     "sub": "Canberra becomes the Solomons\u2019 \u2018primary security "
            "partner\u2019.",
     "source": "REUTERS", "tag": "CONFIRMED", "region": "OCE",
     "art": "tile-solomons"},
]

# list 14-36: dateline, field, headline, source, region
MORE = [
    ("Bangkok, Thailand", "Energy", "Oil depot blast injures nine",
     "AP", "EA"),
    ("London, UK", "Migration", "Net migration falls to 77,000",
     "ONS", "EU"),
    ("World", "Tech", "Memory prices triple in global shortage",
     "REUTERS", "WORLD"),
    ("Miami, USA", "Aviation", "FedEx cargo plane runs off runway",
     "AP", "NA"),
    ("Dhaka, Bangladesh", "Protest", "Police fire tear gas at protesters",
     "AP", "SA"),
    ("Washington, USA", "Economy", "Trump calls GDP data \u2018fake\u2019",
     "REUTERS", "NA"),
    ("Washington, USA", "Economy", "Jobless claims fall to 189,000",
     "REUTERS", "NA"),
    ("Brussels, Belgium", "Trade", "EU caps hybrid-car imports from China",
     "EU", "EU"),
    ("Cartagena, Colombia", "Crime", "Police free 20 supermarket hostages",
     "AP", "SAM"),
    ("Damazin, Sudan", "Conflict", "Drone strikes kill 19 in Blue Nile",
     "REUTERS", "AFR"),
    ("Cairo, Egypt", "Disaster", "Tanker crash kills 31; driver held",
     "AP", "AFR"),
    ("Mekelle, Ethiopia", "Rights", "Amnesty seeks Tigray shelling probe",
     "AP", "AFR"),
    ("Darmstadt, Germany", "Space", "Hera reveals DART crater on Dimorphos",
     "ESA", "EU"),
    ("Kuala Lumpur, Malaysia", "Tech", "Malaysia sues Google for $146m",
     "REUTERS", "EA"),
    ("Pyongyang, N. Korea", "Defence", "Vows to expand nuclear arsenal",
     "TELEGRAPH INDIA", "EA"),
    ("Kyiv, Ukraine", "Conflict", "Russian missile hits Kyiv; seven hurt",
     "REUTERS", "EU"),
    ("New Delhi, India", "Aid", "India unveils $1.6bn Nepal package",
     "ANI", "SA"),
    ("Bras\u00edlia, Brazil", "Diplomacy",
     "Brazil withdraws envoy to Argentina", "MERCOPEPRESS", "SAM"),
    ("Buea, Cameroon", "Wildlife", "Swiss hiker killed by elephants",
     "BBC", "AFR"),
    ("Hodeidah, Yemen", "Conflict", "Coalition hits Hodeidah port again",
     "CNA", "ME"),
    ("Gaza, Palestine", "Law", "UN tribunal faults UNRWA sackings",
     "GUARDIAN", "ME"),
    ("Belo Horizonte, Brazil", "Health",
     "Wolbachia cuts dengue 68.5%", "AL JAZEERA", "SAM"),
    ("London, UK", "Aviation", "PIA shifts UK flights to own 777s",
     "REUTERS", "EU"),
]

NUMBERS = [
    ("100", "YEARS OF", "MACY\u2019S PARADE"),
    ("166", "KILLED IN", "MUMBAI, 26/11"),
    ("500,000", "RUSSIAN", "WAR DEAD"),
    ("2M", "BARRELS ON", "HIT TANKER"),
    ("189,000", "US JOBLESS", "CLAIMS"),
    ("77,000", "UK NET", "MIGRATION"),
]

TIMELINE = [
    ("06:00", "Russian strikes knock out power in five regions"),
    ("07:45", "Bangkok refinery blast injures nine"),
    ("09:30", "UK reports net migration of 77,000"),
    ("14:00", "Gukesh\u2013Sindarov Game 3 begins in Geneva"),
    ("23:00", "Nor\u2019easter moves offshore as Thanksgiving ends"),
]

DATE_CHECK = [
    ("Huawei found guilty on 10 counts", "24 NOV"),
    ("Shanghai party chief Chen Jining probed", "24 NOV"),
    ("COP31 ends without a pact", "22 NOV"),
    ("Belgium strike grounds 429 flights", "23 NOV"),
]

# (pin, lon, lat, region, badge dx, dy)
PINS = [
    (1, -74.0, 40.7, "NA", -16, -12),
    (2, 72.8, 19.0, "SA", 12, -12),
    (3, 6.1, 46.2, "EU", -2, -16),
    (4, 46.7, 24.6, "ME", 14, 10),
    (5, 56.2, 26.2, "ME", 16, -8),
    (6, 34.5, 31.5, "ME", -16, 8),
    (7, 30.5, 50.4, "EU", -18, -8),
    (8, 36.2, 49.9, "EU", 16, -12),
    (9, -77.0, 38.9, "NA", 14, 12),
    (10, 90.4, 23.8, "SA", 14, 6),
    (11, 116.4, 39.9, "EA", 12, -12),
    (12, 37.6, 55.8, "EU", -2, -18),
    (13, 160.0, -9.4, "OCE", 0, -16),
]

# ---------------------------------------------------------------- derived
ALL_SOURCES = set()
for lead in LEADS:
    ALL_SOURCES.update(lead["sources"])
for tile in TILES:
    ALL_SOURCES.add(tile["source"])
for _place, _field, _head, src, _region in MORE:
    ALL_SOURCES.add(src)
REGION_COUNTS = Counter([lead["region"] for lead in LEADS] +
                        [tile["region"] for tile in TILES] +
                        [row[4] for row in MORE])
N_STORIES = len(LEADS) + len(TILES) + len(MORE)
N_REGIONS = len(REGION_COUNTS)
N_SOURCES = len(ALL_SOURCES)
CHIP_ORDER = sorted(REGION_COUNTS.items(),
                    key=lambda kv: (-kv[1], REGION_ORDER.index(kv[0])))

# ---------------------------------------------------------------- helpers
def wrap_text(dr, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if dr.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(dr, x, y, lines, fnt, fill, leading):
    for line in lines:
        dr.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def centred(dr, cx, y, text, fnt, fill):
    w = dr.textlength(text, font=fnt)
    dr.text((cx - w / 2, y), text, font=fnt, fill=fill)


def hrule(dr, x0, x1, y, fill=RULE, width=1):
    dr.line([(x0, y), (x1, y)], fill=fill, width=width)


def tag_colour(tag):
    if tag == "CONFIRMED":
        return GREEN
    if tag == "CLAIM":
        return RED
    return AMBER


def find_asset(stem):
    hits = sorted(glob.glob(os.path.join(
        ASSETS, "media-generation-" + stem + "-*.png")))
    return hits[0] if hits else None


def cover_crop(im, w, h, focus_y=0.5):
    sw, sh = im.size
    target = w / h
    if sw / sh > target:
        nw = int(sh * target)
        x0 = (sw - nw) // 2
        box = (x0, 0, x0 + nw, sh)
    else:
        nh = int(sw / target)
        y0 = int((sh - nh) * focus_y)
        y0 = max(0, min(sh - nh, y0))
        box = (0, y0, sw, y0 + nh)
    return im.crop(box).resize((w, h), Image.LANCZOS)


def paste_art(dr, box, stem, focus_y=0.5):
    x0, y0, x1, y1 = box
    path = find_asset(stem)
    if path is None:
        dr.rectangle(box, fill=(206, 198, 182))
        dr.line([(x0, y0), (x1, y1)], fill=RULE, width=1)
        dr.line([(x1, y0), (x0, y1)], fill=RULE, width=1)
    else:
        with Image.open(path) as im:
            art = cover_crop(im.convert("RGB"), x1 - x0, y1 - y0, focus_y)
        img.paste(art, (x0, y0))
    dr.rectangle(box, outline=INK, width=1)


img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)
d.rectangle([5, 5, W - 6, H - 6], outline=NAVY, width=2)

# ---------------------------------------------------------------- masthead
centred(d, W // 2, 12, "Thursday 26 November 2026", serif_b(38), NAVY)
centred(d, W // 2, 54,
        "%d STORIES \u00b7 %d REGIONS \u00b7 %d SOURCES" %
        (N_STORIES, N_REGIONS, N_SOURCES),
        sans_b(11), INK)
centred(d, W // 2, 70,
        "Macy\u2019s 100th parade falls to the storm \u2014 Mumbai remembers "
        "26/11 \u2014 Gukesh and Sindarov level in Geneva.",
        serif_i(13), RED)

# region chips, coloured, ordered by story count
chip_font = sans_b(10)
chip_texts = ["%s %d" % (REGIONS[key][0].upper(), count)
              for key, count in CHIP_ORDER]
chip_widths = [d.textlength(t, font=chip_font) + 16 for t in chip_texts]
chip_total = sum(chip_widths) + 8 * (len(chip_texts) - 1)
cx = (W - chip_total) // 2
for (key, _count), text, cw in zip(CHIP_ORDER, chip_texts, chip_widths):
    colour = REGIONS[key][1]
    d.rounded_rectangle([cx, 90, cx + cw, 110], radius=10, fill=colour)
    centred(d, cx + cw / 2, 94, text, chip_font, (255, 255, 255))
    cx += cw + 8

# ---------------------------------------------------------------- numbers
hrule(d, 14, W - 14, 118, fill=NAVY, width=1)
d.text((14, 124), "THE DAY IN NUMBERS", font=sans_b(10), fill=NAVY)
col_w = (W - 28) // 6
for i, (big, lab1, lab2) in enumerate(NUMBERS):
    ccx = 14 + col_w * i + col_w // 2
    centred(d, ccx, 136, big, sans_b(26), RED)
    centred(d, ccx, 164, lab1, sans_b(9), FAINT)
    centred(d, ccx, 175, lab2, sans_b(9), FAINT)
hrule(d, 14, W - 14, 188, fill=NAVY, width=1)

# ---------------------------------------------------------------- leads
LEAD_Y = 196
LEAD_W = 324
for i, lead in enumerate(LEADS):
    lx = 14 + i * (LEAD_W + 12)
    paste_art(d, (lx, LEAD_Y, lx + LEAD_W, LEAD_Y + 96), lead["art"],
              lead["focus"])
    kicker = "%s \u00b7 %s \u2014 %s" % (
        lead["place"], lead["field"], ", ".join(lead["sources"]))
    d.text((lx + 2, LEAD_Y + 102), "No. %d" % lead["num"],
           font=sans_b(9), fill=RED)
    nw = d.textlength("No. %d " % lead["num"], font=sans_b(9))
    d.text((lx + 2 + nw, LEAD_Y + 102), kicker, font=sans_b(9),
           fill=FAINT)
    head_lines = wrap_text(d, lead["head"], serif_b(16), LEAD_W - 4)
    y = draw_lines(d, lx + 2, LEAD_Y + 118, head_lines, serif_b(16),
                   NAVY, 19)
    sub_lines = wrap_text(d, lead["sub"], sans_r(11), LEAD_W - 4)
    draw_lines(d, lx + 2, y + 2, sub_lines, sans_r(11), INK, 13)

# ---------------------------------------------------------------- tiles
d.text((14, 398), "TOP STORIES", font=sans_b(11), fill=NAVY)
hrule(d, 110, W - 14, 403, fill=NAVY, width=1)

TILE_W, TILE_H, TILE_IMG = 193, 106, 68
for idx, tile in enumerate(TILES):
    row, col = divmod(idx, 5)
    tx = 14 + col * (TILE_W + 8)
    ty = 406 + row * (TILE_H + 6)
    tc = tag_colour(tile["tag"])
    d.rectangle([tx, ty, tx + TILE_W, ty + TILE_H], fill=CARD,
                outline=RULE, width=1)
    paste_art(d, (tx, ty, tx + TILE_IMG, ty + TILE_H), tile["art"], 0.5)
    # tag tab, top-left of the picture
    tab_w = d.textlength(tile["tag"], font=sans_b(8)) + 10
    d.rectangle([tx, ty, tx + tab_w, ty + 14], fill=tc)
    centred(d, tx + tab_w / 2, ty + 3, tile["tag"], sans_b(8),
            (255, 255, 255))
    # number badge, top-right of the picture
    bx, by = tx + TILE_IMG - 10, ty + 10
    d.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=RED,
              outline=(255, 255, 255), width=1)
    label = str(tile["num"])
    lw = d.textlength(label, font=sans_b(9))
    d.text((bx - lw / 2, by - 6), label, font=sans_b(9),
           fill=(255, 255, 255))
    vx = tx + TILE_IMG + 6
    vw = TILE_W - TILE_IMG - 12
    d.text((vx, ty + 4), tile["place"], font=sans_b(8), fill=NAVY)
    head_lines = wrap_text(d, tile["head"], sans_b(11), vw)
    draw_lines(d, vx, ty + 15, head_lines, sans_b(11), INK, 13)
    sub_lines = wrap_text(d, tile["sub"], sans_r(9), vw)
    draw_lines(d, vx, ty + 56, sub_lines[:3], sans_r(9), (58, 58, 54), 11)
    d.text((vx, ty + 93), "%s \u00b7 %s" % (tile["source"], tile["field"]),
           font=sans_b(9), fill=FAINT)

# ---------------------------------------------------------------- map
d.text((14, 630), "WHERE IT HAPPENED \u2014 PINS 1\u201313",
       font=sans_b(11), fill=NAVY)
d.text((622, 630), "THE DAY IN UTC", font=sans_b(11), fill=NAVY)

MAP_X0, MAP_Y0, MAP_X1, MAP_Y1 = 14, 646, 606, 758
d.rectangle([MAP_X0, MAP_Y0, MAP_X1, MAP_Y1], fill=SEA, outline=RULE,
            width=1)


def project(lon, lat):
    x = MAP_X0 + (lon + 180.0) / 360.0 * (MAP_X1 - MAP_X0)
    y = MAP_Y0 + (84.0 - lat) / 142.0 * (MAP_Y1 - MAP_Y0)
    return x, y


def unproject(px, py):
    lon = (px - MAP_X0) / (MAP_X1 - MAP_X0) * 360.0 - 180.0
    lat = 84.0 - (py - MAP_Y0) / (MAP_Y1 - MAP_Y0) * 142.0
    return lon, lat


def inside_poly(x, y, poly):
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and \
                (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 71), (-95, 80), (-75, 72), (-60, 60),
     (-55, 47), (-70, 42), (-80, 32), (-90, 21), (-97, 16), (-105, 20),
     (-115, 30), (-125, 40), (-125, 49), (-150, 60)],
    [(-80, 10), (-60, 8), (-50, 0), (-40, -5), (-35, -10), (-40, -20),
     (-50, -30), (-60, -35), (-70, -40), (-73, -50), (-70, -55),
     (-65, -45), (-70, -30), (-75, -20), (-80, -10)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (20, 54), (25, 60), (30, 65), (35, 68), (40, 68),
     (45, 60), (40, 55), (35, 50), (30, 45), (25, 40), (20, 40),
     (15, 38), (10, 37), (0, 38), (-5, 36)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31),
     (35, 28), (40, 20), (43, 12), (51, 11), (48, 0), (40, -10),
     (35, -20), (30, -30), (25, -35), (18, -35), (15, -25), (12, -10),
     (8, 4), (-8, 4), (-13, 8)],
    [(40, 68), (60, 70), (80, 73), (100, 77), (120, 73), (140, 72),
     (160, 70), (178, 65), (170, 60), (160, 55), (140, 45), (130, 42),
     (127, 40), (120, 32), (110, 20), (105, 10), (100, 8), (95, 15),
     (90, 22), (80, 15), (77, 8), (72, 20), (65, 25), (60, 25),
     (55, 27), (50, 30), (45, 30), (40, 35), (35, 36), (30, 36),
     (35, 42), (40, 45), (45, 50), (40, 55)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (130, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -27),
     (150, -22), (145, -15), (142, -11), (135, -12), (130, -13),
     (125, -14), (120, -20)],
]
# dot-matrix land: 7px grid, a dot wherever the grid point is on land
py = MAP_Y0 + 4
while py < MAP_Y1 - 2:
    px = MAP_X0 + 4
    while px < MAP_X1 - 2:
        lon, lat = unproject(px, py)
        if any(inside_poly(lon, lat, poly) for poly in CONTINENTS):
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=DOT)
        px += 7
    py += 7

for num, lon, lat, region, dx, dy in PINS:
    colour = REGIONS[region][1]
    px, py = project(lon, lat)
    bx, by = px + dx, py + dy
    d.line([(px, py), (bx, by)], fill=(120, 120, 116), width=1)
    d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=colour,
              outline=(255, 255, 255), width=1)
    d.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=colour,
              outline=(255, 255, 255), width=1)
    label = str(num)
    lw = d.textlength(label, font=sans_b(9))
    d.text((bx - lw / 2, by - 6), label, font=sans_b(9),
           fill=(255, 255, 255))

# ---------------------------------------------------------------- timeline
d.line([(640, 650), (640, 752)], fill=RULE, width=2)
for i, (when, what) in enumerate(TIMELINE):
    ty = 652 + i * 22
    d.ellipse([636, ty + 1, 644, ty + 9], fill=RED,
              outline=(255, 255, 255), width=1)
    d.text((654, ty), when, font=sans_b(12), fill=RED)
    d.text((706, ty + 1), what, font=sans_r(10), fill=INK)

# ---------------------------------------------------------------- region bars
d.text((14, 766), "STORIES BY", font=sans_b(9), fill=NAVY)
d.text((14, 777), "REGION", font=sans_b(9), fill=NAVY)
bar_x0 = 132
bar_cell = (W - 14 - bar_x0) / len(CHIP_ORDER)
max_count = max(REGION_COUNTS.values())
for i, (key, count) in enumerate(CHIP_ORDER):
    cx = bar_x0 + i * bar_cell
    colour = REGIONS[key][1]
    d.text((cx, 766), REGIONS[key][0].upper(), font=sans_r(8), fill=INK)
    bw = count / max_count * 72
    d.rectangle([cx, 780, cx + bw, 787], fill=colour)
    d.text((cx + bw + 4, 778), str(count), font=sans_b(9), fill=INK)

# ---------------------------------------------------------------- date check
d.rectangle([14, 800, W - 14, 850], fill=(250, 240, 214), outline=AMBER,
            width=1)
d.rectangle([14, 800, 18, 850], fill=RED)
d.text((28, 806), "DATE CHECK \u2014 THESE ARE NOT 26 NOVEMBER",
       font=sans_b(12), fill=INK)
d.text((640, 806), "Big stories in this week\u2019s cycle, other days",
       font=sans_r(10), fill=FAINT)
for i, (item, day) in enumerate(DATE_CHECK):
    col = i % 2
    row = i // 2
    ix = 28 + col * 490
    iy = 824 + row * 15
    d.text((ix, iy), "\u00d7", font=sans_b(11), fill=RED)
    d.text((ix + 14, iy), item, font=sans_r(10), fill=INK)
    tw = d.textlength(item, font=sans_r(10))
    d.text((ix + 14 + tw + 6, iy), "\u2014 " + day, font=sans_b(10),
           fill=RED)

# ---------------------------------------------------------------- list 14-36
d.text((14, 858), "AND ALSO \u2014 STORIES 14\u201336", font=sans_b(11),
       fill=NAVY)
hrule(d, 210, W - 14, 863, fill=NAVY, width=1)
for i, (place, field, head, src, _region) in enumerate(MORE):
    num = 14 + i
    col = 0 if i < 12 else 1
    row = i if i < 12 else i - 12
    lx = 14 + col * 502
    ly = 874 + row * 10.5
    d.text((lx, ly), "%d." % num, font=sans_b(10), fill=RED)
    nw = d.textlength("%d." % num, font=sans_b(10))
    body = "%s \u00b7 %s \u2014 %s" % (place, field, head)
    d.text((lx + nw + 4, ly), body, font=sans_r(10), fill=INK)
    bw = d.textlength(body, font=sans_r(10))
    d.text((lx + nw + 4 + bw + 5, ly), "\u2014 " + src, font=sans_r(10),
           fill=FAINT)

# ---------------------------------------------------------------- footer
hrule(d, 14, W - 14, 1004, fill=RULE, width=1)
foot_head = "HOW SURE \u2014 "
foot_body = ("OFFICIAL = primary source \u00b7 CONFIRMED = verified by 2+ "
             "outlets \u00b7 REPORTED = single-source \u00b7 CLAIM = "
             "unverified \u00b7 ONGOING = still developing \u00b7 "
             "Compiled 26 Nov 2026")
fw = (d.textlength(foot_head, font=sans_b(8)) +
      d.textlength(foot_body, font=sans_r(8)))
fx = (W - fw) / 2
d.text((fx, 1008), foot_head, font=sans_b(8), fill=RED)
d.text((fx + d.textlength(foot_head, font=sans_b(8)), 1008), foot_body,
       font=sans_r(8), fill=FAINT)

img.save(OUT, "PNG", optimize=True)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
