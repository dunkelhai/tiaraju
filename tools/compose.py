#!/usr/bin/env python3
"""compose.py — trilha sonora e efeitos sonoros do Tiaraju, sintetizados em Python puro.

Sem dependências externas: osciladores, envelopes ADSR, filtro de 1 polo,
reverb Schroeder estéreo e gravação WAV 16-bit. Saída em assets/audio/.

Tema principal: "Esta terra tem dono" — ré menor, 90 BPM, 32 compassos (~85 s):
drone grave + flauta (mimby) + cordas + coro + tambores (angu'a, takuapu, mbaraka)
+ metais no clímax. Pensado para tocar em loop (o final cai no mesmo drone do começo).

Uso: python3 compose.py [--only musica|sfx|ambiente]
"""
import array
import math
import os
import random
import sys
import wave

SR = 22050
TWO_PI = 2.0 * math.pi
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "audio")

NOTE_IDX = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6,
            "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}


def freq(name):
    midi = 12 * (int(name[-1]) + 1) + NOTE_IDX[name[:-1]]
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)


def lp_alpha(fc):
    return 1.0 - math.exp(-TWO_PI * fc / SR)


def envelope(n, a, d, s, r):
    """ADSR em segundos; devolve lista de n + release amostras."""
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    total = n + nr
    env = [0.0] * total
    for i in range(total):
        if i < na:
            v = i / max(1, na)
        elif i < na + nd:
            v = 1.0 - (1.0 - s) * (i - na) / max(1, nd)
        elif i < n:
            v = s
        else:
            v = s * (1.0 - (i - n) / max(1, nr))
        env[i] = v
    return env


# ---------------------------------------------------------------- instrumentos ----
def flute(f, dur, vib=0.006):
    """Flauta guarani (mimby): seno + 2º e 3º harmônicos, vibrato que entra depois, sopro."""
    n = int(dur * SR)
    env = envelope(n, 0.05, 0.12, 0.85, 0.3)
    out = [0.0] * len(env)
    ph, rng, breath, alpha = 0.0, random.Random(int(f)), 0.0, lp_alpha(1800)
    for i in range(len(env)):
        t = i / SR
        vdepth = vib * min(1.0, max(0.0, (t - 0.12) / 0.3))
        fi = f * (1.0 + vdepth * math.sin(TWO_PI * 5.3 * t))
        ph += TWO_PI * fi / SR
        breath += alpha * ((rng.random() * 2 - 1) - breath)
        s = math.sin(ph) + 0.28 * math.sin(2 * ph) + 0.09 * math.sin(3 * ph) + 0.08 * breath
        out[i] = s * env[i]
    return out


def strings(f, dur, cutoff=1400):
    """Cordas: três dentes-de-serra desafinados, passa-baixas, ataque lento."""
    n = int(dur * SR)
    env = envelope(n, 0.35, 0.25, 0.8, 0.6)
    out = [0.0] * len(env)
    phs = [0.0, 0.0, 0.0]
    dets = [1.0, 1.004, 0.9965]
    y, alpha = 0.0, lp_alpha(cutoff)
    for i in range(len(env)):
        s = 0.0
        for k in range(3):
            phs[k] += dets[k] * f / SR
            if phs[k] >= 1.0:
                phs[k] -= 1.0
            s += 2.0 * phs[k] - 1.0
        y += alpha * (s / 3.0 - y)
        out[i] = y * env[i]
    return out


def choir(f, dur):
    """Coro missioneiro: aditivo (4 harmônicos), duas vozes desafinadas, vibrato lento."""
    n = int(dur * SR)
    env = envelope(n, 0.6, 0.3, 0.75, 0.9)
    out = [0.0] * len(env)
    ph1 = ph2 = 0.0
    for i in range(len(env)):
        t = i / SR
        v = 1.0 + 0.004 * math.sin(TWO_PI * 4.6 * t)
        ph1 += TWO_PI * f * v * 1.002 / SR
        ph2 += TWO_PI * f * v * 0.998 / SR
        s = 0.0
        for ph in (ph1, ph2):
            s += math.sin(ph) + 0.5 * math.sin(2 * ph) + 0.22 * math.sin(3 * ph) + 0.1 * math.sin(4 * ph)
        out[i] = s * 0.5 * env[i] * (0.85 + 0.15 * math.sin(TWO_PI * 0.4 * t))
    return out


