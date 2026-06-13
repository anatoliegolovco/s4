# Q: What primary-source materials do we have, and where are they kept?

- **Topic:** sourcing ([index](./README.md))
- **Status:** resolved
- **Opened:** 2026-06-13T11:23:03Z
- **Resolved:** 2026-06-13T11:32:15Z
- **Decision:** —

## Context

The owner supplied original Sintez-2 reference materials (schematics, board
photos, a memory-expansion writeup, a video-output pinout) and asked that they
all be saved in the repository.

## Discussion

### 2026-06-13T11:23:03Z — user

Provided `sintez2_sch.pdf` (mainboard schematic) and then `Sintez_II_orig.pdf`,
a betadisk photo, `Sintez128.jpg`, and a video pinout PNG. Instruction: save all
PDFs, the betadisk image, and the next PDF too.

### 2026-06-13T11:32:15Z — claude

Saved all five assets under `reference/` (committed, so they survive the
ephemeral container — overriding the earlier "don't commit large sources"
default). Catalogued with provenance hashes in
`docs/references/sources-catalog.md`. Rendered the PDFs with PyMuPDF (poppler
was not installable) and extracted key facts:

- Mainboard schematic = "ПРОЦЕССОР «СИНТЕЗ-2», ПРИЛОЖЕНИЕ 2"; BOM table on the
  right edge (to be transcribed in T1).
- Beta Disk board → **КР1818ВГ93 ≈ WD1793 FDC** confirmed (added to
  `parts_map.json`).
- 128 KB expansion → port `#7FFD` paging (feeds the bank-switching question).
- SCART/Jack video mod → 200 Ω sync resistor note (RGB stage detail).

## Outcome

All materials are in `reference/` and catalogued; `schematics/NOTES.md` (T1) and
`parts_map.json` updated with confirmed parts. See
[`docs/references/sources-catalog.md`](../../references/sources-catalog.md).
