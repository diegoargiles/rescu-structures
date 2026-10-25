"""Run independent read-only mass or STEP stages against the saved P07 native.
Shares the canonical stage implementation with check_export_account.py.
"""
import sys,json,math,csv,hashlib,zipfile
from pathlib import Path
import FreeCAD as A,Part,Assembly
R=Path(__file__).resolve().parents[1];B=R.parent;W=B/'v4-attachments' if (B/'v4-attachments').exists() else B
sys.path.insert(0,str(W));import RescU_Structures_V4 as engine
g=json.loads((R/'reports/build.json').read_text());d=A.openDocument(str(R/'cad/RescU_P07_Wing_Arm_Integration.FCStd'))
def gs(o):
 s=o.Shape.copy();s.Placement=o.getGlobalPlacement()*o.Placement.inverse()*s.Placement;s.tessellate(.3);return s.Solids[0] if len(s.Solids)==1 else s
names=g['old_physical_names']+[r['name'] for r in g['new_components']]
shapes={n:gs(d.getObject(n)) for n in names}
text=Path(__file__).with_name('check_export_account.py').read_text()
if sys.argv[1]=='mass':code=text[text.index('# Replace original quantities once.'):]
elif sys.argv[1]=='export':code=text[text.index('# Flatten global placements;'):text.index('# Replace original quantities once.')]
else:raise ValueError('Choose mass or export')
exec(compile(code,str(Path(__file__).with_name('check_export_account.py'))+' ['+sys.argv[1]+']','exec'))
