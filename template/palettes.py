"""TFSS colour palettes — all in the brand family (dark purple/plum/wine/maroon/cocoa
backgrounds, orange-red-coral accents, yellow-gold highlights, never blue).

A post can pick one with "palette": "<name>" or "palette": <0-9> in posts.json.
Otherwise it is chosen from the post id, so the same post always renders the same way
and consecutive posts usually differ. Monthly runs should set "palette" explicitly and
rotate 0 → 9 in posting order (see the monthly-run doc).
"""
import zlib

PALETTES = [
    # name, bg1, bg2, bg3, glow, accent1, accent2, highlight, soft, muted
    ("classic",        "#1f0a2e", "#35104f", "#24093a", "#5b1d7a", "#f97316", "#ef4444", "#facc15", "#d9c8ee", "#c9b3e6"),
    ("plum-pink",      "#2a0a2a", "#4a0f45", "#2d0a2b", "#8e1f78", "#fb923c", "#ec4899", "#fde047", "#f3d0ea", "#e3b5d8"),
    ("wine",           "#2b0a12", "#4c0f22", "#2e0b16", "#7f1d3a", "#fb923c", "#f43f5e", "#fcd34d", "#f5cdd6", "#e6b3c0"),
    ("charcoal-ember", "#17121c", "#2a2030", "#1a141f", "#4a2a3f", "#f97316", "#f59e0b", "#fde68a", "#e2d6e8", "#cbbcd3"),
    ("aubergine-coral","#1c0b24", "#3a1240", "#220b29", "#6d2a6b", "#fb7185", "#f97316", "#fef08a", "#ecd2f0", "#d6b6dc"),
    ("maroon-gold",    "#240a0a", "#43120f", "#2a0c0b", "#7c2d12", "#f59e0b", "#ef4444", "#fde047", "#f3d6c8", "#e0bba8"),
    ("violet-rose",    "#160b2e", "#2b1250", "#1a0c36", "#6d28d9", "#f472b6", "#fb923c", "#fde68a", "#ddd0f5", "#c7b5ec"),
    ("cocoa-orange",   "#1e120c", "#3a2216", "#22140d", "#6b3a1f", "#fb923c", "#ea580c", "#fcd34d", "#f0dccd", "#dcc1ad"),
    ("raspberry",      "#2a0718", "#50102f", "#2e081c", "#9d174d", "#fbbf24", "#f43f5e", "#facc15", "#f6cfe0", "#e5b0c8"),
    ("dusk-amber",     "#241033", "#3f1d52", "#2a1239", "#7e3fa0", "#fbbf24", "#f97316", "#fde047", "#e6d4f2", "#cfb8e0"),
]
KEYS = ["bg1", "bg2", "bg3", "glow", "a1", "a2", "hl", "soft", "muted"]


def _hex_rgba(h, a):
    h = h.lstrip("#")
    return f"rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{a})"


def pick(p):
    v = p.get("palette")
    if isinstance(v, int):
        return PALETTES[v % len(PALETTES)]
    if isinstance(v, str):
        for row in PALETTES:
            if row[0] == v:
                return row
    return PALETTES[zlib.crc32(p["id"].encode()) % len(PALETTES)]


def style(p, extra="--s:1"):
    row = pick(p)
    vals = dict(zip(KEYS, row[1:]))
    vals["ring"] = _hex_rgba(vals["a1"], 0.28)
    vals["hlbg"] = _hex_rgba(vals["hl"], 0.10)
    return extra + ";" + ";".join(f"--{k}:{v}" for k, v in vals.items())
