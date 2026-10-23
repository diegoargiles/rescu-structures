"""Correct drawing transcription: body length20 +/-0.1 mm, not +/-1 mm.

Only the reference maximum-bell envelope changes; physical geometry unchanged.
"""
import json,hashlib
from pathlib import Path
import FreeCAD as A,Part,Assembly
R=Path(__file__).resolve().parents[1];p=R/'cad/RescU_P05_Motor_Arm_Assembly.FCStd';d=A.openDocument(str(p));a=json.loads((R/'reports/assembly_checks.json').read_text())
checks=[]
for side,y in [('PosY',265.),('NegY',-265.)]:
 for end,x in [('Front',235.),('Rear',555.)]:
  tag=side+'_'+end;o=d.getObject('MaxMotorBell_'+tag);o.Shape=Part.makeCylinder(17.95,17.1,A.Vector(x,y,14))
  distances=[]
  for r in a['components']:
   if tag not in r['name'] or r['name'].startswith(('UM2807','MotorScrew_')):continue
   q=d.getObject(r['name']);s=q.Shape.copy();s.Placement=q.getGlobalPlacement()*q.Placement.inverse()*s.Placement
   distances.append(o.Shape.distToShape(s)[0])
  v=min(distances);assert abs(v-3.)<1e-6
  for r in a['clearances']:
   if r.get('station')==tag and r['check']=='max_bell_to_mount':r['min_distance_mm']=v
  checks.append(dict(station=tag,minimum_external_clearance_mm=v))
d.recompute();d.save();a['native_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();a['motor']['body_length_tolerance_mm']=.1
a['drawing_tolerance_revision']=dict(body_length_tolerance_mm=.1,maximum_reference_body_length_mm=20.1,physical_geometry_changed=False,external_clearance_checks=checks)
(R/'reports/assembly_checks.json').write_text(json.dumps(a,indent=2));(R/'data/motor_spec.json').write_text(json.dumps(a['motor'],indent=2))
print('Reference gauge corrected to20.1mm maximum body; external clearance remains3mm')
