"""P04 study, not fabrication CAD. Execute with FreeCAD's Python runtime.

Read-only P03 source; new static solids in an independent document. All new
dimensions are engineering assumptions; booleans use saved P03 solids.
"""
import sys,json,hashlib,math
from pathlib import Path
import FreeCAD as A, Part
V=A.Vector
ROOT=Path(__file__).resolve().parents[1]
src=Path(sys.argv[1]);sys.path.insert(0,str(src.parent))
if hashlib.sha256(src.read_bytes()).hexdigest()!='5b4ce6b6f7f8afe0953386b3191f858bde2d42926b18e56e2cbed9a3c0d6caa2':
 raise RuntimeError('Source differs from audited Desktop P03. Re-audit geometry and interfaces before rebuilding.')
old=A.openDocument(str(src));snap=json.loads((ROOT/'data/cad_snapshot.json').read_text())
D=A.newDocument('RescU_P04_Attachment_Study')
parts={};records=[];cuts=[]
for r in snap['structural_parts']:
 o=D.addObject('Part::Feature',r['name']);o.Shape=old.getObject(r['name']).Shape.copy();parts[o.Name]=o
 r=dict(r);r['source']='P03 saved solid copied into P04 study; see native audit';records.append(r)
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def center(shape):return sum((s.CenterOfMass*s.Volume for s in shape.Solids),V())/shape.Volume
def row(o,material,group):
 s=o.Shape;c=center(s);b=s.BoundBox;rho={'GFRP':1850,'CFRP':1600,'Ravatherm XPS X H LB':32,'Epoxy':1200,'Aluminum 6061-T6':2700}[material]
 # Intrinsic inertia omitted here until assembled via solid tensors below.
 I=[[0.]*3 for _ in range(3)]
 for solid in s.Solids:
  mat=solid.MatrixOfInertia;delta=solid.CenterOfMass-c;dv=[delta.x,delta.y,delta.z]
  for i in range(3):
   for j in range(3):I[i][j]+=(getattr(mat,'A'+str(i+1)+str(j+1))+solid.Volume*((sum(t*t for t in dv) if i==j else 0)-dv[i]*dv[j]))*rho*1e-15
 return dict(name=o.Name,material=material,density_kg_m3=rho,volume_mm3=s.Volume,mass_kg=s.Volume*rho*1e-9,x_m=c.x/1000,y_m=c.y/1000,z_m=c.z/1000,bounds_mm=[b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax],valid=s.isValid(),inertia_centroid_kgm2=I,source='P04 candidate solid integral; assumed geometry/density; not manufactured',attachment_group=group)
def add(name,shape,mat,group,replace_foam=False):
 print('Building',name,flush=True)
 # Reserve space in low-density cores; retain all existing skins, tubes and bond.
 for r in records:
  o=parts[r['name']]
  if not o.Shape.BoundBox.intersect(shape.BoundBox):continue
  if replace_foam and r['material']=='Ravatherm XPS X H LB':
   common=o.Shape.common(shape).Volume
   if common>1e-6:
    before=o.Shape.Volume;o.Shape=o.Shape.cut(shape);cuts.append(dict(part=o.Name,removed_mm3=before-o.Shape.Volume,by=name))
  elif r['name'].startswith('VTOL_Arm') or r['name'].startswith('Payload_'):shape=shape.cut(o.Shape)
 # New/new interference is measured in the audit rather than silently erased.
 if shape.Volume<1e-6:raise RuntimeError('Empty new part '+name)
 o=D.addObject('Part::Feature',name);o.Shape=shape
 for typ,key,value in [('App::PropertyBool','StructuralPart',True),('App::PropertyString','Material',mat),('App::PropertyString','DesignStatus','PROVISIONAL; fit/load-path/test closure required'),('App::PropertyString','AttachmentGroup',group)]:o.addProperty(typ,key);setattr(o,key,value)
 o.addProperty('App::PropertyFloat','Density_kg_m3');o.Density_kg_m3={'GFRP':1850,'CFRP':1600,'Ravatherm XPS X H LB':32}[mat]
 additions.append(o);groups[o.Name]=group
 checkpoint=ROOT/'cad';checkpoint.mkdir(exist_ok=True)
 D.saveAs(str(checkpoint/'P04_build_checkpoint.FCStd'))
 return o
