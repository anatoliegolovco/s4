# Primary-source materials catalog

Authoritative reference assets supplied by the project owner. The binaries live
under [`reference/`](../../reference/) at the repo root (committed so they
survive the ephemeral container); this catalog records what each one is, its
provenance hash, and what we learned from it.

> Language note: source documents are in Russian; all extracted notes here are
> in English per `docs/RULES.md`.

## Inventory

| File | Type | What it is | SHA-256 (short) |
| --- | --- | --- | --- |
| `reference/schematics/sintez2-schematic.pdf` | PDF, 1 sheet (2040×1560 pt) | **"ПРОЦЕССОР «СИНТЕЗ-2» — СХЕМА ЭЛЕКТРИЧЕСКАЯ ПРИНЦИПИАЛЬНАЯ, ПРИЛОЖЕНИЕ 2."** Clean scan of the full mainboard schematic with a component table down the right edge (the BOM). | `1d8cf4f1…` |
| `reference/schematics/sintez2-original.pdf` | PDF, 1 sheet (A4) | Re-drawn / colorized version of the same mainboard schematic (KiCad-style nets). Useful cross-check against the scan. | `b37f7be2…` |
| `reference/photos/betadisk-original.png` | PNG 1200×1600 | Photo of the **original Beta Disk interface board** (TR-DOS controller), board marking `СМП59-96Г-16-2 8903`. | `a7975b58…` |
| `reference/photos/sintez128.jpg` | JPEG 560×920 | **"Расширение памяти Синтеза-2 до 128 кб"** — ©1997 PREDATOR/FAST Group writeup of the 128 KB RAM expansion mod, including its schematic. | `d2e74c1b…` |
| `reference/pinouts/video-pinout.png` | PNG 921×2048 | Screenshot (pvsm.ru) of a **SCART / Jack video output modification** with connector pinouts (RGB + sync + cassette). | `849fa38f…` |
| `reference/board/sintez2-element-placement.jpg` | JPEG (from 5144×3183 scan) | **"ПРИЛОЖЕНИЕ 2", page 25 — element-placement / silkscreen layout** of the mainboard. Locates every Dxx package physically; the single artifact that resolved the open designators D37/D44/D49/D50/D51. From the Muravyev Google-Drive set. | `99947620…` |
| `reference/schematics/sintez2-power-supply.jpg` | JPEG (from 5100×2989 scan) | **PSU schematic** — linear: toroidal transformer + LM7805, K50-24 main smoothing cap, K50-35 post-regulator. | `770eb3e2…` |
| `reference/schematics/sintez2-keyboard.jpg` | JPEG (from 5021×2879 scan) | **Keyboard schematic** — 8×5 = 40-key matrix (5-layer membrane); two Sinclair-joystick ports duplicating keypad 1–5 / 6–0. | `7ffcda00…` |
| `reference/manual/sintez2-user-manual.pdf` | PDF, 11 pages | **Full factory user manual** (signal characteristics, TV-mod instructions, keyboard schematic, PSU schematic, acceptance certificate dated March 1992). | `34e68014…` |

| `reference/schematics/betadisk-controller-bdi.pdf` | PDF, 2 pp (raster) | **"КОНТРОЛЛЕР ДИСКОВОДА «Ленинград 2»"** — the Beta-Disk / TR-DOS controller schematic (WD1793-class FDC + ИР16/ИЕ10/ТМ9 glue, system connector, board layout). Fills the TR-DOS block that previously had only a board photo. From the zx-pk t-29397 mods thread. | `48e7a4c4…` |
| `reference/schematics/sintez2-128k-ay-mod.pdf` | PDF, 7 pp (raster) | **128 KB RAM + AY sound-processor expansion** schematics (Odessa boards, Leningrad-2 origin). Feeds the optional banking + audio paths. | `bce3afa7…` |
| `reference/schematics/sintez2-mainboard-photo.jpg` | JPEG (from 4032×3024) | Photographed copy of the Sintez-2 mainboard schematic — independent cross-check of the canonical scan. | `6b68875e…` |

> Full-resolution originals of the rows above (incl. the 8283×6956
> `Schematic_Full.png`, the raw manual PNGs, and the author's EasyEDA keyboard
> redesign) are kept locally under `schematics/sources/sintez2-drive-2022/`
> (gitignored per repo policy — large reference downloads are not versioned).
> The ROM, captured as an audio tape signal `roms/sintez2-rom.wav`, and the
> Sintez-**M** ROM dump `roms/sintez-M.rom` (José Leandro, 2007), also live
> under the gitignored `roms/`.

## Key facts extracted

### Mainboard schematic (`sintez2-schematic.pdf`)
- Confirms the discrete-TTL design (К555 / К1533 families), matching the spec.
- Right-edge component table is the canonical BOM — to be transcribed in full
  during milestone T1 (high-resolution renders are reproducible via PyMuPDF;
  see `schematics/NOTES.md`).

