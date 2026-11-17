"""RescU landing station (for R16). Station frame: X, Y as the aircraft; Z up from the ground (aircraft Z + 300).
Aircraft seated: fuselage axis at Z 300 -> 13 in pusher-prop tip at Z 134.9 (5.31 in above ground).
Frame: 2020 T-slot aluminium. Cradles: printed PETG. Pads: 3 mm EVA. Nothing sits under a lift-prop disk."""
import sys, os, json, numpy as np
import cadquery as cq
from cadquery import Vector as V
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out'); os.makedirs(OUT, exist_ok=True)
ZAC = 300.0                                        # aircraft datum (fuselage axis) height above ground
Y_B, Z_BOOM = 265.0, -43.0 + ZAC                   # boom centre line / boom bottom when seated (Z 257)
X_T, R_T = 1005.0, 29.60                           # tail rest centre / fuselage radius at X 990 (tail tapers 29.75->28.55); V bears at the F990 ring frame
PAD = 3.0
E = 20.0                                           # 2020 extrusion
Z_RAIL = 25.0                                      # rail bottom (leveling feet below)
def box(x0, x1, y0, y1, z0, z1): return cq.Workplane().box(x1-x0, y1-y0, z1-z0, centered=False).translate((x0, y0, z0))
def prof2020():
    h, so, sd = 10.0, 3.1, 5.8                    # half size, half slot opening, slot depth
    pts = []
    for k in range(4):
        a = np.radians(90*k); R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
        side = [(h, -h), (h, -so), (h-sd, -so), (h-sd, so), (h, so)]
        pts += [tuple(R @ np.array(p)) for p in side]
    return pts
def bar(p0, p1, up=(0, 0, 1)):
    p0, p1 = np.array(p0, float), np.array(p1, float); d = p1-p0; L = np.linalg.norm(d); d /= L
    up = np.array(up, float)
    if abs(np.dot(up, d)) > 0.9: up = np.array([1.0, 0, 0])
    xd = np.cross(up, d); xd /= np.linalg.norm(xd)
    pl = cq.Plane(origin=tuple(p0), xDir=tuple(xd), normal=tuple(d))
    w = cq.Workplane(pl).polyline(prof2020()).close().extrude(L)
    return w.cut(cq.Workplane(pl).circle(2.1).extrude(L))
P = {}
# ---------------- base frame (rails Z 25-45) ----------------
zc = Z_RAIL + E/2
P['Rail_Front_Cross_2020_L700'] = bar((385, -350, zc), (385, 350, zc))
P['Rail_Spine_2020_L600'] = bar((395, 0, zc), (995, 0, zc))
P['Rail_Rear_Cross_2020_L340'] = bar((1005, -170, zc), (1005, 170, zc))
# ---------------- posts ----------------
ZT_RAIL = Z_RAIL + E
Z_CR_BOT = 228.0                                     # boom-cradle underside
Z_POCKET = 18.0
for sg, sd in ((1, 'R'), (-1, 'L')):
    P[f'Post_Boom_{sd}_2020_L{int(Z_CR_BOT+Z_POCKET-ZT_RAIL)}'] = bar((385, sg*Y_B, ZT_RAIL), (385, sg*Y_B, Z_CR_BOT + Z_POCKET))
    # 45 deg inboard brace, mitred flush to post face and rail top
    b = bar((385, sg*(Y_B-10-130), ZT_RAIL - 14.14), (385, sg*(Y_B-10+14.14), ZT_RAIL + 130 + 14.14))
    b = b.intersect(box(375, 395, min(sg*(Y_B-10), sg*(Y_B-200)), max(sg*(Y_B-10), sg*(Y_B-200)), ZT_RAIL, 400))
    P[f'Brace_Boom_{sd}_2020_45deg'] = b
