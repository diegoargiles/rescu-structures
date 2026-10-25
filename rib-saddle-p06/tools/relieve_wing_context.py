"""Proposed skin/core entry slots: keep original source untouched.

Slots are an explicit interface proposal, not permission to cut a flight wing.
Their structural edge reinforcement remains a wing-group requirement.
"""
import json,hashlib
from pathlib import Path
import FreeCAD as A,Part,Assembly
R=Path(__file__).resolve().parents[1];W=(R.parent/'v4-attachments' if (R.parent/'v4-attachments').exists() else R.parent);native=R/'cad/RescU_P06_Rib_Saddle_Assembly.FCStd'
d=A.openDocument(str(native));w=A.openDocument(str(W/'cad/RescU_P04_Attachment_Study.FCStd'));g=json.loads((R/'reports/geometry_checks.json').read_text())
context=d.WingPocketContext;revisions=[];checks=[]
for side,y in [('PosY',265.),('NegY',-265.)]:
 masks=[]
 for ribindex,out in [(1,-1),(2,1)]:
  face_y=y+out*16
  for station,x,top in [('Spar',356.4,14.),('Rear',410.,10.)]:
   thickness=2.0 if station=='Spar' else 1.5;extent=2.2+thickness
   lo=min(face_y+out*extent,face_y)-.3
   s=Part.makeBox(24.6,extent+.6,top+30.3,A.Vector(x-12.3,lo,-30));masks.append(s)
   o=d.addObject('Part::Feature','Slot_'+side+'_'+station+'_Rib'+str(ribindex));o.Shape=s;context.addObject(o);o.addProperty('App::PropertyString','MassCategory');o.MassCategory='reference only; proposed cutting envelope';o.Visibility=False
 compound=Part.makeCompound(masks)
 for material,suffix,density in [('GFRP','GFRP_Skin_Exposed',1850.),('XPS','Ravatherm_Core_Exposed',32.)]:
  original=w.getObject('Wing_'+side+'_'+suffix).Shape;revised=original.cut(compound);assert revised.isValid()
  removed=original.Volume-revised.Volume;pieces=original.common(compound)
  name='RelievedWingSkin_'+side if material=='GFRP' else 'PocketedCore_'+side
  o=d.getObject(name)
  if o is None:o=d.addObject('Part::Feature',name);context.addObject(o);o.addProperty('App::PropertyString','MassCategory');o.MassCategory='reference only; replacement quantity in aircraft ledger'
  o.Shape=revised;o.Visibility=False
  revisions.append(dict(side=side,original_part='Wing_'+side+'_'+suffix,context_object=name,material=material,density_kg_m3=density,original_volume_mm3=original.Volume,revised_volume_mm3=revised.Volume,removed_volume_mm3=removed,removed_mass_kg=removed*density*1e-9,removed_bounds_mm=[pieces.BoundBox.ZMin,pieces.BoundBox.ZMax],valid=revised.isValid()))
 for suffix in ['GFRP_Skin_Exposed','CFRP_TaperedSpar']:
  q=d.getObject('RelievedWingSkin_'+side).Shape if suffix=='GFRP_Skin_Exposed' else w.getObject('Wing_'+side+'_'+suffix).Shape
  objects=[d.getObject(r['name']) for r in g['added_components'] if r['assembly']=='MotorArm_'+side]
  shapes=[]
  for o in objects:
   s=o.Shape.copy();s.Placement=o.getGlobalPlacement()*o.Placement.inverse()*s.Placement;shapes.append(s)
  c=Part.makeCompound(shapes);v=c.common(q).Volume;gap=c.distToShape(q)[0]
  checks.append(dict(side=side,target=suffix,intersection_mm3=v,min_gap_mm=gap));assert v<1e-4
 print('Relieved skin/core',side,flush=True)
context.Visibility=False;d.recompute();d.save()
g['native_sha256']=hashlib.sha256(native.read_bytes()).hexdigest();g['original_wing_checks']=g.pop('wing_checks');g['wing_checks_after_relief']=checks;g['wing_material_revisions']=revisions;g['wing_slots']=dict(clearance_per_side_mm=.3,slot_x_length_mm=24.6,slot_y_width_mm=dict(Spar=4.8,Rear=4.3),stations_x_mm=[356.4,410.],per_arm=4,total=8,status='Proposed lower-wing entry slots; edge reinforcement/sealing and wing load redistribution unresolved')
(R/'reports/geometry_checks.json').write_text(json.dumps(g,indent=2));print(json.dumps(dict(revisions=revisions,checks=checks),indent=2))
