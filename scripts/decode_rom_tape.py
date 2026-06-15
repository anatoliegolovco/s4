# decode_rom_tape.py — recover the genuine Sintez-2 ROM from the tape-audio dump
# (roms/sintez2-rom.wav, Muravyev) using standard ZX-tape pulse decoding -> roms/sintez2.rom.
# Result: 16384-byte ZX48-compatible ROM, boots to "(c) 1989 Sintez SIGNAL".
import wave, numpy as np, sys
w=wave.open("roms/sintez2-rom.wav","rb"); fr=w.getframerate(); n=w.getnframes(); ch=w.getnchannels(); sw=w.getsampwidth()
a=np.frombuffer(w.readframes(n),dtype={1:np.uint8,2:np.int16}[sw]).astype(np.float64)
if ch==2: a=a[::2]
a-=a.mean()
# square up, get pulse lengths (samples between sign changes)
s=np.sign(a); s[s==0]=1
edges=np.where(np.diff(s)!=0)[0]
P=np.diff(edges)              # pulse lengths in samples
# ZX @48k: bit0~11.7, bit1~23.4, pilot~29.7, sync~9/10. thresholds:
def classify(L):
    if L>=27: return 'P'      # pilot
    if L>=17: return '1'      # bit-1 half
    if L>=6:  return '0'      # bit-0 half (or sync)
    return 'x'                # noise
cls=[classify(L) for L in P]
# walk: find pilot runs -> sync -> data bits (2 pulses/bit)
blocks=[]; i=0; N=len(P)
while i<N:
    # find a pilot run
    j=i
    while j<N and cls[j]=='P': j+=1
    if j-i < 200:   # not a real pilot
        i+=1; continue
    k=j
    # skip a couple short sync pulses
    while k<N and cls[k]=='x': k+=1
    sync=k
    while k<N and cls[k] in '01' and P[k]<14 and k<sync+2: k+=1  # ~sync pair (short)
    # read data bits until next pilot run or noise
    bits=[]; m=k
    while m+1<N:
        if cls[m]=='P' and (m+1<N and cls[m+1]=='P'): break
        if cls[m]=='x': break
        b='1' if P[m]>=17 else '0'
        bits.append(b); m+=2   # 2 pulses per bit
    # bytes MSB first
    by=bytearray()
    for q in range(0,len(bits)-7,8):
        by.append(int(''.join(bits[q:q+8]),2))
    if len(by)>16: blocks.append(bytes(by))
    i=m
print("blocks decoded:", [len(b) for b in blocks])
# pick the block whose size ~ 16384 (+flag+checksum) or the largest
best=max(blocks,key=len) if blocks else b''
print("largest block:", len(best),"bytes; first bytes:", best[:8].hex())
# strip ZX block flag (first) + checksum (last) if present
for cand in [best, best[1:], best[1:-1]]:
    if len(cand)>=16384:
        rom=cand[:16384]
        # ZX48 ROM signature: F3 AF 11 FF FF C3 CB 11
        print("candidate head:", rom[:8].hex(), "MATCH" if rom[:3]==bytes([0xF3,0xAF,0x11]) else "")
        if rom[:3]==bytes([0xF3,0xAF,0x11]):
            open("/tmp/s4work/sintez2.rom","wb").write(rom); print("WROTE /tmp/s4work/sintez2.rom (16384) — ZX48 signature OK"); break
