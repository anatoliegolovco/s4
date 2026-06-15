#!/usr/bin/env python3
"""net2sim.py — KiCad netlist (from SKiDL) -> SimulIDE .sim1 circuit.

Canonical bridge direction (spec §7, milestone T3). Reads kicad/sintez2.net,
maps each component to a SimulIDE library item, and emits sim/circuits/sintez2.sim1
with one Node + Connectors per net so it loads and runs in SimulIDE.

Pin mapping:
  • 74xx ICs  -> Subcircuit; pin NUMBER -> pin id read from SimulIDE's .package file
                 (so it is exact for whatever SimulIDE part we point at).
  • Z80       -> the SimulIDE Z80 model, mapped by a fixed number->id table.
  • R / C     -> Resistor / Capacitor items.
  • Power     -> +5V net to a Rail, GND to Ground.
Family timing (К555 LS vs К1533 ALS) selects the _LS.package variant where present.

v0 scope: emits all parts it can map cleanly + their nets; ROM/DRAM (SimulIDE
built-in Memory items, pinned differently) and a few non-exact parts are reported
as TODO rather than mis-wired. Run:
    .venv/bin/python bridge/net2sim.py
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NET  = os.path.join(ROOT, "kicad", "sintez2.net")
OUT  = os.path.join(ROOT, "sim", "circuits", "sintez2.sim1")
SIM_DATA = os.path.expanduser(
    "~/.local/opt/simulide/SimulIDE_1.1.0-SR2_Lin64/data")

# SKiDL part name -> SimulIDE mapping.
#   kind: 'ic' (Subcircuit, .package-mapped), 'z80', 'mem', 'R', 'C', 'xtal'
#   sim : SimulIDE part folder name under data/ICs (for 'ic')
#   ls  : prefer the _LS.package (LS-family timing) when True
#   note: coverage caveat
PART_MAP = {
    "Z84C00":    {"kind": "z80"},
    "27128":     {"kind": "mem", "note": "ROM: SimulIDE Memory built-in (16Kx8) — pin-map TODO"},
    "K565RU5":   {"kind": "mem", "note": "DRAM РУ5 1-bit: behavioral model TODO (T5)"},
    "K1533TM2":  {"kind": "ic", "sim": "74HC74"},
    "K1533IE7":  {"kind": "ic", "sim": "74HC193"},
    "K1533KP11": {"kind": "ic", "sim": "74HC257"},
    "K1533KP12": {"kind": "ic", "sim": "74HC153", "note": "74HC153≈КП12 but non-tristate"},
    "K1533IR22": {"kind": "ic", "sim": "74HC373"},
    "K1533IR23": {"kind": "ic", "sim": "74HC374"},
    "KR1533IR27":{"kind": "ic", "sim": "74HC273"},
    "K1533AP3":  {"kind": "ic", "sim": "74XX244"},
    "K555IR16":  {"kind": "ic", "sim": "74XX166", "ls": True, "note": "74166 is 8-bit; ИР16 is 4-bit"},
    "K1533LN1":  {"kind": "ic", "sim": "74HC04"},
    "K1533LA3":  {"kind": "ic", "sim": "74HC00"},
    "K1533LA4":  {"kind": "ic", "sim": "74HC00", "note": "no 3-in NAND (74HC10) in lib; 74HC00 is 2-in — APPROX"},
    "K1533LI1":  {"kind": "ic", "sim": "74HC08"},
    "K1533LE1":  {"kind": "ic", "sim": "74HC02"},
    "R":         {"kind": "R"},
    "C":         {"kind": "C"},
    "Crystal":   {"kind": "xtal"},
}

# Z80 DIP-40 pin number -> SimulIDE Z80 model pin id (from data/Z80/Z80/Z80.package).
Z80_PINS = {
    1:"PA11",2:"PA12",3:"PA13",4:"PA14",5:"PA15",6:"CLK",7:"PD4",8:"PD3",9:"PD5",
    10:"PD6",11:"Vcc",12:"PD2",13:"PD7",14:"PD0",15:"PD1",16:"INT",17:"NMI",
    18:"HALT",19:"MREQ",20:"IORQ",21:"RD",22:"WR",23:"BUSAK",24:"WAIT",25:"BUSRQ",
    26:"RESET",27:"M1",28:"RFSH",29:"Gnd",30:"PA0",31:"PA1",32:"PA2",33:"PA3",
    34:"PA4",35:"PA5",36:"PA6",37:"PA7",38:"PA8",39:"PA9",40:"PA10",
}

def parse_netlist(path):
    t = open(path).read()
    comps = {}
    cseg = t[t.index("(components"):t.index("(libparts") if "(libparts" in t else t.index("(nets")]
    for b in re.split(r"\n    \(comp\b", cseg)[1:]:
        ref = re.search(r'\(ref "([^"]+)"\)', b)
        part = re.search(r'\(part "([^"]+)"\)', b)
        val = re.search(r'\(value "([^"]*)"\)', b)
        if ref and part:
            comps[ref.group(1)] = {"part": part.group(1), "value": val.group(1) if val else ""}
    nets = []
    nseg = t[t.index("(nets"):]
    for b in re.split(r"\n    \(net\n", nseg)[1:]:
        nm = re.search(r'\(name "([^"]+)"\)', b)
        nodes = re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', b)
        if nm:
            nets.append((nm.group(1), nodes))
    return comps, nets

def package_pinmap(simpart, ls):
    """Read SimulIDE .package -> {pin_number(str): pin_id}."""
    d = os.path.join(SIM_DATA, "ICs", simpart)
    f = os.path.join(d, f"{simpart}_LS.package" if ls else f"{simpart}.package")
    if not os.path.exists(f):
        f = os.path.join(d, f"{simpart}.package")
    if not os.path.exists(f):
        return None
    txt = open(f).read()
    m = {}
    for mm in re.finditer(r'id="([^"]+)"[^>]*?/>\s*<!--\s*packagePin(\d+)', txt):
        m[mm.group(2)] = mm.group(1)
    if not m:  # fallback: order of <pin> = pin 1..N
        for i, mm in enumerate(re.finditer(r'<pin\b[^>]*\bid="([^"]+)"', txt), 1):
            m[str(i)] = mm.group(1)
    return m

def main():
    comps, nets = parse_netlist(NET)
    items, warns = [], []
    pin_id = {}   # (ref, pinnum) -> SimulIDE "CircId-pinid", or None if skipped
    circid = {}   # ref -> CircId

    # place components on a grid
    x, y, col = -400, -300, 0
    for ref, c in sorted(comps.items()):
        m = PART_MAP.get(c["part"])
        cid = f"{ref}"
        circid[ref] = cid
        px, py = x + (col % 6) * 140, y + (col // 6) * 120
        col += 1
        if not m:
            warns.append(f"{ref}: no mapping for part '{c['part']}' — skipped")
            continue
        k = m["kind"]
        if k == "z80":
            items.append(f'<item itemtype="Subcircuit" CircId="{cid}" Pos="{px},{py}" label="{ref}" />')
            for num, pid in Z80_PINS.items():
                pin_id[(ref, str(num))] = f"{cid}-{pid}"
        elif k == "ic":
            pm = package_pinmap(m["sim"], m.get("ls", False))
            note = f" ({m['note']})" if m.get("note") else ""
            if not pm:
                warns.append(f"{ref}: package for '{m['sim']}' not found — skipped")
                continue
            items.append(f'<item itemtype="Subcircuit" CircId="{cid}" Pos="{px},{py}" label="{ref}={m["sim"]}" />')
            for num, pid in pm.items():
                pin_id[(ref, num)] = f"{cid}-{pid}"
            if note:
                warns.append(f"{ref}: mapped to {m['sim']}{note}")
        elif k in ("R", "C"):
            it = "Resistor" if k == "R" else "Capacitor"
            items.append(f'<item itemtype="{it}" CircId="{cid}" Pos="{px},{py}" label="{ref}" Value="{c["value"]}" />')
            pin_id[(ref, "1")] = f"{cid}-lPin"
            pin_id[(ref, "2")] = f"{cid}-rPin"
        elif k == "xtal":
            items.append(f'<item itemtype="Clock" CircId="{cid}" Pos="{px},{py}" label="{ref}" Freq="14000000 Hz" />')
            pin_id[(ref, "2")] = f"{cid}-outnod"
            warns.append(f"{ref}: crystal modeled as an ideal 14 MHz Clock source")
        elif k == "mem":
            warns.append(f"{ref}: {m.get('note','memory built-in')} — skipped in v0")

    # one Node + Connectors per net (only endpoints we could map)
    conns, nodes, uid, ni = [], [], 0, 0
    for name, endpoints in nets:
        pins = [pin_id.get((r, p)) for (r, p) in endpoints]
        pins = [p for p in pins if p]
        if len(pins) < 2:
            continue
        nodes.append(f'<item itemtype="Node" CircId="Node-{ni}" Pos="0,0" />')
        hub = f"Node-{ni}-0"; ni += 1
        for p in pins:
            uid += 1
            conns.append(f'<item itemtype="Connector" uid="con-{uid}" startpinid="{p}" endpinid="{hub}" pointList="0,0,0,0" />')

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write('<circuit version="1.1.0" rev="2221" stepSize="1000000" stepsPS="1000000" NLsteps="100000" reaStep="1000000" animate="1" >\n\n')
        for it in items: f.write(it + "\n")
        for nd in nodes: f.write(nd + "\n")
        for cn in conns: f.write(cn + "\n")
        f.write("\n</circuit>\n")

    print(f"wrote {OUT}")
    print(f"components: {len(comps)} | items emitted: {len(items)} | nets wired: {len(nodes)} | connectors: {len(conns)}")
    if warns:
        print("\nNOTES / coverage:")
        for w in warns: print("  -", w)

if __name__ == "__main__":
    main()
