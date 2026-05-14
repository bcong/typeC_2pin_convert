"""
Step 2: Fill all zones (fresh board load — no Remove() calls to avoid segfault).
"""
import sys
sys.path.insert(0, r'C:\Program Files\KiCad\10.0\bin')
import pcbnew

board = pcbnew.LoadBoard(r'C:\Users\SEOP\Desktop\usbc_charger\usbc_charger.kicad_pcb')
print(f"Zones found: {len(list(board.Zones()))}", flush=True)
for z in board.Zones():
    print(f"  {z.GetNetname()} layer={z.GetLayer()} filled={z.IsFilled()}", flush=True)

filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())

for z in board.Zones():
    print(f"  after fill: {z.GetNetname()} layer={z.GetLayer()} filled={z.IsFilled()}", flush=True)

board.Save(r'C:\Users\SEOP\Desktop\usbc_charger\usbc_charger.kicad_pcb')
print("Zones filled and saved", flush=True)
