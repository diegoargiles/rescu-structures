import cadquery as cq
from cadquery import Vector as Vv
fw=cq.Shape.importBrep('out/Wing_Root_Fairings_ASA_Fuselage.brep')
for side,sg in (('R',1),('L',-1)):
    d=cq.Shape.importBrep(f'out/Wing_Root_Diaphragm_GFRP_Wing_{side}.brep'); f=[s for s in fw.Solids() if s.Center().y*sg>0][0]
    sol=[]
    for s in d.Solids():
        for t in (0.5,1,1.5,2,2.5,3,4,5,6,8): s=s.cut(f.translate(Vv(0,-sg*t,0)))
        sol+=s.Solids()
    d2=cq.Compound.makeCompound(sol)
    for t in (1,2,3):
        v=sum(x.translate(Vv(0,sg*t,0)).intersect(f).Volume() for x in d2.Solids()); print(side,'slide',t,'overlap',round(v,4))
    d2.exportBrep(f'out/Wing_Root_Diaphragm_GFRP_Wing_{side}.brep')
