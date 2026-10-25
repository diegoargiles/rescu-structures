"""P07 local wing integration candidate. Run with bundled FreeCAD 1.1 Python.
P04/P06 sources are never modified. Millimetres; geometry assumptions in inputs_p07.json.
"""
import json,sys,hashlib,time,functools,faulthandler
from pathlib import Path
import FreeCAD as A,Part,Assembly
sys.path.append(str(Path(A.getHomePath())/'Mod/Assembly'))
import JointObject
faulthandler.dump_traceback_later(120,repeat=True)
V=A.Vector;R=Path(__file__).resolve().parents[1];B=R.parent;W=B/'v4-attachments' if (B/'v4-attachments').exists() else B
for f in ['cad','cad/parts','reports','data','docs']:(R/f).mkdir(parents=True,exist_ok=True)
src=B/'rib-saddle-p06/cad/RescU_P06_Rib_Saddle_Assembly.FCStd'
resume='--resume-posy' in sys.argv
d=A.openDocument(str(R/'cad/P07_PosY_checkpoint.FCStd') if resume else str(src));d.Label='RescU P07 | wing-arm integration | preliminary bonded candidate'
w=A.openDocument(str(W/'cad/RescU_P04_Attachment_Study.FCStd'))
g06=json.loads((B/'rib-saddle-p06/reports/geometry_checks.json').read_text())
p05=json.loads((B/'motor-arm-p05/reports/assembly_checks.json').read_text())
oldnames=[r['name'] for r in p05['components']]+[r['name'] for r in g06['added_components']]
assert len(set(oldnames))==162
inputs=dict(version='P07 wing-arm integration candidate',source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
 flange_x_mm=[340.,425.],flange_width_mm=18.,flange_vertical_thickness_mm=.6,skin_bond_vertical_mm=.2,rib_edge_bond_vertical_mm=.2,
 rib_face_tape_thickness_mm=.4,rib_face_bond_mm=.2,
 spar_bond_radial_mm=.2,spar_cheek_radial_mm=.6,rib_spar_bond_radial_mm=.2,
 spar_coupler_span_mm=64.,spar_cheek_half_height_mm=3.2,collar_face_thickness_mm=.8,collar_face_bond_mm=.2,
 slot_reinforcement_thickness_vertical_mm=.6,slot_edge_overlap_mm=8.,
 densities_kg_m3={'GFRP':1850.,'Epoxy':1200.,'XPS':32.},
 evidence='Native saved profiles and spar geometry; all new laminate/bond dimensions are design assumptions, not measured hardware.',
 fit_strategy='Open fore/aft spar cheeks, not a closed sleeve: retained wing envelope limits top/bottom space.')
(R/'data/inputs_p07.json').write_text(json.dumps(inputs,indent=2))
rows=[];modified=[];wings={};bonds=[];diagnostics=[]
rho=inputs['densities_kg_m3']
def prep(s):
 # OCC's unmeshed spline-face bounding boxes can span the whole source loft.
 # Tessellation supplies tight bounds for Boolean broad-phase culling without
 # replacing, approximating or changing the exact underlying BREP geometry.
 s.tessellate(.3);return s
def gs(o):
 s=o.Shape.copy();s.Placement=o.getGlobalPlacement()*o.Placement.inverse()*s.Placement;return prep(s)
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def shift(s,z):
 q=s.copy();q.translate(V(0,0,z));return q
def comp(items):return Part.makeCompound(items)
def prop(o,k,v,typ='App::PropertyString'):
 if k not in o.PropertiesList:o.addProperty(typ,k,'P07 design')
 setattr(o,k,v)
def fixed(jg,parent,o):
 j=jg.newObject('App::FeaturePython','Fix_'+o.Name);JointObject.Joint(j,0)
 j.Detach1=True;j.Detach2=True;j.Reference1=(parent,['','']);j.Reference2=(o,['',''])
 j.Placement1=parent.Placement.inverse()*o.Placement;j.Placement2=A.Placement()
