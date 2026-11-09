# TFSS slide template

Makes the 3-slide Instagram carousels (1080×1350 JPG) in the TFSS look:
purple background, orange→red accents, yellow tags, Poppins + Lora italic, "TFSS" watermark, no blue.

    python3 template/render.py posts.json <month-folder>

See the docstring at the top of `render.py` for the posts.json fields.
Slide 1 = question, slide 2 = answer + explanation, slide 3 = product promo.
Long text shrinks automatically; the script stops with "text too long" if it still doesn't fit.

`logo.png` is the badge used on every slide (`logo-alt.png` is the variant from the November FACT slides).
Fonts are bundled in `fonts/` (Poppins and Lora, SIL Open Font License).
