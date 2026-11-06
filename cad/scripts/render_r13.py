import json,sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Circle
out=Path(sys.argv[1]);m=json.loads((out/'review_mesh.json').read_text())
fig,axs=plt.subplots(1,2,figsize=(16,8));fig.suptitle('RescU R13 | Preliminary CAD layout',fontsize=22,fontweight='bold')
def color(n):
 if 'Aft_Torque' in n or 'Aft_Spar_Bond' in n or 'Aft_Root' in n:return '#d77e35'
 if 'Round_Boom' in n:return '#334b60'
 if 'Bonded_Motor' in n or 'Bonded_Wing' in n:return '#55a389'
 if 'ESC' in n or 'AIR40A' in n:return '#c59d45'
 if 'AT2814' in n:return '#727b87'
 if 'Skin' in n or 'Shell' in n:return '#dbe2e6'
 return '#a3b2bd'
for ax,mode in zip(axs,['top','side']):
 polys=[];cols=[];depth=[]
 for n,z in m.items():
  if n.startswith('REFERENCE_') or 'VTail' in n or 'Pusher' in n or 'Generic' in n:continue
  pts=np.array(z['v']);fs=z['t']
  if mode=='side' and ('NegY' in n or 'Fuselage' in n or 'Shell' in n):continue
  keep=(n.startswith('R13_') or any(t in n for t in ['Wing_Skin','Rebuilt_Swept','AT2814','AIR40A','CFRP_motor_rib','Fuselage_Shell','Rear_AntiRotation']))
  if not keep:continue
  for f in fs:
   p=pts[f]
   if mode=='top':
    if p[:,0].max()>700:continue
    poly=np.column_stack([p[:,1],-p[:,0]]);dep=p[:,2].mean()
   else:
    if p[:,1].max()<40 or p[:,1].min()>430:continue
    poly=p[:,[0,2]];dep=p[:,1].mean()
   polys.append(poly);cols.append(color(n));depth.append(dep)
 order=np.argsort(depth)
 ax.add_collection(PolyCollection([polys[i] for i in order],facecolors=[cols[i] for i in order],edgecolors='none',alpha=.9))
 ax.autoscale_view();ax.set_aspect('equal');ax.axis('off')
 if mode=='top':
  for y in [-265,265]:
   for x in [170,600]:ax.add_patch(Circle((y,-x),127,facecolor='#6a9ec9',edgecolor='#30638c',alpha=.15))
  ax.set_xlim(-750,750);ax.set_ylim(-760,-20);ax.set_title('Plan view | 10-inch propeller envelopes',fontsize=13)
 else:
  ax.set_xlim(120,640);ax.set_ylim(-60,55);ax.set_title('Side projection | right wing and booms\nMotors lowered 6 mm from R12',fontsize=13)
fig.text(.04,.12,'Dark blue: round booms   Green: bonded sockets / motor pods   Orange: aft reinforcement   Gold: internal ESC provisions',fontsize=11)
fig.text(.04,.06,'Candidate dimensions and materials are provisional. Skins retained; hidden parts may obscure internal details.\nNot a structural or aerodynamic release. Review accompanying geometry checks and mass exclusions.',fontsize=11)
fig.savefig(out/'R13_Layout_Review.png',dpi=140,bbox_inches='tight')
