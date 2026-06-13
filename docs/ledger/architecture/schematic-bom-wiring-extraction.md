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

### 2026-06-13T13:18:41Z — user

Asked whether the **color schematic** (the redraw whose netlist uses color
codes) was captured too — it needs its own tiling + extraction.

### 2026-06-13T13:40:00Z — claude

It had not been tiled. The redraw `sintez2-original.pdf` is a **vector** file:
text is outlined (not selectable) but strokes are color-coded — **dark-red =
parts/pins, blue = net-name labels, other colors = wire groups**. Tiled it (4×3
@400 dpi) into `schematics/tiles-color/`, rendered **per-color layer
separations** (`layers/`) as a net-tracing aid, and high-zoom crops (`zoom/`).
The redraw prints exact part numbers and names nets, so it is now the **primary**
source; the scan is the cross-check. Bumped BOM/wiring to **v0.2** with
corrections: family **К1533** (registers К555ИР16/22/23, DRAM К565РУ5, CPU
Z80A); **D41** (not "D61") is the 3rd shift register; **D13 = ЛИ1** makes
/RAS+/CAS; **D14 = ЛЕ1**; **D45 = ИР16**, **D46/D47 = КП12**; **X8** 64-pin bus
pinout high-confidence; **УС-1…5 = YC-1…5** analog driver modules.

### 2026-06-13T13:50:38Z — user

Asked to web-search Russian forums for the still-missing details.

### 2026-06-13T14:05:00Z — claude

Searched zx-pk.ru / Habr / Pikabu. **No per-designator BOM or netlist is
published anywhere** — our schematic (originally from **ZX-Club #7** magazine)
is the authoritative source; forums only confirm top-level specs. Concrete gains
recorded to `bom.json` → `external_corroboration`:

- Specs match: Z80A @3.5 MHz, 48 KB base / 128 KB upgrade, 16 KB ROM (BASIC),
  board **СМП59**, the 200-Ω sync resistor.
- zx-pk t-240: the **128K upgrade lifts 3 pins of the КП12 mux that carry
  A14/A15** and feeds A14'/A15' from paging logic — **corroborates D26 КП12 as
  the A14/A15 paging mux**, and the "2nd-storey РУ5 row + CAS split" method.
- **D36 ROM** is a 28-pin 16Kx8 EPROM (27128-class; Soviet К573РФ6/РФ8 or
  imported 27128) — exact marka to confirm from a board photo.
- Further docs: `Sintez-128.zip`, ZX-Club #7, zx-pk thread t-240.

The unresolved low-confidence parts (D37/D44/D49/D50/D51, ИЕ10) are **not
obtainable from forums** — they must come from high-zoom reads of the color
tiles and (ideally) a clear board photo. Logged as such.

### 2026-06-13T14:20:00Z — claude

Owner has no physical Sintez and asked to try the Internet Archive for the 404s.
**web.archive.org and archive.ph are unreachable from this environment** (egress
policy: `curl`→"Blocked by egress policy", WebFetch→"unable to fetch"); the
`archive.org/wayback/available` API responds but has no snapshot for those URLs,
and the surviving forum mirrors are dead (one hijacked to a casino, one 503).

Pivoted to the **color tiles** (no board/internet needed) with targeted high-zoom
crops, which resolved most remaining gaps to high confidence:
- **D5 = К1533КП12** — generates video-fetch address K8–K12 from the V-counters.
- **D11 = К561ИЕ10 (CD4520)** — CMOS dual counter; resolves the "ИЕ10" question.
- **D26 = К1533КП12** — A/K address mux; **D36 = 27128** (labeled literally).
- **D48 = К1533ИР22** — border register (D0–D4 → BB/RB/GB).
- Captured the К565РУ5 address-pin → VADDR map (`wiring.json` `dram_addr_map`).

Still open (not online, no board): **D37, D44, D49, D50, D51** (disk/keyboard area).

## Outcome

<!-- in progress -->
BOM **v0.3** and wiring **v0.3** captured (both source documents tiled & extracted).
Remaining: trace pin-level nets per block (cpu → decode → dram → arbitration, per
T2/T3) using the color layers, complete the X8 lower-row pins and the IC power
table. Each completed block gets `status: done` and is fed to `bridge/net2sim.py`.
