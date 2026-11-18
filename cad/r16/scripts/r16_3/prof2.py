import numpy as np, json
prof=np.load('/home/claude/z30_profile.npy'); zl=prof[:,0]; Ra=prof[:,1]
XC, ZOFF, C = 85.0, -90.0, 5.0
ZTOP = ZOFF + 103.36
def Rabove(z): return np.interp(z, zl, Ra, left=Ra[0], right=0.0)
def req(z): return np.where(z<ZTOP, Rabove(z-ZOFF-C)+C, 0.0)
for z in np.arange(-50,14,1): print(f'{z:4.0f} {float(req(z)):5.1f}', end=' |')
print()
def lcm(z, r):
    hull=[]
    for p in zip(z,r):
        while len(hull)>=2:
            (x1,y1),(x2,y2)=hull[-2],hull[-1]
            if (x2-x1)*(p[1]-y1)-(y2-y1)*(p[0]-x1) >= 0: hull.pop()
            else: break
        hull.append(p)
    return np.array(hull)
z=np.arange(-140,-5.0+1e-9,0.25); H=lcm(z,req(z))
print(H)
