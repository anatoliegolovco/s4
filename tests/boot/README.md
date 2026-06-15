# tests/boot — headless boot validation (spec T7: "boots to the © prompt")

Runs the ZX-Spectrum-48K-compatible ROM (`roms/sintez-M.rom`) on a vendored Z80
core, using the Sintez-2 memory map our SKiDL/KiCad decode implements
(ROM 0x0000–0x3FFF read-only, RAM 0x4000–0xFFFF), and checks the machine boots.

This validates, **fully headless** (no SimulIDE GUI), the "functional" decode the
trace-verify workflow could not confirm visually: does the intended memory map
actually boot a real ROM? (It does not validate gate-level timing — RAS/CAS — which
needs the SimulIDE gate model.)

## Run
```bash
cc -O2 -o tests/boot/boot tests/boot/boot.c tests/boot/z80.c
tests/boot/boot                 # uses roms/sintez-M.rom
```

## Result (2026-06-15) — PASS ✅
- **P-RAMT (5CB4) = FFFF** — RAM-size probe found the top of 64 KB (RAM map works).
- **CHARS (5C36) = 3C00** — font base set; ROM init completed.
- **768 attributes + screen pixels set** — display initialised; the **© sign-on
  message** is rendered at screen rows 184–191 (confirmed by ASCII render).
- Conclusion: the ROM(0–3FFF)/RAM(4000+) map boots a ZX-compatible ROM to the
  © prompt — the T7 bar is met for the functional memory map.

`boot.c` is the harness; `z80.c`/`z80.h` are the **superzazu/z80** core
(github.com/superzazu/z80, MIT licence — third-party, retains its own licence;
passes ZEXALL). The ROM lives in the gitignored `roms/`.
