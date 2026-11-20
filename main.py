#!/usr/bin/env python3
"""news-image-20261120: draws a one-page newspaper front page summing up
Friday 20 November 2026's world news and writes it to /output/entry.png.

Pure Python 3 standard library only: no network, no third-party packages.
The PNG is encoded by hand (zlib + CRC32) and the text is rendered with a
built-in 5x7 bitmap font, so two runs produce byte-identical output.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette ---
PAPER = (248, 244, 233)
INK = (26, 26, 26)
NAVY = (22, 41, 77)
NAVY_LT = (38, 62, 108)
GOLD = (201, 162, 39)
RED = (178, 39, 30)
GREY = (110, 108, 100)
LIGHT = (233, 228, 214)
SKY = (176, 205, 226)
SEA = (46, 110, 138)
GREEN = (46, 110, 74)

# ------------------------------------------------------------- bitmap font --
# Each glyph: 7 rows of 5 bits, top row first, bit 4 = leftmost pixel.
# Written as seven 5-character strings of '1' (ink) and '0' (blank).
_RAW_FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10001", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "11110", "10001", "10001", "11110", "10000", "10000"),
    "q": ("00000", "01111", "10001", "10001", "01111", "00001", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11110", "01000", "01000", "01000", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "10001", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
}

FONT = {ch: tuple(int(row, 2) for row in rows) for ch, rows in _RAW_FONT.items()}
GLYPH_W, GLYPH_H, GLYPH_ADV = 5, 7, 6


def text_width(text, scale):
    return len(text) * GLYPH_ADV * scale - scale


# -------------------------------------------------------------- pixel buffer -
buf = bytearray([PAPER[0], PAPER[1], PAPER[2]] * (W * H))


def px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i], buf[i + 1], buf[i + 2] = color


def fill_rect(x0, y0, x1, y1, color):
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(W - 1, x1)
    y1 = min(H - 1, y1)
    for y in range(y0, y1 + 1):
        base = (y * W + x0) * 3
        span = (x1 - x0 + 1) * 3
        buf[base:base + span] = bytes(color) * (x1 - x0 + 1)


def hline(x0, x1, y, color, thick=1):
    for t in range(thick):
        fill_rect(x0, y + t, x1, y + t, color)


def vline(x, y0, y1, color, thick=1):
    for t in range(thick):
        fill_rect(x + t, y0, x + t, y1, color)


def line(x0, y0, x1, y1, color, thick=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        for a in range(thick):
            for b in range(thick):
                px(x0 + a, y0 + b, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def circle(cx, cy, r, color, filled=True):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            d = (x - cx) * (x - cx) + (y - cy) * (y - cy)
            if filled:
                if d <= r * r:
                    px(x, y, color)
            else:
                if abs(d - r * r) <= r:
                    px(x, y, color)


def ring(cx, cy, r, color, thick=2):
    for y in range(cy - r - thick, cy + r + thick + 1):
        for x in range(cx - r - thick, cx + r + thick + 1):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if abs(d - r) <= thick / 2:
                px(x, y, color)


def triangle(x0, y0, x1, y1, x2, y2, color):
    minx, maxx = min(x0, x1, x2), max(x0, x1, x2)
    miny, maxy = min(y0, y1, y2), max(y0, y1, y2)
    den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    if den == 0:
        return
    for y in range(miny, maxy + 1):
        for x in range(minx, maxx + 1):
            a = ((y1 - y2) * (x - x2) + (x2 - x1) * (y - y2)) / den
            b = ((y2 - y0) * (x - x2) + (x0 - x2) * (y - y2)) / den
            c = 1 - a - b
            if a >= 0 and b >= 0 and c >= 0:
                px(x, y, color)


# --------------------------------------------------------------------- text --
def draw_text(x, y, text, scale, color):
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT["?"])
        for row in range(GLYPH_H):
            bits = glyph[row]
            for col in range(GLYPH_W):
                if bits >> (4 - col) & 1:
                    fill_rect(cx + col * scale, y + row * scale,
                              cx + (col + 1) * scale - 1,
                              y + (row + 1) * scale - 1, color)
        cx += GLYPH_ADV * scale
    return cx


def draw_text_centered(cx, y, text, scale, color):
    draw_text(cx - text_width(text, scale) // 2, y, text, scale, color)


def wrap_text(text, scale, max_width):
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(x, y, text, scale, color, max_width, line_gap=4):
    for ln in wrap_text(text, scale, max_width):
        draw_text(x, y, ln, scale, color)
        y += GLYPH_H * scale + line_gap
    return y


# -------------------------------------------------------------- PNG encode --
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def png_bytes():
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        raw += buf[y * W * 3:(y + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + _chunk(b"IEND", b"")
    )


# ------------------------------------------------------------ illustrations --
def draw_globe(cx, cy, r, sea_color, land_color):
    circle(cx, cy, r, sea_color)
    ring(cx, cy, r, INK, 3)
    # meridians and parallels
    for k in range(1, 4):
        ring(cx, cy, r * k // 4, (255, 255, 255), 1)
    hline(cx - r, cx + r, cy, (255, 255, 255), 2)
    vline(cx, cy - r, cy + r, (255, 255, 255), 2)
    # simple land blobs
    circle(cx - r // 3, cy - r // 4, r // 4, land_color)
    circle(cx + r // 4, cy + r // 5, r // 5, land_color)
    circle(cx + r // 6, cy - r // 2, r // 6, land_color)


def draw_storm(cx, cy, r):
    # spiral cyclone: concentric broken arcs
    for k in range(5, 0, -1):
        rr = r * k // 5
        for deg in range(0, 360, 4):
            import math
            a = math.radians(deg + k * 55)
            x = int(cx + rr * math.cos(a))
            y = int(cy + rr * math.sin(a) * 0.8)
            px(x, y, SEA)
            px(x + 1, y, SEA)
    circle(cx, cy, r // 5, RED)


def draw_scales(cx, cy, s):
    # scales of justice, s = overall width
    vline(cx, cy - 40, cy + 42, INK, 3)
    hline(cx - s // 2, cx + s // 2, cy - 40, INK, 3)
    circle(cx, cy - 46, 5, GOLD)
    for side in (-1, 1):
        x = cx + side * s // 2
        line(x, cy - 40, x - 14, cy - 8, INK, 2)
        line(x, cy - 40, x + 14, cy - 8, INK, 2)
        hline(x - 16, x + 16, cy - 8, INK, 2)
        triangle(x - 16, cy - 8, x + 16, cy - 8, x, cy + 16, GOLD)
    hline(cx - 24, cx + 24, cy + 42, INK, 3)


def draw_skyline(x0, y0, x1, y1, color):
    # simple city silhouette with two missile arcs above it
    import math
    base = y1
    step = (x1 - x0) // 6
    heights = [20, 30, 16, 36, 22, 28]
    for i, hh in enumerate(heights):
        fill_rect(x0 + i * step + 3, base - hh, x0 + (i + 1) * step - 3, base, color)
    for k in range(2):
        cx = x0 + 40 + k * 130
        for deg in range(0, 181, 3):
            a = math.radians(deg)
            px(int(cx + 46 * math.cos(a)), int(y0 + 30 - 20 * math.sin(a)), RED)
            px(int(cx + 46 * math.cos(a)) + 1, int(y0 + 30 - 20 * math.sin(a)), RED)


def draw_spacecraft(cx, cy, color):
    # small probe: dish + body + boom
    fill_rect(cx - 26, cy - 6, cx + 26, cy + 6, color)
    triangle(cx - 26, cy - 6, cx - 44, cy - 18, cx - 26, cy + 6, GOLD)
    line(cx + 26, cy, cx + 52, cy - 14, color, 3)
    circle(cx + 54, cy - 16, 4, RED)


# ------------------------------------------------------------------ layout --
def draw_page():
    # frame
    fill_rect(0, 0, W - 1, 7, NAVY)
    fill_rect(0, H - 8, W - 1, H - 1, NAVY)
    fill_rect(0, 0, 7, H - 1, NAVY)
    fill_rect(W - 8, 0, W - 1, H - 1, NAVY)

    # ---- masthead ----
    fill_rect(8, 8, W - 9, 148, NAVY)
    draw_text_centered(W // 2, 26, "THE WORLD TODAY", 7, (255, 255, 255))
    draw_text_centered(W // 2, 92, "FRIDAY, 20 NOVEMBER 2026", 3, GOLD)
    draw_text_centered(W // 2, 122, "THE DAY'S WORLD NEWS - IN ONE PICTURE",
                       2, (200, 208, 224))

    # ---- lead story: Trump / Iran ----
    lx, ly, lw = 28, 168, 600
    draw_text(lx, ly, "WASHINGTON  -  LEAD STORY", 2, RED)
    y = ly + 26
    y = draw_para(lx, y, "TRUMP DELAYS IRAN DECISION TO 2027", 4, INK, lw, 8)
    y += 6
    y = draw_para(
        lx, y,
        "The US president says he is in \"no rush\" and will decide on any "
        "new strikes after 1 January, as Israel's envoy warns Israel may "
        "act alone against Tehran.",
        2, INK, lw, 6)
    # lead art: globe + clock banner
    ax, ay = 660, 168
    draw_globe(830, 300, 96, SKY, GREEN)
    fill_rect(660, 402, 996, 436, RED)
    draw_text_centered(828, 410, "NO DECISION UNTIL 2027", 2, (255, 255, 255))
    hline(28, 996, 452, INK, 2)

    # ---- cyclone box (right of lead, below art) ----
    # (placed under the lead art to balance the page)
    # ---- row B: three stories ----
    by = 472
    cols = [(28, 316), (360, 316), (692, 316)]
    stories = [
        ("INDIA", RED, "CYCLONE AKVAN HITS INDIA'S EAST COAST",
         "The storm crosses near Gopalpur, Odisha, with winds near "
         "100 km/h. About 300,000 people are moved to shelters and "
         "dozens of trains are cancelled."),
        ("THE HAGUE", RED, "WORLD COURT: MYANMAR GUILTY OF ROHINGYA GENOCIDE",
         "The International Court of Justice rules 9-6 that Myanmar "
         "committed genocide in its 2017 crackdown - the first time "
         "the court has found a state guilty."),
        ("ANTALYA", RED, "COP31 CLOSES WITHOUT FOSSIL-FUEL DEAL",
         "Climate talks end with a draft that drops any fossil-fuel "
         "phase-out, while promising $120bn a year in adaptation "
         "finance by 2035."),
    ]
    for (cx0, cw), (kick, kc, head, body) in zip(cols, stories):
        draw_text(cx0, by, kick, 2, kc)
        yy = by + 24
        yy = draw_para(cx0, yy, head, 3, INK, cw, 6)
        yy += 4
        draw_para(cx0, yy, body, 2, INK, cw, 5)
    hline(28, 996, 700, INK, 2)

    # ---- row C: Kyiv + Voyager ----
    cy = 720
    # Kyiv, left half
    draw_text(28, cy, "KYIV", 2, RED)
    y = draw_para(28, cy + 24, "KYIV HIT BY FOUR BALLISTIC MISSILES", 3, INK, 460, 6)
    draw_para(28, y + 6,
              "Russia strikes the capital overnight. Europe's leaders "
              "say they are ready for talks with Moscow.",
              2, INK, 460, 5)
    draw_skyline(28, cy + 140, 488, cy + 176, NAVY)
    vline(508, 720, 888, GREY, 1)
    # Voyager, right half
    draw_text(528, cy, "SPACE", 2, RED)
    y = draw_para(528, cy + 24, "VOYAGER 1 PASSES ONE LIGHT-DAY FROM EARTH",
                  3, INK, 468, 6)
    draw_para(528, y + 6,
              "NASA confirms the 1977 probe is the first human-made "
              "object more than 24 light-hours away - about 26 billion "
              "km - and still phoning home.",
              2, INK, 468, 5)
    # spacecraft below the body text, in the clear space at lower right
    draw_spacecraft(880, 878, NAVY)
    hline(28, 996, 904, INK, 2)

    # ---- ticker ----
    draw_text(28, 920, "ALSO TODAY", 2, RED)
    draw_para(28, 946,
              "Genoa airport shut by mystery drones - Tanker hits a mine "
              "east of the Strait of Hormuz - Houthis claim strikes on "
              "four Saudi targets - GTA 6 sales pass $1.8bn.",
              2, INK, 968, 5)

    # ---- footer ----
    draw_text_centered(
        W // 2, 992,
        "ALL STORIES REPORTED FRIDAY 20 NOVEMBER 2026  -  SOURCES: REUTERS, BBC, THE HINDU, IMD, NASA",
        1, GREY)


def main():
    draw_page()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png_bytes())


if __name__ == "__main__":
    main()
