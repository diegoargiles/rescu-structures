"""Proposed external-side lead gauges, avoiding the lower wing skin.
No added wire mass: supplied motor-wire allocation remains unchanged.
"""
import json,hashlib
from pathlib import Path
import FreeCAD as A,Part,Assembly
R=Path(__file__).resolve().parents[1];g=json.loads((R/'reports/build.json').read_text());d=A.openDocument(str(R/'cad/RescU_P07_Wing_Arm_Integration.FCStd'))
V=A.Vector;routes=[]
for side,y,sign in [('PosY',265.,1),('NegY',-265.,-1)]:
 for end,x,direction in [('Front',235.,1),('Rear',555.,-1)]:
  for k in [0]:
   outside=y+sign*31
   pts=[V(x+direction*23,y,18),V(x+direction*36,outside,18),V(x+direction*48,outside,-8),V(x+direction*110,outside,-8)]
   segments=[Part.makeCylinder(4.,(q-p).Length,p,q-p) for p,q in zip(pts,pts[1:])]
   # Spheres cover nominal direction changes as clearance envelopes. A real
   # cable bend radius/exit and ESC termination still need hardware verification.
   segments += [Part.makeSphere(6.,p) for p in pts[1:-1]]
   o=d.getObject('WireRoute_'+side+'_'+end+'_'+str(k));o.Shape=Part.makeCompound(segments)
   o.Label='P07 three-wire bundle | assumed8 mm envelope | '+side+' '+end
   routes.append(dict(gauge=o.Name,conductors=3,centerline_length_mm=sum((q-p).Length for p,q in zip(pts,pts[1:])),bundle_radius_assumption_mm=4.,corner_clearance_radius_assumption_mm=6.,side_offset_mm=sign*31,route_z_mm=-8.,start_status='Proposed free-air start outside motor envelope; actual motor exit/bend radius unverified',mass_status='Reference clearance envelope only; no second wire mass added to supplied52g motor-with-wire allocation'))
  for k in [1,2]:
   old=d.getObject('WireRoute_'+side+'_'+end+'_'+str(k))
   if old:d.removeObject(old.Name)
d.recompute();d.save();g['proposed_wire_routes']=routes;g['native_sha256']=hashlib.sha256(Path(d.FileName).read_bytes()).hexdigest();(R/'reports/build.json').write_text(json.dumps(g,indent=2));print('Routed four three-wire bundle gauges outside arm/wing interfaces')
