"""
Reroute traces after J1 USB-C rotation change (180 -> 0 deg).
New J1 pad positions (footprint at 15,-15.5, rot 0):
  pad1 GND  : (12.25, -13.551)
  pad2 VBUS : (13.48, -13.551)
  pad3 CC1  : (14.5,  -13.551)
  pad4 CC2  : (15.5,  -13.551)
  pad5 VBUS : (16.52, -13.551)
  pad6 GND  : (17.75, -13.551)
R1 (6,-17.1) rot90: pad1 CC1=(6,-17.53)  pad2 GND=(6,-16.67)
R2 (24,-17.1) rot90: pad1 CC2=(24,-17.53) pad2 GND=(24,-16.67)
J2 (15,-4)   rot0: pad1 VBUS=(13.73,-4)  pad2 GND=(16.27,-4)
"""
import sys, os

try:
    import pcbnew
except ImportError:
    sys.exit("pcbnew not found – run with KiCad Python")

PCB_PATH = os.path.join(os.path.dirname(__file__), "usbc_charger.kicad_pcb")

board = pcbnew.LoadBoard(PCB_PATH)

# ── 1. Remove all existing segments ──────────────────────────────────────────
to_remove = [t for t in board.GetTracks()
             if t.GetClass() == "PCB_TRACK"]
for t in to_remove:
    board.Remove(t)
print(f"Removed {len(to_remove)} old segments")

# ── 2. Helper ─────────────────────────────────────────────────────────────────
def seg(x1, y1, x2, y2, w, net_name):
    net = board.FindNet(net_name)
    if net is None:
        raise ValueError(f"Net '{net_name}' not found")
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
    t.SetEnd  (pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
    t.SetWidth(pcbnew.FromMM(w))
    t.SetLayer(pcbnew.F_Cu)
    t.SetNet(net)
    board.Add(t)

# ── 3. New routes ─────────────────────────────────────────────────────────────
# CC1  J1-pad3 (14.5,-13.551) → R1-pad1 (6,-17.53)   0.25mm
seg(14.5, -13.551, 14.5, -15.0,   0.25, "CC1")
seg(14.5, -15.0,   6.0, -15.0,    0.25, "CC1")
seg( 6.0, -15.0,   6.0, -17.53,   0.25, "CC1")

# CC2  J1-pad4 (15.5,-13.551) → R2-pad1 (24,-17.53)  0.25mm
seg(15.5, -13.551, 15.5, -15.0,   0.25, "CC2")
seg(15.5, -15.0,  24.0, -15.0,    0.25, "CC2")
seg(24.0, -15.0,  24.0, -17.53,   0.25, "CC2")

# VBUS  J1-pad2 (13.48,-13.551) → J2-pad1 (13.73,-4) 0.5mm
seg(13.48, -13.551, 13.48, -4.0,  0.5, "VBUS")
seg(13.48,  -4.0,   13.73, -4.0,  0.5, "VBUS")

# VBUS  J1-pad5 (16.52,-13.551) → join bus at (13.48,-12)  0.5mm
seg(16.52, -13.551, 16.52, -12.0, 0.5, "VBUS")
seg(16.52, -12.0,   13.48, -12.0, 0.5, "VBUS")

print("Added 10 new segments")

# ── 4. Rebuild connectivity + refill GND zone ─────────────────────────────────
board.BuildConnectivity()
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())
print("Zone refilled")

# ── 5. Save ───────────────────────────────────────────────────────────────────
board.Save(PCB_PATH)
print(f"Saved: {PCB_PATH}")
