"""Reopen P07, check fit, export placed STEP parts and update aircraft accounting."""
import sys,json,math,csv,hashlib,zipfile,faulthandler
from pathlib import Path
import FreeCAD as A,Part,Assembly
sys.path.append(str(Path(A.getHomePath())/'Mod/Assembly'));import JointObject
R=Path(__file__).resolve().parents[1];B=R.parent;W=B/'v4-attachments' if (B/'v4-attachments').exists() else B;sys.path.insert(0,str(W))
import RescU_Structures_V4 as engine
faulthandler.dump_traceback_later(120,repeat=True)
g=json.loads((R/'reports/build.json').read_text());d=A.openDocument(str(R/'cad/RescU_P07_Wing_Arm_Integration.FCStd'))
w=A.openDocument(str(W/'cad/RescU_P04_Attachment_Study.FCStd'))
def gs(o):
 s=o.Shape.copy();s.Placement=o.getGlobalPlacement()*o.Placement.inverse()*s.Placement;s.tessellate(.3);return s.Solids[0] if len(s.Solids)==1 else s
def fixed(jg,parent,o):
 j=jg.newObject('App::FeaturePython','Fix_'+o.Name);JointObject.Joint(j,0);j.Detach1=True;j.Detach2=True
 j.Reference1=(parent,['','']);j.Reference2=(o,['','']);j.Placement1=parent.Placement.inverse()*o.Placement;j.Placement2=A.Placement()
def add(side,name,shape,mat,role='replacement'):
 asm=d.getObject('MotorArm_'+side);out=[]
 for i,s in enumerate(shape.Solids):
  if s.Volume<1e-5:continue
  assert s.isValid()
  n=name+('_Piece'+str(i+1) if len(shape.Solids)>1 else '')
  o=asm.newObject('Part::Feature',n);o.Shape=s;o.Placement=asm.getGlobalPlacement().inverse()*s.Placement
  o.addProperty('App::PropertyString','Material');o.Material=mat
  o.addProperty('App::PropertyString','DesignStatus');o.DesignStatus='P07 candidate; no qualified laminate/process allowables'
  fixed(d.getObject('Joints_'+side),d.getObject('CFRP_Arm_'+side),o)
  density=1200 if mat=='Epoxy' else 1850
  row=dict(name=n,side=side,material=mat,role=role,volume_mm3=s.Volume,mass_kg=s.Volume*density*1e-9,valid=True,solid_count=1)
  g['new_components'].append(row);g['wing_parts'][side].append(n);out.append(o)
 return out
if not any(r['name'].startswith('SlotEdgePotting') for r in g['new_components']):
 source=A.openDocument(str(B/'rib-saddle-p06/cad/RescU_P06_Rib_Saddle_Assembly.FCStd'))
 for side,y in [('PosY',265.),('NegY',-265.)]:
  print('Slot edge closure',side,flush=True)
  # Potting lies entirely within the pre-existing rectangular entry slots.
  # The replacement core/skin already excludes those slots; subtracting their
  # entire complex wing BREP again is redundant and extremely expensive.
  physical=[gs(d.getObject(n)) for n in g['old_physical_names'] if side in n]+[gs(d.getObject(row['name'])) for row in g['new_components'] if row['side']==side and row['role']!='replacement']
  sp=w.getObject('Wing_'+side+'_CFRP_TaperedSpar').Shape
  sf=max((f for f in sp.Faces if type(f.Surface).__name__=='Cone'),key=lambda f:f.Area)
  filled=Part.makeSolid(Part.makeShell([sf]+[Part.Face(f.OuterWire) for f in sp.Faces if type(f.Surface).__name__=='Plane']))
  filled.fix(1e-7,1e-7,1e-7)
  for slot in [o for o in d.Objects if o.Name.startswith('Slot_'+side+'_')]:
   bb=slot.Shape.optimalBoundingBox();ri=1 if 'Rib1' in slot.Name else 2
   rib=gs(source.getObject('Wing_Spar_Rib'+str(ri)+'_'+side))
   clip=Part.makeBox(bb.XLength,4,40,A.Vector(bb.XMin,rib.CenterOfMass.y-2,-10))
   z=rib.common(clip).optimalBoundingBox().ZMin
   # Proposed3 mm-high local potting/bead envelope referenced to the native
   # lower rib contour; not a verified cured sealant shape or exact skin offset.
   s=Part.makeBox(bb.XLength,bb.YLength,3.,A.Vector(bb.XMin,bb.YMin,z-.7))
   occ=[q for q in physical if q.optimalBoundingBox().intersect(s.optimalBoundingBox())]
   s=s.cut(Part.makeCompound(occ),1e-5).cut(filled,1e-5)
   if s.Volume>1e-4:add(side,'SlotEdgePotting_'+slot.Name,s,'Epoxy','physical')
 d.recompute();d.save();g['native_sha256']=hashlib.sha256(Path(d.FileName).read_bytes()).hexdigest()
 (R/'reports/build.json').write_text(json.dumps(g,indent=2))
