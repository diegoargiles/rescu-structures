import cadquery as cq
from OCP.BRepOffsetAPI import BRepOffsetAPI_MakeOffsetShape
from OCP.BRepOffset import BRepOffset_Skin
from OCP.GeomAbs import GeomAbs_Arc, GeomAbs_Intersection
for w in ('wing','tail'):
    o=cq.Shape.importBrep(f'p/{w}_outer.brep')
    for j in (GeomAbs_Arc, GeomAbs_Intersection):
        m=BRepOffsetAPI_MakeOffsetShape(); m.PerformByJoin(o.wrapped,0.5,1e-3,BRepOffset_Skin,False,False,j); m.Build()
        if m.IsDone():
            s=cq.Shape.cast(m.Shape()); print(w, s.ShapeType(), s.isValid()); 
            if s.ShapeType()=='Shell': s=cq.Solid.makeSolid(s)
            s.exportBrep(f'p/{w}_outer_off05.brep'); break
        else: print(w,'fail',j)
    fr=cq.Shape.importBrep(f'p/fair_{w}_R{"6" if w=="wing" else "3.5"}.brep')
    f2=fr.cut(s); print(w,'fair gap', f2.isValid(), round(fr.Volume(),1),'->',round(f2.Volume(),1)); f2.exportBrep(f'p/fair_{w}_gap.brep')
