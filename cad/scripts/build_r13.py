"""R13 preliminary layout. Run with FreeCAD Python, passing R12 native path and output directory.
No strength release. R12 is opened read-only in intent and never saved over.
"""
import FreeCAD as A, Part, json, math, hashlib, csv, sys
from pathlib import Path
V=A.Vector
source=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();out.mkdir(parents=True,exist_ok=True)
before_hash=hashlib.sha256(source.read_bytes()).hexdigest()
assert before_hash=='1998ebcfadd7398ea2b0075816696841f28581b3e9c6e186d92ef756a051b11e'
d=A.openDocument(str(source));baseline={o.Name:o.Shape.copy() for o in d.Objects if o.TypeId=='PartDesign::Feature'}
rows=[];new=[];modified=[];removed=[]
g=d.addObject('App::Part','R13_New_Parts')
def box(x0,x1,y0,y1,z0,z1):return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cyl(r,a,b):
 a=V(*a);b=V(*b);u=b-a;return Part.makeCylinder(r,u.Length,a,u)
def tube(ro,ri,a,b):return cyl(ro,a,b).cut(cyl(ri,a,b))
def record(n,old,newvol,rho):rows.append({'part':n,'density_assumed_g_cm3':rho,'R12_volume_mm3':old,'R13_volume_mm3':newvol,'delta_g':(newvol-old)*rho/1000})
def add(n,s,rho,role='structure'):
 s=s.removeSplitter();assert s.isValid() and s.Solids,n
 o=d.addObject('PartDesign::Feature',n);o.Shape=s;g.addObject(o)
 o.addProperty('App::PropertyString','ReviewStatus').ReviewStatus='R13 PRELIMINARY: geometry candidate; not strength qualified'
 o.addProperty('App::PropertyString','PartRole').PartRole=role
 if rho is not None:record(n,0,s.Volume,rho)
 new.append(n);return o
def change(n,s,rho):
 o=d.getObject(n);record(n,baseline[n].Volume,s.Volume,rho);o.Shape=s;modified.append(n)
def delete(n,rho):
 if rho is not None:record(n,baseline[n].Volume,0,rho)
 d.removeObject(n);removed.append(n)
def move(n,dx=0,dy=0,dz=0):
 s=d.getObject(n).Shape.copy();s.translate(V(dx,dy,dz));d.getObject(n).Shape=s;modified.append(n)

# Remove superseded clamp-on motor mounts, rectangular booms and ESC bands.
for n in list(baseline):
 rho=None;remove=False
 if n.startswith('Arm_30x20'):rho=1.6;remove=True
 elif n.startswith('Internal_GFRP_sleeve_'):rho=1.9;remove=True
 elif 'bonded_axial_stop_band' in n:rho=1.9;remove=True
 elif any(t in n for t in ['integrated_motor_saddle','windowed_lower_keeper','compact_clevis']) or n.startswith(('Forward_lower_keeper','Aft_lower_keeper')):rho=2.7;remove=True
 elif 'clamp_screw' in n:rho=7.85;remove=True
 elif 'ESC_band' in n:rho=1.15;remove=True
 elif 'ESC_cushion' in n:rho=1.2;remove=True
 if remove:delete(n,rho)
