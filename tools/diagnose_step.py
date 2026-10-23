import json
from pathlib import Path
import FreeCAD as A,Part
R=Path(__file__).resolve().parents[1];d=A.openDocument(str(R/'cad/RescU_P04_Attachment_Study.FCStd'));s=json.loads((R/'data/cad_snapshot_p04.json').read_text());q=Part.Shape();q.read(str(R/'cad/RescU_P04_Structure.step'))
remaining=[(x,x.Volume) for x in q.Solids];bad=[]
for r in s['structural_parts']:
 for solid in d.getObject(r['name']).Shape.Solids:
  if not remaining:break
  volume=solid.Volume
  closest=min(remaining,key=lambda x:abs(x[1]-volume))
  err=abs(closest[1]-volume)/max(abs(volume),1e-6)
  if err<1e-6:remaining.remove(closest)
  else:bad.append(dict(name=r['name'],native_volume_mm3=solid.Volume))
report=dict(unmatched_native=bad,unmatched_step=[dict(volume_mm3=v,valid=x.isValid()) for x,v in remaining],invalid_step_solids=sum(not x.isValid() for x in q.Solids))
(R/'reports/native-audit/step_diagnostic.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
