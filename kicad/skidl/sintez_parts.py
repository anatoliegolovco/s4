"""Sintez-2 custom part library for SKiDL.

Each Sintez IC is defined here as a SKiDL TEMPLATE part with its real pin list
(number, name, electrical type) taken from the datasheets (docs/datasheets/) and
the schematic / power table (schematics/bom.json, schematics/wiring.json).

No KiCad symbol library is required to generate a netlist — these definitions ARE
the parts. Footprints reference KiCad's standard through-hole DIP library
(Package_DIP:*), since every Sintez IC is a DIP. When KiCad 9 is installed those
footprints resolve for PCB layout (T8); the netlist itself does not need them.

Western equivalents and corrections are documented in schematics/bom.json (v0.3):
  - К555ИР16 is a 4-bit/14-pin shift register (NOT 74LS165).
  - Tape part D49 is К544СА3, an analog comparator (NOT LM567).
  - D38 is КР1533ИР27 (74273), not ИР23.
"""

from skidl import Part, Pin, TEMPLATE

I, O, B, PWR, PAS, TRI, NC = (
    Pin.types.INPUT, Pin.types.OUTPUT, Pin.types.BIDIR,
    Pin.types.PWRIN, Pin.types.PASSIVE, Pin.types.TRISTATE, Pin.types.NOCONNECT,
)


def _dip(name, footprint, pins, value=None, prefix="D"):
    """Build a TEMPLATE part from a list of (num, name, func) tuples."""
    return Part(
        name=name, tool="skidl", dest=TEMPLATE, ref_prefix=prefix,
        value=value or name, footprint=footprint,
        pins=[Pin(num=str(n), name=nm, func=f) for (n, nm, f) in pins],
    )


# ---------------------------------------------------------------- CPU (D6)
# Zilog Z80 / КР1858ВМ1, DIP-40 — canonical Zilog pinout (pin-compatible).
Z80 = _dip("Z84C00", "Package_DIP:DIP-40_W15.24mm", [
    (1, "A11", O), (2, "A12", O), (3, "A13", O), (4, "A14", O), (5, "A15", O),
    (6, "CLK", I), (7, "D4", B), (8, "D3", B), (9, "D5", B), (10, "D6", B),
    (11, "VCC", PWR), (12, "D2", B), (13, "D7", B), (14, "D0", B), (15, "D1", B),
    (16, "~INT", I), (17, "~NMI", I), (18, "~HALT", O), (19, "~MREQ", TRI),
    (20, "~IORQ", TRI), (21, "~RD", TRI), (22, "~WR", TRI), (23, "~BUSAK", O),
    (24, "~WAIT", I), (25, "~BUSRQ", I), (26, "~RESET", I), (27, "~M1", O),
    (28, "~RFSH", O), (29, "GND", PWR), (30, "A0", TRI), (31, "A1", TRI),
    (32, "A2", TRI), (33, "A3", TRI), (34, "A4", TRI), (35, "A5", TRI),
    (36, "A6", TRI), (37, "A7", TRI), (38, "A8", TRI), (39, "A9", TRI),
    (40, "A10", TRI),
], value="КР1858ВМ1/Z84C00")

# ---------------------------------------------------------------- ROM (D36)
# 27128 16Kx8 EPROM, DIP-28 (pinout read from the schematic).
ROM27128 = _dip("27128", "Package_DIP:DIP-28_W15.24mm", [
    (1, "VPP", PWR), (2, "A12", I), (3, "A7", I), (4, "A6", I), (5, "A5", I),
    (6, "A4", I), (7, "A3", I), (8, "A2", I), (9, "A1", I), (10, "A0", I),
    (11, "D0", TRI), (12, "D1", TRI), (13, "D2", TRI), (14, "GND", PWR),
    (15, "D3", TRI), (16, "D4", TRI), (17, "D5", TRI), (18, "D6", TRI),
    (19, "D7", TRI), (20, "~CE", I), (21, "A10", I), (22, "~OE", I),
    (23, "A11", I), (24, "A9", I), (25, "A8", I), (26, "A13", I),
    (27, "PGM", I), (28, "VCC", PWR),
], value="27128 (ПЗУ)")

