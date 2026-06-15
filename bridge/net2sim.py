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

    # Layout = COMPACT grid that fits on one canvas view. Wires are drawn lines
    # routed directly pin→pin (overlap between wires is fine — SimulIDE has no
    # auto-router). CircId MUST be "<SimulIDE-part>-<uid>" (SimulIDE reads the TYPE
    # from the prefix); label=ref.
    pos = {}; pin_xy = {}; uid = 0
    A = 'mainComp="false" Show_id="true" rotation="0" hflip="1" vflip="1"'
    NCOL, SX, SY = 7, 200, 210
    x0, y0, col = -680, -360, 0
    for ref, c in sorted(comps.items()):
        m = PART_MAP.get(c["part"])
        px, py = x0 + (col % NCOL) * SX, y0 + (col // NCOL) * SY
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
            pass   # ROM/DRAM emitted once below as monolithic memory items

    # ROM + DRAM as single SimulIDE memory items, wired by NET NAME (per-chip
    # 27128/РУ5 pins are dropped — standard sim modeling). ROM = Memory (16Kx8),
    # DRAM = DynamicMemory (64Kx8, real RAS/CAS). NOTE: DRAM data is bidirectional on
    # out0-7 tied straight to the D bus — the board's DOUT→DD→D43 read-latch path is
    # not modeled. Load a ROM image in the GUI for the CPU to boot.
    # Full electrical attribute set the Memory/DynamicMemory components expect
    # (omitting these segfaults SimulIDE on load).
    ELEC = ('Show_Val="false" idLabPos="-16,-24" labelrot="0" valLabPos="-16,20" valLabRot="0" '
            'Input_High_V="2.5 V" Input_Low_V="2.5 V" Input_Imped="1e+09 Ω" '
            'Out_High_V="5 V" Out_Low_V="0 V" Out_Imped="40 Ω" Inverted="false" '
            'Open_Collector="false" pd_n="1 _Gates" Tpd_ps="10000 ps" Tr_ps="3000 ps" Tf_ps="4000 ps"')
    present = {c["part"] for c in comps.values()}
    netmap = {}
    for nm, eps in nets:
        netmap.setdefault(nm, []).extend(eps)
    def mem_attach(ref_, cid_, key, simpin, netname, mx, my):
        pin_id[(ref_, key)] = f"{cid_}-{simpin}"
        pin_xy[(ref_, key)] = (mx, my, 0)
        netmap.setdefault(netname, []).append((ref_, key))
    if "27128" in present:
        uid += 1; cid = f"Memory-{uid}"
        # preload a ZX-Spectrum-48K-compatible 16K ROM into the Memory's Mem= array
        # (SimulIDE stores contents as comma-separated signed int8). roms/sintez2.rom
        # is the José Leandro Sintez-M dump — verified ZX48 ROM (start DI/XOR A/JP $11CB,
        # IM1 handler at $0038, © glyph at the tail).
        romf = os.path.join(ROOT, "roms", "sintez-M.rom")
        memattr = ""
        if os.path.exists(romf):
            rb = open(romf, "rb").read()[:16384]
            mem = ",".join(str(b - 256 if b > 127 else b) for b in rb)
            memattr = f' Mem="{mem}"'
            warns.append(f"D36 ROM preloaded from roms/sintez2.rom ({len(rb)} bytes, ZX48-compatible)")
        items.append(f'<item itemtype="Memory" CircId="{cid}" {A} Pos="900,-360" label="D36 ROM(27128)" Address_Bits="14 _Bits" Data_Bits="8 _Bits" Persistent="true" Asynch="true"{memattr} {ELEC} />')
        for i in range(14): mem_attach("ROM", cid, f"in{i}",  f"in{i}",  f"A{i}", 900, -360 + i*8)
        for i in range(8):  mem_attach("ROM", cid, f"out{i}", f"out{i}", f"D{i}", 990, -360 + i*8)
        mem_attach("ROM", cid, "cs", "Pin_Cs",        "~ROMCS", 900, -392)
        mem_attach("ROM", cid, "oe", "Pin_outEnable", "~ROMOE", 900, -384)
        warns.append("D36 -> one Memory(16Kx8)")
    if "K565RU5" in present:
        uid += 1; cid = f"DynamicMemory-{uid}"
        items.append(f'<item itemtype="DynamicMemory" CircId="{cid}" {A} Pos="900,-120" label="DRAM 64Kx8(D28-35)" Row_Bits="8 _Bits" Column_Bits="8 _Bits" Data_Bits="8 _Bits" {ELEC} />')
        for i in range(8): mem_attach("DRAM", cid, f"in{i}",  f"in{i}",  f"VA{i}", 900, -120 + i*8)
        for i in range(8): mem_attach("DRAM", cid, f"out{i}", f"out{i}", f"D{i}", 990, -120 + i*8)
        mem_attach("DRAM", cid, "ras", "Pin_Ras", "~RAS", 900, -150)
        mem_attach("DRAM", cid, "cas", "Pin_Cas", "~CAS", 900, -142)
        mem_attach("DRAM", cid, "we",  "Pin_We",  "~WR",  900, -134)
        warns.append("D28-D35 -> one DynamicMemory(64Kx8); data out0-7 on the D bus (DD->D43 path not modeled)")
    nets = [(nm, eps) for nm, eps in netmap.items()]

    # Drawn wires: each net is a chain of pins joined by 3-pin Nodes at the net's
    # centroid, with direct straight pointLists. Compact; wires may cross each other
    # (fine — no auto-router in SimulIDE).
    nodes = []
    conns, nidx = [], 0
    def con(a, b, pts):
        nonlocal uid; uid += 1
        conns.append(f'<item itemtype="Connector" uid="con-{uid}" startpinid="{a}" endpinid="{b}" pointList="{pts}" />')
    for name, endpoints in nets:
        eps = [(r, p) for (r, p) in endpoints if pin_id.get((r, p))]
        if len(eps) < 2:
            continue
        sp = [pin_id[(r, p)] for (r, p) in eps]
        XY = [pin_xy[(r, p)][:2] for (r, p) in eps]
        if len(sp) == 2:
            con(sp[0], sp[1], f"{XY[0][0]},{XY[0][1]},{XY[1][0]},{XY[1][1]}"); continue
        n = len(sp)
        cx = sum(x for x, _ in XY) // n; cy = sum(y for _, y in XY) // n
        nd = []
        for k in range(n - 2):
            cid = f"Node-{nidx}"; nidx += 1; nd.append(cid)
            nodes.append(f'<item itemtype="Node" CircId="{cid}" mainComp="false" Pos="{cx+k*8},{cy}" />')
        con(sp[0], f"{nd[0]}-0", f"{XY[0][0]},{XY[0][1]},{cx},{cy}")
        for i in range(n - 2):
            con(f"{nd[i]}-1", sp[i+1], f"{cx+i*8},{cy},{XY[i+1][0]},{XY[i+1][1]}")
        for i in range(n - 3):
            con(f"{nd[i]}-2", f"{nd[i+1]}-0", f"{cx+i*8},{cy},{cx+(i+1)*8},{cy}")
        con(f"{nd[-1]}-2", sp[-1], f"{cx+(n-3)*8},{cy},{XY[-1][0]},{XY[-1][1]}")

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
