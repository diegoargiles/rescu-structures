import json, glob, os, cadquery as cq
from cadquery import Vector as V
G='../gear2/out_deployed'
meta=json.load(open(f'{G}/meta.json'))['parts']
rep={}
for n,(g,sub) in meta.items():
    s=cq.Shape.importBrep(f'{G}/{n}.brep')
    rep[n]=s.translate(V(35,0,0)) if '_LG_Front_' in n else s
for side in 'RL':
    rep[f'Boom_Lower_Half_Boom_{side}']=cq.Shape.importBrep(f'{G}/MOD__Boom_Lower_Half_Boom_{side}.brep').translate(V(35,0,0))
rep['Fuselage_Seam_Strips_GFRP_Fuselage']=cq.Shape.importBrep(f'{G}/MOD__Fuselage_Seam_Strips_GFRP_Fuselage.brep')
HOLES=[(310.0,4.2,6.1),(345.0,4.0,3.1),(385.0,3.0,1.6)]
ann=cq.Solid.makeCylinder(45.0,400,V(250,0,0),V(1,0,0)).cut(cq.Solid.makeCylinder(44.67,400,V(250,0,0),V(1,0,0)))
def holes(dx):
    out=None
    for x,z,r in HOLES:
        c=cq.Solid.makeCylinder(r,120,V(x+dx,-60,z),V(0,1,0)); out=c if out is None else out.fuse(c)
    return out
for side in ('Left','Right'):
    sh=cq.Shape.importBrep(f'{G}/MOD__Fuselage_Shell_{side}_GFRP_Fuselage.brep')
    half=cq.Solid.makeBox(2000,1000,2000,V(0,-1000 if side=='Left' else 0,-1000))
    rep[f'Fuselage_Shell_{side}_GFRP_Fuselage']=sh.fuse(holes(0).intersect(ann).intersect(half)).clean().cut(holes(35))
for n,s in rep.items(): s.exportBrep(f'out/{n}.brep')
json.dump({'replace':sorted(rep),'add':[],'remove':[]},open('ops.json','w'),indent=1)
print(len(rep))
