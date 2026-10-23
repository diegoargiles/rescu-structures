"""P05 motor-arm review assembly. FreeCAD 1.1 Python; no GUI required.

Native Assembly joints, independent physical pieces, nominal motor interface.
P04 is read-only. Hardware and new construction dimensions remain proposals.
"""
import sys, json, math, hashlib, itertools
from pathlib import Path
import FreeCAD as A, Part, Assembly
sys.path.append(str(Path(A.getHomePath())/'Mod/Assembly'))
import JointObject
V=A.Vector
R=Path(__file__).resolve().parents[1]
P04=R/'baseline-p04' if (R/'baseline-p04').exists() else R.parent if (R.parent/'RescU_Structures_V4.py').exists() else R.parent/'v4-attachments'
source=P04/'cad/RescU_P04_Attachment_Study.FCStd'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='d006f41b80dfd97d7eaf982ae1475e8acdadeca3b1699967dcd34d0410118ff0'
old=A.openDocument(str(source));d=A.newDocument('RescU_P05_Motor_Arm_Assembly')
root=d.addObject('Assembly::AssemblyObject','MotorArmPair');root.Type='Assembly';root.Label='P05 | Motor-arm pair | REVIEW CANDIDATE'
rootj=root.newObject('Assembly::JointGroup','PairJoints')
refs=d.addObject('App::DocumentObjectGroup','ClearanceGauges');refs.Label='Reference envelopes | no added mass'
rows=[];mates=[];parts={};assemblies=[];shapes={};tests=[]
rho={'GFRP':1850.,'CFRP':1600.,'Epoxy':1200.,'Isolation liner':1200.,'Steel':7850.}
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def cyl(r,h,x=0,y=0,z=0):return Part.makeCylinder(r,h,V(x,y,z))
def roundrect(l,w,r,z,h):
 s=box(-l/2+r,-w/2,z,l-2*r,w,h).fuse(box(-l/2,-w/2+r,z,l,w-2*r,h))
 for x in [-l/2+r,l/2-r]:
  for y in [-w/2+r,w/2-r]:s=s.fuse(cyl(r,h,x,y,z))
 return s.removeSplitter()
def holes(s,points,r,z,h):
 for x,y in points:s=s.cut(cyl(r,h,x,y,z))
 return s.removeSplitter()
def prop(o,key,value,typ='App::PropertyString'):
 if key not in o.PropertiesList:o.addProperty(typ,key,'P05 evidence')
 setattr(o,key,value)
def global_shape(o):
 s=o.Shape.copy();s.Placement=o.getGlobalPlacement()*o.Placement.inverse()*s.Placement
 return s
def fixed(asm,jg,parent,child,label):
 j=jg.newObject('App::FeaturePython','Fix_'+child.Name);JointObject.Joint(j,0)
 j.Detach1=True;j.Detach2=True;j.Reference1=(parent,['','']);j.Reference2=(child,['',''])
 j.Placement1=parent.Placement.inverse()*child.Placement;j.Placement2=A.Placement();j.Label=label
 mates.append(dict(name=j.Name,parent=parent.Name,child=child.Name,type='Fixed',connector_basis='Explicit nominal component datums; detached from generated face numbering'))
 return j
def add(asm,jg,name,shape,material,x=0,y=0,z=0,mass=None,category='structure',basis='Proposed dimensions and assumed density',parent=None):
 o=asm.newObject('Part::Feature',name);o.Shape=shape;o.Placement=A.Placement(V(x,y,z),A.Rotation())*shape.Placement
 prop(o,'Material',material);prop(o,'Evidence',basis);prop(o,'MassCategory',category)
 prop(o,'DesignStatus','REVIEW CANDIDATE; no manufacturing release')
 m=shape.Volume*rho.get(material,0)*1e-9 if mass is None else mass
 prop(o,'AccountedMass_kg',m,'App::PropertyFloat');prop(o,'MassMethod','solid volume x assumed density' if mass is None else 'assigned budget / supplied motor mass; envelope volume not used')
 parts[name]=o;rows.append(dict(name=name,assembly=asm.Name,material=material,category=category,mass_kg=m,volume_mm3=shape.Volume,valid=shape.isValid(),solid_count=len(shape.Solids),basis=basis))
 if parent is not None:fixed(asm,jg,parent,o,'Fixed | '+name)
 return o
def gauge(name,shape,label):
 o=d.addObject('Part::Feature',name);o.Shape=shape;refs.addObject(o);o.Label=label
 prop(o,'MassCategory','reference only');return o