Z_TC_BOT = 222.0
P[f'Post_Tail_2020_L{int(Z_TC_BOT+Z_POCKET-ZT_RAIL)}'] = bar((X_T, 0, ZT_RAIL), (X_T, 0, Z_TC_BOT + Z_POCKET))
bt = bar((X_T-10-110, 0, ZT_RAIL-14.14), (X_T-10+14.14, 0, ZT_RAIL+110+14.14), up=(0, 1, 0))
P['Brace_Tail_2020_45deg'] = bt.intersect(box(X_T-10-200, X_T-10, -10, 10, ZT_RAIL, 400))
# ---------------- boom cradles (PETG) ----------------
CX0, CX1 = 300.0, 472.0                    # cradle length; contact pad on flat boom bottom X 312-448
FL_HALF, FLARE, Z_TOP = 15.5, 55.0, ZAC - 14.0          # channel floor half-width, wall flare from vertical, rim height
def cradle(sg):
    y0 = sg*Y_B; zf = Z_BOOM - PAD                     # printed floor top
    t = np.tan(np.radians(FLARE)); h = Z_TOP - zf; wi = FL_HALF + h*t
    outer = [(-24, Z_CR_BOT), (24, Z_CR_BOT), (24, zf - 14), (wi + 6, Z_TOP), (-(wi + 6), Z_TOP), (-24, zf - 14)]
    inner = [(-FL_HALF, zf), (FL_HALF, zf), (wi, Z_TOP + 0.01), (-wi, Z_TOP + 0.01)]
    def ext(pts, x0, x1):
        return cq.Workplane('YZ', origin=(x0, y0, 0)).polyline(pts).close().extrude(x1 - x0)
    c = ext(outer, CX0, CX1)
    try: c = c.edges('|X').fillet(3.0)
    except Exception: pass
    c = c.cut(ext(inner, CX0 - 1, CX1 + 1))
    try: c = c.faces('>Z').edges().fillet(1.2)
    except Exception: pass
    # post pocket + M5 counterbored centre screw into the 2020 end tap (head hidden under the pad)
    c = c.cut(box(374.85, 395.15, y0 - 10.15, y0 + 10.15, Z_CR_BOT - 1, Z_CR_BOT + Z_POCKET))
    c = c.cut(cq.Workplane().circle(2.75).extrude(40).translate((385, y0, Z_CR_BOT)))
    c = c.cut(cq.Workplane().circle(5.0).extrude(3.6).translate((385, y0, zf - 3.6)))   # M5 button head under the pad, 4.4 mm floor under it
    # 2x M5 side screws into T-nuts in the post slots (anti-pull-off)
    for zz in (Z_CR_BOT + 9,):
        c = c.cut(cq.Workplane('XZ', origin=(385, 0, zz)).circle(2.75).extrude(-60).translate((0, y0 - 30, 0)))
    # hold-down strap slots (1/2 in hook-and-loop strap) aft of the wing trailing edge
    for s in (-1, 1):
        c = c.cut(box(455, 469, y0 + s*(FL_HALF + 2) - 2.5, y0 + s*(FL_HALF + 2) + 2.5, zf - 12, zf + 1).union(
                  box(455, 469, min(y0 + s*(FL_HALF + 2), y0 + s*30), max(y0 + s*(FL_HALF + 2), y0 + s*30), zf - 12, zf - 7)))
    # lightening pockets in the solid base under the floor
    for xs in ((308, 368), (402, 452)):
        c = c.cut(box(xs[0], xs[1], y0 - 17, y0 + 17, Z_CR_BOT - 1, zf - 6).cut(box(453, 471, y0 - 40, y0 + 40, 0, 400)))
    return c, zf
for sg, sd in ((1, 'R'), (-1, 'L')):
    c, zf = cradle(sg)
    P[f'Cradle_Boom_{sd}_PETG'] = c
    P[f'Pad_Boom_{sd}_EVA3'] = box(312, 448, sg*Y_B - FL_HALF + 0.5, sg*Y_B + FL_HALF - 0.5, zf, zf + PAD)
# ---------------- tail V-rest (PETG) ----------------
TX0, TX1 = 980.0, 1030.0
zv = ZAC - R_T*np.sqrt(2)                    # V vertex for a 90 deg V tangent to the fuselage (Z 258.8)
zvp = zv - PAD*np.sqrt(2)                    # printed V vertex (pads on both faces)
TOPT = ZAC - 2.0
def tail_rest():
    hw = TOPT - zvp
    outer = [(-30, Z_TC_BOT), (30, Z_TC_BOT), (hw + 7, TOPT), (-(hw + 7), TOPT)]
    c = cq.Workplane('YZ', origin=(TX0, 0, 0)).polyline(outer).close().extrude(TX1 - TX0)
    try: c = c.edges('|X').fillet(3.0)
    except Exception: pass
    vee = cq.Workplane('YZ', origin=(TX0 - 1, 0, 0)).polyline([(0, zvp), (hw + 30, TOPT + 30), (-(hw + 30), TOPT + 30)]).close().extrude(TX1 - TX0 + 2)
    c = c.cut(vee).cut(box(TX0 - 1, TX1 + 1, -2.5, 2.5, zvp - 3, zvp + 1))          # vertex relief / drain
    c = c.cut(box(X_T - 10.15, X_T + 10.15, -10.15, 10.15, Z_TC_BOT - 1, Z_TC_BOT + Z_POCKET))
    c = c.cut(cq.Workplane().circle(2.75).extrude(60).translate((X_T, 0, Z_TC_BOT)))
    c = c.cut(cq.Workplane().circle(5.0).extrude(6).translate((X_T, 0, zvp - 7)))
    for yy in (-1, 1):
        c = c.cut(box(X_T - 12, X_T + 12, yy*16 - 8, yy*16 + 8, Z_TC_BOT + Z_POCKET + 3, zvp - 2 + abs(yy*16) - 9).cut(box(0, 2000, -2, 2, 0, 400)))
    return c
