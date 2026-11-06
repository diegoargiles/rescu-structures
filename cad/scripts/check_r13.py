import FreeCAD as A,Part,json,sys,math
from pathlib import Path
import numpy as np
from shapely.geometry import MultiPoint,Point
out=Path(sys.argv[1]).resolve();d=A.openDocument(str(out/'RescU_R13_Layout_Candidate.FCStd'))
meta=json.loads((out/'summary.json').read_text());names=set(meta['new']+[n for n in meta['changed'] if 'AT2814' in n or 'AIR40A' in n or 'motor_screw' in n or 'hub_envelope' in n]);p={o.Name:o for o in d.Objects if o.TypeId=='PartDesign::Feature'}
meshes={};bounds={}
for n,o in p.items():
 v,t=o.Shape.tessellate(.35);pts=np.array([[a.x,a.y,a.z] for a in v]);bounds[n]=(pts.min(axis=0),pts.max(axis=0));meshes[n]={'v':pts.tolist(),'t':t}
(out/'review_mesh.json').write_text(json.dumps(meshes))
res={'invalid_shapes':[n for n,o in p.items() if not o.Shape.isValid()],'intersections':[],'tested_pairs':0,'plan_clearance_mm':{},'notes':['New components and relocated equipment/hardware checked against physical features. Modified inherited ribs are included as counterparts; unchanged-to-unchanged and modified-rib-to-inherited-shell pairs are excluded.','Hardware envelopes may intentionally engage. All overlaps are reported for review.','Clearances are nominal rigid geometry, no blade flex or tolerance budget.']}
keys=[n for n in p if not n.startswith('REFERENCE_')]
for i,a in enumerate(keys):
 for b in keys[i+1:]:
  if a not in names and b not in names:continue
  aa,ab=bounds[a];ba,bb=bounds[b]
  if np.any(ab<ba+1e-5) or np.any(bb<aa+1e-5):continue
  res['tested_pairs']+=1
  print('PAIR',a,b,flush=True)
  vol=p[a].Shape.common(p[b].Shape).Volume
  if vol>.01:res['intersections'].append({'a':a,'b':b,'mm3':vol})
  (out/'geometry_progress.json').write_text(json.dumps(res,indent=2))
 print('CHECKED',i,flush=True) if i%60==0 else None
for side,sg in [('PosY',1),('NegY',-1)]:
 xy=np.array(meshes['Wing_Skin_'+side]['v'])[:,:2];wing=MultiPoint(xy).convex_hull
 for tag,x in [('Front',170),('Rear',600)]:
  disk=Point(x,sg*265).buffer(127,resolution=256)
  res['plan_clearance_mm'][tag+'_'+side]=wing.distance(disk)
  res['plan_clearance_mm'][tag+'_'+side+'_overlap_mm2']=wing.intersection(disk).area
 # Exact cylinder axes retain required tail angle and straight joiner.
for n in ['Joiner_OD8_ID6_L200','VTail_PosY_AntiRotation_Pin_D3','VTail_NegY_AntiRotation_Pin_D3']:
 axes=[list(f.Surface.Axis) for f in p[n].Shape.Faces if isinstance(f.Surface,Part.Cylinder)]
 res[n+'_axes']=axes
res['status']='PASS targeted static geometry' if not res['intersections'] and not res['invalid_shapes'] else 'OPEN: inspect reported interference before release'
(out/'geometry_checks.json').write_text(json.dumps(res,indent=2));(out/'review_mesh.json').write_text(json.dumps(meshes))
print(json.dumps(res,indent=2),flush=True)
