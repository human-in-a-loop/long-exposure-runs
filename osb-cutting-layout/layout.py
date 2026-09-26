"""Final 11-sheet OSB cutting plan: validation + drawings.

Sheet coordinates: x runs along the 96" length, y across the 48" width.
Every piece is (label, part, x, y, length_along_x, width_along_y).
Run:  python3 layout.py   -> checks the plan, writes drawings/*.svg
"""
import os
from collections import defaultdict

SHEET_L, SHEET_W, KERF = 96.0, 48.0, 0.125

# Finished rectangles (inches) as given
PARTS = {
    "Floor": (61, 82), "Ceiling": (61, 82),
    "Side wall A": (90, 82), "Side wall B": (87, 82),
    "Front wall A": (87, 17), "Front wall B": (87, 17.5),
    "Front wall C": (75, 25.5), "Front wall D": (11.75, 25.5),
    "Back wall": (60, 87), "Inside ceiling": (72.5, 50.5),
    "Inside side wall": (77.5, 71),
}

# How each part is assembled: list of panel sizes, and the seam direction.
ASSEMBLY = {
    "Floor": "48 × 82 + 13 × 82 (seam runs the 82″ way)",
    "Ceiling": "48 × 82 + 13 × 82 (seam runs the 82″ way)",
    "Side wall A": "90 × 48 + 90 × 34 (seam runs the 90″ way)",
    "Side wall B": "87 × 48 + 87 × 34 (seam runs the 87″ way)",
    "Back wall": "48 × 87 + 12 × 87 (seam runs the 87″ way)",
    "Inside ceiling": "72.5 × 37.75 + 72.5 × 12.75 (seam runs the 72.5″ way)",
    "Inside side wall": "77.5 × 48 + 77.5 × 23 (seam runs the 77.5″ way)",
    "Front wall A": "48 × 17 + 39 × 17 (one short seam across the 17″ height)",
    "Front wall B": "one piece",
    "Front wall C": "one piece",
    "Front wall D": "one piece",
}

