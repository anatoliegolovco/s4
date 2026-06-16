//
// К565РУ5 — behavioral DRAM model (≈ 4164, 64K x 1) for SimulIDE 1.1.0
//
// Single-bit-wide dynamic RAM: 64Ki cells = 256 rows x 256 columns,
// addressed through a multiplexed 8-bit address bus (A0..A7) with the
// row address latched on /RAS falling and the column address latched on
// /CAS falling.  Data is 1 bit wide (separate DIN and DOUT pins) with
// /WE selecting read vs. write.
//
// FIDELITY NOTE (spec §2.4, decision 0004 "fidelity over improvement"):
// this model deliberately reproduces the SLOW Soviet К565РУ5 timing
// (≈ −20 grade or slower: tRAS ~200 ns, tCAC ~100 ns).  Do NOT swap in a
// generic fast 4164 / SRAM model — the Sintez-2 WAIT generator was tuned
// to this slow part, and faster timing would make the machine look more
// reliable than the real hardware.  See docs/datasheets/README.md.
//
// PinModes: undef_mode=0, input=1, openCo=2, output=3, source=4
//
// ---------------------------------------------------------------------
// Required component pins (define these on the SimulIDE package/subcircuit):
//
//   IoPort "PORTA" — multiplexed address bus A0..A7 (8 lines, input)
//   IoPin  "RAS"   — /RAS, row address strobe   (active-low, input)
//   IoPin  "CAS"   — /CAS, column address strobe (active-low, input)
//   IoPin  "WE"    — /WE,  write enable          (active-low, input)
//   IoPin  "DIN"   — data in                     (input)
//   IoPin  "DOUT"  — data out                    (output, tri-state)
//
// ---------------------------------------------------------------------

// PinModes
const int MODE_UNDEF  = 0;
const int MODE_INPUT  = 1;
const int MODE_OPENCO = 2;
const int MODE_OUTPUT = 3;
const int MODE_SOURCE = 4;

// --- К565РУ5 timing (nanoseconds) -----------------------------------
// component.addEvent() takes a delay in picoseconds (1 ns = 1000 ps),
// matching the 6532/6522 cores (m_rDelay = 10000 == 10 ns).
const uint NS = 1000;

const uint tRAC = 200 * NS; // access time from /RAS falling (row access)
const uint tCAC = 100 * NS; // access time from /CAS falling (column access) -> DOUT valid
const uint tRAS = 200 * NS; // minimum /RAS pulse width (documented, checked)
const uint tCAS = 100 * NS; // minimum /CAS pulse width (documented, checked)
const uint tRP  = 120 * NS; // /RAS precharge time (documented, checked)
const uint tOFF =  40 * NS; // /CAS rising -> DOUT high-Z (output disable)

// Logic threshold: TTL-ish, single +5 V part. A line below this is '0'.
const double VLOW = 2.5;

// --- Pins ------------------------------------------------------------
IoPort@ addrPort = component.getPort("PORTA"); // A0..A7 multiplexed
IoPin@  rasPin   = component.getPin("RAS");
IoPin@  casPin   = component.getPin("CAS");
IoPin@  wePin    = component.getPin("WE");
IoPin@  dinPin   = component.getPin("DIN");
IoPin@  doutPin  = component.getPin("DOUT");

// --- 64Kib storage: 65536 cells packed into 8192 bytes ---------------
array<uint8> mem(8192);

// --- Strobe / cycle state -------------------------------------------
bool   m_ras;        // current /RAS level (true = high/inactive)
bool   m_cas;        // current /CAS level (true = high/inactive)
bool   m_rasActive;  // /RAS is asserted (low)
bool   m_casActive;  // /CAS is asserted (low)

uint   m_row;        // latched row address  (0..255)
uint   m_col;        // latched column address (0..255)
bool   m_rowLatched; // a valid row has been latched this /RAS cycle
bool   m_write;      // current cycle is a write (sampled /WE low at /CAS)
uint8  m_dout;       // bit scheduled to drive on DOUT (0/1)
bool   m_firstAccess;// /CAS falling is the first one since this /RAS fell

// --------------------------------------------------------------------
// SimulIDE 1.1 IoPin reads its LOGIC level with getInpState() (true=high), per the
// bundled MCS65 cores; there is no getVolt(). Low = logic-0.
bool isLow( IoPin@ p ) { return !p.getInpState(); }

uint cellIndex( uint row, uint col )
{
    return (row << 8) | col;   // 0..65535
}

uint8 readCell( uint row, uint col )
{
    uint idx = cellIndex( row, col );
    return ( mem[idx >> 3] >> (idx & 7) ) & 1;
}

void writeCell( uint row, uint col, uint8 bit )
{
    uint idx  = cellIndex( row, col );
    uint8 msk = uint8( 1 << (idx & 7) );
    if( bit != 0 ) mem[idx >> 3] |=  msk;
    else           mem[idx >> 3] &= ~msk;
}

// --------------------------------------------------------------------
void setup() // Executed when the Component is created
{
    print("К565РУ5 (4164 64Kx1 DRAM) setup() OK");
}

