import cadquery as cq, itertools, json, time, sys, os
sys.argv.append('--nostep')
OUT='/home/claude/full/out'
exec(open('/home/claude/full/assemble_full.py').read().split("motor = cq.Shape")[0])
P={}
for g,parts in groups.items():
    for k,s in parts.items(): P[f'{g}/{k}']=s
m=cq.Shape.importBrep('/home/claude/cadwork/motor/um.brep')
for sg,sd in ((1,'R'),(-1,'L')):
    for xm in (170,600): P[f'Boom_{sd}/UM2807_{xm}']=m.translate(cq.Vector(xm,sg*265,-12.8))
names=sorted(P); bb={k:P[k].BoundingBox() for k in names}
def ov(a,b,g=0.0): return not (a.xmax<b.xmin-g or b.xmax<a.xmin-g or a.ymax<b.ymin-g or b.ymax<a.ymin-g or a.zmax<b.zmin-g or b.zmax<a.zmin-g)
from vol import pvol
res=[]; t=time.time(); n=0
for a,b in itertools.combinations(names,2):
    if a.split('/')[1].startswith('REF') and b.split('/')[1].startswith('REF'): continue
    if not ov(bb[a],bb[b]): continue
    n+=1
    try:
        i=P[a].intersect(P[b]); v=pvol(i) if i.Solids() else 0.0
    except Exception as e: v=-1
    if v>0.05 or v<0: res.append((a,b,round(v,2))); print('!!',a,b,round(v,2)); sys.stdout.flush()
print('pairs checked',n,'time',round(time.time()-t))
json.dump(res,open(f'{OUT}/interference_full.json','w'),indent=1)