if not any(r['name'].startswith('WingOriginalBond') for r in g['new_components']):
 for side in ['PosY','NegY']:
  q=w.getObject('Wing_'+side+'_EpoxyBond_Exposed').Shape
  for slot in [o for o in d.Objects if o.Name.startswith('Slot_'+side+'_')]:q=q.cut(slot.Shape,1e-5)
  # This is a geometric replacement only: retain the original thin-layer mass
  # budget until its Boolean quantities pass the same conservation audit as foam.
  add(side,'WingOriginalBond_'+side,q,'Epoxy')
 d.recompute();d.save();g['native_sha256']=hashlib.sha256(Path(d.FileName).read_bytes()).hexdigest()
 (R/'reports/build.json').write_text(json.dumps(g,indent=2))
if '--prepare-only' in sys.argv:
 print('Wing context and proposed slot potting prepared');sys.exit(0)
names=g['old_physical_names']+[r['name'] for r in g['new_components']]
assert len(names)==len(set(names))
shapes={n:gs(d.getObject(n)) for n in names};bounds={n:s.optimalBoundingBox() for n,s in shapes.items()}
assert all(s.isValid() and len(s.Solids)==1 for s in shapes.values())
print('Checking',len(names),'placed pieces',flush=True)
newnames=[r['name'] for r in g['new_components'] if r['role']!='replacement']
collisions=[]
wingtargets=[r['name'] for r in g['new_components'] if r['role']=='replacement']
wing_batch_checks=[]
for target in wingtargets:
 side=next(r['side'] for r in g['new_components'] if r['name']==target)
 if target.startswith('WingCore_'):
  wing_batch_checks.append(dict(target=target,method='Constructed web bays, cap channels and spar-cheek pocket; removed-volume conservation passed. Full compound/foam Boolean deferred.',intersection_mm3=None))
  continue
 candidates=[n for n in newnames if side in n and bounds[n].intersect(bounds[target])]
 if target.startswith(('WingSkin_','WingOriginalBond_')):
  candidates=[n for n in candidates if n.startswith(('SkinBond_','SlotEdgePotting_','SparCheek_'))]
 if not candidates:continue
 total=0.
 for n in candidates:
  gap=shapes[n].distToShape(shapes[target])[0]
  vol=0. if gap>1e-4 else shapes[n].common(shapes[target]).Volume
  total+=vol
  if vol>1e-3:collisions.append(dict(part=n,other=target,intersection_mm3=vol))
 wing_batch_checks.append(dict(target=target,new_part_count=len(candidates),method='Individual gap/intersection checks; skin/bond checked at outer bedding interfaces',intersection_mm3=total))
 print('Wing interface check',target,round(total,6),flush=True)
