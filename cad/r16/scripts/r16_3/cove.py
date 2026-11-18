import numpy as np, json, cadquery as cq
from cadquery import Vector as V
prof=np.load('/home/claude/z30_profile.npy'); zl=prof[:,0]; Ra=prof[:,1]
XC, ZOFF, C = 84.0, -90.0, 5.0
ZTOP = ZOFF + 103.36
def req(z): return np.where(z<ZTOP, np.interp(z-ZOFF-C, zl, Ra, left=Ra[0], right=0.0)+C, 0.0)
def profile_face(pts, fil):
    w = cq.Wire.makePolygon([V(r,0,z) for r,z in pts], close=True)
    f = cq.Face.makeFromWires(w)
    vs = [v for v in f.Vertices() if any(abs(v.X-r)<1e-6 and abs(v.Z-z)<1e-6 for (r,z),R in fil.items() if R)]
    for (r,z),R in fil.items():
        v=[v for v in f.Vertices() if abs(v.X-r)<1e-6 and abs(v.Z-z)<1e-6]
        if v: f = f.fillet2D(R, v)
    return f
PTS=[(0,-140),(83.0,-140),(83.0,-62),(81.2,-48),(67.8,-34),(41.4,-6.6),(20.55,-5.4),(20.55,ZTOP),(0,ZTOP)]
FIL={(83.0,-62):10,(81.2,-48):10,(67.8,-34):12,(41.4,-6.6):2.5,(20.55,-5.4):3}
def build():
    f=profile_face(PTS,FIL)
    return f
def check(f):
    # sample cutter radius vs z by slicing the profile face with horizontal lines
    bad=[]; out=[]
    for z in np.arange(-100,ZTOP-0.05,0.25):
        e=cq.Edge.makeLine(V(0,0,z),V(200,0,z))
        sec=f._entities('Face')  # placeholder
        isec=cq.Shape.cast(__import__('OCP.BRepAlgoAPI',fromlist=['x']).BRepAlgoAPI_Common(f.wrapped,e.wrapped).Shape())
        rr=max((v.X for v in isec.Vertices()), default=0)
        out.append((z,rr))
        if rr < float(req(z))-1e-6: bad.append((z,rr,float(req(z))))
    return np.array(out),bad
if __name__=='__main__':
    f=build(); prof_,bad=check(f)
    print('violations', len(bad), bad[:10])
    fc=prof_[prof_[:,0]>=-3.0]; print('max r for z>=-3 :', fc[:,1].max())
    np.save('cutter_profile.npy',prof_)
    cq.exporters.export(cq.Workplane().add(f),'cutter_profile.step')
