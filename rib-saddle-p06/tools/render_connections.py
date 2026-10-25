"""Actual native solids: carrier view and transverse rear-joint section."""
import json
from pathlib import Path
import FreeCAD as A,Part,Assembly
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as PlotPath
from matplotlib.patches import PathPatch,Patch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
R=Path(__file__).resolve().parents[1];g=json.loads((R/'reports/geometry_checks.json').read_text());d=A.openDocument(str(R/'cad/RescU_P06_Rib_Saddle_Assembly.FCStd'))
def gs(o):
 s=o.Shape.copy();s.Placement=o.getGlobalPlacement()*o.Placement.inverse()*s.Placement;return s
def color(name):
 if name.startswith('SplicePlate'):return '#e6903c'
 if name.startswith('RibPackerBond') or name.startswith('PackerSpliceBond') or name.startswith('SaddleSpliceBond'):return '#e0c743'
 if name.startswith('RibPacker'):return '#38a79c'
 if name.startswith('CFRP'):return '#384b61'
 if 'Rib' in name:return '#acbdcc'
 return '#6c8fa3'
names=['CFRP_Arm_PosY','Wing_Spar_Saddle_PosY','Wing_Rear_Saddle_PosY','Wing_Spar_Rib1_PosY','Wing_Spar_Rib2_PosY']+[r['name'] for r in g['added_components'] if r['assembly']=='MotorArm_PosY']
fig=plt.figure(figsize=(15,8),facecolor='#f4f7fa');ax=fig.add_axes([.01,.22,.65,.69],projection='3d');section=fig.add_axes([.70,.22,.26,.69])
viewbox=Part.makeBox(96,50,50,A.Vector(334,240,-25));plane=Part.Face(Part.makePolygon([A.Vector(410,205,-60),A.Vector(410,325,-60),A.Vector(410,325,60),A.Vector(410,205,60),A.Vector(410,205,-60)]))
for name in names:
 s=gs(d.getObject(name));clipped=s.common(viewbox) if name.startswith('CFRP') else s
 vertices,tri=clipped.tessellate(.2);pts=[(v.x,v.y-265,v.z) for v in vertices]
 ax.add_collection3d(Poly3DCollection([[pts[i] for i in t] for t in tri],facecolors=color(name),edgecolors='#34485b',linewidths=.07,alpha=1))
 # Exact X410 section of actual geometry, then discretized curves for plotting.
 cross=s.common(plane)
 for f in cross.Faces:
  verts=[];codes=[]
  for wire in [f.OuterWire]+[w for w in f.Wires if not w.isSame(f.OuterWire)]:
   vv=wire.discretize(Deflection=.03)
   if len(vv)<3:continue
   points=[(v.y-265,v.z) for v in vv];verts+=points+[points[0]];codes += [PlotPath.MOVETO]+[PlotPath.LINETO]*(len(points)-1)+[PlotPath.CLOSEPOLY]
  if verts:section.add_patch(PathPatch(PlotPath(verts,codes),facecolor=color(name),edgecolor='#34485b',linewidth=.6))
ax.set(xlim=(333,431),ylim=(-23,23),zlim=(-24,22));ax.set_box_aspect((98,46,46));ax.view_init(23,-64);ax.set_axis_off();ax.set_title('Assembled carrier · actual P06 geometry',loc='left',fontsize=15,color='#213547',pad=0)
section.set(xlim=(-21,-12),ylim=(-23,16));section.set_aspect('equal');section.set_xlabel('Y relative to arm center (mm)');section.set_ylabel('Z (mm)');section.spines[['top','right']].set_visible(False);section.grid(alpha=.15);section.set_title('Rear joint section · X410',fontsize=13,color='#213547')
fig.text(.04,.95,'P06 · Rib-to-saddle bonded splice',fontsize=22,color='#213547',weight='bold')
fig.legend(handles=[Patch(color='#e6903c',label='2 mm front / 1.5 mm rear splice'),Patch(color='#38a79c',label='1.8 mm fitted packer'),Patch(color='#e0c743',label='0.2 mm bond layers'),Patch(color='#acbdcc',label='Existing rib'),Patch(color='#6c8fa3',label='Existing saddle')],loc='lower left',bbox_to_anchor=(.025,.12),ncol=3,frameon=False,fontsize=11)
fig.text(.04,.065,'Eight splice plates bridge the measured rib/saddle gaps. Spar relief and proposed lower-skin entry slots are modeled.',fontsize=12,color='#30495d')
fig.text(.04,.03,'Review candidate: average-shear/plate-strip screens only. Peel, fatigue and skin-slot reinforcement remain unresolved.',fontsize=11,color='#963f2c')
fig.savefig(R/'cad/Rib_Saddle_Review.png',dpi=150);plt.close(fig);print('Rendered carrier and actual transverse section')
