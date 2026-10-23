"""CAD volume/fit evidence, including explicit unclosed interfaces."""
import json,sys,math,hashlib
from pathlib import Path
import FreeCAD as A,Part
R=Path(__file__).resolve().parents[1]
s=json.loads((R/'data/cad_snapshot_p04.json').read_text())
d=A.openDocument(str(R/'cad'/s['source_file']))
parts=[d.getObject(r['name']) for r in s['structural_parts']]
new=[o for o in parts if hasattr(o,'AttachmentGroup')]
refs=[o for o in d.Objects if o.Name.startswith('REF_')]
def overlap_bbox(a,b):
 aa=a.Shape.BoundBox;bb=b.Shape.BoundBox
 return all(min(getattr(aa,k+'Max'),getattr(bb,k+'Max'))-max(getattr(aa,k+'Min'),getattr(bb,k+'Min'))>1e-5 for k in 'XYZ')
intersections=[]
for i,o in enumerate(new):
 print('Audit',o.Name,flush=True)
 for other in [q for q in parts if q not in new]+new[:i]+refs:
  # Existing cores were explicitly cut by every insert in build_attachments.
  # Their volume loss is recorded; avoid re-solving the same costly spline cut.
  if 'Ravatherm_Core' in other.Name:continue
  if overlap_bbox(o,other):
   v=o.Shape.common(other.Shape).Volume
   if v>1e-4:intersections.append(dict(part=o.Name,other=other.Name,volume_mm3=v,kind='equipment envelope' if other in refs else 'structural overlap'))
step=Part.Shape();step.read(str(R/'cad'/'RescU_P04_Structure.step'))
result=dict(native_valid=all(p.Shape.isValid() for p in parts),step_valid=step.isValid(),step_solids=len(step.Solids),native_solids=sum(len(p.Shape.Solids) for p in parts),step_volume_mm3=step.Volume,native_sum_volume_mm3=sum(p.Shape.Volume for p in parts),interferences=intersections,status='Candidate audit; overlaps and absent bond/fastener detail prevent fabrication release')
connections=[]
for aa,bb in [('WingCenterBox','WingCenterSideWeb_1'),('WingCenterSideWeb_1','WingRootCaps_PosY'),('PusherFirewall','PusherTie_20_0'),('PusherTie_20_0','PusherForwardFrame'),('BatteryTray_Front','BatteryCradle_Front_206')]:
 a=d.getObject(aa);b=d.getObject(bb)
 connections.append(dict(part=aa,other=bb,gap_mm=a.Shape.distToShape(b.Shape)[0],note='Zero distance is geometry contact only, not bond/load-path qualification'))
result['selected_interface_distances']=connections
result['native_sha256']=hashlib.sha256((R/'cad'/s['source_file']).read_bytes()).hexdigest()
rho={r['name']:r['density_kg_m3'] for r in s['structural_parts']}
result['pairwise_duplicate_material_upper_bound_g']=sum(x['volume_mm3']*min(rho[x['part']],rho[x['other']])*1e-6 for x in intersections if x['kind']=='structural overlap')
result['duplicate_bound_note']='Pairwise upper bound for new-part overlaps if denser material retained; triple intersections can be counted repeatedly. Not an installed-mass correction or design approval. Preexisting P03/P03 overlaps not audited here.'
result['step_volume_relative_difference']=abs(step.Volume-result['native_sum_volume_mm3'])/result['native_sum_volume_mm3']
result['roundtrip_screen_pass']=bool(result['native_valid'] and result['step_valid'] and result['native_solids']==result['step_solids'] and result['step_volume_relative_difference']<1e-6)
(R/'reports/native-audit/candidate_audit.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
