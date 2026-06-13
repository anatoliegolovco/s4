# Sintez 2 — Modern Reconstruction & LLM-Driven Visual Simulation

## Technical Specification / Hand-off Brief for a Claude Code Context

> **Read me first.** You are a fresh Claude Code agent inheriting an ongoing
> retro-computing project. You did **not** participate in the prior design
> conversations; this document is your entire context. It is intentionally
> dense and self-contained. Treat every section as authoritative project
> knowledge. Where you must search, the canonical links are in
> [§12 References](#12-references). When in doubt about Sintez-specific
> hardware quirks, the Russian community at **zx-pk.ru** has people with the
> physical machine and corrected schematics.

-----

## 0. TL;DR — What we are building

Three deliverables, one loop:

1. **A modern recreation of the Sintez 2** — a Soviet/Moldovan ZX Spectrum
   clone built entirely from discrete TTL logic (no ULA chip) — rebuilt with
   **modern, sourceable components** while keeping a **real Zilog Z80** CPU.
1. **A visual, open-source electronics simulator** where the human owner can
   **watch the signals propagate** (buses, /MREQ, RAS/CAS, pixel clock, RGB).
1. **An LLM “puppeteering” layer**: the simulator and EDA tools are open
   source so we **extend their internal classes / APIs** with **text-friendly
   functions** an LLM can drive **fully automatically, zero-click** — no GUI
   pixel-clicking, no human in the inner loop.

The board is fabricated by exporting to / authoring in **KiCad** (Gerbers →
PCB fab). The visual play happens in **SimulIDE**. A **text↔text bridge**
connects the two so the LLM owns the full iterate→simulate→verify→layout loop.

**Non-negotiable constraints**

- Keep a genuine **Zilog Z80** (Z84C00 family) in the physical build.
- **KiCad is the source of truth for the PCB** (you order from its Gerbers).
- Everything the LLM touches must be **text** (netlists, `.kicad_sch`, SimulIDE
  XML, VCD, JSON) — never screen automation.
- **Fidelity over “improvement”:** the Sintez has no memory contention. If a
  contention-dependent test passes, the model is *wrong* for this machine.

-----

## 1. Project background — what the Sintez 2 actually is

- **Origin:** Soviet-era ZX Spectrum 48K-compatible clone manufactured at the
  **“Signal” plant (НПО «Сигнал»)** in **Chișinău, Moldovan SSR**, ~1989.
  It is **not** a Romanian clone (do not confuse with ICE Felix HC-85, Cobra,
  CIP from Băneasa/Politehnica) and **not** Băneasa.
- **CPU:** Uses the Soviet **UA 880D / КР1858ВМ1**-class part, which is
  **pin- and opcode-compatible with the Zilog Z80**. Runs at **3.5 MHz**.
- **Defining hardware trait — NO ULA.** Unlike a real Spectrum (Ferranti ULA),
  the Sintez 2 implements all video/timing/glue with **discrete TTL** (Soviet
  К555 / К1533 families ≈ 74LS / 74ALS). The RGB output is generated directly
  at TTL level (clean digital), not through a ULA.
- **Consequence — NO MEMORY CONTENTION.** There is no ULA disputing the bus,
  so the Z80 runs at a constant 3.5 MHz with **no slowdown** on any memory
  region. This is the single most important behavioral fact:
  - The Z80 core uses **canonical T-state counts** — no contention table, no
    `6,5,4,3,2,1,0,0` pattern.
  - Software that depends on tight contention timing (multicolor demos,
    Nirvana engine, rainbow-border effects) **will not run** on real Sintez 2
    hardware and must **not** run in our model. That is fidelity, not a bug.
- **ROM/BASIC:** Runs the **stock ZX Spectrum 48K 16 KB ROM**. All BASIC
  interpreter / FP-calculator internals are standard Spectrum documentation.
- **Storage:** Beta Disk + **TR-DOS** (WD1793 FDC, separate TR-DOS ROM with
  bank switching) on 5.25” floppies, in addition to tape.

**Schematic caveat:** the publicly scanned Sintez schematics contain **known
errors** (some connector pinouts relate to the mainboard rather than the
wired connectors). A re-mastered schematic on the MCbx page has corrected
pinouts. Always cross-check against zx-pk.ru repair threads.

-----

## 2. Target hardware architecture (what the recreation must implement)

### 2.1 CPU & clock

- **Z80** @ **3.5 MHz** (canonical T-states; 69,888 T-states per 50 Hz frame:
  224 × 312).
- **Pixel clock 14 MHz = 2× CPU clock**, asynchronous to the CPU clock. Drives
  the pixel shift register chain.

### 2.2 Memory map (standard 48K Spectrum)

|Region                                    |Address                            |Notes                         |
|------------------------------------------|-----------------------------------|------------------------------|
|ROM (BASIC + FP calculator + I/O)         |`0x0000–0x3FFF`                    |16 KB, stock 48K ROM          |
|RST handlers / vectors                    |`0x0000, 0x0008, 0x0010, …, 0x0038`|entry points                  |
|BASIC interpreter                         |`0x0000–0x1CFF`                    |main logic                    |
|FP calculator (5-byte float stack machine)|`0x1D00+` (`CALCULATE` ≈ `0x335B`) |RPN-like calc stack           |
|Keyboard scan                             |`~0x028E`                          |                              |
|Character font (8×8)                      |`0x3D00–0x3FFF`                    |96 chars × 8 bytes = 768 bytes|
|Screen bitmap                             |`0x4000–0x57FF`                    |256×192, ZX interleaved layout|
|Screen attributes                         |`0x5800–0x5AFF`                    |32×24, byte = `FLASH          |
|System vars / BASIC area / RAM            |`0x5B00–0xFFFF`                    |                              |

- **Bank switching:** native Z80 addresses 64 KB. If the modern build wants
  more RAM, page it through a window with latches/registers holding a wide
  bank address (the Z80 doesn’t care what’s behind the address decoder).
  128–512 KB is typical; >1 MB is possible but software-impractical. The
  Z180/Z280 have built-in MMUs (up to ~1 MB) if a successor CPU is ever
  considered — but **we keep the Z80**.

### 2.3 Video subsystem (the most Sintez-specific part — all discrete TTL)

- **ULA-replacement logic:** discrete TTL generates H/V sync and bus
  arbitration. **No ULA chip exists** — this entire arbitration circuit is the
  “crown jewel” to visualize.
- **Sync/refresh counters:** **К1533ИЕ7** counters (≈ 74ALS counter) generate
  H/V sync and the DRAM refresh addresses.
- **CPU/video bus arbitration:** **КП12** multiplexers switch the address/data
  bus between CPU and video fetch.
- **Pixel shift registers:** **D39/D40/D41 = К555ИР16** (≈ **74LS165**),
  clocked at **14 MHz** to serialize pixel data. **Deliberately К555 (LS), not
  К1533 (ALS)** — the designer chose the slower family for more forgiving
  setup/hold margin against the pixel clock. **Preserve this choice.**
- **RGB output stage:** emitter-follower level shifters built from
  **КТ315Г (NPN) / КТ361Г (PNP)** transistors (VT13–VT18 region), with trimmer
  resistors (~R41–R60 region) to calibrate output levels per transistor batch.

### 2.4 Memory (DRAM) — timing is analog and matters

- **DRAM:** **К565РУ5** (≈ 4164, 64Kx1 DRAM). Requires **RAS-before-CAS**
  refresh; **RAS-only refresh cycles interleaved** with CPU accesses, addressed
  by the К1533ИЕ7 counter.
- The Sintez **WAIT generator was calibrated to the *slow* Soviet РУ5 timing**
  (tRAS, tCAS, tRCD, precharge, sense-amp recovery). zx-pk.ru repair threads
  confirm that dropping faster imported 4164s in can cause **instability**
  (WAIT pulse mismatch, marginal address setup). For simulation, **model DRAM
  behaviorally with actual К565РУ5 timing parameters** — do not silently swap
  to a generic 4164 or SRAM model, which would make the machine look more
  reliable than reality.

### 2.5 Audio & tape

- **BEEP** via port `0xFE` (also border + tape). Port `0xFE` writes must be
  **timestamped in T-states**, not collapsed at end-of-frame, because the
  raster exists regardless of TTL-vs-ULA implementation.
- **Tape tone decoder:** **К5545АЗ** ≈ **LM567**. **Do not substitute** for
  accurate analog behavior.

-----

## 3. Soviet → modern component substitution guide (encyclopedic)

Soviet ICs were **clones, not exact copies** — same nominal datasheet, but
different process nodes and fab tolerances, occasionally subtle circuit
changes. Risk of behavioral divergence splits into categories:

|#|Class                                     |Examples                                             |Substitution risk       |Rule                                                                                |
|-|------------------------------------------|-----------------------------------------------------|------------------------|------------------------------------------------------------------------------------|
|1|**Pure Boolean logic** (~95% of the board)|К1533ЛА3 ≈ 74ALS10, decoders, bus muxes, control glue|**Zero** for logic state|Free to swap to 74ALS/74HC equivalents; truth tables identical                      |
|2|**DRAM**                                  |К565РУ5 ≈ 4164                                       |**High (timing)**       |Model with real РУ5 timing; swapping to fast 4164/SRAM changes WAIT behavior        |
|3|**Pixel shift registers**                 |К555ИР16 ≈ 74LS165 (D39/D40/D41)                     |**Subtle (setup/hold)** |Keep **LS** family timing (~20–25 ns setup) — ALS (~7–10 ns) gives ~3× false margin |
|4|**Video-output transistors**              |КТ315Г/КТ361Г (VT13–VT18)                            |**Analog levels**       |RGB level depends on Vbe/hFE; real boards used trimmers. 2N3904/BC237 ≈ wrong levels|
|5|**Tape tone decoder**                     |К5545АЗ ≈ LM567                                      |**Do not substitute**   |Keep equivalent function exactly                                                    |

**Practical guidance for the recreation:**

- For everything in **Class 1**, choose modern, **sourceable** logic
  (74HC/74HCT or 74ALS) — these are the parts you can buy and put on a PCB.
- For **Class 2 (DRAM)**: a real recreation may legitimately replace DRAM with
  **modern SRAM + glue** to drop the refresh complexity *in hardware*, but the
  **simulation model must keep РУ5 timing** if you want bug-for-bug fidelity.
  Decide explicitly per build target (faithful vs. “improved & reliable”).
- For **Class 3/4/5**: preserve family/part choices where analog/timing
  behavior is observable (pixel chain, RGB stage, tape).

> Tool note: AI-assisted “legacy → modern part” suggestion exists in
> **Flux (flux.ai / buildwithflux)** — Copilot can propose cheaper/in-stock
> alternatives, create parts from datasheets, and import **KiCad** libraries
> (schematic import from Altium ASCII / Cadence EDIF; **layout import not
> supported**). Optional aid, not a core dependency.

-----

## 4. Keeping a real Z80 — sourcing

|Part                            |What                                  |Notes / where                                                             |
|--------------------------------|--------------------------------------|--------------------------------------------------------------------------|
|**Zilog Z84C00** (e.g. Z84C0020)|Genuine modern CMOS Z80, in production|€3–5 at Mouser / Digi-Key / TME; ships to Moldova; **recommended default**|
|КР1858ВМ1 / КР1858ВМ3           |Soviet NMOS/CMOS Z80 clone            |eBay / au.ru / orion43.ru; shipping restrictions vary                     |
|U880 / UB880D                   |East German (MME) clone               |eBay; often easier to find than Soviet parts                              |
|MMN 80 CPU                      |Romanian (Microelectronica) clone     |from Romania (EU neighbor)                                                |
|MME “80A CPU”                   |Z80A 4 MHz NMOS clone                 |~$10 + shipping from Ukraine                                              |

**FPGA fallback (if a physical Z80 ever becomes unavailable):** run an
open-source soft core — **TV80** or **A-Z80** — on a small FPGA
(Lattice iCE40, Gowin GW1N; boards: iCEBreaker, Tang Nano), optionally
pin-compatible with a Z80 socket. **In simulation we always use a soft/
behavioral Z80 core** (TV80 / A-Z80) because a physical chip can’t be
co-simulated; the real Z84C00 only lives on the fabricated PCB.

-----

## 5. Tool stack

### 5.1 KiCad — schematic + PCB + fabrication (source of truth for the board)

- **License:** GPL v3. Full EDA: schematic capture, PCB layout, Gerber output;
  runs on Windows/Linux/macOS.
- **Why it’s the hub:** you **order the PCB from KiCad’s Gerbers** — it is the
  destination, so there is **no “export to KiCad” step** if the schematic is
  authored here. Huge symbol/footprint libraries (74xx, Z80, modern parts).
- **Built-in simulation:** integrates **ngspice** for graphical SPICE
  simulation inside the Schematic Editor (good for analog: PSU, clock, RGB
  output path). Improved substantially in KiCad 8; usable for mixed-signal.
- **Puppeting surface (text/Python — this is the LLM control plane):**
  - **IPC API** (KiCad **9.0+**): stable, language-agnostic interface to a
    running KiCad session over a Unix socket / named pipe. **In 9.0 it covers
    the PCB editor only**; schematic-editor support is on the roadmap.
  - **`kicad-python`** (PyPI): official Python bindings for the IPC API.
    Requires a running KiCad with the API server enabled
    (Preferences → Plugins). Depends on `protobuf`, `pynng`.
  - **Legacy SWIG `pcbnew`** bindings: still present in 9/10, **deprecated**,
    **removed in KiCad 11** — do not build new work on SWIG.
  - **`kicad-cli`**: headless CLI for ERC/DRC, netlist export, plotting
    Gerbers, BOM, etc. — the backbone for zero-click batch steps.
  - **Schematic automation reality (2026):** because IPC doesn’t yet cover the
    schematic editor, the LLM mostly **edits `.kicad_sch` / `.kicad_pro` as
    text** and uses `kicad-cli` for netlist/ERC/exports. Plan around this.

### 5.2 SimulIDE — the visual signal playground (what the human watches)

- **License:** AGPL v3. C++/Qt. Real-time, drag-drop, “push the power button”
  interactive simulation; optimized for speed/low CPU.
- **Why it fits the TTL machine:** **event-driven engine, 1 ps accuracy**, and
  **no digital/analog split — everything runs in analog mode**: logic pins have
  **configurable impedance, output voltage, and LH/HL thresholds**, so it
  models **fan-in/fan-out and different logic families** (LS vs ALS vs HC) —
  exactly the К555-vs-К1533 distinction we must preserve.
- **Observability built-in:** **Oscilloscope**, **Logic Analyzer**, **circuit
  animation**, **VCD export** (configurable base time step, e.g. 100 ps; can
  export at pause), serial-port connection, subcircuits, DIP/logic symbols.
- **Extensibility (your “extend its classes” requirement):** custom components
  via **(a) subcircuits, (b) modular components, (c) script-based components**;
  modules exist for memories, displays, console, comms. For Sintez-specific
  parts (К565РУ5 behavioral DRAM, КП12 mux, ИЕ7 counter, ИР16 shift register)
  you add component classes in the C++ source and/or as subcircuit/script
  modules.
- **Limitation:** SimulIDE is a *simulator*, **not** a PCB/layout tool — it
  does **not** export KiCad/Gerber. Hence the bridge in §7.

### 5.3 ngspice

- The SPICE engine inside KiCad; also usable standalone in **batch mode
  (`-b`)** for the analog corners (PSU, 14 MHz/3.5 MHz clock generation, RGB
  emitter-follower levels with КТ315/КТ361 models). Text netlist in, data out.

### 5.4 Optional reference / cross-check tooling (from prior project work)

> **Owner directive (2026-06-13):** execution is watched **inside the electronics
> simulator** — real components wired in SimulIDE, the real ROM in the ROM
> component, and a custom **monitor component** rendering the circuit's RGB+sync
> in a window. The software-emulator track below is **dropped** as a viewing tool
> (kept only as an optional headless CRC/ZEXDOC cross-check). Real-time monitor is
> pursued via **mixed-level simulation** — see
> [`ledger/tooling/execution-visualization-monitor.md`](../ledger/tooling/execution-visualization-monitor.md).

- **Software emulator** (separate track): C23 → WASM Z80 core + passive video
  renderer; validated headless via **ZEXDOC/ZEXALL** (Frank Cringle, CRC),
  **FUSE test suite** (`tests.in`/`tests.expected`, per-instruction T-states &
  memory accesses), **Patrik Rak** contention/floating-bus tests. **For Sintez
  2, contention tests must NOT pass** (no contention) — passing them means a
  wrong machine. Use ZEXDOC + “boots to the `©` prompt” as the bar.
- **Disassembly/RE:** Fuse (+ gdbserver fork `github.com/speccytools/fuse`,
  `--gdbserver <port>`), `z80dasm`, Ghidra (Z80 module), radare2/rizin,
  `z88dk-gdb`.
- **Floppy ingest (TR-DOS):** SAMdisk, Keir Fraser’s `disk-utilities`,
  `trdtool`/`trd2scl`, Fuse/libspectrum utils.

-----

## 6. LLM puppeteering layer (the core new work)

**Goal:** a thin, text-only control plane so an LLM iterates the design with
**zero clicks**. The LLM never drives a GUI; it edits text artifacts and calls
functions that return text/JSON.

### 6.1 Principle

- **GUI automation is forbidden.** No Playwright/Selenium pixel puppeting.
- The LLM operates on: `.kicad_sch`, `.kicad_pcb`, KiCad netlists (`.net`),
  SimulIDE circuit XML, VCD waveforms, and JSON status blobs.
- We **extend the open-source tools’ internal classes/APIs** to expose exactly
  the verbs the LLM needs, each producing **parseable text**.

### 6.2 The command surface to build (wrap, don’t reinvent)

Expose a small CLI/library (Python preferred) with verbs such as:

- **KiCad side (via `kicad-cli` + `kicad-python`/IPC + text edits):**
  - `kicad.netlist_export()` → canonical netlist (text)
  - `kicad.erc()` / `kicad.drc()` → JSON pass/fail + violations
  - `kicad.plot_gerbers()` → fab outputs
  - `kicad.place(ref, x, y)` / `kicad.list_footprints()` (PCB, IPC API)
  - `kicad.sch_edit(...)` → structured edits to `.kicad_sch` text (until IPC
    covers eeschema)
- **SimulIDE side (via extended C++ classes + a control socket/CLI you add):**
  - `sim.load(circuit.sim)` / `sim.run(t)` / `sim.pause()` / `sim.reset()`
  - `sim.probe(net)` → current logic level / voltage
  - `sim.scope(net, window)` → samples
  - `sim.export_vcd(path)` → waveform file
  - `sim.add_component(type, params)` / `sim.connect(a_pin, b_pin)`
  - `sim.assert(net, expected, at_t)` → JSON verdict
- **Analysis glue (write this):**
  - `vcd_to_json(path, nets=[…])` → compact JSON the LLM reads cheaply
  - Verdict helpers: “Is `/MREQ` low at T2 of an M1 fetch?”, “Is RAS-before-CAS
    honored?”, “Does boot reach the `©` prompt?”, “Are H/V sync periods within
    spec?”

> **Why this matches the requirement:** these are the “internal functions that
> are already text-compatible for an LLM.” KiCad’s Python/IPC API *is* such a
> surface (text in/out); for SimulIDE you create the equivalent by extending
> its classes and adding a headless control entry point.

### 6.3 The zero-click loop

```
        ┌─────────────────────────────────────────────────────┐
        │  LLM (Claude Code)                                   │
        │  reads JSON/VCD verdicts → edits netlist / sch text  │
        └───────────────┬─────────────────────────────────────┘
                        │ text edits + CLI calls
        ┌───────────────▼───────────────┐     ┌──────────────────┐
        │ KiCad (source of truth)        │     │ SimulIDE          │
        │ .kicad_sch / .kicad_pcb        │◄───►│ circuit XML       │
        │ kicad-cli: ERC/DRC/netlist/    │ §7  │ run → scope/LA →  │
        │ gerbers ; IPC(PCB) ; py edits  │bridge│ VCD export        │
        └───────────────┬───────────────┘     └─────────┬────────┘
                        │ netlist                        │ VCD/JSON
                        ▼                                ▼
                ┌───────────────────────────────────────────────┐
                │ Analysis glue: vcd_to_json + verdict library   │
                │ returns PASS/FAIL + reasons (text/JSON)         │
                └───────────────────────────────────────────────┘
                        ▲                                │
                        └────────── verdicts ────────────┘
```

One iteration: LLM edits canonical netlist/schematic → bridge regenerates the
SimulIDE circuit → `sim.run` → `export_vcd` → `vcd_to_json` + verdicts →
LLM reads text result → corrects. Periodically: `kicad-cli` ERC/DRC and
Gerber plot as sanity gates. **No human click anywhere in the inner loop.**
The human watches SimulIDE’s animated schematic when they *want* to (“vreau să
văd și eu”), but it is not required for progress.

-----

## 7. KiCad ↔ SimulIDE bridge (build this — both ends are text)

**Problem:** SimulIDE doesn’t export KiCad/Gerber; KiCad’s digital-logic
*visualization* is weak compared to SimulIDE’s animated TTL. **Solution:** keep
**one canonical design in KiCad** (so the PCB is automatic) and **generate the
SimulIDE circuit from it** (so the human sees signals and the LLM gets VCD).

- **Canonical direction (recommended):** `KiCad netlist (.net) → SimulIDE circuit XML`. Map each KiCad component (by value/footprint) to a SimulIDE
  component class + parameters (incl. the family timing: LS vs ALS vs HC), and
  each KiCad net to SimulIDE wires/tunnels.
- **Reverse direction (optional):** `SimulIDE XML → KiCad netlist` if you ever
  prefer to draft in SimulIDE; then KiCad imports the netlist for layout.
- Both formats are **plain text/XML**, so the **LLM owns the converter** and
  can extend the mapping table as new Sintez parts are modeled.
- **Component mapping table** is a first-class artifact: `parts_map.json`
  (Soviet part ↔ modern part ↔ KiCad symbol/footprint ↔ SimulIDE class ↔
  timing params). Drives both substitution (§3) and the bridge.

-----

## 8. Concrete tasks (milestones with “done” criteria)

> Execute roughly in order; each task is self-contained enough to hand to a
> sub-agent. “Done” = the stated, machine-checkable criterion.

**T0 — Environment & repo skeleton**

- Install KiCad 9+ (IPC API enabled), SimulIDE (latest dev), ngspice, Python.
- Create repo layout (§9). Commit `parts_map.json` stub.
- **Done:** `python -c "import pcbnew"` works *and* `kicad-cli version` works
  *and* SimulIDE launches and runs a 2-gate test circuit headlessly.

**T1 — Acquire & sanity-check the Sintez schematics**

- Pull schematics/pinouts from the §12 sources; flag the known scan errors;
  reconcile against the re-mastered MCbx pinouts and zx-pk.ru threads.
- **Done:** a `schematics/NOTES.md` listing every block (CPU, decode, DRAM+
  refresh, video arbitration, pixel chain, RGB, audio, tape, TR-DOS) with the
  source used and any discrepancy resolved.

**T2 — Canonical KiCad schematic, block by block**

- Author the schematic in KiCad using **modern Class-1** logic, behavioral
  decisions per §3 for Classes 2–5. Keep Z80 socket for a real Z84C00.
- **Done:** `kicad-cli sch erc` passes (no unconnected/no ERC errors), netlist
  exports cleanly.

**T3 — KiCad→SimulIDE bridge v1**

- Implement `net2sim` using `parts_map.json`. Start with the CPU + memory
  decode + DRAM blocks only.
- **Done:** generated `.sim` loads in SimulIDE; the Z80 (TV80/A-Z80 model)
  fetches from ROM and address/data lines toggle in the scope.

**T4 — LLM command surface (§6.2)**

- Wrap `kicad-cli`/`kicad-python` and the SimulIDE control entry point; build
  `vcd_to_json` + verdict library.
- **Done:** a single script runs sim, exports VCD, and prints JSON verdicts for
  at least: M1 fetch timing, RAS-before-CAS, H/V sync periods.

**T5 — DRAM timing model (К565РУ5)**

- Behavioral DRAM with real РУ5 tRAS/tCAS/tRCD/precharge; refresh via ИЕ7
  counter; correct WAIT generation.
- **Done:** verdict “RAS-before-CAS honored & refresh interleaved” passes;
  swapping to a fast-4164 timing profile *changes* the WAIT verdict (proves the
  model is timing-sensitive, per §2.4).

**T6 — Video chain & RGB**

- КП12 bus arbitration, ИЕ7 sync, К555ИР16 pixel chain @14 MHz, RGB stage
  (ngspice for КТ315/КТ361 levels). Preserve LS timing on the shift chain.
- **Done:** generated framebuffer matches the standard ZX screen layout for a
  known test image; pixel-clock vs CPU-clock asynchrony visible in scope;
  contention tests are confirmed **inapplicable**.

**T7 — Boot validation**

- Run the stock 48K ROM to the `©` prompt in the integrated model.
- **Done:** boot reaches `©`; ZEXDOC passes on the CPU core; Patrik Rak
  contention tests are intentionally **not** run / documented as N/A.

**T8 — PCB layout & fabrication outputs**

- Lay out in KiCad Pcbnew; DRC clean; generate Gerbers/drill/BOM; target a fab
  (e.g. JLCPCB) reachable from Moldova; source the Z84C00 and Class-1 parts.
- **Done:** `kicad-cli pcb drc` clean; Gerbers + BOM produced; a sourcing sheet
  lists in-stock modern equivalents for every line in `parts_map.json`.

**T9 — Full zero-click loop hardening**

- Make the entire iterate→simulate→verify→(layout sanity) loop runnable as one
  command with structured logs; add regression verdicts to CI.
- **Done:** a single `make iterate` (or equivalent) runs end-to-end with no GUI
  interaction and emits a pass/fail report.

-----

## 9. Suggested repository layout

```
sintez2-recon/
├─ SINTEZ2-RECON-SPEC.md        # this file
├─ schematics/
│  ├─ NOTES.md                  # block inventory + scan-error reconciliation
│  └─ sources/                  # downloaded references (uncommitted if large)
├─ kicad/                       # canonical project (.kicad_pro/.kicad_sch/.kicad_pcb)
├─ parts_map.json               # Soviet ↔ modern ↔ KiCad symbol ↔ SimulIDE class ↔ timing
├─ bridge/
│  ├─ net2sim.py                # KiCad netlist → SimulIDE XML
│  └─ sim2net.py                # (optional) reverse
├─ sim/
│  ├─ components/               # extended SimulIDE component classes / subcircuits
│  └─ circuits/                 # generated .sim files
├─ llm/
│  ├─ kicad_cmds.py             # kicad-cli / kicad-python / IPC wrappers
│  ├─ sim_cmds.py               # SimulIDE control + probe/scope/assert
│  ├─ vcd_to_json.py
│  └─ verdicts.py               # M1 timing, RAS/CAS, sync, boot checks
├─ cpu/                         # TV80 / A-Z80 model integration for sim
├─ roms/                        # NOT versioned; user supplies 48K ROM
└─ tests/                       # ZEXDOC/ZEXALL, FUSE tests harness, regressions
```

-----

## 10. Known pitfalls (read before you waste a day)

1. **No contention is a feature.** Do not “fix” missing slowdown. Passing
   Patrik Rak contention tests = wrong machine. Bar is ZEXDOC + boots to `©`.
1. **DRAM timing is analog-ish.** Don’t swap К565РУ5 → generic 4164/SRAM in the
   *model* without flagging it; the WAIT generator was tuned to slow Soviet
   parts (zx-pk.ru repair evidence). Hardware *may* modernize; the model must
   stay honest about which target it represents.
1. **Keep LS on the pixel shift chain.** К555ИР16 (LS) was a deliberate timing
   choice; ALS timing inflates setup margin ~3×.
1. **RGB transistors aren’t 1:1.** КТ315/КТ361 ≠ 2N3904/BC237 for output
   *levels*; real boards had trimmers. Only matters for the analog RGB path.
1. **KiCad schematic scripting is immature (2026).** IPC API in 9.0 is **PCB
   only**; SWIG is deprecated (gone in 11). Plan to edit `.kicad_sch` as text +
   use `kicad-cli` for ERC/netlist/exports. Don’t assume an eeschema Python API.
1. **SimulIDE has no PCB export.** That’s why the bridge exists — KiCad stays
   the fabrication source of truth.
1. **Schematic scans have errors.** Trust the re-mastered MCbx pinouts and
   cross-check zx-pk.ru before committing a net.
1. **14 MHz pixel clock is async to the 3.5 MHz CPU clock.** Visualizing it
   correctly needs sub-T-state resolution — SimulIDE’s 1 ps engine handles it,
   but keep the two clock domains explicitly separate in the model.

-----

## 11. Glossary (quick decode of Soviet part numbers)

|Soviet                   |Western ≈                 |Role in Sintez                     |
|-------------------------|--------------------------|-----------------------------------|
|КР1858ВМ1 / UA880D / U880|Z80                       |CPU                                |
|К1533… (e.g. ЛА3)        |74ALS… (74ALS10)          |fast glue logic                    |
|К555… (e.g. ИР16)        |74LS… (74LS165)           |shift registers, slower glue       |
|К565РУ5                  |4164                      |64Kx1 DRAM                         |
|К1533ИЕ7                 |74ALS-class counter       |refresh address + H/V sync counters|
|КП12                     |bus multiplexer           |CPU/video bus arbitration          |
|КТ315Г / КТ361Г          |(≈) NPN / PNP small-signal|RGB output level shifters          |
|К5545АЗ                  |LM567                     |tape tone decoder                  |

-----

## 12. References

**Sintez 2 hardware / schematics**

- MCbx Old Computer Collection (best English deep-dive; corrected pinouts):
  `https://oldcomputer.info/8bit/sintez/index.htm`
- speccy.info (Russian, most detailed Sintez technical wiki):
  `https://speccy.info/Sintez`
- Sintez-M schematics (predecessor, shares logic design):
  `https://trastero.speccy.org/cosas/JL/Sintez-M/sintez-m.html`
- retropages.hu hardware photos:
  `https://retropages.hu/Gepek/Sintez`
- zx-pk.ru — Russian forum, most active for Soviet clones, repair threads, PCB
  scans, corrected schematics: `https://zx-pk.ru`

**ROM / BASIC internals (stock 48K ROM)**

- “The Complete Spectrum ROM Disassembly” (Logan & O’Hara) PDF:
  `https://primrosebank.net/computers/zxspectrum/docs/CompleteSpectrumROMDisassemblyThe.pdf`
- Annotated `.asm` (reclaimed/prettybasic):
  `https://github.com/reclaimed/prettybasic`
- Geoff Wearmouth annotated disassembly (search online)

**Z80 references**

- `https://z80.info`
- Opcode tables: `https://clrhome.org/tables/`
- Soft cores: TV80 (`https://github.com/hutch31/tv80`), A-Z80
  (`https://github.com/gdevic/A-Z80`)

**KiCad**

- IPC API for add-on developers:
  `https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-addon-developers/index.html`
- APIs & bindings (SWIG deprecation notice, removed in v11):
  `https://dev-docs.kicad.org/en/apis-and-binding/index.html`
- `kicad-python` (PyPI): `https://pypi.org/project/kicad-python/`
- SPICE/ngspice integration: `https://www.kicad.org/discover/spice/`
- ngspice-in-KiCad examples (labtroll): `https://github.com/labtroll/KiCad-Simulations`

**SimulIDE**

- Site / features: `https://simulide.com/p/`
- Knowledge base (engine, custom components): `https://simulide.com/p/simulidekb/`
- Component list (scope/VCD/logic analyzer details): `https://simulide.com/p/component-list/`

**RE / debug / floppy ingest**

- Fuse + gdbserver fork: `https://github.com/speccytools/fuse`
- Keir Fraser disk-utilities: `https://github.com/keirf/disk-utilities`
- SAMdisk: `https://simonowen.com/samdisk/`

**Validation suites**

- ZEXDOC/ZEXALL (Frank Cringle) — CPU correctness via CRC
- FUSE test suite (`tests.in` / `tests.expected`) — per-instruction T-states &
  memory accesses
- Patrik Rak tests — contention/floating bus (**N/A for Sintez 2 — must NOT pass**)

-----

## 13. How to start (first three moves for the inheriting agent)

1. Confirm tools (T0). If KiCad’s IPC server or SimulIDE headless run isn’t
   available, say so and propose the text-file fallback path.
1. Build `schematics/NOTES.md` (T1) from §12 sources; surface every place the
   public scans disagree with zx-pk.ru / MCbx before drawing a single net.
1. Stand up `parts_map.json` + `bridge/net2sim.py` against the CPU+decode+DRAM
   blocks (T2→T3) so the zero-click loop has something real to chew on.

Keep the human’s two hard wants in view at all times: **(a) a real Zilog Z80 on
a KiCad-fabricated PCB, and (b) a visual simulator they can watch — driven by an
LLM through text functions, zero-click.**