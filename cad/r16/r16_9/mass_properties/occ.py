import sys, json, numpy as np, cadquery as cq
sys.path.insert(0,'/home/claude/work/fdr'); from vr import shape, NAMES
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
out={}
for k in NAMES:
    s=shape(k); g=GProp_GProps(); BRepGProp.VolumeProperties_s(s.wrapped,g)
    c=g.CentreOfMass(); M=g.MatrixOfInertia()
    I=[[M.Value(i,j) for j in (1,2,3)] for i in (1,2,3)]
    out[k]=dict(vol=g.Mass(), c=[c.X(),c.Y(),c.Z()], I=I, nsol=len(s.Solids()))
json.dump(out,open('occ.json','w'))
print(len(out))