def replace(o,s,asm,reason):
 before=gs(o);assert s.isValid() and s.Volume>0,(o.Name,len(s.Solids))
 if len(s.Solids)>1:
  solids=sorted(s.Solids,key=lambda q:q.Volume,reverse=True)
  mat=o.Material
  for i,extra in enumerate(solids[1:],1):add(asm,d.getObject('Joints_'+asm.Name.split('_')[-1]),o.Name+'_P07Segment'+str(i),extra,mat)
  s=solids[0]
 o.Shape=s;o.Placement=asm.getGlobalPlacement().inverse()*s.Placement
 modified.append(dict(name=o.Name,reason=reason,before_volume_mm3=before.Volume,after_volume_mm3=s.Volume,removed_volume_mm3=before.Volume-s.Volume))
 assert abs(gs(o).Volume-s.Volume)<1e-5
def add(asm,jg,name,s,mat,parent=None,role='physical'):
 result=[]
 for i,solid in enumerate(s.Solids):
  if solid.Volume<1e-5:continue
  assert solid.isValid(),name
  prep(solid)
  n=name+('_Piece'+str(i+1) if len(s.Solids)>1 else '')
  o=asm.newObject('Part::Feature',n);o.Shape=solid;o.Placement=asm.getGlobalPlacement().inverse()*solid.Placement
  prop(o,'Material',mat);prop(o,'Evidence','P07 assumed thickness; native surface-derived geometry')
  prop(o,'DesignStatus','Preliminary bonded candidate; peel/fatigue and laminate qualification open')
  prop(o,'MassCategory','replacement wing part' if role=='replacement' else 'additional structure')
  prop(o,'AccountedMass_kg',solid.Volume*rho.get(mat,1600)*1e-9,'App::PropertyFloat')
  fixed(jg,parent or d.getObject('CFRP_Arm_'+asm.Name.split('_')[-1]),o)
  rows.append(dict(name=n,side=asm.Name.split('_')[-1],material=mat,role=role,volume_mm3=solid.Volume,mass_kg=solid.Volume*rho.get(mat,1600)*1e-9,solid_count=1,valid=True))
  result.append(o)
 assert result,'Empty part: '+name
 return result
def outer_spar(s):
 f=max((f for f in s.Faces if type(f.Surface).__name__=='Cone'),key=lambda f:f.Area)
 q=Part.makeSolid(Part.makeShell([f]+[Part.Face(f.OuterWire) for f in s.Faces if type(f.Surface).__name__=='Plane']))
 q.fix(1e-7,1e-7,1e-7);assert q.isValid();return q,f.Surface
if resume:
 ref=A.openDocument(str(src))
 for o in d.MotorArm_PosY.Group:
  if o.Name in oldnames or not hasattr(o,'Material') or not hasattr(o,'Shape'):continue
  q=gs(o);mat=o.Material
  rows.append(dict(name=o.Name,side='PosY',material=mat,role='physical',volume_mm3=q.Volume,mass_kg=q.Volume*rho.get(mat,1600)*1e-9,solid_count=len(q.Solids),valid=q.isValid()))
 for name in oldnames:
  old=gs(ref.getObject(name));new=gs(d.getObject(name))
  if abs(old.Volume-new.Volume)>1e-5:modified.append(dict(name=name,reason='Restored P07 checkpoint modification',before_volume_mm3=old.Volume,after_volume_mm3=new.Volume,removed_volume_mm3=old.Volume-new.Volume))
