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

### 2026-06-13T11:31:15Z — claude

New evidence: the owner supplied a ©1997 PREDATOR/FAST Group writeup,
**"Расширение памяти Синтеза-2 до 128 кб"** (`reference/photos/sintez128.jpg`),
documenting a real **128 KB expansion** for this exact machine via **port
`#7FFD` paging** (ZX-128 style). Mod chips: К555ТМ9 (≈74LS175 paging latch),
К1533КП11 (≈74ALS257 mux), К555ЛЛ1 (≈74LS32), К1533ЛА3 (≈74ALS00). This makes
128 KB the natural, historically-attested banked variant.

Refined recommendation: **48 K stock as the faithful baseline** (first build,
boot-to-`©` validation), with the **#7FFD 128 KB expansion as the documented
opt-in variant** modeled from this writeup. Decision still pending owner sign-off.

## Outcome

<!-- pending owner sign-off: 48K baseline + optional #7FFD 128K variant -->
