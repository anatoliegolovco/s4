# s4 — Sintez 4

**Sintez 2 — Modern Reconstruction & LLM-Driven Visual Simulation.**

A modern, sourceable recreation of the Soviet/Moldovan discrete-TTL ZX Spectrum
clone (keeping a real Zilog Z80), a visual open-source simulator (SimulIDE) the
owner can watch, and a text-only LLM control plane that drives the full
iterate→simulate→verify→layout loop with zero clicks. KiCad is the source of
truth for the PCB.

## Start here

- **Technical spec (canonical):** [`docs/spec/sintez2-recon-spec.md`](./docs/spec/sintez2-recon-spec.md)
- **Docs index:** [`docs/README.md`](./docs/README.md)
- **Decisions:** [`docs/decisions/`](./docs/decisions/)
- **Discussion ledger:** [`docs/ledger/README.md`](./docs/ledger/README.md)
- **Repo layout:** [`docs/repo-layout.md`](./docs/repo-layout.md)

## Source tree

`schematics/` · `kicad/` · `bridge/` · `sim/` · `llm/` · `cpu/` · `tests/` ·
`parts_map.json` — all currently skeletons, populated per milestones T0–T9 in
the spec. All Markdown lives under `docs/` (project rule).

## License

**Proprietary and confidential — © 2026 Lightcypher SRL. All rights reserved.**
This is **not** open-source software. See [`LICENSE`](./LICENSE). Third-party
tools (KiCad, SimulIDE, ngspice, SKiDL) keep their own licenses; mirrored
datasheets/scans under `reference/` belong to their respective owners.
