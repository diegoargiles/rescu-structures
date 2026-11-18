import cadquery as cq, numpy as np, sys
from cadquery import Vector as V
sys.path.insert(0,'.'); from cove import build, XC, ZTOP
def dz(z, add=0.0):
    return np.interp(z, [-60,-45,-38,-30,-22,-15,40], [4.5,4.5,6.5,9.5,12.0,13.5,13.5]) + add
def kvar(add=0.0, zclip=6.0):
    f=build()
    w0=f.outerWire(); n=int(w0.Length()/0.02)
    P=np.array([w0.positionAt(t).toTuple() for t in np.linspace(0,1,n,endpoint=False)])[:,[0,2]]
    # order: ensure contiguous loop; compute normals
    T=np.roll(P,-1,0)-np.roll(P,1,0); Nn=np.c_[T[:,1],-T[:,0]]; Nn/=np.linalg.norm(Nn,axis=1)[:,None]
    # orient outward: test midpoint + small step not inside face
    test=P[len(P)//3]+0.3*Nn[len(P)//3]
    from OCP.BRepClass import BRepClass_FaceClassifier
    from OCP.gp import gp_Pnt
    from OCP.TopAbs import TopAbs_IN
    i=np.argmax(P[:,0]*(P[:,1]>-30)*(P[:,1]<-10)); test=P[i]+0.3*Nn[i]
    inside = BRepClass_FaceClassifier(f.wrapped, gp_Pnt(test[0],0,test[1]), 1e-6).State()==TopAbs_IN
    Q=P+Nn*dz(P[:,1],add)[:,None]
    if inside: Q=P-Nn*dz(P[:,1],add)[:,None]
    Q=Q[(Q[:,0]>0.5)&(P[:,0]>0.5)]
    Q=Q[Q[:,1]<=zclip]
    # rebuild: from axis at bottom up the outer offset curve to clip height, then back along axis
    Q=Q[np.argsort(Q[:,1])]
    # keep monotone envelope: for each z keep max r
    zz=np.round(Q[:,1]/0.2)*0.2; env={}
    for (r,z0) in zip(Q[:,0],zz): env[z0]=max(env.get(z0,0),r)
    Z=np.array(sorted(env)); Rr=np.array([env[z] for z in Z])
    Rr=np.maximum.reduce([np.roll(Rr,1),Rr,np.roll(Rr,-1)]); Rr[0]=env[Z[0]]; Rr[-1]=env[Z[-1]]
    Z=Z[::2]; Rr=Rr[::2]
    zb=Z[0]; zt=min(zclip,Z[-1])
    # decimate to ~1 mm and smooth lightly, keep outside: take max over window
    k=max(1,int(1.0/0.4)); Zd=Z[::k]; Rd=np.array([Rr[max(0,i-k):i+k+1].max() for i in range(0,len(Rr),k)])
    Rd=Rd+0.2
    sp=cq.Edge.makeSpline([V(r,0,z) for r,z in zip(Rd,Zd)])
    a=sp.startPoint(); b=sp.endPoint()
    w=cq.Wire.assembleEdges([cq.Edge.makeLine(V(0,0,a.z),a), sp, cq.Edge.makeLine(b,V(0,0,b.z)), cq.Edge.makeLine(V(0,0,b.z),V(0,0,a.z))])
    S=cq.Solid.revolve(cq.Face.makeFromWires(w),360,V(0,0,0),V(0,0,1)).translate(V(XC,0,0))
    return S
if __name__=='__main__':
    K=cq.Shape.importBrep('K.brep')
    Kb=kvar(0,6.0).fuse(K).clean(); print('Kbig', Kb.isValid(), Kb.BoundingBox().xmin, Kb.BoundingBox().xmax)
    Kf=kvar(10.0,16.0).fuse(Kb).clean(); print('Kfl', Kf.isValid())
    R=np.load('tangent.npy'); bad=0
    for x,y,z,d in R:
        if not Kb.isInside(V(x,y,z),1e-3): bad+=1
    print('tangent points outside Kbig:', bad, 'of', len(R))
    Kb.exportBrep('Kbig.brep'); Kf.exportBrep('Kfl.brep')
