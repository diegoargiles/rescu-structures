import cadquery as cq, json, math, sys, numpy as np
sys.path.insert(0,'/home/claude/rescu-structures/cad/r15/scripts')
from geom import *
from cadquery import Vector as Vv
import pickle, glob, os
names=pickle.load(open('/home/claude/verify4/orig/names.pkl','rb')); nm=[n.split('/')[-1] for n in names]
F={n:f'/home/claude/verify4/orig/{i:03d}.brep' for i,n in enumerate(nm)}
for f in glob.glob('out/*.brep'): F[os.path.basename(f)[:-5]]=f
L=lambda k: cq.Shape.importBrep(F[k])
a=math.radians(TDIH); e=np.array([0,math.cos(a),math.sin(a)])
d=np.array([0.4347,0,0])+e; d=d/np.linalg.norm(d)
mov=['VTail_Fixed_Skin_GFRP_VTail_R','VTail_Fixed_Core_XPS_VTail_R','VTail_Root_Diaphragm_GFRP_VTail_R','VTail_Spar_CFRP_VTail_R','VTail_AntiRotation_Pin_D3_VTail_R','VTail_Spar_Root_Plug_6061_VTail_R','VTail_Ruddervator_Skin_GFRP_VTail_R','VTail_Ruddervator_Core_XPS_VTail_R']
sta=['VTail_Root_Block_PA-CF_Fuselage','VTail_Root_Receivers_GFRP_Fuselage','Fuselage_Shell_Right_GFRP_Fuselage','Fuselage_Shell_Left_GFRP_Fuselage','VTail_Root_Fairings_ASA_Fuselage','Frames_Ring_GFRP_Fuselage','VTail_Retention_Inserts_M3_Brass_Fuselage','Hatch_Rims_GFRP_Fuselage']
M={k:L(k) for k in mov}; S={k:L(k) for k in sta}
res={}
print('V-tail R slide-out along spar axis d =', np.round(d,3))
for t in (0.0,2.0,6.0,15.0,30.0):
    tot=0; worst=None
    for mk,m in M.items():
        mm=m.translate(Vv(*(d*t)))
        for sk,s in S.items():
            bb1,bb2=mm.BoundingBox(),s.BoundingBox()
            if max(bb2.xmin-bb1.xmax,bb1.xmin-bb2.xmax,bb2.ymin-bb1.ymax,bb1.ymin-bb2.ymax,bb2.zmin-bb1.zmax,bb1.zmin-bb2.zmax)>0.5: continue
            v=mm.intersect(s).Volume()
            if v>0.01: tot+=v; worst=(round(v,2),mk,sk) if worst is None or v>worst[0] else worst
    print(f'  t={t:5.1f} mm  overlap {tot:8.3f} mm3  worst {worst}', flush=True); res[f'vtail_slide_{t}']=[round(tot,3),worst]
# ruddervator deflection
def hpt(s): return np.array([txle(s)+HINGE_FRAC*tchord(s),0,0])+e*s
p0,p1=hpt(0),hpt(245); ax=p1-p0
R=[L('VTail_Ruddervator_Skin_GFRP_VTail_R'),L('VTail_Ruddervator_Core_XPS_VTail_R')]
ST=[S['VTail_Root_Fairings_ASA_Fuselage'],S['Fuselage_Shell_Right_GFRP_Fuselage'],L('VTail_Fixed_Skin_GFRP_VTail_R'),L('VTail_Fixed_Core_XPS_VTail_R')]
for ang in (-25,-15,15,25):
    tot=0
    for r in R:
        rr=r.rotate(Vv(*p0),Vv(*(p0+ax)),ang)
        for s in ST: tot+=max(0,rr.intersect(s).Volume())
    print(f'  ruddervator {ang:+d} deg: overlap {tot:.3f} mm3', flush=True); res[f'rudd_{ang}']=round(tot,3)
# wing R slide-out along +y
movw=[k for k in F if k.endswith('_Wing_R') and 'Retention_Screw' not in k]
staw=['Fuselage_Shell_Right_GFRP_Fuselage','Wing_Root_Fairings_ASA_Fuselage','Wing_Pin_Bushing_Pads_G10_Fuselage','Wing_Root_Side_Rails_GFRP_Fuselage','Wing_Joiner_CFRP_OD12_Fuselage','Joiner_Receiver_Sleeves_GFRP_Fuselage']
MW={k:L(k) for k in movw}; SW={k:L(k) for k in staw}
print('Wing R slide-out along +y')
for t in (0.0,2.0,6.0,15.0,40.0):
    tot=0; worst=None
    for mk,m in MW.items():
        mm=m.translate(Vv(0,t,0)); b1=mm.BoundingBox()
        if b1.ymin>60: continue
        for sk,s in SW.items():
            b2=s.BoundingBox()
            if max(b2.xmin-b1.xmax,b1.xmin-b2.xmax,b2.ymin-b1.ymax,b1.ymin-b2.ymax,b2.zmin-b1.zmax,b1.zmin-b2.zmax)>0.5: continue
            v=mm.intersect(s).Volume()
            if v>0.01: tot+=v; worst=(round(v,2),mk,sk) if worst is None or v>worst[0] else worst
    print(f'  t={t:5.1f} mm  overlap {tot:8.3f} mm3  worst {worst}', flush=True); res[f'wing_slide_{t}']=[round(tot,3),worst]
json.dump(res,open('motion165.json','w'),indent=1)
