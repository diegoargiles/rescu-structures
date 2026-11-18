import cadquery as cq, numpy as np, pickle, json, glob, os
from scipy.spatial import cKDTree
import sys; sys.path.insert(0,'.'); from cove import XC, ZOFF, ZTOP
a=cq.importers.importStep('/home/claude/z30/Z30.step'); sols=a.solids().vals()
def pts(s,tol=0.2):
    v,t=s.tessellate(tol,0.2); V=np.array([[p.x,p.y,p.z] for p in v]); tri=V[np.array(t)]
    return np.vstack([V,tri.mean(1),(tri[:,0]+tri[:,1])/2,(tri[:,1]+tri[:,2])/2,(tri[:,0]+tri[:,2])/2])
fixed=np.vstack([pts(sols[i]) for i in (0,7,8)]); pitch=np.vstack([pts(sols[i]) for i in (1,2,3,4,5,6)])
allp=[fixed]
for a_ in np.radians(np.arange(-120,31,2.5)):
    y=pitch[:,1]-44.0; z=pitch[:,2]; yn=y*np.cos(a_)+z*np.sin(a_); zn=-y*np.sin(a_)+z*np.cos(a_)
    allp.append(np.c_[pitch[:,0],yn+44.0,zn])
P=np.vstack(allp); G=np.c_[np.hypot(P[:,0]-0.5,P[:,1]-49.1), P[:,2]+ZOFF]
G=np.unique(np.round(G,1),axis=0); tree=cKDTree(G)
zb=np.round(G[:,1]*4)/4; Rs={}
for zz,rr in zip(zb,G[:,0]): Rs[zz]=max(Rs.get(zz,0),rr)
print('gimbal 2D pts', len(G), 'lowest air z (pitch down)', G[:,1].min())
names=pickle.load(open('orig/names.pkl','rb')); nm=[n.split('/')[-1] for n in names]
files={n:f'orig/{i:03d}.brep' for i,n in enumerate(nm)}
for f in glob.glob('new3/*.brep')+glob.glob('add3/*.brep'): files[os.path.basename(f)[:-5]]=f
files.pop('REF_Camera_AI_PROVISIONAL_Fuselage',None)
res=[]
for n,f in []:
    if n.startswith('REF_Z30'): continue
    s=cq.Shape.importBrep(f); b=s.BoundingBox()
    if b.xmin>XC+100 or b.xmax<XC-100 or b.zmin>ZTOP+5 or abs(b.ymin)>100 and abs(b.ymax)>100 and b.ymin*b.ymax>0: continue
    Q=pts(s,0.1); Q=Q[(np.abs(Q[:,0]-XC)<100)&(Q[:,2]<ZTOP+5)]
    if not len(Q): continue
    q=np.c_[np.hypot(Q[:,0]-XC,Q[:,1]),Q[:,2]]
    d,_=tree.query(q); i=d.argmin()
    zz=np.round(q[:,1]*4)/4; inside=np.array([r< Rs.get(z_,-1) for r,z_ in zip(q[:,0],zz)])
    res.append((round(float(d.min()),2), int(inside.sum()), n, [round(v,1) for v in Q[i]]))
res.sort()
for r in res: print(r)
json.dump(res,open('sweep_clearance.json','w'),indent=1)
s=cq.Shape.importBrep('add3/Nose_Shell_GFRP_Fuselage.brep'); Q=pts(s,0.05)
for lim in (ZTOP-0.5, ZTOP-3):
    k=Q[:,2]<lim; q=np.c_[np.hypot(Q[k,0]-XC,Q[k,1]),Q[k,2]]; d,_=tree.query(q); i=d.argmin()
    print('nose shell below z',round(lim,2),': min clearance', round(float(d.min()),2), 'at', np.round(Q[k][i],1))
