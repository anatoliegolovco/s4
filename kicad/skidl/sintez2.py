"""Sintez-2 mainboard — canonical design authored in SKiDL (text -> KiCad netlist).

Source of truth for the PCB per decision 0002: this Python generates the KiCad
netlist (-> Pcbnew -> Gerbers) and feeds bridge/net2sim.py for SimulIDE.

Incremental, block by block (spec §8 milestones T2/T3). Run:
    .venv/bin/python kicad/skidl/sintez2.py
Outputs kicad/sintez2.net and prints the ERC summary.

STATUS: blocks 1-2 of N — CPU + clock + reset + pull-ups (D6, Z1, D1, RC); ROM
(D36 27128) wired to the address/data buses + power. ROM /CE,/OE and the CPU CLK
are named nets driven by decode/divider sub-blocks still to be traced. Bus pins
without a second endpoint yet read as unconnected in ERC (expected).
"""

import os
# make netlistsvg (npm, under nvm) findable for generate_svg()
_node_bin = os.path.expanduser("~/.nvm/versions/node/v22.16.0/bin")
if os.path.isdir(_node_bin):
    os.environ["PATH"] = _node_bin + os.pathsep + os.environ.get("PATH", "")

from skidl import Net, generate_netlist, generate_svg, ERC
import sintez_parts as P

HERE = os.path.dirname(os.path.abspath(__file__))
NETLIST = os.path.join(HERE, "..", "sintez2.net")
SVG = os.path.join(HERE, "sintez2")   # generate_svg appends .svg

# ---- power rails -----------------------------------------------------------
vcc = Net("+5V");  vcc.drive = 7      # POWER drive so ERC is satisfied
gnd = Net("GND");  gnd.drive = 7

# ---- canonical buses (grow as blocks are added) ----------------------------
A = [Net(f"A{i}") for i in range(16)]      # CPU address bus A0..A15
D = [Net(f"D{i}") for i in range(8)]       # data bus D0..D7

# ---- CPU (D6) --------------------------------------------------------------
cpu = P.Z80(ref="D6")
cpu["VCC"] += vcc
cpu["GND"] += gnd
for i in range(16):
    cpu[f"A{i}"] += A[i]
for i in range(8):
    cpu[f"D{i}"] += D[i]

# control signals as named nets (consumed by decode/DRAM/video blocks later)
MREQ, IORQ, RD, WR, M1, RFSH = (Net(n) for n in ("~MREQ", "~IORQ", "~RD", "~WR", "~M1", "~RFSH"))
cpu["~MREQ"] += MREQ; cpu["~IORQ"] += IORQ; cpu["~RD"] += RD
cpu["~WR"]  += WR;   cpu["~M1"]  += M1;   cpu["~RFSH"] += RFSH

clk_cpu  = Net("CLK")        # 3.5 MHz, driven by the /4 divider (video-sync block)
reset_n  = Net("~RESET")
int_n, nmi_n, busrq_n, wait_n = (Net(n) for n in ("~INT", "~NMI", "~BUSRQ", "~WAIT"))
cpu["CLK"] += clk_cpu
cpu["~RESET"] += reset_n
cpu["~INT"] += int_n; cpu["~NMI"] += nmi_n
cpu["~BUSRQ"] += busrq_n; cpu["~WAIT"] += wait_n

# ---- ROM (D36) — 27128 16Kx8 EPROM, stock 48K Spectrum ROM -----------------
# Read mode: VPP=PGM=VCC. /CE from address decode (ROM region 0x0000-0x3FFF),
# /OE from the gated read strobe — both driven by the decode sub-block (TODO),
# kept as named nets here (same pattern as CLK in block 1).
rom = P.ROM27128(ref="D36")
rom["VCC"] += vcc; rom["GND"] += gnd
rom["VPP"] += vcc; rom["PGM"] += vcc
for i in range(14):
    rom[f"A{i}"] += A[i]          # ROM A0..A13 <- CPU address bus
for i in range(8):
    rom[f"D{i}"] += D[i]          # ROM data <-> data bus
rom_ce_n = Net("~ROMCS")          # <- decode: A14·A15·/MREQ (ROM at 0x0000-3FFF)
rom_oe_n = Net("~ROMOE")          # <- gated /RD
rom["~CE"] += rom_ce_n
rom["~OE"] += rom_oe_n

