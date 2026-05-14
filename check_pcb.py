import sys; sys.path.insert(0, r'C:\Program Files\KiCad\10.0\bin')
import pcbnew
board = pcbnew.LoadBoard(r'C:\Users\SEOP\Desktop\usbc_charger\usbc_charger.kicad_pcb')

print('=== BOARD EDGES ===')
for d in board.GetDrawings():
    if d.GetLayer() == pcbnew.Edge_Cuts:
        s = d.GetStart(); e = d.GetEnd()
        print(f'  ({pcbnew.ToMM(s.x):.2f},{pcbnew.ToMM(s.y):.2f}) -> ({pcbnew.ToMM(e.x):.2f},{pcbnew.ToMM(e.y):.2f})')

print()
print('=== ALL FOOTPRINTS (pads) ===')
ATTR = {0:'PTH', 1:'SMD', 2:'CONN', 3:'NPTH'}
for fp in sorted(board.GetFootprints(), key=lambda f: f.GetReference()):
    cx = pcbnew.ToMM(fp.GetX()); cy = pcbnew.ToMM(fp.GetY())
    print(f'{fp.GetReference():4s}  center=({cx:.2f},{cy:.2f})')
    for pad in fp.Pads():
        px = pcbnew.ToMM(pad.GetPosition().x)
        py = pcbnew.ToMM(pad.GetPosition().y)
        attr = ATTR.get(pad.GetAttribute(), '?')
        sz = pad.GetSize()
        sw = pcbnew.ToMM(sz.x); sh = pcbnew.ToMM(sz.y)
        print(f'     pad {pad.GetNumber():4s}  {attr}  abs=({px:.3f},{py:.3f})  size={sw:.3f}x{sh:.3f}  net={pad.GetNetname()}')

print()
print('=== TRACKS ===')
for t in board.GetTracks():
    s = t.GetStart(); e = t.GetEnd()
    print(f'  ({pcbnew.ToMM(s.x):.2f},{pcbnew.ToMM(s.y):.2f}) -> ({pcbnew.ToMM(e.x):.2f},{pcbnew.ToMM(e.y):.2f})  net={t.GetNetname()}  w={pcbnew.ToMM(t.GetWidth()):.2f}')
