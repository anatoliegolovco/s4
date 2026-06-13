# Q: How does the LLM automate KiCad schematics in 2026?

- **Topic:** tooling ([index](./README.md))
- **Status:** resolved
- **Opened:** 2026-06-13T10:33:56Z
- **Resolved:** 2026-06-13T10:33:56Z
- **Decision:** [0003](../../decisions/0003-text-only-llm-control-plane.md)

## Context

Spec §5.1 / §10.5. KiCad's IPC API (9.0+) covers the **PCB editor only**;
schematic-editor support is on the roadmap. The legacy SWIG `pcbnew` bindings
are deprecated and **removed in KiCad 11**.

## Discussion

### 2026-06-13T10:33:56Z — claude

Resolved from the spec's stated reality. Strategy:

- **Schematic:** the LLM edits `.kicad_sch` / `.kicad_pro` **as text** and uses
  `kicad-cli` for ERC, netlist export, and Gerber/BOM plotting. Do **not**
  assume an eeschema Python API.
- **PCB:** use the IPC API via `kicad-python` (placement, footprints, DRC) once
  the netlist exists.
- **Do not** build new work on SWIG `pcbnew` (gone in v11).

## Outcome

Schematic automation = text edits + `kicad-cli`; PCB automation = IPC API.
Captured in decision 0003 and the `llm/` skeleton (`kicad_cmds.py`).
Re-evaluate if/when IPC gains eeschema coverage.
