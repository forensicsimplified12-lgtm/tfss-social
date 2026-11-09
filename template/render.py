#!/usr/bin/env python3
"""TFSS carousel renderer.

Usage:  python3 render.py posts.json OUTPUT_DIR

posts.json is a list of posts. Each post becomes 3 slides (1080x1350 JPG):
  <id>-1.jpg  question   <id>-2.jpg  answer   <id>-3.jpg  promo

Post fields:
  id           e.g. "dec-n1"
  tag          pill text, e.g. "UGC NET · PYQ 2021 · Q34" or "FACT 2026 · Biology · Section B"
  question     question text (plain)
  options      list of 4 option texts (A-D, in the PDF's order)
  answer       "A" | "B" | "C" | "D"
  explanation  2-4 sentences, from the PDF
  confusion    optional box text; <b>..</b> allowed
  box_title    optional, "COMMON CONFUSION" (default, gets ⚠) or "QUICK RECALL"
  source       e.g. "From NET-Cracker Module 9 · Digital & Cyber Forensics"
  promo        {headline (HTML; wrap accent words in <g>..</g>), sub (Lora italic line),
                checks [4 short lines], price ("₹90"), price_label, cta,
                foot_left (yellow), foot_right (default "forensicsimplified.com")}
Text in the HTML-allowed fields is not escaped; everything else is.
"""
import base64, html, json, os, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
FONTS = HERE / "fonts"


def b64(p):
    return base64.b64encode(Path(p).read_bytes()).decode()


def font_face():
    faces = [("Poppins", "Poppins-Regular.ttf", 400, "normal"),
             ("Poppins", "Poppins-Medium.ttf", 500, "normal"),
             ("Poppins", "Poppins-Bold.ttf", 700, "normal"),
             ("Lora", "Lora-Italic-Variable.ttf", "400 700", "italic")]
    return "\n".join(
        f"@font-face{{font-family:'{f}';src:url(data:font/ttf;base64,{b64(FONTS/file)}) format('truetype');"
        f"font-weight:{w};font-style:{s};}}" for f, file, w, s in faces)


CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1350px;overflow:hidden}
body{font-family:'Poppins','Noto Color Emoji',sans-serif;color:#fff;
 background:radial-gradient(ellipse 900px 700px at 820px 260px,#5b1d7a 0%,rgba(91,29,122,0) 70%),
 linear-gradient(160deg,#1f0a2e 0%,#35104f 55%,#24093a 100%);position:relative}
.wm{position:absolute;inset:-300px;display:flex;flex-wrap:wrap;gap:60px 120px;align-content:flex-start;
 transform:rotate(-24deg);opacity:.07;font-weight:700;font-size:124px;letter-spacing:4px;pointer-events:none}
.rings{position:absolute;right:-6px;top:805px;width:310px;height:310px;pointer-events:none}
.rings i{position:absolute;border:2px solid rgba(249,115,22,.28);border-radius:50%}
.wrap{position:absolute;left:80px;right:80px;top:88px;bottom:0}
.pill{display:inline-block;height:62px;line-height:58px;padding:0 26px;border:2px solid #facc15;border-radius:31px;
 color:#facc15;font-weight:700;font-size:24px;letter-spacing:.3px}
.logo{position:absolute;right:84px;top:74px;width:88px;height:88px}
.content{position:absolute;left:80px;right:80px;top:222px;bottom:150px;display:flex;flex-direction:column}
h1{font-weight:700;font-size:calc(72px*var(--s));line-height:1.08;letter-spacing:-.5px}
g,.g{background:linear-gradient(90deg,#f97316,#ef4444);-webkit-background-clip:text;background-clip:text;color:transparent}
.q{font-weight:700;font-size:calc(47px*var(--s));line-height:1.4;max-width:890px;margin-top:calc(42px*var(--s))}
.opts{margin-top:calc(46px*var(--s));display:flex;flex-direction:column;gap:calc(26px*var(--s))}
.opt{display:flex;align-items:center;min-height:calc(116px*var(--s));padding:calc(18px*var(--s)) 32px;border-radius:18px;
 background:rgba(255,255,255,.06);border:2px solid rgba(255,255,255,.13)}
.opt b{flex:none;width:62px;height:62px;border-radius:50%;background:linear-gradient(135deg,#f97316,#ef4444);
 display:flex;align-items:center;justify-content:center;font-size:26px;font-weight:700;margin-right:28px}
.opt span{font-size:calc(40px*var(--s));line-height:1.3}
.opt.right{background:rgba(250,204,21,.09);border-color:#facc15}
.opt.right b{background:#facc15;color:#1f0a2e}
.exp{font-size:calc(36px*var(--s));line-height:1.45;margin-top:calc(42px*var(--s))}
.conf{margin-top:calc(42px*var(--s));padding:calc(36px*var(--s)) 44px;border-radius:22px;border-left:8px solid #facc15;
 background:rgba(255,255,255,.07)}
.conf h3{color:#facc15;font-size:calc(32px*var(--s));font-weight:700;letter-spacing:1px;margin-bottom:14px}
.conf p{font-size:calc(33px*var(--s));line-height:1.45}
.src{margin-top:calc(34px*var(--s));color:#c9b3e6;font-size:28px}
.sub{font-family:'Lora',serif;font-style:italic;font-size:calc(38px*var(--s));color:#d9c8ee;margin-top:calc(28px*var(--s))}
.checks{list-style:none;margin-top:calc(52px*var(--s));display:flex;flex-direction:column;gap:calc(40px*var(--s))}
.checks li{font-size:calc(38px*var(--s));display:flex;gap:26px}
.checks li:before{content:'✓';color:#facc15;font-weight:400}
.price{margin-top:auto;display:flex;align-items:baseline;gap:28px}
.price .g{font-weight:700;font-size:130px;line-height:1}
.price span{font-size:32px;color:#d9c8ee}
.price span.g{color:transparent}
.cta{margin-top:40px;align-self:flex-start;height:116px;line-height:116px;padding:0 48px;border-radius:58px;
 background:linear-gradient(90deg,#f97316,#ef4444);font-weight:700;font-size:40px}
.foot{position:absolute;left:80px;right:80px;bottom:62px;display:flex;justify-content:space-between;align-items:center;font-size:30px}
.foot .l{color:#facc15;font-weight:700}
.foot .r{color:#d9c8ee}
"""

FIT_JS = """
() => { const c=document.querySelector('.content'); let s=1;
  const over=()=>c.scrollHeight>c.clientHeight+1;
  while(over() && s>0.62){ s-=0.02; document.body.style.setProperty('--s',s); }
  return {scale:s, overflow:over()}; }
"""


def page(body, foot_l, foot_r):
    wm = "".join("<span>TFSS</span>" for _ in range(60))
    rings = "".join(f"<i style='left:{155-r}px;top:{155-r}px;width:{2*r}px;height:{2*r}px'></i>"
                    for r in (40, 75, 112, 152))
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{font_face()}{CSS}</style></head>"
            f"<body style='--s:1'><div class='wm'>{wm}</div><div class='rings'>{rings}</div>"
            f"<img class='logo' src='data:image/png;base64,{b64(HERE/'logo.png')}'>"
            f"<div class='wrap'><span class='pill'>{{TAG}}</span></div>"
            f"<div class='content'>{body}</div>"
            f"<div class='foot'><span class='l'>{foot_l}</span><span class='r'>{foot_r}</span></div></body></html>")


def slides(p):
    e = html.escape
    tag = e(p["tag"])
    letters = "ABCD"
    ans = p["answer"].strip().upper()
    site = "forensicsimplified.com"
    opts = "".join(f"<div class='opt'><b>{letters[i]}</b><span>{e(o)}</span></div>" for i, o in enumerate(p["options"]))
    s1 = page(f"<h1>Can you <g>crack this?</g></h1><div class='q'>{e(p['question'])}</div><div class='opts'>{opts}</div>",
              "💬 Comment A, B, C or D · Swipe →", site)
    bt = p.get("box_title", "COMMON CONFUSION").upper()
    icon = "<span style=\"font-family:'DejaVu Sans'\">⚠</span> " if bt == "COMMON CONFUSION" else ""
    conf = (f"<div class='conf'><h3>{icon}{e(bt)}</h3><p>{p['confusion']}</p></div>" if p.get("confusion") else "")
    right = p["options"][letters.index(ans)]
    s2 = page(f"<h1>The answer is <g>{ans}</g></h1>"
              f"<div class='opts'><div class='opt right'><b>{ans}</b><span>{e(right)}</span></div></div>"
              f"<div class='exp'>{e(p['explanation'])}</div>{conf}<div class='src'>{e(p['source'])}</div>",
              "🔖 Save this for revision", site)
    pr = p["promo"]
    checks = "".join(f"<li>{e(c)}</li>" for c in pr["checks"])
    s3 = page(f"<h1>{pr['headline']}</h1><div class='sub'>{e(pr['sub'])}</div><ul class='checks'>{checks}</ul>"
              f"<div class='price'><span class='g'>{e(pr['price'])}</span><span>{e(pr['price_label'])}</span></div>"
              f"<div class='cta'>{e(pr['cta'])}</div>",
              e(pr.get("foot_left", "")), e(pr.get("foot_right", site)))
    return [x.replace("{TAG}", tag) for x in (s1, s2, s3)]


def main(spec, out):
    posts = json.loads(Path(spec).read_text())
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    problems = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        for p in posts:
            for i, h in enumerate(slides(p), 1):
                pg.set_content(h, wait_until="load")
                pg.evaluate("document.fonts.ready")
                fit = pg.evaluate(FIT_JS)
                if fit["overflow"]:
                    problems.append(f"{p['id']}-{i}: text too long, shorten it")
                f = out / f"{p['id']}-{i}.jpg"
                pg.screenshot(path=str(f), type="jpeg", quality=92)
                print(f, "scale", round(fit["scale"], 2))
        b.close()
    if problems:
        print("PROBLEMS:\n" + "\n".join(problems)); sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
