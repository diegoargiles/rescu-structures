import pickle, math, cadquery as cq
from cadquery import Vector as V
import lg
names=[n.split('/')[-1] for n in pickle.load(open('../orig/names.pkl','rb'))]
def S(n): return cq.Shape.importBrep(f'../orig/{names.index(n):03d}.brep')
SECS=pickle.load(open('boom_inner_R.pkl','rb')); XS=sorted(SECS)
BOOM_CTX=['Boom_Upper_Half_Boom_R','Compression_Tubes_Boom_R','Boom_Junction_Fillets_Boom_R','Motor_Backing_Rings_6061_Boom_R',
 'Motor_Screws_M3x10_Boom_R','Pad_Access_Covers_Boom_R','Saddle_Bolts_M3_and_Barrel_Nuts_Boom_R','Saddle_U_Channel_Boom_R','UM2807_Front_Boom_R']
def inside_boom(u,v,w):
    x,y,z=lg.P_R[0]+u, lg.P_R[1]+v, lg.P_R[2]+w
    if x<XS[0] or x>XS[-1]: return False
    pts=SECS[min(XS,key=lambda q:abs(q-x))]; n=len(pts); c=False
    for i in range(n):
        (y1,z1),(y2,z2)=pts[i],pts[(i+1)%n]
        if (z1>z)!=(z2>z) and y < (y2-y1)*(z-z1)/(z2-z1)+y1: c=not c
    return c
def boom_ctx(crop=True):
    P=V(*lg.P_R)
    c={n:S(n).translate(-P) for n in BOOM_CTX}
    c['Boom_Lower_Half_Boom_R']=S('Boom_Lower_Half_Boom_R').translate(-P).cut(lg.slot_cutter())
    if crop:
        bx=lg.box(-25,365,-12.6,12.6,-20,30); out={}
        for k,v in c.items():
            s=v.intersect(bx)
            if s.Volume()>0.001: out[k]=s
        c=out
    return c
def trim(part, shells, inside=inside_boom):
    for sh in shells: part=part.cut(sh)
    import random
    def frac(s):
        rnd=random.Random(1); b=s.BoundingBox(); pts=[]; n=0
        while len(pts)<12 and n<4000:
            n+=1; p=(rnd.uniform(b.xmin,b.xmax),rnd.uniform(b.ymin,b.ymax),rnd.uniform(b.zmin,b.zmax))
            if s.isInside(cq.Vector(*p)): pts.append(p)
        return sum(1 for p in pts if inside(*p))/max(1,len(pts))
    keep=[s for s in part.Solids() if frac(s)>0.5]
    return cq.Compound.makeCompound(keep) if len(keep)>1 else keep[0]
def ov(a,b):
    A,B=a.BoundingBox(),b.BoundingBox()
    if A.xmax<B.xmin or B.xmax<A.xmin or A.zmax<B.zmin or B.zmax<A.zmin or A.ymax<B.ymin or B.ymax<A.ymin: return 0
    return a.intersect(b).Volume()