def bass(f, dur):
    n = int(dur * SR)
    env = envelope(n, 0.01, 0.15, 0.7, 0.15)
    out = [0.0] * len(env)
    ph, saw, y, alpha = 0.0, 0.0, 0.0, lp_alpha(320)
    for i in range(len(env)):
        ph += TWO_PI * f / SR
        saw += f / SR
        if saw >= 1.0:
            saw -= 1.0
        y += alpha * ((2 * saw - 1) - y)
        out[i] = (0.8 * math.sin(ph) + 0.5 * y) * env[i]
    return out


def brass(f, dur):
    """Metais: dente-de-serra com envelope de filtro (abre rápido, fecha devagar)."""
    n = int(dur * SR)
    env = envelope(n, 0.06, 0.12, 0.8, 0.25)
    out = [0.0] * len(env)
    saw1 = saw2 = y = 0.0
    for i in range(len(env)):
        t = i / SR
        fc = 500 + 2200 * math.exp(-t * 6.0) + 600 * min(1.0, t * 12)
        alpha = lp_alpha(fc)
        saw1 += f / SR
        saw2 += f * 1.006 / SR
        if saw1 >= 1.0:
            saw1 -= 1.0
        if saw2 >= 1.0:
            saw2 -= 1.0
        y += alpha * (((2 * saw1 - 1) + (2 * saw2 - 1)) * 0.5 - y)
        out[i] = y * env[i]
    return out


def drone(f, dur, attack=2.0, release=3.0):
    """Drone grave: seno, sub-oitava, dente-de-serra bem filtrado, respiração lenta."""
    n = int(dur * SR)
    out = [0.0] * n
    ph, saw, y, alpha = 0.0, 0.0, 0.0, lp_alpha(220)
    na, nr = int(attack * SR), int(release * SR)
    for i in range(n):
        t = i / SR
        ph += TWO_PI * f / SR
        saw += f * 1.003 / SR
        if saw >= 1.0:
            saw -= 1.0
        y += alpha * ((2 * saw - 1) - y)
        e = min(1.0, i / na) if i < na else 1.0
        if i > n - nr:
            e *= (n - i) / nr
        lfo = 0.8 + 0.2 * math.sin(TWO_PI * 0.07 * t)
        out[i] = (0.6 * math.sin(ph) + 0.5 * math.sin(ph * 0.5) + 0.7 * y) * e * lfo
    return out


def angua(dur=0.5, pitch=110.0):
    """Angu'a (tambor grave): seno com queda de afinação + clique."""
    n = int(dur * SR)
    out = [0.0] * n
    ph, rng = 0.0, random.Random(1)
    for i in range(n):
        t = i / SR
        f = pitch * math.exp(-t * 18.0) + 46.0
        ph += TWO_PI * f / SR
        a = math.exp(-t * 7.0)
        click = (rng.random() * 2 - 1) * math.exp(-t * 300.0) * 0.6
        out[i] = (math.sin(ph) * a + click) * (1.0 - math.exp(-i / 20.0))
    return out


def takuapu(dur=0.18):
    """Takuapu (bambu batido no chão): ruído curto + 'toc' grave."""
    n = int(dur * SR)
    out = [0.0] * n
    rng, y, alpha, ph = random.Random(2), 0.0, lp_alpha(2600), 0.0
    for i in range(n):
        t = i / SR
        x = rng.random() * 2 - 1
        y += alpha * (x - y)
        hp = x - y
        ph += TWO_PI * (95.0 * math.exp(-t * 30) + 70) / SR
        out[i] = hp * math.exp(-t * 60.0) * 0.9 + math.sin(ph) * math.exp(-t * 28.0) * 0.8
    return out


def mbaraka(dur=0.08):
    """Chocalho (mbaraka): ruído agudo bem curto."""
    n = int(dur * SR)
    out = [0.0] * n
    rng, y, alpha = random.Random(3), 0.0, lp_alpha(4000)
    for i in range(n):
        t = i / SR
        x = rng.random() * 2 - 1
        y += alpha * (x - y)
        out[i] = (x - y) * math.exp(-t * 70.0)
    return out


