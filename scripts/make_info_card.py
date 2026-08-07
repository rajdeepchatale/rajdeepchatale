"""
Generate a neofetch-style info card as an animated SVG.

Designed to sit beside the ASCII portrait in the same terminal-window aesthetic.
Each line fades + slides in with a stagger. The card uses SMIL animations
compatible with GitHub's SVG renderer.

Set STATIC=1 to emit a frozen frame for Quick Look previews.

    python scripts/make_info_card.py
"""
import html
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "info-card.svg")

# ── Content ────────────────────────────────────────────────────
USERNAME = "rajdeepchatale"
HOSTNAME = "github"

CARD_LINES = [
    ("Role", "CS Undergrad · Developer"),
    ("Stack", "Java · Python · C/C++"),
    ("Tools", "Git · VS Code"),
    ("OS", "macOS · Linux"),
    ("Shell", "zsh"),
]

# ── Visual settings (matches the ASCII portrait panel) ─────────
BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"
INK = "#c9d1d9"
TITLE_COLOR = "#58a6ff"
ACCENT_COLORS = ["#f97583", "#56d364", "#e3b341", "#bc8cff", "#79c0ff", "#ff7b72"]

CELL_H = 15
PAD = 20
TITLEBAR_H = 30
FONT_SIZE = 13

STATIC = bool(os.environ.get("STATIC"))

# ── Animation timing ───────────────────────────────────────────
LINE_STAGGER = 0.12   # seconds between lines
FADE_DUR = 0.35

# ── Build SVG ──────────────────────────────────────────────────
LINE_H = 24
num_content_lines = len(CARD_LINES) + 2  # title + separator + data lines
card_h = num_content_lines * LINE_H + 50  # extra for color dots
CANVAS_W = 490
CANVAS_H = TITLEBAR_H + card_h + PAD

parts = []
parts.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
    f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, '
    f'Menlo, Consolas, monospace">'
)

# CSS animations for fade-slide-in
if not STATIC:
    css_lines = [
        '.info-line { opacity: 0; }',
        f'@keyframes fadeSlide {{ from {{ opacity: 0; transform: translateX(12px); }} '
        f'to {{ opacity: 1; transform: translateX(0); }} }}',
    ]
    for i in range(num_content_lines + 1):  # +1 for color dots
        delay = i * LINE_STAGGER
        css_lines.append(
            f'.line-{i} {{ animation: fadeSlide {FADE_DUR}s ease-out {delay:.2f}s forwards; }}'
        )
    parts.append(f'<style>{"".join(css_lines)}</style>')

# Background
parts.append('<defs>'
             f'<linearGradient id="ibg" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
             f'</linearGradient></defs>')
parts.append(f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="url(#ibg)"/>')
parts.append(f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="12" '
             f'fill="none" stroke="{FRAME}" stroke-width="1"/>')

# Title bar with traffic-light dots
parts.append(f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>')
for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
parts.append(f'<text x="{CANVAS_W/2}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
             f'text-anchor="middle">rajdeep@github: ~$ neofetch</text>')

# ── Content area ───────────────────────────────────────────────
content_top = TITLEBAR_H + PAD
y = content_top + FONT_SIZE
line_idx = 0

def cls(idx):
    return f'info-line line-{idx}' if not STATIC else ''

# Title: user@host
parts.append(f'<text x="{PAD}" y="{y}" font-size="{FONT_SIZE}" class="{cls(line_idx)}">'
             f'<tspan fill="{TITLE_COLOR}">{USERNAME}</tspan>'
             f'<tspan fill="{INK}">@</tspan>'
             f'<tspan fill="{TITLE_COLOR}">{HOSTNAME}</tspan></text>')
line_idx += 1
y += LINE_H

# Separator line
sep_w = len(f"{USERNAME}@{HOSTNAME}") * (FONT_SIZE * 0.6)
parts.append(f'<line x1="{PAD}" y1="{y - FONT_SIZE*0.3:.1f}" '
             f'x2="{PAD + sep_w:.1f}" y2="{y - FONT_SIZE*0.3:.1f}" '
             f'stroke="{FRAME}" stroke-width="1" class="{cls(line_idx)}"/>')
line_idx += 1
y += LINE_H * 0.6

# Key-value rows
for i, (key, value) in enumerate(CARD_LINES):
    accent = ACCENT_COLORS[i % len(ACCENT_COLORS)]
    safe_val = html.escape(value)
    parts.append(
        f'<text x="{PAD}" y="{y:.1f}" font-size="{FONT_SIZE}" class="{cls(line_idx)}">'
        f'<tspan fill="{accent}">{key}</tspan>'
        f'<tspan fill="{TITLE_TEXT}"> → </tspan>'
        f'<tspan fill="{INK}">{safe_val}</tspan></text>'
    )
    line_idx += 1
    y += LINE_H

# Color palette dots (like neofetch)
y += 12
dot_class = cls(line_idx)
parts.append(f'<g class="{dot_class}">')
for i, color in enumerate(ACCENT_COLORS):
    cx = PAD + i * 22 + 8
    parts.append(f'<circle cx="{cx}" cy="{y:.1f}" r="7" fill="{color}"/>')
# second row of dots (darker variants)
for i, color in enumerate(ACCENT_COLORS):
    cx = PAD + i * 22 + 8
    parts.append(f'<circle cx="{cx}" cy="{y + 20:.1f}" r="7" fill="{color}" opacity="0.4"/>')
parts.append('</g>')

parts.append("</svg>")

svg = "".join(parts)
with open(OUT, "w") as f:
    f.write(svg)
mode = "STATIC" if STATIC else "ANIMATED"
print(f"wrote {OUT} ({mode}, {len(svg)} bytes)")
