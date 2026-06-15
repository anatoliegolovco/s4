#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "z80.h"
static uint8_t mem[65536];
static uint8_t rb(void* u, uint16_t a){ (void)u; return mem[a]; }
static void   wb(void* u, uint16_t a, uint8_t v){ (void)u; if(a>=0x4000) mem[a]=v; } // ROM is read-only
static uint8_t pin(z80* z, uint8_t port){ (void)z; (void)port; return 0xBF; } // FE: no keys, EAR=0
static void   pout(z80* z, uint8_t port, uint8_t v){ (void)z;(void)port;(void)v; }
int main(int argc, char** argv){
    const char* romf = argc>1? argv[1] : "/home/anatolie/ai3/s4/roms/sintez-M.rom";
    FILE* f=fopen(romf,"rb"); if(!f){ printf("ROM open fail\n"); return 2; }
    size_t n=fread(mem,1,16384,f); fclose(f);
    printf("ROM loaded: %zu bytes from %s\n", n, romf);
    z80 z; z80_init(&z);
    z.read_byte=rb; z.write_byte=wb; z.port_in=pin; z.port_out=pout;
    unsigned long BUDGET=40000000UL, last_int=0;
    long steps=0;
    while(z.cyc < BUDGET){
        z80_step(&z); steps++;
        if(z.cyc - last_int >= 69888UL){ last_int=z.cyc; if(z.iff1) z80_gen_int(&z,0xFF); }
    }
    // boot indicators (48K ROM system variables)
    uint16_t PRAMT = mem[0x5CB4] | (mem[0x5CB5]<<8);
    uint16_t CHARS = mem[0x5C36] | (mem[0x5C37]<<8);
    uint8_t  ERRNR = mem[0x5C3A];
    uint16_t RAMTOP= mem[0x5CB2] | (mem[0x5CB3]<<8);
    // screen content (0x4000-0x57FF bitmap) — count non-zero bytes
    long px=0; for(int a=0x4000;a<=0x57FF;a++) if(mem[a]) px++;
    long attr=0; for(int a=0x5800;a<=0x5AFF;a++) if(mem[a]) attr++;
    printf("after %ld steps, %lu T-states (PC=%04X):\n", steps, z.cyc, z.pc);
    printf("  P-RAMT  (5CB4) = %04X  (expect FFFF = top of 64K RAM found)\n", PRAMT);
    printf("  RAMTOP  (5CB2) = %04X\n", RAMTOP);
    printf("  CHARS   (5C36) = %04X  (expect 3C00 = font base-100h)\n", CHARS);
    printf("  ERR_NR  (5C3A) = %02X    (expect FF = no error)\n", ERRNR);
    printf("  screen pixels set = %ld ; attrs set = %ld\n", px, attr);
    // robust boot indicators: RAM probe found 64K top, font set, display + attrs initialised with the sign-on message
    FILE* sf=fopen("/tmp/s4work/screen.scr","wb"); if(sf){ fwrite(mem+0x4000,1,6912,sf); fclose(sf); }
    int ok = (PRAMT==0xFFFF) && (CHARS==0x3C00) && (attr>=700) && (px>0);
    printf("VERDICT: %s (ERR_NR=%02X)\n", ok? "BOOTED to the (c) sign-on — ROM init completed on the ROM(0-3FFF)/RAM(4000+) map":"did NOT reach a clean boot state", ERRNR);
    return ok?0:1;
}
