import cadquery as cq, pickle, os, json, numpy as np, time
import pyvista as pv
from scipy.spatial import cKDTree
from matplotlib.path import Path
W='/home/claude/work'; os.chdir(W)
names=pickle.load(open('verify2/names.pkl','rb')); nm=[n.split('/')[-1] for n in names]
S={n: f'verify2/{i:03d}.brep' for i,n in enumerate(nm)}
C={}
def sh(n):
    if n not in C: C[n]=cq.Shape.importBrep(S[n])
    return C[n]
PC={}
def mesh(n,tol=0.05):
    if (n,tol) not in PC:
        v,t=sh(n).tessellate(tol,0.15); v=np.array([p.toTuple() for p in v]); t=np.array(t)
        PC[(n,tol)]=(v,t)
    return PC[(n,tol)]
def pts(n,tol=0.05):
    v,t=mesh(n,tol); a,b,c=v[t[:,0]],v[t[:,1]],v[t[:,2]]
    return np.vstack([v]+[a+u*(b-a)+w*(c-a) for u,w in ((1/3,1/3),(.5,0),(0,.5),(.5,.5))])
def gap(a,b):
    A,B=sh(a).BoundingBox(),sh(b).BoundingBox()
    return max(B.xmin-A.xmax,A.xmin-B.xmax,B.ymin-A.ymax,A.ymin-B.ymax,B.zmin-A.zmax,A.zmin-B.zmax)
def inside_count(a,b):
    v,t=mesh(b); m=pv.PolyData(v,np.hstack([[3,*x] for x in t])).clean()
    return int(pv.PolyData(pts(a)).select_enclosed_points(m,tolerance=1e-6,check_surface=False)['SelectedPoints'].sum())
focus=[n for n in nm if any(k in n for k in ('Tarot','Motor_Screws_M3x4','Prop_Nut','Removable_Plate','Bonded_Collar','REF_Prop_Adapter','APC_13x8'))]+[n for n in nm if n.startswith('UM2807')]
res={}; t0=time.time(); done=set()
for a in focus:
    for b in nm:
        if a==b or (b,a) in done or gap(a,b)>2: continue
        done.add((a,b))
        d=float(cKDTree(pts(b)).query(pts(a))[0].min())
        ins = inside_count(a,b) if d<0.05 else 0
        res[f'{a} | {b}']=(round(d,3),ins); print(f'{time.time()-t0:5.0f}s', a,'|',b, round(d,3), 'pts inside', ins, flush=True)
# swept 13x8 envelope
pl=json.load(open('add2/placement.json'))
an='APC_13x8_LP13080P_Pusher_Prop_Fuselage'; o=np.array([pl['X_PROP'],0,0.]); ax=np.array([1,0,0.])
P=pts(an,0.1)-o; z=P@ax; r=np.linalg.norm(P-np.outer(z,ax),axis=1)
env=[]
for b0 in np.arange(0,r.max()+1,1.0):
    k=(r>=b0)&(r<b0+1)
    if k.any(): env.append((min(b0+1,r.max()),z[k].min(),z[k].max()))
poly=np.array([(0,env[0][1])]+[(e[0],e[1]) for e in env]+[(e[0],e[2]) for e in env[::-1]]+[(0,env[0][2])])
sw=[]
for b in nm:
    if b in (an,'REF_Prop_Adapter_Pusher_Fuselage','Prop_Nut_1-4in_Bullet_Pusher_Fuselage'): continue
    B=sh(b).BoundingBox()
    if B.xmax<o[0]-120 or B.xmin>o[0]+120 or min(abs(B.ymin),abs(B.ymax),abs(B.zmin),abs(B.zmax))>300: continue
    Q=pts(b,0.3)-o; qz=Q@ax; qr=np.linalg.norm(Q-np.outer(qz,ax),axis=1); k=(qr<r.max()+120)&(np.abs(qz)<120)
    if not k.any(): continue
    Pq=np.c_[qr[k],qz[k]]
    if Path(poly).contains_points(Pq).any(): best=0.0
    else:
        best=np.inf
        for p0,p1 in zip(poly,np.roll(poly,-1,axis=0)):
            d=p1-p0; L=(d@d) or 1e-12; tt=np.clip(((Pq-p0)@d)/L,0,1); best=min(best,np.linalg.norm(Pq-(p0+np.outer(tt,d)),axis=1).min())
    sw.append((round(float(best),1),b))
sw.sort(); print('swept 13x8', sw[:6]); res['swept_13x8']=sw[:6]
json.dump(res,open('add2/clearance.json','w'),indent=1); print('done')