for side,sg in [('PosY',1),('NegY',-1)]:
 y=sg*265
 add('R13_Round_Boom_'+side,tube(12.5,11.5,(150,y,-31),(620,y,-31)),1.6)
 for tag,xold,xnew in [('Front',235,170),('Rear',555,600)]:
  # Composite bonded socket plus motor deck and two webs; separate manufacture from boom.
  socket=tube(14,12.65,(xnew-16,y,-31),(xnew+16,y,-31))
  deck=cyl(19,(xnew,y,-15.3),(xnew,y,-12.8)).cut(cyl(4,(xnew,y,-16),(xnew,y,-12)))
  for dy in [-9,9]:deck=deck.fuse(box(xnew-14,xnew+14,y+dy-1,y+dy+1,-23,-15))
  sh=socket.fuse(deck).cut(cyl(12.65,(xnew-25,y,-31),(xnew+25,y,-31)))
  for dx,dy in [(-9.5,0),(9.5,0),(0,-12.5),(0,12.5)]:
   sh=sh.cut(cyl(1.6,(xnew+dx,y+dy,-25),(xnew+dx,y+dy,-10)))
   sh=sh.cut(cyl(2.85,(xnew+dx,y+dy,-25),(xnew+dx,y+dy,-15.3)))
  add('R13_'+tag+'_Bonded_Motor_Pod_'+side,sh,1.6)
  for n in baseline:
   if n.endswith('_'+side) and n.startswith(tag+'_') and any(s in n for s in ['AT2814','hub_envelope','motor_screw']):move(n,xnew-xold,0,-6)
  # Reference disk is a volume reservation, never structural mass.
  # Hub height from translated geometry; disk thickness is a provisional +/-2 mm allowance.
  hub=d.getObject(tag+'_hub_envelope_'+side).Shape.BoundBox
  z=(hub.ZMin+hub.ZMax)/2
  add('REFERENCE_R13_'+tag+'_10inch_Disk_'+side,cyl(127,(xnew,y,z-2),(xnew,y,z+2)),None,'clearance')
 # Tube-to-wing sockets retain the small existing rib bolts; no boom clamp screws.
 for tag,x in [('Forward',335),('Aft',405)]:
  sh=tube(14,12.65,(x-10,y,-31),(x+10,y,-31))
  for a,b in [(-3.5,-1.15),(1.15,3.5)]:sh=sh.fuse(box(x-7,x+7,y+a,y+b,-18.8,-3.2))
  sh=sh.cut(cyl(12.65,(x-11,y,-31),(x+11,y,-31)))
  sh=sh.cut(cyl(1.6,(x,y-12,-8),(x,y+12,-8)))
  add('R13_'+tag+'_Bonded_Wing_Socket_'+side,sh,1.6)
 # An aft spar follows sweep; it does not alter the straight retained main joiner.
 a=(385,sg*85,3.1);b=(427.9,sg*415,3.1)
 member=tube(2.5,1.75,a,b)
 add('R13_Aft_Torque_Tube_'+side,member,1.6)
 # Distinct root socket accepts the existing D3 removable pin and the bonded aft tube.
 socket=cyl(2.5,(385,sg*46,3),(385,sg*65,3))
 w1=Part.Wire(Part.makeCircle(2.5,V(385,sg*64.9,3),V(0,sg,0)))
 w2=Part.Wire(Part.makeCircle(3.25,V(385,sg*75,3.3),V(0,sg,0)))
 socket=socket.fuse(Part.makeLoft([w1,w2],True)).fuse(cyl(3.25,(385,sg*74.9,3.3),(385,sg*95,3.3)))
 socket=socket.cut(cyl(1.65,(385,sg*45,3),(385,sg*69,3)))
 unit=(V(*b)-V(*a));unit.normalize()
 socket=socket.cut(Part.makeCylinder(2.65,30,V(*a),unit))
 delete('AntiRotation_Bushing_'+side,1.9)
 add('R13_Aft_Root_Socket_'+side,socket,1.9)
 # Retain the original root-diaphragm interface; enlarge only foam passage for the socket transition.
 rootpass=cyl(2.65,(385,sg*45,3),(385,sg*65,3)).fuse(cyl(3.4,(385,sg*65,3.3),(385,sg*96,3.3)))
 for n in baseline:
  if n.startswith('XPS_Rib_'+side+'_'):
   o=d.getObject(n)
   if o.Shape.distToShape(rootpass)[0]<1e-6:
    o.Shape=o.Shape.cut(rootpass)
    if n not in modified:modified.append(n)
 # Explicit bonded collars at load-introduction rib and three outboard ribs.
 for station in [265,310,360,410]:
  pt=V(385+.13*(station-85),sg*station,3.1)
  tool=Part.makeCylinder(3.15,14,pt-unit*7,unit)
  collar=Part.makeCylinder(3.0,8,pt-unit*4,unit).cut(Part.makeCylinder(2.65,10,pt-unit*5,unit))
  add('R13_Aft_Spar_Bond_Collar_'+str(station)+'_'+side,collar,1.9)
  # Cut only affected ribs; foam removal is accounted at 32 kg/m3.
  for n in baseline:
   if n.startswith('XPS_Rib_'+side+'_') or n=='CFRP_motor_rib_nominal_2mm_'+side:
    o=d.getObject(n)
    if o.Shape.distToShape(tool)[0]<1e-6:
     rho=1.6 if n.startswith('CFRP') else .032
     # Multiple cuts require cumulative mass from original only once.
     s=o.Shape.cut(tool);o.Shape=s
     if n not in modified:modified.append(n)
  # Collar shell load spreading still requires local skin/bond design.
 # Other crossed foam ribs receive passage clearance; no assumed load transfer there.
 passage=Part.makeCylinder(2.65,(V(*b)-V(*a)).Length,V(*a),unit)
 for n in baseline:
  if n.startswith('XPS_Rib_'+side+'_'):
   o=d.getObject(n)
   if o.Shape.distToShape(passage)[0]<1e-6:
    o.Shape=o.Shape.cut(passage)
    if n not in modified:modified.append(n)
 # ESCs relocate as equipment envelopes; mass unchanged, wiring/cooling are open.
 for tag,x in [('Front',465),('Rear',535)]:
  n=tag+'_AIR40A_installation_envelope_'+side;o=d.getObject(n);bb=o.Shape.BoundBox
  move(n,x-(bb.XMin+bb.XMax)/2,sg*15-(bb.YMin+bb.YMax)/2,-15.5-bb.ZMin)
  add('R13_'+tag+'_ESC_Pad_'+side,box(x-27.8,x+27.8,sg*15-12.6,sg*15+12.6,-16,-15.5),1.2)

