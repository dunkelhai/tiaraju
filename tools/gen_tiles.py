#!/usr/bin/env python3
"""Tileset do pampa e das ruínas, props (fogueira, cruz missioneira, erva, arco), UI e texturas de FX."""
import os
import random

from palette import P
from pixelart import Canvas, sheet, preview, rgba

ROOT = os.path.join(os.path.dirname(__file__), "..", "assets")
T = 16


# ------------------------------------------------------------------ tiles ----
def grass_top(seed, left=False, right=False):
    rng = random.Random(seed)
    c = Canvas(T, T)
    c.rect(0, 5, T, T - 5, P["dirt"])
    c.speckle(0, 6, T, T - 6, P["dirt_l"], 0.10, rng)
    c.speckle(0, 7, T, T - 7, P["dirt_d"], 0.12, rng)
    c.rect(0, 2, T, 3, P["grass"])
    c.dither_rect(0, 2, T, 2, P["grass"], P["grass_l"], 0.45)
    c.dither_rect(0, 4, T, 1, P["grass"], P["grass_d"], 0.5)
    c.hline(0, T - 1, 5, P["grass_d"])
    # lâminas de capim saindo do tile
    for x in range(T):
        r = rng.random()
        if r < 0.35:
            c.set(x, 1, P["grass_l"] if rng.random() < 0.5 else P["grass"])
            if r < 0.12:
                c.set(x, 0, P["grass_l"])
    # raízes/terra
    for _ in range(2):
        x = rng.randrange(1, T - 2)
        c.set(x, 6, P["grass_d"])
    if left:
        c.vline(0, 2, T - 1, P["dirt_d"])
        c.vline(1, 6, T - 1, P["dirt_d"])
        c.set(0, 2, P["grass_d"])
    if right:
        c.vline(T - 1, 2, T - 1, P["dirt_d"])
        c.vline(T - 2, 6, T - 1, P["dirt_d"])
        c.set(T - 1, 2, P["grass_d"])
    return c


def dirt_fill(seed, left=False, right=False):
    rng = random.Random(seed)
    c = Canvas(T, T, P["dirt"])
    c.speckle(0, 0, T, T, P["dirt_l"], 0.09, rng)
    c.speckle(0, 0, T, T, P["dirt_d"], 0.14, rng)
    # pedrinha
    x, y = rng.randrange(2, 12), rng.randrange(2, 12)
    c.rect(x, y, 3, 2, P["dirt_ll"])
    c.set(x, y + 1, P["dirt_d"])
    if left:
        c.vline(0, 0, T - 1, P["dirt_d"])
    if right:
        c.vline(T - 1, 0, T - 1, P["dirt_d"])
    return c


def stone(seed, top=False, bottom=False, left=False, right=False, moss=False):
    rng = random.Random(seed)
    c = Canvas(T, T, P["stone"])
    # duas fiadas de tijolos de arenito (8x8), segunda fiada deslocada
    for row in range(2):
        y0 = row * 8
        off = 0 if row == 0 else 4
        c.hline(0, T - 1, y0 + 7, P["stone_dd"])
        for bx in range(-1, 3):
            x0 = bx * 8 + off
            c.vline(x0 + 7, y0, y0 + 6, P["stone_dd"])
            c.hline(x0, x0 + 6, y0, P["stone_l"])
            c.set(x0, y0, P["stone_ll"])
            c.vline(x0, y0 + 1, y0 + 6, P["stone_l"])
            c.hline(x0 + 1, x0 + 6, y0 + 6, P["stone_d"])
    c.speckle(0, 0, T, T, P["stone_d"], 0.06, rng, only_over=P["stone"])
    c.speckle(0, 0, T, T, P["stone_l"], 0.04, rng, only_over=P["stone"])
    if moss:
        for _ in range(5):
            x, y = rng.randrange(0, T), rng.randrange(0, T)
            c.set(x, y, P["leaf"])
            c.set(x + 1, y, P["leaf_d"])
    if top:
        c.hline(0, T - 1, 0, P["stone_ll"])
        c.dither_rect(0, 1, T, 1, P["stone_l"], P["stone_ll"], 0.4)
        for x in range(T):
            if rng.random() < 0.25:
                c.set(x, 0, P["grass_d"])
    if bottom:
        c.hline(0, T - 1, T - 1, P["stone_dd"])
        c.hline(0, T - 1, T - 2, P["stone_d"])
    if left:
        c.vline(0, 0, T - 1, P["stone_dd"])
        c.vline(1, 0, T - 1, P["stone_l"])
    if right:
        c.vline(T - 1, 0, T - 1, P["stone_dd"])
        c.vline(T - 2, 0, T - 1, P["stone_d"])
    return c


