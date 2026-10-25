"""Reopened native solver and face-area coverage of every adhesive interface."""
import sys,json,math
from pathlib import Path
import FreeCAD as A,Part,Assembly
sys.path.append(str(Path(A.getHomePath())/'Mod/Assembly'));import JointObject
R=Path(__file__).resolve().parents[1];g=json.loads((R/'reports/geometry_checks.json').read_text());d=A.openDocument(str(R/'cad/RescU_P06_Rib_Saddle_Assembly.FCStd'))
def gs(o):
 s=o.Shape.copy();s.Placement=o.getGlobalPlacement()*o.Placement.inverse()*s.Placement;return s
def contact_area(a,b):
 # Solid intersection intentionally omits lower-dimensional contact. Intersect
 # coplanar faces instead; do not mistake zero distance for a developed overlap.
 area=0.
 for fa in a.Faces:
  if type(fa.Surface).__name__!='Plane':continue
  for fb in b.Faces:
   if type(fb.Surface).__name__!='Plane':continue
   n1=fa.normalAt(0,0);n2=fb.normalAt(0,0)
   if abs(abs(n1.dot(n2))-1)>1e-6 or fa.distToShape(fb)[0]>1e-6:continue
   area+=fa.common(fb).Area
 return area
coverage=[]
for row in g['bond_interfaces']:
 a=Part.makeCompound([gs(d.getObject(n)) for n in row['bond_parts']]);values=[]
 for neighbor in row['contacts']:
  b=Part.makeCompound([gs(d.getObject(n)) for n in neighbor['parts']]);area=contact_area(a,b);ratio=area/row['mean_projected_area_mm2']
  assert .9<ratio<1.1,(row['bond_parts'],neighbor['parts'],area,ratio)
  neighbor['area_mm2']=area;neighbor['gap_mm']=a.distToShape(b)[0];values.append(area)
 coverage.append(dict(bond_parts=row['bond_parts'],minimum_contact_area_mm2=min(values),mean_projected_area_mm2=row['mean_projected_area_mm2'],minimum_coverage_ratio=min(values)/row['mean_projected_area_mm2']))
solves=[]
for side in ['PosY','NegY']:
 asm=d.getObject('MotorArm_'+side);assert asm.solve()==0
 rib=d.getObject('Wing_Spar_Rib1_'+side);before=rib.Placement;rib.Placement=A.Placement(A.Vector(before.Base.x+2,before.Base.y+1,before.Base.z+3),A.Rotation(2,0,0)*before.Rotation)
 code=asm.solve();err=(rib.Placement.Base-before.Base).Length;angle=(rib.Placement.Rotation.inverted()*before.Rotation).Angle
 assert code==0 and err<1e-5 and angle<1e-5
 solves.append(dict(arm=side,solve_code=int(code),rib_perturbation_translation_residual_mm=err,rotation_residual_rad=angle))
assert d.MotorArmPair.solve()==0
assert not g['physical_collisions']
assert g['STEP']['pass']
assert all(r['intersection_mm3']<1e-4 for r in g['wing_checks_after_relief'])
w=A.openDocument(str(R.parent/'v4-attachments/cad/RescU_P04_Attachment_Study.FCStd'))
for side in ['PosY','NegY']:
 masks=[]
 for o in d.Objects:
  if not o.Name.startswith('Slot_'+side+'_'):continue
  b=o.Shape.BoundBox;top=14.3 if '_Spar_' in o.Name else 10.3;masks.append(Part.makeBox(b.XLength,b.YLength,top+30,A.Vector(b.XMin,b.YMin,-30)))
 core=w.getObject('Wing_'+side+'_Ravatherm_Core_Exposed').Shape;removed=core.common(Part.makeCompound(masks)).Volume
 row=next(q for q in g['wing_material_revisions'] if q['side']==side and q['material']=='XPS');error=abs(removed-row['removed_volume_mm3']);row.update(intersection_volume_mm3=removed,volume_conservation_error_mm3=error,quantity_screen_pass=error<max(.1,.01*removed));assert row['quantity_screen_pass']
if 'foam_pockets' in g:g['initial_foam_pockets_before_installation_clearance']=g.pop('foam_pockets')
result=dict(status='PASS: geometric coverage, native reopen/solver and explicit slot/spar compatibility checks',bond_interface_groups=len(coverage),coverage=coverage,solver_tests=solves,limits='No chemical adhesion, peel/fatigue or skin-slot reinforcement qualification. STEP is arm-only; relieved skins/cores remain native context objects.')
(R/'reports/geometry_checks.json').write_text(json.dumps(g,indent=2));(R/'reports/validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],minimum_coverage_ratio=min(x['minimum_coverage_ratio'] for x in coverage),interfaces=len(coverage),solver_tests=solves),indent=2))
