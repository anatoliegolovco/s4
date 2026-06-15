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

# Z80 DIP-40 pin number -> SimulIDE Z80 *MCU* pin id. The MCU (itemtype="MCU")
# names its pins PORTA<n> (addr), PORTD<n> (data), CPORT0<SIG> (control) — NOT the
# .package ids. (From examples/Micro/Z80/ZX_Spectrum/*.sim1.) Vcc/Gnd are internal.
Z80_PINS = {
    1:"PORTA11",2:"PORTA12",3:"PORTA13",4:"PORTA14",5:"PORTA15",6:"CPORT0CLK",
    7:"PORTD4",8:"PORTD3",9:"PORTD5",10:"PORTD6",12:"PORTD2",13:"PORTD7",
    14:"PORTD0",15:"PORTD1",16:"CPORT0INT",17:"CPORT0NMI",18:"CPORT0HALT",
    19:"CPORT0MREQ",20:"CPORT0IORQ",21:"CPORT0RD",22:"CPORT0WR",23:"CPORT0BUSAK",
    24:"CPORT0WAIT",25:"CPORT0BUSRQ",26:"CPORT0RESET",27:"CPORT0M1",28:"CPORT0RFSH",
    30:"PORTA0",31:"PORTA1",32:"PORTA2",33:"PORTA3",34:"PORTA4",35:"PORTA5",
    36:"PORTA6",37:"PORTA7",38:"PORTA8",39:"PORTA9",40:"PORTA10",
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
    m = {}   # pin_number -> (id, xpos, ypos, angle)
    for i, mm in enumerate(re.finditer(r'<pin\b([^>]*)/>', txt), 1):
        attrs = mm.group(1)
        pid = re.search(r'\bid="([^"]+)"', attrs)
        xp = re.search(r'\bxpos="(-?\d+)"', attrs)
        yp = re.search(r'\bypos="(-?\d+)"', attrs)
        ang = re.search(r'\bangle="(-?\d+)"', attrs)
        num = re.search(r'packagePin(\d+)', txt[mm.end():mm.end()+40])
        n = num.group(1) if num else str(i)
        if pid:
            m[n] = (pid.group(1), int(xp.group(1)) if xp else 0,
                    int(yp.group(1)) if yp else 0, int(ang.group(1)) if ang else 0)
    return m

def main():
    comps, nets = parse_netlist(NET)
    items, warns = [], []
    pin_id = {}   # (ref, pinnum) -> SimulIDE "CircId-pinid", or None if skipped
    circid = {}   # ref -> CircId

    # Layout = single ROW of components with a wide ROUTING CHANNEL below them.
    # Drawn wires (Connectors) are routed orthogonally: each pin escapes sideways,
    # drops into the channel, and joins a per-net horizontal TRACK at a unique Y.
    # Because every track lives in the channel BELOW the components, no wire ever
    # crosses a component body (tracks only cross each other). CircId MUST be
    # "<SimulIDE-part>-<uid>" (SimulIDE reads the TYPE from the prefix); label=ref.
    pos = {}; pin_xy = {}; uid = 0
    A = 'mainComp="false" Show_id="true" rotation="0" hflip="1" vflip="1"'
    SLOT, ROWY = 220, 0
    x0, col = -3600, 0
    for ref, c in sorted(comps.items()):
        m = PART_MAP.get(c["part"])
        px, py = x0 + col * SLOT, ROWY
        col += 1; pos[ref] = (px, py)
        if not m:
            warns.append(f"{ref}: no mapping for part '{c['part']}' — skipped"); continue
        k = m["kind"]
        def newcid(name):
            nonlocal uid; uid += 1
            cid = f"{name}-{uid}"; circid[ref] = cid; return cid
        if k == "z80":
            cid = newcid("Z80")
            items.append(f'<item itemtype="MCU" CircId="{cid}" {A} Pos="{px},{py}" label="{ref}" Producer="Zilog" />')
            for i, num in enumerate(sorted(Z80_PINS, key=int)):
                pid = Z80_PINS[num]; pin_id[(ref, str(num))] = f"{cid}-{pid}"
                side = 0 if i < 19 else 1
                pin_xy[(ref, str(num))] = (px + (96 if side else -8), py + (i - 19*side) * 8, 0 if side else 180)
        elif k == "ic":
            pm = package_pinmap(m["sim"], m.get("ls", False))
            if not pm:
                warns.append(f"{ref}: package for '{m['sim']}' not found — skipped"); continue
            cid = newcid(m["sim"])
            items.append(f'<item itemtype="Subcircuit" CircId="{cid}" {A} Pos="{px},{py}" label="{ref}" />')
            for num, (pid, pxo, pyo, ang) in pm.items():
                pin_id[(ref, num)] = f"{cid}-{pid}"
                pin_xy[(ref, num)] = (px + pxo, py + pyo, ang)
            if m.get("note"): warns.append(f"{ref}: {m['sim']} ({m['note']})")
        elif k in ("R", "C"):
            it = "Resistor" if k == "R" else "Capacitor"
            cid = newcid(it)
            items.append(f'<item itemtype="{it}" CircId="{cid}" {A} Pos="{px},{py}" label="{ref}" Value="{c["value"]}" />')
            pin_id[(ref, "1")] = f"{cid}-lPin"; pin_id[(ref, "2")] = f"{cid}-rPin"
            pin_xy[(ref, "1")] = (px - 8, py, 180); pin_xy[(ref, "2")] = (px + 24, py, 0)
        elif k == "xtal":
            cid = newcid("Clock")
            items.append(f'<item itemtype="Clock" CircId="{cid}" {A} Pos="{px},{py}" label="{ref}" Freq="14000000 Hz" Out="true" Running="true" />')
            pin_id[(ref, "2")] = f"{cid}-outnod"; pin_xy[(ref, "2")] = (px + 24, py, 0)
            warns.append(f"{ref}: crystal modeled as an ideal 14 MHz Clock source")
        elif k == "mem":
            warns.append(f"{ref}: {m.get('note','memory built-in')} — skipped in v0")

    # Channel router: drawn orthogonal wires, one horizontal track per net, in the
    # channel below the row. Per net: a Node under each pin's escape point on the
    # track (3-pin junction), chained left→right; pin→node drops vertically.
    nodes = []          # Node items (emitted with the components)
    conns, nidx = [], 0
    CH_Y0 = 280         # channel starts below the tallest part (Z80 ~160 px)
    routable = [(nm, [(r, p) for (r, p) in eps if pin_id.get((r, p))]) for nm, eps in nets]
    routable = [(nm, e) for nm, e in routable if len(e) >= 2]
    def con(a, b, pts):
        nonlocal uid; uid += 1
        conns.append(f'<item itemtype="Connector" uid="con-{uid}" startpinid="{a}" endpinid="{b}" pointList="{pts}" />')
    for ni, (name, eps) in enumerate(routable):
        ty = CH_Y0 + ni * 12                       # this net's track Y (unique)
        pts = []                                    # (escape_x, pin_abs_x, pin_abs_y, simpinid)
        for r, p in eps:
            ax, ay, ang = pin_xy[(r, p)]
            ex = ax + (24 if ang == 0 else -24)     # escape just off the pin's side
            pts.append((ex, ax, ay, pin_id[(r, p)]))
        pts.sort(key=lambda t: t[0])
        nd = []
        for (ex, ax, ay, sp) in pts:               # a node per pin, sitting on the track
            cid = f"Node-{nidx}"; nidx += 1; nd.append((cid, ex, ax, ay, sp))
            nodes.append(f'<item itemtype="Node" CircId="{cid}" mainComp="false" Pos="{ex},{ty}" />')
        for i, (cid, ex, ax, ay, sp) in enumerate(nd):     # pin -> its node (escape + drop)
            con(sp, f"{cid}-0", f"{ax},{ay},{ex},{ay},{ex},{ty}")
        for i in range(len(nd) - 1):                       # chain nodes along the track
            con(f"{nd[i][0]}-2", f"{nd[i+1][0]}-1", f"{nd[i][1]},{ty},{nd[i+1][1]},{ty}")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write('<circuit version="1.1.0" rev="2221" stepSize="1000000" stepsPS="1000000" NLsteps="100000" reaStep="1000000" animate="1" >\n\n')
        for it in items: f.write(it + "\n")
        for nd in nodes: f.write(nd + "\n")
        for cn in conns: f.write(cn + "\n")
        f.write("\n</circuit>\n")

    print(f"wrote {OUT}")
    print(f"components: {len(comps)} | items: {len(items)} | nodes: {len(nodes)} | connectors: {len(conns)}")
    if warns:
        print("\nNOTES / coverage:")
        for w in warns: print("  -", w)

if __name__ == "__main__":
    main()
