import sys
sys.path.insert(0, r'C:\Program Files\KiCad\10.0\bin')
import pcbnew

# NOTE: board was saved without J1 in previous failed run, reload from scratch
board = pcbnew.LoadBoard(r'C:\Users\SEOP\Desktop\usbc_charger\usbc_charger.kicad_pcb')

def mm(x): return pcbnew.FromMM(x)
def pt(x, y): return pcbnew.VECTOR2I(mm(x), mm(y))

# ── Pre-capture tracks BEFORE any board modifications ──
# board.Tracks() returns TRACKS type only on unmodified board
tv = board.Tracks()
tracks_snap = [tv[i] for i in range(tv.size())]
print(f"Captured {len(tracks_snap)} tracks")

# ── 1. Remove old J1 footprint ──
for fp in list(board.GetFootprints()):
    if fp.GetReference() == 'J1':
        board.Remove(fp)
        print("Removed old J1")

# ── 2. Remove all existing traces ──
for track in tracks_snap:
    board.Remove(track)
print(f"Removed {len(tracks_snap)} tracks")

# ── 3. Create new J1 footprint ──
j1 = pcbnew.FOOTPRINT(board)
j1.SetReference('J1')
j1.SetValue('USB_C_6PIN')
board.Add(j1)
j1.SetPosition(pt(148.5, 99.5))

# Reference text position (above component, outside board)
try:
    j1.Reference().SetPos0(pcbnew.VECTOR2I(mm(0), mm(-5.0)))
    j1.Reference().SetLayer(pcbnew.F_SilkS)
    j1.Value().SetPos0(pcbnew.VECTOR2I(mm(0), mm(3.0)))
    j1.Value().SetLayer(pcbnew.F_Fab)
    j1.Value().SetVisible(False)
except Exception as e:
    print(f"  Reference/value text warning (non-fatal): {e}")

# Signal pads: (number, net_name, x_rel_mm)
# EasyEDA data (mils→mm *0.0254): B12(-2.750), B9(-1.520), A5(-0.500), B5(+0.500), A9(+1.520), A12(+2.750)
# All signal pads at y_rel = +1.949mm from center (connector opening toward board edge)
SIG_Y = 1.949
signal_pads = [
    ('1', 'GND',  -2.750),  # B12
    ('2', 'VBUS', -1.520),  # B9
    ('3', 'CC1',  -0.500),  # A5
    ('4', 'CC2',  +0.500),  # B5
    ('5', 'VBUS', +1.520),  # A9
    ('6', 'GND',  +2.750),  # A12
]

for num, net_name, x_rel in signal_pads:
    pad = pcbnew.PAD(j1)
    pad.SetNumber(num)
    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    pad.SetLayerSet(pcbnew.PAD.SMDMask())
    pad.SetShape(pcbnew.PAD_SHAPE_RECT)
    pad.SetSize(pcbnew.VECTOR2I(mm(0.8), mm(1.4)))
    pad.SetFPRelativePosition(pt(x_rel, SIG_Y))
    net = board.FindNet(net_name)
    if net:
        pad.SetNet(net)
    j1.Add(pad)

# Mounting tabs: 4x PTH slots (EasyEDA data converted from mils *0.0254)
# e38:(-4.320,-1.951) e39:(-4.320,+1.849) e37:(+4.320,-1.931) e40:(+4.320,+1.849)
# Drill: 0.5mm(W) x 1.2mm(H) OBLONG (90-deg rotated), outer pad: 1.0mm x 1.7mm
mount_tabs = [
    ('M1', -4.320, -1.951),
    ('M2', -4.320, +1.849),
    ('M3', +4.320, -1.931),
    ('M4', +4.320, +1.849),
]

for num, x_rel, y_rel in mount_tabs:
    pad = pcbnew.PAD(j1)
    pad.SetNumber(num)
    pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
    pad.SetLayerSet(pcbnew.PAD.PTHMask())
    pad.SetShape(pcbnew.PAD_SHAPE_OVAL)
    pad.SetSize(pcbnew.VECTOR2I(mm(1.0), mm(1.7)))
    # Oblong drill: width=0.5mm, height=1.2mm (vertical slot)
    try:
        pad.SetDrillShape(pcbnew.PAD_DRILL_SHAPE_OBLONG)
        pad.SetDrillSize(pcbnew.VECTOR2I(mm(0.5), mm(1.2)))
    except Exception as e:
        print(f"  Drill shape warning: {e} - using circle fallback")
        pad.SetDrillSize(pcbnew.VECTOR2I(mm(1.0), mm(1.0)))
    pad.SetFPRelativePosition(pt(x_rel, y_rel))
    net = board.FindNet('GND')
    if net:
        pad.SetNet(net)
    j1.Add(pad)

