"""P06 rib-to-saddle splice study. FreeCAD1.1 Python; P05/P04 read only.

Adds flat external splice plates, alignment packers and explicit bondlines.
Uses exact saved rib faces and filled native spar for profile/clearance checks.
"""
import sys,json,hashlib,itertools
from pathlib import Path
import FreeCAD as A,Part,Assembly
sys.path.append(str(Path(A.getHomePath())/'Mod/Assembly'))
import JointObject
V=A.Vector;R=Path(__file__).resolve().parents[1];P=R.parent/'motor-arm-p05';W=(R.parent/'v4-attachments' if (R.parent/'v4-attachments').exists() else R.parent)
src=P/'cad/RescU_P05_Motor_Arm_Assembly.FCStd';p05=json.loads((P/'reports/assembly_checks.json').read_text())
assert hashlib.sha256(src.read_bytes()).hexdigest()==p05['native_sha256']
d=A.openDocument(str(src));d.Label='RescU P06 | Rib-saddle bonded splice study';d.MotorArmPair.Label='P06 | Motor-arm pair | bonded rib-saddle splice candidate'
assert hashlib.sha256((W/'cad/RescU_P04_Attachment_Study.FCStd').read_bytes()).hexdigest()=='d006f41b80dfd97d7eaf982ae1475e8acdadeca3b1699967dcd34d0410118ff0'
w=A.openDocument(str(W/'cad/RescU_P04_Attachment_Study.FCStd'))
records=[];interfaces=[];guards={};physical={};rho={'GFRP':1850.,'Epoxy':1200.}
def box(x,y,z,l,b,h):return Part.makeBox(l,b,h,V(x,y,z))
def gs(o):
 s=o.Shape.copy();s.Placement=o.getGlobalPlacement()*o.Placement.inverse()*s.Placement;return s
def center(s):return sum((q.CenterOfMass*q.Volume for q in s.Solids),V())/s.Volume
def prop(o,name,val,typ='App::PropertyString'):
 if name not in o.PropertiesList:o.addProperty(typ,name,'P06 connection')
 setattr(o,name,val)
def fixed(jg,parent,child):
 j=jg.newObject('App::FeaturePython','Fix_'+child.Name);JointObject.Joint(j,0);j.Detach1=True;j.Detach2=True;j.Reference1=(parent,['','']);j.Reference2=(child,['','']);j.Placement1=parent.Placement.inverse()*child.Placement;j.Placement2=A.Placement();j.Label='Fixed | '+child.Name
 return j
def add(asm,jg,name,s,mat,parent):
 if not s.isValid() or s.Volume<1e-5 or len(s.Solids)!=1:raise RuntimeError('Invalid/empty/disconnected new piece '+name+': '+str(len(s.Solids)))
 o=asm.newObject('Part::Feature',name);o.Shape=s;o.Placement=A.Placement(V(0,-asm.Placement.Base.y,0),A.Rotation())*s.Placement
 for key,value in [('Material',mat),('MassCategory','structure'),('Evidence','P06 proposed splice dimensions; exact native rib profile/spar relief; assumed density'),('DesignStatus','REVIEW CANDIDATE; peel, fatigue and process qualification open')]:prop(o,key,value)
 prop(o,'AccountedMass_kg',s.Volume*rho[mat]*1e-9,'App::PropertyFloat');fixed(jg,parent,o)
 physical[name]=gs(o);c=center(physical[name]);records.append(dict(name=name,material=mat,category='structure',assembly=asm.Name,volume_mm3=s.Volume,mass_kg=s.Volume*rho[mat]*1e-9,density_kg_m3=rho[mat],centroid_mm=[c.x,c.y,c.z],valid=s.isValid(),solid_count=len(s.Solids)))
 return o

def add_set(asm,jg,name,s,mat,parent):
 solids=s.Solids
 if not solids:raise RuntimeError('Empty component set '+name)
 return [add(asm,jg,name+('_Piece'+str(i+1) if len(solids)>1 else ''),q,mat,parent) for i,q in enumerate(solids)]
def compound(items):return Part.makeCompound([gs(o) for o in items])

def extruded_band(face,outward,a,b):
 s=face.copy();s.translate(V(0,outward*a,0));return s.extrude(V(0,outward*(b-a),0))
