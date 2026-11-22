import sys, json, pickle, glob, math, cadquery as cq, lg, ctx
from cadquery import Vector as V
names=[n.split('/')[-1] for n in pickle.load(open('../orig/names.pkl','rb'))]
def S(n): return cq.Shape.importBrep(f'../orig/{names.index(n):03d}.brep')
TILT=0.4; L_T=json.load(open('out_deployed/meta.json'))['L_T']
def T_T(s): return s.rotate(V(0,0,0),V(0,0,1),180).rotate(V(0,0,0),V(0,1,0),-TILT).translate(V(*lg.P_T))
CTX={}
for n in ['ESC_Deck_GFRP_Fuselage','ESC_Pads_Foam_Fuselage','REF_ESC_AIR40A_x4_Fuselage','Frames_Lower_and_Battery_Saddles_GFRP_Fuselage',
          'Frames_Ring_GFRP_Fuselage','REF_VTail_Servos_Fuselage','VTail_Root_Block_PA-CF_Fuselage','Hatch_Rims_GFRP_Fuselage','Hatch_Tail_GFRP_Fuselage']:
    CTX[n]=S(n)
for f in glob.glob('out_deployed/MOD__Fus*.brep'): CTX[f.split('MOD__')[1][:-5]]=cq.Shape.importBrep(f)
crop=lg.box(530,1000,-50,50,-60,40)
CTX={k:v.intersect(crop) for k,v in CTX.items()}
CTX={k:v for k,v in CTX.items() if v.Volume()>0.001}
FIX={f.split('/')[-1][:-5]:cq.Shape.importBrep(f) for f in glob.glob('out_deployed/*_LG_Tail.brep') if 'Fixed' in json.load(open('out_deployed/meta.json'))['parts'][f.split('/')[-1][:-5]][1]}
mode=sys.argv[1]
if mode=='fixed':
    for a,s in FIX.items():
        for b,c in CTX.items():
            v=ctx.ov(s,c)
            if v>0.01: print('FIXED',a,b,round(v,3),flush=True)
    ks=list(FIX)
    for i in range(len(ks)):
        for j in range(i+1,len(ks)):
            v=ctx.ov(FIX[ks[i]],FIX[ks[j]])
            if v>0.01: print('FIXEDFIXED',ks[i],ks[j],round(v,3),flush=True)
    print('done'); sys.exit()
ALL=dict(CTX); ALL.update(FIX)
for psi in [float(a) for a in sys.argv[2:]]:
    m,d,th=lg.moving_parts(psi,L_T); out=[]
    for k,s in m.items():
        s=T_T(s)
        for b,c in ALL.items():
            v=ctx.ov(s,c)
            if v>0.01: out.append((k,b,round(v,3)))
    print(psi,round(th,1),out,flush=True)
