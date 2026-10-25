"""Trim planar web-face layups to the exact tapered spar and cap boundaries.
The planar templates are manufacturing blanks; this operation defines installed fit.
"""
import json,hashlib,sys
from pathlib import Path
import FreeCAD as A,Part,Assembly
sys.path.append(str(Path(A.getHomePath())/'Mod/Assembly'));import JointObject
R=Path(__file__).resolve().parents[1];B=R.parent;W=B/'v4-attachments' if (B/'v4-attachments').exists() else B
g=json.loads((R/'reports/build.json').read_text());d=A.openDocument(str(R/'cad/RescU_P07_Wing_Arm_Integration.FCStd'))
w=A.openDocument(str(W/'cad/RescU_P04_Attachment_Study.FCStd'))
source=A.openDocument(str(B/'rib-saddle-p06/cad/RescU_P06_Rib_Saddle_Assembly.FCStd'))
def gs(o):
 s=o.Shape.copy();s.Placement=o.getGlobalPlacement()*o.Placement.inverse()*s.Placement;s.tessellate(.3);return s
changes=[]
for side,y in [('PosY',265.),('NegY',-265.)]:
 window=Part.makeBox(90,70,35,A.Vector(338,y-35,-8))
 env=w.getObject('Wing_'+side+'_Ravatherm_Core_Exposed').Shape.common(window)
 for ri in [1,2]:env=env.fuse(gs(source.getObject('Wing_Spar_Rib'+str(ri)+'_'+side)))
 spar=w.getObject('Wing_'+side+'_CFRP_TaperedSpar').Shape
 outerface=max((f for f in spar.Faces if type(f.Surface).__name__=='Cone'),key=lambda f:f.Area)
 outer=Part.makeSolid(Part.makeShell([outerface]+[Part.Face(f.OuterWire) for f in spar.Faces if type(f.Surface).__name__=='Plane']))
 outer.fix(1e-7,1e-7,1e-7);env=env.fuse(outer.common(window)).removeSplitter();env.tessellate(.3)
 guard=outer.makeOffsetShape(1.,1e-5);guard.tessellate(.3)
 upper=env.copy();upper.translate(A.Vector(0,0,-.8));lower=env.copy();lower.translate(A.Vector(0,0,.8))
 for row in list(g['new_components']):
  if row['side']!=side or not row['name'].startswith(('RibFaceTape_','RibFaceBond_')):continue
  o=d.getObject(row['name']);s=gs(o);q=s.cut(guard,1e-5).common(upper,1e-5).common(lower,1e-5).removeSplitter()
  q=Part.makeCompound(q.Solids)
  if not q.isValid():q.fix(1e-6,1e-6,1e-4)
  if not q.isValid() or len(q.Solids)<1:
   changes.append(dict(name=row['name'],before_volume_mm3=s.Volume,after_volume_mm3=s.Volume,status='Exact trim rejected by validity gate; original valid template retained for explicit clash audit'))
   continue
  if len(q.Solids)>1:
   # Kept explicit: each disconnected installed ply region is a separate CAD piece.
   ss=sorted(q.Solids,key=lambda z:z.Volume,reverse=True);q=ss[0]
   for i,extra in enumerate(ss[1:],1):
    asm=d.getObject('MotorArm_'+side);jg=d.getObject('Joints_'+side);n=row['name']+'_TrimPiece'+str(i)
    obj=asm.newObject('Part::Feature',n);obj.Shape=extra;obj.Placement=asm.getGlobalPlacement().inverse()*extra.Placement
    for key,value in [('Material',row['material']),('DesignStatus','Installed ply region; layup/process unqualified')]:obj.addProperty('App::PropertyString',key);setattr(obj,key,value)
    parent=d.getObject('CFRP_Arm_'+side);j=jg.newObject('App::FeaturePython','Fix_'+n);JointObject.Joint(j,0);j.Detach1=True;j.Detach2=True;j.Reference1=(parent,['','']);j.Reference2=(obj,['','']);j.Placement1=parent.Placement.inverse()*obj.Placement;j.Placement2=A.Placement()
    rr=dict(row);rr.update(name=n,volume_mm3=extra.Volume,mass_kg=extra.Volume*(1850 if row['material']=='GFRP' else 1200)*1e-9);g['new_components'].append(rr);g['wing_parts'][side].append(n)
  o.Shape=q;o.Placement=d.getObject('MotorArm_'+side).getGlobalPlacement().inverse()*q.Placement
  changes.append(dict(name=row['name'],before_volume_mm3=s.Volume,after_volume_mm3=q.Volume))
  row.update(volume_mm3=q.Volume,mass_kg=q.Volume*(1850 if row['material']=='GFRP' else 1200)*1e-9)
 print('Trimmed web-face layups',side,flush=True)
for j in d.Objects:
 if hasattr(j,'Reference1') and hasattr(j,'Reference2') and j.Reference1 and j.Reference2:
  a,b=j.Reference1[0],j.Reference2[0]
  if a and b:j.Placement1=a.Placement.inverse()*b.Placement;j.Placement2=A.Placement()
d.recompute();assert d.MotorArm_PosY.solve()==0 and d.MotorArm_NegY.solve()==0;d.save()
g['native_sha256']=hashlib.sha256(Path(d.FileName).read_bytes()).hexdigest();g['installed_layer_trims']=changes
(R/'reports/build.json').write_text(json.dumps(g,indent=2));print('Installed laminate layers refined')