# Native conical outside face plus filled end faces defines the exact outer spar.
for side in ['PosY','NegY']:
 s=w.getObject('Wing_'+side+'_CFRP_TaperedSpar').Shape
 outer=max((f for f in s.Faces if type(f.Surface).__name__=='Cone'),key=lambda f:f.Area)
 solid=Part.makeSolid(Part.makeShell([outer]+[Part.Face(f.OuterWire) for f in s.Faces if type(f.Surface).__name__=='Plane']))
 solid.fix(1e-7,1e-7,1e-7);assert solid.isValid() and solid.Volume>0
 guards[side]=solid.makeOffsetShape(.4,1e-5);assert guards[side].isValid()
for side,yy in [('PosY',265.),('NegY',-265.)]:
 asm=d.getObject('MotorArm_'+side);jg=d.getObject('Joints_'+side)
 for ribindex,out in [(1,-1),(2,1)]:
  rib=d.getObject('Wing_Spar_Rib'+str(ribindex)+'_'+side);ribshape=gs(rib)
  candidates=[f for f in ribshape.Faces if type(f.Surface).__name__=='Plane' and abs(f.normalAt(0,0).y-out)<1e-6]
  face=max(candidates,key=lambda f:f.Area);yf=face.CenterOfMass.y
  # Shift the section down0.3 mm for an upper-edge installation margin.
  # Full native spar+0.4mm also trims every new part, including adhesive.
  profile=face.copy();profile.translate(V(0,0,-.3))
  for label,station in [('Spar',356.4),('Rear',410.)]:
   tag=side+'_'+label+'_Rib'+str(ribindex);saddle=d.getObject('Wing_'+label+'_Saddle_'+side)
   x=station-12;top=14. if label=='Spar' else 10.;uppermask=box(x,yy-25,1.2,24,50,top-1.2)
   def upper(a,b):return extruded_band(profile,out,a,b).common(uppermask).cut(guards[side]).removeSplitter()
   pad=upper(.2,2.0)
   ribbond=upper(0,.2)
   upperbond=upper(2.0,2.2)
   thickness=2.0 if label=='Spar' else 1.5
   ymin=min(yf+out*2.2,yf+out*(2.2+thickness))
   strap=box(x,ymin,-18,24,thickness,top+18).cut(guards[side]).removeSplitter()
   lowerbond=box(x,min(yf+out*2.,yf+out*2.2),-18,24,.2,19.).cut(guards[side]).removeSplitter()
   plate=add(asm,jg,'SplicePlate_'+tag,strap,'GFRP',saddle)
   packers=add_set(asm,jg,'RibPacker_'+tag,pad,'GFRP',plate)
   rb=add_set(asm,jg,'RibPackerBond_'+tag,ribbond,'Epoxy',plate)
   ub=add_set(asm,jg,'PackerSpliceBond_'+tag,upperbond,'Epoxy',plate)
   lb=add_set(asm,jg,'SaddleSpliceBond_'+tag,lowerbond,'Epoxy',plate)
   # Actual geometric contact at each adhesive boundary, not an assumed full rectangle.
   for bond,aa,bb in [(rb,[rib],packers),(ub,packers,[plate]),(lb,[saddle],[plate])]:
    sh=compound(bond);contacts=[]
    for neighbor in [aa,bb]:
     q=sh.common(compound(neighbor));contacts.append(dict(parts=[o.Name for o in neighbor],area_mm2=q.Area,gap_mm=sh.distToShape(compound(neighbor))[0]))
    interfaces.append(dict(bond_parts=[o.Name for o in bond],station=label,side=side,rib_index=ribindex,thickness_mm=.2,mean_projected_area_mm2=sh.Volume/.2,contacts=contacts))
   # Constraint spanning tree: one fixed connection per moving piece. Physical
   # rear bonds form a closed load path without redundant fixed-joint loops.
   if label=='Spar':
    j=d.getObject('Fix_'+rib.Name);j.Reference1=(plate,['','']);j.Reference2=(rib,['','']);j.Detach1=True;j.Detach2=True;j.Placement1=plate.Placement.inverse()*rib.Placement;j.Placement2=A.Placement()
   print('Added',tag,'rib-bond area',round(ribbond.Volume/.2,2),flush=True)
 d.recompute();assert asm.solve()==0
# Internal new/new and new/existing solid overlap checks.
existing=[d.getObject(r['name']) for r in p05['components']];collisions=[]
for i,(name,s) in enumerate(physical.items()):
 for other in existing+list(physical)[:i]:
  oname=other if isinstance(other,str) else other.Name;q=physical[oname] if isinstance(other,str) else gs(other)
  if not s.BoundBox.intersect(q.BoundBox):continue
  vol=s.common(q).Volume
  if vol>1e-4:collisions.append(dict(new=name,other=oname,volume_mm3=vol))