pitch=19.;a=pitch/2/math.sqrt(2);motorpoints=[(i*a,j*a) for i in [-1,1] for j in [-1,1]]
# Geometry shared by all four mount stations; dimensions in mm.
top=holes(cyl(22,3,z=8).fuse(box(-10,-30,8,20,60,3)),motorpoints,1.7,7.9,3.2)
top=holes(top,[(0,-24),(0,24)],1.7,7.9,3.2).cut(cyl(5,3.2,z=7.9)).removeSplitter()
lower=holes(roundrect(24,60,3,-24.2,4),[(0,-24),(0,24)],1.7,-24.3,4.2)
motor=cyl(12.75,3).fuse(cyl(17.7,17,z=3)).fuse(cyl(2.5,13.5,z=20))
# These are thread MAJOR-diameter engagement gauges, not verified blind bores.
motor=holes(motor,motorpoints,1.5,0,2.5)
body_max=cyl(17.95,17.1,z=14) # max diameter35.9 and body length20.1; face at11.
motor_spec=dict(model='Unusual Machines UM2807 1700KV',mpn='ENT-UMAC-2807-1700',source_url='https://irlock.com/products/unusual-machines-um2807-1700kv-motor',retrieved='2026-10-23',supplied_drawing='references/UM2807_user_supplied_drawing.png',mass_without_wires_g=45.8,mass_with_three_200mm_18AWG_wires_g=52.,diameter_mm=35.4,diameter_tolerance_mm=0.5,body_length_mm=20.,body_length_tolerance_mm=.1,overall_length_mm=33.5,shaft_diameter_mm=5.,shaft_thread='M5 x 0.8',shaft_exposed_thread_length_mm=9.5,mount_pattern='4 x M3 x 0.5 on PCD 19 mm',mount_angle_proposal_deg=45.,base_diameter_mm=25.5,base_thickness_mm=3.,base_geometry_basis='dimensions transcribed from user supplied drawing; simplified envelope',mount_hole_depth_mm=None,max_safe_screw_insertion_mm=None,mount_torque_Nm=None,wire_exit_geometry=None,voltage_max_V=21.,voltage_cells='3S-5S',maximum_current_A=62.,current_duration_s=3.,verified_status='Supplier nominal dimensions + user drawing; not an inspection report')
design=dict(arm_section_mm=[30,20,1],arm_length_mm=350,motor_axis_x_mm=[235,555],arm_y_mm=[265,-265],motor_mount_face_z_mm=11.,prop_seat_assumption_z_mm=35.,top_plate_thickness_mm=3.,top_outline='diameter44 center, 20mm-wide ears to Y +/-30',clamp_hole_xy_mm=[[0,-24],[0,24]],clearance_hole_diameter_mm=3.4,center_relief_diameter_mm=10.,rails_mm=[28,4,7.6],rail_adhesive_thickness_mm=0.2,liner_thickness_mm=0.2,lower_strap_mm=[24,60,4],motor_screw='M3x6 + 0.5mm washer; PROVISIONAL',motor_screw_insertion_mm=2.5,clamp_screw='2 x M3x45 per motor + 0.5mm washers + 4mm locknut envelope',prop_diameter_gauge_mm=254.,prop_gauge_thickness_mm=2.,wire_gauge_diameter_mm=2.2,dimensions_status='New construction, tool and wire envelopes are proposed, not vendor verified.',saddle_status='P04 geometry separated into actual solids; 0.2mm top/bottom bond pockets added. Wing rib/skin/spar transfer remains unresolved.')
fit=[]
for side,yy in [('PosY',265.),('NegY',-265.)]:
 print('Building',side,flush=True)
 asm=root.newObject('Assembly::AssemblyObject','MotorArm_'+side);asm.Type='Assembly';asm.Label='Motor arm '+side+' | fixed installation';asm.Placement.Base=V(0,yy,0)
 jg=asm.newObject('Assembly::JointGroup','Joints_'+side);assemblies.append(asm)
 # Native arm is checked, then represented with its exact simple section locally.
 arm=add(asm,jg,'CFRP_Arm_'+side,box(0,-15,-20,350,30,20).cut(box(-.01,-14,-19,350.02,28,18)),'CFRP',220,basis='P04 native tube: 350x30x20, wall1 mm; independently volume checked')
 assert abs(arm.Shape.Volume-old.getObject('VTOL_Arm_'+side).Shape.Volume)<1e-5
 gr=jg.newObject('App::FeaturePython','Ground_'+side);JointObject.GroundedJoint(gr,arm);gr.Label='Grounded CFRP arm datum'
 # Retain exact P04 saddle/rib shapes; split its disconnected solids into pieces.
 for label,station in [('Spar',356.4),('Rear',410.)]:
  original=old.getObject('ArmSaddle_'+side+'_'+label)
  for k,solid in enumerate(original.Shape.Solids):
   local=solid.copy();local.translate(V(0,-yy,0))
   if k==0:
    pocket=box(station-12,-15,-20.2,24,30,20.4)
    local=local.cut(pocket)
   saddle=add(asm,jg,'Wing_'+label+('_Saddle' if k==0 else '_Rib'+str(k))+'_'+side,local,'GFRP',parent=arm,basis='P04 exact solid, separated; saddle top/bottom cut for proposed 0.2 mm epoxy interface')
   if k==0:
    for z,labelz in [(0,'Top'),(-20.2,'Bottom')]:
     add(asm,jg,'SaddleBond_'+side+'_'+label+'_'+labelz,box(station-12,-15,z,24,30,.2),'Epoxy',parent=arm,basis='Proposed 0.2mm bondline; top/bottom faces only, side gaps unfilled')
 for end,x,wire_sign in [('Front',235.,1),('Rear',555.,-1)]:
  tag=side+'_'+end
  plate=add(asm,jg,'MotorPlate_'+tag,top,'GFRP',x,parent=arm)
  prop(plate,'MountPCD_mm',19.,'App::PropertyLength');prop(plate,'HoleDiameter_mm',3.4,'App::PropertyLength');prop(plate,'PlateThickness_mm',3.,'App::PropertyLength')
  add(asm,jg,'LowerStrap_'+tag,lower,'GFRP',x,parent=plate)
  add(asm,jg,'LowerLiner_'+tag,box(-12,-15,-20.2,24,30,.2),'Isolation liner',x,parent=plate)
  for n,rail_y in enumerate([-15.,11.]):
   add(asm,jg,'Rail_'+tag+'_'+str(n),box(-14,rail_y,.2,28,4,7.6),'GFRP',x,parent=plate)
   add(asm,jg,'TopLiner_'+tag+'_'+str(n),box(-14,rail_y,0,28,4,.2),'Isolation liner',x,parent=plate)
   add(asm,jg,'RailBond_'+tag+'_'+str(n),box(-14,rail_y,7.8,28,4,.2),'Epoxy',x,parent=plate)
  mo=add(asm,jg,'UM2807_'+tag,motor,'Vendor motor',x,z=11.,mass=.052,category='motor with wires',basis='Supplier 52g incl 3x200mm wires; nominal envelope and mounting pattern, no internal geometry',parent=plate)
  prop(mo,'ThreadDepthStatus','UNKNOWN. Modeled 2.5mm engagement gauge is proposed screw insertion, not verified blind-hole depth.')
  prop(mo,'VoltageStatus','3S-5S / 21V maximum per supplied vendor page. Existing 6S aircraft input is incompatible as direct supply.')
  # Four independent motor screws and washers. Threads represented by major diameter.
  for n,(hx,hy) in enumerate(motorpoints):
   washer=cyl(3.5,.5,hx,hy,7.5).cut(cyl(1.6,.5,hx,hy,7.5))
   add(asm,jg,'MotorWasher_'+tag+'_'+str(n),washer,'Steel',x,parent=plate)
   screw=cyl(1.5,6,hx,hy,7.5).fuse(cyl(2.75,3,hx,hy,4.5))
   add(asm,jg,'MotorScrew_'+tag+'_'+str(n),screw,'Steel',x,parent=plate,basis='M3x6 simple major-diameter/head envelope; approximate steel mass, insertion2.5mm unverified safe')
  for n,hy in enumerate([-24.,24.]):
   add(asm,jg,'ClampScrew_'+tag+'_'+str(n),cyl(1.5,45,0,hy,-33.5).fuse(cyl(2.75,3,0,hy,11.5)),'Steel',x,parent=plate,basis='M3x45 simplified envelope, not selected vendor hardware')
   for k,z in enumerate([11.,-24.7]):
    add(asm,jg,'ClampWasher_'+tag+'_'+str(n)+'_'+str(k),cyl(3.5,.5,0,hy,z).cut(cyl(1.6,.5,0,hy,z)),'Steel',x,parent=plate)
   pts=[V(3.175*math.cos(math.pi/3*k),hy+3.175*math.sin(math.pi/3*k),-28.7) for k in range(6)]
   nut=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,4)).cut(cyl(1.5,4,0,hy,-28.7))
   add(asm,jg,'ClampLocknut_'+tag+'_'+str(n),nut,'Steel',x,parent=plate,basis='5.5 AF x4mm locknut simplified all-steel envelope; mass estimate includes lock insert volume as steel')
  disk=cyl(127,2,x,yy,35.).cut(cyl(2.5,2,x,yy,35.));gauge('PropSweep_'+tag,disk,'10 inch prop sweep | assumed seat plane | '+tag)
  mx=body_max.copy();mx.translate(V(x,yy,0));gauge('MaxMotorBell_'+tag,mx,'Maximum diameter bell gauge | '+tag)
  # Provisional routed wire envelopes: no independent mass (included in motor52g).
  for k,wy in enumerate([-3.,0.,3.]):
   pts=[V(x+wire_sign*t,yy+wy,z) for t,z in [(13.,12.5),(26.,12.5),(32.,3.),(110.,3.)]]
   seg=[]
   for p,q in zip(pts,pts[1:]):seg.append(Part.makeCylinder(1.1,(q-p).Length,p,q-p))
   gauge('WireRoute_'+tag+'_'+str(k),Part.makeCompound(seg),'Wire route gauge | exit/bend limits unverified | '+tag)
  # Driver gauges are checked in stages; motor screws deliberately bench-installed.
  for k,(hx,hy) in enumerate(motorpoints):gauge('MotorTool_'+tag+'_'+str(k),cyl(2,50,x+hx,yy+hy,-45.5),'Motor screw driver | bench access only | '+tag)
  for k,hy in enumerate([-24.,24.]):
   gauge('ClampTopTool_'+tag+'_'+str(k),cyl(4,40,x,yy+hy,14.5),'Clamp head driver envelope | '+tag)
   socket=cyl(5,34,x,yy+hy,-58.7).cut(cyl(3.3,34,x,yy+hy,-58.7))
   gauge('ClampNutTool_'+tag+'_'+str(k),socket,'Clamp locknut hollow socket envelope | '+tag)
 d.recompute();solve=asm.solve();print('Solved',side,solve,flush=True)
 tests.append(dict(assembly=asm.Name,solve_code=int(solve),component_count=sum(r['assembly']==asm.Name for r in rows)))
