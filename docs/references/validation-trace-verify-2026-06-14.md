# Schematic trace + adversarial-verify report (2026-06-14)

Output of the `sintez2-trace-verify` workflow: 8 schematic blocks, each traced by
one agent and adversarially verified by a second (16 agents). Raw results in
`schematics/sources/trace-verify-2026-06-14/` (gitignored). This file is the
human-readable distillation — what is **confirmed**, **ambiguous**, **missing**,
and what each finding changes.

> Purpose: resolve the netlist ambiguities/uncertainties/missing components before
> the SimulIDE validation pass. Items marked ⚠ need a targeted re-trace or a
> simulation check; items marked ✅ are safe to wire into the SKiDL netlist.

## Corrections to BOM / earlier work (applied)

| Item | Was | Now (verified) | Source |
| --- | --- | --- | --- |
| **D5** | КП12 (74ALS253) | **К1533КП11** (quad 2:1, 74ALS257) | schematic label, both agents |
| **R49** | 1k | **1.8K** (reads "1,8K") | RGB-ladder render |
| **VT13–VT18** | "RGB output VT13–VT18" | RGB drivers are **VT3–VT12**; VT13 is the **beep** driver; VT14–VT18 not found | RGB region scan |
| **Net `a`** | (unknown global) | **= GND/0V** (red global label on GND triangles); `a2` is distinct | sync block |

Still to confirm (flagged, not yet applied):
- **D15 / D16**: redraw draws them as **К1533ТМ2** (dual D-FF); BOM types them ЛН1
  (74LS04). Re-trace before trusting either. ⚠
- **D9–D16 designator collision**: the disk-address diodes (КД522) near D50 appear
  labelled D9–D16, which also name logic ICs. Likely the diodes are VD-series and
  the BOM's "D9..D16 disk-address diodes" was a misread. ⚠

## Per-block status

### pixel-chain — ✅ medium, consistent
- D39/D40/D41 = К555ИР16 (4-bit/14-pin). **Chain: D41(VD0-3) → D40(VD4-7) → D39 →
  D18 XOR (FLASH)**, via Q3→SI of the next stage. D40.Q3 also taps D13.12 (FLASH AND).
- OE(8) of all three + D41.SI tie to net `a` (= GND). PE(6) to GND. Outputs Q0-Q2 NC.
- ✅ Safe to wire. ⚠ Confirm the D13.12 tap is on D40.Q3 (verifier says yes).

