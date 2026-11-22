import json, pickle, glob, cadquery as cq, lg, ctx
from cadquery import Vector as V
names=[n.split('/')[-1] for n in pickle.load(open('../orig/names.pkl','rb'))]
def S(n): return cq.Shape.importBrep(f'../orig/{names.index(n):03d}.brep')
def T_L(s): return s.mirror('XZ').translate(V(lg.P_R[0], -lg.P_R[1], lg.P_R[2]))
crop=lg.box(160,575,-280,-250,-50,5)
C={}
for n in ['Boom_Upper_Half_Boom_L','Motor_Backing_Rings_6061_Boom_L','Motor_Screws_M3x10_Boom_L','Pad_Access_Covers_Boom_L','UM2807_Front_Boom_L','Compression_Tubes_Boom_L','Saddle_Bolts_M3_and_Barrel_Nuts_Boom_L']:
    C[n]=S(n).intersect(crop)
C['Boom_Lower_Half_Boom_L']=cq.Shape.importBrep('out_deployed/MOD__Boom_Lower_Half_Boom_L.brep').intersect(crop)
meta=json.load(open('out_deployed/meta.json'))['parts']
F={n:cq.Shape.importBrep(f'out_deployed/{n}.brep') for n,(g,s) in meta.items() if s=='LG_Front_L_Fixed'}
for a,s in F.items():
    for b,c in C.items():
        v=ctx.ov(s,c)
        if v>0.01: print('FIXED',a,b,round(v,3))
ALL=dict(C); ALL.update(F)
for psi in [60,20,-20,-60]:
    m,d,th=lg.moving_parts(psi); out=[]
    for k,s in m.items():
        s=T_L(s)
        for b,c in ALL.items():
            v=ctx.ov(s,c)
            if v>0.01: out.append((k,b,round(v,3)))
    print(psi,out,flush=True)
