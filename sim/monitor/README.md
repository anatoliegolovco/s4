# sim/monitor — "monitor output" of the simulation (headless screenshot)

The Sintez-2 video hardware displays exactly the screen-RAM contents
(0x4000–0x57FF bitmap + 0x5800–0x5AFF attributes). So a connected monitor's image
can be reconstructed **zero-click, headless** by rendering that RAM — no SimulIDE
GUI, no screen capture needed.

`scr2png.py` renders a 6912-byte ZX screen dump to a colour PNG (ZX palette, ×3).

## Pipeline
```bash
tests/boot/boot                      # boots the ROM, dumps /tmp/s4work/screen.scr
.venv/bin/python sim/monitor/scr2png.py /tmp/s4work/screen.scr sim/monitor/boot-screen.png
```

## boot-screen.png — the reconstructed machine's video output at boot
Shows the ZX sign-on screen with **"© 1990 Intercomplex"** — the clone ROM in
`roms/sintez-M.rom`. This is the "monitor as if connected to our electronic
simulation" the project wants, produced from the simulated screen RAM.

## On SimulIDE extensibility (researched 2026-06-15)
- SimulIDE's scripting language is **AngelScript** (`.as` component scripts:
  `getPin()/getPort()/setVoltage()`, `setup()/reset()/voltChanged()` callbacks,
  RAM/ROM/interrupt access). Good for **behavioural** parts (e.g. a К565РУ5 DRAM
  model) — but scripted components **cannot draw graphics** ("custom draw" is only a
  forum feature-request).
- A true in-SimulIDE raster/CRT monitor would be a **C++ built-in/modular component**
  compiled into SimulIDE's (AGPL) source — the spec's "extend its classes" path.
- Until/unless that's built, this RAM→PNG renderer is the practical monitor view.
