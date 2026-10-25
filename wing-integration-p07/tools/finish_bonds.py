"""Complete radial bedding after inherited carrier reliefs have been cut.
Also omit sub0.1 mm3 Boolean islands from manufacturing regions, recording them.
"""
import json,sys,hashlib
from pathlib import Path
import FreeCAD as A,Part,Assembly
sys.path.append(str(Path(A.getHomePath())/'Mod/Assembly'));import JointObject
R=Path(__file__).resolve().parents[1];B=R.parent;W=B/'v4-attachments' if (B/'v4-attachments').exists() else B
g=json.loads((R/'reports/build.json').read_text());d=A.openDocument(str(R/'cad/RescU_P07_Wing_Arm_Integration.FCStd'))
w=A.openDocument(str(W/'cad/RescU_P04_Attachment_Study.FCStd'))
source=A.openDocument(str(B/'rib-saddle-p06/cad/RescU_P06_Rib_Saddle_Assembly.FCStd'))
def gs(o):
 q=o.Shape.copy();q.Placement=o.getGlobalPlacement()*o.Placement.inverse()*q.Placement;return q
def remove(row):
 name=row['name'];joint=d.getObject('Fix_'+name)
 if joint:d.removeObject(joint.Name)
 d.removeObject(name);g['new_components'].remove(row)
 for ns in g['wing_parts'].values():
  if name in ns:ns.remove(name)
omitted=[]
for row in list(g['new_components']):
 if row['name'].startswith('SparToRibBond_') or (row['role']!='replacement' and gs(d.getObject(row['name'])).Volume<.1):
  omitted.append(dict(name=row['name'],volume_mm3=gs(d.getObject(row['name'])).Volume,reason='Radial bedding regenerated' if row['name'].startswith('SparToRibBond_') else 'Sub0.1 mm3 Boolean island omitted; not a manufacturable separate region'))
  remove(row)
for side,y in [('PosY',265.),('NegY',-265.)]:
 sp=w.getObject('Wing_'+side+'_CFRP_TaperedSpar').Shape
 face=max((f for f in sp.Faces if type(f.Surface).__name__=='Cone'),key=lambda f:f.Area)
 out=Part.makeSolid(Part.makeShell([face]+[Part.Face(f.OuterWire) for f in sp.Faces if type(f.Surface).__name__=='Plane']))
 out.fix(1e-7,1e-7,1e-7);surface=face.Surface
 axis=surface.Axis;vertical=A.Vector(0,0,1)-axis*axis.z;vertical.normalize();across=axis.cross(vertical);across.normalize()
 m=A.Matrix();m.A11=across.x;m.A21=across.y;m.A31=across.z;m.A12=axis.x;m.A22=axis.y;m.A32=axis.z;m.A13=vertical.x;m.A23=vertical.y;m.A33=vertical.z
 ctr=surface.Center+axis*((y-surface.Center.y)/axis.y)
 clip=Part.makeBox(40,160,6.4,A.Vector(-20,-80,-3.2));clip.Placement=A.Placement(ctr,A.Rotation(m))
 annulus=out.makeOffsetShape(1.,1e-5).cut(out.makeOffsetShape(.8,1e-5)).common(clip)
 for ri in [1,2]:
  yy=gs(source.getObject('Wing_Spar_Rib'+str(ri)+'_'+side)).CenterOfMass.y
  band=Part.makeBox(100,5.2,40,A.Vector(330,yy-2.6,-10));q=annulus.common(band)
  for i,s in enumerate(q.Solids,1):
   assert s.isValid();asm=d.getObject('MotorArm_'+side);jg=d.getObject('Joints_'+side);n='SparToRibBond_'+side+'_Rib'+str(ri)+'_Sector'+str(i)
   o=asm.newObject('Part::Feature',n);o.Shape=s;o.Placement=asm.getGlobalPlacement().inverse()*s.Placement
   o.addProperty('App::PropertyString','Material');o.Material='Epoxy'
   parent=d.getObject('CFRP_Arm_'+side);j=jg.newObject('App::FeaturePython','Fix_'+n);JointObject.Joint(j,0);j.Detach1=True;j.Detach2=True;j.Reference1=(parent,['','']);j.Reference2=(o,['','']);j.Placement1=parent.Placement.inverse()*o.Placement;j.Placement2=A.Placement()
   g['new_components'].append(dict(name=n,side=side,material='Epoxy',role='physical',volume_mm3=s.Volume,mass_kg=s.Volume*1200e-9,solid_count=1,valid=True));g['wing_parts'][side].append(n)
 d.recompute();assert d.getObject('MotorArm_'+side).solve()==0
g['omitted_or_replaced_islands']=omitted;d.save();g['native_sha256']=hashlib.sha256(Path(d.FileName).read_bytes()).hexdigest()
(R/'reports/build.json').write_text(json.dumps(g,indent=2));print('Finished radial bedding and island cleanup')
