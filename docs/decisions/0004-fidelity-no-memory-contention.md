# 0004 — Fidelity over improvement: no memory contention

- **Status:** accepted
- **Date:** 2026-06-13
- **Deciders:** project owner (via spec)
- **Related question:** [architecture/dram-faithful-vs-improved](../ledger/architecture/dram-faithful-vs-improved.md)

## Context

A real Spectrum's ULA disputes the bus, causing memory contention. The Sintez 2
has **no ULA** (all discrete TTL), so there is **no memory contention** — the
Z80 runs a constant 3.5 MHz with canonical T-states. This is the single most
important behavioral fact about the machine.

## Decision

The model is **faithful, not "improved."** It uses canonical T-state counts
with **no contention table**. Software depending on tight contention timing
(multicolor demos, Nirvana, rainbow-border) **must not run** in our model, just
as it does not on real hardware. The validation bar is **ZEXDOC + boots to the
`©` prompt**. Patrik Rak contention tests are **N/A and must NOT pass** —
passing them means the model is a wrong machine.

## Consequences

- Positive: bug-for-bug fidelity to the actual Sintez 2.
- Trade-offs: some famous ZX demos won't run — this is correct, not a defect.
- Follow-ups: DRAM timing model keeps real К565РУ5 timing (T5); document the
  faithful-vs-improved hardware target separately (see related question).

## Alternatives considered

- **Add contention for broader software compat** — rejected: wrong machine.