for side,y in [('PosY',265.),('NegY',-265.)]:
 print('Starting',side,flush=True)
 asm=d.getObject('MotorArm_'+side);asm.Label='P07 | '+side+' wing + motor arm';jg=d.getObject('Joints_'+side)
 core=prep(w.getObject('Wing_'+side+'_Ravatherm_Core_Exposed').Shape)
 skin=d.getObject('RelievedWingSkin_'+side).Shape.copy()
 spar=w.getObject('Wing_'+side+'_CFRP_TaperedSpar').Shape
 outer,surface=outer_spar(spar)
 offsets={0:outer}
 for a in [.2,.4,.8,1.0]:offsets[a]=outer.makeOffsetShape(a,1e-5)
 ribs=[d.getObject('Wing_Spar_Rib'+str(i)+'_'+side) for i in [1,2]]
 originalribs=[gs(ref.getObject(o.Name)) if resume and side=='PosY' else gs(o) for o in ribs]
 # Native P04 foam already contains rib/spar cavities. Fill only these cavities
 # locally to recover the skin-side contour before creating conforming cap strips.
 window=box(338,y-35,-8,90,70,35)
 env=core.common(window)
 for q in originalribs+[outer.common(window)]:env=env.fuse(q)
 env=prep(env.removeSplitter());assert env.isValid()
 # Material bands grow inward from the native core boundary, without assuming
 # a constant airfoil thickness or adding a generic rectangular top skin.
 @functools.lru_cache(None)
 def upper(a,b):return prep(shift(env,-a).cut(shift(env,-b),1e-6))
 @functools.lru_cache(None)
 def lower(a,b):return prep(shift(env,a).cut(shift(env,b),1e-6))
 masks=[];localnew=[];cap_envelopes=[]
 if not (resume and side=='PosY'):
  # Restrict the spar coupling to lateral arcs: the upper/lower crown is open.
  axis=surface.Axis;radial=V(0,0,1)-axis*axis.z;radial.normalize()
  across=axis.cross(radial);across.normalize()
  basis=A.Matrix();basis.A11=across.x;basis.A21=across.y;basis.A31=across.z
  basis.A12=axis.x;basis.A22=axis.y;basis.A32=axis.z
  basis.A13=radial.x;basis.A23=radial.y;basis.A33=radial.z
  center=surface.Center+axis*((y-surface.Center.y)/axis.y)
  clip=box(-20,-80,-3.2,40,160,6.4);clip.Placement=A.Placement(center,A.Rotation(basis))
  span=box(330,y-32,-20,100,64,60)
  cheekmask=clip.common(span)
  radialbond=offsets[.2].cut(outer).common(cheekmask)
  cheek=offsets[.8].cut(offsets[.2]).common(cheekmask)
  ringbond=offsets[1.0].cut(offsets[.8]).common(cheekmask)
  # Open side arcs preserve the native skin envelope; their development length is
  # a sizing proposal. Later collision checks include every retained splice piece.
  localnew+=add(asm,jg,'SparCheekBond_'+side,radialbond,'Epoxy')
  localnew+=add(asm,jg,'SparCheek_'+side,cheek,'GFRP')
  for ri,(rib,oldrib) in enumerate(zip(ribs,originalribs),1):
   yy=oldrib.CenterOfMass.y
   strip=box(340,yy-9,-8,85,18,35)
   # A cap is bonded to each skin; another thin layer beds the trimmed rib edge.
   # Relief of the spar keeps these caps physically distinct from the side cheeks.
   for label,fn in [('Upper',upper),('Lower',lower)]:
    skinbond=fn(0,.2).common(strip).cut(offsets[1.0])
    cap=fn(.2,.8).common(strip).cut(offsets[1.0])
    bed=fn(.8,1.0).common(box(340,yy-1,-8,85,2,35)).cut(offsets[1.0])
    cap_envelopes.append(fn(0,1.0).common(strip))
    for n,s,mat in [('SkinBond',skinbond,'Epoxy'),('Flange',cap,'GFRP'),('RibEdgeBond',bed,'Epoxy')]:
     localnew+=add(asm,jg,n+'_'+label+'_'+side+'_Rib'+str(ri),s,mat)
   newrib=oldrib.cut(offsets[1.0]).common(shift(env,-1.)).common(shift(env,1.)).removeSplitter()
   segments=sorted(newrib.Solids,key=lambda q:q.Volume,reverse=True)
   replace(rib,segments[0],asm,'Skin flange inset and spar relief; main aft shear-web segment retained')
   for sn,segment in enumerate(segments[1:],1):
    localnew+=add(asm,jg,'RibForwardSegment_'+side+'_Rib'+str(ri)+'_'+str(sn),segment,'GFRP')
   print('Rib',side,ri,'segments',len(segments),flush=True)
   # Two thin glass face tapes join the rib web to its cap strips. Their final
   # corner radius/ply drape is a manufacturing detail, not implied by sharp CAD edges.
   for faceid,sgn in [('A',-1),('B',1)]:
    faceparts=[f for f in newrib.Faces if type(f.Surface).__name__=='Plane' and abs(f.normalAt(0,0).y-sgn)<1e-5]
    extended=oldrib.cut(offsets[1.0]).common(shift(env,-.8)).common(shift(env,.8))
    tapefaces=[f for f in extended.Faces if type(f.Surface).__name__=='Plane' and abs(f.normalAt(0,0).y-sgn)<1e-5]
    bond=comp([f.extrude(V(0,sgn*.2,0)) for f in tapefaces])
    tape=[]
    for f in tapefaces:
     a=f.copy();a.translate(V(0,sgn*.2,0));tape.append(a.extrude(V(0,sgn*.4,0)))
    tape=comp(tape)
    avoid=comp([gs(d.getObject(n)) for n in oldnames if side in n and not n.startswith('Wing_Spar_Rib')])
    bond=bond.cut(avoid);tape=tape.cut(avoid)
    localnew+=add(asm,jg,'RibFaceBond_'+side+'_Rib'+str(ri)+faceid,bond,'Epoxy')
    localnew+=add(asm,jg,'RibFaceTape_'+side+'_Rib'+str(ri)+faceid,tape,'GFRP')
   # Collar doublers spread sleeve-to-rib transfer over the rib faces. They are
   # cropped to the thin native airfoil rather than modeled as oversized washers.
   for faceid,sgn in [('A',-1),('B',1)]:
    yf=yy+sgn*1.
    collarzone=box(339,min(yf+sgn*.6,yf+sgn*1.6),-8,35,1.,35)
    # Face tapes occupy first0.6 mm; collar bond0.2 and laminate0.8 follow.
    bondzone=box(339,min(yf+sgn*.6,yf+sgn*.8),-8,35,.2,35)
    glasszone=box(339,min(yf+sgn*.8,yf+sgn*1.6),-8,35,.8,35)
    outerzone=offsets[1.0].makeOffsetShape(4.,1e-5).cut(offsets[1.0])
    for n,zone,mat in [('CollarFaceBond',bondzone,'Epoxy'),('SparCollar',glasszone,'GFRP')]:
     s=outerzone.common(zone).common(shift(env,-1.)).common(shift(env,1.)).cut(avoid)
     localnew+=add(asm,jg,n+'_'+side+'_Rib'+str(ri)+faceid,s,mat)
    # Continuous radial epoxy bridges sleeve to rib, tape and collar edges.
   localnew+=add(asm,jg,'SparToRibBond_'+side+'_Rib'+str(ri),ringbond.common(box(330,yy-2.6,-10,100,5.2,40)).cut(avoid),'Epoxy')
 else:
  localnew=[d.getObject(row['name']) for row in rows if row['side']==side]
  for oldrib in originalribs:
   yy=oldrib.CenterOfMass.y;strip=box(340,yy-9,-8,85,18,35)
   cap_envelopes += [upper(0,1.).common(strip),lower(0,1.).common(strip)]
  # Restore the same open-cheek cutting envelope from exact conical geometry.
  axis=surface.Axis;radial=V(0,0,1)-axis*axis.z;radial.normalize();across=axis.cross(radial);across.normalize()
  basis=A.Matrix();basis.A11=across.x;basis.A21=across.y;basis.A31=across.z
  basis.A12=axis.x;basis.A22=axis.y;basis.A32=axis.z;basis.A13=radial.x;basis.A23=radial.y;basis.A33=radial.z
  center=surface.Center+axis*((y-surface.Center.y)/axis.y)
  clip=box(-20,-80,-3.2,40,160,6.4);clip.Placement=A.Placement(center,A.Rotation(basis))
  cheekmask=clip.common(box(330,y-32,-20,100,64,60))
 # Trim inherited P06 pieces against the larger cheek/collar clearance and cap
 # volumes; record every replaced quantity rather than adding a second rib.
 print('Trimming inherited carrier',side,flush=True)
 d.recompute();d.saveAs(str(R/('cad/P07_'+side+'_checkpoint.FCStd')))
 cutters=[prep(q) for q in [offsets[1.0].common(cheekmask)]+cap_envelopes]
 for n in oldnames:
  if side not in n or n.startswith('Wing_Spar_Rib'):continue
  o=d.getObject(n);s=gs(o)
  if s.optimalBoundingBox().intersect(window.BoundBox):
   q=s
   for cutter in cutters:
    if q.optimalBoundingBox().intersect(cutter.optimalBoundingBox()):q=q.cut(cutter,1e-5)
   q=q.removeSplitter()
   if s.Volume-q.Volume>1e-5:replace(o,q,asm,'Clearance for P07 cap and spar coupling')
 # Inboard skin doublers surround the four existing lower-skin entry slots.
 print('Slot reinforcement',side,flush=True)
 for slot in [o for o in d.Objects if o.Name.startswith('Slot_'+side+'_')]:
  bb=slot.Shape.BoundBox;rim=box(bb.XMin-8,bb.YMin-8,-8,bb.XLength+16,bb.YLength+16,20).cut(box(bb.XMin,bb.YMin,-10,bb.XLength,bb.YLength,40))
  occupied=comp([gs(o) for o in localnew]+[gs(o) for o in ribs])
  for label,a,b,mat in [('SlotSkinBond',0,.2,'Epoxy'),('SlotDoubler',.2,.8,'GFRP')]:
   s=lower(a,b).common(rim)
   # Keep doublers outside the full cap/web installation footprint. This is a
   # simple manufacturing trim, not hundreds of pairwise spline subtractions.
   for originalrib in originalribs:
    yy=originalrib.CenterOfMass.y
    s=s.cut(box(340,yy-9,-10,85,18,40),1e-5)
   s=s.cut(offsets[1.0],1e-5)
   if s.Volume>1e-4:localnew+=add(asm,jg,label+'_'+slot.Name,s,mat)
 print('Core pocketing',side,flush=True)
 # Explicit manufacturing pockets, rather than an impractical negative of every
 # individual ply/bond edge. Web bays give0.4 mm nominal lateral clearance around
 # the5.2 mm collar stack; caps retain their native contour channels.
 beforecore=prep(d.getObject('PocketedCore_'+side).Shape)
 foam_cutters=list(cap_envelopes)+[offsets[1.0].common(cheekmask)]
 for originalrib in originalribs:
  yy=originalrib.CenterOfMass.y;foam_cutters.append(box(338,yy-3,-8,92,6,35))
 for slot in [o for o in d.Objects if o.Name.startswith('Slot_'+side+'_')]:
  bb=slot.Shape.BoundBox;rim=box(bb.XMin-8,bb.YMin-8,-8,bb.XLength+16,bb.YLength+16,20)
  foam_cutters.append(lower(0,.8).common(rim))
 newcore=beforecore
 for ci,cutter in enumerate(foam_cutters):
  prep(cutter);newcore=newcore.cut(cutter,1e-5);prep(newcore)
  print('Foam pocket',side,ci+1,'/',len(foam_cutters),flush=True)
 assert newcore.isValid()
 removed=beforecore.cut(newcore,1e-5)
 foamerror=abs((beforecore.Volume-newcore.Volume)-removed.Volume)
 diagnostics.append(dict(side=side,foam_removed_mm3=removed.Volume,foam_conservation_error_mm3=foamerror,foam_credit_pass=foamerror<max(.1,.01*removed.Volume),skin_mass_credit_kg=0.))
 localnew+=add(asm,jg,'WingCore_'+side,newcore,'XPS',role='replacement')
 localnew+=add(asm,jg,'WingSkin_'+side,skin,'GFRP',role='replacement')
 localnew+=add(asm,jg,'WingSpar_'+side,spar,'CFRP',role='replacement')
 wings[side]=[o.Name for o in localnew]
 print('Built',side,len(localnew),'new pieces; foam delta',beforecore.Volume-newcore.Volume,flush=True)
# Refresh explicit datums after shape replacements. Shape changes are not rigid-body DOFs.
for j in d.Objects:
 if hasattr(j,'Reference1') and hasattr(j,'Reference2') and j.Reference1 and j.Reference2:
  a,b=j.Reference1[0],j.Reference2[0]
  if a and b:j.Placement1=a.Placement.inverse()*b.Placement;j.Placement2=A.Placement()
d.MotorArmPair.Label='P07 | wing-arm pair | preliminary bonded integration'
d.WingPocketContext.Visibility=False;d.recompute()
solves={side:int(d.getObject('MotorArm_'+side).solve()) for side in wings}
assert all(v==0 for v in solves.values()),solves
out=R/'cad/RescU_P07_Wing_Arm_Integration.FCStd';d.saveAs(str(out))
result=dict(version=inputs['version'],source_sha256=inputs['source_sha256'],new_components=rows,modified_components=modified,wing_parts=wings,diagnostics=diagnostics,solver_codes=solves,native_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),old_physical_names=oldnames)
(R/'reports/build.json').write_text(json.dumps(result,indent=2))
print('Saved P07',len(rows),'new pieces',len(modified),'modified inherited pieces',flush=True)
