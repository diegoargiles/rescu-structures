"""Fuselage (R12/R13 layout) rebuilt for R15: split GFRP shell, frames, hatches, decks, bays, tail and pusher interfaces."""
import cadquery as cq, numpy as np, sys
from geom import *
def ring_frame(x, t, r_in_off, zcut=None, keep='all'):
    o = fus_solid(FWALL + 0.3, x, x+t); i = fus_solid(FWALL + r_in_off, x - 1, x + t + 1)
    f = o.cut(i)
    if zcut is not None: f = f.intersect(box(x-1, x+t+1, -60, 60, -60, zcut))
    return f
def lower_bulkhead(x, t, ztop, holes=()):
    """bonded lower frame/saddle: fuselage interior below ztop, lightened centre"""
    o = fus_solid(FWALL + 0.3, x, x+t).intersect(box(x-1, x+t+1, -60, 60, -60, ztop))
    light = fus_solid(FWALL + 7.0, x-1, x+t+1).intersect(box(x-2, x+t+2, -60, 60, -60, ztop - 6.0))
    return o.cut(light)
def build_fuselage(log=print):
    P = {}
    outer = fus_solid(); inner = fus_solid(FWALL)
    shell = outer.cut(inner); log('shell')
    # top openings (hatches) and wing/tail through-holes
    def top_opening(x0, x1, half_w, zmin=18.0):
        return box(x0, x1, -half_w, half_w, zmin, 60)
    op_front, op_rear, op_tail = top_opening(192, 280, 33), top_opening(321.5, 407, 33), top_opening(962, 1048, 16, 10)
    hatch_f = shell.intersect(top_opening(192.4, 279.6, 32.6)); hatch_r = shell.intersect(top_opening(321.9, 406.6, 32.6))
    hatch_t = shell.intersect(top_opening(962.4, 1047.6, 15.6, 10))
    shell = shell.cut(op_front).cut(op_rear).cut(op_tail)
    for yy in (-1, 1):
        shell = shell.cut(cyly(310, 4.2, 6.1, yy*30, yy*60) if yy > 0 else cyly(310, 4.2, 6.1, -60, -30))
        shell = shell.cut(cyly(385, 3.0, 1.6, *(sorted((yy*30, yy*60)))))
        shell = shell.cut(cyly(CONDUIT_X_ROOT, CONDUIT_Z, 3.1, *(sorted((yy*30, yy*60)))))
    log('openings')
    # split into left/right moulded halves + internal seam joining strips (top & bottom)
    sh_R = shell.intersect(box(-5, FL+5, 0, 60, -60, 60)); sh_L = shell.intersect(box(-5, FL+5, -60, 0, -60, 60))
    band = fus_solid(FWALL).cut(fus_solid(FWALL + 0.3))
    seams = band.intersect(box(5, 1068, -6, 6, -60, 60))
    for (x0, x1, hw) in ((192, 280, 33), (321.5, 407, 33), (962, 1048, 16)): seams = seams.cut(box(x0-6, x1+6, -hw-6, hw+6, 0, 60))
    # hatch support rims (bonded ledge under each opening)
    rims = None
    for (x0, x1, hw, zm) in ((192, 280, 33, 18.0), (321.5, 407, 33, 18.0), (962, 1048, 16, 10.0)):
        r = fus_solid(FWALL).cut(fus_solid(FWALL + 1.0)).intersect(box(x0-5, x1+5, -hw-5, hw+5, zm-4, 60)).cut(box(x0+1, x1-1, -hw+1, hw-1, zm-10, 60))
        rims = r if rims is None else rims.union(r)
    log('halves')
    # frames: wing carry-through frames F282/F320, tail frames, avionics/ESC lower frames, battery saddles
    frames = ring_frame(282, 1.5, 7.0).union(ring_frame(320, 1.5, 7.0)).union(ring_frame(990, 2.0, 6.0)).union(ring_frame(1021, 2.0, 6.0))
    for (x0, x1, hw, zm) in ((192, 280, 33, 18.0), (321.5, 407, 33, 18.0), (962, 1048, 16, 10.0)):
        frames = frames.cut(box(x0-6, x1+6, -hw-6, hw+6, zm-5, 60))
    lower = None
    for (x, t, zt) in ((135, 1.5, -5.0), (170, 1.5, -5.0), (445, 1.5, -17.0), (550, 1.5, -17.0),
                       (199.5, 2, -25.6), (273.5, 2, -25.6), (324.5, 2, -25.6), (398.5, 2, -25.6)):
        b = lower_bulkhead(x, t, zt)
        lower = b if lower is None else lower.union(b)
    lower = lower.cut(box(274, 325, -3.2, 3.2, -36.5, -29.5))           # inter-bay harness corridor
    log('frames')
    # decks, trays, rails, receivers
    av_deck = box(130, 175, -25, 25, -5.0, -4.0)
    av_strips = box(132, 173, -22, -18, -4.0, -2.5).union(box(132, 173, 18, 22, -4.0, -2.5))
    esc_deck = box(435, 565, -29, 29, -17, -16)
    esc_pads = None
    for x0 in (437.2, 507.2):
        for yy in (2.4, -27.6):
            p = box(x0, x0+55.6, yy, yy+25.2, -16.0, -15.5); esc_pads = p if esc_pads is None else esc_pads.union(p)
    trays = []; stops = []
    for (x0, x1) in ((196.0, 279.0), (321.8, 404.0)):
        t = box(x0, x1, -35.2, 35.2, -25.5, -24.5).union(box(x0, x1, -35.2, -34.2, -25.5, -19.0)).union(box(x0, x1, 34.2, 35.2, -25.5, -19.0))
        trays.extend(t.intersect(inner).vals())
    for (x0, x1) in ((196.5, 199.5), (275.5, 278.5), (322.0, 324.6), (400.4, 403.4)):
        stops.extend(box(x0, x1, -20, 20, -24.5, -15.0).vals())
    trays = cq.Workplane().add(trays); stops = cq.Workplane().add(stops)
    pads = cq.Workplane().add(box(200.5, 274.5, -33.5, 33.5, -24.5, -22.2).vals() + box(325.5, 399.5, -33.5, 33.5, -24.5, -22.2).vals())
    joiner = tube_between((310, -100, 4.2), (310, 100, 4.2), 6.0, 5.0)        # R15: OD12/ID10 (was OD8/ID6)
    recv = tube_between((310, 2.2, 4.2), (310, 37, 4.2), 7.4, 6.1).union(tube_between((310, -37, 4.2), (310, -2.2, 4.2), 7.4, 6.1))
    stop_ring = tube_between((310, -2.0, 4.2), (310, 2.0, 4.2), 7.0, 6.05)
    rails = None
    for sg in (1, -1):
        r = box(283.5, 402, sg*41.0 - 1.0, sg*41.0 + 1.0, -5.0, 10.0).intersect(inner)
        r = r.cut(cyly(310, 4.2, 7.5, -60, 60)).cut(cyly(385, 3.0, 1.6, -60, 60)).cut(cyly(CONDUIT_X_ROOT, CONDUIT_Z, 3.1, -60, 60))
        r = r.cut(box(281.9, 283.6, -60, 60, -60, 60)).cut(box(319.9, 321.6, -60, 60, -60, 60))
        rails = r if rails is None else rails.union(r)
    log('decks')
    # tail interfaces: V-tail root receivers (sleeves along spar root axis), pusher collar + Al plate
    a = np.radians(TDIH); recvs = None; tail_holes = None
    for sg in (1, -1):
        e = np.array([0, sg*np.cos(a), np.sin(a)])
        def spt(s): return np.array([txle(s) + 0.30*tchord(s), 0, 0]) + e*s
        def ppt(s): return np.array([TLE + 0.60*TCR, 0, 0]) + e*s
        r = tube_between(tuple(spt(3.5)), tuple(spt(22.0)), 4.2, 3.05)
        recvs = r if recvs is None else recvs.union(r)
        h = tube_between(tuple(spt(0)), tuple(spt(45)), 3.1).union(tube_between(tuple(ppt(0)), tuple(ppt(45)), 1.6))
        tail_holes = h if tail_holes is None else tail_holes.union(h)
    sh_R = sh_R.cut(tail_holes); sh_L = sh_L.cut(tail_holes); rims = rims.cut(tail_holes)
    frames = frames.cut(tube_between(tuple(spt(0)*np.array([1,0,0])+np.array([0,0,0])), tuple(spt(0)), 0.1)) if False else frames
    for sg in (1, -1):
        e = np.array([0, sg*np.cos(a), np.sin(a)])
        frames = frames.cut(tube_between(tuple(np.array([txle(0)+0.3*tchord(0), 0, 0])), tuple(np.array([txle(40)+0.3*tchord(40), 0, 0]) + e*40), 4.3))
    collar = fus_solid(FWALL, 1072, 1102).cut(fus_solid(FWALL + 2.0, 1071, 1103))
    flange = cylx(0, 0, 24.5, 1100, 1102).cut(cylx(0, 0, 11.0, 1099, 1103)).intersect(fus_solid(FWALL, 1099, 1103))
    plate = cylx(0, 0, 24.5, 1102, 1103.5).cut(cylx(0, 0, 6.0, 1101, 1105))
    for yy, zz in ((15, 15), (-15, 15), (-15, -15), (15, -15)):
        plate = plate.cut(cylx(yy, zz, 1.65, 1101, 1105))
    log('tail ifaces')
    P.update(Fuselage_Shell_Right_GFRP=sh_R, Fuselage_Shell_Left_GFRP=sh_L, Fuselage_Seam_Strips_GFRP=seams,
             Hatch_Front_GFRP=hatch_f, Hatch_Rear_GFRP=hatch_r, Hatch_Tail_GFRP=hatch_t, Hatch_Rims_GFRP=rims,
             Frames_Ring_GFRP=frames, Frames_Lower_and_Battery_Saddles_GFRP=lower, Avionics_Deck_GFRP=av_deck,
             Avionics_Adjust_Strips=av_strips, ESC_Deck_GFRP=esc_deck, ESC_Pads_Foam=esc_pads,
             Battery_Trays_GFRP=trays, Battery_End_Stops_GFRP=stops, Battery_Insulating_Pads_Foam=pads, Wing_Joiner_CFRP_OD12=joiner,
             Joiner_Receiver_Sleeves_GFRP=recv, Joiner_Axial_Stop_Ring=stop_ring, Wing_Root_Side_Rails_GFRP=rails,
             VTail_Root_Receivers_GFRP=recvs, Pusher_Bonded_Collar_GFRP=collar.union(flange),
             Pusher_Removable_Plate_6061=plate)
    return P
