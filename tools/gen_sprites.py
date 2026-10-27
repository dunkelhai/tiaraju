#!/usr/bin/env python3
"""Sprites de personagens: Sepé Tiaraju (jogador) e o soldado luso-espanhol.

Frames de 40x32. Cabeça e torso desenhados à mão (ASCII); pernas vêm de um rig
de dois segmentos (coxa/canela) com tabela de passada; contorno automático.
"""
import math
import os

from palette import P
from pixelart import Canvas, sheet, preview

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "sprites")
FW, FH = 40, 32
OX, OY = 14, 3  # origem da arte dentro do frame

LEG = {
    # fase -> (ângulo coxa, ângulo canela), graus a partir da vertical; + = frente
    "run": [(30, 15), (5, 5), (-25, -10), (-30, -75), (0, -70), (35, -10)],
    "idle": [(2, 2), (-2, -2)],
    "jump": [(25, -70), (-15, -45)],
    "fall": [(30, 10), (-25, -25)],
    "hurt": [(35, 20), (-30, -20)],
    "attack": [(25, 10), (-20, -10)],
}
RUN_BOB = [0, 1, 0, 0, 1, 0]


def leg(c, hip, angles, L1, L2, col, shade, foot, boot=None):
    a1, a2 = (math.radians(a) for a in angles)
    kx, ky = hip[0] + L1 * math.sin(a1), hip[1] + L1 * math.cos(a1)
    fx, fy = kx + L2 * math.sin(a2), ky + L2 * math.cos(a2)
    kx, ky, fx, fy = round(kx), round(ky), round(fx), round(fy)
    c.line(hip[0], hip[1], kx, ky, col, width=3, shade=shade)
    c.line(kx, ky, fx, fy, boot or col, width=3, shade=None if boot else shade)
    c.rect(fx - 1, fy, 4, 2, foot)


# ---------------------------------------------------------------- Sepé ----
SEPE_LEGEND = {
    "h": P["hair"], "H": P["hair2"], "r": P["red"], "R": P["red_l"],
    "s": P["skin"], "S": P["skin_l"], "d": P["skin_d"], "k": P["outline"],
    "w": P["white"], "W": P["white_s"], "x": P["white_d"],
    "p": P["wood"], "P": P["wood_l"], "t": P["steel"], "T": P["steel_d"],
    "y": P["gold"], "f": P["wood_d"],
}

# Torso em pé (mão direita segurando a lança vertical na coluna rel. 16)
SEPE_TORSO = """
..hhhhhh..........
.hhhhhhhh.........
hhhHHhhhhh........
hhrrrrrrrh........
hhsSSSSsSh........
hhsSkSSkS.........
hhsSSSSSs.........
hhhsssds..........
.hh.ddd...........
.hhwwwww..........
hhwwwwwwwws.......
hwwwwrwwwwwww.....
swwwwwwwwwwwwwssSs
sWwwwwwwwwwwx..sSs
xWwwwwwwwwwx......
xrrrrrrrrrr.......
.RrrrrrrrRr.......
"""

# Torso atacando: braço estendido para a frente, mão mais à direita
SEPE_TORSO_ATTACK = """
..hhhhhh..............
.hhhhhhhh.............
hhhHHhhhhh............
hhrrrrrrrh............
hhsSSSSsSh............
hhsSkSSkS.............
hhsSSSSSs.............
hhhsssds..............
.hh.ddd...............
.hhwwwww..............
hhwwwwwwwws...........
hwwwwrwwwwwwwwwwss....
swwwwwwwwwwwwwwwwssSs.
sWwwwwwwwwwwx.....sSs.
xWwwwwwwwwwx..........
xrrrrrrrrrr...........
.RrrrrrrrRr...........
"""

SEPE_TORSO_HURT = SEPE_TORSO.replace("hhsSkSSkS", "hhsSdSSdS")


def spear_v(c, x, y_top, y_bottom):
    c.set(x, y_top, P["steel"])
    c.set(x, y_top + 1, P["steel"])
    c.set(x, y_top + 2, P["steel_d"])
    c.set(x, y_top + 3, P["red_l"])
    c.set(x, y_top + 4, P["red"])
    for y in range(y_top + 5, y_bottom + 1):
        c.set(x, y, P["wood_l"] if y % 4 == 0 else P["wood"])


