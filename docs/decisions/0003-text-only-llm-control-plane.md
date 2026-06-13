# 0003 — Text-only, zero-click LLM control plane (no GUI automation)

- **Status:** accepted
- **Date:** 2026-06-13
- **Deciders:** project owner (via spec)
- **Related question:** [tooling/schematic-automation-strategy](../ledger/tooling/schematic-automation-strategy.md)

## Context

The owner wants an LLM to own the full iterate→simulate→verify→layout loop
with zero clicks. GUI pixel-puppeting (Playwright/Selenium) is brittle and
forbidden.

## Decision

Everything the LLM touches is **text**: `.kicad_sch`, `.kicad_pcb`, KiCad
netlists, SimulIDE circuit XML, VCD waveforms, JSON. We **extend the
open-source tools' internal classes/APIs** to expose exactly the verbs the LLM
needs, each returning parseable text/JSON (spec §6.2). **GUI automation is
forbidden.**

## Consequences

- Positive: robust, scriptable, CI-able; human watches SimulIDE only when they
  want to ("vreau să văd și eu"), never required for progress.
- Trade-offs: SimulIDE needs a headless control entry point we must build.
- Follow-ups: build `llm/` command surface (T4) and the bridge (T3).

## Alternatives considered

- **GUI automation** — rejected: brittle, against the core requirement.
