import cadquery as cq, numpy as np, pickle, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.gp import gp_Pln, gp_Pnt, gp_Dir
n=[x.split('/')[-1] for x in pickle.load(open('/home/claude/verify5/orig/names.pkl','rb'))]
S=lambda k: cq.Shape.importBrep(f'/home/claude/verify5/orig/{n.index(k):03d}.brep')
def sec(shape,p,d):
    out=[]
    for so in shape.Solids():
        s=BRepAlgoAPI_Section(so.wrapped, gp_Pln(gp_Pnt(*p),gp_Dir(*d))); s.Build()
        for e in cq.Shape.cast(s.Shape()).Edges(): out.append(np.array([e.positionAt(t).toTuple() for t in np.linspace(0,1,30)]))
    return out
T={'Fuselage shell':(['Fuselage_Shell_Right_GFRP_Fuselage','Fuselage_Shell_Left_GFRP_Fuselage'],'#8A8A8A',1.4),
 'Ring frames':(['Frames_Ring_GFRP_Fuselage'],'#D29A2A',1.2),'Hatch + rims':(['Hatch_Tail_GFRP_Fuselage','Hatch_Rims_GFRP_Fuselage'],'#B0B0B0',1.2),
 'Root block (PA-CF, new)':(['VTail_Root_Block_PA-CF_Fuselage'],'#2E3136',2.0),'Receivers':(['VTail_Root_Receivers_GFRP_Fuselage'],'#D0505A',1.6),
 'Spars':(['VTail_Spar_CFRP_VTail_R','VTail_Spar_CFRP_VTail_L'],'#1C1D20',1.2),'Spar root plugs':(['VTail_Spar_Root_Plug_6061_VTail_R','VTail_Spar_Root_Plug_6061_VTail_L'],'#8E5BB5',1.2),
 'Retention screws + inserts':(['VTail_Retention_Screws_M3x20_ISO4762_Fuselage','VTail_Retention_Inserts_M3_Brass_Fuselage'],'#C9A227',1.6),
 'Anti-rotation pins':(['VTail_AntiRotation_Pin_D3_VTail_R','VTail_AntiRotation_Pin_D3_VTail_L'],'#3D7FC1',1.6),
 'Tail skins':(['VTail_Fixed_Skin_GFRP_VTail_R','VTail_Fixed_Skin_GFRP_VTail_L'],'#6FA8DC',1.2),'Root fairings (ASA, new)':(['VTail_Root_Fairings_ASA_Fuselage'],'#4C9F70',2.0)}
SH={k:([S(p) for p in v[0]],v[1],v[2]) for k,v in T.items()}
fig,ax=plt.subplots(1,3,figsize=(21,7.5))
for j,(x,ttl) in enumerate(((991.3,'x 991.3: spar receivers + retention screws'),(1022.0,'x 1022: anti-rotation pins'))):
    a=ax[j]
    for k,(shs,c,lw) in SH.items():
        first=True
        for s in shs:
            for E in sec(s,(x,0,0),(1,0,0)): a.plot(E[:,1],E[:,2],color=c,lw=lw,label=k if first else None); first=False
    a.set_aspect('equal'); a.set_xlim(-42,42); a.set_ylim(-20,40); a.grid(alpha=.3); a.set_title(ttl); a.set_xlabel('Y (mm)'); a.set_ylabel('Z (mm)')
ax[0].legend(fontsize=8,loc='lower left',ncol=2)
a=ax[2]
for k,(shs,c,lw) in SH.items():
    if k in ('Hatch + rims',): continue
    for s in shs:
        for E in sec(s,(0,0,6.0),(0,0,1)): a.plot(E[:,0],E[:,1],color=c,lw=lw)
a.set_xlim(960,1050); a.set_ylim(-32,32); a.set_aspect('equal'); a.grid(alpha=.3); a.set_title('Plan section at z 6'); a.set_xlabel('X (mm)'); a.set_ylabel('Y (mm)')
plt.suptitle('R16.5 V-tail root: printed root block holds receivers, pins and retention screws; panels slide out along the spar axis', fontsize=13)
plt.tight_layout(); plt.savefig('/home/claude/out165/render/r16_5_vtail_root_sections.png',dpi=95)
# wing
W={'Fuselage shell':(['Fuselage_Shell_Right_GFRP_Fuselage'],'#8A8A8A',1.4),'Wing skin':(['Wing_Skin_GFRP_Wing_R'],'#6FA8DC',1.2),
 'Root diaphragm':(['Wing_Root_Diaphragm_GFRP_Wing_R'],'#2E7D4F',1.2),'Root fairing (ASA, new)':(['Wing_Root_Fairings_ASA_Fuselage'],'#4C9F70',2.0),
 'Side rail':(['Wing_Root_Side_Rails_GFRP_Fuselage'],'#D29A2A',1.4),'Pin pad (G10, new)':(['Wing_Pin_Bushing_Pads_G10_Fuselage'],'#C9A227',2.0),
 'Anti-rotation pin':(['Wing_AntiRotation_Pin_D3_Wing_R'],'#3D7FC1',1.8),'Aft elbow':(['Wing_Aft_Elbow_CFRP_Wing_R'],'#1C1D20',1.2)}
SW={k:([S(p) for p in v[0]],v[1],v[2]) for k,v in W.items()}
fig,ax=plt.subplots(1,2,figsize=(17,7))
for j,(x,ttl) in enumerate(((340.0,'x 340: root fairing (R6) and 0.5 mm root gap'),(385.0,'x 385: anti-rotation pin through rail + G10 pad'))):
    a=ax[j]
    for k,(shs,c,lw) in SW.items():
        first=True
        for s in shs:
            for E in sec(s,(x,0,0),(1,0,0)): a.plot(E[:,1],E[:,2],color=c,lw=lw,label=k if first else None); first=False
    a.set_aspect('equal'); a.set_xlim(30,60); a.set_ylim(-12,20); a.grid(alpha=.3); a.set_title(ttl); a.set_xlabel('Y (mm)'); a.set_ylabel('Z (mm)')
ax[0].legend(fontsize=8,loc='lower right')
plt.suptitle('R16.5 main wing root (right side)', fontsize=13); plt.tight_layout(); plt.savefig('/home/claude/out165/render/r16_5_wing_root_sections.png',dpi=95)
