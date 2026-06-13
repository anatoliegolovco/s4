# schematics/NOTES.md — block inventory & scan-error reconciliation

> **Status: STUB (task T1, not yet done).** This file is the deliverable for
> milestone **T1** in the spec (`docs/spec/sintez2-recon-spec.md` §8). It must
> list every functional block with the source used and any discrepancy
> resolved, reconciled against the re-mastered MCbx pinouts and zx-pk.ru repair
> threads. Sources are tracked under `schematics/sources/` (not committed if
> large).

## Sources consulted

| Source | URL | Used for | Notes |
| --- | --- | --- | --- |
| MCbx (corrected pinouts) | https://oldcomputer.info/8bit/sintez/index.htm | TBD | best English deep-dive |
| speccy.info (RU) | https://speccy.info/Sintez | TBD | most detailed RU wiki |
| Sintez-M schematics | https://trastero.speccy.org/cosas/JL/Sintez-M/sintez-m.html | TBD | predecessor, shared logic |
| zx-pk.ru | https://zx-pk.ru | TBD | repair threads, corrected schematics |

## Block inventory

For each block: source schematic, parts (Soviet → modern per `parts_map.json`),
and any scan discrepancy and how it was resolved.

- [ ] **CPU & clock** — Z80 @ 3.5 MHz; 14 MHz pixel clock (async).
- [ ] **Address decode / memory map** — ROM 0x0000–0x3FFF, screen 0x4000+.
- [ ] **DRAM + refresh** — К565РУ5, RAS-before-CAS, ИЕ7 refresh counter, WAIT gen.
- [ ] **Video bus arbitration** — КП12 muxes (the "crown jewel").
- [ ] **Sync generation** — К1533ИЕ7 H/V sync counters.
- [ ] **Pixel chain** — К555ИР16 (D39/D40/D41) @ 14 MHz, keep LS timing.
- [ ] **RGB output stage** — КТ315Г/КТ361Г (VT13–VT18), trimmers R41–R60.
- [ ] **Audio** — BEEP via port 0xFE, T-state timestamped.
- [ ] **Tape** — К5545АЗ (≈ LM567) tone decoder.
- [ ] **TR-DOS / Beta Disk** — WD1793 FDC, separate ROM + bank switching.

## Known scan errors to reconcile

- [ ] Some connector pinouts in public scans relate to the mainboard rather
      than the wired connectors → cross-check MCbx re-mastered pinouts.
- [ ] Add each discrepancy here as it is found, with resolution + source.
