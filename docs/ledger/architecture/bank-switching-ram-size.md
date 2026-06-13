# Q: How much RAM / what bank-switching scheme?

- **Topic:** architecture ([index](./README.md))
- **Status:** open
- **Opened:** 2026-06-13T10:33:56Z
- **Resolved:** —
- **Decision:** —

## Context

Spec §2.2. The Z80 natively addresses 64 KB. The stock 48K layout is the
baseline. If the modern build wants more RAM, it is paged through a window via
latches/registers holding a wider bank address. 128–512 KB is typical; >1 MB is
possible but software-impractical.

## Discussion

### 2026-06-13T10:33:56Z — claude

Opened from the spec. Baseline = stock 48K (no banking) to reach the `©` boot
and run standard software. Optional extension: 128 KB (ZX-128-like paging) or
more. Recommendation: ship **48K faithful first**; treat banked RAM as an
opt-in later variant so it doesn't complicate the initial fidelity validation.

## Outcome

<!-- pending; default to 48K for the first build -->
