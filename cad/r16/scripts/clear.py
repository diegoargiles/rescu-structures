import sys; sys.path.insert(0,'/home/claude/r15pkg/scripts')
import numpy as np
from geom import *
def zin(x,y):
    return wing_zup(x,y)-WSKIN, wing_zlo(x,y)+WSKIN
def tube_clear(p0,p1,ro,ymin=46.0,n=60,m=48):
    p0,p1=np.array(p0,float),np.array(p1,float); d=p1-p0; L=np.linalg.norm(d); d/=L
    a=np.cross(d,[0,0,1]); a/=np.linalg.norm(a); b=np.cross(a,d)
    worst=(1e9,None)
    for t in np.linspace(0,L,n):
        c=p0+d*t
        for th in np.linspace(0,2*np.pi,m,endpoint=False):
            p=c+ro*(np.cos(th)*a+np.sin(th)*b)
            if abs(p[1])<ymin: continue
            zu,zl=zin(p[0],abs(p[1])); cl=min(zu-p[2],p[2]-zl)
            if cl<worst[0]: worst=(cl,tuple(np.round(p,1)))
    return worst
if __name__=='__main__':
    T={
     'joiner OD12 (310,z4.2) y46-100':((310,46,4.2),(310,100,4.2),6.0),
     'R15 joiner socket r7.3 y46-112':((310,46,4.2),(310,112,4.2),7.3),
     'R15 spar socket r6.4 y92-150':((spar_x(92),92,SPAR_Z),(spar_x(150),150,SPAR_Z),6.4),
     'spar OD10 y92-380':((spar_x(92),92,SPAR_Z),(spar_x(380),380,SPAR_Z),5.0),
     'spar OD8 y350-560':((spar_x(350),350,SPAR_Z),(spar_x(560),560,SPAR_Z),4.0),
     'spar OD6 y530-685':((spar_x(530),530,SPAR_Z),(spar_x(685),685,SPAR_Z),3.0),
     'spar sleeve r5.65 @265':((spar_x(244.5),244.5,SPAR_Z),(spar_x(285.5),285.5,SPAR_Z),5.65),
     'aft tube OD5':((385,85,AFT_Z),(427.9,415,AFT_Z),2.5),
     'aft collars r3.0 (worst at 410)':((aft_x(406),406,AFT_Z),(aft_x(414),414,AFT_Z),3.0),
     'aft root socket straight r2.5 y46-66 z3.0':((385,46,3.0),(385,66,3.0),2.5),
     'aft root socket angled r3.0':((385-0.13*19,85-19,AFT_Z),(385+0.13*12,85+12,AFT_Z),3.0),
     'conduit r3.0':((CONDUIT_X_ROOT,46,CONDUIT_Z),(CONDUIT_X,257.5,CONDUIT_Z),3.0),
    }
    for k,v in T.items(): print(f'{k:42s} min clearance {tube_clear(*v)[0]:6.2f} mm at {tube_clear(*v)[1]}')
