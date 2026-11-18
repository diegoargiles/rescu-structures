from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
def tv(s, eps=1e-5):
    p=GProp_GProps(); BRepGProp.VolumeProperties_s(s.wrapped,p,eps,False); return p.Mass()
def tvc(s, eps=1e-5):
    p=GProp_GProps(); BRepGProp.VolumeProperties_s(s.wrapped,p,eps,False); c=p.CentreOfMass(); return p.Mass(), (c.X(),c.Y(),c.Z())
import numpy as np
def mv(s, tol=0.01):
    tot=0
    for so in s.Solids():
        v,t=so.tessellate(tol,0.1); v=np.array([x.toTuple() for x in v]); t=np.array(t)
        a,b,c=v[t[:,0]],v[t[:,1]],v[t[:,2]]; tot+=np.einsum('ij,ij->i',a,np.cross(b,c)).sum()/6
    return tot