for i,n in enumerate(newnames):
 if i%20==0:print('Fit checks',i,'of',len(newnames),flush=True)
 for other in names:
  if n==other or other in wingtargets or (other in newnames and newnames.index(other)>i):continue
  if not bounds[n].intersect(bounds[other]):continue
  volume=shapes[n].common(shapes[other]).Volume
  if volume>1e-3:collisions.append(dict(part=n,other=other,intersection_mm3=volume))
solver=[]
for side in ['PosY','NegY']:
 asm=d.getObject('MotorArm_'+side);assert asm.solve()==0
 o=d.getObject('Wing_Spar_Rib1_'+side);before=o.Placement
 o.Placement=A.Placement(before.Base+A.Vector(1,2,3),A.Rotation(1,2,3)*before.Rotation)
 code=asm.solve();delta=(o.Placement.Base-before.Base).Length;angle=(o.Placement.Rotation.inverted()*before.Rotation).Angle
 solver.append(dict(side=side,solve_code=int(code),perturbation_translation_residual_mm=delta,rotation_residual_rad=angle))
 assert code==0 and delta<1e-5 and angle<1e-5
assert d.MotorArmPair.solve()==0
print('Collision count',len(collisions),flush=True)
nominal=[];hard=[]
for row in collisions:
 mats=[getattr(d.getObject(row[k]),'Material','') for k in ['part','other']]
 if row['intersection_mm3']<=.02 and 'Epoxy' in mats:nominal.append(row)
 else:hard.append(row)
collisions=hard
gauge_checks=[]
for gauge in d.Objects:
 if not gauge.Name.startswith(('PropSweep_','ClampTopTool_','ClampNutTool_','WireRoute_','MotorTool_')):continue
 s=gs(gauge);bb=s.optimalBoundingBox();bad=[]
 for n in (names if gauge.Name.startswith('WireRoute_') else [r['name'] for r in g['new_components']]):
  if not bb.intersect(bounds[n]):continue
  vol=s.common(shapes[n]).Volume
  if vol>1e-3:bad.append(dict(part=n,intersection_mm3=vol))
 gauge_checks.append(dict(gauge=gauge.Name,new_geometry_collisions=bad,scope='Retained P05 assumed gauge; baseline bench motor-screw installation requirement unchanged'))
(R/'reports/fit_checks.json').write_text(json.dumps(dict(source_native_sha256=g['native_sha256'],collisions=collisions,nominal_wet_bond_intersections=nominal,nominal_wet_bond_overlap_mass_upper_bound_g=sum(q['intersection_mm3'] for q in nominal)*.0012,wing_batch_checks=wing_batch_checks,solver=solver,gauge_checks=gauge_checks,physical_piece_count=len(names)),indent=2))
assert not any(q['new_geometry_collisions'] for q in gauge_checks),'New geometry blocks a retained P05 access/prop gauge'
if collisions:
 print(json.dumps(collisions[:30],indent=2));sys.exit(2)
if '--fit-only' in sys.argv:sys.exit(0)
# Flatten global placements; STEP does not retain native FreeCAD joint definitions.
native_quantities={n:(q.CenterOfMass,q.Volume) for n,q in shapes.items()}
def export(ns,path):
 flat=A.newDocument('P07Export');objs=[]
 for n in ns:
  o=flat.addObject('Part::Feature',n);o.Label=n;o.Shape=shapes[n];objs.append(o)
 Part.export(objs,str(path));A.closeDocument(flat.Name)
 s=Part.Shape();s.read(str(path))
 assert s.isValid() and len(s.Solids)==len(ns),(str(path),len(s.Solids),len(ns))
 matches=[];remaining=[(q,q.CenterOfMass,q.Volume) for q in s.Solids]
 for n in ns:
  original=shapes[n];c,volume=native_quantities[n]
  selected=min(remaining,key=lambda item:(item[1]-c).Length+100*abs(math.log(max(item[2],1e-9)/max(volume,1e-9))));remaining.remove(selected)
  q,centroid,imported_volume=selected
  err=(centroid-c).Length;ve=abs(imported_volume-volume)/max(1,volume)
  reference=n.startswith(('WingSkin_','WingOriginalBond_'))
  assert reference or (err<.002 and ve<.002),(n,err,ve)
  matches.append(dict(name=n,centroid_error_mm=err,relative_volume_error=ve,quantity_pass=err<.002 and ve<.002,retained_thin_shell_reference=reference))
 return dict(file=path.name,solids=len(s.Solids),valid=True,maximum_centroid_error_mm=max(t['centroid_error_mm'] for t in matches),maximum_relative_volume_error=max(t['relative_volume_error'] for t in matches),all_quantities_pass=all(t['quantity_pass'] for t in matches),component_checks=matches,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),scope='Placed separate solids; any thin-shell quantity deviations are reference-only and retain native mass budgeting')