for n in modified:
 if n.startswith(('XPS_Rib_','CFRP_motor_rib_')):record(n,baseline[n].Volume,d.getObject(n).Shape.Volume,1.6 if n.startswith('CFRP') else .032)
# ESC deck is a mounting provision; lower bonded frames and retention must be finalized.
add('R13_ESC_Service_Deck',box(435,565,-29,29,-17,-16),1.9)
# Explicit lower cradle geometry with nominal shell clearance; fitted to original cylindrical bay.
for x in [445,550]:
 # R12 tapers aft. Radius sampled from shell section bounding limits, then inset.
 shell=d.getObject('Fuselage_Shell_with_TopOpenings').Shape
 sec=shell.slice(V(1,0,0),x);outer=max(sec,key=lambda w:Part.Face(w).Area)
 face=Part.Face(outer);inside=outer.makeOffset2D(-.55,0,False,False,True)
 innermore=outer.makeOffset2D(-2.05,0,False,False,True)
 ring=Part.Face(inside).cut(Part.Face(innermore)).extrude(V(1.5,0,0)).common(box(x,x+1.5,-60,60,-60,-17))
 bar=box(x,x+1.5,-44,44,-18.5,-17).common(Part.Face(inside).extrude(V(1.5,0,0)))
 add('R13_ESC_Bonded_Cradle_'+str(x),ring.fuse(bar),1.9)
d.recompute()
features=[o for o in d.Objects if o.TypeId=='PartDesign::Feature']
invalid=[o.Name for o in features if not o.Shape.isValid() or not o.Shape.Solids]
assert not invalid,invalid
native=out/'RescU_R13_Layout_Candidate.FCStd';d.saveAs(str(native))
physical=[o for o in features if not o.Name.startswith('REFERENCE_')]
Part.export(physical,str(out/'RescU_R13_Assembly.step'))
Part.export([d.getObject(n) for n in new if not n.startswith('REFERENCE_')],str(out/'RescU_R13_New_Parts.step'))
with (out/'mass_changes.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary={'revision':'R13 preliminary layout','baseline_sha256':before_hash,'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'changed':modified,'new':new,'removed':removed,'invalid_features':invalid,'feature_count':len(features),'modeled_structural_delta_g':sum(r['delta_g'] for r in rows),'mass_scope':'Changed structural parts/pads/hardware only. Assumed densities; added adhesive, ESC retention, wiring/connectors and finish excluded. No whole-aircraft mass or CG release.','candidate':{'motor_x_mm':[170,600],'motor_z_change_mm':-6,'boom_OD_ID_length_mm':[25,23,470],'aft_spar_OD_ID_mm':[5,3.5],'aft_spar_end_absY_mm':415,'prop_diameter_mm':254,'main_wing_dihedral_requirement_deg':0,'vtail_dihedral_requirement_deg':35},'status':'GEOMETRY CANDIDATE ONLY; clearance and strength checks separate'}
(out/'summary.json').write_text(json.dumps(summary,indent=2))
assert hashlib.sha256(source.read_bytes()).hexdigest()==before_hash
print(json.dumps({k:v for k,v in summary.items() if k not in ['changed','new','removed']},indent=2),flush=True)