def ledge(kind):
    """Laje de pedra fina (plataforma de mão única): só as 6 linhas de cima."""
    c = Canvas(T, T)
    x0, x1 = 0, T - 1
    if kind == "left":
        x0 = 1
    if kind == "right":
        x1 = T - 2
    c.rect(x0, 1, x1 - x0 + 1, 5, P["stone"])
    c.hline(x0, x1, 0, P["stone_ll"])
    c.hline(x0, x1, 1, P["stone_l"])
    c.hline(x0, x1, 5, P["stone_dd"])
    c.hline(x0, x1, 4, P["stone_d"])
    for x in range(x0 + 3, x1, 5):
        c.vline(x, 2, 4, P["stone_dd"])
    if kind == "left":
        c.vline(0, 1, 5, P["stone_dd"])
        c.set(0, 0, P["outline"])
    if kind == "right":
        c.vline(T - 1, 1, 5, P["stone_dd"])
    return c


def deco(kind, seed=1):
    rng = random.Random(seed)
    c = Canvas(T, T)
    if kind in ("grass_a", "grass_b"):
        n = 5 if kind == "grass_a" else 7
        for i in range(n):
            x = 2 + i * 2 + (1 if kind == "grass_b" else 0)
            h = rng.randrange(4, 10)
            col = P["grass_l"] if rng.random() < 0.5 else P["grass"]
            c.vline(x, T - h, T - 1, col)
            if rng.random() < 0.5:
                c.set(x + 1, T - h, P["grass_dry"])
    elif kind == "flowers":  # macela
        for i in range(4):
            x = 2 + i * 4
            h = rng.randrange(4, 8)
            c.vline(x, T - h, T - 1, P["grass"])
            c.set(x, T - h - 1, P["gold_l"])
            c.set(x + 1, T - h, P["gold"])
    elif kind == "rock":
        c.ellipse(8, 12, 5, 3, P["dirt_ll"])
        c.ellipse(7, 11, 3, 2, P["steel_d"])
        c.hline(4, 12, 15, P["dirt_d"])
    elif kind == "shards":  # cacos de cerâmica guarani
        c.rect(3, 12, 4, 3, P["stone_l"])
        c.rect(9, 13, 5, 2, P["stone"])
        c.set(4, 12, P["stone_ll"])
        c.set(10, 13, P["red_d"])
        c.set(12, 13, P["red_d"])
    elif kind == "rubble":
        c.rect(2, 11, 6, 5, P["stone_d"])
        c.rect(7, 13, 7, 3, P["stone"])
        c.rect(5, 9, 4, 3, P["stone"])
        c.set(5, 9, P["stone_l"])
        c.hline(2, 13, 15, P["stone_dd"])
    elif kind == "bush":
        c.ellipse(8, 11, 6, 4, P["leaf"])
        c.ellipse(6, 10, 3, 2, P["leaf_l"])
        c.ellipse(10, 13, 4, 2, P["leaf_d"])
    return c


