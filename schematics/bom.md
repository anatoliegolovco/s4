# Sintez-2 mainboard — Bill of Materials

Corrected BOM extracted from the original schematic (scan + colorized redraw) and
the factory element-placement + power tables. Supersedes the generic
"best-guess" list — every line below is read from a primary source.

- **Machine-readable source of truth:** [`bom.json`](./bom.json) (per-designator)
  and [`wiring.json`](./wiring.json) (nets/connectors).
- **Logic family:** К1533 (≈74ALS/F) for glue/counters/muxes; К555 for the
  ИР16/ИР22/ИР23 registers (keep LS timing); DRAM К565РУ5.
- **Confidence:** ✅ confirmed from a printed label/table · 🟡 located + pin-count
  known, exact type to confirm · ⚠ open conflict.

## Processor & clock

| Ref | Part | ≈ Western | Function | Conf. |
| --- | --- | --- | --- | --- |
| D6 | КР1858ВМ1 (Z80) | Z80A | CPU; 14.3 MHz ÷4 ≈ 3.575 MHz (habr unit uses a Zilog Z8400) | ✅ |
| Z1 | 14.3 MHz crystal | — | master/pixel clock (÷4 → CPU) | ✅ |
| D1 | К1533ЛН1 | 74LS04 | hex inverter — clock/glue | ✅ |
| D20 | К1533ТМ2 | 74LS74 | dual D-FF — WAIT generation | ✅ |
| D12 | К1533ТМ2 | 74LS74 | FLASH / glue | ✅ |

## Memory

| Ref | Part | ≈ Western | Function | Conf. |
| --- | --- | --- | --- | --- |
| D28–D35 | 8× К565РУ5 | 4164 (64Kx1) | DRAM array (1 bit/chip) → 48 KB usable | ✅ |
| D36 | 27128 (UV-EPROM) | 27128 (16Kx8) | stock BASIC ROM, A0–A13; replaceable by W27C512 | ✅ |
| D38 | К1533ИР23 | 74LS374 | RAM address latch | ✅ |
| D13 | К1533ЛИ1 | 74LS08 | generates /RAS and /CAS (R15 470 + C5) | ✅ |

## Address arbitration (the "crown jewel")

CPU address (A*) vs video-fetch address (K*) multiplexed onto VADDR for the DRAM.

| Ref | Part | ≈ Western | Function | Conf. |
| --- | --- | --- | --- | --- |
| D5 | К1533КП12 | 74ALS253 | video-fetch address K8–K12 from V-counters | ✅ |
| D23/D24/D25/D26 | К1533КП12 | 74ALS253 | A*/K* → VADDR muxes (D26 = A14/A15 paging tap) | ✅ |
| D38 | К1533ИР23 | 74LS374 | row/col address latch | ✅ |

## Video — sync, pixel chain, colour

| Ref | Part | ≈ Western | Function | Conf. |
| --- | --- | --- | --- | --- |
| D2/D19 | К1533ИЕ7 | 74xx193 | horizontal counters (СТ2) | ✅ |
| D3/D4 | К1533ИЕ7 | 74xx193 | vertical counters V0–V7 | ✅ |
| D11 | К561ИЕ10 | CD4520 | CMOS dual counter — video timing | ✅ |
| D8/D21 | К1533ТМ2 | 74LS74 | sync flip-flops | ✅ |
| D10 | К1533ЛА4 | 74LS10 | 3-in NAND — sync decode | ✅ |
| D14 | К1533ЛЕ1 | 74LS02 | NOR — glue | ✅ |
| D17 | К1533ЛА3 | 74ALS00 | NAND — glue | ✅ |
| D18 | К1533ЛП5 | 74LS86 | XOR — FLASH/attribute | ✅ |
| D39/D40/D41 | К555ИР16 | 74LS165 | pixel shift registers @14 MHz | ⚠ |
| D42 | К1533ИР23 | 74LS374 | pixel/attribute data latch | ✅ |
| D43 | К1533ИР22 | 74LS373 | video-data latch (VD0–VD7 → D0–D7) | ✅ |
| D45 | К555ИР16 | 74LS165 | colour register BM/RM/GM/YM → BR/RR/GR/YR | ⚠ |
| D46/D47 | К1533КП12 | 74ALS253 | colour/attribute muxes | ✅ |
| D48 | К1533ИР22 | 74LS373 | border register → BB/RB/GB | ✅ |

