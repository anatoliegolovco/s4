# Q: Which Z80 part for the physical build?

- **Topic:** sourcing ([index](./README.md))
- **Status:** open
- **Opened:** 2026-06-13T10:33:56Z
- **Resolved:** —
- **Decision:** [0001](../../decisions/0001-keep-real-zilog-z80.md) (keep a real Z80)

## Context

Spec §4. Decision 0001 mandates a genuine Z80. Which exact part to buy, and
shipping to Moldova, is still open.

## Discussion

### 2026-06-13T10:33:56Z — claude

Candidates from the spec:

| Part | What | Notes |
| --- | --- | --- |
| **Zilog Z84C00** (e.g. Z84C0020) | Genuine modern CMOS Z80, in production | €3–5 Mouser/Digi-Key/TME; ships to Moldova; **recommended default** |
| КР1858ВМ1 / КР1858ВМ3 | Soviet NMOS/CMOS clone | eBay/au.ru; shipping restrictions vary |
| U880 / UB880D | East German (MME) clone | eBay; often easier to find |
| MMN 80 CPU | Romanian clone | from Romania (EU neighbor) |
| MME "80A CPU" | Z80A 4 MHz NMOS clone | ~$10 + shipping from Ukraine |

Recommendation: **Z84C00** as default (in production, sourceable, ships to MD).
Buy 2–3 for spares. FPGA soft core (TV80/A-Z80 on iCE40/Gowin) is the fallback
only if physical Z80s become unavailable.

## Outcome

<!-- pending purchase at T8 -->
