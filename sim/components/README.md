# sim/components — SimulIDE behavioral component models

AngelScript (`.as`) behavioral models for the Sintez-2 custom / timing-critical
parts, loaded by SimulIDE 1.1.0 scripted components. See spec
`docs/spec/sintez2-recon-spec.md` §2.4 and decision
[0004](../../docs/decisions/0004-fidelity-no-memory-contention.md).

## Files

- `k565ru5.as` — К565РУ5 behavioral DRAM (≈ 4164, 64K × 1).

## SimulIDE AngelScript API used

Template: `…/SimulIDE_1.1.0-SR2_Lin64/data/scripted/DAC/dac_core.as` and the
MCS65 cores (`data/MCS65/6532/6532_core.as`, `6522_core.as`).

The global `component` object exposes the script's host component. Pins/ports
are fetched once at file scope:

| Call | Returns | Notes |
| --- | --- | --- |
| `component.getPin("Name")` | `IoPin@` | a single pin |
| `component.getPort("Name")` | `IoPort@` | a parallel bus (read as an int) |
| `component.addEvent(picoseconds)` | — | schedule a `runEvent()` callback after a delay; **unit is picoseconds** (the 6532 core uses `10000 // 10 ns`) |
| `component.addCpuReg/addCpuVar` | — | expose registers in the inspector (optional) |

Pin / port methods:

| Call | Meaning |
| --- | --- |
| `pin.setPinMode(mode)` | `undef=0, input=1, openCo=2, output=3, source=4` |
| `pin.setVoltage(v)` | drive an output pin (volts) |
| `pin.getVolt()` | read pin voltage (volts) |
| `pin.setOutState(bool)` / `getInpState()` | logic-level helpers |
| `port.getInpState()` | read the whole bus as an integer |
| `port.setOutState(int)` / `setPinMode(mode)` | drive / configure the bus |
| `pin.changeCallBack(element, true)` | register the pin so its transitions invoke `voltChanged()` |
| `port.changeCallBack(element, true)` | same, for a bus |

Script callbacks SimulIDE invokes:

| Callback | When |
| --- | --- |
| `setup()` | component created |
| `reset()` | simulation start — set pin modes, register callbacks |
| `voltChanged()` | any registered pin/port changed (re-sample levels yourself) |
| `runEvent()` | a previously scheduled `addEvent()` delay elapsed |
| `extClock(bool)` | clock-pin edge (clocked components only) |
| `getCpuReg/getStrReg` | inspector reads (optional) |

## К565РУ5 model (`k565ru5.as`)

64Ki × 1 dynamic RAM: 256 rows × 256 columns, multiplexed 8-bit address bus.

Pins expected on the package/subcircuit:

- `PORTA` — A0..A7 multiplexed address bus (input)
- `RAS` — /RAS row strobe (active-low, input)
- `CAS` — /CAS column strobe (active-low, input)
- `WE` — /WE write enable (active-low, input)
- `DIN` — data in (input)
- `DOUT` — data out (output, tri-state-ish: parked at 0 V when /CAS high)

Behavior:

- **RAS-before-CAS**: row address latched on **/RAS falling**, column latched on
  **/CAS falling**.
- **/WE low at /CAS fall ⇒ write** (early-write): DIN is sampled and stored.
- **/WE high ⇒ read**: the cell is fetched and driven on DOUT after the access
  delay.
- **/CAS-before-/RAS** (no row latched) is treated as a RAS-only / CBR
  **refresh** cycle — no data access, DOUT unchanged.
- **/CAS rising** disables the output (DOUT → 0 V) after `tOFF`.

### Timing — slow Soviet К565РУ5 (the point of the model)

Per `docs/datasheets/README.md` (РУ5 ≈ 4164 **−20 grade or slower**) and spec
§2.4 / decision 0004, the model reproduces the **slow** part. A fast 4164 must
change the WAIT verdict; do **not** swap in a generic fast 4164 / SRAM model.

| Param | Value | Meaning | Source |
| --- | --- | --- | --- |
| tRAC | 200 ns | access from /RAS (row-access read path) | datasheet −20 |
| tCAC | 100 ns | access from /CAS → DOUT valid | datasheet −20 |
| tRAS | 200 ns | min /RAS pulse width | datasheet −20 |
| tCAS | 100 ns | min /CAS pulse width | datasheet −20 |
| tRP | 120 ns | /RAS precharge | datasheet −20 |
| tOFF | 40 ns | /CAS rising → DOUT high-Z | model estimate |

`addEvent()` delays are in picoseconds (`NS = 1000`). A read drives DOUT after
`tRAC` on the first /CAS fall after /RAS (row-access path dominates), then
`tCAC` for subsequent page-mode-style accesses within the same /RAS.

> Exact tRAC/tCAC from the original РУ5 ТУ are **(to confirm)** — datasheet notes
> quote ~200–230 ns access; the −20-grade 200 ns / 100 ns figures are used as the
> slow baseline. `tRAS`, `tCAS`, `tRP` are also used as documented bounds; the
> WAIT generator on the real board enforces precharge/pulse-width spacing.