# ---- block 2b: ROM address decode -----------------------------------------
# FUNCTIONAL decode (48K-compatible: ROM occupies 0x0000-0x3FFF, i.e. A14=A15=0):
#   ~ROMCS = NAND( (A14 NOR A15) , NOT/MREQ )   -> low only on a memory access
#            in the low 16K.
#   ROM /OE = /RD (output enabled while the CPU reads).
# Uses the real decode-gate types present on the board (D22 ЛЕ1, D9 ЛН1, D17 ЛА3).
# CONFIDENCE: the LOGIC is correct for a Spectrum-compatible map; the exact
# gate-SECTION assignment (which D22/D9/D17 section, which pins) is to be verified
# pin-by-pin against the scan — see schematics/wiring.json decode TODO.
d22 = P.K1533LE1(ref="D22"); d22["VCC"] += vcc; d22["GND"] += gnd
d9  = P.K1533LN1(ref="D9");  d9["VCC"]  += vcc; d9["GND"]  += gnd
d17 = P.K1533LA3(ref="D17"); d17["VCC"] += vcc; d17["GND"] += gnd

rom_region = Net("ROM_REGION")     # high when A14=A15=0 (low 16K)
mreq_h     = Net("MREQ_H")         # active-high copy of /MREQ
d22["1A"] += A[14]; d22["1B"] += A[15]; d22["1Y"] += rom_region   # NOR
d9["1A"]  += MREQ;  d9["1Y"]  += mreq_h                           # inverter
d17["1A"] += rom_region; d17["1B"] += mreq_h; d17["1Y"] += rom_ce_n  # NAND -> ~ROMCS
RD += rom_oe_n                     # ROM /OE follows CPU /RD

# ---- block 3: DRAM array (D28-D35 К565РУ5) + /RAS/CAS (D13) ----------------
# 8x К565РУ5 (4164), 1 bit each = 64 KB. All chips share the multiplexed address
# bus VA0-VA7, /RAS, /CAS, /WE; they differ only in DIN/DOUT (one data bit each).
# Address-pin -> VA-net map is the one extracted into schematics/wiring.json
# (dram_addr_map, from the colour tile gap_bot_center).
VA = [Net(f"VA{i}") for i in range(8)]     # multiplexed row/col addr (driven by D24/D25 КП12, block 4)
DD = [Net(f"DD{i}") for i in range(8)]     # DRAM data-out -> D43 latch (block 6)
ras_n = Net("~RAS"); cas_n = Net("~CAS"); we_n = Net("~WE")

# Per-chip address pin (by its schematic A-label) -> VA net:
ADDR_MAP = {"A0": 7, "A1": 5, "A2": 1, "A3": 4, "A4": 2, "A5": 3, "A6": 0, "A7": 6}

for bit in range(8):
    ru = P.K565RU5(ref=f"D{28 + bit}")
    ru["VCC"] += vcc; ru["GND"] += gnd
    ru["~RAS"] += ras_n; ru["~CAS"] += cas_n; ru["~WE"] += we_n
    for apin, va in ADDR_MAP.items():
        ru[apin] += VA[va]
    ru["DIN"]  += D[bit]      # CPU data bus -> DRAM (write path)
    ru["DOUT"] += DD[bit]     # DRAM -> read latch D43 (block 6)

# /WE follows the CPU write strobe (functional; gating to verify vs scan).
WR += we_n

# D13 К1533ЛИ1 (AND) generates /RAS and /CAS from the memory-cycle timing strobes
# (R15 470 + C5 set the RAS->CAS delay). Timing-strobe inputs come from the
# arbitration/sync block (block 4/5) — named nets for now. FUNCTIONAL.
d13 = P.K1533LI1(ref="D13"); d13["VCC"] += vcc; d13["GND"] += gnd
ras_stb = Net("RAS_STB"); cas_stb = Net("CAS_STB"); mem_stb = Net("MEM_STB")
d13["2A"] += mem_stb; d13["2B"] += ras_stb; d13["2Y"] += ras_n   # -> /RAS
d13["3A"] += mem_stb; d13["3B"] += cas_stb; d13["3Y"] += cas_n   # -> /CAS

