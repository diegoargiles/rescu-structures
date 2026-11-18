import cadquery as cq, math, pickle, numpy as np, json
from cadquery import Vector as V
from OCP.gp import gp_Trsf, gp_Ax1, gp_Pnt, gp_Dir, gp_Vec
from OCP.TopLoc import TopLoc_Location
import sys; sys.path.insert(0,'.'); from cove import XC, ZOFF, ZTOP
T=0.33; XJ=179.0
names=pickle.load(open('orig/names.pkl','rb')); idx={n.split('/')[-1]:i for i,n in enumerate(names)}
def orig(n): return cq.Shape.importBrep(f'orig/{idx[n]:03d}.brep')
def box(x0,x1,y0,y1,z0,z1): return cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
# 1 shells trimmed at the nose joint
for n in ('Fuselage_Shell_Left_GFRP_Fuselage','Fuselage_Shell_Right_GFRP_Fuselage'):
    s=orig(n).cut(box(-5,XJ,-60,60,-60,60)); print(n, s.isValid(), round(s.Volume()), round(orig(n).Volume())); s.exportBrep(f'new3/{n}.brep')
# 2 seam strips: nose is one piece, drop the strip forward of the joiner band end
n='Fuselage_Seam_Strips_GFRP_Fuselage'; s=orig(n).cut(box(-5,186,-60,60,-60,60)); print(n, s.isValid(), round(s.Volume())); s.exportBrep(f'new3/{n}.brep')
# 3 Frames_Lower: clear the cove (cove + skin offset)
K=cq.Shape.importBrep('K.brep')
from OCP.BRepOffsetAPI import BRepOffsetAPI_MakeOffsetShape
from OCP.BRepOffset import BRepOffset_Skin
from OCP.GeomAbs import GeomAbs_Arc
m=BRepOffsetAPI_MakeOffsetShape(); m.PerformByJoin(K.wrapped, T+0.5, 1e-4, BRepOffset_Skin, False, False, GeomAbs_Arc); m.Build()
Kc=cq.Shape.cast(m.Shape()); Kc.exportBrep('K_clear.brep')
n='Frames_Lower_and_Battery_Saddles_GFRP_Fuselage'; o=orig(n); s=o.cut(Kc)
print(n, s.isValid(), 'removed mm3', round(o.Volume()-s.Volume(),1)); s.exportBrep(f'new3/{n}.brep')
# 4 nose shell (one piece) and joiner band
S=cq.Shape.importBrep('nose_skin.brep'); S.exportBrep('add3/Nose_Shell_GFRP_Fuselage.brep')
def ring(x0,x1,dr0,dr1):
    def r(x): return 45*math.sqrt(1-(1-x/200)**2)
    xs=np.linspace(x0,x1,15)
    o=cq.Edge.makeSpline([V(x,0,r(x)-dr0) for x in xs]); i=cq.Edge.makeSpline([V(x,0,r(x)-dr1) for x in xs])
    w=cq.Wire.assembleEdges([o, cq.Edge.makeLine(o.endPoint(),i.endPoint()), i, cq.Edge.makeLine(i.startPoint(),o.startPoint())])
    return cq.Solid.revolve(cq.Face.makeFromWires(w),360,V(0,0,0),V(1,0,0))
B=ring(172,186,T,T+0.6); print('band', B.isValid(), round(B.Volume()*1.85e-3,2),'g'); B.exportBrep('add3/Nose_Joiner_Band_GFRP_Fuselage.brep')
# 5 camera shelf (G10, 3 mm) on top of the cove roof
If=cq.Shape.importBrep('nose_inner.brep')
sh=box(58,104,-40,40,ZTOP+T,ZTOP+T+3.0).intersect(If)
print('shelf', sh.isValid(), round(sh.Volume()*1.85e-3,2),'g', sh.BoundingBox().xmin, sh.BoundingBox().xmax); sh.exportBrep('add3/Camera_Shelf_G10_Fuselage.brep')
# 6 Z30 placed: local -> air: rotate -90 deg about Z, local yaw axis (0.5,49.1) -> (XC,0), local z -> z + ZOFF
z=cq.importers.importStep('/home/claude/z30/Z30.step').val()
t1=gp_Trsf(); t1.SetTranslation(gp_Vec(-0.5,-49.1,0))
t2=gp_Trsf(); t2.SetRotation(gp_Ax1(gp_Pnt(0,0,0),gp_Dir(0,0,1)), math.radians(-90))
t3=gp_Trsf(); t3.SetTranslation(gp_Vec(XC,0,ZOFF))
t=t3.Multiplied(t2).Multiplied(t1)
Z=cq.Shape.cast(z.wrapped.Moved(TopLoc_Location(t)))
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
Z=cq.Shape.cast(BRepBuilderAPI_Transform(z.wrapped,t,True).Shape())
b=Z.BoundingBox(); print('Z30 air bbox', [round(v,1) for v in (b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax)])
Z.exportBrep('add3/REF_Z30_Camera_Gimbal_Fuselage.brep')
json.dump(dict(t=[[t.Value(i,j) for j in range(1,5)] for i in range(1,4)]),open('z30_trsf.json','w'))
# 7 swept envelope (raw, no clearance): revolve R_above profile about the yaw axis
prof=np.load('/home/claude/z30_profile.npy')
pts=[V(0,0,prof[0,0]+ZOFF)]+[V(r,0,zz+ZOFF) for zz,r in prof]+[V(0,0,ZOFF+103.36)]
# stairs -> polygon
P=[(0,prof[0,0]+ZOFF)]
for (z0,r0),(z1,r1) in zip(prof[:-1],prof[1:]): P+= [(r0,z0+ZOFF),(r0,z1+ZOFF)]
P+=[(prof[-1,1],ZOFF+103.36),(0,ZOFF+103.36)]
Pc=[P[0]]
for p in P[1:]:
    if abs(p[0]-Pc[-1][0])>1e-6 or abs(p[1]-Pc[-1][1])>1e-6: Pc.append(p)
w=cq.Wire.makePolygon([V(r,0,zz) for r,zz in Pc],close=True)
E=cq.Solid.revolve(cq.Face.makeFromWires(w),360,V(0,0,0),V(0,0,1)).translate(V(XC,0,0)).clean()
print('envelope', E.isValid(), E.BoundingBox().zmin, E.BoundingBox().zmax); E.exportBrep('add3/REF_Z30_Swept_Envelope_Fuselage.brep')
