# s4 — Documentation

Code name **Sintez 4**.

**Project:** *Sintez 2 — Modern Reconstruction & LLM-Driven Visual Simulation.*
A modern, sourceable recreation of the Soviet/Moldovan discrete-TTL ZX Spectrum
clone (keeping a real Zilog Z80), a visual open-source simulator the owner can
watch, and a text-only LLM control plane that drives the whole
iterate→simulate→verify→layout loop zero-click.

The canonical technical specification is
[`spec/sintez2-recon-spec.md`](./spec/sintez2-recon-spec.md). **Read it first.**

## Layout

| Path | Purpose |
| --- | --- |
| `docs/README.md` | This index. Start here. |
| `docs/RULES.md` | Rules for writing and maintaining docs and the ledger. |
| `docs/spec/` | Canonical technical specification. |
| `docs/decisions/` | Decision records (ADR-style) for lasting choices. |
| `docs/datasheets/` | Datasheet links + key parameters per part. |
| `docs/references/` | Catalog of owner-supplied primary sources (in `reference/`). |
| `docs/repo-layout.md` | The source-tree layout (spec §9) and deviations. |
| `docs/templates/` | Reusable templates for docs, decisions, and ledger entries. |
| `docs/ledger/` | Discussion ledger: timestamped Q&A grouped by topic. |

## Key decisions (non-negotiable constraints)

- [0001 — Keep a genuine Zilog Z80](./decisions/0001-keep-real-zilog-z80.md)
- [0002 — KiCad is the source of truth for the PCB](./decisions/0002-kicad-source-of-truth-for-pcb.md)
- [0003 — Text-only, zero-click LLM control plane](./decisions/0003-text-only-llm-control-plane.md)
- [0004 — Fidelity over improvement: no memory contention](./decisions/0004-fidelity-no-memory-contention.md)

## Conventions (summary)

- **Language:** every written record is in **English**, even when the
  discussion happened in another language.
- **Files and folders:** `kebab-case` (lowercase, words joined by `-`).
- **Timestamps:** UTC, ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`).

See [`RULES.md`](./RULES.md) for the full set of rules.

## Quick start

1. Understand the project → read [`spec/sintez2-recon-spec.md`](./spec/sintez2-recon-spec.md).
2. See where work stands → [`ledger/README.md`](./ledger/README.md) (open questions).
3. Adding a doc? Copy [`templates/doc.md`](./templates/doc.md).
4. Recording a decision? Copy [`templates/decision-record.md`](./templates/decision-record.md).
5. Logging a discussion? See [`ledger/README.md`](./ledger/README.md).
