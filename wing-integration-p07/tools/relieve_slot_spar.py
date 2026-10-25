"""Relieve slot reinforcement and potting against the actual tapered spar."""
import json,sys,hashlib
from pathlib import Path
import FreeCAD as A,Part,Assembly
sys.path.append(str(Path(A.getHomePath())/'Mod/Assembly'));import JointObject
R=Path(__file__).resolve().parents[1];B=R.parent;W=B/'v4-attachments' if (B/'v4-attachments').exists() else B
g=json.loads((R/'reports/build.json').read_text());d=A.openDocument(str(R/'cad/RescU_P07_Wing_Arm_Integration.FCStd'));w=A.openDocument(str(W/'cad/RescU_P04_Attachment_Study.FCStd'))
def gs(o):
 s=o.Shape.copy();s.Placement=o.getGlobalPlacement()*o.Placement.inverse()*s.Placement;return s
def remove(row):
 n=row['name'];j=d.getObject('Fix_'+n)
 if j:d.removeObject(j.Name)
 d.removeObject(n);g['new_components'].remove(row)
 for ns in g['wing_parts'].values():
  if n in ns:ns.remove(n)
changes=[]
for side in ['PosY','NegY']:
 s=w.getObject('Wing_'+side+'_CFRP_TaperedSpar').Shape
 f=max((f for f in s.Faces if type(f.Surface).__name__=='Cone'),key=lambda f:f.Area)
 outer=Part.makeSolid(Part.makeShell([f]+[Part.Face(f.OuterWire) for f in s.Faces if type(f.Surface).__name__=='Plane']));outer.fix(1e-7,1e-7,1e-7)
 guard=outer.makeOffsetShape(1.,1e-5)
 for row in list(g['new_components']):
  if row['side']!=side or not row['name'].startswith(('SlotSkinBond_','SlotDoubler_','SlotEdgePotting_')):continue
  o=d.getObject(row['name']);before=gs(o);cut=outer if row['name'].startswith('SlotEdgePotting_') else guard
  q=before.cut(cut,1e-5);ss=[p for p in q.Solids if p.Volume>=.1]
  assert all(p.isValid() for p in ss),row['name']
  changes.append(dict(name=row['name'],before_volume_mm3=before.Volume,after_volume_mm3=sum(p.Volume for p in ss),radial_coupler_relief_mm=0. if row['name'].startswith('SlotEdgePotting_') else 1.))
  if not ss:remove(row);continue
  main=max(ss,key=lambda p:p.Volume);o.Shape=main;o.Placement=d.getObject('MotorArm_'+side).getGlobalPlacement().inverse()*main.Placement
  row.update(volume_mm3=main.Volume,mass_kg=main.Volume*(1850 if row['material']=='GFRP' else 1200)*1e-9)
  for i,extra in enumerate([p for p in ss if p is not main],1):
   # TopoShape wrappers are not identity-stable: exclude the main by matching
   # the exact shape identity before adding any disconnected trim pieces.
   if extra.isSame(main):continue
   asm=d.getObject('MotorArm_'+side);name=row['name']+'_SparRelief'+str(i)
   new=asm.newObject('Part::Feature',name);name=new.Name;new.Shape=extra;new.Placement=asm.getGlobalPlacement().inverse()*extra.Placement
   new.addProperty('App::PropertyString','Material');new.Material=row['material']
   parent=d.getObject('CFRP_Arm_'+side);j=d.getObject('Joints_'+side).newObject('App::FeaturePython','Fix_'+name);JointObject.Joint(j,0);j.Detach1=True;j.Detach2=True;j.Reference1=(parent,['','']);j.Reference2=(new,['','']);j.Placement1=parent.Placement.inverse()*new.Placement;j.Placement2=A.Placement()
   rr=dict(row);rr.update(name=name,volume_mm3=extra.Volume,mass_kg=extra.Volume*(1850 if row['material']=='GFRP' else 1200)*1e-9);g['new_components'].append(rr);g['wing_parts'][side].append(name)
 print('Slot/spar relief',side,flush=True)
for j in d.Objects:
 if hasattr(j,'Reference1') and hasattr(j,'Reference2') and j.Reference1 and j.Reference2:
  a,b=j.Reference1[0],j.Reference2[0]
  if a and b:j.Placement1=a.Placement.inverse()*b.Placement;j.Placement2=A.Placement()
d.recompute();assert d.MotorArm_PosY.solve()==0 and d.MotorArm_NegY.solve()==0;d.save()
g['slot_spar_relief']=changes;g['native_sha256']=hashlib.sha256(Path(d.FileName).read_bytes()).hexdigest();(R/'reports/build.json').write_text(json.dumps(g,indent=2))
print('Saved slot/spar correction')
