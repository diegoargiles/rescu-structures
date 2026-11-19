import sys, time, cadquery as cq, numpy as np
sys.path.insert(0,'/home/claude/rescu-structures/cad/r15/scripts')
from geom import *
from cadquery import Vector as Vv
t0=time.time()
which=sys.argv[1]; Rs=[float(a) for a in sys.argv[2:]]
if which=='wing':
    other=cq.Solid.makeLoft([wing_wire(0.0), wing_wire(150.0)],True); xcut=wxle(45)+0.95*wchord(45)
else:
    other=cq.Solid.makeLoft([tail_wire(1,0.0), tail_wire(1,TSPAN)],True); xcut=1031.0
clip=cq.Solid.makeBox(2000,2000,2000,Vv(-1000+xcut-2000+1000,-1000,-1000))  # x <= xcut
clip=cq.Solid.makeBox(xcut+500,2000,2000,Vv(-500,-1000,-1000))
oc=other.intersect(clip)
fus=fus_solid().val()
U=fus.fuse(oc)
U=U.Solids()[0] if U.ShapeType()!='Solid' else U
fusF=[f for f in U.Faces() if f.geomType() in ('CONE','CYLINDER') ]
lofF=[f for f in U.Faces() if f.geomType()=='BSPLINE']
E=[]
for f in lofF:
    for e in f.Edges():
        if any(e.isSame(x) for g in fusF for x in g.Edges()): E.append(e)
# unique
U_E=[]
for e in E:
    if not any(e.isSame(x) for x in U_E): U_E.append(e)
print(which,'junction edges',len(U_E),[round(e.Length(),1) for e in U_E], 'xcut', round(xcut,1))
for R in Rs:
    try:
        F=U.fillet(R,U_E)
        if F.isValid():
            fair=F.cut(U).intersect(clip)
            print(which,'R',R,'OK vol',round(fair.Volume(),1), len(fair.Solids()), round(time.time()-t0)); fair.exportBrep(f'p/fair_{which}_R{R:g}.brep'); other.exportBrep(f'p/{which}_outer.brep'); break
        else: print('R',R,'invalid')
    except Exception as ex: print(which,'R',R,'fail',str(ex)[:60])
