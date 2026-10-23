import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
R=Path(__file__).resolve().parents[1];items=json.loads((R/'cad/preview_mesh.json').read_text())
fig,ax=plt.subplots(figsize=(10,12),facecolor='white')
for item in items:
 pts=item['points'];tris=[[[pts[i][0],pts[i][1]] for i in f] for f in item['faces']]
 ax.add_collection(PolyCollection(tris,facecolor='#dd8a37' if item['new'] else '#506477',edgecolor='none'))
ax.set(xlim=(170,1140),ylim=(-720,720),xlabel='X from nose (mm)',ylabel='Y lateral (mm)')
ax.set_aspect('equal','box');ax.grid(alpha=.2);ax.set_axisbelow(True)
for label,xy,at in [('Lift motor shoes',(555,265),(650,380)),('Arm saddles / ribs',(410,265),(650,270)),('Wing center / root',(335,100),(550,110)),('Battery trays',(235,0),(550,-110)),('Tail root laminates',(1010,45),(770,190)),('Pusher support',(1080,0),(830,-190))]:
 ax.annotate(label,xy=xy,xytext=at,fontsize=9,arrowprops=dict(arrowstyle='-',color='#666666',lw=.8),color='#303030')
fig.suptitle('RescU P04 attachment study — plan view',fontsize=16)
fig.subplots_adjust(bottom=.13,top=.94)
fig.text(.06,.045,'Orange: proposed attachments  |  Blue: retained spars and arms\nSkins, equipment and foam hidden. Source: generated P04 CAD, 22 Oct 2026.\nCandidate geometry; not a fabrication release.',fontsize=10)
fig.savefig(R/'cad/Attachment_Study_Preview.png',dpi=170,bbox_inches='tight');plt.close(fig)
