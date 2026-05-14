import pcbnew

pcb_path = r"C:\Users\SEOP\Desktop\usbc_charger\usbc_charger.kicad_pcb"

board = pcbnew.BOARD()
board.GetDesignSettings().SetBoardThickness(pcbnew.FromMM(1.6))

def addNet(board, name, code):
    n = pcbnew.NETINFO_ITEM(board, name, code)
    board.Add(n); return n

nGND  = addNet(board, "GND",  1)
nVBUS = addNet(board, "VBUS", 2)
nCC1  = addNet(board, "CC1",  3)
nCC2  = addNet(board, "CC2",  4)

outline = pcbnew.PCB_SHAPE(board)
outline.SetShape(pcbnew.SHAPE_T_RECT)
outline.SetLayer(pcbnew.Edge_Cuts)
outline.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(0), pcbnew.FromMM(0)))
outline.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(30), pcbnew.FromMM(20)))
outline.SetWidth(pcbnew.FromMM(0.05))
board.Add(outline)

def makeFP(ref, val, fp_name, x_mm, y_mm):
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference(ref); fp.SetValue(val); fp.SetFPIDAsString(fp_name)
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x_mm), pcbnew.FromMM(y_mm)))
    return fp

def addPadSMD(fp, name, rel_x, rel_y, w, h, net):
    pad = pcbnew.PAD(fp)
    pad.SetNumber(name); pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    pad.SetShape(pcbnew.PAD_SHAPE_RECT)
    pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(w), pcbnew.FromMM(h)))
    pad.SetFPRelativePosition(pcbnew.VECTOR2I(pcbnew.FromMM(rel_x), pcbnew.FromMM(rel_y)))
    pad.SetLayerSet(pcbnew.PAD.SMDMask())
    if net: pad.SetNet(net)
    fp.Add(pad); return pad

def addMountHole(fp, name, rel_x, rel_y, drill=0.9):
    """NPTH 고정홀 — USB-C 커넥터 기구 고정용"""
    pad = pcbnew.PAD(fp)
    pad.SetNumber(name); pad.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
    pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(drill), pcbnew.FromMM(drill)))
    pad.SetDrillSize(pcbnew.VECTOR2I(pcbnew.FromMM(drill), pcbnew.FromMM(drill)))
    pad.SetFPRelativePosition(pcbnew.VECTOR2I(pcbnew.FromMM(rel_x), pcbnew.FromMM(rel_y)))
    ls = pcbnew.LSET(); ls.addLayer(pcbnew.F_Cu); ls.addLayer(pcbnew.B_Cu)
    pad.SetLayerSet(ls); fp.Add(pad); return pad

# ---------------------------------------------------------------
# J1: USB-C 6핀 + 4개 고정홀  center=(15, 4.5)
#
# 신호 패드 6개: y=+2.5 (커넥터 하단)
#   pad1(GND)  rel(-2.25, +2.5)
#   pad2(VBUS) rel(-1.35, +2.5)
#   pad3(CC1)  rel(-0.45, +2.5)
#   pad4       rel(+0.45, +2.5)
#   pad5       rel(+1.35, +2.5)
#   pad6(CC2)  rel(+2.25, +2.5)
#
# 고정홀 4개 (NPTH 0.9mm):
#   MP1 앞 왼쪽  rel(-4.0, +1.75)
#   MP2 앞 오른쪽 rel(+4.0, +1.75)
#   MP3 뒤 왼쪽  rel(-4.0, -1.75)
#   MP4 뒤 오른쪽 rel(+4.0, -1.75)
# ---------------------------------------------------------------
j1 = makeFP("J1","USB_C_6Pin","Connector_USB:USB_C_Receptacle_GCT_USB4085",15,4.5)
j1.SetLayer(pcbnew.F_Cu)
addPadSMD(j1,"1",-2.25, 2.5,0.55,1.2,nGND)
addPadSMD(j1,"2",-1.35, 2.5,0.55,1.2,nVBUS)
addPadSMD(j1,"3",-0.45, 2.5,0.55,1.2,nCC1)
addPadSMD(j1,"4", 0.45, 2.5,0.55,1.2,None)
addPadSMD(j1,"5", 1.35, 2.5,0.55,1.2,None)
addPadSMD(j1,"6", 2.25, 2.5,0.55,1.2,nCC2)
addMountHole(j1,"MP1",-4.0, 1.75)
addMountHole(j1,"MP2", 4.0, 1.75)
addMountHole(j1,"MP3",-4.0,-1.75)
addMountHole(j1,"MP4", 4.0,-1.75)
board.Add(j1)