def spear_h(c, x_tip, y, length):
    """Lança horizontal apontando para a direita; x_tip é a ponta."""
    for i in range(length):
        x = x_tip - i
        if i < 3:
            col = P["steel"] if i < 2 else P["steel_d"]
        elif i < 5:
            col = P["red_l"] if i == 3 else P["red"]
        else:
            col = P["wood_l"] if x % 4 == 0 else P["wood"]
        c.set(x, y, col)
    c.set(x_tip - 2, y - 1, P["steel_d"])
    c.set(x_tip - 2, y + 1, P["steel_d"])


def sepe_frame(pose, phase=0, bob=0, torso=SEPE_TORSO, lean=0):
    c = Canvas(FW, FH)
    hip_y = OY + 18 + bob
    # lança vertical antes do corpo (a mão cobre o cabo)
    if pose in ("idle", "run", "jump", "fall", "hurt"):
        spear_v(c, OX + 16 + lean, 0 + bob, hip_y + 8)
    # pélvis
    c.rect(OX + 1 + lean, hip_y - 1, 10, 3, P["white"])
    c.rect(OX + 11 + lean, hip_y - 1, 1, 3, P["white_s"])
    # pernas: trás primeiro (sombreada), frente depois
    table = LEG[pose]
    if pose == "run":
        back, front = table[(phase + 3) % 6], table[phase % 6]
    elif pose == "idle":
        back, front = table[phase % 2], table[(phase + 1) % 2]
    else:
        front, back = table
    leg(c, (OX + 3 + lean, hip_y), back, 4, 4, P["white_s"], P["white_d"], P["wood_d"])
    leg(c, (OX + 8 + lean, hip_y), front, 4, 4, P["white"], P["white_s"], P["wood_d"])
    # torso por cima
    c.paint_ascii(torso, SEPE_LEGEND, OX + lean, OY + bob)
    return c


def sepe_frames():
    frames = {}
    frames["idle"] = [sepe_frame("idle", 0), sepe_frame("idle", 1, bob=1)]
    frames["run"] = [sepe_frame("run", i, bob=RUN_BOB[i]) for i in range(6)]
    frames["jump"] = [sepe_frame("jump", bob=-1)]
    frames["fall"] = [sepe_frame("fall", bob=0)]
    frames["hurt"] = [sepe_frame("hurt", bob=1, torso=SEPE_TORSO_HURT, lean=-1)]
    # ataque: preparação (lança recuada), estocada, recuperação
    a1 = sepe_frame("attack", torso=SEPE_TORSO_ATTACK, lean=-1)
    spear_h(a1, OX + 20, OY + 12, 22)
    a1.paint_ascii(["sSs", "sSs"], SEPE_LEGEND, OX + 17, OY + 12)
    a2 = sepe_frame("attack", torso=SEPE_TORSO_ATTACK, lean=1)
    spear_h(a2, FW - 1, OY + 12, 24)
    a2.paint_ascii(["sSs", "sSs"], SEPE_LEGEND, OX + 19, OY + 12)
    a3 = sepe_frame("attack", torso=SEPE_TORSO_ATTACK, lean=0)
    spear_h(a3, OX + 24, OY + 12, 22)
    a3.paint_ascii(["sSs", "sSs"], SEPE_LEGEND, OX + 18, OY + 12)
    frames["attack"] = [a1, a2, a3]
    return frames


# ------------------------------------------------------------- Soldado ----
SOLD_LEGEND = {
    "k": P["black"], "K": P["grey"], "y": P["gold"], "Y": P["gold_l"],
    "b": P["brown_hair"], "s": P["skin"], "S": P["skin_l"], "d": P["skin_d"],
    "e": P["outline"], "B": P["blue"], "L": P["blue_l"], "D": P["blue_d"],
    "w": P["white"], "W": P["white_s"], "p": P["wood"], "P": P["wood_l"],
    "t": P["steel"], "T": P["steel_d"],
}

