# Color schematic (redraw) — tiles & extraction

The colorized **vector** redraw `reference/schematics/sintez2-original.pdf`
(842×595 pt, A4 landscape) is far cleaner than the photographic scan and, decisively,
**names its nets and prints exact part numbers**. It is the *primary* source for
the netlist; the scan (`../tiles/`) is the cross-check.

## Color semantics (decoded from per-color layer separations)

| Stroke RGB | Meaning |
| --- | --- |
| `(0.63,0,0)` dark red | **component symbols + pins** (IC bodies, R/C, transistors, connectors) |
| `(0,0,1)` blue | **text labels** — net names, bus names, designators, pin names |
| `(0,0.63,0.63)` cyan, `(0,0.63,0)` green, `(0,0,0.75)` dk-blue, `(1,0,0)` red, black | **wires/nets**, color-grouped for routing legibility |

The text is vector outlines (not selectable — `get_text()` returns 0 chars), so
labels are still read visually, but at this clarity transcription is reliable.

## Files

- `c_r{row}c{col}.png` — 4×3 overlapping grid @400 dpi (same scheme as `../tiles/`).
- `_overview.png` — whole sheet @200 dpi.
- `_grid_overview.png` — overview with a 50-pt magenta coordinate grid (use it to
  pick clip rectangles for tight high-zoom crops).
- `layers/layer_<color>.png` — each stroke color rendered in isolation. `layer_darkred`
  = the parts layer; `layer_blue` = the net-name layer; the rest are wire groups.
  **These are the net-tracing aid**: follow one wire color to see a net group alone.
- `zoom/zoom_*.png` — high-zoom crops where exact part numbers / pinouts were read
  (color stage, DRAM, RGB output + connectors, X8 bus pinout).

## Reproduce a tight crop

```python
import fitz
p = fitz.open("reference/schematics/sintez2-original.pdf")[0]
p.get_pixmap(matrix=fitz.Matrix(1000/72, 1000/72),
             clip=fitz.Rect(615, 278, 725, 340)).save("zoom_x8.png")  # X8 bus pinout
```

## What this pass corrected vs the scan

- **Logic family is К1533** (≈74ALS/F), not К555, for the glue/counters/muxes.
  Registers/shift-registers are **К555ИР16/ИР22/ИР23** (LS) and DRAM is **К565РУ5**.
- **D41** (not "D61") is the third pixel shift register — matches the spec text.
- **D13 = К1533ЛИ1** generates **/RAS** and **/CAS** (with R15 470 + C5).
- **D14 = К1533ЛЕ1** (NOR) — original scan read was right.
- CPU is labeled **Z80A** (D6); D28–D35 block is labeled **DRAM**.
- Net names harvested: see `../wiring.json`.