### Beta Disk / TR-DOS controller (`betadisk-original.png`)
- FDC is **КР1818ВГ93 ≈ WD1793** (Western FDC), per the spec's TR-DOS section.
- Carries a ROM (TR-DOS) + К555 / КР1533 glue logic and bank-switch control.
- Board ident: `СМП59-96Г-16-2`, date code `8903` (1989, week 03) — consistent
  with the ~1989 manufacture date.

### 128 KB expansion (`sintez128.jpg`)
- Adds **port `#7FFD` paging** (ZX-128-style) to expand the stock 48 K to 128 K.
- Mod chips: **К555ТМ9** (≈74LS175 quad D latch — the paging register),
  **К1533КП11** (≈74ALS257 mux), **К555ЛЛ1** (≈74LS32 OR),
  **К1533ЛА3** (≈74ALS00 NAND).
- Documents screen selection and full system-port blocking behavior.
- Feeds the open question
  [`architecture/bank-switching-ram-size`](../ledger/architecture/bank-switching-ram-size.md).

### Video output / SCART mod (`video-pinout.png`)
- RGB + sync wiring to SCART and a 3.5 mm jack; cassette connector pinout.
- Note: a **200 Ω resistor on the sync channel**; dropping it to **100 Ω causes
  loss of color** — an analog-level detail relevant to the RGB stage (spec §2.3).

### Element-placement layout + power table (`sintez2-element-placement.jpg` + schematic)
- **Physically locates all 51 ICs.** Resolved the previously-open designators:
  - **D37** — small DIP, left-centre near D9/C16 (a 14-pin gate).
  - **D44** — wide DIP, top-centre by connector X4 + R31/R32 (tape/IO area), 20-pin.
  - **D49** — wide DIP, bottom-left near D17, 20-pin.
  - **D50** — wide DIP, top-right by X6/X9, 20-pin (the disk/IO address buffer).
  - **D51** — wide DIP, top-left by X1/X2, 20-pin.
- The **"Питание микросхем" (chip-power) table** down the schematic's right edge
  gives the package size of every IC by its power pins (authoritative inventory):

  | Power (+5 V / GND) | Pins | Designators |
  | --- | --- | --- |
  | 11 / 29 | 40 | D6 (Z80) |
  | 8 / 16 | 16 | D28…D35 (DRAM К565РУ5) |
  | 1,27,28 / 14 | 28 | D36 (ROM 27128) |
  | 20 / 10 | 20 | D38, D42…D44, D48, D50, D51 (octal latch/buffer) |
  | 16 / 8 | 16 | D2…D5, D11, D19, D23…D26, D46, D47 (counters/muxes) |
  | 14 / 7 | 14 | D1, D7…D10, D12…D18, D20…D22, D27, D37, D39…D41, D45 (gates) |

  > ⚠ **Discrepancy to reconcile:** the table places the pixel/colour shift
  > registers **D39–D41 and D45 in the 14-pin group**, but the spec/earlier
  > reads call them К555ИР16 (a 16-pin part). Re-check the ИР16 symbol vs. a
  > 14-pin shift register before freezing the BOM. Pin-count is from the scan;
  > the type letter must come from the schematic symbol.

### Connector pinouts (schematic right-edge tables)
- **X7 "TV":** FV=13, HS=16, VS=7, Y=11, CSYNC=5, +5 V=1; B=3, R=5, G=4,
  SYNC=2, SOUND=1 (pins 6,7 = GND). Matches the video-output stage (spec §2.3).
- **X8.1 / X8.2 (expansion bus):** full Z80 bus on the card edge — A0–A15 plus
  CLK, RESET, WAIT, INT, NMI, M1, MREQ, IORQ, RFSH, RD, WR. This is the
  **SNP58-64** connector the manual/video call out ("all CPU pins + power").

### Video transcript corroboration (`transcripts/sintez2-repair-short-*.txt`)
- **CPU = КР1858ВМ1**, fitted in place of a Z80A ("higher speed", per the
  manual page read on camera). Crystal **14.3 MHz ÷ 4 ≈ 3.575 MHz** CPU clock —
  note this is master ÷4, refining the spec's "14 MHz = 2× CPU" wording.
- **ROM is a UV-erasable EPROM** (window sealed on camera) → confirms the
  27128-class D36.
- **PSU:** linear, toroidal transformer + LM7805; a factory **39 Ω resistor**
  to ground biases the output to ~5.35 V (intentional). Caps K50-24 / K50-35.
- **RGB trimmers = SP3-38A**; **piezo buzzer = ЗП-3** (support parts present on
  board even when the buzzer itself was omitted at the factory).
