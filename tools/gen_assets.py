#!/usr/bin/env python3
"""Gera TODOS os assets visuais do jogo (sprites, tiles, fundos, fonte, UI, ícone).

Uso: python3 tools/gen_assets.py [pasta_de_previas]
Os .wav vêm de tools/compose.py (separado, porque demora ~1 min).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import gen_backgrounds
import gen_font
import gen_sprites
import gen_tiles
from palette import P
from pixelart import Canvas

ROOT = os.path.join(os.path.dirname(__file__), "..")


def icon():
    """Ícone 128x128: lua sobre as coxilhas ao entardecer, com a lança de Sepé."""
    c = Canvas(32, 32)
    c.gradient_v(0, 31, [(0.0, P["sky0"]), (0.45, P["sky2"]), (0.7, P["sky3"]), (0.85, P["sky4"]), (1.0, P["sky5"])], n=4)
    c.circle(22, 9, 6, P["cream"])
    c.set(20, 8, P["moon_s"])
    c.set(24, 11, P["moon_s"])
    for x in range(32):
        import math
        y = int(22 + 3 * math.sin(x / 5.0) + 1.5 * math.sin(x / 2.1))
        c.vline(x, y, 31, P["hill_far2"])
        c.set(x, y, P["hill_far"])
    # lança diagonal
    c.line(6, 30, 20, 4, P["wood"], width=2, shade=P["wood_d"])
    c.line(18, 7, 21, 2, P["steel"], width=2, shade=P["steel_d"])
    c.set(18, 8, P["red_l"])
    c.set(17, 9, P["red"])
    # moldura
    c.box(0, 0, 32, 32, P["outline"])
    return c.scaled(4)


def main():
    prev = sys.argv[1] if len(sys.argv) > 1 else None
    gen_sprites.main(prev)
    gen_tiles.main(prev)
    gen_backgrounds.main(prev)
    gen_font.main(prev)
    icon().save(os.path.join(ROOT, "icon.png"))
    print("icon.png ok")


if __name__ == "__main__":
    main()
