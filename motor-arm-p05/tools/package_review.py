"""Package the candidate and audited dependencies, excluding backups/caches."""
from pathlib import Path
import json,zipfile,hashlib
R=Path(__file__).resolve().parents[1]
with zipfile.ZipFile(R/'cad/RescU_P05_CAD.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name in ['RescU_P05_Motor_Arm_Assembly.FCStd','RescU_P05_Motor_Arm_Pair.step','Open_Motor_Arm.FCMacro','Mount_Plates_Review.svg']:z.write(R/'cad'/name,name)
p=R/'cad/ARTIFACT_MANIFEST.json';j=json.loads(p.read_text());b=R/'cad/RescU_P05_CAD.zip';j['files']=[x for x in j['files'] if x['path']!='cad/RescU_P05_CAD.zip'];j['files'].append(dict(path='cad/RescU_P05_CAD.zip',size_bytes=b.stat().st_size,sha256=hashlib.sha256(b.read_bytes()).hexdigest()));p.write_text(json.dumps(j,indent=2))
files=[p for p in R.rglob('*') if p.is_file() and p.suffix.lower() in ['.md','.py','.json','.csv','.html','.fcmacro','.svg','.png','.fcstd','.step','.dat'] and '__pycache__' not in p.parts and p.name not in ['publish_files.json','repo_README.md']]
with zipfile.ZipFile(R/'RescU_P05_Review_Package.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,p.relative_to(R).as_posix())
 z.write(b,b.relative_to(R).as_posix())
with zipfile.ZipFile(R/'RescU_P05_Review_Package.zip') as z:
 assert z.testzip() is None
 for row in j['files']:assert hashlib.sha256(z.read(row['path'])).hexdigest()==row['sha256'],row['path']
publish=[p.relative_to(R).as_posix() for p in files if 'baseline-p04' not in p.parts and p.suffix.lower() not in ['.png','.fcstd','.step']]
(R/'publish_files.json').write_text(json.dumps(publish))
print('ZIP CRC and all manifest hashes PASS. Review package bytes:',(R/'RescU_P05_Review_Package.zip').stat().st_size,'CAD ZIP bytes:',b.stat().st_size)