- Keyboard: **5-layer membrane, 8×5 = 40 keys**; two Sinclair joystick ports
  (1–5 and 6–0), **no Kempston** (would need a register chip). Built **03/1992**.

### KiCad-source search (owner request — outcome)
- The colorized redraw `sintez2-original.pdf` was produced by **Eeschema (KiCad)
  on 2012-11-09** (PostScript title `Sintez_II_orig.ps`) — so a KiCad redraw
  exists, but its **`.sch` source is not published anywhere reachable**: not on
  GitHub, not on habr, not in the zx-pk t-240/27280 threads, not in José
  Leandro's trastero set (that's Sintez-M, a JPEG). We only have the exported
  PDF (already vector, re-renderable at any DPI — `pdftocairo -svg/-r 600`).
- **Useful adjacent KiCad assets found** (for authoring our own T2 schematic):
  `github.com/alvaroalea/8bits_kicad_libraries` (К155/К555/К1533 + Spectrum
  symbols) and `github.com/krzys9876/ZX_Spectrum_diy` (full DIY Spectrum in
  KiCad). Per the spec, **KiCad is our source of truth**, so we author the
  canonical `.kicad_sch` fresh rather than inherit the 2012 file.

## Online sources (web)

Not committed binaries — links discovered/used during research. External content;
treat as secondary to the committed primary sources above.

| Link | Type | Notes |
| --- | --- | --- |
| https://youtu.be/0_mFe5sdLsc | Video (YouTube) | **Dmitry Muravyev**, "Импортозамещение" (2022-07-30) — Sintez-2 revival, supplied by the project owner. Auto-caption transcript saved at `docs/references/transcripts/sintez2-repair-short-{ru,en}.txt`. |
| https://youtu.be/hP12QHBkZDM | Video (YouTube) | Muravyev's **full 36-min restoration** of the same unit (no captions available; visual board close-ups only). |
| https://drive.google.com/drive/folders/1PBfw-9AaOMJzl4I1Lhckx7aKGpiDoIub | Google Drive | **Muravyev's reference set** linked in the video description: full schematic scan, board element-placement, PSU + keyboard schematics, 11-page user manual, ROM-as-audio, and his EasyEDA keyboard redesign. Mirrored into the repo (see inventory above). |
| https://trastero.speccy.org/cosas/JL/Sintez-M/sintez-m.html | Page | **José Leandro Novellan** (2007): Sintez-**M** (predecessor) schematic JPEG + a 16 KB `sintez-M.rom` dump. The M shares the logic design; not the same board. |
| https://zx-pk.ru/threads/29397-dorabotki-klona-sintez-2.html | Forum | **"Доработки клона SINTEZ 2"** (user *jil2*, 2018) — owner of a Sintez-2 with Odessa 128K + AY + Beta-Disk(PLL) mods originally for Leningrad-2; discusses INT-signal fix and port #FF. Found via Yandex during the forum dig. |
| https://cloud.mail.ru/public/MwCe/wVycd7nSd | File host | **SCHEMES.zip** (24 MB) linked from thread 29397: BDI, 128K+AY, Leningrad-2 PLL schematics (photos + raster PDFs). Mirrored into the repo. **No KiCad source here — all raster.** |
| https://habr.com/ru/articles/222569/ | Article | "Синтез-2 — отечественный клон ZX-Spectrum"; source of the 1920×1278 board photo (`reference/photos/sintez2-board-habr.jpg`) and rear-panel shot. |
| https://zx-pk.ru/threads/27280-remont-sintez-2.html | Forum | "Ремонт Синтез 2"; text corroborates D39–D42 / КР1533КП12 / ИР16; 27128 ROM → W27C512 flash. |
| https://zx-pk.ru/archive/index.php/t-240.html | Forum | Sintez-2 schematic/repair; 128K mod lifts 3 pins of the КП12 A14/A15 mux. |
| https://priborazbor.ru/sintez-2-sintez-evm-kompyuter-igrovoj/ | Page | Scrap/teardown; rough IC count (~18 DRAM + 17 155/1533 + Z80 + 17 КТ315) and a 696px top-view board photo. |

> Reachability note (this environment): image CDNs (habrastorage, wp.com,
> zx-pk attachments) are fetchable; **web.archive.org and archive.ph are blocked**
> by the egress policy. No higher-res board photo than 1920px exists online.

## Reproducing the renders

PDFs render with PyMuPDF (no poppler needed):

```python
import fitz
d = fitz.open("reference/schematics/sintez2-schematic.pdf")
pix = d[0].get_pixmap(matrix=fitz.Matrix(400/72, 400/72),
                      clip=fitz.Rect(1470, 40, 2040, 1300))  # right-edge BOM
pix.save("bom.png")
```