### color — ✅ high (after fix), was inconsistent
- **D43 was FABRICATED by the trace** (duplicated D42's pins). Real members:
  **D42 (ИР23 octal register)** VD0-7 in → B0/R0/G0/B1/R1/G1/Y color/attr out;
  **D46/D47 (КП12)** mux those → BM/RM/GM/YM; **D48 (ИР22)** border latch D0-D4 →
  BB/RB/GB; **D45 (ИР16)** colour shift register.
- A real **D43 (ИР22 video-data latch) exists in the BOM but was NOT located** in
  this crop — find it (likely just outside the window). ⚠ missing
- D48 input order as drawn is D0,D1,D2,**D4,D3** (D3/D4 swap — read clearly).
- D46/D47 OE0 ← D13D (FLASH-gated SCREEN); A1 select = BORDER; A0 select source ⚠.

### rgb-output — ✅ high, analog (ngspice T6)
- VT3–VT12 КТ315/КТ361 emitter-followers + ladder (R41 620/R42 1.8k/R47 270/
  R48 620/**R49 1.8k**/R54 620/R55 1.8k/R60 820) + VD3–VD8 (КД522). 26 nets confirmed.
- ⚠ B-channel pulldown 33k shown as "R?" (likely R43); G-channel diode "VD?" (likely VD8).
- No DIP ICs here → analog model only.

### tape-audio — ⚠ medium, needs re-trace (trace had errors, verifier corrected)
- ✅ **X5**: pin3=TAPE_IN, pin2=GND, pin1=TAPE_OUT (matches wiring.json).
- ✅ Beep push-pull: VT13 collector = {R71.2, +5V}; VT13 base = {R69.2, VT13.2, BA1.1}.
- ✅ D49 = К544СА3 comparator (tape-IN conditioning: R30/R31/C7 → R39 → comparator).
- ⚠ Passives R30/R31/R32/R33/C6/C7/C9 omitted by the trace — re-trace to place them.
- ⚠ The BEEP/port-0xFE drive net has **no visible label**; source must be found
  (decode/IO). This is a genuine ambiguity for the simulator (sound timing).

### disk-io — ✅ high, consistent on the ICs
- ✅ D44/D51 = К1533ИР22, D50 = К1533АП3 (both halves) — types/pins confirmed.
- ✅ X1 'L'/X2 'R' joysticks → AA11/AA12; X6 → AA8-AA15 disk address; КД522 diodes.
- ⚠ Net `a` (D44.11 latch enable + D51.11/14/17/18) source is off-block (D37A/D22D gate logic).
- ⚠ D50_OE, D51.17, D51.OE destinations route off-block — trace later.

### addr-decode — ⚠ medium, consistent; ROM select unreadable
- ✅ D26 = КП12 paging mux (A9/A13/A14/A15 + K9); OE1(pin15) tied GND (always enabled).
- ⚠ **ROM /CE (pin20) and /OE (pin22) could NOT be traced to a specific gate** even
  by a dedicated agent — the decode field's green wires are too dense. **This
  vindicates the "functional decode" choice in sintez2.py block 2b.** Resolve via
  simulation (does the functional decode boot the ROM?) or a much higher-zoom trace.
- ⚠ Glue-gate (D9/D17/D22/D27/D37) pin numbers read, but inter-gate nets unresolved.

### arbitration ("crown jewel") — ⚠ medium, inconsistent; partially resolved
- ✅ **D5 = К1533КП11** (corrected). D5 makes K8/K11/K12; K9→D26.4; K10 from D7B (ЛИ1).
- ⚠ **D38 (ИР27)**: the 'CLK' label wires to D38.6 (Q2) — illogical (Q→CLK); the
  real clock input is pin11. D38 outputs Q3(9)=RAM, Q5(15)=FV; other Q's route to
  the data/bus area unlabeled. Needs careful re-trace.
- ⚠ Mux select lines (A0=pin14, A1=pin2) + OE0 shared on unlabeled vertical wires —
  the arbitration-control source is **the single most important unresolved net**
  (it's the screen-address generator). Defer to a dedicated high-zoom trace +
  simulator validation, as planned.

### sync-decode — ✅ medium, consistent
- ✅ Net `a` = GND (counter DI pins, /S, /R ties). D2/D19 (H) + D3/D4 (V) ИЕ7 counters.
- ⚠ D15/D16 drawn as ТМ2 (see corrections). D8A/D10B/D14C present (trace mis-reported missing).
- ⚠ Counter cascade control inputs (L/CU/CD, carries) + HSYNC/VSYNC decode gate
  nets (D10A/D14A/D14D/D21) route across the sheet — far ends not all resolved.

## What this means for the two tracks

- **KiCad (SKiDL):** pixel-chain, color (minus the missing D43), rgb-output,
  disk-io ICs, sync counters are ✅ ready to wire. addr-decode ROM-select and the
  arbitration screen-address generator are the two ⚠ blocks where vision tracing
  hit its limit — wire them functionally + flag, exactly as block 2b/4 already do.
- **Electronics simulator (SimulIDE):** the unresolved items (ROM /CE/OE gating,
  arbitration select timing, beep/port-0xFE source, РУ5 timing) are precisely the
  ones to **validate by simulation** — boot the ROM, watch /MREQ→/RAS/CAS, confirm
  the functional decode/arbitration produce a correct screen address. Installing
  SimulIDE + the `bridge/net2sim.py` is the enabling next step.
