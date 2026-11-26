#!/usr/bin/env python3
"""Render 'The World in One Day - 25 November 2026' as a one-page newspaper.

A single 1024x1024 PNG: one dominant hero story, three medium stories,
four small stories and twenty-four one-line briefs. Every story was
reported on Wednesday 25 November 2026. Pure Pillow, no network, no
timestamps, no randomness: running this file twice writes identical bytes.
"""
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (26, 26, 26)
NAVY = (16, 42, 74)
CRIMSON = (165, 28, 38)
GOLD = (198, 155, 55)
GRAY = (110, 108, 102)
LIGHT = (233, 227, 214)
TEAL_DARK = (10, 48, 62)
TEAL = (24, 96, 110)
TEAL_LIGHT = (90, 160, 175)
ORANGE = (232, 116, 30)
YELLOW = (245, 196, 66)
SMOKE = (120, 120, 118)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, max_w):
    """Greedy word wrap returning a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def block(d, x, y, text, fnt, max_w, leading, color=INK):
    """Draw wrapped text; return the y just below the last line."""
    for line in wrap(d, text, fnt, max_w):
        d.text((x, y), line, font=fnt, fill=color)
        y += leading
    return y


def vgrad(d, box, top, bottom):
    """Vertical gradient inside box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    span = max(1, y1 - y0)
    for i in range(span):
        t = i / span
        col = tuple(round(top[c] + (bottom[c] - top[c]) * t) for c in range(3))
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=col)


def burst(d, cx, cy, r_out, r_in, points, color):
    """Starburst polygon centred at (cx, cy)."""
    import math
    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.pi * i / points - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=color)


def tanker_scene(d, x0, y0, x1, y1):
    """Night strait: tanker silhouette, mine blast, spiked mines, waves."""
    vgrad(d, (x0, y0, x1, y0 + int((y1 - y0) * 0.55)), (18, 34, 58), (58, 74, 96))
    vgrad(d, (x0, y0 + int((y1 - y0) * 0.55), x1, y1), TEAL_DARK, (8, 34, 46))
    # stars
    for sx, sy in [(0.12, 0.10), (0.30, 0.05), (0.55, 0.12), (0.78, 0.06),
                   (0.90, 0.16), (0.42, 0.18), (0.66, 0.20)]:
        d.ellipse([x0 + sx * (x1 - x0) - 2, y0 + sy * (y1 - y0) - 2,
                   x0 + sx * (x1 - x0) + 2, y0 + sy * (y1 - y0) + 2],
                  fill=(220, 220, 200))
    # explosion above the tanker
    ex, ey = x0 + int((x1 - x0) * 0.62), y0 + int((y1 - y0) * 0.34)
    burst(d, ex, ey, 62, 26, 9, ORANGE)
    burst(d, ex, ey, 40, 16, 9, YELLOW)
    burst(d, ex, ey, 20, 8, 9, (255, 236, 170))
    # smoke puffs
    for px, py, pr in [(0.50, 0.16, 20), (0.66, 0.12, 26), (0.80, 0.18, 18)]:
        d.ellipse([x0 + px * (x1 - x0) - pr, y0 + py * (y1 - y0) - pr,
                   x0 + px * (x1 - x0) + pr, y0 + py * (y1 - y0) + pr],
                  fill=SMOKE)
    # tanker hull and containers
    hx0, hy = x0 + 18, y0 + int((y1 - y0) * 0.62)
    d.polygon([(hx0, hy), (x1 - 18, hy), (x1 - 44, hy + 34), (hx0 + 26, hy + 34)],
              fill=(8, 8, 10))
    for i, col in enumerate([(150, 60, 40), (60, 110, 90), (190, 150, 60)]):
        cx = hx0 + 34 + i * 52
        d.rectangle([cx, hy - 34, cx + 44, hy - 2], fill=col, outline=(10, 10, 10))
    d.rectangle([x1 - 96, hy - 52, x1 - 62, hy - 2], fill=(200, 200, 190))
    # spiked mines floating on the water
    for mx, my, mr in [(0.16, 0.78, 13), (0.38, 0.86, 10), (0.82, 0.82, 12)]:
        cx, cy = x0 + mx * (x1 - x0), y0 + my * (y1 - y0)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-0.7, -0.7), (0.7, 0.7),
                       (-0.7, 0.7), (0.7, -0.7)]:
            d.line([(cx, cy), (cx + dx * (mr + 8), cy + dy * (mr + 8))],
                   fill=(20, 20, 20), width=3)
        d.ellipse([cx - mr, cy - mr, cx + mr, cy + mr], fill=(28, 28, 30),
                  outline=(90, 90, 90))
    # wave arcs
    for wy in (0.70, 0.76, 0.90, 0.95):
        yy = y0 + wy * (y1 - y0)
        for k in range(4):
            ax = x0 + 14 + k * 86
            d.arc([ax, yy - 8, ax + 62, yy + 8], 200, 340, fill=TEAL_LIGHT, width=2)