# Courtyard: from EasyEDA POLY outline (mils→mm)
# x: ±175.984 mils = ±4.470mm, y: -179.172 to +88.545 mils = -4.549 to +2.249mm
crtyd_pts = [(-4.47, -4.55), (4.47, -4.55), (4.47, 2.25), (-4.47, 2.25)]
for i in range(4):
    seg = pcbnew.PCB_SHAPE(j1)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetLayer(pcbnew.F_CrtYd)
    seg.SetWidth(mm(0.05))
    x0, y0 = crtyd_pts[i]
    x1, y1 = crtyd_pts[(i + 1) % 4]
    seg.SetStart(pcbnew.VECTOR2I(mm(x0), mm(y0)))
    seg.SetEnd(pcbnew.VECTOR2I(mm(x1), mm(y1)))
    j1.Add(seg)

# Silkscreen body outline (F.SilkS) – simplified rectangle
silk_pts = [(-4.47, -4.55), (4.47, -4.55), (4.47, 2.0), (-4.47, 2.0)]
for i in range(4):
    seg = pcbnew.PCB_SHAPE(j1)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetLayer(pcbnew.F_SilkS)
    seg.SetWidth(mm(0.12))
    x0, y0 = silk_pts[i]
    x1, y1 = silk_pts[(i + 1) % 4]
    seg.SetStart(pcbnew.VECTOR2I(mm(x0), mm(y0)))
    seg.SetEnd(pcbnew.VECTOR2I(mm(x1), mm(y1)))
    j1.Add(seg)

print("Created new J1 footprint with correct dimensions")

# ── 4. Add new traces ──
net_vbus = board.FindNet('VBUS')
net_cc1  = board.FindNet('CC1')
net_cc2  = board.FindNet('CC2')

def add_track(net, x1, y1, x2, y2, width=0.25):
    t = pcbnew.PCB_TRACK(board)
    t.SetNet(net)
    t.SetStart(pt(x1, y1))
    t.SetEnd(pt(x2, y2))
    t.SetWidth(mm(width))
    t.SetLayer(pcbnew.F_Cu)
    board.Add(t)

# Signal pad absolute Y = 99.5 + 1.949 = 101.449
PAD_Y = 99.5 + SIG_Y  # = 101.449

# VBUS: J1.B9(x=146.98) -> down to J2.pin1(147.5, 111.0)
add_track(net_vbus, 146.98, PAD_Y, 146.98, 111.0, 0.5)
add_track(net_vbus, 146.98, 111.0, 147.5,  111.0, 0.5)

# VBUS bridge: A9(150.02) to B9(146.98) via y=100.0 (above pads to avoid CC pads)
add_track(net_vbus, 146.98, PAD_Y, 146.98, 100.0, 0.5)
add_track(net_vbus, 146.98, 100.0, 150.02, 100.0, 0.5)
add_track(net_vbus, 150.02, 100.0, 150.02, PAD_Y, 0.5)

# CC1: J1.A5(x=148.0) -> R1.pad1(139.5, 98.5)
add_track(net_cc1, 148.0, PAD_Y, 148.0, 98.5, 0.25)
add_track(net_cc1, 148.0, 98.5,  139.5, 98.5, 0.25)

# CC2: J1.B5(x=149.0) -> R2.pad1(157.5, 98.5)
add_track(net_cc2, 149.0, PAD_Y, 149.0, 98.5, 0.25)
add_track(net_cc2, 149.0, 98.5,  157.5, 98.5, 0.25)

print("Added corrected traces")

# ── 5. Zone fill ──
# board.Zones() causes segfault in pcbnew 10 after Remove() calls → skip entirely
# KiCad GUI will prompt to refill zones on next open

# ── 6. Save ──
import sys as _sys; _sys.stdout.flush()
print("About to save...")
board.Save(r'C:\Users\SEOP\Desktop\usbc_charger\usbc_charger.kicad_pcb')
print("Board saved OK")
_sys.stdout.flush()

# ── Verify ──
print("\n=== J1 pads (absolute positions) ===")
_sys.stdout.flush()
board2 = pcbnew.LoadBoard(r'C:\Users\SEOP\Desktop\usbc_charger\usbc_charger.kicad_pcb')
for fp in board2.GetFootprints():
    if fp.GetReference() == 'J1':
        for pad in sorted(fp.Pads(), key=lambda p: pcbnew.ToMM(p.GetPosition().x)):
            px = pcbnew.ToMM(pad.GetPosition().x)
            py = pcbnew.ToMM(pad.GetPosition().y)
            a  = {0:'PTH',1:'SMD',2:'CONN',3:'NPTH'}.get(pad.GetAttribute(),'?')
            print(f"  pad {pad.GetNumber():3s} {a}  ({px:.3f}, {py:.3f})  net={pad.GetNetname()}")
_sys.stdout.flush()
print("\n=== Tracks ===")
tv2 = board2.Tracks()
for i in range(tv2.size()):
    t = tv2[i]; s = t.GetStart(); e = t.GetEnd()
    print(f"  ({pcbnew.ToMM(s.x):.2f},{pcbnew.ToMM(s.y):.2f})->({pcbnew.ToMM(e.x):.2f},{pcbnew.ToMM(e.y):.2f})  net={t.GetNetname()}")
_sys.stdout.flush()
