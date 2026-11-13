# TFSS slide template

Makes the 3-slide Instagram carousels (1080×1350 JPG) in the TFSS look:
purple background, orange→red accents, yellow tags, Poppins + Lora italic, "TFSS" watermark, no blue.

    python3 template/render.py posts.json <month-folder>

See the docstring at the top of `render.py` for the posts.json fields.
Slide 1 = question, slide 2 = answer + explanation, slide 3 = product promo.
Long text shrinks automatically; the script stops with "text too long" if it still doesn't fit.

`logo.png` is the fingerprint-magnifier badge used on most November slides (`logo-w1.png` is the variant with "TFSS" under it, used on the first two posts).
Fonts are bundled in `fonts/` (Poppins and Lora, SIL Open Font License).

## Quiz Reels

    python3 template/reel.py posts.json <month-folder> [id ...]

Makes `<id>-reel.mp4` (1080×1920, 15 s: question → 5-second countdown with ticks → answer + explanation → follow card)
and `<id>-reel-cover.jpg`. Same posts.json as the carousels; optional `reel_explain` gives a shorter answer-screen line.
No voice, no music (Instagram music can only be added in the app).

## Colour palettes

`template/palettes.py` has 16 TFSS palettes: 10 dark (0-9: classic, plum-pink, wine, charcoal-ember, aubergine-coral,
maroon-gold, violet-rose, cocoa-orange, raspberry, dusk-amber) and 6 light (10-15: lavender-light, peach-cream,
rose-blush, sand-gold, lilac-coral, ivory-plum). Set `"palette": 0-15` (or a name) per post
in posts.json / reels.json; rotate them in posting order, about 2 dark : 1 light. Without it, the palette is picked from the post id.