# Root placement constraints make a true installed pair; no second geometry mass.
g=rootj.newObject('App::FeaturePython','Ground_PositiveArm');JointObject.GroundedJoint(g,assemblies[0]);g.Label='Ground positive-Y assembly'
fixed(root,rootj,assemblies[0],assemblies[1],'Fixed pair | 530mm separation')
d.recompute();pairsolve=root.solve();print('Pair solve',pairsolve,flush=True)
for o in parts.values():shapes[o.Name]=global_shape(o)
# Local physical interference only; adjacent intentional touching is allowed.
overlaps=[]
for asm in assemblies:
 names=[r['name'] for r in rows if r['assembly']==asm.Name]
 for na,nb in itertools.combinations(names,2):
  sa,sb=shapes[na],shapes[nb]
  if not sa.BoundBox.intersect(sb.BoundBox):continue
  vol=sa.common(sb).Volume
  if vol>1e-4:
   known=('MotorScrew_' in na and 'UM2807_' in nb) or ('MotorScrew_' in nb and 'UM2807_' in na)
   overlaps.append(dict(a=na,b=nb,volume_mm3=vol,classification='thread engagement envelope' if known else 'REVIEW INTERFERENCE'))
print('Interference pairs',len(overlaps),flush=True)
clearances=[]
for side,yy in [('PosY',265.),('NegY',-265.)]:
 for end,x in [('Front',235.),('Rear',555.)]:
  tag=side+'_'+end;bell=d.getObject('MaxMotorBell_'+tag).Shape;disk=d.getObject('PropSweep_'+tag).Shape
  mountnames=[n for n in shapes if tag in n and not n.startswith(('UM2807','MotorScrew_'))]
  for typ,ss in [('max_bell',bell),('prop_sweep',disk)]:
   # hardware installation clearances to the motor rotating envelope/prop disk.
   minimum=min((ss.distToShape(shapes[n])[0],n) for n in mountnames)
   clearances.append(dict(check=typ+'_to_mount',station=tag,min_distance_mm=minimum[0],nearest=minimum[1]))
  for target in ['Wing_'+side+'_GFRP_Skin_Exposed','Wing_'+side+'_Ravatherm_Core_Exposed','Fuselage_GFRP_Shell_0330']:
   q=old.getObject(target).Shape
   clearances.append(dict(check='prop_to_P04_airframe',station=tag,target=target,min_distance_mm=disk.distToShape(q)[0],intersection_mm3=disk.common(q).Volume))
  # Tool/route collision stages against physical assembly.
  names=[r['name'] for r in rows if r['assembly']=='MotorArm_'+side]
  for prefix in ['ClampTopTool_','ClampNutTool_','WireRoute_','MotorTool_']:
   bad=[]
   for go in [o for o in refs.Group if o.Name.startswith(prefix+tag)]:
    for n in names:
     if prefix=='MotorTool_' and (n.startswith('MotorScrew') or n.startswith('MotorWasher')):continue
     ss=shapes[n]
     if not ss.BoundBox.intersect(go.Shape.BoundBox):continue
     v=ss.common(go.Shape).Volume
     if v>1e-4:bad.append(dict(gauge=go.Name,part=n,overlap_mm3=v))
   clearances.append(dict(check=prefix+'stage',station=tag,collisions=bad,status=('BENCH INSTALLATION REQUIRED' if prefix=='MotorTool_' and bad else 'REVIEW' if bad else 'CLEAR for assumed gauge')))
