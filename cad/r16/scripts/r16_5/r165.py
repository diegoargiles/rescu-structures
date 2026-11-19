import sys, time, math, pickle, cadquery as cq, numpy as np
sys.path.insert(0,'/home/claude/rescu-structures/cad/r15/scripts')
from geom import *
import tail as T
from cadquery import Vector as Vv
t0=time.time()
names=[x.split('/')[-1] for x in pickle.load(open('/home/claude/verify4/orig/names.pkl','rb'))]
def O(k): return cq.Shape.importBrep(f'/home/claude/verify4/orig/{names.index(k):03d}.brep')
def sv(s,n):
    s.exportBrep(f'out/{n}.brep'); b=s.BoundingBox()
    print(f'{n:48s} ok {s.isValid()} n {len(s.Solids())} vol {s.Volume():9.1f} x {b.xmin:6.1f}..{b.xmax:6.1f} y {b.ymin:6.1f}..{b.ymax:6.1f} z {b.zmin:6.1f}..{b.zmax:6.1f} t{time.time()-t0:.0f}', flush=True)
def FS(off, x0=0.0, x1=FL): return fus_solid(off, x0, x1).val()
def B(x0,x1,y0,y1,z0,z1): return cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,Vv(x0,y0,z0))
def cyl(p0,p1,r): p0,p1=Vv(*p0),Vv(*p1); d=p1-p0; return cq.Solid.makeCylinder(r,d.Length,p0,d.normalized())
a=math.radians(TDIH)
def E(sg): return np.array([0, sg*math.cos(a), math.sin(a)])
def spt(sg,s): return np.array([txle(s)+0.30*tchord(s),0,0])+E(sg)*s
def ppt(sg,s): return np.array([TLE+0.60*TCR,0,0])+E(sg)*s
def mirror(s): return s.mirror('XZ')
def pnew(sg,s): return np.array([TLE+0.60*TCR,0,0])+(spt(sg,s)-spt(sg,0))
# ================= V-tail root block =================
X0,X1=983.0,1030.0
interior=FS(0.33,975,1035).intersect(B(X0,X1,-40,40,-40,40))
parts=[]
SCR={}
for sg in (1,-1):
    e=E(sg); n=np.array([0,-sg*math.sin(a),math.cos(a)])
    parts.append(cyl(spt(sg,0),spt(sg,28.5),7.2))
    parts.append(cyl(pnew(sg,9),pnew(sg,30),5.0))
    q=[spt(sg,2),spt(sg,28.5),pnew(sg,30),pnew(sg,9)]
    w=cq.Wire.makePolygon([Vv(*p) for p in q],close=True)
    web=cq.Solid.extrudeLinear(cq.Face.makeFromWires(w), Vv(*(n*4.0))).translate(Vv(*(-n*2.0)))
    parts.append(web)
    ps=spt(sg,10.0); SCR[sg]=ps
    parts.append(cyl((ps[0],ps[1],-7.0),(ps[0],ps[1],16.0),5.0))
parts.append(B(X0,986.0,-40,40,-14,40)); parts.append(B(1027.0,X1,-40,40,-14,40))
blk=parts[0]
for p in parts[1:]: blk=blk.fuse(p)
blk=blk.intersect(interior)
cut=[O('Frames_Ring_GFRP_Fuselage'),O('Hatch_Rims_GFRP_Fuselage'),O('Hatch_Tail_GFRP_Fuselage'),B(960,1050,-16.5,16.5,18,40)]
for sg in (1,-1):
    cut+= [cyl(spt(sg,3.0),spt(sg,32),4.2), cyl(pnew(sg,0),pnew(sg,40),1.55)]
    ps=SCR[sg]; cut+= [cyl((ps[0],ps[1],0.0),(ps[0],ps[1],30),1.7), cyl((ps[0],ps[1],-6.0),(ps[0],ps[1],0.2),2.0)]
for yy in (12,-12): cut.append(cyl((975,yy,-8),(1030,yy,-8),4.0))
for c in cut: blk=blk.cut(c)
blk=max(blk.Solids(),key=lambda s:s.Volume()) if blk.ShapeType()!='Solid' else blk
sv(blk,'VTail_Root_Block_PA-CF_Fuselage')
# receivers to the centre (s 3.5-27.5), screw holes
rec=None; ins=[]; scr=[]
for sg in (1,-1):
    ps=SCR[sg]
    r=cyl(spt(sg,3.5),spt(sg,27.5),4.2).cut(cyl(spt(sg,3.0),spt(sg,28),3.05)).cut(cyl((ps[0],ps[1],-10),(ps[0],ps[1],30),1.6))
    rec=r if rec is None else rec.fuse(r)
    ins.append(cyl((ps[0],ps[1],-5.7),(ps[0],ps[1],0.0),2.0).cut(cyl((ps[0],ps[1],-6),(ps[0],ps[1],1),1.25)))
    head=cyl((ps[0],ps[1],16.0),(ps[0],ps[1],19.0),2.75).cut(cq.Workplane('XY').polygon(6,2.5/math.cos(math.pi/6)).extrude(2.0).val().translate(Vv(ps[0],ps[1],17.0)))
    scr.append(head.fuse(cyl((ps[0],ps[1],-4.0),(ps[0],ps[1],16.0),1.5)))
