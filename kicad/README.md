# kicad — canonical project (source of truth for the PCB)

See `docs/spec/sintez2-recon-spec.md` §5.1 and milestones T2/T8.
Gerbers ordered from here. The LLM mostly edits `.kicad_sch` as text and uses
`kicad-cli` for ERC/DRC/netlist/Gerber export (IPC API is PCB-only in 9.0).

(Skeleton — no project authored yet.)

## T8 — PCB (in progress)

The PCB is seeded from the SKiDL netlist (no hand layout):
```bash
# 1. netlist -> board with all footprints (run once to seed)
PYTHONPATH=/usr/lib/python3/dist-packages KICAD9_FOOTPRINT_DIR=/usr/share/kicad/footprints \
  .venv/bin/kinet2pcb -i kicad/sintez2.net -o kicad/sintez2.kicad_pcb -w
# 2. spread footprints + add board outline
PYTHONPATH=/usr/lib/python3/dist-packages python3 kicad/place_board.py
# 3. fab outputs
kicad-cli pcb export gerbers -o kicad/gerbers/ kicad/sintez2.kicad_pcb
kicad-cli pcb export drill   -o kicad/gerbers/ kicad/sintez2.kicad_pcb
```
**Status:** `kicad/sintez2.kicad_pcb` has all 85 footprints placed on a 9×10 grid
(337×320 mm) with an Edge.Cuts outline; Gerber + drill export verified (26 files).
DRC: 23 courtyard/silk overlaps + 421 unconnected pads = **not routed yet**.
**Next:** tighten placement by block; route (manual or Freerouting .dsn/.ses);
then DRC-clean + final Gerbers/BOM. `kicad/sintez2.kicad_pcb` is the layout source
of truth — do NOT re-run kinet2pcb once routing starts (it overwrites the board).
