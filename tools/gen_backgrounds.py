#!/usr/bin/env python3
"""Camadas de parallax: céu com lua, coxilhas, ruínas de São Miguel com umbus, e vegetação em primeiro plano."""
import math
import os
import random

from palette import P
from pixelart import Canvas, preview, bayer, mix

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "backgrounds")
W = 960  # largura das camadas repetíveis


def sky(w=480, h=300):
    """Céu 480x300 (a camada fica em y=-24, então o horizonte quente cai atrás das coxilhas)."""
    c = Canvas(w, h)
    c.gradient_v(0, h - 1, [
        (0.00, P["sky0"]), (0.20, P["sky1"]), (0.36, P["sky2"]), (0.46, P["sky3"]),
        (0.56, P["sky4"]), (0.66, P["sky5"]), (0.80, P["sky6"]), (1.00, P["sky6"]),
    ])
    rng = random.Random(7)
    for _ in range(120):
        x, y = rng.randrange(0, w), rng.randrange(0, int(h * 0.5))
        bright = rng.random()
        col = P["cream"] if bright > 0.8 else P["star_dim"]
        c.set(x, y, col)
        if bright > 0.95:
            c.set(x + 1, y, P["star_dim"])
            c.set(x, y + 1, P["star_dim"])
    # lua (a "lunar" de Sepé)
    mx, my, r = 372, 72, 14
    for rr in range(r + 10, r, -1):
        t = (rr - r) / 10.0
        c.ring(mx, my, rr, None)
        for y in range(-rr, rr + 1):
            for x in range(-rr, rr + 1):
                d = (x * x + y * y) ** 0.5
                if rr - 0.5 <= d <= rr + 0.5:
                    base = c.get(mx + x, my + y)
                    if (1 - t) * 0.45 > bayer(mx + x, my + y):
                        c.set(mx + x, my + y, mix(base, P["cream"], 0.35))
    c.circle(mx, my, r, P["cream"])
    for (dx, dy, rr) in ((-4, -3, 3), (5, 2, 2), (-2, 6, 2), (6, -6, 1), (-7, 4, 1)):
        c.circle(mx + dx, my + dy, rr, P["moon_s"])
    # nuvens finas de fim de tarde
    for (x0, y0, ln, th, col) in ((40, 124, 150, 4, P["sky2"]), (210, 142, 120, 3, P["sky3"]),
                                  (300, 160, 160, 4, P["sky4"]), (90, 172, 110, 3, P["sky5"]),
                                  (380, 132, 90, 3, P["sky3"])):
        for y in range(y0, y0 + th):
            for x in range(x0, x0 + ln):
                edge = min(x - x0, x0 + ln - 1 - x) / 12.0
                vert = 1.0 - abs((y - y0) - th / 2) / (th / 2 + 0.5)
                a = min(1.0, edge) * vert * 0.9
                if a > bayer(x, y):
                    c.set(x, y, mix(c.get(x, y), col, 0.7))
    return c


def hills(w=W, h=110):
    c = Canvas(w, h)

    def profile(x, base, amps, phases):
        return base + sum(a * math.sin(2 * math.pi * k * x / w + p) for (k, a), p in zip(amps, phases))

    far_amps = [(1, 14), (2, 9), (3, 5), (5, 3), (8, 1.5)]
    near_amps = [(1, 10), (2, 12), (4, 5), (7, 2)]
    for x in range(w):
        yf = int(profile(x, 40, far_amps, [0.3, 1.9, 4.1, 0.7, 2.2]))
        yn = int(profile(x, 66, near_amps, [2.4, 0.9, 3.3, 1.1]))
        c.vline(x, yf, h - 1, P["hill_far"])
        c.set(x, yf, mix(P["hill_far"], P["sky3"], 0.35))
        c.vline(x, yn, h - 1, P["hill_far2"])
        c.set(x, yn, mix(P["hill_far2"], P["hill_far"], 0.6))
    return c


