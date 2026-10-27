#!/usr/bin/env python3
"""pixelart.py — mini biblioteca de pixel art em Python puro (zero dependências).

Canvas RGBA guardado em bytearray, primitivas básicas (retângulo, linha,
círculo, elipse), dithering ordenado (Bayer), contorno automático e gravação
de PNG via zlib/struct. Usada pelos geradores em tools/gen_*.py.
"""
from __future__ import annotations

import math
import random
import struct
import zlib

TRANSPARENT = (0, 0, 0, 0)

BAYER4 = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
_B2 = [[0, 2], [3, 1]]
BAYER8 = [[4 * BAYER4[y % 4][x % 4] + _B2[y // 4][x // 4] for x in range(8)] for y in range(8)]


def rgba(h: str, a: int = 255) -> tuple:
    """'#rrggbb' -> (r, g, b, a)."""
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def mix(c1: tuple, c2: tuple, t: float) -> tuple:
    return tuple(int(round(c1[i] + (c2[i] - c1[i]) * t)) for i in range(4))


def darken(c: tuple, f: float) -> tuple:
    return (int(c[0] * f), int(c[1] * f), int(c[2] * f), c[3])


def bayer(x: int, y: int, n: int = 8) -> float:
    """Limiar ordenado em [0,1) para a posição (x,y)."""
    if n == 4:
        return (BAYER4[y % 4][x % 4] + 0.5) / 16.0
    return (BAYER8[y % 8][x % 8] + 0.5) / 64.0


class Canvas:
    __slots__ = ("w", "h", "buf")

    def __init__(self, w: int, h: int, fill: tuple | None = None):
        self.w, self.h = w, h
        self.buf = bytearray(w * h * 4)
        if fill is not None:
            self.rect(0, 0, w, h, fill)

    # --- acesso a pixels -------------------------------------------------
    def set(self, x: int, y: int, c: tuple | None) -> None:
        if c is None or x < 0 or y < 0 or x >= self.w or y >= self.h:
            return
        i = (y * self.w + x) * 4
        self.buf[i] = c[0]
        self.buf[i + 1] = c[1]
        self.buf[i + 2] = c[2]
        self.buf[i + 3] = c[3]

    def get(self, x: int, y: int) -> tuple:
        if x < 0 or y < 0 or x >= self.w or y >= self.h:
            return TRANSPARENT
        i = (y * self.w + x) * 4
        return (self.buf[i], self.buf[i + 1], self.buf[i + 2], self.buf[i + 3])

    def opaque(self, x: int, y: int) -> bool:
        if x < 0 or y < 0 or x >= self.w or y >= self.h:
            return False
        return self.buf[(y * self.w + x) * 4 + 3] > 0

    # --- primitivas --------------------------------------------------------
    def rect(self, x: int, y: int, w: int, h: int, c: tuple) -> None:
        for yy in range(max(0, y), min(self.h, y + h)):
            for xx in range(max(0, x), min(self.w, x + w)):
                self.set(xx, yy, c)

    def box(self, x: int, y: int, w: int, h: int, c: tuple) -> None:
        self.hline(x, x + w - 1, y, c)
        self.hline(x, x + w - 1, y + h - 1, c)
        self.vline(x, y, y + h - 1, c)
        self.vline(x + w - 1, y, y + h - 1, c)

    def hline(self, x0: int, x1: int, y: int, c: tuple) -> None:
        if x0 > x1:
            x0, x1 = x1, x0
        for x in range(x0, x1 + 1):
            self.set(x, y, c)

    def vline(self, x: int, y0: int, y1: int, c: tuple) -> None:
        if y0 > y1:
            y0, y1 = y1, y0
        for y in range(y0, y1 + 1):
            self.set(x, y, c)

    def line(self, x0: int, y0: int, x1: int, y1: int, c: tuple, width: int = 1,
             shade: tuple | None = None) -> None:
        """Bresenham. width>1 engrossa na direção perpendicular dominante;
        `shade` pinta a última fatia (lado direito/inferior) com outra cor."""
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        offsets = range(-(width // 2), width - width // 2)
        for k, off in enumerate(offsets):
            col = shade if (shade is not None and k == len(offsets) - 1 and width > 1) else c
            if dx >= dy:
                self._bres(x0, y0 + off, x1, y1 + off, col)
            else:
                self._bres(x0 + off, y0, x1 + off, y1, col)

    def _bres(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx: int, cy: int, r: int, c: tuple) -> None:
        for y in range(-r, r + 1):
            for x in range(-r, r + 1):
                if x * x + y * y <= r * r + r * 0.5:
                    self.set(cx + x, cy + y, c)

    def ring(self, cx: int, cy: int, r: int, c: tuple) -> None:
        for y in range(-r, r + 1):
            for x in range(-r, r + 1):
                d = x * x + y * y
                if (r - 0.5) ** 2 <= d <= (r + 0.5) ** 2:
                    self.set(cx + x, cy + y, c)

    def ellipse(self, cx: int, cy: int, rx: int, ry: int, c: tuple) -> None:
        for y in range(-ry, ry + 1):
            for x in range(-rx, rx + 1):
                if (x * x) / (rx * rx + 0.01) + (y * y) / (ry * ry + 0.01) <= 1.0:
                    self.set(cx + x, cy + y, c)

    def blit(self, src: "Canvas", x: int, y: int, flip_h: bool = False) -> None:
        for sy in range(src.h):
            for sx in range(src.w):
                c = src.get(sx, sy)
                if c[3] == 0:
                    continue
                dx = (src.w - 1 - sx) if flip_h else sx
                self.set(x + dx, y + sy, c)

    # --- preenchimentos com dithering ------------------------------------
    def gradient_v(self, y0: int, y1: int, stops: list, x0: int = 0, x1: int | None = None,
                   n: int = 8) -> None:
        """Gradiente vertical com dithering ordenado. stops = [(t, cor), ...], t em [0,1]."""
        if x1 is None:
            x1 = self.w - 1
        span = max(1, y1 - y0)
        for y in range(y0, y1 + 1):
            t = (y - y0) / span
            a, b, u = stops[0][1], stops[0][1], 0.0
            for i in range(len(stops) - 1):
                ta, ca = stops[i]
                tb, cb = stops[i + 1]
                if ta <= t <= tb:
                    a, b = ca, cb
                    u = (t - ta) / max(1e-6, (tb - ta))
                    break
            else:
                if t > stops[-1][0]:
                    a = b = stops[-1][1]
            for x in range(x0, x1 + 1):
                self.set(x, y, b if u > bayer(x, y, n) else a)

    def dither_rect(self, x: int, y: int, w: int, h: int, c1: tuple, c2: tuple,
                    ratio: float, n: int = 8) -> None:
        """Mistura c1/c2 por dithering: ratio = proporção de c2."""
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c2 if ratio > bayer(xx, yy, n) else c1)

    def speckle(self, x: int, y: int, w: int, h: int, c: tuple, density: float,
                rng: random.Random, only_over: tuple | None = None) -> None:
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if rng.random() < density:
                    if only_over is None or self.get(xx, yy) == only_over:
                        self.set(xx, yy, c)

    # --- transformações ----------------------------------------------------
    def outline(self, color: tuple, diagonal: bool = False) -> "Canvas":
        """Devolve cópia com contorno de 1px ao redor dos pixels opacos."""
        out = self.copy()
        nb = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        if diagonal:
            nb += [(1, 1), (-1, -1), (1, -1), (-1, 1)]
        for y in range(self.h):
            for x in range(self.w):
                if self.opaque(x, y):
                    continue
                for dx, dy in nb:
                    if self.opaque(x + dx, y + dy):
                        out.set(x, y, color)
                        break
        return out

    def copy(self) -> "Canvas":
        c = Canvas(self.w, self.h)
        c.buf[:] = self.buf
        return c

    def flip_h(self) -> "Canvas":
        c = Canvas(self.w, self.h)
        c.blit(self, 0, 0, flip_h=True)
        return c

    def shifted(self, dx: int, dy: int) -> "Canvas":
        c = Canvas(self.w, self.h)
        c.blit(self, dx, dy)
        return c

    def crop(self, x: int, y: int, w: int, h: int) -> "Canvas":
        c = Canvas(w, h)
        for yy in range(h):
            for xx in range(w):
                c.set(xx, yy, self.get(x + xx, y + yy))
        return c

    def scaled(self, k: int) -> "Canvas":
        c = Canvas(self.w * k, self.h * k)
        for y in range(self.h):
            for x in range(self.w):
                px = self.get(x, y)
                if px[3] == 0:
                    continue
                c.rect(x * k, y * k, k, k, px)
        return c

    def replace(self, old: tuple, new: tuple) -> "Canvas":
        c = self.copy()
        for y in range(self.h):
            for x in range(self.w):
                if c.get(x, y) == old:
                    c.set(x, y, new)
        return c

    def tint(self, f: float) -> "Canvas":
        c = self.copy()
        for y in range(self.h):
            for x in range(self.w):
                px = c.get(x, y)
                if px[3]:
                    c.set(x, y, (min(255, int(px[0] * f)), min(255, int(px[1] * f)),
                                 min(255, int(px[2] * f)), px[3]))
        return c

    def bbox(self):
        """(x0, y0, x1, y1) dos pixels opacos, ou None."""
        xs, ys = [], []
        for y in range(self.h):
            for x in range(self.w):
                if self.opaque(x, y):
                    xs.append(x)
                    ys.append(y)
        if not xs:
            return None
        return (min(xs), min(ys), max(xs), max(ys))

    # --- ASCII art -----------------------------------------------------------
    @staticmethod
    def from_ascii(rows, legend: dict, w: int | None = None, h: int | None = None,
                   ox: int = 0, oy: int = 0) -> "Canvas":
        if isinstance(rows, str):
            rows = [r for r in rows.strip("\n").split("\n")]
        rw = max(len(r) for r in rows)
        c = Canvas(w or (rw + ox), h or (len(rows) + oy))
        c.paint_ascii(rows, legend, ox, oy)
        return c

    def paint_ascii(self, rows, legend: dict, ox: int = 0, oy: int = 0) -> None:
        if isinstance(rows, str):
            rows = [r for r in rows.strip("\n").split("\n")]
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch == "." or ch == " ":
                    continue
                col = legend.get(ch)
                if col is None:
                    raise KeyError(f"caractere sem cor na legenda: {ch!r}")
                self.set(ox + x, oy + y, col)

    # --- saída -----------------------------------------------------------------
    def save(self, path: str) -> None:
        write_png(path, self.w, self.h, self.buf)


def write_png(path: str, w: int, h: int, buf: bytes) -> None:
    raw = bytearray()
    stride = w * 4
    for y in range(h):
        raw.append(0)
        raw += buf[y * stride:(y + 1) * stride]

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


def sheet(frames: list, cols: int | None = None) -> Canvas:
    """Monta um spritesheet em grade (todos os frames do mesmo tamanho)."""
    fw, fh = frames[0].w, frames[0].h
    cols = cols or len(frames)
    rows = (len(frames) + cols - 1) // cols
    s = Canvas(fw * cols, fh * rows)
    for i, f in enumerate(frames):
        s.blit(f, (i % cols) * fw, (i // cols) * fh)
    return s


def preview(canvases: list, scale: int, path: str, gap: int = 4, bg: tuple = (40, 40, 48, 255)) -> None:
    """Monta uma prévia ampliada lado a lado (só para inspeção visual)."""
    w = sum(c.w * scale + gap for c in canvases) + gap
    h = max(c.h for c in canvases) * scale + 2 * gap
    out = Canvas(w, h, bg)
    x = gap
    for c in canvases:
        out.blit(c.scaled(scale), x, gap)
        x += c.w * scale + gap
    out.save(path)