# ---- block 4: bus arbitration — the "crown jewel" (PARTIAL) ----------------
# D23/D24/D25 КП12 mux CPU address vs video-fetch address onto VA0-VA5 (each dual
# 4:1 mux drives 2 VA bits; selects pick {row|col} x {CPU|video}). D5 КП12 makes
# the video-fetch address K8-K12 from the V-counters; D26 КП12 is the A14/A15
# paging mux; D38 ИР27 latches the row/RAM address.
#
# HONEST SCOPE: only the parts I can map with confidence are wired here — the mux
# OUTPUTS -> VA (per schematics/wiring.json) and power. The detailed DATA-INPUT
# mapping (which CPU/screen-address bit feeds which 4:1 input, and the exact
# select/enable timing) is the screen-address generator — the most intricate logic
# on the board. It must be traced pin-by-pin from the scan before it is trustworthy,
# so it is deliberately left as a dedicated task rather than guessed here.
d5  = P.K1533KP12(ref="D5");  d5["VCC"]  += vcc; d5["GND"]  += gnd
d23 = P.K1533KP12(ref="D23"); d23["VCC"] += vcc; d23["GND"] += gnd
d24 = P.K1533KP12(ref="D24"); d24["VCC"] += vcc; d24["GND"] += gnd
d25 = P.K1533KP12(ref="D25"); d25["VCC"] += vcc; d25["GND"] += gnd
d26 = P.K1533KP12(ref="D26"); d26["VCC"] += vcc; d26["GND"] += gnd
d38 = P.KR1533IR27(ref="D38"); d38["VCC"] += vcc; d38["GND"] += gnd

# Confident: mux outputs -> multiplexed DRAM address bus (wiring.json).
d23["1Y"] += VA[0]; d23["2Y"] += VA[1]
d24["1Y"] += VA[2]; d24["2Y"] += VA[3]
d25["1Y"] += VA[4]; d25["2Y"] += VA[5]
# (VA6/VA7 source still to be traced.)

# Shared arbitration controls as named nets (driven by the sync/timing block 5).
arb_rowcol = Net("ARB_ROWCOL")   # select B: row vs column phase
arb_cpuvid = Net("ARB_CPUVID")   # select A: CPU vs video access phase
for m in (d23, d24, d25):
    m["A"] += arb_cpuvid; m["B"] += arb_rowcol

# ---- 14 MHz clock oscillator (Z1 + D1 К1533ЛН1 inverters, R1/R2 470, C1 330p)
# Classic 2-inverter crystal oscillator; output CLK14 feeds the /4 divider.
z1   = P.XTAL("14MHz")(ref="Z1")
d1   = P.K1533LN1(ref="D1")
d1["VCC"] += vcc; d1["GND"] += gnd
r1 = P.R("470")(ref="R1"); r2 = P.R("470")(ref="R2"); c1 = P.C("330p")(ref="C1")

clk14   = Net("CLK14")
osc_in  = Net("OSC_IN")
osc_mid = Net("OSC_MID")
# inverter 1: in=osc_in, out=osc_mid, with R1 feedback across it
d1["1A"] += osc_in; d1["1Y"] += osc_mid
r1[1] += osc_in; r1[2] += osc_mid
z1[1] += osc_in; z1[2] += osc_mid          # crystal across the inverter
c1[1] += osc_in; c1[2] += gnd
# inverter 2: buffer osc_mid -> CLK14, R2 series
d1["2A"] += osc_mid
d1["2Y"] += clk14
r2[1] += osc_mid; r2[2] += clk14

# ---- block 5: /4 CPU-clock divider + video-sync counters -------------------
# CLK14 (14 MHz) -> /2 -> 7 MHz (pixel/dot) -> /2 -> 3.5 MHz CPU clock.
# Two toggling D-FFs of D8 К1533ТМ2 form the ripple /4 (each FF: D<-/Q). This
# resolves the CPU CLK net (was undriven). Set/reset tied inactive (high).
d8 = P.K1533TM2(ref="D8"); d8["VCC"] += vcc; d8["GND"] += gnd
clk7 = Net("CLK7")                     # 7 MHz dot clock (= CLK14/2)
d8["~1S"] += vcc; d8["~1R"] += vcc; d8["~2S"] += vcc; d8["~2R"] += vcc
d8["1C"] += clk14; d8["1D"] += d8["~1Q"]; d8["1Q"] += clk7        # /2 -> 7 MHz
d8["2C"] += clk7;  d8["2D"] += d8["~2Q"]; d8["2Q"] += clk_cpu     # /2 -> 3.5 MHz = CLK

