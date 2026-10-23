"""Deterministic P04 fit cleanup; retains original study as a local checkpoint."""
import json,hashlib,shutil
from pathlib import Path
import FreeCAD as A,Part
R=Path(__file__).resolve().parents[1];p=R/'data/cad_snapshot_p04.json';s=json.loads(p.read_text())
native=R/'cad'/s['source_file'];d=A.openDocument(str(native));V=A.Vector
shutil.copy2(native,R/'cad/RescU_P04_Unrefined_Checkpoint.FCStd')
# These stations move clear of the rear cell bank; fuselage diameter is constant
# at both old and new locations, so translation preserves the ring fit.
for name,dx in [('WingFrame_326',-7),('WingLocalFoam_321',-15),('WingLocalFoam_280',2)]:
 o=d.getObject(name);shape=o.Shape.copy();shape.translate(V(dx,0,0));o.Shape=shape
# Remove foam occupied by new dense parts. Never count both materials in a voxel.
new=[d.getObject(r['name']) for r in s['structural_parts'] if r.get('attachment_group')!='P03 retained structure']
changes=[]
for o in new:
 if o.Material!='Ravatherm XPS X H LB':continue
 for q in new:
  if q is o or q.Material=='Ravatherm XPS X H LB' or not o.Shape.BoundBox.intersect(q.Shape.BoundBox):continue
  prior=o.Shape.Volume;o.Shape=o.Shape.cut(q.Shape)
  if prior-o.Shape.Volume>1e-6:changes.append(dict(part=o.Name,other=q.Name,removed_mm3=prior-o.Shape.Volume))
for r in s['structural_parts']:
 o=d.getObject(r['name'])
 for typ,key,value in [('App::PropertyBool','StructuralPart',True),('App::PropertyString','Material',r['material']),('App::PropertyFloat','Density_kg_m3',r['density_kg_m3'])]:
  if key not in o.PropertiesList:o.addProperty(typ,key)
  setattr(o,key,value)
 shape=o.Shape;rho=r['density_kg_m3'];c=sum((q.CenterOfMass*q.Volume for q in shape.Solids),V())/shape.Volume;b=shape.BoundBox;I=[[0.]*3 for _ in range(3)]
 for q in shape.Solids:
  mat=q.MatrixOfInertia;dv=q.CenterOfMass-c;delta=[dv.x,dv.y,dv.z]
  for i in range(3):
   for j in range(3):I[i][j]+=(getattr(mat,'A'+str(i+1)+str(j+1))+q.Volume*((sum(x*x for x in delta) if i==j else 0)-delta[i]*delta[j]))*rho*1e-15
 r.update(volume_mm3=shape.Volume,mass_kg=shape.Volume*rho*1e-9,x_m=c.x/1000,y_m=c.y/1000,z_m=c.z/1000,valid=shape.isValid(),inertia_centroid_kgm2=I,bounds_mm=[b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax])
d.recompute();d.save();Part.export([d.getObject(r['name']) for r in s['structural_parts']],str(R/'cad/RescU_P04_Structure.step'))
s['source_sha256']=hashlib.sha256(native.read_bytes()).hexdigest();p.write_text(json.dumps(s,indent=2))
bpath=R/'reports/native-audit/build.json';build=json.loads(bpath.read_text());build['new_parts']=[r for r in s['structural_parts'] if r.get('attachment_group')!='P03 retained structure'];build['refinement_foam_cuts']=changes;bpath.write_text(json.dumps(build,indent=2))
(R/'reports/native-audit/refinement.json').write_text(json.dumps(dict(station_moves_mm={'WingFrame_326':-7,'WingLocalFoam_321':-15,'WingLocalFoam_280':2},foam_cuts=changes),indent=2))
print('Refined candidate; foam cut records',len(changes))