def build_tileset():
    """Devolve (canvas, mapa nome -> (col, linha))."""
    grid = {}
    rows = [
        [("grass_a", grass_top(1)), ("grass_b", grass_top(2)), ("grass_c", grass_top(3)),
         ("grass_l", grass_top(4, left=True)), ("grass_r", grass_top(5, right=True)),
         ("dirt_a", dirt_fill(6)), ("dirt_b", dirt_fill(7)), ("dirt_l", dirt_fill(8, left=True)),
         ("dirt_r", dirt_fill(9, right=True))],
        [("stone_top", stone(10, top=True)), ("stone_a", stone(11)), ("stone_b", stone(12, moss=True)),
         ("stone_l", stone(13, left=True)), ("stone_r", stone(14, right=True)),
         ("stone_tl", stone(15, top=True, left=True)), ("stone_tr", stone(16, top=True, right=True)),
         ("stone_single", stone(17, top=True, left=True, right=True)),
         ("stone_bottom", stone(18, bottom=True))],
        [("deco_grass_a", deco("grass_a", 21)), ("deco_grass_b", deco("grass_b", 22)),
         ("deco_flowers", deco("flowers", 23)), ("deco_rock", deco("rock")), ("deco_shards", deco("shards")),
         ("deco_rubble", deco("rubble")), ("deco_bush", deco("bush"))],
        [("ledge_l", ledge("left")), ("ledge_m", ledge("mid")), ("ledge_r", ledge("right")),
         ("stone_bl", stone(19, bottom=True, left=True)), ("stone_br", stone(20, bottom=True, right=True))],
    ]
    cols = max(len(r) for r in rows)
    c = Canvas(cols * T, len(rows) * T)
    for ry, row in enumerate(rows):
        for rx, (name, tile) in enumerate(row):
            c.blit(tile, rx * T, ry * T)
            grid[name] = (rx, ry)
    return c, grid


# ------------------------------------------------------------------ props ----
def campfire():
    frames = []
    for i in range(3):
        c = Canvas(16, 16)
        # lenha
        c.line(2, 14, 13, 11, P["wood"], width=2)
        c.line(2, 11, 13, 14, P["wood_l"], width=2)
        c.hline(3, 12, 15, P["wood_d"])
        # chamas (três silhuetas diferentes)
        shapes = [
            ["....rr....", "...rrrr...", "..rroorr..", "..rooyor..", "...oyyo...", "...oyyo...", "....yy...."],
            ["...rr.....", "..rrrr....", "..rooro...", ".rroyyor..", "..roooro..", "...oyyo...", "....yy...."],
            [".....rr...", "....rrrr..", "...rroor..", "..rroyyor.", "..rooyyo..", "...oyyo...", "....yy...."],
        ][i]
        legend = {"r": P["fire_r"], "o": P["fire_o"], "y": P["fire_y"]}
        c.paint_ascii(shapes, legend, 3, 4)
        # faíscas
        rng = random.Random(100 + i)
        for _ in range(3):
            c.set(rng.randrange(3, 13), rng.randrange(0, 5), P["fire_y"])
        frames.append(c)
    return frames


def cruz_missioneira(active):
    """Cruz de duas travessas (símbolo das Missões), 16x24."""
    c = Canvas(16, 24)
    wood, light = (P["wood"], P["wood_l"]) if not active else (P["gold"], P["gold_l"])
    c.rect(7, 1, 2, 22, wood)
    c.vline(7, 1, 22, light)
    c.rect(3, 5, 10, 2, wood)
    c.hline(3, 12, 5, light)
    c.rect(1, 10, 14, 2, wood)
    c.hline(1, 14, 10, light)
    c.rect(5, 22, 6, 2, P["stone_d"])
    c.hline(5, 10, 22, P["stone"])
    if active:
        for x, y in ((5, 3), (10, 3), (2, 8), (13, 8), (7, 0)):
            c.set(x, y, P["fire_y"])
    return c.outline(P["outline"])


def erva():
    """Cuia de chimarrão com bomba — item de cura."""
    c = Canvas(12, 12)
    c.ellipse(5, 8, 4, 3, P["wood_l"])
    c.ellipse(4, 7, 2, 1, P["skin_l"])
    c.rect(2, 5, 7, 2, P["grass"])
    c.hline(2, 8, 5, P["grass_l"])
    c.line(7, 6, 10, 1, P["steel"])
    c.set(10, 1, P["steel_d"])
    c.hline(3, 7, 11, P["wood_d"])
    return c.outline(P["outline"])


def heart(full):
    c = Canvas(8, 8)
    rows = [".##.##..", "#######.", "#######.", ".#####..", "..###...", "...#...."]
    if full:
        c.paint_ascii(rows, {"#": P["red_l"]}, 0, 1)
        c.set(1, 2, P["cream"])
        c.set(2, 3, P["red"])
    else:
        c.paint_ascii(rows, {"#": P["grey"]}, 0, 1)
    return c.outline(P["outline"])


