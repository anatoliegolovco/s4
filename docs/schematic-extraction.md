# Schematic extraction pipeline

How the paper Sintez-2 schematic becomes machine-readable design data, and the
text format we capture **before** anything goes into KiCad or SimulIDE.

## Pipeline

```
reference/schematics/sintez2-schematic.pdf   (scanned sheet, 2040×1560 pt)
        │  PyMuPDF render @350 dpi, overlapping grid
        ▼
schematics/tiles/t_r{row}c{col}.png          (kept; reviewable segments)
        │  visual transcription (designators, types, connectors, nets)
        ▼
schematics/bom.json      ← parts: ref → type → western equiv → block
schematics/wiring.json   ← nets: buses, connectors, power, block relations
        │  (incremental, per-block, with confidence flags)
        ▼
parts_map.json  +  bridge/net2sim.py  →  KiCad (.kicad_sch) / SimulIDE (.sim)
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

- **Tiles:** full board segmented (3×4 grid) and committed.
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
