#!/usr/bin/env python3
"""
render_heatmap_svg.py — Render contribution data as a clean, animated,
glowing streak SVG matching the exact reference style.

Features:
  - Clean layout (no window border inside SVG, transparent/dark background)
  - Month & Day labels
  - Pop & flash glowing animations for contribution cells (cascading sweep)
  - Single summary text at bottom: "X contributions in the last year"
"""
import datetime
import json
import os

HERE = os.path.dirname(__file__)
IN_PATH = os.path.join(HERE, "..", "data", "contributions.json")
OUT_PATH = os.path.join(HERE, "..", "contrib-heatmap.svg")

# GitHub green palette: empty -> level 4 (brightest green)
COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
GRAY = "#7d8590"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Layout dimensions
CELL, GAP, RAD = 13, 3, 2.5
LEFT, TOP = 34, 24

# Reveal animation timing
REVEAL, DUR = 3.6, 0.55


def level_for(count):
    if count == 0:
        return 0
    if count <= 3:
        return 1
    if count <= 10:
        return 2
    if count <= 20:
        return 3
    return 4


def render(data):
    days = data.get("days", [])
    total = data.get("total_contributions", sum(d["count"] for d in days))

    if not days:
        print("Warning: No day data found")
        return ""

    n = len(days)
    nw = (n + 6) // 7
    w = LEFT + nw * (CELL + GAP) + 6
    h = TOP + 7 * (CELL + GAP) + 22

    max_order = (nw - 1) + 6 * 0.55

    rects = []
    labels = []

    # Month labels
    sd = datetime.date.fromisoformat(days[0]["date"])
    last_m = None
    for wk in range(nw):
        d = sd + datetime.timedelta(days=wk * 7)
        if d.month != last_m:
            last_m = d.month
            labels.append(
                f'<text class="lbl" x="{LEFT + wk * (CELL + GAP)}" y="{TOP - 8}">{MONTHS[d.month - 1]}</text>'
            )

    # Day labels
    for name, r in [("Mon", 1), ("Wed", 3), ("Fri", 5)]:
        labels.append(
            f'<text class="lbl" x="2" y="{TOP + r * (CELL + GAP) + CELL - 2}">{name}</text>'
        )

    # Contribution cells with pop & glowing flash animation
    for i, c in enumerate(days):
        wk, row = i // 7, i % 7
        cnt = c["count"]
        lvl = level_for(cnt)
        x = LEFT + wk * (CELL + GAP)
        y = TOP + row * (CELL + GAP)
        delay = round((wk + row * 0.55) / max_order * REVEAL, 3)

        cls = "c g" if lvl >= 1 else "c e"
        plural = "s" if cnt != 1 else ""
        date_s = c["date"]

        rects.append(
            f'<rect class="{cls}" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="{RAD}" '
            f'fill="{COLORS[lvl]}" style="animation-delay:{delay:.3f}s">'
            f'<title>{date_s}: {cnt} contribution{plural}</title></rect>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif">
<style>
  text.lbl {{ fill: {GRAY}; font-size: 13px; font-weight: 600; }}
  text.total {{ fill: #e6edf3; font-size: 15px; font-weight: 700; }}
  .c {{ transform-box: fill-box; transform-origin: center; opacity: 0; animation: pop {DUR}s ease-out both; }}
  .g {{ animation: pop {DUR}s ease-out both, flash {DUR + 0.15:.2f}s ease-out both; }}
  @keyframes pop {{
    0%   {{ opacity: 0; transform: scale(0.2); }}
    60%  {{ opacity: 1; transform: scale(1.1); }}
    100% {{ opacity: 1; transform: scale(1); }}
  }}
  @keyframes flash {{
    0%   {{ filter: brightness(2.4); }}
    45%  {{ filter: brightness(2.4); }}
    100% {{ filter: brightness(1); }}
  }}
  @media (prefers-reduced-motion: reduce) {{
    .c {{ opacity: 1 !important; animation: none !important; }}
  }}
</style>
<rect width="{w}" height="{h}" fill="none"/>
{''.join(labels)}
{''.join(rects)}
<text class="total" x="{LEFT}" y="{h - 6}">{total:,} contributions in the last year</text>
</svg>'''

    return svg


if __name__ == "__main__":
    with open(IN_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    svg_content = render(data)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"wrote {OUT_PATH} ({len(svg_content)} bytes)")
