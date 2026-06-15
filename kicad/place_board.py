#!/usr/bin/env python3
"""Seed placement for the Sintez-2 PCB: spread the kinet2pcb-stacked footprints into
a grid and add a rectangular Edge.Cuts board outline. Run once after kinet2pcb.
    PYTHONPATH=/usr/lib/python3/dist-packages python3 kicad/place_board.py
"""
import sys, math
sys.path.insert(0, "/usr/lib/python3/dist-packages")
import pcbnew
B = "/home/anatolie/ai3/s4/kicad/sintez2.kicad_pcb"
bd = pcbnew.LoadBoard(B)
fps = list(bd.GetFootprints())
fps.sort(key=lambda f: f.GetReference())
MM = pcbnew.FromMM
cols, dx, dy, x0, y0 = 9, 33.0, 28.0, 20.0, 20.0
for i, fp in enumerate(fps):
    x = x0 + (i % cols) * dx; y = y0 + (i // cols) * dy
    fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
# remove any existing Edge.Cuts shapes (idempotent re-run)
for d in list(bd.GetDrawings()):
    if d.GetLayer()==bd.GetLayerID('Edge.Cuts'): bd.Remove(d)
rows = math.ceil(len(fps) / cols)
W = x0 * 2 + cols * dx; H = y0 * 2 + rows * dy
# board outline on Edge.Cuts
ec = bd.GetLayerID("Edge.Cuts")
pts = [(0, 0), (W, 0), (W, H), (0, H), (0, 0)]
for (ax, ay), (bx, by) in zip(pts, pts[1:]):
    seg = pcbnew.PCB_SHAPE(bd); seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetStart(pcbnew.VECTOR2I(MM(ax), MM(ay))); seg.SetEnd(pcbnew.VECTOR2I(MM(bx), MM(by)))
    seg.SetLayer(ec); seg.SetWidth(MM(0.15)); bd.Add(seg)
pcbnew.SaveBoard(B, bd)
print(f"placed {len(fps)} footprints in {cols}x{rows} grid; board {W:.0f}x{H:.0f} mm")
