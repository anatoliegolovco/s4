# kicad/skidl — canonical schematic authored in SKiDL (text → KiCad netlist)

Per decision [0005](../../docs/decisions/0005-skidl-text-schematic.md), the
Sintez-2 schematic (spec milestone T2) is authored as **Python/SKiDL**, which
emits a **KiCad netlist** that feeds Pcbnew for layout (T8, decision 0002) and
`bridge/net2sim.py` for SimulIDE. SKiDL is the text-only surface the LLM drives
zero-click (decision 0003); no graphical `.kicad_sch` is hand-drawn.

## Files
- `sintez_parts.py` — the Sintez part library: each IC defined with its real pin
  list (number/name/type) from `docs/datasheets/` + `schematics/bom.json` (v0.3).
  No KiCad symbol library needed; footprints reference KiCad's standard `Package_DIP:*`.
- `sintez2.py` — the top-level design, built block by block. Generates
  `kicad/sintez2.net` and runs ERC.

## Run
```bash
.venv/bin/python kicad/skidl/sintez2.py
```
(`.venv` has `skidl`; create with `python3 -m venv .venv && .venv/bin/pip install skidl`.)
The generated `*.net` is a build artifact (gitignored) — regenerate from the Python.

## Status — block by block (spec §8)
- [x] **Block 1 — CPU + clock + reset** (D6 Z80, Z1 14 MHz osc + D1 К1533ЛН1,
      reset RC C2/R10, control-input pull-ups R4–R7). Netlist generates, **0 ERC
      errors** (warnings are unconnected bus pins — expected until the blocks
      below are wired).
- [x] **Block 2a — ROM (D36 27128)** wired to the A0–A13 / D0–D7 buses + power
      (VPP/PGM=VCC). Verified: A0=D6.30+D36.10 … D0=D6.14+D36.11; A14 CPU-only
      (27128 is 16K). /CE,/OE are named decode nets pending the decode sub-block.
- [x] **Block 2b — ROM decode** (D22 ЛЕ1, D9 ЛН1, D17 ЛА3): ~ROMCS =
      NAND(A14 NOR A15, ¬/MREQ); ROM /OE = /RD. Logic verified in the netlist,
      0 ERC errors. ⚠ Functional: exact gate-section/pin mapping to verify vs the
      scan. Screen / I/O (port 0xFE) selects + D10/D27/D37/D26 still to add.
- [x] **Block 3 — DRAM array (D28–D35 К565РУ5)** — 8×1-bit = 64 KB, sharing VA0–VA7
      (address-pin map from wiring.json), /RAS, /CAS, /WE; per-bit DIN←Dn, DOUT→DDn.
      /RAS,/CAS from D13 ЛИ1; /WE=/WR. Verified, 0 ERC errors. ⚠ Timing strobes into
      D13 + refresh come from the arbitration/sync blocks (4/5); РУ5 timing model = T5.
- [ ] Block 4 — bus arbitration (D5/D23–D26 КП12, D38 ИР27 latch).
- [ ] Block 5 — video sync (D2/D3/D4/D19 ИЕ7, D8/D21 ТМ2) + /4 CPU-clock divider.
- [ ] Block 6 — pixel chain (D39/D40/D41 ИР16) + colour (D42–D48) + RGB out.
- [ ] Block 7 — tape/audio (D49 К544СА3, beep) + disk I/O (D44/D50/D51) + connectors.

Each block draws its pin-level nets from `schematics/wiring.json` (filled in as
blocks are traced).

## KiCad version
For PCB layout + headless ERC you need **KiCad 9** (kicad-cli 7 has no `sch erc`):
```bash
sudo add-apt-repository -y ppa:kicad/kicad-9.0-releases
sudo apt update && sudo apt install -y kicad
```
The SKiDL netlist generation here does **not** need KiCad installed.
