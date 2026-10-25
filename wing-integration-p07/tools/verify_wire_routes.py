"""Recheck changed reference bundle envelopes; preserve verified physical fit."""
import json
from pathlib import Path
import FreeCAD as A,Assembly
R=Path(__file__).resolve().parents[1];g=json.loads((R/'reports/build.json').read_text());r=json.loads((R/'reports/fit_checks.json').read_text());d=A.openDocument(str(R/'cad/RescU_P07_Wing_Arm_Integration.FCStd'))
def gs(o):
 s=o.Shape.copy();s.Placement=o.getGlobalPlacement()*o.Placement.inverse()*s.Placement;return s
names=g['old_physical_names']+[row['name'] for row in g['new_components']];shapes={n:gs(d.getObject(n)) for n in names};bounds={n:q.optimalBoundingBox() for n,q in shapes.items()}
checks=[]
for o in [p for p in d.Objects if p.Name.startswith('WireRoute_')]:
 q=gs(o);bb=q.optimalBoundingBox();bad=[]
 for n in names:
  if not bb.intersect(bounds[n]):continue
  gap=q.distToShape(shapes[n])[0]
  volume=0. if gap>1e-4 else sum(p.Volume for p in q.common(shapes[n]).Solids)
  if volume>1e-3:bad.append(dict(part=n,intersection_mm3=volume))
 checks.append(dict(gauge=o.Name,new_geometry_collisions=bad,scope='Revised8 mm reference bundle against all physical parts; actual motor lead exit and bend radius remain unverified'))
 print(o.Name,bad,flush=True)
r['gauge_checks']=[q for q in r['gauge_checks'] if not q['gauge'].startswith('WireRoute_')]+checks
r['source_native_sha256']=g['native_sha256'];r['reference_only_update']='Bundle inlet raised to18 mm to clear the11 mm mount-plate top. Physical solids unchanged; physical pair matrix and solver recovery remain applicable.'
(R/'reports/fit_checks.json').write_text(json.dumps(r,indent=2))
assert not r['collisions'] and not any(q['new_geometry_collisions'] for q in checks)
for side in ['PosY','NegY']:assert d.getObject('MotorArm_'+side).solve()==0
print('All four bundle gauges clear all modeled physical parts')
