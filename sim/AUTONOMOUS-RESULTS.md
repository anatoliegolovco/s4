# Autonomous workflow results (2026-06-16)

Fan-out workflow (16 agents, build + adversarial verify). Raw: `schematics/sources/autonomous-2026-06-16/result.json`.

## ngspice analog (sim/spice/)
| deck | verify | result |
| --- | --- | --- |
| clock_osc.cir | ✅ CONFIRMED | /4 ripple divider → 7 MHz dot / 3.5 MHz CPU; quartz AC-resonance 14.000 MHz (motional params = documented 14 MHz AT-cut typicals). |
| rgb_ladder_full.cir | ✅ CONFIRMED (caveat) | 8 distinct levels 0→0.718 V into 75 Ω; full-white ~0.72 V ≈ 0.7 Vpp std. Ladder NET topology = standard ZX diode-OR DAC (values exact, exact wiring TODO). |
| wait_gen.cir | ⚠ DISPUTED | WAIT ≈ 307 ns, SAFE vs РУ5 (200-230 ns), verdict CHANGES for fast-4164 (timing-sensitive, decision 0004). BUT the /CAS R13/R14/C4 network + 1-Tclk count are ASSUMED, not pin-traced. |

## К565РУ5 behavioral model (sim/components/k565ru5.as)
SimulIDE AngelScript: RAS-before-CAS, row/col latch, /WE early-write, DOUT after tCAC;
РУ5 slow timing (tRAC 200 / tCAC 100 / tRP 120 ns). **Fixed** the verifier-found bug
(`getVolt()` → `getInpState()`, the real SimulIDE 1.1 IoPin logic read). Needs GUI run to validate.

## Net traces (→ folded into wiring.json)
- **arbitration (crown jewel) ✅ CONFIRMED high-conf** — D5 КП11 makes K8-K12 from V-counters;
  D23-D26 КП12 screen-address mux DATA inputs fully resolved (only the A/B select + OE0 =
  arbitration timing remain ambiguous). The previously-unresolvable block.
- **ROM decode ✅ CONFIRMED** — real chain D22A NOR(A14,A15) → D9E → D27C NAND → ROM /CE
  (not the earlier functional D17 guess); D26 КП12 = A14/A15 paging.
- **sync flip-flops ⚠** — D16A/D16B/D8B traced (one error corrected by verify); some
  set/reset wraps still unresolved.

## Family timing (→ for net2sim)
ALS(К1533) Tpd 4 ns / LS(К555) 15 ns / CMOS(К561) 50 ns; **К555ИР16 forced LS (NOT ALS),
tpd ~27 ns, tsu ~22 ns** — the deliberate setup-margin choice (spec §3). ✅ verified.
