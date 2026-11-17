"""RescU R15 candidate: integrated molded motor boom + flush rib-tab saddle connection.
Builds both sides, reference wing (reconstructed from repo parameters), modified motor rib,
hardware, UM2807 motors. Exports STEP assembly for SolidWorks.  Units mm, X aft, Y right, Z up."""
import cadquery as cq, numpy as np, json, sys
from cadquery import Vector as V
OUT = '/home/claude/cadwork/out'; import os; os.makedirs(OUT, exist_ok=True)
Y0 = 265.0; XF, XR = 170.0, 600.0; ZPAD = -12.8
# ---------------- wing reference (repo: SD7037, root LE 260, root c 165, tip c 100, sweep 140, b/2 700, dihedral 0)
af = np.loadtxt('/home/claude/rescu-structures/engine/airfoils/sd7037.dat', skiprows=1)
iLE = np.argmin(af[:, 0]); UP = af[:iLE+1][::-1]; LO = af[iLE:]
def chord(y): return 165 - 65*abs(y)/700
def xle(y): return 260 + 140*abs(y)/700
def zlo(x, y=Y0): c = chord(y); return float(np.interp((x-xle(y))/c, LO[:, 0], LO[:, 1])*c)
def zup(x, y=Y0): c = chord(y); return float(np.interp((x-xle(y))/c, UP[:, 0], UP[:, 1])*c)
def af_wire(y, inset=0.0):
    c = chord(y) - 2*inset; pts = af[:-1]
    vs = [V(xle(y)+inset + p[0]*c, y, p[1]*c) for p in pts]
    e1 = cq.Edge.makeSpline(vs + [vs[0]], periodic=False)
    return cq.Wire.assembleEdges([e1])
def wing_half(sg):
    return cq.Solid.makeLoft([af_wire(0.0), af_wire(sg*700.0)], True)
# ---------------- boom sections: (x, width, z_top, z_bot, superellipse exponent)
def sat(x, cap=2.0): return min(cap, zlo(x) + 0.8, zup(x) - 0.8)
front = [(151.5, 10, -14.0, -22.0, 2.4), (154, 22, -12.9, -27.5, 2.8), (158, 30, -12.4, -31, 3.2),
         (164, 36, -12.2, -33.5, 3.6), (170, 38.6, -12.2, -34.8, 3.8), (176, 36.5, -12.2, -34.8, 3.6),
         (183, 31.5, -12.2, -34.9, 3.2), (192, 26.6, -12.4, -35.2, 2.8), (205, 26, -12.8, -35.8, 2.6)]
span_f = [(x, 26, -12.8 + (x-205)/(310-205)*(-3.0+12.8), -35.8 + (x-205)/(310-205)*(-43+35.8), 2.6) for x in (230, 255, 280, 300, 310)]
saddle = [(313, 26, -1.2, -43, 2.8), (316, 26, sat(316), -43, 3.2)] + \
         [(x, 26, sat(x), -43, 3.4) for x in (320, 326, 334, 345, 360, 380, 400, 415, 426, 432, 436)] + \
         [(440, 26, sat(440), -43, 3.2), (444, 26, zlo(444)-0.6, -43, 2.9), (450, 26, -1.6, -42.8, 2.8)]
def mirror_x(s): return (770.0 - s[0],) + s[1:]
span_r = [(x, 26, -12.8 + (565-x)/(565-458)*(-2.6+12.8), -35.8 + (565-x)/(565-458)*(-42.6+35.8), 2.6) for x in (458, 480, 505, 530, 550)]
rear = [mirror_x(s) for s in reversed(front)]
SECT = front + span_f + saddle + span_r + rear
assert all(SECT[i][0] < SECT[i+1][0] for i in range(len(SECT)-1)), [s[0] for s in SECT]
def se_wire(x, w, zt, zb, p, y0=Y0, n=36):
    a, b = w/2, (zt-zb)/2; zc = (zt+zb)/2
    th = np.linspace(-np.pi/2, 1.5*np.pi, n, endpoint=False)
    pts = [V(x, y0 + a*np.sign(np.cos(t))*abs(np.cos(t))**(2/p), zc + b*np.sign(np.sin(t))*abs(np.sin(t))**(2/p)) for t in th]
    return cq.Wire.makePolygon(pts + [pts[0]])
T = 0.8
def inner(s):
    x, w, zt, zb, p = s
    if x < 154 or x > 616: return None
    if 151 <= x <= 200 or 570 <= x <= 619: zti = ZPAD - 1.8          # pad laminate
    else:
        top = min(zt, zlo(x)) if 313.0 <= x <= 453.0 else zt               # actual outer top after wing cut
        zti = top - (1.2 if 316 <= x <= 446 else T)                        # saddle roof: +plies / bond face
    return (x, w - 2*T, zti, zb + T, p)
