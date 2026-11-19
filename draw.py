#!/usr/bin/env python3
"""Draw the 18 November 2026 world-news front page (1024x1024 PNG). v2.

A photo-led broadsheet front page: masthead, one big summit photograph,
and a four-column below-the-fold grid. All photography is AI-generated
photojournalistic imagery made for this entry (see assets/); all type is
set with Pillow. Rendered at 2x and downscaled for crisp type.

Stories (all reported 18 Nov 2026, same verified set as v1):
  HERO  Shenzhen: Xi meets Putin at APEC; Trump lands for US-China-Russia talks
  1     Gulf: Iran drones target US bases in Kuwait/Bahrain; US strikes Qeshm Island
  2     Ukraine: 141 Russian drones overnight, 126 downed, six hurt in Dnipro
  3     Alaska: Peltola flips Senate seat; Democrats 56-44; first Alaska Native senator
  4     Health: US loses measles elimination status after 26 years; 5,412 cases
"""
import os

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")

SS = 2  # supersample factor; final image is 1024x1024
W = H = 1024

PAPER = (248, 244, 233)
INK = (18, 20, 26)
RED = (178, 34, 28)
GREY = (106, 99, 89)
HAIR = (196, 188, 170)

NOTO = "/usr/share/fonts/truetype/noto"
SERIF_BLACK = f"{NOTO}/NotoSerif-Black.ttf"
SERIF_BOLD = f"{NOTO}/NotoSerif-Bold.ttf"
SERIF_REG = f"{NOTO}/NotoSerif-Regular.ttf"
SERIF_IT = f"{NOTO}/NotoSerif-Italic.ttf"
SANS_BOLD = f"{NOTO}/NotoSans-Bold.ttf"
SANS_SEMI = f"{NOTO}/NotoSans-SemiBold.ttf"
SANS_REG = f"{NOTO}/NotoSans-Regular.ttf"


def F(path, size):
    return ImageFont.truetype(path, int(size * SS))


def tw(d, s, f):
    return d.textbbox((0, 0), s, font=f)[2] / SS


def fit_font(d, s, path, size, max_w, min_size=12):
    while size > min_size and tw(d, s, F(path, size)) > max_w:
        size -= 1
    return F(path, size), size


def center(d, cx, y, s, f, fill):
    d.text(((cx - tw(d, s, f) / 2) * SS, y * SS), s, font=f, fill=fill)


def tracked(d, x, y, s, f, fill, tracking=2.0):
    """Draw letter-spaced text starting at x; return its width (unscaled px)."""
    cx = x
    for ch in s:
        d.text((cx * SS, y * SS), ch, font=f, fill=fill)
        cx += tw(d, ch, f) + (tracking if ch != " " else tracking * 2)
    return cx - x - tracking


def tracked_center(d, cx, y, s, f, fill, tracking=2.0):
    total = sum(tw(d, ch, f) + (tracking if ch != " " else tracking * 2) for ch in s) - tracking
    tracked(d, cx - total / 2, y, s, f, fill, tracking)
    return total


def wrap(d, s, f, max_w):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if tw(d, t, f) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def photo(name, box_w, box_h, centering=(0.5, 0.5)):
    im = Image.open(os.path.join(ASSETS, name)).convert("RGB")
    im = ImageOps.fit(im, (int(box_w * SS), int(box_h * SS)),
                      method=Image.LANCZOS, centering=centering)
    im = ImageEnhance.Color(im).enhance(1.06)
    im = ImageEnhance.Contrast(im).enhance(1.05)
    im = ImageEnhance.Sharpness(im).enhance(1.15)
    return im


def paste_photo(img, d, name, x, y, w, h, centering=(0.5, 0.5), border=2):
    img.paste(photo(name, w, h, centering), (int(x * SS), int(y * SS)))
    d.rectangle([x * SS, y * SS, (x + w) * SS - 1, (y + h) * SS - 1],
                outline=INK, width=int(border * SS))


img = Image.new("RGB", (W * SS, H * SS), PAPER)
d = ImageDraw.Draw(img)

M = 28                      # page margin
CW = W - 2 * M              # content width = 968