> ⚠ **ir16_pincount_conflict** — the "Питание микросхем" table puts D39–D41/D45
> in the **14-pin** group, but the redraw labels them К555ИР16 (**16-pin**).
> Settle by counting pins on `reference/board/sintez2-element-placement.jpg`
> before freezing footprints.

## RGB output stage (analog)

| Ref | Part | Function |
| --- | --- | --- |
| VT3–VT18 | КТ315Г / КТ361Г | RGB driver transistors (emitter followers) |
| УС-1…УС-5 (YC-1…5) | КТ315 + R | five identical analog line-driver modules |
| RGB ladder | R41 620 / R42 1.8k / R47 270 / R48 620 / R49 1k / R54 620 / R55 1.8k / R60 820 + VD3–VD8 | per-colour level network; **SP3-38A** trimmers |
| sync | R66 470 / R67 820 / R68 820 / VD17; **200 Ω** on sync (critical) | /CSYNC, //SYNC |

## I/O, tape, disk

| Ref | Part | ≈ Western | Function | Conf. |
| --- | --- | --- | --- | --- |
| D37 | gate (14-pin) | 74LS-gate | glue near D9/C16 | 🟡 |
| D44 | octal latch/buffer (20-pin) | 74LS373/374/245 | tape/IO near X4 + R31/R32 | 🟡 |
| D49 | octal latch/buffer (20-pin) | 74LS373/374/245 | IO near D17 | 🟡 |
| D50 | octal buffer (20-pin) | 74LS244/245 | disk/IO address buffer (AA8–AA14), by X6/X9 | 🟡 |
| D51 | octal latch (20-pin) | 74LS373/374 | disk data latch, by X1/X2 | 🟡 |
| tape | К5545АЗ ≈ LM567 + R30/R31 3k, R32 5.1k, C6/C7 | tone decode (port #FE) | ✅ |

## Connectors

| Ref | Role | Key pins |
| --- | --- | --- |
| X7 "TV" | RGB/SCART + sound | FV13, HS16, VS7, Y11, CSYNC5, +5V1; B3, R5, G4, SYNC2, SOUND1; GND6,7 |
| X8 "SNP58-64" | expansion card-edge (full Z80 bus) | A2=/IORQ, A3=/MREQ, A4=/HALT, A5=/NMI, A6=/INT, A7=D1, A8=D0; B2=/WR, B4=/BUSAK, B5=/WAIT, B6=/BUSRQ, B7=/RESET, B8=/M1; B1=/BJ |
| X5 "M" | tape | OUT1, GND2, IN3 |
| X9 "РБ" | power | +5V 2,6; GND 1,5 |

## Power

| Item | Part | Notes |
| --- | --- | --- |
| Rail | +5 V single | factory 39 Ω bias to GND → ~5.35 V (intentional) |
| Regulator | LM7805 | linear, toroidal transformer |
| Smoothing | K50-24 / K50-35 | main + post-regulator |
| Decoupling | C12…C36 = 25× 0.15 µF | board-wide; CH 200 pF on sync |

## Package inventory (authoritative — "Питание микросхем")

| +5V / GND | Pins | Designators |
| --- | --- | --- |
| 11 / 29 | 40 | D6 |
| 8 / 16 | 16 | D28–D35 |
| 1,27,28 / 14 | 28 | D36 |
| 20 / 10 | 20 | D38, D42, D43, D44, D48, D50, D51 |
| 16 / 8 | 16 | D2, D3, D4, D5, D11, D19, D23, D24, D25, D26, D46, D47 |
| 14 / 7 | 14 | D1, D7, D8, D9, D10, D12–D18, D20, D21, D22, D27, D37, D39, D40, D41, D45 |