# ---------------------------------------------------------------- glue logic
# К1533ЛН1 = 74LS04 hex inverter, DIP-14.
K1533LN1 = _dip("K1533LN1", "Package_DIP:DIP-14_W7.62mm", [
    (1, "1A", I), (2, "1Y", O), (3, "2A", I), (4, "2Y", O), (5, "3A", I),
    (6, "3Y", O), (7, "GND", PWR), (8, "4Y", O), (9, "4A", I), (10, "5Y", O),
    (11, "5A", I), (12, "6Y", O), (13, "6A", I), (14, "VCC", PWR),
], value="К1533ЛН1 (74LS04)")

# К1533ТМ2 = 74LS74 dual D flip-flop, DIP-14.
K1533TM2 = _dip("K1533TM2", "Package_DIP:DIP-14_W7.62mm", [
    (1, "~1R", I), (2, "1D", I), (3, "1C", I), (4, "~1S", I), (5, "1Q", O),
    (6, "~1Q", O), (7, "GND", PWR), (8, "~2Q", O), (9, "2Q", O), (10, "~2S", I),
    (11, "2C", I), (12, "2D", I), (13, "~2R", I), (14, "VCC", PWR),
], value="К1533ТМ2 (74LS74)")

# К1533ЛЕ1 = 74LS02 quad 2-input NOR, DIP-14 (outputs on 1/4/10/13).
K1533LE1 = _dip("K1533LE1", "Package_DIP:DIP-14_W7.62mm", [
    (1, "1Y", O), (2, "1A", I), (3, "1B", I), (4, "2Y", O), (5, "2A", I),
    (6, "2B", I), (7, "GND", PWR), (8, "3A", I), (9, "3B", I), (10, "3Y", O),
    (11, "4A", I), (12, "4B", I), (13, "4Y", O), (14, "VCC", PWR),
], value="К1533ЛЕ1 (74LS02)")

# К1533ЛА3 = 74ALS00 quad 2-input NAND, DIP-14.
K1533LA3 = _dip("K1533LA3", "Package_DIP:DIP-14_W7.62mm", [
    (1, "1A", I), (2, "1B", I), (3, "1Y", O), (4, "2A", I), (5, "2B", I),
    (6, "2Y", O), (7, "GND", PWR), (8, "3Y", O), (9, "3A", I), (10, "3B", I),
    (11, "4Y", O), (12, "4A", I), (13, "4B", I), (14, "VCC", PWR),
], value="К1533ЛА3 (74ALS00)")

# К1533ЛА4 = 74ALS10 triple 3-input NAND, DIP-14.
K1533LA4 = _dip("K1533LA4", "Package_DIP:DIP-14_W7.62mm", [
    (1, "1A", I), (2, "1B", I), (3, "2A", I), (4, "2B", I), (5, "2C", I),
    (6, "2Y", O), (7, "GND", PWR), (8, "3Y", O), (9, "3A", I), (10, "3B", I),
    (11, "3C", I), (12, "1C", I), (13, "1Y", O), (14, "VCC", PWR),
], value="К1533ЛА4 (74ALS10)")

# К1533ЛИ1 = 74LS08 quad 2-input AND, DIP-14.
K1533LI1 = _dip("K1533LI1", "Package_DIP:DIP-14_W7.62mm", [
    (1, "1A", I), (2, "1B", I), (3, "1Y", O), (4, "2A", I), (5, "2B", I),
    (6, "2Y", O), (7, "GND", PWR), (8, "3Y", O), (9, "3A", I), (10, "3B", I),
    (11, "4Y", O), (12, "4A", I), (13, "4B", I), (14, "VCC", PWR),
], value="К1533ЛИ1 (74LS08)")

# К565РУ5 = 4164 64Kx1 DRAM, DIP-16 (standard 4164 pin functions; power 8/16 per
# the 'Питание' table). Address-pin names follow the schematic's A0..A7 labels;
# their VA-net mapping (per chip) is applied in sintez2.py from wiring.json.
K565RU5 = _dip("K565RU5", "Package_DIP:DIP-16_W7.62mm", [
    (1, "NC", NC), (2, "DIN", I), (3, "~WE", I), (4, "~RAS", I),
    (5, "A6", I), (6, "A4", I), (7, "A2", I), (8, "VCC", PWR),
    (9, "A0", I), (10, "A1", I), (11, "A3", I), (12, "A5", I), (13, "A7", I),
    (14, "DOUT", TRI), (15, "~CAS", I), (16, "GND", PWR),
], value="К565РУ5 (4164)")

