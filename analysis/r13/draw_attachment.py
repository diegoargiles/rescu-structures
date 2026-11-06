from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
out=Path(__file__).resolve().parents[2]/'reports/connection_study'
fig,axs=plt.subplots(2,1,figsize=(11,8.5),gridspec_kw={'height_ratios':[1.25,1]})
ax=axs[0];ax.set_xlim(125,650);ax.set_ylim(-100,95);ax.axis('off')
ax.add_patch(Rectangle((150,-43.5),470,25,fc='#c7d4df',ec='#28475e'))
for x in [170,600]:
 ax.add_patch(Rectangle((x-12,-18.5),24,25,fc='#7d8d98'))
for x,l in [(335,'A'),(405,'B')]:
 ax.add_patch(Rectangle((x-16,-45),32,28,fc='none',ec='#267f6c',lw=2))
 ax.plot([x,x],[-17,-8],c='#267f6c',lw=4);ax.plot(x,-8,'ko',ms=4)
 ax.text(x if l=='A' else x+16,-58,f'{l}: X={x} mm',ha='center' if l=='A' else 'left',fontsize=10)
ax.annotate('',(600,65),(600,8),arrowprops={'arrowstyle':'->','color':'#b16428','lw':2})
ax.text(590,75,'Rear thrust = 26 N',ha='right',fontsize=11)
ax.text(170,25,'Front thrust = 0',ha='center',fontsize=11)
ax.annotate('',(335,50),(335,-8),arrowprops={'arrowstyle':'->','color':'#28475e','lw':2})
ax.annotate('',(405,-75),(405,-8),arrowprops={'arrowstyle':'->','color':'#28475e','lw':2})
ax.text(325,60,'72.43 N up',ha='right',fontsize=11)
ax.text(415,-85,'98.43 N down',ha='left',fontsize=11)
ax.text(385,87,'Forces ON BOOM | rear-only 26 N sensitivity case',ha='center',fontsize=12,weight='bold')
ax.text(385,-98,'Wing receives equal and opposite support forces. Support spacing = 70 mm.',ha='center',fontsize=10)
ax=axs[1];ax.set_xlim(-35,105);ax.set_ylim(-25,25);ax.set_aspect('equal');ax.axis('off')
for r,c in [(14,'#79af9d'),(12.65,'#e5b67e'),(12.5,'#708b9e'),(11.5,'white')]:ax.add_patch(Circle((0,0),r,fc=c,ec='#47515a',lw=.6))
ax.text(0,-20,'Socket section',ha='center',fontsize=10)
ax.text(25,17,'Boom: OD 25 / ID 23 mm',fontsize=11)
ax.text(25,9,'Socket: OD 28 / ID 25.3 mm',fontsize=11)
ax.text(25,1,'Radial adhesive gap: 0.15 mm',fontsize=11)
ax.text(25,-7,'R13 sleeve: 20 mm → R14 study: 32 mm',fontsize=11)
ax.text(25,-15,'Clevis ears and M3 hardware unchanged',fontsize=11)
fig.suptitle('RescU attachment study | annotated dimensions and free body',fontsize=15,weight='bold')
fig.text(.08,.025,'Schematic; not a manufacturing drawing. Provisional loads, nominal geometry, no strength acceptance.',fontsize=10)
fig.subplots_adjust(top=.91,bottom=.08,hspace=.22)
fig.savefig(out/'Attachment_Annotated.png',dpi=180)