def arch():
    """Arco de arenito (meta da fase), 32x48."""
    c = Canvas(32, 48)
    for x0 in (2, 24):
        c.rect(x0, 14, 6, 34, P["stone"])
        c.vline(x0, 14, 47, P["stone_l"])
        c.vline(x0 + 5, 14, 47, P["stone_dd"])
        for y in range(16, 48, 6):
            c.hline(x0 + 1, x0 + 4, y, P["stone_d"])
    # arco
    for y in range(0, 14):
        for x in range(0, 32):
            dx, dy = x - 15.5, y - 14
            r2 = dx * dx + dy * dy
            if 70 <= r2 <= 256:
                c.set(x, y, P["stone"])
            if 70 <= r2 <= 100:
                c.set(x, y, P["stone_dd"])
            if 230 <= r2 <= 256:
                c.set(x, y, P["stone_l"])
    c.rect(13, 0, 6, 3, P["stone_l"])
    # cruz pequena no topo
    c.rect(15, -2, 2, 1, P["stone_ll"])
    c.hline(0, 31, 47, P["stone_dd"])
    return c.outline(P["outline"])


def light_radial(size=64):
    c = Canvas(size, size)
    r = size / 2
    for y in range(size):
        for x in range(size):
            d = ((x + 0.5 - r) ** 2 + (y + 0.5 - r) ** 2) ** 0.5 / r
            a = max(0.0, 1.0 - d)
            a = a * a
            c.set(x, y, (255, 255, 255, int(255 * a)))
    return c


def vignette(w=480, h=270):
    c = Canvas(w, h)
    cx, cy = w / 2, h / 2
    for y in range(h):
        for x in range(w):
            d = (((x - cx) / cx) ** 2 + ((y - cy) / cy) ** 2) ** 0.5
            a = max(0.0, min(1.0, (d - 0.6) / 0.6)) * 0.6
            # quantiza em 4 níveis com dithering (estética pixel)
            lvl = a * 4
            base = int(lvl)
            frac = lvl - base
            from pixelart import bayer
            if frac > bayer(x, y):
                base += 1
            if base > 0:
                c.set(x, y, (10, 6, 16, min(255, base * 64)))
    return c


def pixel():
    return Canvas(2, 2, (255, 255, 255, 255))


def cursor_spear():
    c = Canvas(12, 6)
    c.hline(0, 7, 2, P["wood"])
    c.hline(0, 7, 3, P["wood_d"])
    c.hline(8, 11, 2, P["steel"])
    c.hline(8, 10, 3, P["steel_d"])
    c.set(11, 3, P["steel"])
    return c.outline(P["outline"])


def main(preview_dir=None):
    tiles_dir = os.path.join(ROOT, "tiles")
    props_dir = os.path.join(ROOT, "sprites")
    ui_dir = os.path.join(ROOT, "ui")
    fx_dir = os.path.join(ROOT, "fx")
    for d in (tiles_dir, props_dir, ui_dir, fx_dir):
        os.makedirs(d, exist_ok=True)
    ts, grid = build_tileset()
    ts.save(os.path.join(tiles_dir, "tileset.png"))
    with open(os.path.join(tiles_dir, "tileset.txt"), "w") as f:
        for k, (x, y) in grid.items():
            f.write(f"{k}={x},{y}\n")
    fire = campfire()
    sheet(fire).save(os.path.join(props_dir, "fogueira.png"))
    sheet([cruz_missioneira(False), cruz_missioneira(True)]).save(os.path.join(props_dir, "cruz.png"))
    erva().save(os.path.join(props_dir, "erva.png"))
    arch().save(os.path.join(props_dir, "arco.png"))
    heart(True).save(os.path.join(ui_dir, "coracao_cheio.png"))
    heart(False).save(os.path.join(ui_dir, "coracao_vazio.png"))
    cursor_spear().save(os.path.join(ui_dir, "cursor.png"))
    vignette().save(os.path.join(ui_dir, "vinheta.png"))
    light_radial(96).save(os.path.join(fx_dir, "luz.png"))
    pixel().save(os.path.join(fx_dir, "pixel.png"))
    if preview_dir:
        preview([ts], 4, os.path.join(preview_dir, "prev_tiles.png"))
        preview(fire + [cruz_missioneira(False), cruz_missioneira(True), erva(), arch(), heart(True), heart(False), cursor_spear()],
                6, os.path.join(preview_dir, "prev_props.png"))
    print("tiles:", len(grid))


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else None)
