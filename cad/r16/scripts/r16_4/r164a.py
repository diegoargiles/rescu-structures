# R16.4 step A: offset cutters, inner voids, liner, shells
import cadquery as cq, numpy as np, math, time, sys
from cadquery import Vector as V
sys.path.insert(0,'.'); from cove import build, XC, ZOFF, ZTOP
from OCP.BRepOffsetAPI import BRepOffsetAPI_MakeOffsetShape
from OCP.BRepOffset import BRepOffset_Skin
from OCP.GeomAbs import GeomAbs_Arc
t0=time.time(); XJ=179.0
def kof(d):
    f=build(); w=f.outerWire().offset2D(d,'arc')[0]
    ff=cq.Face.makeFromWires(w).intersect(cq.Face.makePlane(400,400,V(200,0,0),V(0,1,0)))
    ff=ff.Faces()[0] if ff.ShapeType()!='Face' else ff
    return cq.Solid.revolve(ff,360,V(0,0,0),V(0,0,1)).translate(V(XC,0,0))
def nin(t, x1=XJ+1):
    pts=[]
    for x in np.arange(0, x1+1e-9, 0.5):
        r=45*math.sqrt(max(0,1-(1-x/200)**2))-t
        if r>0.05: pts.append(V(x,0,r))
    sp=cq.Edge.makeSpline(pts); p0,p1=pts[0],pts[-1]
    w=cq.Wire.assembleEdges([sp, cq.Edge.makeLine(p1,V(p1.x,0,0)), cq.Edge.makeLine(V(p1.x,0,0),V(p0.x,0,0)), cq.Edge.makeLine(V(p0.x,0,0),p0)])
    return cq.Solid.revolve(cq.Face.makeFromWires(w),360,V(0,0,0),V(1,0,0))
K=cq.Shape.importBrep('K.brep'); N=cq.Shape.importBrep('N.brep'); O=cq.Shape.importBrep('Nf_8.brep')
Kbig=kof(12.5); Kfl=kof(24.5); print('offsets ok', Kbig.isValid(), Kfl.isValid(), round(time.time()-t0))
Kbig.exportBrep('Kbig.brep'); Kfl.exportBrep('Kfl.brep')
# inner void for a 0.66 dent skin (same recipe as skin.py)
def inner_void(T):
    m=BRepOffsetAPI_MakeOffsetShape(); m.PerformByJoin(K.wrapped, T, 1e-4, BRepOffset_Skin, False, False, GeomAbs_Arc); m.Build()
    Ko=cq.Shape.cast(m.Shape())
    I=nin(T).cut(Ko); I=I.Solids()[0] if I.ShapeType()!='Solid' else I
    outer=[f for f in I.Faces() if f.geomType() in ('REVOLUTION','BSPLINE') and f.BoundingBox().xlen>100][0]
    aft=[f for f in I.Faces() if f.geomType()=='PLANE' and f.BoundingBox().xmin>179.5]
    cove=[f for f in I.Faces() if not f.isSame(outer) and not any(f.isSame(a) for a in aft) and f.BoundingBox().xmin>0.5]
    lip=[e for e in outer.Edges() if any(e.isSame(e2) for f in cove for e2 in f.Edges())]
    return I.fillet(8-T, lip)
I66=inner_void(0.66); print('I66', I66.isValid(), round(time.time()-t0)); I66.exportBrep('I66.brep')
N33=nin(0.33); N99=nin(0.99)
liner_out=O.cut(I66).intersect(Kbig)
flange=N33.cut(N99).intersect(Kfl.cut(Kbig))
# roof doubler: 2 plies over the roof (r 20.55 + 0.66 wall), z ZTOP+0.66 .. +0.99
dbl=cq.Solid.makeCylinder(21.21,0.33,V(XC,0,ZTOP+0.66))
liner=liner_out.fuse(flange).fuse(dbl).clean()
print('liner', liner.isValid(), len(liner.Solids()), round(liner.Volume(),1), round(time.time()-t0))
liner.exportBrep('p_liner.brep')
shell=N.cut(N33).cut(Kbig)
print('shell', shell.isValid(), len(shell.Solids()), round(shell.Volume(),1))
shell.exportBrep('p_shell.brep'); N33.exportBrep('N33.brep'); N99.exportBrep('N99.brep')
print('liner/shell overlap', round(liner.intersect(shell).Volume(),4))
