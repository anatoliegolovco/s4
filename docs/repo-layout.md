# Source repository layout

This repository follows the layout in the spec (`docs/spec/sintez2-recon-spec.md`
§9), with one deviation: **all Markdown lives under `docs/`** per the project
documentation rules (`docs/RULES.md`). The spec itself therefore lives at
`docs/spec/sintez2-recon-spec.md` rather than the repo root.

| Path | Purpose | Spec task |
| --- | --- | --- |
| `docs/` | All documentation, decisions, and the discussion ledger. | — |
| `schematics/` | Block inventory (`NOTES.md`) + downloaded references. | T1 |
| `kicad/` | Canonical KiCad project (source of truth for the PCB). | T2, T8 |
| `parts_map.json` | Soviet ↔ modern ↔ KiCad symbol ↔ SimulIDE class ↔ timing. | T0 |
| `bridge/` | `net2sim.py` (KiCad netlist → SimulIDE XML) + reverse. | T3 |
| `sim/` | Extended SimulIDE component classes + generated circuits. | T5, T6 |
| `llm/` | Text-only LLM command surface + analysis glue. | T4 |
| `cpu/` | TV80 / A-Z80 soft-core integration for simulation. | T3 |
| `roms/` | NOT versioned; user supplies the stock 48K ROM. | — |
| `tests/` | ZEXDOC/ZEXALL, FUSE harness, regression verdicts. | T7, T9 |

All code directories are currently empty skeletons; they are populated as the
T0–T9 milestones are executed. Track progress in the ledger
(`docs/ledger/`).
