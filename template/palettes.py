"""TFSS colour palettes — all in the brand family (purple/plum/wine/maroon/cocoa,
orange-red-coral accents, gold/purple highlights, never blue). 10 dark + 6 light.

A post can pick one with "palette": "<name>" or "palette": <index> in posts.json.
Otherwise it is chosen from the post id, so the same post always renders the same way.
Monthly runs should set "palette" explicitly and rotate through all of them in posting
order (see the monthly-run doc), roughly 2 dark : 1 light.
"""
import zlib

# name, bg1, bg2, bg3, glow, accent1, accent2, highlight, soft text, muted text
DARK = [
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
# light: bg1, bg2, bg3, glow, accent1, accent2, highlight, soft text, muted text, main text
LIGHT = [
    ("lavender-light", "#f6f0fc", "#ebdff8", "#faf6fd", "#d9c3f2", "#f97316", "#ef4444", "#6b21a8", "#4b2a63", "#6b4f80", "#2a0d40"),
    ("peach-cream",    "#fff5ed", "#ffe5d2", "#fff9f4", "#ffcfae", "#ea580c", "#dc2626", "#9a3412", "#6b3420", "#8a5a44", "#3b1206"),
    ("rose-blush",     "#fff1f4", "#ffdfe7", "#fff7f9", "#fbc6d4", "#f97316", "#e11d48", "#9d174d", "#6d2a45", "#8d5068", "#3a0a1c"),
    ("sand-gold",      "#fbf6ea", "#f2e6cb", "#fdfaf1", "#ebd6a2", "#d97706", "#dc2626", "#92400e", "#5c3d12", "#7d6236", "#2e1a05"),
    ("lilac-coral",    "#f8f2ff", "#eee2ff", "#fcf9ff", "#e2cdff", "#fb7185", "#f97316", "#86198f", "#57376a", "#765a88", "#2b0f3a"),
    ("ivory-plum",     "#fbf9f6", "#f1e9e2", "#fdfcfa", "#e8d3e6", "#f97316", "#be123c", "#581c87", "#4a3357", "#6e5a78", "#1f0a2e"),
]
PALETTES = DARK + LIGHT
NAMES = [r[0] for r in PALETTES]


def _rgba(h, a):
    h = h.lstrip("#")
    return f"rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{a})"


def pick(p):
    v = p.get("palette")
    if isinstance(v, int):
        return PALETTES[v % len(PALETTES)]
    if isinstance(v, str) and v in NAMES:
        return PALETTES[NAMES.index(v)]
    return PALETTES[zlib.crc32(p["id"].encode()) % len(PALETTES)]


def style(p, extra="--s:1"):
    row = pick(p)
    light = len(row) == 11
    bg1, bg2, bg3, glow, a1, a2, hl, soft, muted = row[1:10]
    fg = row[10] if light else "#ffffff"
    v = dict(bg1=bg1, bg2=bg2, bg3=bg3, glow=glow, a1=a1, a2=a2, hl=hl, soft=soft, muted=muted, fg=fg,
             ring=_rgba(a1, 0.30 if light else 0.28), hlbg=_rgba(hl, 0.08 if light else 0.10),
             card=_rgba(fg, 0.05 if light else 0.07), cardb=_rgba(fg, 0.13 if light else 0.14),
             track=_rgba(fg, 0.12), wm=fg, onhl="#ffffff" if light else bg1)
    return extra + ";" + ";".join(f"--{k}:{x}" for k, x in v.items())