def tree(c, x, y, rx, ry, dark, mid, light, trunk):
    """Umbuzeiro: copa larga e baixa, tronco curto."""
    c.rect(x - 2, y, 5, 14, trunk)
    c.line(x, y + 2, x - 10, y - 4, trunk, width=2)
    c.line(x, y + 2, x + 9, y - 5, trunk, width=2)
    c.ellipse(x, y - 8, rx, ry, dark)
    c.ellipse(x - rx // 3, y - 10, rx // 2 + 2, ry // 2 + 1, mid)
    c.ellipse(x + rx // 3, y - 9, rx // 2, ry // 2, mid)
    c.ellipse(x - rx // 4, y - 12, rx // 3, ry // 3, light)
    rng = random.Random(x)
    for _ in range(rx):
        px, py = x + rng.randrange(-rx, rx), y - 8 + rng.randrange(-ry, ry)
        if c.get(px, py) == dark:
            c.set(px, py, mid)


def church(c, x, ground):
    """Fachada da igreja de São Miguel Arcanjo (em ruína), estilizada."""
    d, m, l, ll = P["ruin_d"], P["ruin"], P["ruin_l"], P["ruin_ll"]
    # torre (à esquerda)
    tx, tw, th = x, 34, 100
    c.rect(tx, ground - th, tw, th, m)
    c.vline(tx, ground - th, ground, l)
    c.rect(tx + tw - 4, ground - th, 4, th, d)
    for i, y in enumerate(range(ground - th + 10, ground - 10, 26)):
        c.rect(tx + 10, y, 12, 16, d)                     # vãos em arco
        c.ellipse(tx + 15, y, 6, 4, d)
        c.hline(tx + 10, tx + 21, y + 16, l)
    c.hline(tx, tx + tw - 1, ground - th, ll)
    c.rect(tx + 4, ground - th - 6, 26, 6, m)             # topo arruinado
    c.hline(tx + 4, tx + 29, ground - th - 6, ll)
    c.rect(tx + 12, ground - th - 12, 3, 6, d)
    # corpo principal
    bx, bw, bh = x + tw, 112, 70
    c.rect(bx, ground - bh, bw, bh, m)
    c.rect(bx + bw - 5, ground - bh, 5, bh, d)
    c.hline(bx, bx + bw - 1, ground - bh, ll)
    # frontão triangular
    for i in range(22):
        c.hline(bx + 10 + i * 2, bx + bw - 11 - i * 2, ground - bh - i, m if i % 2 else l)
    c.rect(bx + bw // 2 - 1, ground - bh - 30, 3, 9, d)   # cruz
    c.rect(bx + bw // 2 - 4, ground - bh - 27, 9, 2, d)
    # três portais em arco e pilastras
    for i in range(3):
        px = bx + 14 + i * 32
        c.rect(px, ground - 40, 16, 40, d)
        c.ellipse(px + 7, ground - 40, 8, 6, d)
        c.vline(px, ground - 40, ground, P["ruin_d"])
    for i in range(4):
        px = bx + 6 + i * 32
        c.rect(px, ground - bh + 4, 3, bh - 4, l)
        c.set(px + 3, ground - bh + 4, d)
    # janelas altas
    for i in range(3):
        px = bx + 18 + i * 32
        c.rect(px, ground - bh + 10, 8, 10, d)
    # textura de tijolos (dithering) e desgaste
    rng = random.Random(3)
    for y in range(ground - th - 12, ground):
        for xx in range(x, bx + bw):
            if c.get(xx, y) == m and rng.random() < 0.05:
                c.set(xx, y, d if rng.random() < 0.5 else l)


def arcade(c, x, ground, n=6, step=26):
    """Arcada em ruína (a antiga 'quadra' do povoado)."""
    d, m, l, ll = P["ruin_d"], P["ruin"], P["ruin_l"], P["ruin_ll"]
    h = 46
    for i in range(n + 1):
        px = x + i * step
        c.rect(px, ground - h, 6, h, m)
        c.vline(px, ground - h, ground, l)
        c.vline(px + 5, ground - h, ground, d)
    for i in range(n):
        px = x + i * step + 6
        broken = i in (2, 4)
        top = ground - h
        if not broken:
            c.rect(px, top, step - 6, 8, m)
            c.hline(px, px + step - 7, top, ll)
            c.ellipse(px + (step - 6) // 2, top + 8, (step - 6) // 2, 7, m)
            for yy in range(top + 8, top + 16):
                for xx in range(px, px + step - 6):
                    dx, dy = xx - (px + (step - 6) / 2), yy - (top + 8)
                    if dx * dx / 100.0 + dy * dy / 49.0 <= 1.0 and dy >= 0:
                        c.set(xx, yy, d)
        else:
            c.rect(px, top + 6, 4, 6, m)
            c.rect(px + step - 11, top + 9, 5, 4, m)


def ruins(w=W, h=150):
    c = Canvas(w, h)
    ground = h - 10
    c.rect(0, ground, w, 10, P["hill_near"])
    c.hline(0, w - 1, ground, mix(P["hill_near"], P["ruin"], 0.3))
    church(c, 70, ground)
    arcade(c, 300, ground)
    # muros baixos
    for (x0, ln) in ((520, 70), (820, 90)):
        c.rect(x0, ground - 14, ln, 14, P["ruin"])
        c.hline(x0, x0 + ln - 1, ground - 14, P["ruin_ll"])
        c.rect(x0 + ln // 2, ground - 20, 8, 6, P["ruin"])
    for x in (600, 720, 940 - 40):
        tree(c, x, ground - 14, 34, 16, P["tree_d"], P["tree"], P["tree_l"], P["ruin_d"])
    # casas dos índios (longas, telhado baixo)
    for x0 in (440, 760):
        c.rect(x0, ground - 18, 50, 18, P["ruin_d"])
        for i in range(0, 50, 2):
            c.hline(x0 - 2 + i // 2, x0 + 52 - i // 2, ground - 18 - i // 2, P["ruin"] if i % 4 else P["ruin_l"])
            if i >= 12:
                break
        for i in range(3):
            c.rect(x0 + 6 + i * 16, ground - 10, 5, 10, P["hill_near"])
    return c


def foreground(w=W, h=40):
    c = Canvas(w, h)
    rng = random.Random(11)
    for x in range(0, w, 3):
        hh = rng.randrange(6, 26)
        col = P["fg"] if rng.random() < 0.7 else P["fg_l"]
        c.vline(x, h - hh, h - 1, col)
        if rng.random() < 0.4:
            c.set(x + 1, h - hh + rng.randrange(0, 4), col)
        if rng.random() < 0.25:
            c.line(x, h - hh, x + rng.choice((-2, 2)), h - hh - 3, col)
    for x in range(0, w, 97):
        c.ellipse(x + 20, h - 8, 14, 8, P["fg"])
        c.ellipse(x + 26, h - 11, 8, 5, P["fg_l"])
    return c


def main(preview_dir=None):
    os.makedirs(OUT, exist_ok=True)
    layers = {"ceu": sky(), "coxilhas": hills(), "ruinas": ruins(), "capim": foreground()}
    for name, c in layers.items():
        c.save(os.path.join(OUT, f"{name}.png"))
    if preview_dir:
        comp = Canvas(480, 270)
        comp.blit(layers["ceu"], 0, -24)
        comp.blit(layers["coxilhas"], 0, 104)
        comp.blit(layers["ruinas"], -60, 56)
        comp.rect(0, 190, 480, 80, P["dirt"])
        comp.blit(layers["capim"], 0, 236)
        preview([comp], 3, os.path.join(preview_dir, "prev_bg.png"))
    print("backgrounds:", list(layers))


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else None)