from scipy.interpolate import PchipInterpolator
def densify(secs, step=4.0):
    a = np.array(secs, float); xs = a[:, 0]
    f = [PchipInterpolator(xs, a[:, k]) for k in range(1, 5)]
    extra = np.r_[np.arange(xs[0], 206, 3.0), np.arange(310, 460, 6.0), np.arange(565, xs[-1], 3.0)]
    xn = sorted(set(np.round(np.r_[extra, xs], 3)))
    xn = [x for x in xn if xs[0] <= x <= xs[-1]]
    return [(x,) + tuple(float(g(x)) for g in f) for x in xn]
def boom_solids(y0):
    outer = cq.Solid.makeLoft([se_wire(*s, y0=y0) for s in densify(SECT)], True)
    inn = cq.Solid.makeLoft([se_wire(*s, y0=y0) for s in densify([inner(s) for s in SECT if inner(s)])], True)
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeSolid
    from OCP.TopoDS import TopoDS
    ms = BRepBuilderAPI_MakeSolid(TopoDS.Shell_s(outer.Shells()[0].wrapped))
    ms.Add(TopoDS.Shell_s(inn.Shells()[0].wrapped.Reversed()))
    hollow = cq.Solid(ms.Solid())
    assert hollow.isValid() and hollow.Volume() > 0
    return cq.Workplane().add(outer), cq.Workplane().add(inn), cq.Workplane().add(hollow)