sv(rec,'VTail_Root_Receivers_GFRP_Fuselage')
sv(cq.Compound.makeCompound(ins),'VTail_Retention_Inserts_M3_Brass_Fuselage')
sv(cq.Compound.makeCompound(scr),'VTail_Retention_Screws_M3x20_ISO4762_Fuselage')
for sg,side in ((1,'R'),(-1,'L')):
    ps=SCR[sg]; hole=cyl((ps[0],ps[1],-10),(ps[0],ps[1],30),1.6)
    sv(O(f'VTail_Spar_CFRP_VTail_{side}').cut(hole),f'VTail_Spar_CFRP_VTail_{side}')
    sv(cyl(spt(sg,4.5),spt(sg,15.0),2.15).cut(hole),f'VTail_Spar_Root_Plug_6061_VTail_{side}')
# ================= V-tail panel root gaps + diaphragm =================
F05,F10,F15=FS(-0.5,900,1130),FS(-1.0,900,1130),FS(-1.5,900,1130)
for sg,side in ((1,'R'),(-1,'L')):
    sv(O(f'VTail_Fixed_Skin_GFRP_VTail_{side}').cut(F05),f'VTail_Fixed_Skin_GFRP_VTail_{side}')
    sv(O(f'VTail_Fixed_Core_XPS_VTail_{side}').cut(F15),f'VTail_Fixed_Core_XPS_VTail_{side}')
    sv(O(f'VTail_Ruddervator_Skin_GFRP_VTail_{side}').cut(F10),f'VTail_Ruddervator_Skin_GFRP_VTail_{side}')
    sv(O(f'VTail_Ruddervator_Core_XPS_VTail_{side}').cut(F10),f'VTail_Ruddervator_Core_XPS_VTail_{side}')
    inner=T.loft(sg,'fixed',TSKIN).val()
    env=cyl(spt(sg,0),spt(sg,120),3.05).fuse(cyl(spt(sg,119),spt(sg,240),3.05))
    d=inner.intersect(F15.cut(F05)).cut(env).cut(cyl(pnew(sg,0),pnew(sg,42),1.6))
    core=cq.Shape.importBrep(f'out/VTail_Fixed_Core_XPS_VTail_{side}.brep')
    old=cyl(ppt(sg,0),ppt(sg,42),1.6).intersect(inner).cut(F15)
    core=core.fuse(old).cut(cyl(pnew(sg,0),pnew(sg,42),1.6))
    sv(core,f'VTail_Fixed_Core_XPS_VTail_{side}')
    sv(cyl(pnew(sg,6),pnew(sg,36),1.5),f'VTail_AntiRotation_Pin_D3_VTail_{side}')
    sv(d,f'VTail_Root_Diaphragm_GFRP_VTail_{side}')
# shells: fill the old (unswept) pin holes, drill the new ones parallel to the spar
band=FS(0,900,1110).cut(FS(0.33,900,1110))
for side in ('Right','Left'):
    sh=O(f'Fuselage_Shell_{side}_GFRP_Fuselage')
    for sg in (1,-1):
        sh=sh.fuse(cyl(ppt(sg,0),ppt(sg,45),1.6).intersect(band)).cut(cyl(pnew(sg,0),pnew(sg,45),1.6))
    keep=sh.Solids(); sh=max(keep,key=lambda q:q.Volume())
    sv(sh,f'Fuselage_Shell_{side}_GFRP_Fuselage')
# ================= V-tail fairings (printed, R3.5, 0.5 mm reveal to panel) =================
ft=cq.Shape.importBrep('p/fair_tail_gap.brep')
ftc=[ft.Solids()[0], mirror(ft).Solids()[0]]
tcut=[O('Hatch_Rims_GFRP_Fuselage'),O('Hatch_Tail_GFRP_Fuselage'),B(960,1050,-16.5,16.5,18,40)]
out=[]
for f in ftc:
    for c in tcut: f=f.cut(c)
    out+= [s for s in f.Solids() if s.Volume()>1]
sv(cq.Compound.makeCompound(out),'VTail_Root_Fairings_ASA_Fuselage')
# ================= wing root gaps, fairings, pin pads =================
FW=FS(-0.5,150,600)
for side in ('R','L'):
    sv(O(f'Wing_Skin_GFRP_Wing_{side}').cut(FW),f'Wing_Skin_GFRP_Wing_{side}')
    sv(O(f'Wing_Root_Diaphragm_GFRP_Wing_{side}').cut(FW),f'Wing_Root_Diaphragm_GFRP_Wing_{side}')
fw=cq.Shape.importBrep('p/fair_wing_R6.brep')
sv(cq.Compound.makeCompound(fw.Solids()+mirror(fw).Solids()),'Wing_Root_Fairings_ASA_Fuselage')
pad=B(378,392,36,40,-3,9).cut(cyl((385,30,3),(385,45,3),1.55))
sv(cq.Compound.makeCompound([pad, mirror(pad)]),'Wing_Pin_Bushing_Pads_G10_Fuselage')
pin=cyl((385,36.5,3),(385,63,3),1.5)
sv(pin,'Wing_AntiRotation_Pin_D3_Wing_R'); sv(mirror(pin),'Wing_AntiRotation_Pin_D3_Wing_L')