# Video-sync counters (D2/D19 horizontal, D3/D4 vertical = К1533ИЕ7). Placed +
# powered + clocked from the dot clock; the H/V sync DECODE (which counter bits
# gate HSYNC/VSYNC/blank via D10/D14/D21) is FUNCTIONAL/TODO — to trace from scan.
hcount = [Net(f"H{i}") for i in range(8)]
vcount = [Net(f"V{i}") for i in range(8)]
d2  = P.K1533IE7(ref="D2");  d2["VCC"]  += vcc; d2["GND"]  += gnd
d19 = P.K1533IE7(ref="D19"); d19["VCC"] += vcc; d19["GND"] += gnd
d3  = P.K1533IE7(ref="D3");  d3["VCC"]  += vcc; d3["GND"]  += gnd
d4  = P.K1533IE7(ref="D4");  d4["VCC"]  += vcc; d4["GND"]  += gnd
# horizontal counter chain clocked by the dot clock; cascade via carry.
d2["~CU"] += clk7
for c, qs in ((d2, hcount[0:4]), (d19, hcount[4:8]), (d3, vcount[0:4]), (d4, vcount[4:8])):
    c["QA"] += qs[0]; c["QB"] += qs[1]; c["QC"] += qs[2]; c["QD"] += qs[3]
d19["~CU"] += d2["~CO"]      # H high nibble cascades off D2 carry
d3["~CU"]  += d19["~CO"]     # V counter advances on H rollover (functional cascade)
d4["~CU"]  += d3["~CO"]

# ---- power-on reset (C2 10u + R10 5.1k) ------------------------------------
c2 = P.C("10u")(ref="C2"); r10 = P.R("5.1k")(ref="R10")
c2[1] += reset_n; c2[2] += gnd
r10[1] += vcc;    r10[2] += reset_n

# ---- pull-ups on Z80 control inputs (R4..R7 5.1k) --------------------------
# /INT, /NMI, /BUSRQ, /WAIT must idle high. (R8/R9 pull-ups on bus /BJ,/BK
# pending an exact net trace — see schematics/wiring.json.)
for ref, net in zip(("R4", "R5", "R6", "R7"), (int_n, nmi_n, busrq_n, wait_n)):
    r = P.R("5.1k")(ref=ref)
    r[1] += vcc; r[2] += net

# ---- block 6a: pixel chain (D39/D40/D41 К555ИР16, 4-bit, KEEP LS timing) ----
# From the verified trace: D41 loads VD0-3, D40 loads VD4-7; serial chain
# D41 → D40 → D39 → FLASH XOR (D18). OE/PE of all three + D41's serial-in tie to
# net 'a' = GND. Clocked at 14 MHz. D40.Q3 also taps the FLASH AND (D13 sec 4).
VD = [Net(f"VD{i}") for i in range(8)]          # video-data bus (from D42/D43 latches)
d39v = P.K555IR16(ref="D39"); d40v = P.K555IR16(ref="D40"); d41v = P.K555IR16(ref="D41")
for r in (d39v, d40v, d41v):
    r["VCC"] += vcc; r["GND"] += gnd; r["OE"] += gnd; r["PE"] += gnd; r["C"] += clk14
for i in range(4):
    d41v[f"D{i}"] += VD[i]; d40v[f"D{i}"] += VD[4 + i]
d41v["SI"] += gnd                                # first stage serial-in low ('a'=GND)
d41v["Q3"] += d40v["SI"]                          # D41 → D40
d40v["Q3"] += d39v["SI"]; d40v["Q3"] += d13["4A"] # D40 → D39, and FLASH-AND tap
pix_ser = Net("PIX_SER"); d39v["Q3"] += pix_ser   # final serial pixel → FLASH XOR (D18)