# (title, pieces, cuts). cut = (x1, y1, x2, y2, instruction)
SHEETS = [
    ("Floor, main panel",
     [("Floor 1/2", "Floor", 0, 0, 82, 48)],
     [(82, 0, 82, 48, "Crosscut the full sheet at 82″.")]),
    ("Ceiling, main panel",
     [("Ceiling 1/2", "Ceiling", 0, 0, 82, 48)],
     [(82, 0, 82, 48, "Crosscut the full sheet at 82″.")]),
    ("Side wall A, main panel",
     [("Side wall A 1/2", "Side wall A", 0, 0, 90, 48)],
     [(90, 0, 90, 48, "Crosscut the full sheet at 90″.")]),
    ("Side wall B, main panel",
     [("Side wall B 1/2", "Side wall B", 0, 0, 87, 48)],
     [(87, 0, 87, 48, "Crosscut the full sheet at 87″.")]),
    ("Back wall, main panel",
     [("Back wall 1/2", "Back wall", 0, 0, 87, 48)],
     [(87, 0, 87, 48, "Crosscut the full sheet at 87″.")]),
    ("Inside side wall + Front wall A",
     [("Inside side wall 1/2", "Inside side wall", 0, 0, 77.5, 48),
      ("Front wall A 1/2", "Front wall A", 77.625, 0, 17, 48)],
     [(77.5, 0, 77.5, 48, "Crosscut the full sheet at 77.5″."),
      (94.625, 0, 94.625, 48, "Crosscut the 18⅜″ offcut at 17″ (1¼″ scrap).")]),
    ("Side wall A + Floor strips",
     [("Side wall A 2/2", "Side wall A", 0, 0, 90, 34),
      ("Floor 2/2", "Floor", 0, 34.125, 82, 13)],
     [(0, 34, 96, 34, "Rip the full length at 34″."),
      (90, 0, 90, 34, "Crosscut the 34″ strip at 90″."),
      (0, 47.125, 96, 47.125, "Rip the 13⅞″ strip down to 13″."),
      (82, 34.125, 82, 47.125, "Crosscut the 13″ strip at 82″.")]),
    ("Side wall B + Ceiling strips",
     [("Side wall B 2/2", "Side wall B", 0, 0, 87, 34),
      ("Ceiling 2/2", "Ceiling", 0, 34.125, 82, 13)],
     [(0, 34, 96, 34, "Rip the full length at 34″."),
      (87, 0, 87, 34, "Crosscut the 34″ strip at 87″."),
      (0, 47.125, 96, 47.125, "Rip the 13⅞″ strip down to 13″."),
      (82, 34.125, 82, 47.125, "Crosscut the 13″ strip at 82″.")]),
    ("Front walls C, D and B",
     [("Front wall C", "Front wall C", 0, 0, 75, 25.5),
      ("Front wall D", "Front wall D", 75.125, 0, 11.75, 25.5),
      ("Front wall B", "Front wall B", 0, 25.625, 87, 17.5)],
     [(0, 25.5, 96, 25.5, "Rip the full length at 25.5″."),
      (0, 43.125, 96, 43.125, "Rip the remaining 22⅜″ strip at 17.5″ (4¾″ scrap)."),
      (75, 0, 75, 25.5, "Crosscut the 25.5″ strip at 75″ → Front wall C."),
      (86.875, 0, 86.875, 25.5, "Crosscut the 20⅞″ offcut at 11.75″ → Front wall D."),
      (87, 25.625, 87, 43.125, "Crosscut the 17.5″ strip at 87″ → Front wall B.")]),
    ("Inside side wall, Back wall, Inside ceiling strips",
     [("Inside side wall 2/2", "Inside side wall", 0, 0, 77.5, 23),
      ("Back wall 2/2", "Back wall", 0, 23.125, 87, 12),
      ("Inside ceiling 2/2", "Inside ceiling", 0, 35.25, 72.5, 12.75)],
     [(0, 23, 96, 23, "Rip the full length at 23″."),
      (0, 35.125, 96, 35.125, "Rip the remaining strip at 12″. What is left (≈12¾″) is the Inside ceiling strip: measure it."),
      (77.5, 0, 77.5, 23, "Crosscut the 23″ strip at 77.5″."),
      (87, 23.125, 87, 35.125, "Crosscut the 12″ strip at 87″."),
      (72.5, 35.25, 72.5, 48, "Crosscut the ≈12¾″ strip at 72.5″.")]),
    ("Inside ceiling + Front wall A",
     [("Inside ceiling 1/2", "Inside ceiling", 0, 0, 72.5, 37.75),
      ("Front wall A 2/2", "Front wall A", 72.625, 0, 17, 39)],
     [(72.5, 0, 72.5, 48, "Crosscut the full sheet at 72.5″."),
      (0, 37.75, 72.5, 37.75, "Rip the 72.5″ piece to 50.5″ minus the strip measured on sheet 10 (37.75″ if it was 12.75″)."),
      (89.625, 0, 89.625, 48, "Crosscut the 23⅜″ offcut at 17″."),
      (72.625, 39, 89.625, 39, "Rip that 17″ piece to 39″.")]),
]


def validate():
    eps = 1e-6
    area = defaultdict(float)
    for i, (title, pieces, cuts) in enumerate(SHEETS, 1):
        for (lab, part, x, y, l, w) in pieces:
            assert x >= -eps and y >= -eps and x + l <= SHEET_L + eps and y + w <= SHEET_W + eps, (i, lab)
            area[part] += l * w
        for a in range(len(pieces)):
            for b in range(a + 1, len(pieces)):
                _, _, x1, y1, l1, w1 = pieces[a]
                _, _, x2, y2, l2, w2 = pieces[b]
                sep = (x1 + l1 + KERF <= x2 + eps or x2 + l2 + KERF <= x1 + eps or
                       y1 + w1 + KERF <= y2 + eps or y2 + w2 + KERF <= y1 + eps)
                assert sep, f"sheet {i}: {pieces[a][0]} overlaps / no kerf with {pieces[b][0]}"
    for part, (a, b) in PARTS.items():
        assert abs(area[part] - a * b) < 1e-6, (part, area[part], a * b)
    n_cuts = sum(len(s[2]) for s in SHEETS)
    n_panels = sum(len(s[1]) for s in SHEETS)
    return len(SHEETS), n_cuts, n_panels


