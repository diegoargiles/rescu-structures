"""Wing half (R13 internal structure) rebuilt for R15 with integrated boom interfaces."""
import cadquery as cq, numpy as np, sys
from geom import *
RIB_ST = [60, 110, 160, 210, 260, 310, 360, 410, 460, 510, 560, 610, 660, 692]
def build_wing(sg, log=print):
    P = {}
    oml = cq.Workplane().add(cq.Solid.makeLoft([wing_wire(0), wing_wire(sg*WB2)], True))
    inner = cq.Workplane().add(cq.Solid.makeLoft([wing_wire(0, WSKIN), wing_wire(sg*WB2, WSKIN)], True))
    fus = fus_solid()
    skin = oml.cut(inner).cut(fus); log('skin')
    # ---- spar system
    y_sp0, y_sp1 = 99.0, 685.0
    # R15 spar: telescoped CFRP tubes OD10/8 -> OD8/6.4 -> OD6/4.4, 30 mm bonded overlaps (sized for +3 g x1.5 with skin)
    spar = cq.Workplane().add(tube_between((spar_x(92.0), sg*92.0, SPAR_Z), (spar_x(380), sg*380, SPAR_Z), 5.0, 4.0).vals() +
           tube_between((spar_x(350), sg*350, SPAR_Z), (spar_x(560), sg*560, SPAR_Z), 4.0, 3.2).vals() +
           tube_between((spar_x(530), sg*530, SPAR_Z), (spar_x(y_sp1), sg*y_sp1, SPAR_Z), 3.0, 2.2).vals())
    d = np.array([spar_x(y_sp1)-spar_x(y_sp0), sg*(y_sp1-y_sp0), 0]); d /= np.linalg.norm(d)
    c265 = np.array([spar_x(265), sg*265, SPAR_Z])
    sleeve = tube_between(tuple(c265-d*20.8), tuple(c265+d*20.8), 5.65, 5.15)
    spar_env = tube_between((spar_x(88.0), sg*88.0, SPAR_Z), (spar_x(380), sg*380, SPAR_Z), 5.2).union(
               tube_between((spar_x(378), sg*378, SPAR_Z), (spar_x(560), sg*560, SPAR_Z), 4.2)).union(
               tube_between((spar_x(558), sg*558, SPAR_Z), (spar_x(y_sp1+2), sg*(y_sp1+2), SPAR_Z), 3.2))
    # root adapter: swept spar to straight joiner (x 310, z 4.2), GFRP block trimmed to the wing interior
    # R15 root adapter: joiner socket + spar socket + 2 mm GFRP shear plate (replaces solid R13 block)
    j_sock = tube_between((310, sg*46, 4.2), (310, sg*112, 4.2), 7.3, 6.05)
    s_sock = tube_between((spar_x(92), sg*92, SPAR_Z), (spar_x(150), sg*150, SPAR_Z), 6.4, 5.05)
    ys = np.linspace(46, 150, 14)
    plate_pts = [(310.0, sg*y) for y in ys] + [(spar_x(y), sg*y) for y in ys[::-1]]
    plate = cq.Workplane('XY', origin=(0, 0, SPAR_Z-1.0)).polyline(plate_pts).close().extrude(2.0)
    plate = plate.cut(cyly(310, 4.2, 6.05, -160, 160)).cut(spar_env)
    adapter = cq.Workplane().add(j_sock.vals() + s_sock.vals() + plate.vals()).intersect(inner)
    adapter_env = tube_between((310, sg*40, 4.2), (310, sg*114, 4.2), 7.4).union(
        tube_between((spar_x(90), sg*90, SPAR_Z), (spar_x(152), sg*152, SPAR_Z), 6.5)).union(
        cq.Workplane('XY', origin=(0, 0, SPAR_Z-1.1)).polyline(plate_pts).close().extrude(2.2))
    # aft torque tube + collars + root socket
    a0, a1 = (385.0, sg*85.0, AFT_Z), (427.9, sg*415.0, AFT_Z)
    aft = tube_between(a0, a1, 2.5, 1.75)
    da = np.array(a1)-np.array(a0); da /= np.linalg.norm(da)
    collars = None
    for st in (265, 310, 360, 410):
        pt = np.array([aft_x(st), sg*st, AFT_Z]); c = tube_between(tuple(pt-da*4), tuple(pt+da*4), 3.0, 2.55)
        collars = c if collars is None else collars.union(c)
    rsock = tube_between((385, sg*46, 3.0), (385, sg*66, 3.0), 2.5, 1.65).union(tube_between(tuple(np.array(a0)-da*19), tuple(np.array(a0)+da*12), 3.0, 2.55)).intersect(inner)
    aft_env = tube_between(a0, a1, 2.6).union(tube_between((385, sg*40, 3.0), (385, sg*90, 3.0), 3.3))
    # wire conduit (new): PTFE 6/4.5 from root diaphragm to boom saddle exit (X375, Y +-257.5)
    ydrop = 265 - 7.5
    zl = wing_zlo(CONDUIT_X, ydrop)
    cond = tube_between((CONDUIT_X_ROOT, sg*46, CONDUIT_Z), (CONDUIT_X, sg*ydrop, CONDUIT_Z), 3.0, 2.6)
    cond = cond.union(tube_between((CONDUIT_X, sg*ydrop, CONDUIT_Z+2.9), (CONDUIT_X, sg*ydrop, zl+0.4), 3.0, 2.6))
    cond_env = tube_between((CONDUIT_X_ROOT - 0.85, sg*40, CONDUIT_Z), (CONDUIT_X, sg*ydrop, CONDUIT_Z), 3.2).union(
               tube_between((CONDUIT_X, sg*ydrop, CONDUIT_Z+3.2), (CONDUIT_X, sg*ydrop, zl-1), 3.2))
    sleeve_env = tube_between(tuple(c265-d*21), tuple(c265+d*21), 5.75)
    collar_env = None
    for st in (265, 310, 360, 410):
        pt = np.array([aft_x(st), sg*st, AFT_Z]); ce = tube_between(tuple(pt-da*4.2), tuple(pt+da*4.2), 3.1)
        collar_env = ce if collar_env is None else collar_env.union(ce)
    # CFRP motor rib (2 mm) with extended lower tab: rib-tab clevis for the integrated boom saddle
    rib = box(313.0, 446.0, sg*265-1.0, sg*265+1.0, -20, 25).intersect(inner)
    above = box(300, 460, sg*265-3, sg*265+3, 0.5, 30).cut(oml)
    tab = box(318.0, 440.0, sg*265-1.0, sg*265+1.0, -14.2, 2).edges('|Y and <Z').fillet(3.0).cut(above)
    mrib = rib.union(tab).cut(sleeve_env).cut(collar_env)
    for bx in (324.0, 381.0, 434.0): mrib = mrib.cut(cyly(bx, -9.5, 1.65, -300, 300))
    log('tubes')
    # ---- ribs (XPS ~4 mm) + GFRP root diaphragm + motor-rib doublers
    # R15: full-depth hot-wire XPS core in two panels per half (root->motor rib, motor rib->tip) replaces 14 foam ribs,
    # so the 0.33 mm GFRP skin is continuously stabilised (sandwich) and carries bending with the spar.
    keep_out = spar_env.union(aft_env).union(cond_env).union(sleeve_env).union(adapter_env).union(collar_env).union(rsock)
    panels = []
    for (y0_, y1_) in ((46.5, 263.8), (266.2, 700.0)):
        zone = box(200, 520, min(sg*y0_, sg*y1_), max(sg*y0_, sg*y1_), -20, 25)
        pnl = zone.intersect(inner).cut(keep_out)
        if y0_ < 100: pnl = pnl.cut(cylz(370, sg*50, 3.2, -10, 20)).cut(box(363, 377, min(sg*46, sg*56), max(sg*46, sg*56), 0.5, 6.0))
        pnl = pnl.cut(box(341.6, 375.4, min(sg*262.0, sg*268.0), max(sg*262.0, sg*268.0), -20, 25))   # doubler pockets
        panels.extend(pnl.vals()); log(f'core panel {y0_}-{y1_}')
    ribs = cq.Workplane().add(panels)
    diaphragm = box(200, 520, sg*45.5 - 1.0, sg*45.5 + 1.0, -20, 25).intersect(inner).cut(cyly(310, 4.2, 7.4, -150, 150)) \
        .cut(cyly(385, 3.0, 2.55, -150, 150)).cut(cond_env).cut(cyly(370, 4, 1.7, -150, 150)).cut(adapter_env).cut(fus)
    doub = None
    for yo in (-2.0, 2.0):
        dd = box(343.1, 373.9, sg*265 + yo - 0.75, sg*265 + yo + 0.75, -20, 25).intersect(inner).cut(sleeve_env)
        doub = dd if doub is None else doub.union(dd)
    log('ribs')
    # ---- root hardware: retention lug + M3 screw, anti-rotation pin (straight joiner lives in fuselage module)
    lug = box(365, 375, sg*48 if sg > 0 else -54, sg*54 if sg > 0 else -48, 1, 5.5).cut(cylz(370, sg*50, 1.7, -5, 15))
    screw = cylz(370, sg*50, 1.5, 0.0, 8.2).union(cylz(370, sg*50, 2.75, 5.5, 8.2))
    pin = cyly(385, 3.0, 1.5, *(sorted((sg*37, sg*63))))
    # skin cut-outs: boom saddle rib-tab passage + conduit drop + retention screw access
    skin = skin.cut(box(317.5, 440.5, sg*265-1.2, sg*265+1.2, -8, 2)).cut(cylz(CONDUIT_X, sg*ydrop, 3.1, -8, 0)) \
               .cut(cylz(370, sg*50, 3.0, 5, 20))
    P.update(Wing_Skin_GFRP=skin, Wing_XPS_Core_Panels=ribs, Wing_Root_Diaphragm_GFRP=diaphragm, Wing_Main_Spar_CFRP=spar,
             Wing_Spar_Sleeve_GFRP=sleeve, Wing_Root_Adapter_GFRP=adapter, Wing_Aft_Torque_Tube_CFRP=aft,
             Wing_Aft_Collars_GFRP=collars, Wing_Aft_Root_Socket_GFRP=rsock, Wing_Motor_Rib_Doublers_GFRP=doub,
             Wing_Wire_Conduit_PTFE=cond, Wing_Retention_Lug_GFRP=lug, Wing_Retention_Screw_M3=screw,
             Wing_AntiRotation_Pin_D3=pin, Wing_Motor_Rib_Extended_Tab_CFRP=mrib)
    log('done')
    return P
if __name__ == '__main__':
    import os, time; t0 = time.time(); sg = int(sys.argv[1]); side = 'R' if sg > 0 else 'L'
    out = f'/home/claude/full/out/wing_{side}'; os.makedirs(out, exist_ok=True)
    P = build_wing(sg, log=lambda m: (print(side, m, round(time.time()-t0, 1)), sys.stdout.flush()))
    for k, v in P.items():
        s = v.val() if len(v.vals()) == 1 else cq.Compound.makeCompound(v.vals())
        print(side, k, s.isValid(), len(s.Solids()), round(s.Volume(), 1)); s.exportBrep(f'{out}/{k}.brep')
