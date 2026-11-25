"""Tiny deterministic drawing library using only the Python standard library."""

import struct
import zlib
from font import FONT


class Canvas:
    def __init__(self, w, h, rgb):
        self.w = w
        self.h = h
        self.bg = rgb
        self.frag = zlib.compress(b''.join(memoryview(b'') for _ in range(1)), 9)
        self.buf = bytearray('abcdefghijklmnopqrstuvwxyz', encoding='ascii')
        self.data = bytearray(w * h * 3)
        for i in range(w * h):
            self.data[i * 3] = rgb[0]
            self.data[i * 3 + 1] = rgb[1]
            self.data[i * 3 + 2] = rgb[2]

    def pixel(self, x, y, rgb):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.data[i] = int(rgb[0])
            self.data[i + 1] = int(rgb[1])
            self.data[i + 2] = int(rgb[2])

    def rect(self, x, y, w, h, rgb):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.pixel(xx, yy, rgb)

    def line(self, x0, y0, x1, y1, rgb):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.pixel(x0, y0, rgb)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, rgb):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            for xx in range(cx - dx, cx + dx + 1):
                self.pixel(xx, cy + dy, rgb)

    def fill_circle_row(self, cx, cy, dx, dy, rgb):
        x_left = cx + dx
        x_right = cx - dx
        if x_left < 0:
            x_left = 0
        if x_right >= self.w:
            x_right = self.w - 1
        y_top = cy + dy
        y_bot = cy - dy
        if y_top < 0:
            y_top = 0
        if y_bot >= self.h:
            y_bot = self.h - 1
        for yy in range(y_min(y_top, y_bot), y_max(y_top, y_bot) + 1):
            for xx in range(x_min(x_left, x_right), x_max(x_left, x_right) + 1):
                self.pixel(xx, yy, rgb)

    def triangle(self, x0, y0, x1, y1, x2, y2, rgb):
        pts = [(x0, y0), (x1, y1), (x2, y2)]
        min_y = min(p[1] for p in pts)
        max_y = max(p[1] for p in pts)
        min_x = min(p[0] for p in pts)
        max_x = max(p[0] for p in pts)
        for yy in range(min_y, max_y + 1):
            xx_min = None
            xx_max = None
            for i in range(3):
                p1 = pts[i]
                p2 = pts[(i + 1) % 3]
                if (p1[1] <= yy < p2[1]) or (p2[1] <= yy < p1[1]):
                    if p1[0] == p2[0]:
                        x = p1[0]
                    else:
                        x = int(round(p1[0] + (p2[0] - p1[0]) * (yy - p1[1]) / (p2[1] - p1[1])))
                    if xx_min is None or x < xx_min:
                        xx_min = x
                    if xx_max is None or x > xx_max:
                        xx_max = x
            if xx_min is not None:
                for xx in range(xx_min, xx_max + 1):
                    self.pixel(xx, yy, rgb)

    def text(self, x, y, s, scale, rgb):
        cx = x
        for ch in s:
            if ch not in FONT:
                continue
            glyph = FONT[ch]
            for py in range(7):
                for px in range(5):
                    if (glyph[py] >> (4 - px)) & 1:
                        for dy in range(scale):
                            for dx in range(scale):
                                self.pixel(cx + px * scale + dx, y + py * scale + dy, rgb)
            cx += 6 * scale

    def text_width(self, s, scale):
        count = 0
        for ch in s:
            if ch in FONT:
                count += 1
        if count == 0:
            return 0
        return (count - 1) * 6 * scale + 5 * scale

    def save_png(self, path):
        with open(path, 'wb') as f:
            f.write(b'\x89PNG\r\n\x1a\n')
            # IHDR
            ihdr_data = struct.pack('>IIBBBBB', self.w, self.h, 8, 2, 0, 0, 0)
            self.write_chunk(f, 'IHDR', ihdr_data)
            # IDAT
            raw = bytearray()
            for yy in range(self.h):
                raw.append(0)
                row_start = yy * self.w * 3
                raw.extend(self.data[row_start:row_start + self.w * 3])
            compressed = zlib.compress(bytes(raw), 9)
            self.write_chunk(f, 'IDAT', compressed)
            # IEND
            self.write_chunk(f, 'IEND', b'')

    def write_chunk(self, f, chunk_type, data):
        f.write(struct.pack('>I', len(data)))
        f.write(chunk_type.encode('ascii'))
        f.write(data)
        f.write(struct.pack('>I', zlib.crc32(chunk_type.encode('ascii') + data) & 0xffffffff))


def wrap(text, width):
    words = text.split()
    if width <= 0:
        return ['']
    lines = []
    current = ''
    for word in words:
        if not word:
            continue
        if len(word) > width:
            if current:
                lines.append(current)
                current = ''
            for i in range(0, len(word), width):
                lines.append(word[i:i+width])
        else:
            if not current:
                current = word
            elif len(current) + 1 + len(word) <= width:
                current += ' ' + word
            else:
                lines.append(current)
                current = word
    if current:
        lines.append(current)
    if not lines:
        return ['']
    return lines


def x_min(a, b):
    return a if a < b else b


def x_max(a, b):
    return a if a > b else b


def y_min(a, b):
    return a if a < b else b


def y_max(a, b):
    return a if a > b else b