exports=[]
exports.append(export(names,R/'cad/RescU_P07_Wing_Arm_Pair.step'))
review=[n for n in names if getattr(d.getObject(n),'Material','')!='Epoxy']
exports.append(export(review,R/'cad/RescU_P07_SolidWorks_Review.step'))
for side in ['PosY','NegY']:
 ns=[n for n in names if side in n]
 exports.append(export(ns,R/('cad/RescU_P07_'+side+'_Wing_Arm.step')))
 carrier=[n for n in ns if not n.startswith(('WingSkin_','WingCore_','WingSpar_','WingOriginalBond_'))]
 exports.append(export(carrier,R/('cad/RescU_P07_'+side+'_Carrier_Cutaway.step')))
for row in g['new_components']:
 if row['role']!='replacement' and row['material']=='GFRP':
  # World-coordinate placement retained for direct comparison with assembly imports.
  exports.append(export([row['name']],R/('cad/parts/'+row['name']+'.step')))
(R/'reports/step_validation.json').write_text(json.dumps(exports,indent=2))
print('Validated STEP exports',len(exports),flush=True)
# Replace original quantities once. Skins retain the previous accepted mass;
# their native Boolean quantity-conservation issue has not been repaired here.
before=json.loads((B/'rib-saddle-p06/reports/results.json').read_text())
c=json.loads((B/'rib-saddle-p06/data/inputs_p06.json').read_text())
s=json.loads((B/'rib-saddle-p06/data/accounting_snapshot_p06.json').read_text())
def integral(name,q,material,density,source):
 ctr=sum((a.CenterOfMass*a.Volume for a in q.Solids),A.Vector())/q.Volume;I=[[0.]*3 for _ in range(3)]
 for a in q.Solids:
  mat=a.MatrixOfInertia;dv=a.CenterOfMass-ctr;v=[dv.x,dv.y,dv.z]
  for i in range(3):
   for j in range(3):I[i][j]+=(getattr(mat,'A'+str(i+1)+str(j+1))+a.Volume*((sum(z*z for z in v) if i==j else 0)-v[i]*v[j]))*density*1e-15
 return dict(name=name,material=material,density_kg_m3=density,volume_mm3=q.Volume,mass_kg=q.Volume*density*1e-9,x_m=ctr.x/1000,y_m=ctr.y/1000,z_m=ctr.z/1000,inertia_centroid_kgm2=I,valid=q.isValid(),source=source)
replacements=[];removed_by_material={};added_by_material={}
for m in g['modified_components']:
 old=next(row for row in s['structural_parts'] if row['name']==m['name'])
 new=integral(old['name'],shapes[old['name']],old['material'],old['density_kg_m3'],'P07 revised native carrier geometry; replaces P06 once')
 removed_by_material[old['material']]=removed_by_material.get(old['material'],0)+old['mass_kg']-new['mass_kg']
 s['structural_parts'][s['structural_parts'].index(old)]=new;replacements.append(dict(name=old['name'],before_mass_kg=old['mass_kg'],after_mass_kg=new['mass_kg']))