def refinery_strip(d, x0, y0, x1, y1):
    """Two refinery towers with flames under a dark sky."""
    vgrad(d, (x0, y0, x1, y1), (28, 30, 44), (74, 52, 44))
    base = y1 - 8
    for tx, th in [(0.20, 0.55), (0.62, 0.72)]:
        cx = x0 + tx * (x1 - x0)
        tw = 26
        d.rectangle([cx - tw / 2, y0 + (y1 - y0) * (1 - th), cx + tw / 2, base],
                    fill=(16, 16, 18))
        d.rectangle([cx - tw / 2 - 6, y0 + (y1 - y0) * (1 - th) + 12,
                     cx + tw / 2 + 6, y0 + (y1 - y0) * (1 - th) + 18],
                    fill=(16, 16, 18))
        fx, fy = cx, y0 + (y1 - y0) * (1 - th) - 6
        d.polygon([(fx - 12, fy), (fx, fy - 26), (fx + 12, fy)], fill=ORANGE)
        d.polygon([(fx - 6, fy), (fx, fy - 16), (fx + 6, fy)], fill=YELLOW)
    d.ellipse([x0 + (x1 - x0) * 0.40 - 14, y0 + 8, x0 + (x1 - x0) * 0.40 + 14, y0 + 36],
              fill=SMOKE)
    d.ellipse([x0 + (x1 - x0) * 0.80 - 10, y0 + 14, x0 + (x1 - x0) * 0.80 + 10, y0 + 34],
              fill=SMOKE)


def chart_strip(d, x0, y0, x1, y1):
    """Falling market chart with a red chip."""
    d.rectangle([x0, y0, x1, y1], fill=(255, 255, 255))
    for gy in (0.25, 0.50, 0.75):
        yy = y0 + gy * (y1 - y0)
        d.line([(x0 + 8, yy), (x1 - 8, yy)], fill=(225, 225, 225), width=1)
    pts = [(0.06, 0.22), (0.22, 0.34), (0.38, 0.30), (0.54, 0.55),
           (0.70, 0.52), (0.86, 0.80), (0.96, 0.74)]
    xy = [(x0 + px * (x1 - x0), y0 + py * (y1 - y0)) for px, py in pts]
    d.polygon(xy + [(x1 - 8, y1 - 6), (x0 + 8, y1 - 6)], fill=(244, 214, 214))
    d.line(xy, fill=CRIMSON, width=4, joint="curve")
    for px, py in xy:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=CRIMSON)
    d.rectangle([x1 - 114, y0 + 8, x1 - 10, y0 + 32], fill=CRIMSON)
    d.text((x1 - 106, y0 + 12), "KOSPI -6.2%", font=font(SANS_BOLD, 14), fill=(255, 255, 255))


def tower_strip(d, x0, y0, x1, y1):
    """City tower at dusk with a drone and a small fire."""
    vgrad(d, (x0, y0, x1, y1), (64, 48, 66), (214, 150, 92))
    base = y1 - 6
    d.rectangle([x0 + 30, y0 + 26, x0 + 66, base], fill=(30, 28, 40))
    d.rectangle([x0 + 84, y0 + 44, x0 + 112, base], fill=(44, 40, 54))
    d.rectangle([x0 + 200, y0 + 18, x0 + 246, base], fill=(24, 22, 34))
    for wx in range(38, 60, 10):
        d.rectangle([x0 + wx, y0 + 34, x0 + wx + 5, y0 + 40], fill=(240, 210, 120))
    for wx in range(208, 238, 10):
        d.rectangle([x0 + wx, y0 + 26, x0 + wx + 5, y0 + 32], fill=(240, 210, 120))
    # drone with a dotted trail
    dx, dy = x0 + 160, y0 + 20
    for i in range(5):
        d.ellipse([dx - 40 + i * 9 - 1, dy + 12 + i * 3 - 1,
                   dx - 40 + i * 9 + 1, dy + 12 + i * 3 + 1], fill=(40, 40, 40))
    d.ellipse([dx - 6, dy - 6, dx + 6, dy + 6], fill=(20, 20, 20))
    d.line([(dx - 12, dy), (dx + 12, dy)], fill=(20, 20, 20), width=2)
    burst(d, x0 + 224, y0 + 12, 12, 5, 6, ORANGE)


