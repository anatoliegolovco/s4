# Datasheets & key parameters

Datasheet links and the parameters that matter for the recreation and the
simulation model. **Verified numbers are cited; values not yet confirmed from a
primary datasheet are marked _(to confirm)_** — never treat those as final.

Sourced via web research (2026-06). Drives `parts_map.json` and the timing in
the SimulIDE component models.

---

## Class 2 — DRAM (timing-critical, spec §2.4)

### К565РУ5 ≈ 4164 (64K×1 DRAM)
- **Western equiv:** 4164 / 2164 / TMS4164.
- **Datasheets:** [TMS4164 (TI)](https://www.silicon-ark.co.uk/datasheets/TMS4164-datasheet-texas-instruments.pdf) ·
  [2164A](https://www.minuszerodegrees.net/memory/4164/datasheet_2164A.pdf) ·
  [4164 overview](https://www.minuszerodegrees.net/memory/4164.htm)
- **Standard 4164 timing** (grade −15 / −20):

  | Param | −15 | −20 | Meaning |
  | --- | --- | --- | --- |
  | tRAC | 150 ns | 200 ns | access from RAS |
  | tCAC | 75 ns | 100 ns | access from CAS |
  | tRAS (min) | 150 ns | 200 ns | RAS pulse width |
  | tCAS (min) | 75 ns | 100 ns | CAS pulse width |
  | tRP | 100 ns | 120 ns | RAS precharge |
  | tRC | 260 ns | 330 ns | read/write cycle |
  | Refresh | 128 cycles / 2 ms | same | RAS-only / RBC |
  | Supply | +5 V single | same | |

- **К565РУ5 specifics:** Soviet part, single +5 V, 128-cycle / 2 ms refresh.
  The spec and zx-pk.ru repair threads state РУ5 is **slower** than imported
  4164s (which is why the WAIT generator was tuned to it, and why faster 4164s
  cause instability). Treat РУ5 as the **−20 grade or slower** baseline.
  Exact tRAC/tCAC from the original ТУ: **_(to confirm)_** — typically quoted
  ~200–230 ns access.
- **Model rule:** keep РУ5 (slow) timing; a fast-4164 profile must *change* the
  WAIT verdict (spec §2.4, decision
  [0004](../decisions/0004-fidelity-no-memory-contention.md)).

---

## Class 3 — Pixel shift register (setup/hold-critical, spec §2.3)

### К555ИР16 ≈ 74LS165 (8-bit PISO shift register, D39/D40/D41)
- **Datasheets:** [SN74LS165A (TI)](https://www.ti.com/product/SN74LS165A) ·
  [LS165 (uvigo PDF)](http://mdgomez.webs.uvigo.es/LEDG/hojas_caracteristicas/74LS165.pdf)
- **Key AC (74LS165, datasheet-typical):**

  | Param | Value | Note |
  | --- | --- | --- |
  | fmax | ≥ 25 MHz | guaranteed min; clocked at 14 MHz here → comfortable |
  | setup time tsu | ~20 ns | data → clock _(LS family; spec cites 20–25 ns)_ |
  | hold time th | ~5 ns _(to confirm)_ | |
  | tPLH/tPHL (clk→Q) | ~27 ns max _(to confirm)_ | |

- **Rule:** keep **LS** timing. ALS (≈7–10 ns setup) gives ~3× false margin
  against the 14 MHz pixel clock — that masks real-hardware behavior (spec §3).

---

## Class 1 — Logic (state-exact; free to modernize)

### К1533ИЕ7 ≈ SN74ALS193 (4-bit up/down binary counter)
- Used for **DRAM refresh address + H/V sync** counting (cascadable).
- **Datasheets:** [chipdip КР1533ИЕ7 = SN74ALS193](https://www.chipdip.ru/product/kr1533ie7) ·
  TI SN74ALS193. tpd ≈ 4 ns/gate; DIP-16.

### КП12 (КР1533КП12) ≈ SN74ALS253 (dual 4→1 mux, 3-state output)
- Used for **CPU/video bus arbitration** (the "crown jewel"). Note: it is a
  **dual 4-to-1 mux with tri-state**, not a simple 2:1 — correct the spec's
  loose "bus multiplexer" wording.
- **Datasheets:** [chipdip КР1533КП12 = SN74ALS253](https://www.chipdip.ru/product/kr1533kp12) ·
  TI SN74ALS253. tpd ≈ 4 ns/gate; DIP-16.

---

## Class 4 — RGB output transistors (analog levels, spec §2.3)

### КТ315Г (NPN) / КТ361Г (PNP), VT13–VT18
- **Datasheets:** [KT315G (alltransistors)](https://alltransistors.com/transistor.php?transistor=38654) ·
  [KT361G (alltransistors)](https://alltransistors.com/transistor.php?transistor=38806) ·
  [KT315 (Wikipedia)](https://en.wikipedia.org/wiki/KT315)

  | Param | КТ315Г (NPN) | КТ361Г (PNP) |
  | --- | --- | --- |
  | hFE (h21e) min | 50 (range ~20–350) | 50 |
  | Vce(max) | 35 V | 35 V |
  | Vbe(max) | 6 V | 4 V |
  | Ic(max) | 100 mA | 50 mA |
  | Ptot | 150 mW | 150 mW |
  | ft | 250 MHz | 250 MHz |

- **Rule:** RGB level depends on Vbe/hFE; real boards used trimmers
  (R41–R60). 2N3904/BC237 give wrong levels — keep these for the analog path.
  Cross-ref SCART mod's 200 Ω sync resistor (`reference/pinouts/video-pinout.png`).

---

## Class 5 — Tape tone decoder (do not substitute, spec §2.5)

### К5545АЗ ≈ LM567 (tone/PLL decoder)
- **Datasheet:** [LM567 (TI)](https://www.ti.com/lit/ds/symlink/lm567.pdf)
- Center freq set by external R/C; supply 4.75–9 V. Keep equivalent function.

---

## CPU (spec §4)

### Zilog Z84C00 (genuine Z80)
- **Datasheet:** [Z8400/Z84C00 (Zilog)](https://www.zilog.com/docs/z80/z8400.pdf)
- Speed grades Z84C00**06/08/10/20** = 6/8/10/20 MHz — all ≥ the 3.5 MHz target.
  Recommended default per decision
  [0001](../decisions/0001-keep-real-zilog-z80.md).

---

## Storage — TR-DOS / Beta Disk (spec §1, confirmed from board photo)

### КР1818ВГ93 ≈ WD1793 (floppy disk controller)
- Confirmed on `reference/photos/betadisk-original.png`. Separate TR-DOS ROM +
  bank switching, 5.25" floppies. Western datasheet: Western Digital WD1793.

---

## 128 KB expansion mod (optional variant, `reference/photos/sintez128.jpg`)

Not on the stock mainboard; documented for the banking variant.

| Mod ref | Western ≈ | Role |
| --- | --- | --- |
| К555ТМ9 | 74LS175 | quad D flip-flop — port #7FFD paging register |
| К1533КП11 | 74ALS257 | 2:1 mux (address paging) |
| К555ЛЛ1 | 74LS32 | OR gates |
| К1533ЛА3 | 74ALS00 | NAND gates |

---

## Sources

- DRAM: [TMS4164](https://www.silicon-ark.co.uk/datasheets/TMS4164-datasheet-texas-instruments.pdf),
  [2164A](https://www.minuszerodegrees.net/memory/4164/datasheet_2164A.pdf),
  [4164 list](https://www.minuszerodegrees.net/memory/4164.htm)
- Shift register: [SN74LS165A (TI)](https://www.ti.com/product/SN74LS165A),
  [uvigo LS165 PDF](http://mdgomez.webs.uvigo.es/LEDG/hojas_caracteristicas/74LS165.pdf)
- Counter / mux: [КР1533ИЕ7](https://www.chipdip.ru/product/kr1533ie7),
  [КР1533КП12](https://www.chipdip.ru/product/kr1533kp12)
- Transistors: [KT315G](https://alltransistors.com/transistor.php?transistor=38654),
  [KT361G](https://alltransistors.com/transistor.php?transistor=38806),
  [KT315 wiki](https://en.wikipedia.org/wiki/KT315)
- Tape: [LM567 (TI)](https://www.ti.com/lit/ds/symlink/lm567.pdf)
- CPU: [Z8400/Z84C00 (Zilog)](https://www.zilog.com/docs/z80/z8400.pdf)
