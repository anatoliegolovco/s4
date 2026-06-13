# Q: TV80 or A-Z80 for the simulation core?

- **Topic:** tooling ([index](./README.md))
- **Status:** open
- **Opened:** 2026-06-13T10:33:56Z
- **Resolved:** —
- **Decision:** —

## Context

Spec §4 / §5.4. A physical Z80 can't be co-simulated, so simulation always uses
a behavioral soft core. Two open-source candidates: **TV80**
(`github.com/hutch31/tv80`) and **A-Z80** (`github.com/gdevic/A-Z80`).

## Discussion

### 2026-06-13T10:33:56Z — claude

Opened from the spec. Selection criteria: ZEXDOC correctness, accurate
per-instruction T-states (FUSE suite), ease of integration into the SimulIDE
model, and clean reset/M1 timing for the verdict library (T4). A-Z80 is a
gate-level reconstruction (very accurate timing); TV80 is a compact synthesizable
core (easier to embed). Decision deferred until T3 integration trials.

## Outcome

<!-- pending integration trial in T3 -->
