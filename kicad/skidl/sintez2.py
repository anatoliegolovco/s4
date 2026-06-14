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

# ---- generate outputs ------------------------------------------------------
ERC()   # prints its own '<n> errors / <n> warnings found' summary
generate_netlist(file_=NETLIST)
try:
    generate_svg(file_=SVG)          # live schematic for the viewer.html "movie"
    print(f"svg     -> {os.path.normpath(SVG)}.svg")
except Exception as e:
    print(f"svg skipped ({e})")
print(f"netlist -> {os.path.normpath(NETLIST)}")
