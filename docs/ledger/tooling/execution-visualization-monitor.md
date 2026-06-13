# Q: How do we watch it run — a real-time monitor inside the electronics simulator?

- **Topic:** tooling ([index](./README.md))
- **Status:** open (requirement fixed by owner; the *how* — mixed-level — is the recommendation)
- **Opened:** 2026-06-13T22:24:19Z
- **Resolved:** —
- **Decision:** —

## Context

The owner's hard requirement, stated plainly: **reconstruct the computer inside the
electronics simulator (SimulIDE) — real components wired together — load the real
ROM, and see the monitor in a window, ideally real-time.** Explicitly **NOT** a
Sintez emulator. This refines spec §5.2/§5.4: the in-simulator monitor is the
canonical way to view execution; the separate software-emulator track (§5.4) is
dropped per the owner.

## Discussion

### 2026-06-13T22:15–22:24 — owner ↔ claude

**Requirement.** Electronics simulator, components connected, real ROM in the ROM
component, and a **monitor component in a SimulIDE window** fed by the circuit's
real RGB + /HS + /VS signals. No emulator.

**The monitor component.** SimulIDE has no native ZX display, so we build one
(SimulIDE is open-source C++; spec §5.2 already plans custom modules). It is an
oscilloscope that draws pixels instead of a trace: sample R/G/B at the pixel
clock → place a pixel; /HS → new line; /VS → new frame. Reconstructs 256×192 +
border.

**Why full gate-level is not real-time (owner asked why a GHz PC can't keep up
with a 3 MHz machine).** GHz measures *operations per second*, not "how fast 3 MHz
is". Reproducing one second of the board gate-by-gate costs **billions** of CPU
operations:

- ~50 chips ≈ a few thousand gates/flip-flops; the fastest clock is **14 MHz**
  (pixel), not 3.5. → ~10⁹–10¹⁰ gate-events per simulated second.
- A GUI event-driven sim spends ~10²–10³ CPU instructions per event (event queue,
  virtual calls, net resolution, GUI). → ~10¹¹–10¹³ instructions per sim-second.
- A 4 GHz core does ~10⁹–10¹⁰ useful instr/sec → **100×–10000× slowdown**; one
  1/50 s frame takes seconds–minutes of wall time.
- Root causes: the sim *computes* behaviour instead of *being* the silicon; real
  gates switch **in parallel**, the sim evaluates them **serially**; the animated
  GUI adds cost.

**Key insight — SimulIDE already "cheats" for speed.** It runs an Arduino in
real-time by using a **compiled behavioural CPU model** plus a *small* gate-level
periphery — not gate-level silicon. We can apply the same selectively.

### Options for a real-time (or near) monitor

| # | Approach | Real-time? | Keeps "electronics simulator" feel? |
| --- | --- | --- | --- |
| 1 | **Mixed-level in SimulIDE** — behavioural/compiled models for the fast/regular blocks (Z80, DRAM, 14 MHz pixel chain); gate-level for the parts we study (bus arbitration, sync, glue) | near real-time | **yes** — recommended |
| 2 | **Compiled RTL (Verilator)** — describe logic in HDL, compile to C++ (~100–1000× faster), thin frame renderer | yes | partly (textual RTL, not animated breadboard) |
| 3 | **FPGA** — synthesize to real parallel hardware, real ROM, real RGB out | absolute | no (leaves the simulator) |
| – | Full gate-level animated SimulIDE | no (100×–10000× slow) | yes, but frame-by-frame only |

**Fundamental trade-off:** *faithful-but-slow* (full gate-level) vs
*fast-but-abstracted* (mixed-level / RTL / FPGA). You cannot max both for a whole
computer on one PC.

## Recommendation

**Option 1 — mixed-level in SimulIDE.** Gate-level where fidelity is the point
(CPU↔video bus arbitration via КП12, К1533ИЕ7 sync/refresh counters, RAS/CAS
timing, the glue we are validating); behavioural models for the heavy/regular
blocks (Z80 core, К565РУ5 DRAM array, the ИР16 pixel serializers) so the custom
monitor window updates fast enough to watch. This satisfies "see it work
electrically" **and** a usable real-time-ish monitor, without an emulator.

Next artefacts: (a) decide the gate-level/behavioural split per block; (b) spec
the monitor component (inputs = post-RGB-stage R/G/B + /HS + /VS; output = raster
widget); (c) obtain the 16 KB ROM binary for the ROM component.

## Outcome

<!-- pending owner sign-off on the mixed-level split -->
