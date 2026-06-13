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

## Online sources (web)

Not committed binaries — links discovered/used during research. External content;
treat as secondary to the committed primary sources above.

| Link | Type | Notes |
| --- | --- | --- |
| https://youtu.be/0_mFe5sdLsc | Video (YouTube) | Sintez-2 ZX-Spectrum clone — supplied by the project owner as a reference. |
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