additions=[];groups={}
# Lift motor shoes: 40 x 44 x 1.5 upper plates; bonded 1 mm side returns,
# 1 mm lower strap. Motor drilling and bolt installation deferred to vendor pattern.
for side,y in [('R',-265),('L',265)]:
 for end,x in [('F',235),('R',555)]:
  shoe=box(x-20,y-22,0,40,44,1.5)
  for yy in [y-16,y+15]:shoe=shoe.fuse(box(x-15,yy,-21,30,1,21))
  shoe=shoe.fuse(box(x-15,y-16,-21,30,32,1))
  add('MotorShoe_'+side+end,shoe,'GFRP','Lift motor mounts')
# Arm saddles and full-depth local wing ribs: insert plates intersected with the
# exact saved core, plus saddle/bridge below it. No guessed airfoil thickness.
for side,sign in [('PosY',1),('NegY',-1)]:
 y=sign*265;core=old.getObject('Wing_'+side+'_Ravatherm_Core_Exposed').Shape
 for label,x in [('Spar',356.4),('Rear',410.)]:
  cap=box(x-12,y-18,-1,24,36,2)
  for yy in [y-18,y+16]:cap=cap.fuse(box(x-12,yy,-22,24,2,22))
  cap=cap.fuse(box(x-12,y-18,-22,24,36,2))
  # Two chordwise rib webs run from spar region to rear saddle and meet skins.
  if label=='Spar':
   for yy in [y-16,y+14]:cap=cap.fuse(core.common(box(340,yy,1,85,2,29)))
  add('ArmSaddle_'+side+'_'+label,cap,'GFRP','Arm-to-wing attachments',True)
# Bonded permanent wing center box inside the 54 mm battery bank gap.
shape=box(286,-40,-10,39,80,1.5).fuse(box(286,-40,13,39,80,1.5))
for x in [286,323.5]:shape=shape.fuse(box(x,-40,-8.5,1.5,80,21.5))
add('WingCenterBox',shape,'CFRP','Wing center and half-wing joints')
for sign in [-1,1]:
 add('WingCenterSideWeb_'+str(sign),box(300,38 if sign>0 else -46,-8.5,40,8,21.5),'GFRP','Wing center and half-wing joints')
# Root cap/skin transfer strips: conform to the existing core surfaces; remove
# displaced foam exactly. These are local reinforcement, not extra full skins.
for side,sign in [('PosY',1),('NegY',-1)]:
 core=old.getObject('Wing_'+side+'_Ravatherm_Core_Exposed').Shape
 lower=core.copy();lower.translate(V(0,0,-1.0))
 upper=core.copy();upper.translate(V(0,0,1.0))
 layer=core.cut(lower).fuse(core.cut(upper))
 mask=box(295,40 if sign>0 else -140,-10,70,100,40)
 add('WingRootCaps_'+side,layer.common(mask),'CFRP','Wing center and half-wing joints',True)
 # Two chordwise shear ribs at fuselage exit, coupled to spar and inner skins.
 for yy in ([44,54] if sign>0 else [-56,-46]):
  add('WingRootRib_'+side+'_'+str(abs(yy)),core.common(box(280,yy,-8,100,2,35)),'GFRP','Wing center and half-wing joints',True)
# Interior shell contours directly from P03 solid; avoid assumed fuselage radius.
outer=old.getObject('Fuselage_Outer_Mold_Line').Shape
shell=old.getObject('Fuselage_GFRP_Shell_0330').Shape
inside=outer.cut(shell)
def ring(x,length,inner_r):return inside.common(Part.makeCylinder(60,length,V(x,0,0),V(1,0,0))).cut(Part.makeCylinder(inner_r,length,V(x,0,0),V(1,0,0)))
for x in [280,326]:add('WingFrame_'+str(x),ring(x,2,32),'GFRP','Fuselage hardpoints and foam')
for x in [280,321]:add('WingLocalFoam_'+str(x),ring(x,12,36),'Ravatherm XPS X H LB','Fuselage hardpoints and foam')
# Pusher: 2 mm firewall plus 4 longitudinal glass ties over 65 mm to a forward
# frame; tail shell remains the aft load path (no unmodeled spine credited).
add('PusherFirewall',inside.common(box(1107,-40,-40,2,80,80)),'GFRP','Pusher support')
add('PusherForwardFrame',ring(1040,2,19),'GFRP','Pusher support')
for yy,zz in [(-20,0),(20,0),(0,-20),(0,20)]:
 add('PusherTie_'+str(yy)+'_'+str(zz),inside.common(box(1042,yy-4,zz-1,65,8,2)),'GFRP','Pusher support')
