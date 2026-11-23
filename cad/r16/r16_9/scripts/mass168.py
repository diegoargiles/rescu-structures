import json, pickle, cadquery as cq
ops=json.load(open('ops.json'))
N=[x.split('/')[-1] for x in pickle.load(open('rt166/names.pkl','rb'))]
def rho(n):
    if n.startswith(('REF_','UM2807','APC_','Tarot')): return 0          # equipment handled separately
    if '_LG_' in n:
        for k,v in [('Knuckle',2.81),('Knee_Shaft',7.85),('Fork_Pin',7.85),('Leg_Rod',1.6),('Foot',1.21),('Tendon',2.81),('Servo_Arm_Pin',7.85),('Servo_Arm',2.81),('Knee_Block',2.81),('Guide_Pin',7.85),('Guide_Tab',1.85),('Servo_Mount',1.85),('Trough',1.55),('Belly',1.55)]:
            if n.startswith(k): return v
    if 'Foam' in n: return 0.10
    if 'XPS' in n: return 0.032
    if any(k in n for k in ['Screw','Nutplate','Pin_D3','Bolts','Prop_Nut','Rod_Ends']): return 7.85
    if '6061' in n or 'Plate_6061' in n or 'Spar_Root_Plug' in n: return 2.7
    if 'PTFE' in n: return 2.2
    if 'ASA' in n or 'PA-CF' in n: return 1.07
    if 'Microballoon' in n or 'Fillets' in n: return 0.6
    if 'TPU' in n: return 0.45
    if 'Nylon' in n: return 1.15
    if 'Brass' in n: return 8.5
    if 'CFRP' in n or 'Boom_' in n or 'Saddle_U' in n or 'Pad_Access' in n: return 1.55
    return 1.85
def mx(s): 
    v=s.Volume(); c=cq.Shape.centerOfMass(s) if v>0 else s.Center(); return v,c.x
dm=dmx=0; moved_m=0
for n in ops['remove']+ops['replace']:
    v,x=mx(cq.Shape.importBrep(f'rt166/{N.index(n):03d}.brep')); m=v*rho(n)/1000; dm-=m; dmx-=m*x
for n in ops['replace']+ops['add']:
    v,x=mx(cq.Shape.importBrep(f'out/{n}.brep')); m=v*rho(n)/1000; dm+=m; dmx+=m*x
    if n in ops['moved_with_wing']: moved_m+=m
# gear servos are REF (mass 0 here) -> add as moved equipment
cam=cq.Shape.centerOfMass(cq.Shape.importBrep('out/REF_Camera_ELP_5MP_IR_USB_Fuselage.brep')).x
EQ=[('Z30',-270,86.5,0),('ELP (35 g assumed)',35,cam,0),('lift motors',208,0,35),('lift props',104.3,0,35),('gear servos front x2',19,0,35),('rear battery module',472,0,35),('ESCs + wiring',150,0,5)]
for name,m,x,d in EQ:
    if d==0: dm+=m; dmx+=m*x
    else: dmx+=m*d
M0,X0=3997.86,386.15
M=M0+dm; X=(M0*X0+dmx)/M
res={'mass_g':M,'cg_x':X,'struct_delta_g':dm-(-270+35),'moved_struct_g':moved_m,'moved_total_g_approx':moved_m+208+104.3+19+472}
json.dump(res,open('mass168.json','w'),indent=1); print(res)