def icon_court(d, x0, y0, s):
    d.rectangle([x0, y0, x0 + s, y0 + s], fill=NAVY)
    d.polygon([(x0 + 6, y0 + 14), (x0 + s / 2, y0 + 5), (x0 + s - 6, y0 + 14)],
              fill=GOLD)
    for i in range(3):
        cx = x0 + 11 + i * 16
        d.rectangle([cx, y0 + 18, cx + 6, y0 + 40], fill=(240, 236, 224))
    d.rectangle([x0 + 6, y0 + 42, x0 + s - 6, y0 + 47], fill=(240, 236, 224))


def icon_rocket(d, x0, y0, s):
    d.rectangle([x0, y0, x0 + s, y0 + s], fill=TEAL_DARK)
    d.polygon([(x0 + s / 2 - 9, y0 + 12), (x0 + s / 2 + 9, y0 + 12),
               (x0 + s / 2 + 5, y0 + 34), (x0 + s / 2 - 5, y0 + 34)],
              fill=(240, 240, 235))
    d.polygon([(x0 + s / 2, y0 + 4), (x0 + s / 2 - 9, y0 + 14),
               (x0 + s / 2 + 9, y0 + 14)], fill=CRIMSON)
    d.polygon([(x0 + s / 2, y0 + 50), (x0 + s / 2 - 7, y0 + 36),
               (x0 + s / 2 + 7, y0 + 36)], fill=ORANGE)


def icon_flags(d, x0, y0, s):
    d.rectangle([x0, y0, x0 + s, y0 + s], fill=(238, 238, 230))
    d.line([(x0 + 12, y0 + 8), (x0 + 12, y0 + 46)], fill=INK, width=2)
    d.line([(x0 + 34, y0 + 8), (x0 + 34, y0 + 46)], fill=INK, width=2)
    d.polygon([(x0 + 12, y0 + 8), (x0 + 32, y0 + 12), (x0 + 12, y0 + 20)],
              fill=(30, 90, 60))
    d.polygon([(x0 + 34, y0 + 8), (x0 + 52, y0 + 12), (x0 + 34, y0 + 20)],
              fill=CRIMSON)


def icon_leaf(d, x0, y0, s):
    d.rectangle([x0, y0, x0 + s, y0 + s], fill=(36, 84, 52))
    d.ellipse([x0 + 10, y0 + 12, x0 + s - 10, y0 + 36], fill=(120, 190, 110))
    d.line([(x0 + s / 2, y0 + 36), (x0 + s / 2, y0 + 48)], fill=(120, 190, 110),
           width=3)
    d.ellipse([x0 + s / 2 - 3, y0 + 22, x0 + s / 2 + 3, y0 + 28], fill=(36, 84, 52))


HERO_HEAD = "TANKERS ABLAZE AFTER MINE STRIKES IN HORMUZ"
HERO_DECK = ("Iran says two oil tankers hit naval mines and caught fire on an "
             "unauthorised route. Brent nears $92 as Washington tells its "
             "citizens to leave Iran at once.")

MEDIUMS = [
    ("UKRAINE", "DRONES SET TWO REFINERIES ABLAZE",
     "Syzran and Kuibyshev ablaze; one killed. Putin vows revenge.",
     refinery_strip),
    ("MARKETS", "ASIAN STOCKS TUMBLE AS AI FEARS SPREAD",
     "Kospi dives 6.2%, Nikkei falls 2.8%; Nasdaq down 3.2% at midday.",
     chart_strip),
    ("MIDDLE EAST", "HOUTHIS CLAIM STRIKE ON SAUDI REFINERY",
     "Ras Tanura attack claimed a day after a Riyadh strike injured 11.",
     tower_strip),
]

SMALLS = [
    ("TECH", "HUAWEI GUILTY ON 10 COUNTS",
     "Brooklyn jury convicts on fraud and sanctions charges.", icon_court),
    ("SPACE", "PAKISTAN IN ORBIT",
     "Shenzhou-24 docks with Tiangong; Zeeshan Ali aboard.", icon_rocket),
    ("PACIFIC", "AUSTRALIA SIGNS PACT",
     "Solomons treaty bars any foreign military base.", icon_flags),
    ("CLIMATE", "POPE SLAMS COP31 FAILURE",
     "Leo XIV urges stronger action as climate talks collapse.", icon_leaf),
]

