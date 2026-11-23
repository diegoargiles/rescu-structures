import sys, pickle, json, cadquery as cq
sys.path.insert(0,'../gear'); import render as R
import matplotlib.pyplot as plt
from cadquery import Vector as V
n=[x.split('/')[-1] for x in pickle.load(open('rt/names.pkl','rb'))]
def pick(k):
    return not (k.endswith('_R') or '_Wing_R' in k or '_VTail_R' in k or 'Right' in k or 'LG_Front_R' in k or (k.startswith(('Wing_','VTail_')) and 'Skin' not in k) or k=='REF_M65A_Cells_6S2P_Fuselage')
def colr(k):
    if k.startswith('REF_Camera'): return (0.85,0.25,0.55)
    if k.startswith('REF_Battery'): return (0.17,0.45,0.85)
    if k.startswith('REF_VTail_Servos'): return (0.10,0.65,0.45)
    if k.startswith(('REF_Flight','REF_Receiver')): return (0.95,0.65,0.10)
    if k.startswith('REF_Payload'): return (0.95,0.45,0.20)
    if 'Shell' in k or 'Wing_Skin' in k or 'VTail_' in k: return R.C['gfrp']
    if 'Boom' in k: return R.C['cfrp']
    if '_LG_' in k: return R.col(k.split('_LG_')[0])
    return (0.75,0.75,0.72)
meta=json.load(open('../gear2/out_retracted/meta.json'))['parts']
def items(state):
    out=[]
    for i,k in enumerate(n):
        if not pick(k): continue
        if '_LG_' in k and state=='retracted':
            s=cq.Shape.importBrep(f'../gear2/out_retracted/{k}.brep')
            if '_LG_Front_' in k: s=s.translate(V(35,0,0))
        else: s=cq.Shape.importBrep(f'rt/{i:03d}.brep')
        out.append((s,colr(k),1.0))
    return out
for st,t in [('deployed','R16.9 — legs shortened to 181 mm: 150 mm ground clearance under the buoy plate'),('retracted','R16.9 — gear retracted: legs hidden inside the boom and belly')]:
    fig=plt.figure(figsize=(16,6.4),dpi=130); ax=fig.add_axes([0,0,1,0.92])
    R.draw(ax,items(st),view=(0,1,0)); ax.axhline(-206,color='0.55',lw=1.2)
    fig.suptitle(t,fontsize=15,x=0.02,ha='left'); fig.savefig(f'r169_side_{st}.png',facecolor='white'); plt.close(fig)
