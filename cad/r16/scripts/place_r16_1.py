"""Place Tarot 4008 pusher (+REF prop adapter) and APC props in the R16 frame (X aft, Y right, Z up, mm)."""
import cadquery as cq, math, pickle, json
V = cq.Vector
P = '/home/claude/props/'
IN = 25.4
def frame_move(shape, origin, zdir, xdir):
    """map local frame (0, +Z, +X) onto world (origin, zdir, xdir)"""
    from OCP.gp import gp_Ax3, gp_Pnt, gp_Dir, gp_Trsf
    from OCP.TopLoc import TopLoc_Location
    t = gp_Trsf(); t.SetTransformation(gp_Ax3(gp_Pnt(*origin), gp_Dir(*zdir), gp_Dir(*xdir)), gp_Ax3())
    return cq.Shape.cast(shape.wrapped.Moved(TopLoc_Location(t)))
out = {}
# ---------- pusher motor: motor +Y (rotor side) -> aircraft +X (aft); base face (y=-9.75) on the R16 envelope face x=1110
X_BASE = 1110.0
names = list(pickle.load(open('/home/claude/motor_in/names.pkl', 'rb')))
solids = []
for i, n in enumerate(names):
    solids += cq.Shape.importBrep(f'/home/claude/motor_in/{i:02d}.brep').Solids()
motor = cq.Compound.makeCompound(solids)
# local motor frame: Y_m is axis. Use Z_local = Y_m, X_local = X_m (tab side) then put tab pointing -Z (down)
from OCP.gp import gp_Ax3, gp_Pnt, gp_Dir, gp_Trsf
from OCP.TopLoc import TopLoc_Location
def ax(o, z, x): return gp_Ax3(gp_Pnt(*o), gp_Dir(*z), gp_Dir(*x))
# tab centroid in motor frame ~ angle in XZ plane
tabc = V((22.3+27.03)/2, 0, (-18.73-11.27)/2)
t = gp_Trsf(); t.SetTransformation(ax((0, 0, 0), (0, 1, 0), (1, 0, 0)))  # motor -> local frame with Z=Y_m
m_loc = cq.Shape.cast(motor.wrapped.Moved(TopLoc_Location(t)))
bb = m_loc.BoundingBox(); print('motor local z', round(bb.zmin, 2), round(bb.zmax, 2))
# find tab direction in local frame
tl = cq.Shape.cast(cq.Vertex.makeVertex(*tabc.toTuple()).wrapped.Moved(TopLoc_Location(t))).Center()
ang = math.atan2(tl.y, tl.x)
m_loc = m_loc.rotate(V(0, 0, 0), V(0, 0, 1), -math.degrees(ang))   # tab now along local +X
# local +Z (rotor side) -> +X aircraft; local +X (tab) -> -Z aircraft; base z_local=-9.75 -> x=1110
pusher_axis_origin = (X_BASE + 9.75, 0, 0)
mot = frame_move(m_loc, pusher_axis_origin, (1, 0, 0), (0, 0, -1))
bb = mot.BoundingBox(); print('motor placed x', round(bb.xmin, 2), round(bb.xmax, 2), 'y', round(bb.ymin, 2), round(bb.ymax, 2), 'z', round(bb.zmin, 2), round(bb.zmax, 2))
out['Tarot_4008_Pusher_Motor_Fuselage'] = mot
X_ROTOR_TOP = X_BASE + 9.75 + 9.25
# ---------- 13x8 pusher prop: mid-plane on the R16 prop-disk plane (x=1146.5); prop front (+Zp, cambered, thrust) faces forward (-X)
X_PROP = 1146.5
spec13 = dict(hub_t=0.48*IN)
p13 = cq.Shape.importBrep(P + 'APC_Sport_13x8_LP13080_P.brep')
out['APC_13x8_LP13080P_Pusher_Prop_Fuselage'] = frame_move(p13, (X_PROP, 0, 0), (-1, 0, 0), (0, 1, 0))
hub_front = X_PROP - spec13['hub_t']/2; hub_back = X_PROP + spec13['hub_t']/2
# ---------- REF bolt-on prop adapter (Tarot rotor top -> 1/4 in prop bore): flange D20x3, seat collar D12, shaft D6.35, nut
def cyl(r, x0, x1): return cq.Solid.makeCylinder(r, x1-x0, V(x0, 0, 0), V(1, 0, 0))
adapter = cyl(10, X_ROTOR_TOP, X_ROTOR_TOP+3).fuse(cyl(6, X_ROTOR_TOP+3, hub_front)).fuse(cyl(0.25*IN/2, hub_front, hub_back+6.0))
adapter = adapter.cut(cyl(2.05, X_ROTOR_TOP-1, X_ROTOR_TOP+3)).clean()
nut = cq.Solid.makeCylinder(5.5, 4.5, V(hub_back, 0, 0), V(1, 0, 0)).cut(cyl(0.25*IN/2, hub_back-1, hub_back+6))
out['REF_Prop_Adapter_Pusher_Fuselage'] = cq.Compound.makeCompound([adapter, nut])
print('pusher hub', round(hub_front, 2), round(hub_back, 2), 'adapter', X_ROTOR_TOP, '->', hub_back+6)
# ---------- 10x3 lift props on the four UM2807s: hub bottom on bell top, bore on shaft axis
# ArduPilot Quad-X: front-right & rear-left CCW (from above) = STD; front-left & rear-right CW = P
p10 = {'STD': cq.Shape.importBrep(P + 'APC_Sport_10x3_LP10030_STD.brep'), 'P': cq.Shape.importBrep(P + 'APC_Sport_10x3_LP10030_P.brep')}
HUB10 = 0.46*IN
lift = {'Front_Boom_R': ((170, 265), 'STD'), 'Rear_Boom_R': ((600, 265), 'P'),
        'Front_Boom_L': ((170, -265), 'P'), 'Rear_Boom_L': ((600, -265), 'STD')}
BELL_TOP = 8.2
for k, ((x, y), hand) in lift.items():
    nm = f"APC_10x3_LP10030{'P' if hand == 'P' else ''}_{k}"
    out[nm] = frame_move(p10[hand], (x, y, BELL_TOP + HUB10/2), (0, 0, 1), (1, 0, 0))
    bb = out[nm].BoundingBox(); print(nm, 'z', round(bb.zmin, 2), round(bb.zmax, 2))
for k, v in out.items(): v.exportBrep(f'/home/claude/work/add/{k}.brep')
json.dump(dict(X_BASE=X_BASE, X_ROTOR_TOP=X_ROTOR_TOP, X_PROP=X_PROP, hub=[hub_front, hub_back], BELL_TOP=BELL_TOP), open('/home/claude/work/add/placement.json', 'w'))
