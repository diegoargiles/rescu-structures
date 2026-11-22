"""Build all three gear modules in aircraft coordinates (deployed or retracted) plus the modified airframe parts.
Writes breps to out_<state>/ : <PartName>_<Group>.brep, and a JSON summary (mass, CG, foot points)."""
import sys, os, math, json, pickle, glob, random
import cadquery as cq
from cadquery import Vector as V
import lg, ctx

STATE = sys.argv[1] if len(sys.argv) > 1 else 'deployed'
PSI = lg.PSI_DEP if STATE == 'deployed' else lg.PSI_RET
OUT = f'out_{STATE}'; os.makedirs(OUT, exist_ok=True)
names = [n.split('/')[-1] for n in pickle.load(open('../orig/names.pkl', 'rb'))]
def S(n): return cq.Shape.importBrep(f'../orig/{names.index(n):03d}.brep')

TILT = 0.4                                   # tail module nose-down tilt, deg (clears the ESC deck)
def T_R(s): return s.translate(V(*lg.P_R))
def T_L(s): return s.mirror('XZ').translate(V(lg.P_R[0], -lg.P_R[1], lg.P_R[2]))
def T_T(s): return s.rotate(V(0, 0, 0), V(0, 0, 1), 180).rotate(V(0, 0, 0), V(0, 1, 0), -TILT).translate(V(*lg.P_T))

# tail leg length: same ground plane as the front feet (lowest point of the foot sphere)
def foot_low_z(L, T, P):
    c = T(cq.Vertex.makeVertex(*([0, 0, 0]))) if False else None
    d, th = lg.pose(lg.PSI_DEP)
    a = math.radians(th); cu, cw = (L - lg.FOOT_R) * math.cos(a), (L - lg.FOOT_R) * math.sin(a)
    p = T(cq.Solid.makeSphere(0.01, V(cu, 0, cw))).Center()
    return p.z - lg.FOOT_R, p
zF, cF = foot_low_z(lg.L_FRONT, T_R, lg.P_R)
lo, hi = 300.0, 420.0
for _ in range(50):
    mid = (lo + hi) / 2
    if foot_low_z(mid, T_T, lg.P_T)[0] > zF: lo = mid
    else: hi = mid
L_T = round((lo + hi) / 2, 2)
zT, cT = foot_low_z(L_T, T_T, lg.P_T)
print('front foot low z', round(zF, 2), 'centre', cF.toTuple(), '| tail L', L_T, 'low z', round(zT, 2), 'centre', cT.toTuple())

# ---------- airframe context and trims ----------
def boom_shells(side):
    up, lo_ = S(f'Boom_Upper_Half_Boom_{side}'), S(f'Boom_Lower_Half_Boom_{side}')
    T = T_R if side == 'R' else T_L
    lo_cut = lo_.cut(T(lg.slot_cutter(lg.L_FRONT)))
    return up, lo_, lo_cut

SECS = ctx.SECS; XS = ctx.XS
def inside_boom_global(side):
    def f(x, y, z):
        if x < XS[0] or x > XS[-1]: return False
        yy = y if side == 'R' else -y
        pts = SECS[min(XS, key=lambda q: abs(q - x))]; n = len(pts); c = False
        for i in range(n):
            (y1, z1), (y2, z2) = pts[i], pts[(i + 1) % n]
            if (z1 > z) != (z2 > z) and yy < (y2 - y1) * (z - z1) / (z2 - z1) + y1: c = not c
        return c
    return f
def R_fus(x): return 44.3 - 0.0275 * (x - 450.0)          # outer radius fit from the shell sections
def inside_fus(x, y, z): return math.hypot(y, z) < R_fus(x) - 0.3 and 186 < x < 1100

