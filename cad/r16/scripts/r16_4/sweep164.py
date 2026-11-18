import cadquery as cq, numpy as np, glob, os, pickle
from scipy.spatial import cKDTree
import sys; sys.path.insert(0,'.'); from cove import XC, ZOFF, ZTOP
a=cq.importers.importStep('/home/claude/z30/Z30.step'); sols=a.solids().vals()
def pts(s,tol=0.2):
    v,t=s.tessellate(tol,0.2); V=np.array([[p.x,p.y,p.z] for p in v]); tri=V[np.array(t)]
    return np.vstack([V,tri.mean(1),(tri[:,0]+tri[:,1])/2,(tri[:,1]+tri[:,2])/2,(tri[:,0]+tri[:,2])/2])
fixed=np.vstack([pts(sols[i]) for i in (0,7,8)]); pitch=np.vstack([pts(sols[i]) for i in (1,2,3,4,5,6)])
allp=[fixed]
for a_ in np.radians(np.arange(-120,31,2.5)):
    y=pitch[:,1]-44.0; z=pitch[:,2]; allp.append(np.c_[pitch[:,0],y*np.cos(a_)+z*np.sin(a_)+44.0,-y*np.sin(a_)+z*np.cos(a_)])
P=np.vstack(allp); G=np.unique(np.round(np.c_[np.hypot(P[:,0]-0.5,P[:,1]-49.1), P[:,2]+ZOFF],1),axis=0); tree=cKDTree(G)
names=pickle.load(open('/home/claude/verify/orig/names.pkl','rb')); nm=[n.split('/')[-1] for n in names]
F={n:f'/home/claude/verify/orig/{i:03d}.brep' for i,n in enumerate(nm) if n in ('REF_Flight_Controller_Cube_Fuselage','Avionics_Deck_GFRP_Fuselage','Avionics_Adjust_Strips_Fuselage','Fuselage_Shell_Left_GFRP_Fuselage','Fuselage_Shell_Right_GFRP_Fuselage')}
for f in glob.glob('p164/*.brep'): F[os.path.basename(f)[:-5]]=f
for n,f in sorted(F.items()):
    s=cq.Shape.importBrep(f); Q=pts(s,0.05); Q=Q[(np.abs(Q[:,0]-XC)<100)]
    if 'Liner' in n or 'Shelf' in n or 'Mount' in n: Q=Q[Q[:,2]<ZTOP-0.2]   # mount face contact excluded
    if not len(Q): continue
    d,_=tree.query(np.c_[np.hypot(Q[:,0]-XC,Q[:,1]),Q[:,2]]); i=d.argmin()
    print(f'{n:42s} {d.min():6.2f} mm  at {np.round(Q[i],1)}')
