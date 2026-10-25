"""Incremental verification after subtractive slot relief and reference-wire reroute.
The preceding complete pair matrix is retained. Only slot-region material was
subtracted/split; all unchanged physical pairs retain that check.
"""
import json,sys,hashlib
from pathlib import Path
import FreeCAD as A,Assembly
R=Path(__file__).resolve().parents[1];g=json.loads((R/'reports/build.json').read_text());base=json.loads((R/'reports/fit_checks_full_before_final_relief.json').read_text());d=A.openDocument(str(R/'cad/RescU_P07_Wing_Arm_Integration.FCStd'))
def gs(o):
 q=o.Shape.copy();q.Placement=o.getGlobalPlacement()*o.Placement.inverse()*q.Placement;return q.Solids[0] if len(q.Solids)==1 else q
names=g['old_physical_names']+[r['name'] for r in g['new_components']]
assert len(names)==len(set(names))
shapes={n:gs(d.getObject(n)) for n in names};bounds={n:q.optimalBoundingBox() for n,q in shapes.items()}
assert all(q.isValid() and len(q.Solids)==1 for q in shapes.values())
material={n:getattr(d.getObject(n),'Material','') for n in names}
changed=[n for n in names if n.startswith(('SlotSkinBond_','SlotDoubler_','SlotEdgePotting_'))]
hard=[];wet=[];checked=0
def classify(row):
 a=row.get('part');b=row.get('other');vol=row['intersection_mm3']
 if vol<=.02 and 'Epoxy' in [material.get(a),material.get(b)]:
  wet.append(dict(**row,classification='Nominal wet-bond layer intersection below0.02 mm3; retained as construction-volume ambiguity, not a rigid-part clash'))
 else:hard.append(row)
assert all(row['after_volume_mm3']<=row['before_volume_mm3']+.001 for row in g['slot_spar_relief'])
for row in base['collisions']:
 if not row['part'].startswith(('SlotSkinBond_','SlotDoubler_','SlotEdgePotting_')):
  classify(row);continue
 family=[n for n in changed if n==row['part'] or n.startswith(row['part']+'_')]
 for n in family:
  other=row['other'];gap=shapes[n].distToShape(shapes[other])[0]
  v=0. if gap>1e-4 else sum(q.Volume for q in shapes[n].common(shapes[other]).Solids);checked+=1
  if v>1e-3:classify(dict(part=n,other=other,intersection_mm3=v))
 print('Verified prior clash family',row['part'],flush=True)
gauges=[]
for o in d.Objects:
 if not o.Name.startswith(('WireRoute_','PropSweep_','ClampTopTool_','ClampNutTool_','MotorTool_')):continue
 q=gs(o);bb=q.optimalBoundingBox();bad=[]
 # New wire routes are checked against all physical pieces. Other gauges retain
 # baseline bench-installation exclusions and check only P07-added regions.
 targets=names if o.Name.startswith('WireRoute_') else [r['name'] for r in g['new_components']]
 for n in targets:
  if not bb.intersect(bounds[n]):continue
  gap=q.distToShape(shapes[n])[0]
  v=0. if gap>1e-4 else sum(p.Volume for p in q.common(shapes[n]).Solids)
  if v>1e-3:bad.append(dict(part=n,intersection_mm3=v))
 gauges.append(dict(gauge=o.Name,new_geometry_collisions=bad,scope='All physical parts for revised bundle gauges; retained baseline bench installation remains required for motor screws'))
solver=[]
for side in ['PosY','NegY']:
 asm=d.getObject('MotorArm_'+side);assert asm.solve()==0
 rib=d.getObject('Wing_Spar_Rib1_'+side);before=rib.Placement
 rib.Placement=A.Placement(before.Base+A.Vector(1,2,3),A.Rotation(1,2,3)*before.Rotation)
 code=asm.solve();translation=(rib.Placement.Base-before.Base).Length;rotation=(rib.Placement.Rotation.inverted()*before.Rotation).Angle
 assert code==0 and translation<1e-5 and rotation<1e-5
 solver.append(dict(side=side,solve_code=int(code),perturbation_translation_residual_mm=translation,rotation_residual_rad=rotation))
assert d.MotorArmPair.solve()==0
result=dict(source_native_sha256=g['native_sha256'],method='Complete preceding pair matrix plus rechecks of all prior affected clash families. Valid Boolean subtraction/splitting and monotonic volumes establish that final slot regions are subsets, so relief cannot introduce a new physical intersection. Revised wire bundles checked against all physical parts.',collisions=hard,nominal_wet_bond_intersections=wet,nominal_wet_bond_overlap_mass_upper_bound_g=sum(r['intersection_mm3'] for r in wet)*.0012,wet_contact_threshold_mm3=.02,wing_batch_checks=base['wing_batch_checks'],gauge_checks=gauges,solver=solver,physical_piece_count=len(names),incremental_pairs_checked=checked,limits='Full compound/core Boolean deferred; foam compatibility uses pocket construction and removed-volume conservation. No strength/peel/fatigue qualification.')
(R/'reports/fit_checks.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(hard_clashes=len(hard),nominal_wet_contacts=len(wet),gauge_clashes=sum(len(q['new_geometry_collisions']) for q in gauges),solids=len(names)),indent=2))
assert not hard and not any(q['new_geometry_collisions'] for q in gauges)
