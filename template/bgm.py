#!/usr/bin/env python3
"""Composes the TFSS signature background track (original, copyright-free).

Lo-fi study beat, 120 BPM half-time feel (2 s bars) so the 1-second countdown ticks
land on the beat and the answer reveal at 8.0 s lands on a bar downbeat, where the
signature bell motif plays.

    python3 bgm.py [out.wav]      (default: tfss-signature-bgm.wav next to this file)
"""
import sys, wave
from pathlib import Path
import numpy as np
from scipy.signal import butter, sosfilt

SR = 44100
DUR = 15.0
BEAT = 0.5
BAR = 2.0
N = int(SR * DUR)
rng = np.random.default_rng(12)  # fixed seed = same track every time


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def place(buf, start, sig, gain=1.0):
    i = int(start * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += gain * sig[: j - i]


def t_of(sec):
    return np.arange(int(sec * SR)) / SR


def lp(x, f):
    return sosfilt(butter(2, f, "low", fs=SR, output="sos"), x)


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x)


def hp(x, f):
    return sosfilt(butter(2, f, "high", fs=SR, output="sos"), x)


def rhodes(notes, length, vel=1.0):
    t = t_of(length)
    out = np.zeros_like(t)
    for k, m in enumerate(notes):
        f = hz(m) * (1 + 0.0015 * (k - 1.5))          # tiny detune between voices
        tone = (np.sin(2 * np.pi * f * t) + 0.28 * np.sin(4 * np.pi * f * t)
                + 0.12 * np.sin(6 * np.pi * f * t) * np.exp(-9 * t))
        env = np.minimum(1, t / 0.012) * np.exp(-1.1 * t)
        out += tone * env
    trem = 1 + 0.08 * np.sin(2 * np.pi * 4.5 * t)
    fade = np.minimum(1, (length - t) / 0.08)
    return lp(out * trem * fade * vel / len(notes), 3500)


def bass(m, length):
    t = t_of(length)
    f = hz(m)
    env = np.minimum(1, t / 0.008) * np.exp(-2.2 * t) * np.minimum(1, (length - t) / 0.05)
    return lp((np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)) * env, 400)


def kick():
    t = t_of(0.45)
    f = 45 + 85 * np.exp(-28 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-7 * t)


def snare():
    t = t_of(0.3)
    noise = bp(rng.standard_normal(len(t)), 1200, 6000) * np.exp(-22 * t)
    body = np.sin(2 * np.pi * 185 * t) * np.exp(-28 * t)
    return 0.7 * noise + 0.5 * body


def hat(open_=False):
    t = t_of(0.12 if not open_ else 0.25)
    return hp(rng.standard_normal(len(t)), 7000) * np.exp(-(45 if not open_ else 14) * t)


def bell(m, length=1.2):
    t = t_of(length)
    f = hz(m)
    tone = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2.76 * f * t) * np.exp(-7 * t)
    return tone * np.minimum(1, t / 0.004) * np.exp(-3.2 * t)


def compose():
    keys = np.zeros(N); low = np.zeros(N); drums = np.zeros(N); lead = np.zeros(N); fx = np.zeros(N)
    side = np.ones(N)  # kick sidechain on the music bus

    # Am9 | Fmaj9 | Cmaj7 | Em7 | Am9 | Fmaj9 | Cmaj7 | Am9(half)
    prog = [((60, 64, 67, 71), 45), ((57, 60, 64, 67), 41), ((52, 55, 59, 60), 36), ((55, 59, 62, 64), 40)]
    bars = int(np.ceil(DUR / BAR))
    for b in range(bars):
        t0 = b * BAR
        notes, root = prog[b % 4]
        place(keys, t0, rhodes(notes, 1.35), 0.9)
        place(keys, t0 + 1.25, rhodes(notes, 0.7, 0.55))           # syncopated push
        place(low, t0, bass(root, 1.1))
        place(low, t0 + 1.25, bass(root + 12 if b % 2 else root, 0.6), 0.7)

        countdown = 3.0 <= t0 < 8.0
        # drums: kick on 1 and the "and of 3", snare on beat 3 (half-time)
        for kt in (0.0, 1.25 if b % 2 == 0 else 1.5):
            place(drums, t0 + kt, kick(), 0.95)
            i = int((t0 + kt) * SR)
            j = min(N, i + int(0.25 * SR))
            side[i:j] = np.minimum(side[i:j], 1 - 0.35 * np.exp(-12 * np.arange(j - i) / SR))
        place(drums, t0 + 1.0, snare(), 0.55)
        step = 0.125 if countdown else 0.25                         # hats double during the countdown
        k = 0
        while k * step < BAR - 1e-9:
            swing = 0.035 if (k % 2 and step == 0.25) else 0.0
            vel = (0.32 if k % 2 == 0 else 0.2) * (0.8 if step == 0.125 else 1)
            place(drums, t0 + k * step + swing, hat(open_=(k == 7 and step == 0.25 and b % 2)), vel)
            k += 1

    # signature bell motif: opening and the answer reveal (8.0 s)
    motif = [(0.0, 76), (0.25, 79), (0.5, 81), (1.0, 84)]           # E5 G5 A5 C6
    for start in (0.0, 8.0):
        for dt, m in motif:
            place(lead, start + dt, bell(m), 0.45)
    place(lead, 12.5, bell(81, 2.0), 0.35); place(lead, 12.75, bell(76, 2.0), 0.3)

    # riser into the reveal
    t = t_of(1.0)
    riser = hp(rng.standard_normal(len(t)), 2500) * (t / 1.0) ** 2.2
    place(fx, 7.0, riser, 0.12)

    # vinyl warmth
    crackle = np.zeros(N)
    idx = rng.integers(0, N, 900)
    crackle[idx] = rng.uniform(-1, 1, len(idx))
    crackle = bp(crackle, 1000, 6000) * 0.25 + lp(rng.standard_normal(N), 900) * 0.006

    music = (keys * 0.75 + low * 0.9 + lead * 0.8) * side
    mix = music + drums * 0.8 + fx + crackle
    mix = lp(mix, 7500)                                               # lo-fi top end
    t = np.arange(N) / SR
    mix *= np.minimum(1, t / 0.15) * np.minimum(1, (DUR - t) / 1.2)
    return mix / (np.max(np.abs(mix)) + 1e-9) * 0.89


def save(x, path):
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "tfss-signature-bgm.wav"
    save(compose(), out)
    print(out)
