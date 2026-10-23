"""Verified partial transfer: omit the inherited shell with failed STEP transfer."""
import json,hashlib
from pathlib import Path
import FreeCAD as A,Part
R=Path(__file__).resolve().parents[1];s=json.loads((R/'data/cad_snapshot_p04.json').read_text());d=A.openDocument(str(R/'cad'/s['source_file']))
objects=[d.getObject(r['name']) for r in s['structural_parts'] if r['name']!='Fuselage_GFRP_Shell_0330']
p=R/'cad/RescU_P04_PARTIAL_without_fuselage_shell.step';Part.export(objects,str(p));shape=Part.Shape();shape.read(str(p))
nv=sum(o.Shape.Volume for o in objects);sv=shape.Volume
result=dict(file=p.name,excluded=['Fuselage_GFRP_Shell_0330'],reason='Inherited native shell fails STEP transfer. NURBS conversion altered volume and was rejected.',valid=shape.isValid(),native_volume_mm3=nv,step_volume_mm3=sv,relative_volume_difference=abs(nv-sv)/nv,native_solids=sum(len(o.Shape.Solids) for o in objects),step_solids=len(shape.Solids),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),source_native_sha256=s['source_sha256'],status='PARTIAL export; native FCStd remains authoritative. No geometry-fit or structural qualification.')
result['roundtrip_screen_pass']=result['valid'] and result['native_solids']==result['step_solids'] and result['relative_volume_difference']<1e-3
(R/'reports/native-audit/partial_step_audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
