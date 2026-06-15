# bridge — KiCad ↔ SimulIDE converter

See `docs/spec/sintez2-recon-spec.md` §7 and milestone T3.

- `net2sim.py` — KiCad netlist (`kicad/sintez2.net`, from SKiDL) → SimulIDE
  circuit (`sim/circuits/*.sim1`), canonical direction.
- `sim2net.py` — optional reverse.

Mapping is driven by `../parts_map.json`.

## SimulIDE `.sim1` format (1.1.0-SR2, learned from `examples/Logic/*.sim1`)

```xml
<circuit version="" rev="2221" stepSize="1000000" stepsPS="1000000" ...>
  <item itemtype="Subcircuit" CircId="74XX90-3" Pos="x,y" label="7490"
        Input_High_V="2.5 V" Out_High_V="5 V" Out_Low_V="0 V" Out_Imped="40 Ω"
        Tpd_ps="10000 ps" Tr_ps="3000 ps" Tf_ps="4000 ps" .../>     <!-- IC -->
  <item itemtype="Clock" CircId="Clock-2" Freq="2 Hz" Voltage="5 V" .../>
  <item itemtype="Node"  CircId="Node-112" Pos="x,y" />              <!-- fan-out -->
  <item itemtype="Connector" uid="connector-113"
        startpinid="Clock-2-outnod" endpinid="74XX90-3-CP0" pointList="x,y,..." />
</circuit>
```
- Each component = one `<item>`; pins referenced as `"<CircId>-<pinname>"`.
- Each net with N endpoints → one `Node` + N `Connector`s (star), or chained connectors.
- **Per-part logic-family timing** (`Tpd_ps`, `Out_High_V`, `Out_Imped`, input
  thresholds/impedance) is set on each Subcircuit — this is where the К555 (LS) vs
  К1533 (ALS) distinction lives (spec §3). net2sim sets these from `parts_map.json`.

## Part mapping (Soviet → SimulIDE library item)

SimulIDE ships everything needed (data dir): a **Z80** model (`z80.xml` — use it,
NOT "ULA ZX48k"), the full 74xx series (`data/ic74.xml`), RAM/ROM/EEPROM, CD4000
(`icCD.xml`), and a USSR lib (`ussr.xml`).

| Sintez (ref) | KiCad/SKiDL part | SimulIDE item |
| --- | --- | --- |
| D6 Z80 | Z84C00 | `Z80` |
| D36 ROM 27128 | 27128 | `Memory`/`EEPROM` (16Kx8, load ROM bin) |
| D28-D35 К565РУ5 | K565RU5 | `RAM` (initial); behavioral РУ5 w/ RAS-CAS = T5 custom |
| ИЕ7 (D2/3/4/19) | K1533IE7 | `74HC193` |
| КП11 (D5) | K1533KP11 | `74HC257` |
| КП12 (D23-26) | K1533KP12 | `74XX253` |
| ИР22 (D43/44/48/51) | K1533IR22 | `74HC373` |
| ИР23 (D42) | K1533IR23 | `74HC374` |
| ИР27 (D38) | KR1533IR27 | `74XX273` |
| АП3 (D50) | K1533AP3 | `74XX244` |
| ИР16 (D39-41/45) | K555IR16 | 4-bit shift (`74XX166`-class), KEEP LS timing |
| ЛН1/ЛА3/ЛА4/ЛИ1/ЛЕ1 | K1533LN1/LA3/LA4/LI1/LE1 | `74XX04/00/10/08/02` |
| СА3 (D49) | K544SA3 | comparator (analog) |

## Validation goal (why the bridge exists)

Load the generated `.sim1` in SimulIDE, run, and validate the nodes the
trace-verify workflow could NOT resolve visually (see
`docs/references/validation-trace-verify-2026-06-14.md`): ROM /CE-/OE gating,
the arbitration screen-address select, RAS-before-CAS, beep/port-0xFE — and the
overall "boots to the © prompt" bar (spec T7). Contention tests must NOT pass.

## Status

- **net2sim.py — v0 WORKING.** Parses `kicad/sintez2.net`, maps parts (Z80 by a
  fixed pin table; 74xx via SimulIDE `.package` number→id; R/C/crystal), and emits
  a well-formed `sim/circuits/sintez2.sim1` with one Node + Connectors per net.
  Current run: 36 components → 27 items, 25 nets, 100 connectors.
  ```bash
  .venv/bin/python bridge/net2sim.py
  ```
  Coverage caveats it prints: DRAM (D28–D35) + ROM (D36) skipped (SimulIDE Memory
  built-ins, pin-map = T5/next); D5 follows the netlist (still КП12 in SKiDL —
  set to КП11 when the arbitration block is finished); КП12→74HC153 (non-tristate),
  ИР16→74XX166 (8- vs 4-bit), ЛА4→74HC00 (no 3-in NAND in lib) are approximations.
- **Next:** (a) add ROM/DRAM as SimulIDE Memory items with real pin maps;
  (b) give Connectors real routing geometry + load-test in the SimulIDE GUI;
  (c) set per-part family timing (Tpd/Out_V from parts_map) on each Subcircuit.

(`sim/circuits/*.sim1` is a generated build artifact — gitignored; regenerate.)
