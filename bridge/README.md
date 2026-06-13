# bridge — KiCad <-> SimulIDE converter

See `docs/spec/sintez2-recon-spec.md` §7 and milestone T3.

- `net2sim.py` — KiCad netlist (.net) -> SimulIDE circuit XML (canonical direction).
- `sim2net.py` — optional reverse.

Mapping is driven by `../parts_map.json`. (Skeleton — not yet implemented.)