def build_refs():
    R = {}
    mods = None; cells = None
    for x0 in (200.0, 325.0):
        m = box(x0, x0+75, -34, 34, -22.2, 24.8); mods = m if mods is None else mods.union(m)
        for iy in range(3):
            for iz in range(2):
                c = cylx(-21.7 + iy*21.7, -10.25 + iz*22.5, 10.85, x0+2, x0+73)
                cells = c if cells is None else cells.union(c)
    R['REF_Battery_Modules_75x68x47'] = mods; R['REF_M65A_Cells_6S2P'] = cells
    R['REF_Flight_Controller_Cube'] = box(105.5, 199.5, -22, 22, -2.5, 15.0)
    R['REF_Receiver'] = box(176, 196, -10, 10, 15.5, 25.0)
    R['REF_Camera_AI_PROVISIONAL'] = cylx(0, 0, 20, 40, 100)
    esc = None
    for x0 in (437.2, 507.2):
        for yy in (2.4, -27.6):
            e = box(x0, x0+55.6, yy, yy+25.2, -15.5, -4.2); esc = e if esc is None else esc.union(e)
    R['REF_ESC_AIR40A_x4'] = esc
    R['REF_Payload_Mount_Plate'] = box(325, 375, -20, 20, -55.75, -54.25)
    R['REF_VTail_Servos'] = box(930, 960, 1, 16, -14.8, 17.2).union(box(930, 960, -16, -1, -14.8, 17.2))
    R['REF_MT4008_Envelope_AWAITING_CAD'] = cylx(0, 0, 22.2, 1110, 1136)
    R['REF_Pusher_Prop_13in_Disk'] = cylx(0, 0, 165.1, 1146, 1147)
    return R
if __name__ == '__main__':
    import os, time; t0 = time.time()
    out = '/home/claude/full/out/fuselage'; os.makedirs(out, exist_ok=True)
    P = build_fuselage(log=lambda m: (print('F', m, round(time.time()-t0, 1)), sys.stdout.flush()))
    P.update(build_refs())
    for k, v in P.items():
        s = v.val() if len(v.vals()) == 1 else cq.Compound.makeCompound(v.vals())
        print('F', k, s.isValid(), len(s.Solids()), round(s.Volume(), 1)); s.exportBrep(f'{out}/{k}.brep')
