# 0002 — KiCad is the source of truth for the PCB

- **Status:** accepted
- **Date:** 2026-06-13
- **Deciders:** project owner (via spec)
- **Related question:** [tooling/schematic-automation-strategy](../ledger/tooling/schematic-automation-strategy.md)

## Context

The board is fabricated by ordering from Gerbers. SimulIDE — the visual
playground — has no PCB/Gerber export. We need one canonical design that
produces the fab outputs.

## Decision

**KiCad is the single canonical design and the source of truth for the PCB.**
Gerbers/drill/BOM are produced from KiCad. SimulIDE circuits are *generated
from* the KiCad netlist via the bridge (`bridge/net2sim.py`), never the other
way around for fabrication purposes.

## Consequences

- Positive: no "export to KiCad" step; fabrication is automatic from the hub.
- Trade-offs: KiCad's digital-logic visualization is weak → hence SimulIDE +
  the bridge (decision 0003 / spec §7).
- Follow-ups: keep `parts_map.json` as the mapping that drives the bridge.

## Alternatives considered

- **Draft in SimulIDE, import to KiCad** — allowed as optional reverse path,
  but KiCad remains authoritative for the PCB.
