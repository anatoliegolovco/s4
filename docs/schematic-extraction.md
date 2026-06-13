# Schematic extraction pipeline

How the paper Sintez-2 schematic becomes machine-readable design data, and the
text format we capture **before** anything goes into KiCad or SimulIDE.

## Two source documents

1. **Scan** `sintez2-schematic.pdf` (2040×1560 pt raster) — the authoritative
   original; has the connector + "Питание микросхем" power tables. Tiled in
   `schematics/tiles/`.
2. **Colorized redraw** `sintez2-original.pdf` (842×595 pt **vector**) — cleaner,
   and it **names nets and prints exact part numbers**. Tiled in
   `schematics/tiles-color/` with per-color layer separations. This is the
   **primary** source for the netlist and part numbers; the scan is the cross-check.

The redraw's color code: dark-red = parts/pins, blue = net-name labels, other
colors = wire groups. Text is vector outlines (not selectable), so labels are
still read visually — but at this clarity, transcription is reliable. Rendering
one wire color in isolation (`tiles-color/layers/`) is the net-tracing aid.

## Pipeline

```
sintez2-schematic.pdf (scan)      sintez2-original.pdf (vector redraw)
   │ render @350dpi, grid             │ render @400dpi grid + per-color layers
   ▼                                  ▼
schematics/tiles/             schematics/tiles-color/  (+ layers/, zoom/)
   └──────────────┬───────────────────┘
                  ▼  visual transcription (designators, types, nets, pins)
   schematics/bom.json    ← parts: ref → type → western equiv → block
   schematics/wiring.json ← nets: buses, connectors, power, block relations
                  │  (incremental, per-block, with confidence flags)
                  ▼
   parts_map.json + bridge/net2sim.py → KiCad (.kicad_sch) / SimulIDE (.sim)
```

The two JSON files are the **canonical intermediate**. They are plain text, so
the LLM owns them (spec §6), and they are filled **one block at a time** with a
`confidence`/`status` flag on every entry — we never silently promote a guess.

## Why JSON before software

- KiCad's schematic API is text-only in 2026 (decision
  [0003](./decisions/0003-text-only-llm-control-plane.md)); authoring from a
  structured netlist is far more reliable than drawing by hand.
- The same JSON drives the KiCad→SimulIDE bridge (spec §7), so BOM and wiring
  stay in one source of truth.
- Confidence flags let us author the **high-confidence blocks first** (CPU,
  ROM, DRAM) and leave low-confidence nets clearly marked for verification
  against the colorized redraw (`sintez2-original.pdf`) and zx-pk.ru.

## Current status (2026-06-13)

- **Tiles:** both sources segmented and committed — scan (3×4 grid,
  `schematics/tiles/`) and color redraw (4×3 grid + 7 color-layer separations +
  high-zoom crops, `schematics/tiles-color/`).
- **Redraw cross-check (v0.2):** logic family confirmed **К1533** (≈74ALS/F),
  registers **К555ИР16/22/23**, DRAM **К565РУ5**, CPU **Z80A**. Corrections:
  **D41** (not "D61") is the 3rd pixel shift register; **D13 = ЛИ1** makes
  /RAS+/CAS; **D14 = ЛЕ1**. **X8** 64-pin bus pinout now high-confidence.
- **BOM:** ~40 packages identified — CPU **D6 = Z80** (confirmed via power
  table), **D28–D35 = К565РУ5 DRAM**, **D36 = 16 KB ROM**, pixel chain
  **D39/D40/D61 = ИР16 (74LS165)**, address arbitration **D23–D26 = КП12
  (74ALS253) + D38 ИР23 latch**, sync counters **D2/D3/D4/D19 = ИЕ7**. See
  `schematics/bom.json`.
- **Wiring:** buses, control signals, connectors (X5/X9 high-confidence;
  X7/X8 medium), power pins, and block-to-bus relations captured. Pin-accurate
  intra-block nets are the next pass (`schematics/wiring.json` → `todo`).

## Next

Trace nets pin-by-pin in milestone order: **cpu → decode → dram →
addr-arbitration** (T2/T3), mark each block `status: done`, then feed it to
`bridge/net2sim.py` for a SimulIDE smoke test. See `schematics/NOTES.md`.