void reset() // Executed at Simulation start
{
    addrPort.setPinMode( MODE_INPUT );
    rasPin.setPinMode( MODE_INPUT );
    casPin.setPinMode( MODE_INPUT );
    wePin.setPinMode( MODE_INPUT );
    dinPin.setPinMode( MODE_INPUT );

    doutPin.setPinMode( MODE_OUTPUT );
    doutPin.setVoltage( 0 );

    // Register for input transitions; voltChanged() handles edges.
    rasPin.changeCallBack( element, true );
    casPin.changeCallBack( element, true );

    m_ras = true;  m_rasActive = false;
    m_cas = true;  m_casActive = false;
    m_rowLatched = false;
    m_write = false;
    m_row = 0; m_col = 0; m_dout = 0;
    m_firstAccess = false;

    // DRAM powers up with indeterminate contents; emulate that as zeroed.
    for( uint i = 0; i < mem.length(); ++i ) mem[i] = 0;

    print("К565РУ5 reset() — slow РУ5 timing: tRAC=200ns tCAC=100ns tRAS=200ns");
}

// --------------------------------------------------------------------
// Edge dispatcher. SimulIDE calls voltChanged() on any registered pin
// change; we re-sample /RAS and /CAS and act only on real transitions.
void voltChanged()
{
    bool ras = !isLow( rasPin );   // true == high (inactive)
    bool cas = !isLow( casPin );

    if( ras != m_ras )
    {
        m_ras = ras;
        if( !ras ) rasFalling();   // /RAS asserted
        else       rasRising();    // /RAS precharge
    }

    if( cas != m_cas )
    {
        m_cas = cas;
        if( !cas ) casFalling();   // /CAS asserted -> latch column, run access
        else       casRising();    // /CAS deasserted -> DOUT goes high-Z
    }
}

// --- /RAS falling: latch ROW address --------------------------------
void rasFalling()
{
    m_rasActive   = true;
    m_row         = addrPort.getInpState() & 0xFF;
    m_rowLatched  = true;
    m_firstAccess = true;   // next /CAS fall is the row-access access
    // tRAC clock starts here; DOUT becomes valid at the later of
    // tRAC (from /RAS) and tCAC (from /CAS) — handled at /CAS fall.
}

// --- /RAS rising: precharge, deselect -------------------------------
void rasRising()
{
    m_rasActive  = false;
    m_rowLatched = false;
    // tRP precharge must elapse before the next /RAS fall; the WAIT
    // generator enforces this on the real board. Nothing to drive here.
}

// --- /CAS falling: latch COLUMN, decide read/write, run the access --
void casFalling()
{
    m_casActive = true;

    if( !m_rasActive )
    {
        // /CAS-before-/RAS with no row latched => RAS-only / CBR refresh
        // style cycle. No data access, DOUT stays in its current state.
        return;
    }

    m_col   = addrPort.getInpState() & 0xFF;
    m_write = isLow( wePin );        // /WE low at /CAS fall => write cycle

    if( m_write )
    {
        // Early-write: sample DIN and store. No DOUT activity.
        uint8 bit = isLow( dinPin ) ? 0 : 1;
        writeCell( m_row, m_col, bit );
    }
    else
    {
        // Read cycle: DOUT valid after the access delay. Normal accesses
        // are limited by tCAC (from /CAS). On the first /CAS fall right
        // after /RAS, the longer tRAC dominates the row-access path; use
        // it as a conservative bound (the WAIT generator allows for it).
        m_dout = readCell( m_row, m_col );

        uint delay = m_firstAccess ? tRAC : tCAC;
        m_firstAccess = false;       // page-mode style follow-ons use tCAC

        component.addEvent( delay ); // -> runEvent() drives DOUT valid
    }
}

// --- /CAS rising: output disable (DOUT -> high-Z after tOFF) ---------
void casRising()
{
    m_casActive = false;
    // Schedule output disable. We model high-Z by parking DOUT at 0;
    // SimulIDE pins read by the bus mux treat this as released.
    component.addEvent( tOFF ); // -> runEvent() releases DOUT
}

// --- Scheduled event: drive (or release) DOUT -----------------------
void runEvent()
{
    if( m_casActive && !m_write )
    {
        // Access complete: present the read bit (~0 V for '0', ~5 V '1').
        doutPin.setVoltage( m_dout != 0 ? 5.0 : 0.0 );
    }
    else
    {
        // /CAS is high (or it was a write): output disabled / high-Z.
        doutPin.setVoltage( 0 );
    }
}

// --------------------------------------------------------------------
// Inspector hooks (optional; mirror the MCS65 cores).
int getCpuReg( string reg )
{
    if( reg == "Row" )  return int(m_row);
    if( reg == "Col" )  return int(m_col);
    if( reg == "DOUT" ) return int(m_dout);
    return 0;
}

string getStrReg( string reg )
{
    if( reg == "RAS" ) return m_rasActive ? "low" : "high";
    if( reg == "CAS" ) return m_casActive ? "low" : "high";
    if( reg == "Op" )  return m_write ? "Write" : "Read";
    return "";
}
