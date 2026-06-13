# Q: Faithful К565РУ5 timing vs modern SRAM in hardware?

- **Topic:** architecture ([index](./README.md))
- **Status:** open
- **Opened:** 2026-06-13T10:33:56Z
- **Resolved:** —
- **Decision:** —

## Context

Spec §2.4 / §3 (Class 2) / §10.2. The Sintez WAIT generator was calibrated to
the *slow* Soviet К565РУ5 DRAM timing. A real recreation *may* legitimately
replace DRAM with modern SRAM + glue to drop refresh complexity in hardware —
but the **simulation model must keep РУ5 timing** for bug-for-bug fidelity.
The build target must be decided explicitly: faithful vs "improved & reliable."

## Discussion

### 2026-06-13T10:33:56Z — claude

Opened from the spec. Two separable choices:
1. **Hardware build:** keep DRAM (К565РУ5-equiv 4164) with refresh + WAIT gen,
   OR modernize to SRAM + glue (simpler, more reliable, less authentic).
2. **Simulation model:** MUST model real РУ5 timing (tRAS/tCAS/tRCD/precharge)
   regardless, and a fast-4164 swap must *change* the WAIT verdict (T5 proves
   timing-sensitivity). This part is already settled by decision 0004's
   fidelity stance.

Open part is the hardware target. Recommendation: support **both as build
targets** with the choice recorded per fabrication run; default to faithful
DRAM for the first board to validate the model end-to-end.

## Outcome

<!-- pending owner decision on hardware target -->
