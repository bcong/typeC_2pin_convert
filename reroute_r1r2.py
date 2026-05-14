import sys; sys.path.insert(0,'.')
import pcbnew

board = pcbnew.LoadBoard(r'C:\Users\SEOP\Desktop\usbc_charger\usbc_charger.kicad_pcb')
def mm(x): return pcbnew.FromMM(x)
def pt(x,y): return pcbnew.VECTOR2I(mm(x), mm(y))
def f(v): return round(pcbnew.ToMM(v), 3)

# 1. Move components
for fp in board.GetFootprints():
    ref = fp.GetReference()
    if ref == 'R1':
        fp.SetPosition(pt(139.5, 97.9))
        print('R1 -> (139.5, 97.9)', flush=True)
    elif ref == 'R2':
        fp.SetPosition(pt(157.5, 97.9))
        print('R2 -> (157.5, 97.9)', flush=True)
    elif ref == 'H1':
        fp.SetPosition(pt(141.0, 102.9))
        print('H1 -> (141.0, 102.9)', flush=True)
    elif ref == 'H2':
        fp.SetPosition(pt(156.0, 102.9))
        print('H2 -> (156.0, 102.9)', flush=True)

# 2. Pre-capture all tracks before any Remove
tv = board.Tracks()
snap = [tv[i] for i in range(tv.size())]

remove_set = {
    ((148.0, 101.449), (148.0, 98.5)),     # CC1 vertical old
    ((148.0, 98.5),    (139.5, 98.5)),     # CC1 horizontal old
    ((149.0, 101.449), (149.0, 98.5)),     # CC2 vertical old
    ((149.0, 98.5),    (157.5, 98.5)),     # CC2 horizontal old
    ((146.98, 101.449),(146.98, 100.0)),   # VBUS up (buggy bridge)
    ((146.98, 100.0),  (150.02, 100.0)),   # VBUS horizontal (buggy bridge)
    ((150.02, 100.0),  (150.02, 101.449)), # VBUS down (buggy bridge)
}

for t in snap:
    if not hasattr(t, 'GetStart'):
        continue
    sx, sy = f(t.GetStart().x), f(t.GetStart().y)
    ex, ey = f(t.GetEnd().x), f(t.GetEnd().y)
    if ((sx,sy),(ex,ey)) in remove_set or ((ex,ey),(sx,sy)) in remove_set:
        board.Remove(t)
        print(f'Removed: ({sx},{sy})->({ex},{ey})', flush=True)

# 3. Add new tracks
def add_track(x1, y1, x2, y2, net_name, width_mm=0.25):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pt(x1, y1))
    t.SetEnd(pt(x2, y2))
    t.SetWidth(mm(width_mm))
    t.SetLayer(pcbnew.F_Cu)
    t.SetNet(board.FindNet(net_name))
    board.Add(t)
    print(f'Added {net_name}: ({x1},{y1})->({x2},{y2})', flush=True)

# CC1: above USB-C PTH holes (M1/M3 at y~97.5, trace at y=96.9)
add_track(148.0, 101.449, 148.0, 96.9,  'CC1', 0.25)
add_track(148.0, 96.9,    139.5, 96.9,  'CC1', 0.25)

# CC2: symmetric
add_track(149.0, 101.449, 149.0, 96.9,  'CC2', 0.25)
add_track(149.0, 96.9,    157.5, 96.9,  'CC2', 0.25)

# VBUS: new bridge below pads at y=103 (pad5 -> down -> left to main vertical)
add_track(150.02, 101.449, 150.02, 103.0, 'VBUS', 0.5)
add_track(150.02, 103.0,   146.98, 103.0, 'VBUS', 0.5)

board.Save(r'C:\Users\SEOP\Desktop\usbc_charger\usbc_charger.kicad_pcb')
print('Saved', flush=True)

# Verify
board2 = pcbnew.LoadBoard(r'C:\Users\SEOP\Desktop\usbc_charger\usbc_charger.kicad_pcb')
print('\n=== Verify components ===', flush=True)
for fp in board2.GetFootprints():
    ref = fp.GetReference()
    cx, cy = f(fp.GetX()), f(fp.GetY())
    if ref in ('R1','R2','H1','H2'):
        print(f'  {ref}: ({cx},{cy})  board-rel=({round(cx-133.5,1)},{round(cy-95.0,1)})', flush=True)
print('\n=== Verify tracks ===', flush=True)
tv2 = board2.Tracks()
for i in range(tv2.size()):
    t = tv2[i]
    if hasattr(t,'GetStart'):
        sx,sy = f(t.GetStart().x), f(t.GetStart().y)
        ex,ey = f(t.GetEnd().x), f(t.GetEnd().y)
        print(f'  {t.GetNetname()}: ({sx},{sy})->({ex},{ey})', flush=True)