# ---------------- masthead ----------------
d.rectangle([0, 10 * SS, W * SS, 15 * SS], fill=INK)
center(d, W // 2, 26, "THE WORLD IN ONE IMAGE", F(SERIF_BLACK, 63), INK)
d.line([M * SS, 104 * SS, (W - M) * SS, 104 * SS], fill=INK, width=SS)
finfo = F(SANS_SEMI, 14.5)
d.text((M * SS, 112 * SS), "WEDNESDAY 18 NOVEMBER 2026", font=finfo, fill=INK)
tracked_center(d, W // 2, 112, "GLOBAL EDITION", finfo, GREY, 2.5)
r = "FIVE STORIES · ONE DAY"
d.text(((W - M - tw(d, r, finfo)) * SS, 112 * SS), r, font=finfo, fill=INK)
d.rectangle([M * SS, 136 * SS, (W - M) * SS, 140 * SS], fill=INK)
d.line([M * SS, 143 * SS, (W - M) * SS, 143 * SS], fill=INK, width=SS)

# ---------------- hero ----------------
tracked(d, M, 156, "APEC SUMMIT — SHENZHEN", F(SANS_BOLD, 16), RED, 2.5)
lead = "THE LEAD STORY"
flead = F(SANS_BOLD, 16)
d.text(((W - M - tw(d, lead, flead)) * SS, 156 * SS), lead, font=flead, fill=GREY)

fh, _ = fit_font(d, "Three Powers Meet in Shenzhen", SERIF_BLACK, 74, CW)
center(d, W // 2, 178, "Three Powers Meet in Shenzhen", fh, INK)
deck = "Xi hosts Putin at APEC  •  Trump lands for the first US–China–Russia talks"
center(d, W // 2, 240, deck, F(SERIF_IT, 22.5), (52, 52, 58))

HY, HH = 272, 348
paste_photo(img, d, "media-generation-hero-summit-0-67710fe2-5f0b-4dea-9f50-c62318c2fb5c.webp",
            M, HY, CW, HH, centering=(0.5, 0.40), border=3)
cap = "The flags of China, Russia and the United States stand over the summit table in Shenzhen."
center(d, W // 2, HY + HH + 8, cap, F(SERIF_IT, 16), GREY)

GY = HY + HH + 44           # grid top = 664
d.line([M * SS, (GY - 12) * SS, (W - M) * SS, (GY - 12) * SS], fill=INK, width=int(2 * SS))

# ---------------- story grid: 4 columns ----------------
GUT = 18
COLW = (CW - 3 * GUT) / 4   # 228.5
PH = 128                    # column photo height

STORIES = [
    dict(img="media-generation-story-gulf-0-59c54827-e507-4e2e-aaf1-b0461ce6dc47.webp",
         center=(0.42, 0.30), kicker="MIDDLE EAST — THE GULF",
         head="Iran Drones Hit at US Gulf Bases",
         body="Kuwait & Bahrain intercept; US strikes Qeshm Island."),
    dict(img="media-generation-story-ukraine-0-7471e579-2ff9-4585-8f0d-0135950883f6.webp",
         center=(0.5, 0.38), kicker="EUROPE — UKRAINE",
         head="141 Drones Over Ukraine in One Night",
         body="Kyiv downs 126 of the swarm; six hurt in Dnipro."),
    dict(img="media-generation-story-capitol-0-6dc9eae9-3769-46b7-a3d3-028d0a2b4f6e.webp",
         center=(0.5, 0.26), kicker="AMERICA — THE SENATE",
         head="Peltola Flips Alaska Senate Seat",
         body="First Alaska Native senator; Dems take the Senate 56–44."),
    dict(img="media-generation-story-vaccine-0-13cb0073-cb2b-4b81-a790-0e40d8b8f217.webp",
         center=(0.5, 0.55), kicker="HEALTH — UNITED STATES",
         head="US Loses Measles-Free Status",
         body="Held for 26 years. 5,412 cases — the worst toll since 1991."),
]

for i, st in enumerate(STORIES):
    x = M + i * (COLW + GUT)
    if i > 0:  # hairline separator between columns
        sx = x - GUT / 2
        d.line([sx * SS, GY * SS, sx * SS, 972 * SS], fill=HAIR, width=SS)
    paste_photo(img, d, st["img"], x, GY, COLW, PH, centering=st["center"], border=2)
    y = GY + PH + 9
    tracked(d, x, y, st["kicker"], F(SANS_BOLD, 12.5), RED, 1.2)
    y += 21
    fh2 = F(SERIF_BOLD, 23.5)
    for ln in wrap(d, st["head"], fh2, COLW):
        d.text((x * SS, y * SS), ln, font=fh2, fill=INK)
        y += 28
    y += 3
    fb = F(SERIF_REG, 16.5)
    for ln in wrap(d, st["body"], fb, COLW):
        d.text((x * SS, y * SS), ln, font=fb, fill=(52, 52, 58))
        y += 21.5
    if y > 976:
        print(f"WARNING: column {i} overflows to y={y:.0f}")

# ---------------- footer ----------------
d.rectangle([M * SS, 984 * SS, (W - M) * SS, 987 * SS], fill=INK)
tracked_center(d, W // 2, 994, "ONE DAY · FIVE STORIES · THE WORLD IN ONE IMAGE",
               F(SANS_SEMI, 13.5), INK, 2.0)

img = img.resize((W, H), Image.LANCZOS)
out = os.path.join(HERE, "entry.png")
img.save(out, optimize=True)
print("saved", out, img.size)
