"""R16.2: Tarot 4008 flush on the removable plate (Tarot Ø19 bolt circle, 4x M3x4 SHCS), collar bore opened for the
screw heads, shell notch for the motor wire tab, UM2807 shafts lengthened 4 mm + M5 bullet prop nuts, pusher bullet nut."""
import cadquery as cq, math, pickle, json, os
from OCP.gp import gp_Ax3, gp_Pnt, gp_Dir, gp_Trsf
from OCP.TopLoc import TopLoc_Location
V = cq.Vector; IN = 25.4
W = '/home/claude/work'; P = '/home/claude/props/'
os.makedirs(f'{W}/add2', exist_ok=True); os.makedirs(f'{W}/new2', exist_ok=True)
names = pickle.load(open(f'{W}/orig/names.pkl', 'rb')); idx = {n.split('/')[-1]: i for i, n in enumerate(names)}
def cur(nm):
    i = idx[nm]; f = f'{W}/new/{i:03d}.brep'
    return cq.Shape.importBrep(f if os.path.exists(f) else f'{W}/orig/{i:03d}.brep')
def mv(shape, trsf): return cq.Shape.cast(shape.wrapped.Moved(TopLoc_Location(trsf)))
def ax3(o, z, x): return gp_Ax3(gp_Pnt(*o), gp_Dir(*z), gp_Dir(*x))
def frame(o, z, x):
    t = gp_Trsf(); t.SetTransformation(ax3(o, z, x), gp_Ax3()); return t
def cylx(r, x0, x1): return cq.Solid.makeCylinder(r, x1 - x0, V(x0, 0, 0), V(1, 0, 0))
def box(x0, x1, y0, y1, z0, z1): return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, V(x0, y0, z0))
out_add, out_rep = {}, {}

# ---------------- motor transform (motor frame: axis +Y_m, base face y=-9.75, tab toward +X_m/-Z_m) ----------------
X_PLATE_AFT = 1103.5            # removable plate aft face (unchanged)
X_BASE = X_PLATE_AFT            # motor base face now seated on the plate
t1 = gp_Trsf(); t1.SetTransformation(ax3((0, 0, 0), (0, 1, 0), (1, 0, 0)))          # motor -> local (Z = Y_m)
tab_l = mv(cq.Vertex.makeVertex((22.3+27.03)/2, -8.5, (-18.73-11.27)/2), t1).Center()
ang = math.degrees(math.atan2(tab_l.y, tab_l.x))
from OCP.gp import gp_Ax1
t2 = gp_Trsf(); t2.SetRotation(gp_Ax1(gp_Pnt(0,0,0), gp_Dir(0,0,1)), math.radians(-ang))
TAB_DIR = (0, 1, 0)             # wire tab points to the right side (+Y), away from the L/R shell seam
t3 = frame((X_BASE + 9.75, 0, 0), (1, 0, 0), TAB_DIR)
T = t3.Multiplied(t2).Multiplied(t1)
mn = list(pickle.load(open('/home/claude/motor_in/names.pkl', 'rb'))); sol = []
for i in range(len(mn)): sol += cq.Shape.importBrep(f'/home/claude/motor_in/{i:02d}.brep').Solids()
motor = mv(cq.Compound.makeCompound(sol), T)
out_add['Tarot_4008_Pusher_Motor_Fuselage'] = motor
bb = motor.BoundingBox(); print('motor x', round(bb.xmin, 2), round(bb.xmax, 2), 'y', round(bb.ymin, 2), round(bb.ymax, 2), 'z', round(bb.zmin, 2), round(bb.zmax, 2))
# Tarot Ø19 bolt circle (4x M3, at 2.2 + k*90 deg in the motor X_m/Z_m plane)
holes = []
for k in range(4):
    a = math.radians(2.2 + 90 * k)
    p = mv(cq.Vertex.makeVertex(9.5*math.cos(a), -9.75, 9.5*math.sin(a)), T).Center()
    holes.append((p.y, p.z)); print('hole', round(p.x, 3), round(p.y, 3), round(p.z, 3), 'r', round(math.hypot(p.y, p.z), 3))
