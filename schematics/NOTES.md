# schematics/NOTES.md — block inventory & scan-error reconciliation

> **Status: IN PROGRESS (milestone T1).** Deliverable for T1 in the spec
> (`docs/spec/sintez2-recon-spec.md` §8): list every functional block with the
> source used and any discrepancy resolved. Primary sources are now in the repo
> (`reference/`, catalogued in `docs/references/sources-catalog.md`).

## Sources in hand

| Source | Location | Used for | Notes |
| --- | --- | --- | --- |
| Sintez-2 mainboard schematic (scan) | `reference/schematics/sintez2-schematic.pdf` | mainboard nets + BOM | "ПРИЛОЖЕНИЕ 2", clean scan, BOM table on right edge |
| Sintez-2 mainboard schematic (redraw) | `reference/schematics/sintez2-original.pdf` | cross-check | colorized re-draw of the same sheet |
| Beta Disk board photo | `reference/photos/betadisk-original.png` | TR-DOS controller | КР1818ВГ93 (WD1793) confirmed |
| 128 KB expansion writeup | `reference/photos/sintez128.jpg` | banking mod | port #7FFD paging |
| SCART/Jack video mod | `reference/pinouts/video-pinout.png` | RGB output stage | 200 Ω sync resistor note |
| MCbx (corrected pinouts) | https://oldcomputer.info/8bit/sintez/index.htm | TBD | online cross-check |
| speccy.info (RU) | https://speccy.info/Sintez | TBD | online cross-check |
| zx-pk.ru | https://zx-pk.ru | TBD | repair threads |

## Block inventory

Designators below were transcribed from the segmented tiles
(`schematics/tiles/`). Full structured data is in `schematics/bom.json`
(parts) and `schematics/wiring.json` (nets). `[x]` = block identified;
pin-level nets are tracked in `wiring.json`'s per-block `status`.

- [x] **CPU & clock** — **D6 = Z80** (power pins 11/29 confirm DIP-40); Z1
      14 MHz pixel clock; clock R3 820, reset C2 10µF + R10 5.1k, pull-ups
      R4/R5 5.1k; WAIT gen D20/D12 ТМ2. (tile r3c1)
- [x] **Address decode** — D26 КП12 mux (A9/A13/A14/A15); D22 ЛЕ1, D32 ЛА4
      decode gates; ROM CS net TODO. (tiles r3c2)
- [x] **DRAM + refresh** — **D28–D35 = К565РУ5** ×8 (power pins 8/16); address
      muxes D24/D25 → VA; refresh address from ИЕ7 counters; WAIT to slow РУ5.
      (tile r2c2)
- [x] **Video bus arbitration ("crown jewel")** — D23/D24/D25/D26 КП12
      (≈74ALS253) + D38 ИР23 latch → VADDR + RAS/CAS. (tiles r1c2, r2c2)
- [x] **Sync generation** — D2/D19 (H), D3/D4 (V) = ИЕ7 (СТ2 counters); D8/D21
      ТМ2; D10 ЛА4; D14 ЛЕ1; D18 ЛП5 (FLASH). (tiles r1c1, r2c1)
- [x] **Pixel chain** — **D39/D40/D61 = К555ИР16** (74LS165) @ 14 MHz; **keep
      LS timing**. (Note: spec text said D41; the board labels D61.) (tile r1c3)
- [x] **RGB output stage** — VT3–VT18 (КТ315Г/КТ361Г) + ladder R41 620/R42
      1.8k/R47 270/R48 620/R49 1k/R54 620/R55 1.8k/R60 820 + VD3–VD8; УС-1
      emitter follower (VT1). SCART mod: **200 Ω sync** (100 Ω → color loss).
      Color stage D42/D43/D45/D46/D47/D48. (tiles r1c3, r2c3, r3c3)
- [x] **Audio/tape** — port 0xFE (BEEP/border/tape); X5 "M" connector
      (OUT/GND/IN); R30/R31 3k, R32 5.1k; К5545АЗ≈LM567 tone decode (net TODO).
      (tile r3c3)
- [x] **TR-DOS / Beta Disk** — **КР1818ВГ93 ≈ WD1793** confirmed from board
      photo; on-board buffers D50/D51 (ИР22) + disk-address diodes; FDC is a
      separate daughterboard, not on the mainboard sheet. Board `СМП59-96Г-16-2`.
- [ ] **(Optional) 128 KB expansion** — port `#7FFD` paging; mod chips
      К555ТМ9 / К1533КП11 / К555ЛЛ1 / К1533ЛА3 (`reference/photos/sintez128.jpg`).
      Opt-in variant — see `docs/ledger/architecture/bank-switching-ram-size.md`.

## Two source documents

- **Scan** `reference/schematics/sintez2-schematic.pdf` — authoritative original;
  carries the connector + power tables. Tiled in `schematics/tiles/`.
- **Colorized vector redraw** `reference/schematics/sintez2-original.pdf` — cleaner,
  **names nets and prints exact part numbers**. Tiled in `schematics/tiles-color/`
  (+ `layers/` per-color separations, + `zoom/` high-zoom crops). **Primary**
  net-naming source; the scan is the cross-check. Color code: dark-red=parts,
  blue=net labels, other colors=wire groups.

## Redraw cross-check corrections (v0.2)

- Logic family is **К1533** (≈74ALS/F); registers **К555ИР16/ИР22/ИР23** (keep LS);
  DRAM **К565РУ5**; CPU labeled **Z80A**.
- **D41** (not "D61") is the 3rd pixel shift register (К555ИР16) — matches spec.
- **D13 = К1533ЛИ1** generates **/RAS** and **/CAS** (R15 470 + C5).
- **D14 = К1533ЛЕ1** (NOR). **D45 = К555ИР16** color register; **D46/D47 = К1533КП12**.
- **X8** is a 64-pin expansion bus, pinout now high-confidence (`tiles-color/zoom/zoom_x8.png`).
- **УС-1…УС-5 = YC-1…YC-5**: five identical single-transistor analog driver modules.

## BOM & wiring — structured outputs

- `schematics/bom.json` — every identified package (ref → Soviet type → western
  equivalent → block), with `confidence` flags and a `gaps_to_resolve` list.
- `schematics/wiring.json` — buses, control signals, connector pinouts, power
  pins, and block-to-bus relations; pin-level intra-block nets are the next pass.
- Pipeline & status: `docs/schematic-extraction.md`.

## Known scan errors to reconcile

- [ ] Some connector pinouts in public scans relate to the mainboard rather
      than the wired connectors → cross-check MCbx re-mastered pinouts.
- [ ] Cross-check the in-repo scan against the colorized redraw
      (`sintez2-original.pdf`); log any net that disagrees here with resolution.