SOLD_TORSO = """
...kkkkkkkk.......
..kkkkkkkkkkk.....
.kkkkKyYkkkkkkk...
...bbssSSSsb......
...bsSSeSSe.......
...bsSSSSSs.......
....sssdds........
.....ddd..........
...DBBwwBBD.......
..BBBLwwBBBB......
.BBBLBwBwBBBBs....
.BBLBBBwBBBBBBs...
.BLBBBBBwBBBBBBsSs
.BBBBBBBBwBBB..sSs
.DBBBBBBBBwBB.....
.DBBBBBBBBBBB.....
..wwwwwwwwww......
"""
SOLD_TORSO_HURT = SOLD_TORSO.replace("bsSSeSSe", "bsSSdSSd")


def musket(c, x_tip, y, length):
    """Mosquete com baioneta apontando para a direita."""
    for i in range(length):
        x = x_tip - i
        if i < 4:
            col = P["steel"]           # baioneta
        elif i < length * 0.55:
            col = P["steel_d"]         # cano
        else:
            col = P["wood_l"] if i % 3 == 0 else P["wood"]  # coronha
        c.set(x, y, col)
    # coronha mais grossa atrás
    c.hline(x_tip - length + 1, x_tip - int(length * 0.6), y + 1, P["wood_d"])
    c.set(x_tip - int(length * 0.55), y - 1, P["gold"])


def soldier_frame(pose, phase=0, bob=0, torso=SOLD_TORSO, lean=0, musket_len=18, musket_dx=0):
    c = Canvas(FW, FH)
    hip_y = OY + 18 + bob
    c.rect(OX + 1 + lean, hip_y - 1, 11, 3, P["white"])
    table = LEG[pose]
    if pose == "run":
        back, front = table[(phase + 3) % 6], table[phase % 6]
    elif pose == "idle":
        back, front = table[phase % 2], table[(phase + 1) % 2]
    else:
        front, back = table
    leg(c, (OX + 3 + lean, hip_y), back, 4, 4, P["white_s"], P["white_d"], P["black"], boot=P["grey"])
    leg(c, (OX + 8 + lean, hip_y), front, 4, 4, P["white"], P["white_s"], P["black"], boot=P["black"])
    musket(c, min(FW - 1, OX + 16 + musket_len - 8 + musket_dx + lean), OY + 13 + bob, musket_len)
    c.paint_ascii(torso, SOLD_LEGEND, OX + lean, OY + bob)
    return c


def soldier_frames():
    frames = {}
    frames["idle"] = [soldier_frame("idle", 0), soldier_frame("idle", 1, bob=1)]
    frames["walk"] = [soldier_frame("run", i, bob=RUN_BOB[i]) for i in range(6)]
    frames["alert"] = [soldier_frame("idle", 0, lean=-1, musket_dx=-2)]
    frames["lunge"] = [soldier_frame("attack", lean=2, musket_len=24, musket_dx=4),
                       soldier_frame("attack", lean=1, musket_len=22, musket_dx=2)]
    frames["hurt"] = [soldier_frame("hurt", bob=1, torso=SOLD_TORSO_HURT, lean=-1)]
    return frames


def finish(frames: dict):
    """Contorno automático em todos os frames; devolve lista ordenada + índice."""
    order, flat = [], []
    for name, fr in frames.items():
        start = len(flat)
        for f in fr:
            flat.append(f.outline(P["outline"]))
        order.append((name, start, len(fr)))
    return flat, order


def write_index(path, fw, fh, order):
    with open(path, "w") as f:
        f.write(f"frame_size={fw}x{fh}\n")
        for name, start, n in order:
            f.write(f"{name}={start},{n}\n")


def main(preview_dir=None):
    os.makedirs(OUT, exist_ok=True)
    for who, fn in (("sepe", sepe_frames), ("soldado", soldier_frames)):
        flat, order = finish(fn())
        sheet(flat).save(os.path.join(OUT, f"{who}.png"))
        write_index(os.path.join(OUT, f"{who}.txt"), FW, FH, order)
        if preview_dir:
            preview(flat, 4, os.path.join(preview_dir, f"prev_{who}.png"))
        print(who, [(n, s, k) for n, s, k in order])


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else None)
