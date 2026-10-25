"""Actual P07 CAD geometry: wing context and enlarged carrier cutaway."""
import json
from pathlib import Path
import FreeCAD as A,Part,Assembly
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch,PathPatch
from matplotlib.path import Path as PlotPath
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
R=Path(__file__).resolve().parents[1]
if (R/'reports/build.json').exists():
 g=json.loads((R/'reports/build.json').read_text());d=A.openDocument(str(R/'cad/RescU_P07_Wing_Arm_Integration.FCStd'))
else:
 d=A.openDocument(str(R/'cad/P07_PosY_checkpoint.FCStd'))
 g=dict(old_physical_names=[o.Name for o in d.MotorArm_PosY.Group if hasattr(o,'Shape') and not o.Shape.isNull()],new_components=[])
def gs(o):
 s=o.Shape.copy();s.Placement=o.getGlobalPlacement()*o.Placement.inverse()*s.Placement;return s.Solids[0] if len(s.Solids)==1 else s
def color(n):
 if n.startswith(('Flange_','RibFaceTape_')):return '#df8c32'
 if n.startswith(('SparCheek_','SparCollar_')):return '#8062ae'
 if n.startswith('SlotDoubler_'):return '#45a58d'
 if 'Bond' in n or n.startswith('SlotEdgePotting_'):return '#d6b52e'
 if n.startswith(('WingSpar','CFRP_Arm')):return '#344c63'
 if 'Rib' in n:return '#88a9c0'
 if n.startswith(('SplicePlate','RibPacker')):return '#7f8d9b'
 return '#6b8194'
names=g['old_physical_names']+[r['name'] for r in g['new_components']]
context={}
if not d.getObject('WingSkin_PosY'):
 source=A.openDocument(str(R.parent/'v4-attachments/cad/RescU_P04_Attachment_Study.FCStd'))
 context['WingSkin_PosY']=source.Wing_PosY_GFRP_Skin_Exposed.Shape
 context['WingSpar_PosY']=source.Wing_PosY_CFRP_TaperedSpar.Shape
 names+=list(context)
local=Part.makeBox(110,76,55,A.Vector(330,227,-28))
fig=plt.figure(figsize=(15,8.6),facecolor='#fbfcfd')
ax=fig.add_axes([.015,.25,.58,.64],projection='3d');section=fig.add_axes([.65,.28,.32,.57])
plane=Part.Face(Part.makePolygon([A.Vector(330,250,-30),A.Vector(440,250,-30),A.Vector(440,250,25),A.Vector(330,250,25),A.Vector(330,250,-30)]))
for n in names:
 if 'PosY' not in n or n.startswith('WingCore_'):continue
 s=context[n] if n in context else gs(d.getObject(n));s.tessellate(.3);bounds=s.optimalBoundingBox()
 if not bounds.intersect(local.BoundBox):continue
 s=s.common(local)
 if n.startswith(('WingSkin_','WingOriginalBond_')):
  # Hide upper skin in the 3D cutaway only; leave the true section intact.
  visible=s.common(Part.makeBox(110,76,35,A.Vector(330,227,-28)))
  c='#bdc6cd';alpha=.16
 else:visible=s;c=color(n);alpha=1.
 if visible.Volume>1e-6:
  vv,tt=visible.tessellate(.18);pts=[(v.x,v.y-265,v.z) for v in vv]
  ax.add_collection3d(Poly3DCollection([[pts[i] for i in t] for t in tt],facecolor=c,edgecolor='#293c4c',linewidth=.045,alpha=alpha))
 cross=s.common(plane)
 for f in cross.Faces:
  v=[];codes=[]
  for wire in [f.OuterWire]+[q for q in f.Wires if not q.isSame(f.OuterWire)]:
   pp=wire.discretize(Deflection=.025)
   if len(pp)<3:continue
   p=[(q.x,q.z) for q in pp];v+=p+[p[0]];codes+=[PlotPath.MOVETO]+[PlotPath.LINETO]*(len(p)-1)+[PlotPath.CLOSEPOLY]
  if v:section.add_patch(PathPatch(PlotPath(v,codes),facecolor=c,edgecolor='#293c4c',linewidth=.35))
ax.set(xlim=(330,440),ylim=(-38,38),zlim=(-28,23));ax.set_box_aspect((110,76,51));ax.view_init(28,-62);ax.set_axis_off();ax.set_title('Actual CAD cutaway | foam and upper skin hidden',loc='left',fontsize=13,color='#263b4b')
section.set(xlim=(334,431),ylim=(-25,21));section.set_aspect('equal');section.set_xlabel('Aircraft X (mm)');section.set_ylabel('Aircraft Z (mm)');section.grid(alpha=.15);section.spines[['top','right']].set_visible(False);section.set_title('Actual section through rib | Y250 mm',fontsize=12,color='#263b4b')
fig.text(.04,.955,'P07 | Wing-to-arm integration candidate',fontsize=22,color='#263b4b',weight='bold')
fig.legend(handles=[Patch(color='#df8c32',label='Skin flanges / rib face tapes'),Patch(color='#8062ae',label='Open spar cheeks / collars'),Patch(color='#45a58d',label='Lower-skin slot doublers'),Patch(color='#d6b52e',label='Explicit adhesive layers'),Patch(color='#88a9c0',label='Revised local web pieces'),Patch(color='#344c63',label='Existing spar / arm')],loc='lower left',bbox_to_anchor=(.03,.105),ncol=3,frameon=False,fontsize=11)
fig.text(.04,.066,'Native wing and tapered spar geometry retained. New thicknesses, bond widths and installation allowances are proposals.',fontsize=11,color='#344c63')
fig.text(.04,.03,'Review geometry only: corner ply drape, adhesive peel, carbon load introduction and local wing stiffness remain unqualified.',fontsize=11,color='#8e4933')
fig.savefig(R/'cad/P07_Wing_Cutaway.png',dpi=150);plt.close(fig)
print('Rendered actual P07 solids')