# Compare every new shape with the actual P04 skin and spar. Foam volume is
# intentional pocketing, explicitly deducted once from a revised core copy.
wing_checks=[];pockets=[];context=d.addObject('App::DocumentObjectGroup','WingPocketContext');context.Label='Revised foam cores | context, excluded from arm-only BOM'
for side in ['PosY','NegY']:
 names=[r['name'] for r in records if r['assembly']=='MotorArm_'+side];compound=Part.makeCompound([physical[n] for n in names]);core=w.getObject('Wing_'+side+'_Ravatherm_Core_Exposed').Shape
 pocket=core.common(compound);revised=core.cut(compound);assert revised.isValid()
 removed=core.Volume-revised.Volume
 obj=d.addObject('Part::Feature','PocketedCore_'+side);obj.Shape=revised;context.addObject(obj);prop(obj,'MassCategory','reference only; counted through foam deduction in aircraft ledger')
 pockets.append(dict(side=side,removed_volume_mm3=removed,removed_mass_kg=removed*32e-9,revised_core_volume_mm3=revised.Volume,valid=revised.isValid()))
 for label in ['GFRP_Skin_Exposed','CFRP_TaperedSpar']:
  q=w.getObject('Wing_'+side+'_'+label).Shape;v=compound.common(q).Volume;wing_checks.append(dict(side=side,target=label,intersection_mm3=v,min_gap_mm=compound.distToShape(q)[0]))
 print('Foam pocket',side,round(removed,3),flush=True)
context.Visibility=False
rootcode=d.MotorArmPair.solve();assert rootcode==0
for o in context.Group:o.Visibility=False
native=R/'cad/RescU_P06_Rib_Saddle_Assembly.FCStd';d.recompute();d.saveAs(str(native))
# Flatten parent placements before STEP export, as established in P05.
objects=existing+[d.getObject(r['name']) for r in records];ed=A.newDocument('P06_STEP');export=[];native_solids=[]
for o in objects:
 s=gs(o);e=ed.addObject('Part::Feature',o.Name);e.Shape=s;export.append(e);native_solids+=s.Solids
step=R/'cad/RescU_P06_Arm_Pair.step';ed.recompute();Part.export(export,str(step));q=Part.Shape();q.read(str(step))
pending=[(s.Volume,s.CenterOfMass) for s in q.Solids];errors=[]
for s in native_solids:
 v=s.Volume;c=s.CenterOfMass;b=min(pending,key=lambda x:(x[1]-c).Length+abs(x[0]-v)/max(v,1));pending.remove(b);errors.append(dict(center_error_mm=(b[1]-c).Length,relative_volume_error=abs(b[0]-v)/max(v,1)))
stepcheck=dict(valid=q.isValid(),native_solids=len(native_solids),step_solids=len(q.Solids),max_center_error_mm=max(x['center_error_mm'] for x in errors),max_relative_volume_error=max(x['relative_volume_error'] for x in errors))
stepcheck['pass']=q.isValid() and not pending and stepcheck['max_center_error_mm']<.001 and stepcheck['max_relative_volume_error']<.001
report=dict(version='P06 rib-saddle bonded splice study',source_P05_sha256=p05['native_sha256'],native_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),STEP_sha256=hashlib.sha256(step.read_bytes()).hexdigest(),added_components=records,bond_interfaces=interfaces,physical_collisions=collisions,wing_checks=wing_checks,foam_pockets=pockets,STEP=stepcheck,root_solve_code=int(rootcode),design=dict(splice_plate_thickness_mm=dict(Spar=2.0,Rear=1.5),lap_length_x_mm=24,lower_lap_z_mm=[-18,1],upper_lap_z_limit_mm=dict(Spar=[1.2,14],Rear=[1.2,10]),rib_packer_thickness_mm=1.8,bondline_thickness_mm=.2,spar_outer_surface_clearance_mm=.4,upper_profile_downshift_mm=.3,source='Native P05 rib faces; P04 conical spar outer surface filled and offset. All new dimensions/materials/load sharing remain proposals.'),scope='Rib-to-saddle geometry developed; rib-to-spar/skin transfer and joint qualification remain open.')
(R/'reports/geometry_checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(added=len(records),collisions=len(collisions),wing_checks=wing_checks,STEP=stepcheck),indent=2))