# КП12 (К1533КП12) = 74ALS253 dual 4:1 mux, 3-state, DIP-16. Shared selects A(14),
# B(2). Group1: 1C0-3=pins 6,5,4,3 -> 1Y=7, enable ~1G=1. Group2: 2C0-3=10,11,12,13
# -> 2Y=9, enable ~2G=15.
K1533KP12 = _dip("K1533KP12", "Package_DIP:DIP-16_W7.62mm", [
    (1, "~1G", I), (2, "B", I), (3, "1C3", I), (4, "1C2", I), (5, "1C1", I),
    (6, "1C0", I), (7, "1Y", TRI), (8, "GND", PWR), (9, "2Y", TRI), (10, "2C0", I),
    (11, "2C1", I), (12, "2C2", I), (13, "2C3", I), (14, "A", I), (15, "~2G", I),
    (16, "VCC", PWR),
], value="К1533КП12 (74ALS253)")

# КР1533ИР27 = 74273 octal D flip-flop with clear, DIP-20.
KR1533IR27 = _dip("KR1533IR27", "Package_DIP:DIP-20_W7.62mm", [
    (1, "~MR", I), (2, "1Q", O), (3, "1D", I), (4, "2D", I), (5, "2Q", O),
    (6, "3Q", O), (7, "3D", I), (8, "4D", I), (9, "4Q", O), (10, "GND", PWR),
    (11, "C", I), (12, "5Q", O), (13, "5D", I), (14, "6D", I), (15, "6Q", O),
    (16, "7Q", O), (17, "7D", I), (18, "8D", I), (19, "8Q", O), (20, "VCC", PWR),
], value="КР1533ИР27 (74273)")

# К1533ИЕ7 = 74193 4-bit up/down binary counter, DIP-16. Used for H/V sync +
# DRAM refresh address counting.
K1533IE7 = _dip("K1533IE7", "Package_DIP:DIP-16_W7.62mm", [
    (1, "B", I), (2, "QB", O), (3, "QA", O), (4, "~CD", I), (5, "~CU", I),
    (6, "QC", O), (7, "QD", O), (8, "GND", PWR), (9, "D", I), (10, "C", I),
    (11, "~LOAD", I), (12, "~CO", O), (13, "~BO", O), (14, "CLR", I), (15, "A", I),
    (16, "VCC", PWR),
], value="К1533ИЕ7 (74193)")

# К555ИР16 = 4-bit parallel-load shift register, DIP-14 (NOT 74LS165; see bom v0.3).
# Pin map from the redraw symbol: SI=1, D0-D3=2/3/4/5, PE=6, GND=7, OE=8, C=9,
# Q3-Q0=10/11/12/13, VCC=14.
K555IR16 = _dip("K555IR16", "Package_DIP:DIP-14_W7.62mm", [
    (1, "SI", I), (2, "D0", I), (3, "D1", I), (4, "D2", I), (5, "D3", I),
    (6, "PE", I), (7, "GND", PWR), (8, "OE", I), (9, "C", I), (10, "Q3", TRI),
    (11, "Q2", TRI), (12, "Q1", TRI), (13, "Q0", TRI), (14, "VCC", PWR),
], value="К555ИР16 (4-bit shift, keep LS)")

# К1533ИР22 = 74LS373 octal transparent latch, DIP-20.
K1533IR22 = _dip("K1533IR22", "Package_DIP:DIP-20_W7.62mm", [
    (1, "~OE", I), (2, "Q0", TRI), (3, "D0", I), (4, "D1", I), (5, "Q1", TRI),
    (6, "Q2", TRI), (7, "D2", I), (8, "D3", I), (9, "Q3", TRI), (10, "GND", PWR),
    (11, "LE", I), (12, "Q4", TRI), (13, "D4", I), (14, "D5", I), (15, "Q5", TRI),
    (16, "Q6", TRI), (17, "D6", I), (18, "D7", I), (19, "Q7", TRI), (20, "VCC", PWR),
], value="К1533ИР22 (74LS373)")

# К1533ИР23 = 74LS374 octal D flip-flop, DIP-20.
K1533IR23 = _dip("K1533IR23", "Package_DIP:DIP-20_W7.62mm", [
    (1, "~OE", I), (2, "Q0", TRI), (3, "D0", I), (4, "D1", I), (5, "Q1", TRI),
    (6, "Q2", TRI), (7, "D2", I), (8, "D3", I), (9, "Q3", TRI), (10, "GND", PWR),
    (11, "CP", I), (12, "Q4", TRI), (13, "D4", I), (14, "D5", I), (15, "Q5", TRI),
    (16, "Q6", TRI), (17, "D6", I), (18, "D7", I), (19, "Q7", TRI), (20, "VCC", PWR),
], value="К1533ИР23 (74LS374)")