# ---- block 6b: colour stage (D42 ИР23, D43 ИР22, D45 ИР16, D46/D47 КП12, D48 ИР22)
# Wired from the verified trace-verify nets (pin-exact). VD0-7 latch into D42 (→ colour
# bits B0/R0/G0/B1/R1/G1/Y) and D43 (→ data bus). D46/D47 КП12 mux those into BM/RM/GM/YM,
# D45 ИР16 registers them to BR/RR/GR/YR; D48 latches the border D0-D4 → BB/RB/GB.
d42 = P.K1533IR23(ref="D42"); d43 = P.K1533IR22(ref="D43"); d45c = P.K555IR16(ref="D45")
d46 = P.K1533KP12(ref="D46"); d47 = P.K1533KP12(ref="D47"); d48 = P.K1533IR22(ref="D48")
for pp in (d42, d43, d48): pp["VCC"] += vcc; pp["GND"] += gnd
for pp in (d45c,):          pp["VCC"] += vcc; pp["GND"] += gnd
for pp in (d46, d47):       pp["VCC"] += vcc; pp["GND"] += gnd
_cp = {"D42": d42, "D43": d43, "D45": d45c, "D46": d46, "D47": d47, "D48": d48}
_exist = {f"VD{i}": VD[i] for i in range(8)}
_exist.update({f"D{i}": D[i] for i in range(8)})
_exist["GND"] = gnd
_colornets = {
    "VD0": ["D42.3", "D43.3"], "VD1": ["D42.4", "D43.4"], "VD2": ["D42.7", "D43.7"],
    "VD3": ["D42.8", "D43.8"], "VD4": ["D42.13", "D43.13"], "VD5": ["D42.14", "D43.14"],
    "VD6": ["D42.17", "D43.17"], "VD7": ["D42.18", "D43.18"],
    "D0": ["D43.2", "D48.3"], "D1": ["D43.5", "D48.4"], "D2": ["D43.6", "D48.7"],
    "D3": ["D43.9", "D48.13"], "D4": ["D43.12", "D48.8"],
    "D5": ["D43.15"], "D6": ["D43.16"], "D7": ["D43.19"],
    "B0": ["D42.2", "D46.5"], "R0": ["D42.5", "D46.11"], "G0": ["D42.6", "D47.5"],
    "B1": ["D42.9", "D46.6"], "R1": ["D42.12", "D46.10"], "G1": ["D42.15", "D47.6"],
    "Y": ["D42.16", "D47.10", "D47.11"],
    "BB": ["D48.2", "D46.4", "D46.3"], "RB": ["D48.5", "D46.12", "D46.13"],
    "GB": ["D48.6", "D47.4", "D47.3"],
    "BM": ["D46.7", "D45.2"], "RM": ["D46.9", "D45.3"], "GM": ["D47.7", "D45.4"],
    "YM": ["D47.9", "D45.5"],
    "BR": ["D45.13"], "RR": ["D45.12"], "GR": ["D45.11"], "YR": ["D45.10"],
    "BORDER": ["D46.2", "D47.2"], "a2": ["D45.6"],
    "GND": ["D42.1", "D46.15", "D47.15", "D48.1"],   # OE/2G ties to ground
}
for _nm, _eps in _colornets.items():
    _n = _exist.get(_nm) or Net(_nm)
    for _ep in _eps:
        _r, _pn = _ep.split(".")
        _n += _cp[_r][int(_pn)]
# D46/D47 OE0(pin1) ← FLASH-gated SCREEN, select A(14) ← arbitration — named, TODO trace
vid_oe = Net("VID_OE"); vid_sel = Net("VID_SEL")
d46[1] += vid_oe; d47[1] += vid_oe; d46[14] += vid_sel; d47[14] += vid_sel
d45c["C"] += clk14; d45c["OE"] += gnd; d45c["SI"] += gnd   # colour register clock/enable

