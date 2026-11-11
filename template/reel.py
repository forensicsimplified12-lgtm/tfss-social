#!/usr/bin/env python3
"""TFSS faceless quiz Reel maker (1080x1920 MP4, ~15 s, tick + reveal sounds, no voice).

Usage:  python3 reel.py posts.json OUTPUT_DIR [id ...]

Uses the same posts.json as render.py (fields: id, tag, question, options, answer,
explanation, source). Optional per post: "reel_explain" = a shorter 1-2 line
explanation for the answer screen (falls back to "explanation").
Writes <id>-reel.mp4 and <id>-reel-cover.jpg (the question screen, for the Reel cover).

Timeline: question 3 s -> countdown 5..1 (1 s each) -> answer 4.5 s -> end card 2.5 s.
Content stays inside Instagram's safe area (top 220 px and bottom 420 px are kept clear
of key text because the Reels UI covers them).
"""
import html, json, math, struct, subprocess, sys, tempfile, wave
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render import font_face, b64, HERE  # noqa: E402

W, H = 1080, 1920
FPS = 30
T_Q, T_TICK, N_TICK, T_ANS, T_END = 3.0, 1.0, 5, 4.5, 2.5

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1920px;overflow:hidden}
body{font-family:'Poppins','Noto Color Emoji',sans-serif;color:#fff;position:relative;
 background:radial-gradient(ellipse 1000px 900px at 820px 420px,#5b1d7a 0%,rgba(91,29,122,0) 70%),
 linear-gradient(165deg,#1f0a2e 0%,#35104f 55%,#24093a 100%)}
.wm{position:absolute;inset:-400px;display:flex;flex-wrap:wrap;gap:60px 120px;align-content:flex-start;
 transform:rotate(-24deg);opacity:.06;font-weight:700;font-size:124px;letter-spacing:4px}
.rings{position:absolute;right:-60px;top:1180px;width:360px;height:360px}
.rings i{position:absolute;border:2px solid rgba(249,115,22,.25);border-radius:50%}
.top{position:absolute;left:80px;right:80px;top:230px;display:flex;justify-content:space-between;align-items:center}
.pill{height:66px;line-height:62px;padding:0 28px;border:2px solid #facc15;border-radius:33px;color:#facc15;font-weight:700;font-size:27px}
.logo{width:96px;height:96px}
.main{position:absolute;left:80px;right:80px;top:350px;bottom:650px;display:flex;flex-direction:column}
h1{font-weight:700;font-size:calc(80px*var(--s));line-height:1.08}
g{background:linear-gradient(90deg,#f97316,#ef4444);-webkit-background-clip:text;background-clip:text;color:transparent}
.q{font-weight:700;font-size:calc(52px*var(--s));line-height:1.36;margin-top:calc(40px*var(--s))}
.opts{margin-top:calc(40px*var(--s));display:flex;flex-direction:column;gap:calc(22px*var(--s))}
.opt{display:flex;align-items:center;min-height:calc(112px*var(--s));padding:calc(18px*var(--s)) 34px;border-radius:20px;
 background:rgba(255,255,255,.07);border:2px solid rgba(255,255,255,.14);transition:none}
.opt b{flex:none;width:68px;height:68px;border-radius:50%;background:linear-gradient(135deg,#f97316,#ef4444);
 display:flex;align-items:center;justify-content:center;font-size:30px;font-weight:700;margin-right:30px}
.opt span{font-size:calc(44px*var(--s));line-height:1.28}
.opt.dim{opacity:.32}
.opt.right{background:rgba(250,204,21,.12);border:3px solid #facc15}
.opt.right b{background:#facc15;color:#1f0a2e}
.timer{position:absolute;left:50%;transform:translateX(-50%);bottom:455px;width:180px;height:180px;border-radius:50%;
 display:flex;align-items:center;justify-content:center;font-weight:700;font-size:92px;
 background:conic-gradient(#facc15 calc(var(--p)*1turn),rgba(255,255,255,.12) 0);}
.timer:before{content:'';position:absolute;inset:12px;border-radius:50%;background:#2a0d40}
.timer span{position:relative}
.hint{position:absolute;left:80px;right:80px;bottom:440px;text-align:center;color:#facc15;font-weight:700;font-size:40px}
.exp{margin-top:calc(40px*var(--s));padding:calc(34px*var(--s)) 40px;border-radius:22px;border-left:8px solid #facc15;
 background:rgba(255,255,255,.08);font-size:calc(38px*var(--s));line-height:1.42}
.src{margin-top:24px;color:#c9b3e6;font-size:28px}
.end{position:absolute;left:80px;right:80px;top:420px;bottom:430px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:44px}
.end img{width:200px;height:200px}
.end h2{font-size:78px;line-height:1.1;font-weight:700}
.end p{font-size:44px;color:#d9c8ee}
.cta{height:120px;line-height:120px;padding:0 56px;border-radius:60px;background:linear-gradient(90deg,#f97316,#ef4444);font-weight:700;font-size:44px}
"""

FIT_JS = """() => { const c=document.querySelector('.main'); if(!c) return 1; let s=1;
  while(c.scrollHeight>c.clientHeight+1 && s>0.6){ s-=0.02; document.body.style.setProperty('--s',s);} return s; }"""


def shell(inner):
    wm = "".join("<span>TFSS</span>" for _ in range(80))
    rings = "".join(f"<i style='left:{180-r}px;top:{180-r}px;width:{2*r}px;height:{2*r}px'></i>" for r in (46, 86, 128, 174))
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{font_face()}{CSS}</style></head>"
            f"<body style='--s:1'><div class='wm'>{wm}</div><div class='rings'>{rings}</div>{inner}</body></html>")


def frames(p):
    e = html.escape
    L = "ABCD"
    ans = p["answer"].strip().upper()
    logo = f"<img class='logo' src='data:image/png;base64,{b64(HERE/'logo.png')}'>"
    top = f"<div class='top'><span class='pill'>{e(p['tag'])}</span>{logo}</div>"

    def opts(state):
        out = []
        for i, o in enumerate(p["options"]):
            cls = "opt" if state == "q" else ("opt right" if L[i] == ans else "opt dim")
            out.append(f"<div class='{cls}'><b>{L[i]}</b><span>{e(o)}</span></div>")
        return "<div class='opts'>" + "".join(out) + "</div>"

    q_main = f"<div class='main'><h1>Can you <g>crack this?</g></h1><div class='q'>{e(p['question'])}</div>{opts('q')}</div>"
    out = [("q", shell(top + q_main + "<div class='hint'>⏱ You have 5 seconds…</div>"))]
    for n in range(N_TICK, 0, -1):
        out.append((f"t{n}", shell(top + q_main + f"<div class='timer' style='--p:{n/N_TICK}'><span>{n}</span></div>")))
    exp = p.get("reel_explain") or p["explanation"]
    a_main = (f"<div class='main' style='bottom:430px'><h1>Answer: <g>{ans}</g></h1>{opts('a')}"
              f"<div class='exp'>{e(exp)}</div><div class='src'>{e(p['source'])}</div></div>")
    out.append(("a", shell(top + a_main)))
    end = (f"<div class='end'><img src='data:image/png;base64,{b64(HERE/'logo.png')}'>"
           f"<h2>Got it right?<br><g>Comment</g> ✅</h2><p>New forensic PYQ quiz every<br>Mon · Wed · Fri</p>"
           f"<div class='cta'>Follow @forensicsimplified12</div><p>🎁 Free NET-Cracker Module 9 · link in bio</p></div>")
    out.append(("end", shell(end)))
    return out


def tone_wav(path, total):
    """Silent track with a tick each countdown second and a chime at the reveal."""
    sr = 44100
    buf = [0.0] * int(sr * total)

    def add(t0, dur, freqs, vol, decay):
        s0 = int(t0 * sr)
        for k in range(int(dur * sr)):
            if s0 + k >= len(buf):
                break
            t = k / sr
            env = math.exp(-decay * t) * min(1.0, k / 200)
            buf[s0 + k] += vol * env * sum(math.sin(2 * math.pi * f * t) for f in freqs) / len(freqs)

    for i in range(N_TICK):
        add(T_Q + i * T_TICK, 0.09, [1500], 0.45, 40)
    t_rev = T_Q + N_TICK * T_TICK
    add(t_rev, 0.9, [880, 1320, 1760], 0.5, 4)
    with wave.open(str(path), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, v)) * 30000)) for v in buf))


def make(posts, out, only=None):
    out.mkdir(parents=True, exist_ok=True)
    durs = {"q": T_Q, "a": T_ANS, "end": T_END, **{f"t{n}": T_TICK for n in range(1, N_TICK + 1)}}
    total = T_Q + N_TICK * T_TICK + T_ANS + T_END
    with sync_playwright() as pw, tempfile.TemporaryDirectory() as td:
        td = Path(td)
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        for p in posts:
            if only and p["id"] not in only:
                continue
            files = []
            for name, h in frames(p):
                pg.set_content(h, wait_until="load"); pg.evaluate("document.fonts.ready")
                s = pg.evaluate(FIT_JS)
                f = td / f"{p['id']}-{name}.png"
                pg.screenshot(path=str(f))
                files.append((f, durs[name]))
                if name == "q":
                    pg.screenshot(path=str(out / f"{p['id']}-reel-cover.jpg"), type="jpeg", quality=92)
                if s < 0.62:
                    print(f"WARNING {p['id']} {name}: text very long, shorten it")
            lst = td / f"{p['id']}.txt"
            lst.write_text("".join(f"file '{f}'\nduration {d}\n" for f, d in files) + f"file '{files[-1][0]}'\n")
            wav = td / "a.wav"; tone_wav(wav, total)
            mp4 = out / f"{p['id']}-reel.mp4"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                            "-i", str(wav), "-vf", f"fps={FPS},format=yuv420p", "-c:v", "libx264", "-preset", "veryfast",
                            "-crf", "20", "-c:a", "aac", "-b:a", "128k", "-t", str(total), "-movflags", "+faststart",
                            str(mp4)], check=True)
            print(mp4)
        b.close()


if __name__ == "__main__":
    make(json.loads(Path(sys.argv[1]).read_text()), Path(sys.argv[2]), set(sys.argv[3:]) or None)
