#!/usr/bin/env python3
"""Render a ZX-Spectrum screen dump (6912 bytes: 6144 bitmap + 768 attrs) to PNG.
This is the 'monitor output' of the Sintez-2 video hardware — a connected monitor
displays exactly the screen-RAM contents (0x4000-0x5AFF). Writes a PPM then converts
to PNG with ImageMagick. Usage: scr2png.py screen.scr out.png"""
import sys, subprocess
scr = open(sys.argv[1], "rb").read()
out = sys.argv[2] if len(sys.argv) > 2 else "screen.png"
# ZX palette: (BRIGHT off, BRIGHT on); index = GRB-ish ZX order 0..7
LO, HI = 0xCD, 0xFF
def col(c, bright):
    v = HI if bright else LO
    b = v if (c & 1) else 0; r = v if (c & 2) else 0; g = v if (c & 4) else 0
    return (r, g, b)
W, H, SCALE = 256, 192, 3
img = [[(0, 0, 0)] * W for _ in range(H)]
for y in range(H):
    addr = ((y & 0xC0) << 5) | ((y & 0x07) << 8) | ((y & 0x38) << 2)
    for xb in range(32):
        byte = scr[addr + xb]
        at = scr[6144 + (y // 8) * 32 + xb]
        ink = at & 7; paper = (at >> 3) & 7; bright = (at >> 6) & 1
        ci, cp = col(ink, bright), col(paper, bright)
        for bit in range(8):
            img[y][xb * 8 + bit] = ci if (byte & (0x80 >> bit)) else cp
# write scaled PPM
with open("/tmp/s4work/scr.ppm", "wb") as f:
    f.write(f"P6\n{W*SCALE} {H*SCALE}\n255\n".encode())
    for y in range(H):
        rows = b"".join(bytes(img[y][x]) for x in range(W) for _ in range(SCALE))
        for _ in range(SCALE): f.write(rows)
subprocess.run(["convert", "/tmp/s4work/scr.ppm", out], check=True)
print("wrote", out)
