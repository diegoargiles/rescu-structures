import json
from pathlib import Path
import FreeCAD as A,Assembly
R=Path(__file__).resolve().parents[1];g=json.loads((R/'reports/build.json').read_text());d=A.openDocument(str(R/'cad/RescU_P07_Wing_Arm_Integration.FCStd'))
def gs(o):
 s=o.Shape.copy();s.Placement=o.getGlobalPlacement()*o.Placement.inverse()*s.Placement;s.tessellate(.3);return s
bad=[]
for side in ['PosY','NegY']:
 spar=gs(d.getObject('WingSpar_'+side));print(side,'spar',spar.optimalBoundingBox(),flush=True)
 for row in g['new_components']:
  if row['side']!=side or row['role']=='replacement':continue
  s=gs(d.getObject(row['name']))
  if not s.BoundBox.intersect(spar.BoundBox) or s.distToShape(spar)[0]>1e-4:continue
  v=s.common(spar).Volume
  if v>1e-3:
   q=dict(name=row['name'],volume_mm3=v);bad.append(q);print(q,flush=True)
(R/'reports/spar_clashes.json').write_text(json.dumps(bad,indent=2))