for side in ['PosY','NegY']:
 old=next(row for row in s['structural_parts'] if row['name']=='Wing_'+side+'_Ravatherm_Core_Exposed')
 ns=[row['name'] for row in g['new_components'] if row['name'].startswith('WingCore_'+side)]
 q=Part.makeCompound([shapes[n] for n in ns]);new=integral(old['name'],q,old['material'],old['density_kg_m3'],'P07 pocketed core; skin credit remains zero')
 diag=next(q for q in g['diagnostics'] if q['side']==side)
 # No foam credit if the geometry quantity audit fails.
 if diag['foam_credit_pass']:
  removed_by_material['XPS']=removed_by_material.get('XPS',0)+old['mass_kg']-new['mass_kg']
  s['structural_parts'][s['structural_parts'].index(old)]=new
  replacements.append(dict(name=old['name'],before_mass_kg=old['mass_kg'],after_mass_kg=new['mass_kg']))
for row in g['new_components']:
 if row['role']=='replacement':continue
 density=1850 if row['material']=='GFRP' else 1200
 new=integral(row['name'],shapes[row['name']],row['material'],density,'P07 proposed part; native integral at assumed density')
 s['structural_parts'].append(new);added_by_material[row['material']]=added_by_material.get(row['material'],0)+new['mass_kg']
epoxy_net=added_by_material.get('Epoxy',0)-removed_by_material.get('Epoxy',0)
budget=next(row for row in c['structural_allowances'] if 'Wing saddle/rib adhesive residual' in row['name'])
allocated=min(max(0,epoxy_net),budget['mass_kg']);budget['mass_kg']-=allocated
budget['name']='Wing saddle/rib adhesive residual above P05/P06/P07 explicit bondlines'
budget['source']='Remaining P06 adhesive allocation less net P07 explicit adhesive; reserve untouched'
c['version']='P07 wing-arm integration candidate'
c['additional_requirements']+=['P07 partial-wrap spar cheek bonds and collar transfer require qualification','P07 rib cap/tape corners require fillet radii, ply continuity and peel/fatigue assessment','Local wing-slot doubler ply orientations, skin shear redistribution and edge closure require qualification']
s.update(source_file='RescU_P07_Wing_Arm_Integration.FCStd plus retained P06 aircraft quantities',source_sha256=g['native_sha256'],scope='Local wing-arm integration; full original skin quantity retained; no global stiffness credit')
ledger,mass=engine.mass_ledger(c,s)
expected=sum(added_by_material.values())-sum(removed_by_material.values())-allocated
assert abs(mass['structural_budget_kg']-before['mass']['structural_budget_kg']-expected)<1e-8
assert abs(mass['reserve_kg']-.2)<1e-9
assert len({row['name'] for row in ledger})==len(ledger)
assert c['components']==json.loads((B/'rib-saddle-p06/data/inputs_p06.json').read_text())['components']
cases,arms,thrust,envelope,plate,support=engine.load_screens(c,s,mass,160)
F=c['loads']['alternate_total_vtol_thrust_N']/4*c['loads']['vtol_thrust_multiplier'];reactions=[]
for label,ff,fr in [('both',F,F),('front only',F,0),('rear only',0,F)]:
 rear=(ff*(235-356.4)+fr*(555-356.4))/(410-356.4);front=ff+fr-rear
 reactions.append(dict(case=label,front_N=front,rear_N=rear,total_N=ff+fr,moment_about_spar_Nm=rear*.0536))