def snare_hit(dur=0.16):
    n = int(dur * SR)
    out = [0.0] * n
    rng, ph = random.Random(4), 0.0
    for i in range(n):
        t = i / SR
        ph += TWO_PI * 180 / SR
        out[i] = (rng.random() * 2 - 1) * math.exp(-t * 28.0) * 0.8 + math.sin(ph) * math.exp(-t * 40) * 0.5
    return out


def cymbal_swell(dur):
    n = int(dur * SR)
    out = [0.0] * n
    rng, y, alpha = random.Random(5), 0.0, lp_alpha(3500)
    for i in range(n):
        t = i / SR
        x = rng.random() * 2 - 1
        y += alpha * (x - y)
        u = t / dur
        out[i] = (x - y) * (u ** 2.2) * 0.9
    return out


def wind(dur, seed=9):
    n = int(dur * SR)
    out = [0.0] * n
    rng, y1, y2 = random.Random(seed), 0.0, 0.0
    for i in range(n):
        t = i / SR
        fc = 240 + 200 * math.sin(TWO_PI * 0.11 * t) + 120 * math.sin(TWO_PI * 0.037 * t + 1.0)
        a = lp_alpha(max(60.0, fc))
        x = rng.random() * 2 - 1
        y1 += a * (x - y1)
        y2 += a * (y1 - y2)
        amp = 0.55 + 0.45 * math.sin(TWO_PI * 0.09 * t + 2.0)
        out[i] = y2 * amp * 3.0
    return out


# ---------------------------------------------------------------- mixagem ----
class Mix:
    def __init__(self, seconds):
        n = int(seconds * SR)
        self.dry = [0.0] * n
        self.send = [0.0] * n
        self.n = n

    def place(self, samples, at, gain=1.0, send=0.0):
        off = int(at * SR)
        dry, snd = self.dry, self.send
        n = self.n
        for i, s in enumerate(samples):
            j = off + i
            if j >= n:
                break
            if j < 0:
                continue
            v = s * gain
            dry[j] += v
            if send:
                snd[j] += v * send


