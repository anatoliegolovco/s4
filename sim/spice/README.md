# sim/spice — analog corner validation (ngspice)

Batch SPICE decks (`ngspice -b *.cir`) validating the analog parts of the Sintez-2
that digital simulation can't (spec §5.3). Run, e.g.:

```bash
ngspice -b sim/spice/psu_mod.cir
```

## psu_mod.cir — the factory 39 Ω GND-lift mod ✅ VALIDATED

The unit had a 39 Ω resistor between the LM7805 GND pin and ground; the repair video
measured **~5.35 V** no-load. A 78xx regulates 5 V between OUT and its GND pin, and
its ground-pin current `Ignd` flows through that resistor: **Vout = 5 + Ignd·Rgnd**.

| Ignd | Vout (39 Ω, factory) | Vout (39‖15 = 10.6 Ω, repair) |
| --- | --- | --- |
| 4.3 mA (typ) | 5.17 V | 5.05 V |
| 6 mA | 5.23 V | 5.06 V |
| 8 mA | 5.31 V | 5.08 V |
| 9 mA | **5.35 V** | 5.10 V |

**Result:** the measured 5.35 V corresponds to Ignd ≈ 9 mA — exactly the documented
behavior. The 15 Ω parallel repair pulls Vout back to ~5.05–5.10 V (near nominal,
effect reduced but not removed — matches the video). Mechanism confirmed quantitatively.

## rgb_level.cir — RGB output levels (КТ315 follower) ✅ representative

One colour channel: TTL colour + BRIGHT bits → resistor DAC → КТ315 emitter follower
→ 75 Ω TV/SCART input. Validates distinct, monotonic levels and that the КТ315
(Vbe/hFE) sets them (spec class-4: 2N3904/BC237 would shift the levels).

| State | Vout into 75 Ω |
| --- | --- |
| OFF | ~0 V |
| NORMAL | 0.96 V |
| NORMAL + BRIGHT | 1.37 V |

**Result:** normal vs bright are cleanly separated → the analog levels are real and
КТ315-dependent. ⚠ Weights here are representative (R48 620, R49 1.8k, R43 33k);
the exact per-board ladder topology is still to be traced
(`docs/references/validation-trace-verify-2026-06-14.md`), after which this deck
becomes the board-exact RGB model (milestone T6).

## Not modeled here
- **14 MHz crystal oscillator** — high-Q crystal start-up is impractical in plain
  transient SPICE; treat the clock as an ideal source in the digital/SimulIDE model.
- **К565РУ5 DRAM RAS/CAS timing** — behavioral, belongs in the SimulIDE model (T5).
