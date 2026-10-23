import json
from pathlib import Path
import FreeCAD as A
R=Path(__file__).resolve().parents[1]
d=A.openDocument(str(R/'cad/RescU_P04_Attachment_Study.FCStd'))
items=[]
for o in d.Objects:
 if not hasattr(o,'Shape') or o.Shape.isNull() or o.Name.startswith('REF_'):continue
 # Isolate new structure plus spar/arms; omit opaque skins for a legible layout.
 if not hasattr(o,'AttachmentGroup') and not any(t in o.Name for t in ['TaperedSpar','VTOL_Arm']):continue
 if hasattr(o,'Material') and o.Material=='Ravatherm XPS X H LB':continue
 pts,faces=o.Shape.tessellate(1.5)
 items.append(dict(name=o.Name,new=hasattr(o,'AttachmentGroup'),points=[[p.x,p.y,p.z] for p in pts],faces=faces))
(R/'cad/preview_mesh.json').write_text(json.dumps(items))
