"""Render actual native geometry and dimensioned nominal plate profiles."""
import json,math
from pathlib import Path
import FreeCAD as A,Part,Assembly
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
R=Path(__file__).resolve().parents[1];r=json.loads((R/'reports/assembly_checks.json').read_text());d=A.openDocument(str(R/'cad/RescU_P05_Motor_Arm_Assembly.FCStd'))
colors={'CFRP':'#333f4c','GFRP':'#2d9e95','Epoxy':'#d9ad4a','Isolation liner':'#ce783b','Steel':'#aab6c4','Vendor motor':'#586c87'}
fig=plt.figure(figsize=(15,9),facecolor='#f4f7fa');ax=fig.add_axes([.02,.40,.96,.52],projection='3d');bx=fig.add_axes([.03,.03,.44,.40],projection='3d');cx=fig.add_axes([.52,.06,.43,.32]);cx.axis('off')
def surface(axis,row,offset=(0,0,0)):
 o=d.getObject(row['name']);s=o.Shape.copy();s.Placement=o.getGlobalPlacement()*o.Placement.inverse()*s.Placement
 vertices,tri=s.tessellate(.4);points=[(v.x+offset[0],v.y-265+offset[1],v.z+offset[2]) for v in vertices]
 mesh=Poly3DCollection([[points[i] for i in t] for t in tri],facecolor=colors[row['material']],edgecolor='#253444',linewidth=.08,alpha=1)
 axis.add_collection3d(mesh)
for row in r['components']:
 if row['assembly']=='MotorArm_PosY':surface(ax,row)
 if 'PosY_Front' in row['name']:surface(bx,row)
arm=next(x for x in r['components'] if x['name']=='CFRP_Arm_PosY');surface(bx,arm)
ax.set(xlim=(205,585),ylim=(-38,38),zlim=(-35,48));ax.set_box_aspect((380,76,83));ax.view_init(24,-62);ax.set_axis_off();ax.set_title('One constrained motor-arm assembly · actual native solids',loc='left',fontsize=14,color='#213547',pad=0)
bx.set(xlim=(208,264),ylim=(-34,34),zlim=(-37,48));bx.set_box_aspect((56,68,85));bx.view_init(23,-50);bx.set_axis_off();bx.set_title('Front mount detail',loc='left',fontsize=12,color='#213547')
cx.text(0,1,'P05 · UM2807 1700KV motor-arm study',fontsize=16,weight='bold',color='#213547',va='top')
cx.text(0,.79,'Motor: Ø35.4 × 20 mm body; 4 × M3 on Ø19 PCD\nMount: 3 mm upper plate, 4 mm lower strap\nArm: 350 × 30 × 20 mm, assumed 1 mm wall\nMotor mounting face: 11 mm above the arm\nNo drilling through the carbon tube',fontsize=12,linespacing=1.7,color='#30495d',va='top')
cx.text(0,.14,'Review candidate · screw depth, clamp preload and bonds unqualified\nColors identify physical materials; wiring/tool/prop gauges hidden.',fontsize=10,color='#8b3d2b',va='top')
fig.savefig(R/'cad/Motor_Arm_Review.png',dpi=150);plt.close(fig)
# Explicit 2D nominal manufacturing review profiles. Units mm, not print-to-scale.
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="900" viewBox="0 0 1400 900"><style>text{font-family:Arial;fill:#213547} .small{font-size:17px}.title{font-size:28px;font-weight:bold}.part{fill:#d5eee8;stroke:#1f645c;stroke-width:1.5}.hole{fill:white;stroke:#213547;stroke-width:.3}.dim{stroke:#607689;stroke-width:.25;fill:none}</style><rect width="1400" height="900" fill="#f6f8fb"/><text x="45" y="50" class="title">P05 motor mount · nominal fabrication review</text><text x="45" y="82" class="small">Dimensions in mm · proposed construction · NOT a manufacturing release · profiles shown at enlarged scale</text>']
scale=6
def circ(x,y,rr):return f'<circle cx="{x}" cy="{y}" r="{rr}" class="hole"/>'
svg.append('<text x="80" y="135" class="title">Upper plate · G10/glass epoxy · 3 thick</text><g transform="translate(285,380) scale(6,-6)"><circle r="22" class="part"/><rect x="-10" y="-30" width="20" height="60" class="part"/><circle r="22" fill="#d5eee8"/>')
for x,y in [(0,-24),(0,24)]+[(i*19/2/math.sqrt(2),j*19/2/math.sqrt(2)) for i in [-1,1] for j in [-1,1]]:svg.append(circ(x,y,1.7))
svg.append(circ(0,0,5));svg.append('<circle r="9.5" class="dim" stroke-dasharray="1,1"/><path d="M-26 0H26M0 -34V34" class="dim" stroke-dasharray="1,1"/></g>')
svg.append('<text x="80" y="605" class="small">Ø44 center; 20-wide ears; total Y length 60</text><text x="80" y="635" class="small">4 × Ø3.4 on Ø19 PCD, rotated 45°; center relief Ø10</text><text x="80" y="665" class="small">2 × Ø3.4 at X0, Y±24; edge distance 6 nominal</text><text x="80" y="695" class="small">Motor-hole centers X±6.717514, Y±6.717514</text>')
svg.append('<text x="760" y="135" class="title">Lower strap · 4 thick</text><g transform="translate(965,380) scale(6,-6)"><rect x="-12" y="-30" width="24" height="60" rx="3" class="part"/>')
svg.append(circ(0,-24,1.7)+circ(0,24,1.7));svg.append('<path d="M-16 0H16M0 -34V34" class="dim" stroke-dasharray="1,1"/></g>')
svg.append('<text x="760" y="605" class="small">24 × 60; corner radius 3; 2 × Ø3.4 at X0,Y±24</text><text x="760" y="635" class="small">Rails: 2 per mount, 28 × 4 × 7.6</text><text x="760" y="665" class="small">Rail bounds: X±14; Y[-15,-11] and [11,15]</text><text x="760" y="695" class="small">0.2 liner beneath rails; 0.2 adhesive above rails</text>')
svg.append('<text x="45" y="765" class="small">Motor screws: provisional M3×6 +0.5 washer → 2.5 insertion. Safe depth UNKNOWN; verify against actual motor.</text><text x="45" y="795" class="small">Clamp: 2 × M3×45 per mount, washers and locknuts. Preload and carbon crushing require test; no torque prescribed.</text><text x="45" y="825" class="small">Suggested fabrication target: hole centers ±0.10, profile ±0.20 mm; proposed, subject to fit/tolerance review.</text><text x="45" y="855" class="small">CNC/waterjet profiles need deburring, radiused/sealed laminate edges. Use native CAD for exact contours; this SVG is not CAM.</text></svg>')
(R/'cad/Mount_Plates_Review.svg').write_text(''.join(svg),encoding='utf-8')
print('Rendered actual assembly PNG and nominal dimension review SVG')