# ---------- drawings ----------
COLORS = {
    "Floor": "#9FB7C9", "Ceiling": "#A9C4A0", "Side wall A": "#D9A77E",
    "Side wall B": "#C9A0C0", "Back wall": "#E3C86F", "Inside ceiling": "#8FC7BE",
    "Inside side wall": "#B8A6DD", "Front wall A": "#E39A94", "Front wall B": "#A7B98A",
    "Front wall C": "#D8B48E", "Front wall D": "#9DB5D8",
}
S = 8.0            # px per inch
PAD_L, PAD_T, PAD_R, PAD_B = 56, 44, 20, 40
STANDALONE_CSS = """
.sheet{fill:#EFE3C8;stroke:#6B5B45;stroke-width:1.5}
.waste{fill:url(#hatch)}
.piece{stroke:#3A3128;stroke-width:1}
.lab{font:600 12px 'IBM Plex Sans Condensed',Arial,sans-serif;fill:#1F1A14}
.dim{font:11px 'IBM Plex Mono',monospace;fill:#1F1A14}
.dimline{stroke:#6B5B45;stroke-width:.8;fill:none}
.axis{font:11px 'IBM Plex Mono',monospace;fill:#6B5B45}
.cut{stroke:#C0392B;stroke-width:2.2;stroke-dasharray:7 4}
.cutdot{fill:#C0392B}
.cutnum{font:700 11px 'IBM Plex Mono',monospace;fill:#fff}
.hatchline{stroke:#B9A887;stroke-width:1}
"""


def fmt(v):
    whole = int(v)
    frac = round((v - whole) * 8)
    if frac == 8:
        whole, frac = whole + 1, 0
    fr = {0: "", 1: "⅛", 2: "¼", 3: "⅜", 4: "½", 5: "⅝", 6: "¾", 7: "⅞"}[frac]
    return f"{whole}{fr}″" if whole else f"{fr}″"


def X(x): return PAD_L + x * S
def Y(y): return PAD_T + y * S


def svg_open(standalone, title):
    w = PAD_L + SHEET_L * S + PAD_R
    h = PAD_T + SHEET_W * S + PAD_B
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="{title}">']
    out.append('<defs><pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
               '<rect width="8" height="8" class="hatchbg" fill="#EFE3C8"/><line x1="0" y1="0" x2="0" y2="8" class="hatchline"/></pattern></defs>')
    if standalone:
        out.append(f"<style>{STANDALONE_CSS}</style>")
    out.append(f'<rect class="sheet" x="{X(0)}" y="{Y(0)}" width="{SHEET_L*S}" height="{SHEET_W*S}"/>')
    out.append(f'<rect class="waste" x="{X(0)}" y="{Y(0)}" width="{SHEET_L*S}" height="{SHEET_W*S}"/>')
    # axis labels
    out.append(f'<text class="axis" x="{X(0)}" y="{Y(SHEET_W)+30}">0</text>')
    out.append(f'<text class="axis" x="{X(SHEET_L)}" y="{Y(SHEET_W)+30}" text-anchor="end">96″ (8 ft)</text>')
    out.append(f'<text class="axis" x="{X(0)-8}" y="{Y(SHEET_W)}" text-anchor="end">48″</text>')
    out.append(f'<text class="axis" x="{X(0)-8}" y="{Y(0)+10}" text-anchor="end">0</text>')
    return out


def piece_rects(pieces, faded=False):
    out = []
    for (lab, part, x, y, l, w) in pieces:
        op = ' fill-opacity=".45"' if faded else ""
        if faded:
            out.append(f'<rect class="under" x="{X(x):.2f}" y="{Y(y):.2f}" width="{l*S:.2f}" height="{w*S:.2f}" fill="#FFFFFF"/>')
        out.append(f'<rect class="piece" x="{X(x):.2f}" y="{Y(y):.2f}" width="{l*S:.2f}" height="{w*S:.2f}" fill="{COLORS[part]}"{op}/>')
    return out


