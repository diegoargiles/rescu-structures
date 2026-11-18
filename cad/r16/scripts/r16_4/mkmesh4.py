import cadquery as cq, numpy as np, pickle, os
names=pickle.load(open('/home/claude/verify4/orig/names.pkl','rb')); nm=[n.split('/')[-1] for n in names]
half=cq.Solid.makeBox(2000,400,400,cq.Vector(-100,0,-200))
for i,n in enumerate(nm):
    s=cq.Shape.importBrep(f'/home/claude/verify4/orig/{i:03d}.brep'); b=s.BoundingBox()
    if b.xmin>420 or 'Envelope' in n: continue
    if not (n.endswith('_Fuselage') or 'Wing' in n or 'Boom' in n): continue
    fine = any(k in n for k in ('Nose','Z30','Shelf','Camera_Mount'))
    for tag in ('full','half'):
        sh=s
        if tag=='half' and not n.startswith('REF_Z30'):
            if b.ymax<=0: continue
            try: sh=s.intersect(half)
            except Exception: continue
        if sh.Volume()<1e-6: continue
        v,t=sh.tessellate(0.03 if fine else 0.2,0.15)
        np.savez(f'mesh4/{tag}__{n}.npz',v=np.array([p.toTuple() for p in v]),t=np.array(t))
print(len(os.listdir('mesh4')))
