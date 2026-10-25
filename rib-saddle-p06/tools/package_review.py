"""Versioned P06 CAD ZIP plus full review package with sibling source refs."""
import json,hashlib,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
cadfiles=['RescU_P06_Rib_Saddle_Assembly.FCStd','RescU_P06_Arm_Pair.step','Open_Rib_Saddle.FCMacro']
with zipfile.ZipFile(R/'cad/RescU_P06_CAD.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name in cadfiles:z.write(R/'cad'/name,name)
manifest=dict(version='P06 rib-saddle splice candidate',status='GEOMETRY REVIEW; peel/fatigue and wing slot reinforcement open',files=[])
for name in [*['cad/'+n for n in cadfiles],'cad/RescU_P06_CAD.zip','cad/Rib_Saddle_Review.png','reports/geometry_checks.json','reports/results.json','reports/validation.json']:
 p=R/name;manifest['files'].append(dict(path=name,size_bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(R/'cad/ARTIFACT_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
own=[p for p in R.rglob('*') if p.is_file() and p.suffix.lower() in ['.py','.md','.html','.csv','.json','.fcmacro','.png','.fcstd','.step'] and '__pycache__' not in p.parts and p.name not in ['publish_files.json','repo_README.md'] and not p.name.endswith('_test.step')]
required={
 'motor-arm-p05':['cad/RescU_P05_Motor_Arm_Assembly.FCStd','reports/assembly_checks.json','reports/results.json','data/inputs_p05.json','data/accounting_snapshot_p05.json'],
 'v4-attachments':['cad/RescU_P04_Attachment_Study.FCStd','RescU_Structures_V4.py','attachment_checks.py','inputs.json','data/cad_snapshot_p04.json','reports/p04/results.json','engine/analytic_v3.py','engine/RescU_Structures_V2.py','engine/airfoils/sd7037.dat']}
target=R/'RescU_P06_Review_Package.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
 for p in own:z.write(p,'rib-saddle-p06/'+p.relative_to(R).as_posix())
 z.write(R/'cad/RescU_P06_CAD.zip','rib-saddle-p06/cad/RescU_P06_CAD.zip')
 for folder,paths in required.items():
  for name in paths:z.write((R.parent/folder if (R.parent/folder).exists() else R.parent)/name,folder+'/'+name)
 z.writestr('START_HERE.md','# P06 rib-to-saddle review\n\nOpen rib-saddle-p06/cad/RescU_P06_Rib_Saddle_Assembly.FCStd in FreeCAD1.1. Read rib-saddle-p06/reports/REVIEW.html and docs/CONNECTION_DESIGN.md. The other folders are read-only source references for reproducibility. Peel/fatigue and lower-wing slot reinforcement remain unresolved.\n')
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None
 for row in manifest['files']:assert hashlib.sha256(z.read('rib-saddle-p06/'+row['path'])).hexdigest()==row['sha256']
for folder,paths in required.items():
 if folder=='motor-arm-p05':
  a=json.loads((R.parent/folder/'reports/assembly_checks.json').read_text());assert hashlib.sha256((R.parent/folder/'cad/RescU_P05_Motor_Arm_Assembly.FCStd').read_bytes()).hexdigest()==a['native_sha256']
print(json.dumps(dict(review_package_bytes=target.stat().st_size,CAD_zip_bytes=(R/'cad/RescU_P06_CAD.zip').stat().st_size,CRC_and_hashes='PASS')))
publish=[p.relative_to(R).as_posix() for p in own if p.suffix.lower() not in ['.png','.fcstd','.step']]
(R/'publish_files.json').write_text(json.dumps(publish))
