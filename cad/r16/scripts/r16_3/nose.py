import cadquery as cq, numpy as np, sys, time
from cadquery import Vector as V
sys.path.insert(0,'.'); from cove import build, XC, ZOFF, ZTOP
XJ=179.0; T=0.33
t0=time.time()
# outer nose solid (exact R16 ellipse r = 45 sqrt(1-(1-x/200)^2)), revolved about X
import math
th=math.degrees(math.acos((XJ-200)/200))
arc=cq.Edge.makeEllipse(200,45,V(200,0,0),V(0,-1,0),V(1,0,0),th,180)
p1=arc.startPoint(); p0=arc.endPoint(); print('arc',p0,p1)
w=cq.Wire.assembleEdges([arc, cq.Edge.makeLine(p0,V(XJ,0,0)) if False else cq.Edge.makeLine(p0,V(0,0,0)) if p0.x>1e-6 else None][:1] + [cq.Edge.makeLine(p1,V(XJ,0,0)), cq.Edge.makeLine(V(XJ,0,0),V(0,0,0))])
half=cq.Face.makeFromWires(w)
N = cq.Solid.revolve(half, 360, V(0,0,0), V(1,0,0))
print('N', N.isValid(), round(N.Volume()), N.BoundingBox().xmax, round(time.time()-t0))
prof = build()
K = cq.Solid.revolve(prof, 360, V(0,0,0), V(0,0,1)).translate(V(XC,0,0))
cq.exporters.export(cq.Workplane().add(K),'cutter.step')
Nc = N.cut(K)
print('Nc', Nc.isValid(), len(Nc.Solids()), len(Nc.Faces()))
import pickle; open('Nc.brep','w').close(); Nc.exportBrep('Nc.brep'); K.exportBrep('K.brep'); N.exportBrep('N.brep')
# lip edges = edges shared between the ellipsoid face and the cove faces
ef = [f for f in Nc.Faces() if f.geomType() in ('REVOLUTION','BSPLINE','SURFACE_OF_REVOLUTION') and f.BoundingBox().xmin<1]
print([ (f.geomType(), round(f.Area())) for f in Nc.Faces()])