def rulers(pieces):
    """Tick marks measured from the sheet's top-left corner at every piece edge."""
    out = []
    xs = sorted({round(p[2] + p[4], 3) for p in pieces if p[2] + p[4] < SHEET_L - 0.01})
    last, row = -99, 0
    for xv in xs:
        row = 1 - row if X(xv) - last < 44 else 0
        last = X(xv)
        ty = Y(0) - 6 - 13 * row
        out.append(f'<line class="dimline" x1="{X(xv):.1f}" y1="{ty+2:.1f}" x2="{X(xv):.1f}" y2="{Y(0)}"/>')
        out.append(f'<text class="dim" x="{X(xv):.1f}" y="{ty:.1f}" text-anchor="middle">{fmt(xv)}</text>')
    ys = sorted({round(p[3] + p[5], 3) for p in pieces if p[3] + p[5] < SHEET_W - 0.01})
    lasty = -99
    for yv in ys:
        dy = 0 if Y(yv) - lasty > 12 else 10
        lasty = Y(yv) + dy
        out.append(f'<line class="dimline" x1="{X(0)-6}" y1="{Y(yv):.1f}" x2="{X(0)}" y2="{Y(yv):.1f}"/>')
        out.append(f'<text class="dim" x="{X(0)-8}" y="{Y(yv)+4+dy:.1f}" text-anchor="end">{fmt(yv)}</text>')
    return out


def layout_svg(title, pieces, standalone):
    out = svg_open(standalone, f"Layout: {title}")
    out += piece_rects(pieces)
    for (lab, part, x, y, l, w) in pieces:
        cx, cy = X(x + l / 2), Y(y + w / 2)
        if w >= 11:
            out.append(f'<text class="lab" x="{cx:.1f}" y="{cy-3:.1f}" text-anchor="middle">{lab}</text>')
            out.append(f'<text class="dim" x="{cx:.1f}" y="{cy+12:.1f}" text-anchor="middle">{fmt(l)} × {fmt(w)}</text>')
        else:
            out.append(f'<text class="lab" x="{cx:.1f}" y="{cy+4:.1f}" text-anchor="middle">{lab} · {fmt(l)} × {fmt(w)}</text>')
    out += rulers(pieces)
    return "\n".join(out + ["</svg>"])


def cuts_svg(title, pieces, cuts, standalone):
    out = svg_open(standalone, f"Cut sequence: {title}")
    out += piece_rects(pieces, faded=True)
    out += rulers(pieces)
    for n, (x1, y1, x2, y2, _) in enumerate(cuts, 1):
        out.append(f'<line class="cut" x1="{X(x1):.1f}" y1="{Y(y1):.1f}" x2="{X(x2):.1f}" y2="{Y(y2):.1f}"/>')
    for n, (x1, y1, x2, y2, _) in enumerate(cuts, 1):
        if x1 == x2:  # crosscut: badge near the start of the line
            bx, by = X(x1), Y(min(y1, y2)) + 14 + 0 * n
        else:        # rip: badge a little in from the left end
            bx, by = X(min(x1, x2)) + 22 + 30 * (n % 2), Y(y1)
        out.append(f'<circle class="cutdot" cx="{bx:.1f}" cy="{by:.1f}" r="9"/>')
        out.append(f'<text class="cutnum" x="{bx:.1f}" y="{by+4:.1f}" text-anchor="middle">{n}</text>')
    return "\n".join(out + ["</svg>"])


def main():
    n_sheets, n_cuts, n_panels = validate()
    here = os.path.dirname(os.path.abspath(__file__))
    d = os.path.join(here, "drawings")
    os.makedirs(d, exist_ok=True)
    for i, (title, pieces, cuts) in enumerate(SHEETS, 1):
        with open(os.path.join(d, f"sheet{i:02d}_layout.svg"), "w") as f:
            f.write(layout_svg(title, pieces, True))
        with open(os.path.join(d, f"sheet{i:02d}_cuts.svg"), "w") as f:
            f.write(cuts_svg(title, pieces, cuts, True))
    print(f"OK: {n_sheets} sheets, {n_cuts} cuts, {n_panels} panels; drawings in {d}")


if __name__ == "__main__":
    main()
