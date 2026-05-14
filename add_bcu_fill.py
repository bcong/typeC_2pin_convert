"""
Step 1: Add B.Cu GND zone + improve VBUS routing (4 tracks instead of 5)
NO board.Remove() calls before zone operations to avoid segfault.
Tracks are captured first, removed second, then zone added last before save.
"""
import sys
sys.path.insert(0, r'C:\Program Files\KiCad\10.0\bin')
import pcbnew

board = pcbnew.LoadBoard(r'C:\Users\SEOP\Desktop\usbc_charger\usbc_charger.kicad_pcb')

def mm(x): return pcbnew.FromMM(x)
def pt(x, y): return pcbnew.VECTOR2I(mm(x), mm(y))

# ── 1. Capture + remove old tracks FIRST ──
tv = board.Tracks()
old_tracks = [tv[i] for i in range(tv.size())]
for t in old_tracks:
    board.Remove(t)
print(f"Removed {len(old_tracks)} old tracks", flush=True)

# ── 2. Improved routing ──
net_vbus = board.FindNet('VBUS')
net_cc1  = board.FindNet('CC1')
net_cc2  = board.FindNet('CC2')

def add_track(net, x1, y1, x2, y2, width, layer=pcbnew.F_Cu):
    t = pcbnew.PCB_TRACK(board)
    t.SetNet(net)
    t.SetStart(pt(x1, y1))
    t.SetEnd(pt(x2, y2))
    t.SetWidth(mm(width))
    t.SetLayer(layer)
    board.Add(t)

PAD_Y = 101.449  # J1 signal pad absolute Y

# VBUS: 4 tracks — pad2 up to bridge, bridge right, pad5 straight down, horizontal to J2
# Bridge clears CC pads (pad top edge = 101.449 - 0.7 = 100.749 → use y=100.0)
add_track(net_vbus, 146.980, PAD_Y,   146.980, 100.0,   0.5)  # pad2 → bridge start
add_track(net_vbus, 146.980, 100.0,   150.020, 100.0,   0.5)  # bridge horizontal
add_track(net_vbus, 150.020, 100.0,   150.020, 111.0,   0.5)  # pad5 → J2 level (vertical)
add_track(net_vbus, 150.020, 111.0,   147.500, 111.0,   0.5)  # horizontal → J2.pad1

# CC1: pad3 (148.0, PAD_Y) → R1.pad1 (139.5, 98.5) — 2 tracks
add_track(net_cc1, 148.0, PAD_Y,  148.0, 98.5,  0.25)
add_track(net_cc1, 148.0, 98.5,   139.5, 98.5,  0.25)

# CC2: pad4 (149.0, PAD_Y) → R2.pad1 (157.5, 98.5) — 2 tracks
add_track(net_cc2, 149.0, PAD_Y,  149.0, 98.5,  0.25)
add_track(net_cc2, 149.0, 98.5,   157.5, 98.5,  0.25)

print("Added 8 optimised tracks (VBUS×4, CC1×2, CC2×2)", flush=True)

# ── 3. Add B.Cu GND zone (same boundary as existing F.Cu zone) ──
# Existing F.Cu zone corners: (134,95.5) (163,95.5) (163,114.5) (134,114.5)
gnd_net = board.FindNet('GND')
zone_b = pcbnew.ZONE(board)
zone_b.SetNet(gnd_net)
zone_b.SetLayer(pcbnew.B_Cu)
zone_b.SetLocalClearance(mm(0.5))
zone_b.SetMinThickness(mm(0.25))
zone_b.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
zone_b.SetIsFilled(False)

corners = [(134.0, 95.5), (163.0, 95.5), (163.0, 114.5), (134.0, 114.5)]
for cx, cy in corners:
    zone_b.AppendCorner(pt(cx, cy), -1)

board.Add(zone_b)
print("Added B.Cu GND zone", flush=True)

# ── 4. Save (no Zones() call to avoid segfault) ──
board.Save(r'C:\Users\SEOP\Desktop\usbc_charger\usbc_charger.kicad_pcb')
print("Saved — run fill_zones.py next", flush=True)
