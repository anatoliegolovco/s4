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

For each block: source schematic, parts (Soviet → modern per `parts_map.json`),
and any scan discrepancy and how it was resolved.

- [ ] **CPU & clock** — Z80 @ 3.5 MHz; 14 MHz pixel clock (async). *(locate on
      schematic sheet; transcribe surrounding glue.)*
- [ ] **Address decode / memory map** — ROM 0x0000–0x3FFF, screen 0x4000+.
- [ ] **DRAM + refresh** — К565РУ5, RAS-before-CAS, ИЕ7 refresh counter, WAIT gen.
- [ ] **Video bus arbitration** — КП12 (≈74ALS253 dual 4:1 mux) — the "crown jewel".
- [ ] **Sync generation** — К1533ИЕ7 (≈74ALS193 up/down counter) H/V sync.
- [ ] **Pixel chain** — К555ИР16 (D39/D40/D41) @ 14 MHz, keep LS timing.
- [ ] **RGB output stage** — КТ315Г/КТ361Г (VT13–VT18), trimmers R41–R60.
      Note SCART mod: **200 Ω sync resistor** (100 Ω → color loss).
- [ ] **Audio** — BEEP via port 0xFE, T-state timestamped.
- [ ] **Tape** — К5545АЗ (≈ LM567) tone decoder.
- [x] **TR-DOS / Beta Disk** — **КР1818ВГ93 ≈ WD1793 FDC** confirmed from the
      board photo; separate TR-DOS ROM + К555/КР1533 glue; board `СМП59-96Г-16-2`
      (1989). Separate daughterboard, not on the mainboard sheet.
- [ ] **(Optional) 128 KB expansion** — port `#7FFD` paging; mod chips
      К555ТМ9 / К1533КП11 / К555ЛЛ1 / К1533ЛА3 (`reference/photos/sintez128.jpg`).
      Tracked as an opt-in variant — see
      `docs/ledger/architecture/bank-switching-ram-size.md`.

## BOM (component table) — TODO

The mainboard schematic's right-edge table is the canonical component list.
Transcribe it into `parts_map.json` (Soviet ref → modern equivalent → timing).
High-res render is reproducible (see `docs/references/sources-catalog.md`).

## Known scan errors to reconcile

- [ ] Some connector pinouts in public scans relate to the mainboard rather
      than the wired connectors → cross-check MCbx re-mastered pinouts.
- [ ] Cross-check the in-repo scan against the colorized redraw
      (`sintez2-original.pdf`); log any net that disagrees here with resolution.
