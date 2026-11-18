import cadquery as cq, sys, numpy as np
a = cq.importers.importStep(sys.argv[1]); sols=a.solids().vals()
def pts(s):
    v,t=s.tessellate(0.2,0.2); V=np.array([[p.x,p.y,p.z] for p in v]); tri=V[np.array(t)]
    return np.vstack([V,tri.mean(1),(tri[:,0]+tri[:,1])/2,(tri[:,1]+tri[:,2])/2,(tri[:,0]+tri[:,2])/2])
fixed=np.vstack([pts(sols[i]) for i in (0,7,8)])
pitch=np.vstack([pts(sols[i]) for i in (1,2,3,4,5,6)])
Y0,Z0=44.0,0.0
allp=[fixed]
for a_ in np.radians(np.arange(-120,31,5)):
    # pitch about X axis; lens faces -Y; positive=up means lens tilts up (+Z)
    y=pitch[:,1]-Y0; z=pitch[:,2]-Z0
    # rotate so -Y direction goes toward +Z for positive angle
    yn= y*np.cos(a_)+z*np.sin(a_); zn=-y*np.sin(a_)+z*np.cos(a_)
    allp.append(np.c_[pitch[:,0],yn+Y0,zn+Z0])
P=np.vstack(allp)
c=np.array([0.5,49.1]); r=np.hypot(P[:,0]-c[0],P[:,1]-c[1])
prof=[]
for z0 in np.arange(np.floor(P[:,2].min()),104,1.0):
    m=P[:,2]>=z0
    prof.append((z0, r[m].max()))
prof=np.array(prof); np.save('/home/claude/z30_profile.npy',prof)
print('zmin',P[:,2].min(),'zmax',P[:,2].max())
for z0,R in prof[::5]: print(f'{z0:6.0f} R_above {R:5.1f}')