# ---- block 7a: disk / joystick I/O (D44/D51 ИР22, D50 АП3) -----------------
# Pin-exact from the trace. D44/D51 latch the disk data bus; D50 buffers the disk
# address A8-A15 through КД522 diodes to AA8-AA15. Connectors X1/X2 (joysticks),
# X3 (keyboard J0-J4), X4 (disk data DO0-4), X6 (disk address). NOTE: the board
# silk-labels the address diodes "D9..D16" — that collides with the logic ICs of
# the same name, so they are VD9..VD16 here. Net 'a' = GND (global, see wiring.json).
d44 = P.K1533IR22(ref="D44"); d51 = P.K1533IR22(ref="D51"); d50 = P.K1533AP3(ref="D50")
x1 = P.CONN(9, "JoyL")(ref="X1"); x2 = P.CONN(9, "JoyR")(ref="X2")
x3 = P.CONN(9, "Kbd")(ref="X3"); x4 = P.CONN(9, "DiskDO")(ref="X4"); x6 = P.CONN(8, "DiskAA")(ref="X6")
for pp in (d44, d51, d50): pp["VCC"] += vcc; pp["GND"] += gnd
vd = {n: P.DIODE("КД522")(ref=f"VD{n}") for n in range(9, 17)}
_dp = {"D44": d44, "D51": d51, "D50": d50, "X1": x1, "X2": x2, "X3": x3, "X4": x4, "X6": x6}
_dp.update({f"D{n}": vd[n] for n in range(9, 17)})   # the address diodes (board "D9..16")
_de = {f"D{i}": D[i] for i in range(8)}; _de.update({f"A{i}": A[i] for i in range(16)}); _de["GND"] = gnd
_disknets = {
    "J0": ["X3.2", "D44.3"], "J1": ["X3.3", "D44.4"], "J2": ["X3.4", "D44.7"],
    "J3": ["X3.5", "D44.8"], "J4": ["X3.9", "D44.13"],
    "GND": ["D44.14", "D44.17", "D44.18", "D44.1"],
    "a": ["D44.11", "D51.11", "D51.14", "D51.18"],
    "D0": ["D44.2", "D51.2"], "D1": ["D44.5", "D51.5"], "D2": ["D44.6", "D51.6"],
    "D3": ["D44.9", "D51.9"], "D4": ["D44.12", "D51.12"], "D5": ["D44.15", "D51.15"],
    "D6": ["D44.16", "D51.16"], "D7": ["D44.19", "D51.19"],
    "DI0": ["D51.3"], "DI1": ["D51.4"], "DI2": ["D51.7"], "DI3": ["D51.8"], "DI4": ["D51.13"],
    "A8": ["D50.2"], "A9": ["D50.4"], "A10": ["D50.6"], "A11": ["D50.8"],
    "A14": ["D50.17"], "A15": ["D50.15"], "A12": ["D50.13"], "A13": ["D50.11"],
    "D50_OE": ["D50.1", "D50.19"],
    "dA8": ["D50.18", "D9.1"], "dA9": ["D50.16", "D10.1"], "dA10": ["D50.14", "D11.1"],
    "dA11": ["D50.12", "D12.1"], "dA14": ["D50.3", "D13.1"], "dA15": ["D50.5", "D14.1"],
    "dA12": ["D50.7", "D15.1"], "dA13": ["D50.9", "D16.1"],
    "AA8": ["D9.2", "X6.6"], "AA9": ["D10.2", "X6.3"], "AA10": ["D11.2", "X6.2"],
    "AA11": ["D12.2", "X6.1", "X1.7"], "AA12": ["D15.2", "X6.4", "X2.7"],
    "AA13": ["D16.2", "X6.5"], "AA14": ["D13.2", "X6.7"], "AA15": ["D14.2", "X6.8"],
    "DO0": ["X4.4", "X1.3", "X2.9"], "DO1": ["X4.5", "X1.2", "X2.5"], "DO2": ["X4.6", "X1.4", "X2.4"],
    "DO3": ["X4.7", "X1.5", "X2.2"], "DO4": ["X4.8", "X1.9", "X2.3"],
}
for _nm, _eps in _disknets.items():
    _n = gnd if _nm in ("GND", "a") else (_de.get(_nm) or Net(_nm))
    for _ep in _eps:
        _r, _pn = _ep.split("."); _n += _dp[_r][int(_pn)]

# ---- generate outputs ------------------------------------------------------
ERC()   # prints its own '<n> errors / <n> warnings found' summary
generate_netlist(file_=NETLIST)

# Live schematic SVG for viewer.html. SKiDL's generate_svg emits the yosys JSON
# but its internal netlistsvg --skin call fails on larger designs; netlistsvg works
# fine on the JSON directly, so we drive it ourselves.
import subprocess
try:
    try:
        generate_svg(file_=SVG)      # produces SVG.json (and may error on its own .svg)
    except Exception:
        pass
    if os.path.exists(SVG + ".json"):
        subprocess.run(["netlistsvg", SVG + ".json", "-o", SVG + ".svg"],
                       check=True, capture_output=True)
        print(f"svg     -> {os.path.normpath(SVG)}.svg")
    else:
        print("svg skipped (no json)")
except Exception as e:
    print(f"svg skipped ({e})")
print(f"netlist -> {os.path.normpath(NETLIST)}")