# ---------------- removable plate: same disk/place, holes now = Tarot Ø19 pattern ----------------
plate = cylx(24.5, 1102.0, 1103.5).cut(cylx(6.0, 1101, 1104.5))
for y, z in holes: plate = plate.cut(cq.Solid.makeCylinder(1.65, 3.5, V(1101, y, z), V(1, 0, 0)))
out_rep['Pusher_Removable_Plate_6061_Fuselage'] = plate.clean()
# ---------------- collar: open the end-wall bore R11 -> R13 so the M3 heads pass through ----------------
collar = cur('Pusher_Bonded_Collar_GFRP_Fuselage').cut(cylx(13.0, 1099.5, 1102.5)).clean()
out_rep['Pusher_Bonded_Collar_GFRP_Fuselage'] = collar
# ---------------- 4x M3x4 ISO 4762 socket head cap screws, inserted from the front face of the plate ----------------
def shcs(y, z, L=4.0, x_face=1102.0):
    head = cq.Solid.makeCylinder(2.75, 3.0, V(x_face - 3.0, y, z), V(1, 0, 0))
    hexr = cq.Workplane('YZ', origin=(x_face - 3.0, y, z)).polygon(6, 2.5 / math.cos(math.pi/6)).extrude(1.5).val()
    head = head.cut(hexr).fillet(0.3, [e for e in head.Edges() if abs(e.Center().x - (x_face - 3.0)) < 1e-6 and e.geomType() == 'CIRCLE' and e.radius() > 2.7]) if False else head.cut(hexr)
    shank = cq.Solid.makeCylinder(1.5, L, V(x_face, y, z), V(1, 0, 0))
    return head.fuse(shank).clean()
out_add['Motor_Screws_M3x4_SHCS_Pusher_Fuselage'] = cq.Compound.makeCompound([shcs(y, z) for y, z in holes])
# ---------------- shell notch for the motor wire tab (right shell, trailing edge) ----------------
tab = motor.intersect(cq.Solid.makeCylinder(40, 30, V(1095, 0, 0), V(1, 0, 0)).cut(cylx(23.0, 1090, 1130)))
tb = tab.BoundingBox(); print('tab bbox', [round(v, 2) for v in (tb.xmin, tb.xmax, tb.ymin, tb.ymax, tb.zmin, tb.zmax)])
notch = box(tb.xmin - 1.0, 1112, 20, 40, tb.zmin - 1.0, tb.zmax + 1.0)
sr = cur('Fuselage_Shell_Right_GFRP_Fuselage'); srn = sr.cut(notch); c = srn.clean(); srn = c if c.isValid() else srn
out_rep['Fuselage_Shell_Right_GFRP_Fuselage'] = srn
print('notch x', round(tb.xmin - 1, 2), '..1110  z', round(tb.zmin - 1, 2), '..', round(tb.zmax + 1, 2), 'shell valid', srn.isValid())
json.dump(dict(notch=[tb.xmin-1, tb.zmin-1, tb.zmax+1]), open(f'{W}/add2/notch.json', 'w'))
# ---------------- bullet prop nut (built along +Z, seat at z=0) ----------------
def bullet_nut(bore, af, flange_d, flange_h, hex_h, dome_h, bore_depth):
    fl = cq.Workplane('XY').circle(flange_d/2).extrude(flange_h)
    hx = cq.Workplane('XY').workplane(offset=flange_h).polygon(6, af / math.cos(math.pi/6)).extrude(hex_h)
    r0 = af/2 * 0.98; z0 = flange_h + hex_h
    pts = [(0, z0)] + [(r0*math.cos(t), z0 + dome_h*math.sin(t)) for t in [i*math.pi/2/16 for i in range(17)]] + [(0, z0+dome_h)]
    pts = [(r, z) for r, z in pts]
    dome = cq.Workplane('XZ').polyline([(0, z0), (r0, z0)] + [(r0*math.cos(t), z0 + dome_h*math.sin(t)) for t in [i*math.pi/2/20 for i in range(1, 21)]]).close().revolve(360, (0, 0, 0), (0, 1, 0))
    n = fl.union(hx).union(dome).cut(cq.Workplane('XY').circle(bore/2).extrude(bore_depth))
    return n.val()