# К1533АП3 = 74LS244 octal 3-state buffer (two 4-bit halves), DIP-20.
K1533AP3 = _dip("K1533AP3", "Package_DIP:DIP-20_W7.62mm", [
    (1, "~1OE", I), (2, "1A0", I), (3, "2Y0", O), (4, "1A1", I), (5, "2Y1", O),
    (6, "1A2", I), (7, "2Y2", O), (8, "1A3", I), (9, "2Y3", O), (10, "GND", PWR),
    (11, "2A3", I), (12, "1Y3", O), (13, "2A2", I), (14, "1Y2", O), (15, "2A1", I),
    (16, "1Y1", O), (17, "2A0", I), (18, "1Y0", O), (19, "~2OE", I), (20, "VCC", PWR),
], value="К1533АП3 (74LS244)")

# К1533КП11 = 74LS257 quad 2:1 mux, 3-state, DIP-16 (D5 video-fetch mux).
K1533KP11 = _dip("K1533KP11", "Package_DIP:DIP-16_W7.62mm", [
    (1, "S", I), (2, "1a", I), (3, "1b", I), (4, "1Y", TRI), (5, "2a", I),
    (6, "2b", I), (7, "2Y", TRI), (8, "GND", PWR), (9, "3Y", TRI), (10, "3b", I),
    (11, "3a", I), (12, "4Y", TRI), (13, "4b", I), (14, "4a", I), (15, "~OE", I),
    (16, "VCC", PWR),
], value="К1533КП11 (74LS257)")

# К544СА3 = analog precision comparator (tape-IN, D49), DIP-14.
K544SA3 = _dip("K544SA3", "Package_DIP:DIP-14_W7.62mm", [
    (1, "W1", I), (2, "QE", O), (3, "C", I), (5, "NC1", NC), (6, "NC2", NC),
    (7, "U2", PWR), (8, "QK", O), (9, "NC3", NC), (11, "U1", PWR), (14, "W2", I),
], value="К544СА3 (comparator)")

# ---------------------------------------------------------------- passives
def R(value):
    return Part(name="R", tool="skidl", dest=TEMPLATE, ref_prefix="R",
                value=value, footprint="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal",
                pins=[Pin(num="1", name="~", func=PAS), Pin(num="2", name="~", func=PAS)])

def C(value):
    return Part(name="C", tool="skidl", dest=TEMPLATE, ref_prefix="C",
                value=value, footprint="Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm",
                pins=[Pin(num="1", name="~", func=PAS), Pin(num="2", name="~", func=PAS)])

def XTAL(value):
    return Part(name="Crystal", tool="skidl", dest=TEMPLATE, ref_prefix="Z",
                value=value, footprint="Crystal:Crystal_HC49-U_Vertical",
                pins=[Pin(num="1", name="1", func=PAS), Pin(num="2", name="2", func=PAS)])

def BJT(value="КТ315"):   # NPN small-signal (pin1=E, pin2=B, pin3=C)
    return Part(name="Q_NPN", tool="skidl", dest=TEMPLATE, ref_prefix="VT", value=value,
                footprint="Package_TO_SOT_THT:TO-92_Inline",
                pins=[Pin(num="1", name="E", func=PAS), Pin(num="2", name="B", func=I),
                      Pin(num="3", name="C", func=PAS)])

def DIODE(value="КД522"):  # pin1=anode, pin2=cathode
    return Part(name="D", tool="skidl", dest=TEMPLATE, ref_prefix="VD", value=value,
                footprint="Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal",
                pins=[Pin(num="1", name="A", func=PAS), Pin(num="2", name="K", func=PAS)])

def SPK(value="ЗП-3"):
    return Part(name="Speaker", tool="skidl", dest=TEMPLATE, ref_prefix="BA", value=value,
                footprint="Buzzer_Beeper:Buzzer_12x9.5RM7.6",
                pins=[Pin(num="1", name="1", func=PAS), Pin(num="2", name="2", func=PAS)])

def CONN(n, value="conn"):  # generic n-pin connector
    return Part(name=f"Conn_{n}", tool="skidl", dest=TEMPLATE, ref_prefix="X", value=value,
                footprint="Connector_PinHeader_2.54mm:PinHeader_1x%02d_P2.54mm_Vertical" % n,
                pins=[Pin(num=str(i), name=str(i), func=PAS) for i in range(1, n + 1)])
