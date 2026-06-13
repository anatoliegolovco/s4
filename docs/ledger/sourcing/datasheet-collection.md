# Q: Where are the datasheets and key parameters for each part?

- **Topic:** sourcing ([index](./README.md))
- **Status:** resolved (living document — extend as parts are modeled)
- **Opened:** 2026-06-13T11:16:51Z
- **Resolved:** 2026-06-13T11:32:00Z
- **Decision:** —

## Context

The substitution guide (spec §3) and the DRAM/shift-register timing models
(T5/T6) need real datasheet numbers. The owner asked to collect datasheets via
web search.

## Discussion

### 2026-06-13T11:16:51Z — user

Instruction: web-search and collect datasheets.

### 2026-06-13T11:32:00Z — claude

Collected datasheets and key parameters into
[`docs/datasheets/README.md`](../../datasheets/README.md). Confirmed:

- **КТ315Г/КТ361Г** — hFE≥50, Vce 35 V, Ic 100/50 mA, ft 250 MHz.
- **К1533ИЕ7 = SN74ALS193** (4-bit up/down counter).
- **КП12 (КР1533КП12) = SN74ALS253** (dual 4:1 mux, 3-state) — corrects the
  spec's loose "bus multiplexer" wording.
- **К555ИР16 = 74LS165** — keep LS timing (~20 ns setup), fmax ≥25 MHz.
- **К565РУ5 = 4164** — standard −15/−20 timing tabulated; РУ5 baseline is the
  slow (−20 or slower) grade; exact ТУ tRAC marked _to confirm_.
- **Z84C00**, **LM567 (К5545АЗ)** datasheet links recorded.

Note: a delegated research sub-agent returned without synthesizing, so the
numbers were gathered directly. PDF fetches were often blocked (403 / binary);
HTML sources and search snippets were used, with uncertain values flagged
_(to confirm)_ rather than invented.

## Outcome

`docs/datasheets/README.md` is the datasheet index; confirmed values flowed into
`parts_map.json` (v1). Remaining: confirm К565РУ5 ТУ timing and 74LS165
hold/tpd from primary PDFs during T5/T6.