BRIEFS = [
    "US plans 20-40% tariffs on 14 partners",
    "Dell record quarter as AI servers soar",
    "Israel kills Hamas security chief",
    "Sudan strikes kill 19 civilians",
    "UN warns of new Israeli attacks in Gaza",
    "Ebola teams flee fighting in DR Congo",
    "Bogor mine flood toll six; 20 trapped",
    "Cartagena hostages freed in dawn raid",
    "Hasina to return to Bangladesh 16 Dec",
    "US pauses joint ops with Ecuador",
    "Poland seeks permanent US presence",
    "US Army destroys 5 tons of explosives",
    "Lille stun Bayern 2-1 in Europe",
    "Isak double in Liverpool 3-0 win",
    "PSG 2-2 Roma; Man Utd 2-2 at Sporting",
    "Barcelona win 4-1; Inter win 2-0",
    "Real Madrid hit five past PSV",
    "UN aid chief arrives in war-hit Yemen",
    "Russian strike kills two in Odesa",
    "490,334 Russian soldiers dead: leak",
    "Three ships hit in strait on Monday",
    "Gavi to buy 1.5m Ebola vaccine doses",
    "Third tanker claimed hit in strait",
    "US tells citizens to leave Iran at once",
]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Top crimson bar and masthead.
    d.rectangle([0, 0, W, 12], fill=CRIMSON)
    mast = font(SERIF, 56)
    d.text((W / 2, 20), "THE WORLD IN ONE DAY", font=mast, fill=NAVY,
           anchor="ma")
    d.rectangle([24, 88, W - 24, 91], fill=GOLD)
    d.rectangle([24, 94, W - 24, 95], fill=INK)
    d.text((W / 2, 102), "WEDNESDAY 25 NOVEMBER 2026",
           font=font(SANS_BOLD, 30), fill=INK, anchor="ma")
    d.rectangle([24, 140, W - 24, 141], fill=INK)

    # Hero: text left, strait scene right.
    hy0, hy1 = 150, 468
    d.rectangle([24, hy0, W - 24, hy1], outline=NAVY, width=2)
    d.text((44, hy0 + 14), "TOP STORY  -  STRAIT OF HORMUZ",
           font=font(SANS_BOLD, 20), fill=CRIMSON)
    y = block(d, 44, hy0 + 44, HERO_HEAD, font(SERIF, 36), 556, 44, NAVY)
    y = block(d, 44, y + 8, HERO_DECK, font(SANS, 18), 556, 24)
    d.text((44, hy1 - 30), "Sources: Reuters, BBC News  -  claims unverified, ships unnamed",
           font=font(SANS, 14), fill=GRAY)
    tanker_scene(d, 624, hy0 + 2, W - 26, hy1 - 2)

    # Three medium stories.
    my0, my1 = 480, 680
    widths = [316, 316, 316]
    xs = [24, 352, 680]
    for (kicker, head, deck, art), x0, w in zip(MEDIUMS, xs, widths):
        d.rectangle([x0, my0, x0 + w, my1], outline=NAVY, width=1)
        art(d, x0 + 1, my0 + 1, x0 + w - 1, my0 + 77)
        d.text((x0 + 10, my0 + 86), kicker, font=font(SANS_BOLD, 14),
               fill=CRIMSON)
        y = block(d, x0 + 10, my0 + 106, head, font(SERIF, 19), w - 20, 24, NAVY)
        block(d, x0 + 10, y + 4, deck, font(SANS, 15), w - 20, 19)

    # Four small stories with icons.
    sy0, sy1 = 692, 808
    sxs = [24, 270, 516, 762]
    for (kicker, head, deck, icon), x0 in zip(SMALLS, sxs):
        d.rectangle([x0, sy0, x0 + 238, sy1], outline=NAVY, width=1)
        icon(d, x0 + 10, sy0 + 10, 54)
        d.text((x0 + 74, sy0 + 10), kicker, font=font(SANS_BOLD, 13),
               fill=CRIMSON)
        y = block(d, x0 + 74, sy0 + 28, head, font(SERIF, 15), 154, 19, NAVY)
        block(d, x0 + 10, y + 6, deck, font(SANS, 13), 218, 16)

    # Briefs band and three columns of eight.
    by0 = 820
    d.rectangle([24, by0, W - 24, by0 + 34], fill=NAVY)
    d.rectangle([24, by0, 40, by0 + 34], fill=GOLD)
    d.text((52, by0 + 6), "ALSO TODAY", font=font(SANS_BOLD, 20),
           fill=(255, 255, 255))
    bf = font(SANS, 15)
    for i, text in enumerate(BRIEFS):
        col, row = i % 3, i // 3
        bx = [24, 352, 680][col]
        by = by0 + 44 + row * 17
        assert d.textlength(text, font=bf) <= 300, text
        d.text((bx, by), "\u25aa", font=bf, fill=GOLD)
        d.text((bx + 14, by), text, font=bf, fill=INK)

    # Footer.
    d.rectangle([24, 1004, W - 24, 1005], fill=INK)
    d.text((W / 2, 1010), "Sources: Reuters  \u00b7  BBC News  \u00b7  Just Security  \u00b7  UEFA",
           font=font(SANS, 13), fill=GRAY, anchor="ma")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, format="PNG")
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()

