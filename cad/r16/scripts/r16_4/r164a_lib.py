import cadquery as cq, numpy as np, math
from cadquery import Vector as V
def nin(t, x1=180.0):
    pts=[]
    for x in np.arange(0, x1+1e-9, 0.5):
        r=45*math.sqrt(max(0,1-(1-min(x,200)/200)**2))-t
        if r>0.05: pts.append(V(x,0,r))
    sp=cq.Edge.makeSpline(pts); p0,p1=pts[0],pts[-1]
    w=cq.Wire.assembleEdges([sp, cq.Edge.makeLine(p1,V(p1.x,0,0)), cq.Edge.makeLine(V(p1.x,0,0),V(p0.x,0,0)), cq.Edge.makeLine(V(p0.x,0,0),p0)])
    return cq.Solid.revolve(cq.Face.makeFromWires(w),360,V(0,0,0),V(1,0,0))
