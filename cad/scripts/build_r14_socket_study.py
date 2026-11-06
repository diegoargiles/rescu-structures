"""Controlled R13 variant: lengthen four wing-socket sleeves only, 20 to 32 mm.
Keeps clevis ears and bolts unchanged; not a strength-qualified revision.
"""
import FreeCAD as A, Part, json, hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2];src=root/'cad/r13/RescU_R13_Layout_Candidate.FCStd'
out=root/'cad/r14_socket_study';out.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=sha(src);d=A.openDocument(str(src));changes=[]
for side,sg in [('PosY',1),('NegY',-1)]:
 for tag,x in [('Forward',335),('Aft',405)]:
  n='R13_'+tag+'_Bonded_Wing_Socket_'+side;o=d.getObject(n);old=o.Shape.Volume
  axis=A.Vector(1,0,0);p=A.Vector(x-16,sg*265,-31)
  sleeve=Part.makeCylinder(14,32,p,axis).cut(Part.makeCylinder(12.65,32,p,axis))
  o.Shape=o.Shape.fuse(sleeve).removeSplitter();o.Label='R14 '+tag+' sleeve 32 mm '+side
  o.ReviewStatus='R14 overlap study: unchanged ears/bolts; no structural acceptance'
  assert o.Shape.isValid() and len(o.Shape.Solids)==1
  changes.append({'name':n,'old_volume_mm3':old,'new_volume_mm3':o.Shape.Volume,'delta_g_at_1600kg_m3':(o.Shape.Volume-old)*.0016})
d.recompute();native=out/'RescU_R14_Socket_Overlap_Study.FCStd';d.saveAs(str(native))
physical=[o for o in d.Objects if o.TypeId=='PartDesign::Feature' and not o.Name.startswith('REFERENCE_')]
inter=[];tested=0
for row in changes:
 o=d.getObject(row['name']);b=o.Shape.BoundBox
 for p in physical:
  if p.Name==o.Name:continue
  if not b.intersect(p.Shape.BoundBox):continue
  tested+=1;v=o.Shape.common(p.Shape).Volume
  if v>.01:inter.append({'a':o.Name,'b':p.Name,'overlap_mm3':v})
Part.export([d.getObject(r['name']) for r in changes],str(out/'RescU_R14_Four_Wing_Sockets.step'))
result={'baseline_r13_sha256':before,'native_sha256':sha(native),'changes':changes,'delta_g':sum(r['delta_g_at_1600kg_m3'] for r in changes),'tested_pairs':tested,'intersections':inter,'scope':'Four modified sockets against physical R14 features, overlap threshold 0.01 mm3. Other interfaces inherit R13 checks. No loaded clearance, tool access or bond strength acceptance.','old_overlap_mm':20,'new_overlap_mm':32,'radial_bond_gap_mm':.15,'status':'FIT STUDY ONLY'}
(out/'study_summary.json').write_text(json.dumps(result,indent=2));assert sha(src)==before
print(json.dumps(result,indent=2),flush=True)
