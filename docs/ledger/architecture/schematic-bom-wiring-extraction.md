# Q: What are the mainboard's BOM and wiring, extracted from the schematic?

- **Topic:** architecture ([index](./README.md))
- **Status:** open (in progress — block-by-block)
- **Opened:** 2026-06-13T11:50:07Z
- **Resolved:** —
- **Decision:** —

## Context

The owner supplied the original mainboard schematic and asked whether we have a
complete BOM yet, then directed: segment the sheet, **keep the segments**, and
document the **wiring in JSON** before importing anything into software.

## Discussion

### 2026-06-13T11:50:07Z — user

Asked if the BOM is complete from the schematics, or if segmentation/extraction
is still needed. Chose: **full BOM, tile by tile.**

### 2026-06-13T11:58:49Z — user

Added: keep the segments, and document the wiring in a JSON format before
putting it all into software.

### 2026-06-13T12:05:00Z — claude

The schematic has **no single BOM table** — only connector pinout tables
(X7/X8/X9…) and a "Питание микросхем" power-pin table; component types are
annotated next to each symbol. Segmented the sheet into a 3×4 grid at 350 DPI,
**kept the tiles** in `schematics/tiles/` (committed), and transcribed:

- **BOM** → `schematics/bom.json` (~40 packages, `confidence` per entry):
  CPU **D6 = Z80** (power pins 11/29 confirm it), **D28–D35 = К565РУ5 DRAM**,
  **D36 = 16 KB ROM**, pixel chain **D39/D40/D61 = ИР16 (74LS165)**, address
  arbitration **D23–D26 = КП12 (74ALS253) + D38 ИР23**, sync counters
  **D2/D3/D4/D19 = ИЕ7**, plus glue (ЛН1/ЛА3/ЛА4/ЛИ1/ЛЕ1/ЛП5/ТМ2) and modules
  УС-1…УС-5.
- **Wiring** → `schematics/wiring.json`: buses (ADDR/DATA/VADDR/VCOUNT…),
  control signals, connector pinouts, power pins, block-to-bus relations.
  Pin-accurate intra-block nets flagged as the next pass.
- Pipeline documented in `docs/schematic-extraction.md`.

## Outcome

<!-- in progress -->
BOM v0.1 and wiring v0.1 captured as the canonical text intermediate. Remaining:
trace pin-level nets per block (cpu → decode → dram → arbitration, per T2/T3),
resolve low-confidence connector pins against the redraw, and finish the IC
power table. Each completed block gets `status: done` and is fed to
`bridge/net2sim.py`.
