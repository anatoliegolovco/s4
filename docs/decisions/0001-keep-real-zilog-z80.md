# 0001 — Keep a genuine Zilog Z80 in the physical build

- **Status:** accepted
- **Date:** 2026-06-13
- **Deciders:** project owner (via spec)
- **Related question:** [sourcing/z80-part-selection](../ledger/sourcing/z80-part-selection.md)

## Context

The Sintez 2 is a discrete-TTL ZX Spectrum clone. The owner's first hard want
is a real Zilog Z80 on the fabricated board, not a soft core. The original used
a Soviet UA880D / КР1858ВМ1 Z80-compatible part.

## Decision

The physical build uses a **genuine modern CMOS Zilog Z80 (Z84C00 family)**.
In simulation, where a physical chip cannot be co-simulated, we use a
behavioral soft core (TV80 / A-Z80). An FPGA soft core is only a fallback if
a physical Z80 ever becomes unavailable.

## Consequences

- Positive: faithful to the machine; Z84C00 is in production and sourceable.
- Trade-offs: soft core in sim must match Z80 behavior (validated by ZEXDOC).
- Follow-ups: source Z84C00 (€3–5, Mouser/Digi-Key/TME) → see T8.

## Alternatives considered

- **Soviet КР1858ВМ1 / U880** — authentic but harder to source; kept as option.
- **Z180/Z280 with MMU** — rejected; changes the machine, owner wants Z80.
