# 0005 — Author the schematic in SKiDL (Python → KiCad netlist)

- **Status:** accepted
- **Date:** 2026-06-14
- **Deciders:** project owner
- **Related:** [0002 KiCad source of truth](0002-kicad-source-of-truth-for-pcb.md) ·
  [0003 text-only LLM control plane](0003-text-only-llm-control-plane.md) ·
  spec §5.1 / §8 (T2)

## Context

T2 needs the canonical Sintez-2 schematic (~51 ICs). The spec §5.1 assumed we
"edit `.kicad_sch` as text". Hand-authoring KiCad `.kicad_sch` S-expressions
(symbol placement coordinates, wires, labels) for 51 ICs is slow and error-prone,
and KiCad has **no Soviet-part symbols** anyway. kicad-cli 7 (Ubuntu noble) also
lacks headless `sch erc` (added in v8+).

## Decision

**Author the schematic as Python using SKiDL**, which emits a **KiCad netlist**.
- Parts are defined once in `kicad/skidl/sintez_parts.py` from the datasheets /
  `schematics/bom.json` (pin number/name/type) — these definitions ARE the parts;
  no KiCad symbol library is required to produce a netlist.
- Standard through-hole **DIP footprints are reused** from KiCad's `Package_DIP:*`
  (every Sintez IC is a DIP) — no custom footprints to draw.
- The generated netlist → Pcbnew for PCB layout (T8) and → `bridge/net2sim.py`
  for SimulIDE. **KiCad remains the source of truth for the PCB** (decision 0002
  unchanged); SKiDL is just the text front-end that authors it.

## Consequences

- Positive: the design is plain Python — ideal for the zero-click LLM loop
  (decision 0003), git diffs, parameterization, and reuse; SKiDL runs its own ERC
  without KiCad installed.
- Trade-off: no hand-drawn graphical `.kicad_sch`. If a human-viewable schematic
  is ever wanted, generate `.kicad_sym`/a schematic from the same pin data — it is
  not on the fabrication path.
- Follow-ups: KiCad **9** still needed for Pcbnew layout + headless ERC at T8
  (`ppa:kicad/kicad-9.0-releases`); `parts_map.json` continues to drive the bridge.

## Alternatives considered

- **Hand-author `.kicad_sch` text** (spec §5.1 literal) — rejected: too tedious /
  error-prone for 51 ICs, no Soviet symbols, needs KiCad 8+ for headless ERC.
- **Generate `.kicad_sch` from `wiring.json`** — real graphical schematic, but
  requires building a robust auto-placement generator first; deferred (can still
  be added later for human viewing).
