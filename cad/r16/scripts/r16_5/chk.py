import cadquery as cq, pickle, json
from cadquery import Vector as V
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
an=[x.split('/')[-1] for x in pickle.load(open('/home/claude/verify5/orig/names.pkl','rb'))]
sn=[x[0].split('/')[-1] for x in pickle.load(open('stn/names.pkl','rb'))]
A={k:cq.Shape.importBrep(f'/home/claude/verify5/orig/{i:03d}.brep').translate(V(0,0,300)) for i,k in enumerate(an) if 'Envelope' not in k}
S={k:cq.Shape.importBrep(f'stn/{i:03d}.brep') for i,k in enumerate(sn)}
zt=max(s.BoundingBox().zmax for s in S.values()); print('station top z', round(zt,1))
res=[]; near=[]
for ka,a in A.items():
    ba=a.BoundingBox()
    if ba.zmin>zt+5: continue
    for ks,s in S.items():
        bs=s.BoundingBox()
        g=max(bs.xmin-ba.xmax,ba.xmin-bs.xmax,bs.ymin-ba.ymax,ba.ymin-bs.ymax,bs.zmin-ba.zmax,ba.zmin-bs.zmax)
        if g>20: continue
        m=BRepExtrema_DistShapeShape(a.wrapped,s.wrapped); m.Perform(); d=m.Value()
        v=a.intersect(s).Volume() if d<1e-6 else 0.0
        res.append((round(d,2),round(v,3),ka,ks))
res.sort()
for r in res[:25]: print(r)
cam=A['REF_Z30_Camera_Gimbal_Fuselage'].BoundingBox(); print('camera bottom (level) z above floor', round(cam.zmin,1))
json.dump(res,open('seated_check.json','w'),indent=0)
