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
