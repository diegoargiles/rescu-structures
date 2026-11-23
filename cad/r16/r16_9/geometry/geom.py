import sys, json, math, numpy as np, cadquery as cq
sys.path.insert(0,'/home/claude/work/fdr'); from vr import shape, NAMES
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.gp import gp_Pln, gp_Pnt, gp_Dir
def section_pts(s, p, n):
    sec=BRepAlgoAPI_Section(s.wrapped, gp_Pln(gp_Pnt(*p), gp_Dir(*n))); sec.Build()
    sh=cq.Shape.cast(sec.Shape())
    pts=[]
    for e in sh.Edges():
        for t in np.linspace(0,1,400): pts.append(e.positionAt(t).toTuple())
    return np.array(pts)
out={}
# wing (right panel): skin + ruddervator-free
wing=shape('Wing_Skin_GFRP_Wing_R')
rows=[]
for y in [46,60,100,150,200,265,300,400,500,600,650,690,699]:
    P=section_pts(wing,(0,y,0),(0,1,0))
    if len(P)==0: continue
    i0=P[:,0].argmin(); i1=P[:,0].argmax()
    le=P[i0]; te=P[i1]; c=te[0]-le[0]
    inc=math.degrees(math.atan2(le[2]-te[2], c))
    rows.append(dict(y=y, x_le=round(le[0],2), z_le=round(le[2],2), x_te=round(te[0],2), z_te=round(te[2],2), chord=round(c,2), incidence_deg=round(inc,2), t_max=round(P[:,2].max()-P[:,2].min(),2)))
out['wing_sections_R']=rows
for r in rows: print(r)
# vtail L panel: planes normal to span direction
d=np.array([0,-math.cos(math.radians(35)),math.sin(math.radians(35))])
fx=shape('VTail_Fixed_Skin_GFRP_VTail_L'); rv=shape('VTail_Ruddervator_Skin_GFRP_VTail_L')
vr=[]
root=np.array([1000,-22,14.0])
for s_ in [2,10,40,80,120,160,200,215,220]:
    p=root+d*s_
    A=section_pts(fx,tuple(p),tuple(d)); Bv=section_pts(rv,tuple(p),tuple(d))
    if len(A)==0: continue
    le=A[:,0].min(); hinge=A[:,0].max(); te=Bv[:,0].max() if len(Bv) else float('nan')
    vr.append(dict(s=s_, y=round(p[1],1), z=round(p[2],1), x_le=round(le,2), x_fixed_te=round(hinge,2), x_te=round(te,2), chord=round(te-le,2), ruddervator_chord=round(te-hinge,2)))
out['vtail_sections_L']=vr
for r in vr: print(r)
json.dump(out,open('sections.json','w'),indent=1)
