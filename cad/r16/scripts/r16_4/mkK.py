import cadquery as cq, sys
from cadquery import Vector as V
sys.path.insert(0,'.'); from cove import build, XC
from voff import kvar
def kof(d):
    f=build(); w=f.outerWire().offset2D(d,'arc')[0]
    ff=cq.Face.makeFromWires(w).intersect(cq.Face.makePlane(400,400,V(200,0,0),V(0,1,0)))
    ff=ff.Faces()[0] if ff.ShapeType()!='Face' else ff
    return cq.Solid.revolve(ff,360,V(0,0,0),V(0,0,1)).translate(V(XC,0,0))
K1=kof(1.0)
Kb=kvar(0,6.0).fuse(K1).clean(); Kbs=kvar(-0.5,6.0).fuse(K1).clean(); Kf=kvar(10.0,16.0).fuse(Kb).clean()
for n,s in (('Kbig',Kb),('Kbs',Kbs),('Kfl',Kf)): print(n, s.isValid(), len(s.Solids())); s.exportBrep(n+'.brep')
