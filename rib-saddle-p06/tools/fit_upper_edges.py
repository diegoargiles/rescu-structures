"""Trim splice upper edges to actual core envelope; restrict skin slots to Z<=7.

Thin spline-skin Boolean volume conservation is checked separately. No skin
mass credit is accepted when that gate fails, even if the BREP is valid.
"""
import json,hashlib
from pathlib import Path
import FreeCAD as A,Part,Assembly
R=Path(__file__).resolve().parents[1];native=R/'cad/RescU_P06_Rib_Saddle_Assembly.FCStd';g=json.loads((R/'reports/geometry_checks.json').read_text());d=A.openDocument(str(native));w=A.openDocument(str(R.parent/'v4-attachments/cad/RescU_P04_Attachment_Study.FCStd'));V=A.Vector
def gs(o):
 s=o.Shape.copy();s.Placement=o.getGlobalPlacement()*o.Placement.inverse()*s.Placement;return s
def center(s):return sum((q.CenterOfMass*q.Volume for q in s.Solids),V())/s.Volume
for side,y in [('PosY',265.),('NegY',-265.)]:
 core=w.getObject('Wing_'+side+'_Ravatherm_Core_Exposed').Shape.copy();core.translate(V(0,0,-.3))
 below=Part.makeBox(200,100,37,V(300,y-50,-30));above=Part.makeBox(200,100,40,V(300,y-50,7))
 for row in g['added_components']:
  if row['assembly']!='MotorArm_'+side or not row['name'].startswith('SplicePlate_'):continue
  o=d.getObject(row['name']);s=gs(o);s=s.common(below).fuse(s.common(above).common(core)).removeSplitter();assert s.isValid() and len(s.Solids)==1
  o.Shape=s;o.Placement=A.Placement(V(0,-y,0),A.Rotation())*s.Placement;row['volume_mm3']=s.Volume;row['mass_kg']=s.Volume*1850e-9;c=center(s);row['centroid_mm']=[c.x,c.y,c.z];o.AccountedMass_kg=row['mass_kg']
 masks=[]
 for slot in [o for o in d.Objects if o.Name.startswith('Slot_'+side+'_')]:
  b=slot.Shape.BoundBox;slot.Shape=Part.makeBox(b.XLength,b.YLength,37,V(b.XMin,b.YMin,-30));masks.append(slot.Shape)
 mask=Part.makeCompound(masks);skin=w.getObject('Wing_'+side+'_GFRP_Skin_Exposed').Shape;revised=skin.cut(mask);assert revised.isValid();d.getObject('RelievedWingSkin_'+side).Shape=revised
 removed=skin.common(mask);v=removed.Volume;delta=skin.Volume-revised.Volume;error=abs(delta-v)
 verts,_=removed.tessellate(.1)
 for row in g['wing_material_revisions']:
  if row['side']==side and row['material']=='GFRP':row.update(revised_volume_mm3=revised.Volume,removed_volume_mm3=delta,removed_mass_kg=delta*1850e-9,intersection_volume_mm3=v,volume_conservation_error_mm3=error,quantity_screen_pass=delta>=0 and error<max(.1,.01*v),mass_credit_accepted=False,mass_credit_kg=0.,sampled_removed_z_bounds_mm=[min(p.z for p in verts),max(p.z for p in verts)],bounds_note='Original BREP bounds are loose; sampled bounds are tessellated diagnostics, not exact extrema.')
 shapes=[gs(d.getObject(row['name'])) for row in g['added_components'] if row['assembly']=='MotorArm_'+side];compound=Part.makeCompound(shapes)
 # Any remaining upper-skin penetration is a failed fit gate.
 assert compound.common(skin).common(above).Volume<1e-4
 for row in g['wing_checks_after_relief']:
  if row['side']==side and row['target']=='GFRP_Skin_Exposed':row['intersection_mm3']=compound.common(revised).Volume;row['min_gap_mm']=compound.distToShape(revised)[0];assert row['intersection_mm3']<1e-4
 print('Upper edges/skin slot',side,'skin mass-conservation error mm3',round(error,3),flush=True)
g['wing_slots']['skin_cut_upper_z_mm']=7.;g['wing_slots']['foam_pocket_note']='Foam pockets include the full-height installation envelope; skin openings restricted to Z<=7 mm.'
g['skin_mass_credit_policy']='Retain complete P05 wing-skin mass; Boolean volume-conservation gate unresolved. No cutout mass credit or future slot-reinforcement mass assumed.'
# Repeat physical fit after the small trimming operation (subtraction cannot add overlap).
assert all(o.Shape.isValid() for o in d.Objects if o.Name.startswith('SplicePlate_'))
d.recompute();d.save();g['native_sha256']=hashlib.sha256(native.read_bytes()).hexdigest()
p05=json.loads((R.parent/'motor-arm-p05/reports/assembly_checks.json').read_text());names=[r['name'] for r in p05['components']]+[r['name'] for r in g['added_components']]
ed=A.newDocument('P06_Final_STEP');objs=[];expected=[]
for name in names:
 s=gs(d.getObject(name));o=ed.addObject('Part::Feature',name);o.Shape=s;objs.append(o);expected+=s.Solids
step=R/'cad/RescU_P06_Arm_Pair.step';ed.recompute();Part.export(objs,str(step));q=Part.Shape();q.read(str(step));remaining=[(s.Volume,s.CenterOfMass) for s in q.Solids];errors=[]
for s in expected:
 v=s.Volume;c=s.CenterOfMass;b=min(remaining,key=lambda x:(x[1]-c).Length+abs(x[0]-v)/max(v,1));remaining.remove(b);errors.append(((b[1]-c).Length,abs(b[0]-v)/max(v,1)))
g['STEP']=dict(valid=q.isValid(),native_solids=len(expected),step_solids=len(q.Solids),max_center_error_mm=max(x[0] for x in errors),max_relative_volume_error=max(x[1] for x in errors));g['STEP']['pass']=q.isValid() and not remaining and g['STEP']['max_center_error_mm']<.001 and g['STEP']['max_relative_volume_error']<.001;assert g['STEP']['pass']
g['STEP_sha256']=hashlib.sha256(step.read_bytes()).hexdigest();(R/'reports/geometry_checks.json').write_text(json.dumps(g,indent=2));print('Reprofiled native and STEP verified')