demands=[]
for side in ['PosY','NegY']:
 area=sum(row['volume_mm3']/.2 for row in g['new_components'] if row['name'].startswith('SparCheekBond_'+side))/2
 # All torsion through the spar cheeks is deliberately a separate bounding
 # assumption; no credit for an uncomputed sharing with the wing skins.
 cheeks=[shapes[row['name']] for row in g['new_components'] if row['name'].startswith('SparCheek_'+side)]
 assert len(cheeks)==2
 separation=abs(cheeks[0].CenterOfMass.x-cheeks[1].CenterOfMass.x)
 moment=max(abs(q['moment_about_spar_Nm']) for q in reactions)
 force=moment*1000/separation+F/2
 demands.append(dict(side=side,cheek_bond_mean_area_each_mm2=area,cad_cheek_centroid_chordwise_separation_mm=separation,torsion_envelope_Nm=moment,force_per_cheek_N=force,effective_area_factor_assumption=.5,average_shear_demand_MPa=force/(.5*area),status='DEMAND ONLY: load sharing, peel and carbon interlaminar strength unresolved'))
 radialarea=sum(row['volume_mm3']/.2 for row in g['new_components'] if row['name'].startswith('SparToRibBond_'+side))/2
 demands[-1]['radial_rib_interface_endcase']=dict(mean_area_per_cheek_mm2=radialarea,average_shear_demand_MPa=force/(.5*radialarea),assumed_shear_screen_MPa=2.,status='Critical edge-transfer screen. A continuous molded flange or larger developed face joint is required if this all-torque-to-spar case governs; no capacity assigned.')
 upper=[shapes[row['name']] for row in g['new_components'] if row['name'].startswith('SkinBond_Upper_'+side)]
 lower=[shapes[row['name']] for row in g['new_components'] if row['name'].startswith('SkinBond_Lower_'+side)]
 zu=sum(q.CenterOfMass.z*q.Volume for q in upper)/sum(q.Volume for q in upper)
 zl=sum(q.CenterOfMass.z*q.Volume for q in lower)/sum(q.Volume for q in lower)
 sep=zu-zl;caparea=min(sum(q.Volume for q in upper),sum(q.Volume for q in lower))/.2
 demands[-1]['alternative_all_torque_to_skin_caps']=dict(cad_bond_centroid_vertical_separation_mm=sep,minimum_total_projected_bond_area_mm2=caparea,couple_force_N=moment*1000/sep,average_shear_demand_MPa=(moment*1000/sep)/(.5*caparea),status='Separate end case, not added to all-torque-through-spar case; skin stress, peel and sharing unresolved')
result=dict(version=c['version'],status='PRELIMINARY GEOMETRY; NOT STRENGTH QUALIFIED',before_P06_mass=before['mass'],mass=mass,structural_delta_kg=expected,added_by_material_kg=added_by_material,removed_by_material_kg=removed_by_material,epoxy_allowance_reallocated_kg=allocated,skin_mass_credit_kg=0.,reserve_unchanged_kg=.2,components=ledger,replacements=replacements,arm_reactions=reactions,wing_joint_demand_screens=demands,updated_global_load_cases=cases,limits=['Native wing skin Boolean quantities remain unreliable: no skin cutout mass credit','No stiffness credit for caps or slot reinforcement; inherited reduced-stiffness concern remains','P06 joint screens must be recomputed for trimmed ribs/plates; no inherited local PASS is retained','New bonded subassembly has no tested capacity or fatigue life','Motor screw engagement and21V motor versus6S battery issue remain open'])
(R/'reports/results.json').write_text(json.dumps(result,indent=2));(R/'data/inputs_p07_accounting.json').write_text(json.dumps(c,indent=2));(R/'data/accounting_snapshot_p07.json').write_text(json.dumps(s,indent=2))
with (R/'reports/mass_components.csv').open('w',newline='') as f:
 out=csv.DictWriter(f,fieldnames=['name','category','material','mass_kg','x_m','y_m','z_m'],extrasaction='ignore');out.writeheader();out.writerows(ledger)
print(json.dumps(dict(structural_mass_g=mass['structural_budget_kg']*1000,delta_g=expected*1000,skin_credit_g=0,reserve_g=200,cheek_demand=demands),indent=2))
