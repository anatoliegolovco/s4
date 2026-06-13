# Schematic tiles — segmentation map

High-resolution segments of the Sintez-2 mainboard schematic, kept so the
visual extraction is reproducible and reviewable without re-rendering.

- **Source:** `reference/schematics/sintez2-schematic.pdf` (page is 2040×1560 pt).
- **Render:** PyMuPDF at **350 DPI** with overlapping clip rectangles.
- **Naming:** `t_r{row}c{col}.png` — a 3-row × 4-col grid (rows top→bottom,
  cols left→right). Overlap avoids cutting components at seams.

## Grid → page rectangle (PDF points) and dominant content

| Tile | clip rect (x0,y0,x1,y1) | Dominant content |
| --- | --- | --- |
| `t_r1c1` | 15,25,560,500 | Z1 14 MHz; sync counters D2/D19; D8 ТМ2; D1 ЛН1 |
| `t_r1c2` | 520,25,1060,500 | address mux D23; RAM addr latch D38; sheet title |
| `t_r1c3` | 1020,25,1545,500 | pixel chain D39/D40/D61; color D45/D46; RGB ladder |
| `t_r1c4` | 1480,25,2035,500 | connectors X7 "TV", X8.1/X8.2 bus; RGB transistors |
| `t_r2c1` | 15,470,560,930 | vertical counters D3/D4; sync gates; D31 ИЕ10 |
| `t_r2c2` | 520,470,1060,930 | **DRAM D28–D35**; address muxes D24/D25 |
| `t_r2c3` | 1020,470,1545,930 | video latches D42/D43/D48; attr mux D47; D50 |
| `t_r2c4` | 1480,470,2035,930 | connectors X8 cont.; D50 buffer; sync transistors |
| `t_r3c1` | 15,895,560,1305 | **CPU D6 (Z80)**; WAIT D20; keyboard mux КП11 |
| `t_r3c2` | 520,895,1060,1305 | **ROM D36**; addr mux D26; decode gates |
| `t_r3c3` | 1020,895,1545,1305 | tape X5 "M"; УС-1 (VT1 КТ315); modules УС-2..5 |
| `t_r3c4` | 1480,895,2035,1305 | D51 latch; X9 power; **"Питание микросхем"** table |

Extra full-context renders:
- `_full_overview.png` — whole sheet at 150 DPI.
- `_right_connectors_top.png` / `_right_connectors_bot.png` — the right-edge
  connector + power tables at 300 DPI.

## Reproduce

```python
import fitz
d = fitz.open("reference/schematics/sintez2-schematic.pdf"); p = d[0]
m = fitz.Matrix(350/72, 350/72)
p.get_pixmap(matrix=m, clip=fitz.Rect(15, 895, 560, 1305)).save("t_r3c1.png")  # CPU
```

Extraction results live in `../bom.json` (parts) and `../wiring.json` (nets).