nut5 = bullet_nut(5.0, 8.0, 11.0, 1.0, 4.5, 4.5, 6.5)            # M5 prop nut, 10 mm tall
nut14 = bullet_nut(0.25*IN, 10.0, 13.0, 1.2, 5.0, 5.5, 7.5)      # 1/4 in prop nut for the pusher adapter
# ---------------- pusher: adapter + prop + nut move with the motor ----------------
pl = json.load(open(f'{W}/add/placement.json'))
DX = X_BASE - pl['X_BASE']                      # -6.5
X_ROTOR_TOP = X_BASE + 19.0; X_PROP = pl['X_PROP'] + DX
hub_t13 = 0.48*IN; hub_front = X_PROP - hub_t13/2; hub_back = X_PROP + hub_t13/2
adapter = cylx(10, X_ROTOR_TOP, X_ROTOR_TOP+3).fuse(cylx(6, X_ROTOR_TOP+3, hub_front)).fuse(cylx(0.25*IN/2, hub_front, hub_back+5.5))
adapter = adapter.cut(cylx(2.05, X_ROTOR_TOP-1, X_ROTOR_TOP+3)).clean()
out_add['REF_Prop_Adapter_Pusher_Fuselage'] = adapter
out_add['Prop_Nut_1-4in_Bullet_Pusher_Fuselage'] = mv(nut14, frame((hub_back, 0, 0), (1, 0, 0), (0, 1, 0)))
p13 = cq.Shape.importBrep(P + 'APC_Sport_13x8_LP13080_P.brep')
out_add['APC_13x8_LP13080P_Pusher_Prop_Fuselage'] = mv(p13, frame((X_PROP, 0, 0), (-1, 0, 0), (0, 1, 0)))
print('pusher: rotor top', X_ROTOR_TOP, 'prop mid', X_PROP, 'hub', round(hub_front, 2), round(hub_back, 2))
# ---------------- lift motors: lengthen the M5 thread by 4 mm, add bullet nuts ----------------
BELL_TOP = pl['BELL_TOP']; HUB10 = 0.46*IN; HUB_TOP = BELL_TOP + HUB10; EXT = 4.0; ZCUT = 17.0
for side in ('Front_Boom_R', 'Rear_Boom_R', 'Front_Boom_L', 'Rear_Boom_L'):
    nm = f'UM2807_{side}'; m = cur(nm); sols = m.Solids()
    sh = min(sols, key=lambda s: abs(s.Volume() - 515.0))
    cy = [f for f in sh.Faces() if f.geomType() == 'CYLINDER' and abs(f._geomAdaptor().Cylinder().Radius() - 2.45) < 0.02][0]
    loc = cy._geomAdaptor().Cylinder().Location(); cx, cyy = loc.X(), loc.Y()
    big = 100
    # thread is a modelled helix with 0.8 mm pitch: extend by 5 pitches (4.0 mm) by copying a 4 mm thread
    # segment (z 13-17) up 4 mm into the gap and lifting everything above z 17 by 4 mm (= 5 pitches) so the helix stays continuous
    B = lambda z0, z1: box(cx-big, cx+big, cyy-big, cyy+big, z0, z1)
    low = sh.intersect(B(-100, ZCUT)); seg = sh.intersect(B(13.0, 17.0)).translate(V(0, 0, EXT))
    cap = sh.intersect(B(ZCUT, 100)).translate(V(0, 0, EXT))
    new_sh = low.fuse(seg).fuse(cap)
    c = new_sh.clean(); new_sh = c if c.isValid() else new_sh
    if not new_sh.isValid():
        new_sh = cq.Compound.makeCompound(low.Solids() + seg.Solids() + cap.Solids()); print('  kept as 3 touching bodies')
    rest = [s for s in sols if s is not sh and not s.isSame(sh)]
    out_rep[nm] = cq.Compound.makeCompound(rest + new_sh.Solids())
    top = new_sh.BoundingBox().zmax
    out_add[f'Prop_Nut_M5_Bullet_{side}'] = mv(nut5, frame((cx, cyy, HUB_TOP), (0, 0, 1), (1, 0, 0)))
    print(nm, 'shaft axis', round(cx, 3), round(cyy, 3), 'shaft top', round(top, 2), 'thread above hub', round(top - HUB_TOP, 2), 'valid', new_sh.isValid())
for k, v in out_add.items(): v.exportBrep(f'{W}/add2/{k}.brep')
for k, v in out_rep.items(): v.exportBrep(f'{W}/new2/{k}.brep')
json.dump(dict(X_BASE=X_BASE, X_ROTOR_TOP=X_ROTOR_TOP, X_PROP=X_PROP, hub=[hub_front, hub_back], BELL_TOP=BELL_TOP, holes=holes), open(f'{W}/add2/placement.json', 'w'))
print('done')