# R1: 세로 배치 center=(6, 4.5)
r1 = makeFP("R1","5.1k","Resistor_SMD:R_0402",6,4.5)
r1.SetLayer(pcbnew.F_Cu)
addPadSMD(r1,"1",0,-1.0,1.0,0.5,nCC1)
addPadSMD(r1,"2",0, 1.0,1.0,0.5,nGND)
board.Add(r1)

# R2: 세로 배치 center=(24, 4.5)
r2 = makeFP("R2","5.1k","Resistor_SMD:R_0402",24,4.5)
r2.SetLayer(pcbnew.F_Cu)
addPadSMD(r2,"1",0,-1.0,1.0,0.5,nCC2)
addPadSMD(r2,"2",0, 1.0,1.0,0.5,nGND)
board.Add(r2)

# H1=(4, 8.4), H2=(26, 8.4) — M3 나사구멍
for ref, x in [("H1",4),("H2",26)]:
    h = makeFP(ref,"MountingHole","MountingHole:MountingHole_3.2mm_M3",x,8.4)
    h.SetLayer(pcbnew.F_Cu)
    pad = pcbnew.PAD(h); pad.SetNumber(""); pad.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
    pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(3.2),pcbnew.FromMM(3.2)))
    pad.SetDrillSize(pcbnew.VECTOR2I(pcbnew.FromMM(3.2),pcbnew.FromMM(3.2)))
    pad.SetFPRelativePosition(pcbnew.VECTOR2I(0,0))
    ls = pcbnew.LSET(); ls.addLayer(pcbnew.F_Cu); ls.addLayer(pcbnew.B_Cu)
    pad.SetLayerSet(ls); h.Add(pad); board.Add(h)

# J2: SMT 2핀 가로 배치 center=(15,16)
j2 = makeFP("J2","Battery_2Pin_SMT","Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_SMD",15,16)
j2.SetLayer(pcbnew.F_Cu)
addPadSMD(j2,"1",-1.27,0,1.6,2.0,nVBUS)
addPadSMD(j2,"2", 1.27,0,1.6,2.0,nGND)
board.Add(j2)

def addTrack(board,x1,y1,x2,y2,w,net):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1),pcbnew.FromMM(y1)))
    t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2),pcbnew.FromMM(y2)))
    t.SetWidth(pcbnew.FromMM(w)); t.SetLayer(pcbnew.F_Cu); t.SetNet(net)
    board.Add(t)

# VBUS: J1-pad2(13.65,7.0) -> J2-pad1(13.73,16.0)
addTrack(board,13.65, 7.0, 13.65,16.0, 0.5, nVBUS)
addTrack(board,13.65,16.0, 13.73,16.0, 0.5, nVBUS)
# CC1: J1-pad3(14.55,7.0) -> R1-pad1(6.0,3.5)
addTrack(board,14.55, 7.0, 14.55, 3.5, 0.25,nCC1)
addTrack(board,14.55, 3.5,  6.0,  3.5, 0.25,nCC1)
# CC2: J1-pad6(17.25,7.0) -> R2-pad1(24.0,3.5)
addTrack(board,17.25, 7.0, 17.25, 3.5, 0.25,nCC2)
addTrack(board,17.25, 3.5, 24.0,  3.5, 0.25,nCC2)

zone = pcbnew.ZONE(board)
zone.SetNet(nGND); zone.SetLayer(pcbnew.F_Cu)
zone.SetAssignedPriority(0)
zone.SetMinThickness(pcbnew.FromMM(0.25))
zone.SetThermalReliefGap(pcbnew.FromMM(0.5))
zone.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.5))
zone.SetLocalClearance(pcbnew.FromMM(0.5))
o2 = zone.Outline(); o2.NewOutline()
for x,y in [(0.5,0.5),(29.5,0.5),(29.5,19.5),(0.5,19.5)]:
    o2.Append(pcbnew.FromMM(x),pcbnew.FromMM(y))
board.Add(zone)

board.Save(pcb_path)
b2 = pcbnew.LoadBoard(pcb_path)
print("OK nets:", b2.GetNetCount() if b2 else "-")
