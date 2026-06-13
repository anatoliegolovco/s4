# Q: What are we building and what are the hard constraints?

- **Topic:** inception ([index](./README.md))
- **Status:** resolved
- **Opened:** 2026-06-13T10:33:56Z
- **Resolved:** 2026-06-13T10:33:56Z
- **Decision:** [0001](../../decisions/0001-keep-real-zilog-z80.md),
  [0002](../../decisions/0002-kicad-source-of-truth-for-pcb.md),
  [0003](../../decisions/0003-text-only-llm-control-plane.md),
  [0004](../../decisions/0004-fidelity-no-memory-contention.md)

## Context

A technical specification was handed off as the project inception document:
*Sintez 2 — Modern Reconstruction & LLM-Driven Visual Simulation*
(`docs/spec/sintez2-recon-spec.md`).

## Discussion

### 2026-06-13T10:33:56Z — user

Provided the full spec and instructed: use it as the tech spec and project
inception.

### 2026-06-13T10:33:56Z — claude

Registered the spec as the canonical document. Extracted the charter:

**Three deliverables, one loop:**
1. A modern recreation of the **Sintez 2** — a Soviet/Moldovan ZX Spectrum 48K
   clone built from discrete TTL (no ULA), rebuilt with modern sourceable parts
   while keeping a **real Zilog Z80**.
2. A **visual open-source electronics simulator** (SimulIDE) where the owner
   can watch signals propagate (buses, /MREQ, RAS/CAS, pixel clock, RGB).
3. An **LLM puppeteering layer**: extend the open-source tools' classes/APIs
   with text-friendly functions the LLM drives fully automatically, zero-click.

**Non-negotiable constraints (→ decision records):**
- Keep a genuine Zilog Z80 (Z84C00) in the physical build — [0001](../../decisions/0001-keep-real-zilog-z80.md).
- KiCad is the source of truth for the PCB — [0002](../../decisions/0002-kicad-source-of-truth-for-pcb.md).
- Everything the LLM touches is text; no GUI automation — [0003](../../decisions/0003-text-only-llm-control-plane.md).
- Fidelity over improvement: **no memory contention** — [0004](../../decisions/0004-fidelity-no-memory-contention.md).

Also created the §9 repository skeleton, `parts_map.json` stub,
`schematics/NOTES.md` stub (T1), and opened follow-up questions under the
`architecture`, `tooling`, and `sourcing` topics.

## Outcome

Project formally inaugurated. The spec is canonical
(`docs/spec/sintez2-recon-spec.md`); the four hard constraints are recorded as
accepted decisions; the repo skeleton and open questions are in place. Next
concrete work is milestones T0→T3 (environment, schematic notes, parts map +
bridge against CPU/decode/DRAM).