# V-tail root inner laminate doublers and full-depth root inserts, each cut to
# exact core. Their angular geometry follows the saved 35 degree P03 tail.
for side in ['PosY','NegY']:
 core=old.getObject('VTail_'+side+'_Ravatherm_Core_Exposed').Shape
 sign=1 if side=='PosY' else -1
 mask=box(965,15 if sign>0 else -65,0,95,50,50)
 # 0.8 mm top/bottom layer along tail normal, using translated core difference.
 off=V(0,-sign*math.sin(math.radians(35))*.8,math.cos(math.radians(35))*.8)
 a=core.copy();a.translate(off);b=core.copy();b.translate(-off)
 add('TailRootLaminates_'+side,core.cut(a).fuse(core.cut(b)).common(mask),'GFRP','V-tail attachments',True)
add('TailFrameFront',ring(969,2,22),'GFRP','V-tail attachments')
add('TailFrameRear',ring(1020,2,19),'GFRP','V-tail attachments')
for x in [969,1014]:add('TailLocalFoam_'+str(x),ring(x,10,20),'Ravatherm XPS X H LB','Fuselage hardpoints and foam')
# Two independent battery trays below the existing packaging envelope. Straps,
# pads and hardware are explicit non-CAD allowances in the analysis inputs.
for label,x in [('Front',198.7),('Rear',323.7)]:
 tray=box(x,-35.5,-26.2,77,71,1)
 for xx in [x,x+76]:tray=tray.fuse(box(xx,-35.5,-25.2,1,71,6))
 add('BatteryTray_'+label,tray,'GFRP','Battery retention')
 for xx in [x+8,x+63]:
  add('BatteryCradle_'+label+'_'+str(int(xx)),inside.common(box(xx,-42,-40,3,84,14)),'GFRP','Battery retention')
for r in records:
 o=parts[r['name']];r.update(row(o,r['material'],'P03 retained structure'))
 r['source']='P03 retained solid; foam subtraction recorded where applicable'
newrows=[row(o,o.Material,groups[o.Name]) for o in additions]
# Equipment/reference geometry retained as reference only; excluded from mass.
for original in old.Objects:
 if hasattr(original,'Shape') and not original.Shape.isNull() and any(t in original.Name for t in ['Cell_','Packaging_Allowance','AXIS_ONLY','SWEPT_DISK','PROPOSED_BODY','SPACE_RESERVE']):
  o=D.addObject('Part::Feature','REF_'+original.Name);o.Shape=original.Shape.copy()
  o.addProperty('App::PropertyBool','StructuralPart');o.StructuralPart=False
D.recompute()
out=ROOT/'cad';out.mkdir(exist_ok=True)
native=out/'RescU_P04_Attachment_Study.FCStd';D.saveAs(str(native))
Part.export([*parts.values(),*additions],str(out/'RescU_P04_Structure.step'))
snapshot=dict(snap);snapshot.update(source_file=native.name,source_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),structural_parts=records+newrows,method='FreeCAD native P04 study, saved and reopened; assumed candidate construction; base P03 retained',shape_hashes={},unmodeled_fuselage_xps_kg=None)
(ROOT/'data/cad_snapshot_p04.json').write_text(json.dumps(snapshot,indent=2))
report=dict(source_file=str(src),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),new_parts=newrows,foam_cuts=cuts,status='CANDIDATE; interfaces and equipment clearances audited separately',new_native=str(native))
(ROOT/'reports/native-audit/build.json').write_text(json.dumps(report,indent=2))
A.closeDocument(D.Name);A.closeDocument(old.Name)
reopened=A.openDocument(str(native));assert all(o.Shape.isValid() for o in reopened.Objects if hasattr(o,'Shape') and not o.Shape.isNull())
print('Native reopen valid; new solids',len(newrows),'new mass g',sum(r['mass_kg'] for r in newrows)*1000)
A.closeDocument(reopened.Name)
