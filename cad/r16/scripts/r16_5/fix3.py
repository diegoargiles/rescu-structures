import cadquery as cq, math, sys, numpy as np, pickle
sys.path.insert(0,'/home/claude/rescu-structures/cad/r15/scripts')
from geom import *
from cadquery import Vector as Vv
names=[x.split('/')[-1] for x in pickle.load(open('/home/claude/verify4/orig/names.pkl','rb'))]
def O(k): return cq.Shape.importBrep(f'/home/claude/verify4/orig/{names.index(k):03d}.brep')
FW=fus_solid(-0.5,150,600).val()
for side in 'RL':
    d=O(f'Wing_Root_Diaphragm_GFRP_Wing_{side}').cut(FW); d.exportBrep(f'out/Wing_Root_Diaphragm_GFRP_Wing_{side}.brep'); print('diaphragm restored', side, round(d.Volume(),1))
a=math.radians(TDIH); k=1/math.tan(math.radians(63))
for side,sg in (('R',1),('L',-1)):
    e=np.array([0,sg*math.cos(a),math.sin(a)]); nrm=np.array([0,-sg*math.sin(a),math.cos(a)])
    def hpt(s): return np.array([txle(s)+HINGE_FRAC*tchord(s),0,0])+e*s
    p0,p1=hpt(-5),hpt(250); ax=(p1-p0)/np.linalg.norm(p1-p0)
    c=np.cross(nrm,ax); c=c/np.linalg.norm(c)
    if c[0]<0: c=-c
    n2=np.cross(ax,c)
    P=lambda u,v: Vv(*(p0+c*u+n2*v))
    pts=[P(0,0),P(6*k,6),P(-1,6),P(-1,-6),P(6*k,-6)]
    w=cq.Wire.makePolygon(pts,close=True)
    wedge=cq.Solid.extrudeLinear(cq.Face.makeFromWires(w),Vv(*(ax*np.linalg.norm(p1-p0))))
    fx=cq.Shape.importBrep(f'out/VTail_Fixed_Skin_GFRP_VTail_{side}.brep')
    for part in ('Skin_GFRP','Core_XPS'):
        kk=f'VTail_Ruddervator_{part}_VTail_{side}'; s=cq.Shape.importBrep(f'out/{kk}.brep'); s2=s.cut(wedge)
        s2=max(s2.Solids(),key=lambda q:q.Volume()) if s2.ShapeType()!='Solid' else s2
        print(kk, round(s.Volume(),1),'->',round(s2.Volume(),1), s2.isValid()); s2.exportBrep(f'out/{kk}.brep')
    if side=='R':
        R=[cq.Shape.importBrep(f'out/VTail_Ruddervator_{p}_VTail_R.brep') for p in ('Skin_GFRP','Core_XPS')]
        for th in (-25,25):
            v=sum(max(0,r.rotate(Vv(*p0),Vv(*p1),th).intersect(fx).Volume()) for r in R); print('  rudd',th,'vs fixed skin',round(v,3))