# Constraint regression: displace one plate, solve, ensure its followers return.
target=parts['MotorPlate_PosY_Front'];before=target.Placement;target.Placement=A.Placement(V(before.Base.x+3,before.Base.y+2,before.Base.z+1),before.Rotation)
recovery=assemblies[0].solve();residual=(target.Placement.Base-before.Base).Length
tests.append(dict(test='Perturb motor plate then solve',solve_code=int(recovery),position_residual_mm=residual))
assert residual<1e-5
for o in refs.Group:o.Visibility=False
d.recompute();native=R/'cad/RescU_P05_Motor_Arm_Assembly.FCStd';d.saveAs(str(native))
# Small assembly STEP; separate from inherited P04 shell transfer problem.
step=R/'cad/RescU_P05_Motor_Arm_Pair.step'
# Part.export on nested component objects drops the assembly parent placement.
# Export independent globally placed copies; validate centers on reimport.
ed=A.newDocument('P05_STEP_Export');export_objects=[]
for name,ss in shapes.items():
 eo=ed.addObject('Part::Feature',name);eo.Shape=ss;export_objects.append(eo)
ed.recompute();Part.export(export_objects,str(step));A.closeDocument(ed.Name)
q=Part.Shape();q.read(str(step))
nv=sum(s.Volume for s in shapes.values());sv=sum(s.Volume for s in q.Solids)
stepcheck=dict(valid=q.isValid(),native_solids=sum(len(s.Solids) for s in shapes.values()),step_solids=len(q.Solids),native_sum_solid_volume_mm3=nv,step_sum_solid_volume_mm3=sv,relative_difference=abs(nv-sv)/nv)
stepcheck['pass']=stepcheck['valid'] and stepcheck['native_solids']==stepcheck['step_solids'] and stepcheck['relative_difference']<1e-5
for rr in rows:
 ss=shapes[rr['name']];c=sum((q.CenterOfMass*q.Volume for q in ss.Solids),V())/ss.Volume;rr['centroid_mm']=[c.x,c.y,c.z]
report=dict(status='REVIEW CANDIDATE',source_P04_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),native_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),step_sha256=hashlib.sha256(step.read_bytes()).hexdigest(),motor=motor_spec,design=design,components=rows,joints=mates,solver_tests=tests,root_solve_code=int(pairsolve),interferences=overlaps,clearances=clearances,STEP=stepcheck,prop_nominal_in_plane_gaps_mm=dict(front_rear=320-254,opposite_sides=530-254),qualification='Fit screens only. Motor thread depth, torque, vendor screw mass, CFRP clamp pressure, actual prop hub, wire exit, bonds and wing attachments unresolved.')
(R/'reports/assembly_checks.json').write_text(json.dumps(report,indent=2));(R/'data/motor_spec.json').write_text(json.dumps(motor_spec,indent=2));(R/'data/design.json').write_text(json.dumps(design,indent=2))
print(json.dumps(dict(parts=len(rows),joints=len(mates),STEP=stepcheck,unresolved_interferences=sum(x['classification']=='REVIEW INTERFERENCE' for x in overlaps)),indent=2))