def reverb(send, decay=0.84, damp=0.35, spread=0):
    """Reverb Schroeder (4 combs + 2 all-pass) com amortecimento; spread muda os tempos (estéreo)."""
    n = len(send)
    out = [0.0] * n
    combs = [int(x * SR / 44100) + spread for x in (1557, 1617, 1491, 1422)]
    cbuf = [[0.0] * c for c in combs]
    cidx = [0] * 4
    cstore = [0.0] * 4
    aps = [int(x * SR / 44100) + spread // 2 for x in (225, 556)]
    abuf = [[0.0] * a for a in aps]
    aidx = [0] * 2
    for i in range(n):
        x = send[i]
        acc = 0.0
        for k in range(4):
            buf = cbuf[k]
            idx = cidx[k]
            y = buf[idx]
            cstore[k] = y * (1 - damp) + cstore[k] * damp
            buf[idx] = x + cstore[k] * decay
            idx += 1
            cidx[k] = 0 if idx == combs[k] else idx
            acc += y
        acc *= 0.25
        for k in range(2):
            buf = abuf[k]
            idx = aidx[k]
            b = buf[idx]
            buf[idx] = acc + b * 0.5
            acc = b - acc * 0.5
            idx += 1
            aidx[k] = 0 if idx == aps[k] else idx
        out[i] = acc
    return out


def finalize(dry, wet_l, wet_r, wet_gain=0.45, peak=0.92):
    n = len(dry)
    left = [dry[i] + wet_l[i] * wet_gain for i in range(n)]
    right = [dry[i] + wet_r[i] * wet_gain for i in range(n)]
    m = max(1e-9, max(max(abs(v) for v in left), max(abs(v) for v in right)))
    g = peak / m
    k = 1.25
    norm = math.tanh(k)
    out = array.array("h")
    for i in range(n):
        l = math.tanh(left[i] * g * k) / norm
        r = math.tanh(right[i] * g * k) / norm
        out.append(int(max(-32767, min(32767, l * 32767))))
        out.append(int(max(-32767, min(32767, r * 32767))))
    return out


def write_wav(path, data, channels=2):
    with wave.open(path, "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def mono16(samples, peak=0.9):
    m = max(1e-9, max(abs(v) for v in samples))
    g = peak / m
    out = array.array("h")
    for v in samples:
        out.append(int(max(-32767, min(32767, v * g * 32767))))
    return out


# ---------------------------------------------------------------- partitura ----
BPM = 90
BEAT = 60.0 / BPM
E8 = BEAT / 2  # colcheia
BAR = BEAT * 4

CHORDS = {
    "Dm": ["D", "F", "A"], "F": ["F", "A", "C"], "C": ["C", "E", "G"], "Bb": ["Bb", "D", "F"],
    "Gm": ["G", "Bb", "D"], "A": ["A", "C#", "E"],
}

# melodia da flauta por compasso (compassos 5-28), em colcheias
MELODY = {
    5: [("D5", 3), ("F5", 1), ("E5", 2), ("D5", 2)],
    6: [("C5", 4), ("A4", 2), ("C5", 2)],
    7: [("D5", 6), (None, 2)],
    8: [("F5", 2), ("G5", 2), ("A5", 3), ("G5", 1)],
    9: [("F5", 3), ("E5", 1), ("D5", 2), ("C5", 2)],
    10: [("D5", 4), ("Bb4", 2), ("A4", 2)],
    11: [("G4", 2), ("A4", 2), ("C5", 2), ("D5", 2)],
    12: [("D5", 8)],
    13: [("A5", 3), ("Bb5", 1), ("A5", 2), ("G5", 2)],
    14: [("F5", 4), ("G5", 2), ("A5", 2)],
    15: [("G5", 3), ("F5", 1), ("E5", 2), ("D5", 2)],
    16: [("E5", 6), (None, 2)],
    17: [("F5", 2), ("G5", 2), ("A5", 2), ("Bb5", 2)],
    18: [("A5", 3), ("G5", 1), ("F5", 2), ("G5", 2)],
    19: [("A5", 6), ("C#5", 2)],
    20: [("D5", 8)],
    21: [("D6", 3), ("C6", 1), ("Bb5", 2), ("A5", 2)],
    22: [("Bb5", 4), ("A5", 2), ("G5", 2)],
    23: [("A5", 3), ("G5", 1), ("F5", 2), ("E5", 2)],
    24: [("F5", 4), ("E5", 2), ("D5", 2)],
    25: [("A5", 2), ("Bb5", 2), ("C6", 2), ("D6", 2)],
    26: [("C6", 3), ("Bb5", 1), ("A5", 2), ("G5", 2)],
    27: [("A5", 4), ("Bb5", 2), ("C#6", 2)],
    28: [("D6", 8)],
}
PROGRESSION = {
    5: "Dm", 6: "C", 7: "Dm", 8: "F", 9: "Dm", 10: "Bb", 11: "Gm", 12: "Dm",
    13: "Dm", 14: "F", 15: "C", 16: "A", 17: "Bb", 18: "F", 19: "A", 20: "Dm",
    21: "Dm", 22: "Bb", 23: "F", 24: "Dm", 25: "Gm", 26: "F", 27: "A", 28: "Dm",
    29: "Dm", 30: "Dm", 31: "Dm", 32: "Dm",
}


def bar_t(bar):
    return (bar - 1) * BAR


def compose_theme():
    total = 32 * BAR + 1.5
    mx = Mix(total)
    print("  drone + vento")
    mx.place(drone(freq("D2"), 32 * BAR, attack=2.5, release=4.0), 0.0, 0.3, send=0.25)
    mx.place(wind(32 * BAR), 0.0, 0.10, send=0.1)

    # chamado da flauta na introdução (compassos 2-3)
    print("  flauta")
    call = [("A5", 4), ("G5", 1), ("F5", 1), ("E5", 1), ("D5", 1)]
    t = bar_t(2)
    for note, ln in call:
        mx.place(flute(freq(note), ln * E8 * 0.98, vib=0.009), t, 0.5, send=0.6)
        t += ln * E8
    mx.place(flute(freq("D5"), 7 * E8, vib=0.009), bar_t(3), 0.45, send=0.65)

    for bar, notes in MELODY.items():
        t = bar_t(bar)
        up = bar >= 21
        for note, ln in notes:
            if note is not None:
                g = 0.52 if not up else 0.5
                mx.place(flute(freq(note), ln * E8 * 0.95), t, g, send=0.55)
                if up:  # dobra uma oitava abaixo no clímax
                    low = note[:-1] + str(int(note[-1]) - 1)
                    mx.place(flute(freq(low), ln * E8 * 0.95), t, 0.3, send=0.5)
            t += ln * E8
    # outro: nota final longa
    mx.place(flute(freq("D5"), 2 * BAR, vib=0.01), bar_t(29), 0.5, send=0.7)
    mx.place(flute(freq("D6"), 1.5 * BAR, vib=0.012), bar_t(31), 0.22, send=0.8)

    print("  baixo")
    for bar in range(5, 29):
        root = CHORDS[PROGRESSION[bar]][0]
        t = bar_t(bar)
        if bar >= 21:
            fifth = CHORDS[PROGRESSION[bar]][2]
            pattern = [root, root, fifth, root, root, fifth, root, root]
            for k, nm in enumerate(pattern):
                mx.place(bass(freq(nm + "2"), E8 * 0.9), t + k * E8, 0.55, send=0.05)
        else:
            mx.place(bass(freq(root + "2"), 2 * BEAT * 0.95), t, 0.55, send=0.05)
            mx.place(bass(freq(root + "2"), 2 * BEAT * 0.95), t + 2 * BEAT, 0.5, send=0.05)

    print("  cordas e coro")
    for bar in range(9, 33):
        ch = CHORDS[PROGRESSION[bar]]
        t = bar_t(bar)
        if bar < 13:
            voices = [ch[0] + "3", ch[2] + "3"]          # só graves
            g = 0.16
        elif bar < 29:
            voices = [ch[0] + "3", ch[2] + "3", ch[1] + "4", ch[0] + "4"]
            g = 0.17 if bar < 21 else 0.23
        else:
            voices = [ch[0] + "3", ch[2] + "3", ch[1] + "4"]
            g = 0.14 * max(0.0, (33 - bar) / 4)
        for v in voices:
            mx.place(strings(freq(v), BAR * 1.02, cutoff=1300 if bar < 21 else 2100), t, g, send=0.4)
        if bar >= 13:
            cg = 0.11 if bar < 21 else 0.17
            if bar >= 29:
                cg = 0.1 * max(0.0, (33 - bar) / 4)
            for v in (ch[0] + "4", ch[2] + "4", ch[0] + "5"):
                mx.place(choir(freq(v), BAR * 1.02), t, cg, send=0.65)

    print("  metais")
    for bar in range(17, 29):
        ch = CHORDS[PROGRESSION[bar]]
        t = bar_t(bar)
        hits = [0.0] if bar < 21 else [0.0, 2.5 * BEAT]
        for h in hits:
            dur = BEAT * 0.6 if h == 0.0 else BEAT * 0.4
            for v in (ch[0] + "3", ch[2] + "3", ch[1] + "4"):
                mx.place(brass(freq(v), dur), t + h, 0.26, send=0.3)
        if bar in (20, 28):  # sustentação no fim das frases
            for v in (ch[0] + "3", ch[2] + "3", ch[1] + "4"):
                mx.place(brass(freq(v), BAR * 0.9), t, 0.16, send=0.35)

    print("  percussão")
    ang, tak, mar, sn = angua(), takuapu(), mbaraka(), snare_hit()
    for bar in range(3, 32):
        t = bar_t(bar)
        if bar < 5:
            pat_a, pat_t, pat_m = "x.......", "........", "........"
        elif bar < 13:
            pat_a, pat_t, pat_m = "x..x....", "....x.x.", "........"
        elif bar < 21:
            pat_a, pat_t, pat_m = "x..x.x..", ".x.x.x.x", "xxxxxxxx"
        elif bar < 29:
            pat_a, pat_t, pat_m = "x.xx.x.x", "x.x.x.x.", "xxxxxxxx"
        elif bar == 29:
            pat_a, pat_t, pat_m = "x.......", "........", "........"
        elif bar == 31:
            pat_a, pat_t, pat_m = "x.......", "........", "........"
        else:
            pat_a, pat_t, pat_m = "........", "........", "........"
        for k in range(8):
            if pat_a[k] == "x":
                mx.place(ang, t + k * E8, 0.85 if k == 0 else 0.65, send=0.2)
            if pat_t[k] == "x":
                mx.place(tak, t + k * E8, 0.45, send=0.3)
            if pat_m[k] == "x":
                mx.place(mar, t + k * E8, 0.09, send=0.2)
                mx.place(mar, t + k * E8 + E8 / 2, 0.06, send=0.2)
        if bar in (20, 28):  # rulo de caixa crescendo nos dois últimos tempos
            for k in range(8):
                mx.place(sn, t + 2 * BEAT + k * E8 / 2, 0.08 + 0.05 * k, send=0.3)
        if bar in (12, 20, 28):
            mx.place(cymbal_swell(BAR), t, 0.22, send=0.5)
        if bar == 21:
            mx.place(sn, t, 0.6, send=0.4)

    print("  reverb")
    wet_l = reverb(mx.send, spread=0)
    wet_r = reverb(mx.send, spread=23)
    return finalize(mx.dry, wet_l, wet_r)


def compose_lamento():
    """Peça curta da introdução narrativa: drone, flauta rubato e coro (~40 s)."""
    total = 40.0
    mx = Mix(total)
    mx.place(drone(freq("D2"), 38.0, attack=3.0, release=5.0), 0.0, 0.4, send=0.3)
    mx.place(wind(40.0, seed=13), 0.0, 0.12, send=0.1)
    phrase = [("D5", 3.0), ("F5", 1.2), ("E5", 1.6), ("D5", 2.6), (None, 1.0),
              ("A4", 1.4), ("C5", 1.0), ("D5", 3.2), (None, 1.2),
              ("F5", 1.2), ("G5", 1.0), ("A5", 3.5), ("G5", 1.0), ("F5", 1.4), ("E5", 1.0), ("D5", 5.0)]
    t = 3.0
    for note, d in phrase:
        if note:
            mx.place(flute(freq(note), d * 0.95, vib=0.009), t, 0.5, send=0.7)
        t += d
    for k, (chord, at, d) in enumerate((("Dm", 8.0, 8.0), ("Bb", 16.0, 6.0), ("Gm", 22.0, 5.0), ("A", 27.0, 4.0), ("Dm", 31.0, 7.0))):
        ch = CHORDS[chord]
        for v in (ch[0] + "4", ch[2] + "4", ch[1] + "4", ch[0] + "5"):
            mx.place(choir(freq(v), d), at, 0.1, send=0.7)
    mx.place(angua(), 8.0, 0.6, send=0.3)
    mx.place(angua(), 31.0, 0.7, send=0.3)
    wet_l = reverb(mx.send, decay=0.88, spread=0)
    wet_r = reverb(mx.send, decay=0.88, spread=29)
    return finalize(mx.dry, wet_l, wet_r, wet_gain=0.55)


# ---------------------------------------------------------------- efeitos ----
def sweep(f0, f1, dur, shape="sine", decay=8.0, duty=0.5):
    n = int(dur * SR)
    out = [0.0] * n
    ph = 0.0
    for i in range(n):
        t = i / SR
        f = f0 + (f1 - f0) * (t / dur)
        ph += TWO_PI * f / SR
        if shape == "sine":
            s = math.sin(ph)
        elif shape == "square":
            s = 1.0 if (ph / TWO_PI) % 1.0 < duty else -1.0
        else:
            s = 2.0 * ((ph / TWO_PI) % 1.0) - 1.0
        out[i] = s * math.exp(-t * decay)
    return out


def noise_burst(dur, fc=2000, decay=30.0, seed=1, hp=False):
    n = int(dur * SR)
    out = [0.0] * n
    rng, y, alpha = random.Random(seed), 0.0, lp_alpha(fc)
    for i in range(n):
        t = i / SR
        x = rng.random() * 2 - 1
        y += alpha * (x - y)
        out[i] = ((x - y) if hp else y) * math.exp(-t * decay)
    return out


def add(*parts):
    n = max(len(p) for p in parts)
    out = [0.0] * n
    for p in parts:
        for i, v in enumerate(p):
            out[i] += v
    return out


def seq(*items):
    """items: (samples, at_seconds, gain)"""
    n = max(int(at * SR) + len(s) for s, at, _ in items)
    out = [0.0] * n
    for s, at, g in items:
        off = int(at * SR)
        for i, v in enumerate(s):
            out[off + i] += v * g
    return out


def sfx_all():
    d5, a5, d6, fs5 = freq("D5"), freq("A5"), freq("D6"), freq("F#5")
    return {
        "pulo": sweep(280, 720, 0.14, decay=10),
        "aterrissar": add(sweep(110, 60, 0.1, decay=25), noise_burst(0.04, 900, 80)),
        "ataque": noise_burst(0.18, 3200, 14, hp=True, seed=2),
        "golpe": add(noise_burst(0.08, 1800, 40, seed=3), sweep(200, 90, 0.08, "square", 30)),
        "dano": sweep(260, 110, 0.3, "square", 7, duty=0.3),
        "morte": add(sweep(180, 40, 0.9, "saw", 3), noise_burst(0.5, 600, 6, seed=4)),
        "inimigo_morre": add(noise_burst(0.35, 1500, 9, seed=5), sweep(220, 50, 0.35, "saw", 8)),
        "coleta": seq((sweep(d5, d5, 0.1, decay=14), 0.0, 0.8), (sweep(a5, a5, 0.1, decay=14), 0.08, 0.8),
                      (sweep(d6, d6, 0.2, decay=10), 0.16, 0.8)),
        "cruz": seq((sweep(d5, d5, 0.9, decay=3), 0.0, 0.6), (sweep(fs5, fs5, 0.9, decay=3), 0.12, 0.5),
                    (sweep(a5, a5, 0.9, decay=3), 0.24, 0.5), (sweep(d6, d6, 1.2, decay=2.5), 0.36, 0.6)),
        "passo": noise_burst(0.05, 500, 90, seed=6),
        "ui_mover": sweep(620, 620, 0.05, decay=30),
        "ui_confirmar": seq((sweep(520, 520, 0.07, decay=25), 0.0, 1.0), (sweep(840, 840, 0.12, decay=18), 0.07, 1.0)),
        "tecla": noise_burst(0.02, 3000, 200, seed=7, hp=True),
    }


def ambience_all():
    out = {}
    out["vento"] = wind(12.0, seed=21)
    # fogueira: ruído grave + estalos aleatórios
    n = int(5.0 * SR)
    rng, y, a = random.Random(8), 0.0, lp_alpha(500)
    fire = [0.0] * n
    pop = 0
    for i in range(n):
        x = rng.random() * 2 - 1
        y += a * (x - y)
        v = y * 0.6
        if pop > 0:
            v += (rng.random() * 2 - 1) * (pop / 60.0)
            pop -= 1
        elif rng.random() < 0.0009:
            pop = rng.randrange(20, 60)
        fire[i] = v
    out["fogueira"] = fire
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    if only in (None, "musica"):
        print("tema principal: Esta terra tem dono")
        write_wav(os.path.join(OUT, "tema_esta_terra_tem_dono.wav"), compose_theme())
        print("lamento (introdução)")
        write_wav(os.path.join(OUT, "lamento.wav"), compose_lamento())
    if only in (None, "sfx"):
        for name, s in sfx_all().items():
            write_wav(os.path.join(OUT, f"sfx_{name}.wav"), mono16(s), channels=1)
        print("sfx ok")
    if only in (None, "ambiente"):
        for name, s in ambience_all().items():
            write_wav(os.path.join(OUT, f"amb_{name}.wav"), mono16(s, peak=0.6), channels=1)
        print("ambiente ok")


if __name__ == "__main__":
    main()