def trim(part, shells, inside):
    for sh in shells: part = part.cut(sh)
    rnd = random.Random(1)
    def frac(s):
        b = s.BoundingBox(); pts = []; n = 0
        while len(pts) < 12 and n < 4000:
            n += 1; p = (rnd.uniform(b.xmin, b.xmax), rnd.uniform(b.ymin, b.ymax), rnd.uniform(b.zmin, b.zmax))
            if s.isInside(cq.Vector(*p)): pts.append(p)
        return sum(1 for p in pts if inside(*p)) / max(1, len(pts))
    keep = [s for s in part.Solids() if frac(s) > 0.5]
    return cq.Compound.makeCompound(keep) if len(keep) > 1 else keep[0]

parts = {}      # name -> (shape, group, subassembly)
mods = {}
# front booms
for side, T in (('R', T_R), ('L', T_L)):
    up, lo_, lo_cut = boom_shells(side)
    mods[f'Boom_Lower_Half_Boom_{side}'] = lo_cut
    shells = [up, lo_cut]
    tag = f'LG_Front_{side}'
    for k, s in lg.fixed_parts(lg.L_FRONT).items():
        parts[f'{k}_{tag}'] = (trim(T(s), shells, inside_boom_global(side)), f'Boom_{side}', f'{tag}_Fixed')
    m, d, th = lg.moving_parts(PSI, lg.L_FRONT)
    for k, s in m.items():
        sub = 'Leg' if k in lg.LEG else 'Tendon' if k in lg.TENDON else 'Servo_Arm'
        parts[f'{k}_{tag}'] = (T(s), f'Boom_{side}', f'{tag}_{sub}')
    print('built', tag, flush=True)

# tail
fus = {n: S(n) for n in ['Fuselage_Shell_Left_GFRP_Fuselage', 'Fuselage_Shell_Right_GFRP_Fuselage', 'Fuselage_Seam_Strips_GFRP_Fuselage']}
cutT = T_T(lg.slot_cutter(L_T))
for n, s in fus.items(): mods[n] = s.cut(cutT)
shellsT = list(mods[n] for n in fus)
tag = 'LG_Tail'
# belly doubler under the tail knee block (CFRP 1.0 mm, conforms to the belly)
x0, x1 = 884.0, 931.0
outer = cq.Solid.makeCone(R_fus(x0) - 0.33, R_fus(x1) - 0.33, x1 - x0, V(x0, 0, 0), V(1, 0, 0))
inner = cq.Solid.makeCone(R_fus(x0) - 1.33, R_fus(x1) - 1.33, x1 - x0, V(x0, 0, 0), V(1, 0, 0))
dbl = outer.cut(inner).intersect(lg.box(x0, x1, -16, 16, -60, -20)).cut(T_T(lg.box(-14, 30, -7.0, 7.0, -30, 0)))
parts[f'Belly_Doubler_CFRP_{tag}'] = (dbl, 'Fuselage', f'{tag}_Fixed')
for k, s in lg.fixed_parts(L_T).items():
    parts[f'{k}_{tag}'] = (trim(T_T(s), shellsT + [dbl], inside_fus), 'Fuselage', f'{tag}_Fixed')
m, d, th = lg.moving_parts(PSI, L_T)
for k, s in m.items():
    sub = 'Leg' if k in lg.LEG else 'Tendon' if k in lg.TENDON else 'Servo_Arm'
    parts[f'{k}_{tag}'] = (T_T(s), 'Fuselage', f'{tag}_{sub}')
print('built tail', flush=True)

for n, s in mods.items(): s.exportBrep(f'{OUT}/MOD__{n}.brep')
meta = {}
for n, (s, g, sub) in parts.items():
    s.exportBrep(f'{OUT}/{n}.brep'); meta[n] = (g, sub)
json.dump({'parts': meta, 'L_T': L_T, 'TILT': TILT, 'front_foot_low_z': zF, 'tail_foot_low_z': zT,
           'front_foot_centre': cF.toTuple(), 'tail_foot_centre': cT.toTuple()}, open(f'{OUT}/meta.json', 'w'), indent=1)
print('done', len(parts))
