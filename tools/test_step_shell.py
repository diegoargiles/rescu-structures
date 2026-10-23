import json
from pathlib import Path
import FreeCAD as A,Part
R=Path(__file__).resolve().parents[1];d=A.openDocument(str(R/'cad/RescU_P04_Attachment_Study.FCStd'))
o=d.addObject('Part::Feature','STEP_Transfer_Shell');o.Shape=d.getObject('Fuselage_GFRP_Shell_0330').Shape.toNurbs()
out=R/'cad/diagnostics';out.mkdir(exist_ok=True);path=out/'NURBS_shell_test.step';Part.export([o],str(path))
q=Part.Shape();q.read(str(path))
result=dict(native_volume_mm3=o.Shape.Volume,imported_volume_mm3=q.Volume,valid=q.isValid(),relative_delta=abs(q.Volume-o.Shape.Volume)/o.Shape.Volume)
(R/'reports/native-audit/nurbs_shell_test.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
