import cadquery as cq, sys
from OCP.TopExp import TopExp
from OCP.TopTools import TopTools_IndexedDataMapOfShapeListOfShape
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE
Nc=cq.Shape.importBrep('Nc.brep')
outer=[f for f in Nc.Faces() if f.geomType()=='REVOLUTION'][0]
aft=[f for f in Nc.Faces() if f.geomType()=='PLANE' and f.BoundingBox().xmin>178][0]
cove=[f for f in Nc.Faces() if not f.isSame(outer) and not f.isSame(aft)]
lip=[e for e in outer.Edges() if any(e.isSame(e2) for f in cove for e2 in f.Edges())]
print('lip edges', len(lip), [round(e.Length(),1) for e in lip])
for R in [float(a) for a in sys.argv[1:]]:
    try:
        s=Nc.fillet(R, lip); print('R',R,'valid',s.isValid(), len(s.Faces()), round(s.Volume()))
        if s.isValid(): s.exportBrep(f'Nf_{R:g}.brep'); break
    except Exception as ex: print('R',R,'fail',ex)
