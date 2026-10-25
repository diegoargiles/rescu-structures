"""Actual bounding-outline extensions; not a continuous-lap qualification."""
import json
from pathlib import Path
import FreeCAD as A,Assembly
R=Path(__file__).resolve().parents[1];g=json.loads((R/'reports/build.json').read_text());d=A.openDocument(str(R/'cad/RescU_P07_Wing_Arm_Integration.FCStd'))
def gs(o):
 q=o.Shape.copy();q.Placement=o.getGlobalPlacement()*o.Placement.inverse()*q.Placement;return q
out=[]
for slot in [o for o in d.Objects if o.Name.startswith('Slot_')]:
 rows=[r for r in g['new_components'] if r['name'].startswith('SlotDoubler_'+slot.Name)]
 if not rows:continue
 bb=gs(slot).optimalBoundingBox();bounds=[gs(d.getObject(r['name'])).optimalBoundingBox() for r in rows]
 out.append(dict(slot=slot.Name,glass_regions=len(rows),blank_expansion_assumption_mm=8.,bounding_outline_extensions_mm=dict(front=bb.XMin-min(b.XMin for b in bounds),rear=max(b.XMax for b in bounds)-bb.XMax,negative_y=bb.YMin-min(b.YMin for b in bounds),positive_y=max(b.YMax for b in bounds)-bb.YMax),status='Bounding outline only; reliefs and separate regions interrupt the perimeter. Continuous developed lap is not established.'))
(R/'reports/patch_extents.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