def box(x0, x1, y0, y1, z0, z1): return cq.Workplane().box(x1-x0, y1-y0, z1-z0, centered=False).translate((x0, y0, z0))
def cylz(x, y, r, z0, z1): return cq.Workplane().circle(r).extrude(z1-z0).translate((x, y, z0))
def cyly(x, z, r, y0, y1): return cq.Workplane('XZ').circle(r).extrude(-(y1-y0)).translate((x, y0, z))
BOLT_X = (324.0, 381.0, 434.0); BOLT_Z = -9.5; TAB_X = (318.0, 440.0); TAB_ZB = -14.5
PCD = 9.5; VENTS = [(8.99, 5.13), (5.13, 8.99)]
ZSPLIT = -24.0
def build_side(sg, log=print):
    y0 = sg*Y0; wing = cq.Workplane().add(wing_half(sg))
    outer, inn, _ = boom_solids(y0); log('loft')
    for xm in (XF, XR): outer = outer.cut(box(xm-30, xm+30, y0-25, y0+25, ZPAD, 0))
    outer = outer.cut(wing); log('outer cut')
    HT = box(100, 700, y0-40, y0+40, ZSPLIT, 20); HB = box(100, 700, y0-40, y0+40, -60, ZSPLIT)
    top = outer.intersect(HT).cut(inn.intersect(HT)); bot = outer.intersect(HB).cut(inn.intersect(HB)); log('halves')
    # rib-tab slot through saddle top + thin U-channel insert
    slot = box(TAB_X[0]-0.5, TAB_X[1]+0.5, y0-1.2, y0+1.2, -15.0, 6)
    top = top.cut(slot)
    chan = box(TAB_X[0]-1, TAB_X[1]+1, y0-2.4, y0+2.4, -16.2, 6).cut(slot).intersect(inn)
    tubes = None; bolts = None
    for bx in BOLT_X:
        h = cyly(bx, BOLT_Z, 1.65, y0-20, y0+20)
        top = top.cut(h).cut(cyly(bx, BOLT_Z, 3.0, y0-16, y0-12.4)); chan = chan.cut(h)
        for lo_, hi_ in ((y0+2.4, y0+11.0), (y0-12.6, y0-2.4)):
            t = cyly(bx, BOLT_Z, 2.75, lo_, hi_).cut(h)
            tubes = t if tubes is None else tubes.union(t)
        b_ = cyly(bx, BOLT_Z, 1.5, y0-12.6, y0+11.0).union(cyly(bx, BOLT_Z, 2.9, y0-13.2, y0-12.4))
        n_ = cyly(bx, BOLT_Z, 2.5, y0+11.0, y0+12.4).cut(cyly(bx, BOLT_Z, 1.5, y0+10, y0+14))
        top = top.cut(cyly(bx, BOLT_Z, 2.55, y0+10.5, y0+16))
        bolts = b_.union(n_) if bolts is None else bolts.union(b_).union(n_)
    tubes = tubes.intersect(inn); log('saddle')
    top = top.cut(cylz(375.0, y0-sg*7.5, 4.0, -8, 6))                 # wire exit to wing conduit (inboard of rib)
    rings = covers = screws = None
    for xm in (XF, XR):
        holes = cylz(xm, y0, 6.0, -25, 0)
        for k in range(4):
            c, s_ = np.cos(k*np.pi/2), np.sin(k*np.pi/2)
            holes = holes.union(cylz(xm+PCD*c, y0+PCD*s_, 1.65, -25, 0))
        for vx, vy in VENTS:
            for sx in (-1, 1):
                for sy in (-1, 1): holes = holes.union(cylz(xm+sx*vx, y0+sy*vy, 2.0, -25, 0))
        ring = cylz(xm, y0, 17.0, ZPAD-1.8-2.0, ZPAD-1.8).cut(holes).intersect(inn)
        top = top.cut(holes)
        cover = bot.intersect(cylz(xm, y0, 14.8, -45, ZSPLIT))
        bot = bot.cut(cylz(xm, y0, 15.0, -45, ZSPLIT))
        scr = None
        for k in range(4):
            c, s_ = np.cos(k*np.pi/2), np.sin(k*np.pi/2)
            px, py = xm+PCD*c, y0+PCD*s_
            sc = cylz(px, py, 1.5, ZPAD-3.8, ZPAD+4.0).union(cylz(px, py, 2.75, ZPAD-6.8, ZPAD-3.8))
            scr = sc if scr is None else scr.union(sc)
        rings = ring if rings is None else rings.union(ring)
        covers = cover if covers is None else covers.union(cover)
        screws = scr if screws is None else screws.union(scr)
    # TPU landing feet bonded/screwed to access covers (bottom at Z -62, clears payload plate at -55.75)
    feet = None
    for xm in (XF, XR):
        f = cq.Workplane().add(cq.Solid.makeLoft([
            cq.Wire.makeEllipse(15.0, 12.0, V(xm, y0, -30.0), V(0, 0, 1), V(1, 0, 0)),
            cq.Wire.makeEllipse(13.0, 10.0, V(xm, y0, -52.0), V(0, 0, 1), V(1, 0, 0)),
            cq.Wire.makeEllipse(8.0, 6.0, V(xm, y0, -62.0), V(0, 0, 1), V(1, 0, 0))], False))
        f = f.cut(outer)
        feet = f if feet is None else feet.union(f)
    log('pads')
    fil = None
    for s in (-1, 1):
        prof = cq.Workplane('YZ', origin=(322, 0, 0)).polyline([(y0+s*5.0, 3.0), (y0+s*19.0, 3.0), (y0+s*13.2, -8.5)]).close().extrude(112)
        fil = prof if fil is None else fil.union(prof)
    fil = fil.cut(wing).cut(outer).intersect(box(300, 460, y0-30, y0+30, -8.5, 3.0)); log('fillet')
    rib_sec = cq.Workplane().add(cq.Solid.makeLoft([af_wire(y0-1.0, 0.33), af_wire(y0+1.0, 0.33)], True))
    rib_sec = rib_sec.intersect(box(313.7, 445.1, y0-1, y0+1, -20, 20))
    tab = box(TAB_X[0], TAB_X[1], y0-1, y0+1, TAB_ZB, 2).edges('|Y and <Z').fillet(3.0).cut(wing)
    rib = rib_sec.union(tab)
    rib = rib.cut(cyly(355.85, 3.87, 4.7, y0-5, y0+5)).cut(cyly(408.4, 3.1, 3.1, y0-5, y0+5))
    for bx in BOLT_X: rib = rib.cut(cyly(bx, BOLT_Z, 1.65, y0-5, y0+5))
    log('rib')
    return dict(Boom_Upper_Half=top, Boom_Lower_Half=bot, Saddle_U_Channel=chan, Compression_Tubes=tubes,
                Motor_Backing_Rings_6061=rings, Pad_Access_Covers=covers, Motor_Screws_M3x10=screws,
                Junction_Fillets=fil, Landing_Feet_TPU=feet, Motor_Rib_Extended_Tab=rib, Saddle_Bolts_M3_and_Barrel_Nuts=bolts,
                REF_Wing_OML=wing, REF_Main_Spar_local=cyly(355.85, 3.87, 4.0, y0-40, y0+40),
                REF_Aft_Tube_local=cyly(408.4, 3.1, 2.5, y0-40, y0+40))
if __name__ == '__main__':
    import time, pickle; t0 = time.time()
    sg = int(sys.argv[1]); side = 'PosY' if sg > 0 else 'NegY'
    p = build_side(sg, log=lambda m: (print(side, m, round(time.time()-t0, 1)), sys.stdout.flush()))
    os.makedirs(f'{OUT}/{side}', exist_ok=True)
    for k, v in p.items():
        sh = v.val() if len(v.vals()) == 1 else cq.Compound.makeCompound(v.vals())
        print(side, k, 'valid', sh.isValid(), 'solids', len(sh.Solids()), 'vol', round(sh.Volume(), 1))
        sh.exportBrep(f'{OUT}/{side}/{k}.brep')
