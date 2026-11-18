import cadquery as cq, math, time
from cadquery import Vector as V
from OCP.BRepOffsetAPI import BRepOffsetAPI_MakeOffsetShape
from OCP.BRepOffset import BRepOffset_Skin
from OCP.GeomAbs import GeomAbs_Intersection, GeomAbs_Arc
t0=time.time(); T=0.33; XJ=179.0
K=cq.Shape.importBrep('K.brep')
m=BRepOffsetAPI_MakeOffsetShape(); m.PerformByJoin(K.wrapped, T, 1e-4, BRepOffset_Skin, False, False, GeomAbs_Arc); m.Build()
Ko=cq.Shape.cast(m.Shape()); print('Ko', Ko.ShapeType(), Ko.isValid(), round(Ko.Volume()-K.Volume()))
if Ko.ShapeType()!='Solid':
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeSolid
    Ko=cq.Solid.makeSolid(cq.Shell(Ko.Shells()[0].wrapped)) if Ko.Shells() else Ko
# inner ellipse: semi-axes 200-? keep radial thickness T: r_in = r - T (x from small x0 to XJ+1)
pts=[]
for x in [i*0.5 for i in range(0, int((XJ+1)*2)+1)]:
    r=45*math.sqrt(max(0,1-(1-x/200)**2))-T
    if r>0.05: pts.append(V(x,0,r))
sp=cq.Edge.makeSpline(pts)
p0,p1=pts[0],pts[-1]
w=cq.Wire.assembleEdges([sp, cq.Edge.makeLine(p1,V(p1.x,0,0)), cq.Edge.makeLine(V(p1.x,0,0),V(p0.x,0,0)), cq.Edge.makeLine(V(p0.x,0,0),p0)])
Nin=cq.Solid.revolve(cq.Face.makeFromWires(w),360,V(0,0,0),V(1,0,0))
I=Nin.cut(Ko); print('I', I.isValid(), len(I.Solids()), round(time.time()-t0))
I=I.Solids()[0] if I.ShapeType()!='Solid' else I
outer=[f for f in I.Faces() if f.geomType() in ('REVOLUTION','BSPLINE') and f.BoundingBox().xlen>100][0]
aft=[f for f in I.Faces() if f.geomType()=='PLANE' and f.BoundingBox().xmin>179.5]
cove=[f for f in I.Faces() if not f.isSame(outer) and not any(f.isSame(a) for a in aft) and f.BoundingBox().xmin>0.5]
lip=[e for e in outer.Edges() if any(e.isSame(e2) for f in cove for e2 in f.Edges())]
print('inner lip edges',len(lip))
If=I.fillet(8-T, lip); print('If', If.isValid(), round(time.time()-t0))
Nf=cq.Shape.importBrep('Nf_8.brep')
S=Nf.cut(If); print('skin', S.isValid(), len(S.Solids()), round(S.Volume(),1), 'mass g', round(S.Volume()*1.85e-3,2))
S.exportBrep('nose_skin.brep'); If.exportBrep('nose_inner.brep')