P['Cradle_Tail_PETG'] = tail_rest()
def vpad(s):
    # 3 mm EVA strip on each V face, X 990-1020, 24 mm wide along the face, centred on the tangent point
    a = np.radians(45); n = np.array([0, -s*np.sin(a), np.cos(a)])           # face normal
    tdir = np.array([0, s*np.cos(a), np.sin(a)])
    cp = np.array([990.0, s*R_T*np.sin(a), ZAC - R_T*np.cos(a)]) - n*PAD/2
    pl = cq.Plane(origin=tuple(cp), xDir=tuple(tdir), normal=(1, 0, 0))
    return cq.Workplane(pl).rect(24, PAD).extrude(30)
P['Pad_Tail_EVA3'] = vpad(1).union(vpad(-1))
# ---------------- COTS hardware (simplified) ----------------
feet = None
for (x, y) in ((385, -330), (385, 330), (1005, -150), (1005, 150), (700, 0)):
    f = cq.Workplane().circle(15).extrude(5).translate((x, y, 0)).union(cq.Workplane().polygon(6, 13).extrude(6).translate((x, y, 5))).union(
        cq.Workplane().circle(3).extrude(Z_RAIL - 11).translate((x, y, 11)))
    feet = f if feet is None else feet.union(f)
P['COTS_Leveling_Feet_M6_x5'] = feet
# joining hardware (simplified envelopes): T-plates where post and rail faces are coplanar, L-brackets, inside corner brackets
def tplate(xf, xs, yc, zr, h=60):          # flat T joining plate 3 mm on the X face at xf (outward sign xs)
    x0, x1 = (xf, xf + 3) if xs > 0 else (xf - 3, xf)
    return box(x0, x1, yc - 40, yc + 40, zr, zr + 20).union(box(x0, x1, yc - 10, yc + 10, zr + 20, zr + 20 + h))
def lbrk(xc, yf, ys, zr):                  # 20x20 L bracket on a Y face at yf, horizontal leg along +ys on rail top
    y0, y1 = (yf, yf + 20) if ys > 0 else (yf - 20, yf)
    yv0, yv1 = (yf, yf + 3) if ys > 0 else (yf - 3, yf)
    return box(xc - 10, xc + 10, y0, y1, zr, zr + 3).union(box(xc - 10, xc + 10, yv0, yv1, zr, zr + 20))
parts = []
for sg in (1, -1):
    parts += [tplate(375, -1, sg*Y_B, Z_RAIL), tplate(395, 1, sg*Y_B, Z_RAIL), lbrk(385, sg*(Y_B + 10), sg, ZT_RAIL)]
parts += [tplate(1015, 1, 0, Z_RAIL), lbrk(X_T, 10, 1, ZT_RAIL), lbrk(X_T, -10, -1, ZT_RAIL)]
for xf, xs in ((395, 1), (995, -1)):      # inside corner brackets, spine to cross rails (both sides of the spine)
    for ys in (1, -1):
        x0, x1 = (xf, xf + 20) if xs > 0 else (xf - 20, xf)
        parts.append(box(x0, x1, ys*10 if ys > 0 else -13, 13 if ys > 0 else -10, Z_RAIL, Z_RAIL + 20).cut(
                     box(x0 + (3 if xs > 0 else 0), x1 - (0 if xs > 0 else 3), ys*13 if ys > 0 else -40, 40 if ys > 0 else -13, Z_RAIL - 1, Z_RAIL + 21)).union(
                     box(xf if xs > 0 else xf - 3, xf + 3 if xs > 0 else xf, ys*10 if ys > 0 else -30, 30 if ys > 0 else -10, Z_RAIL, Z_RAIL + 20)))
brk = parts[0]
for q in parts[1:]: brk = brk.union(q)
P['COTS_Joining_Plates_and_Brackets'] = brk
for k, w in P.items():
    s = w.val() if len(w.vals()) == 1 else cq.Compound.makeCompound(w.vals())
    s.exportBrep(f'{OUT}/{k}.brep'); print(k, s.isValid(), len(s.Solids()), round(s.Volume(), 1)); sys.stdout.flush()
json.dump(dict(ZAC=ZAC, Z_BOOM=Z_BOOM, cradle_floor=float(Z_BOOM-PAD), tail_v_vertex=float(zv), tail_contact_z=float(ZAC - R_T/np.sqrt(2))), open(f'{OUT}/station.json', 'w'), indent=1)
