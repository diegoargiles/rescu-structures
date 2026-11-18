import cadquery as cq, pyvista as pv, numpy as np, pickle, os, sys
pv.OFF_SCREEN = True
W='/home/claude/work'; os.chdir(W)
names=pickle.load(open('verify2/names.pkl','rb')); NM={n.split('/')[-1]: f'verify2/{i:03d}.brep' for i,n in enumerate(names)}
def mesh(s, tol=0.03):
    v,t=s.tessellate(tol,0.12); v=np.array([p.toTuple() for p in v]); return pv.PolyData(v, np.hstack([[3,*x] for x in t]))
def col(n):
    if 'Screws_M3x4' in n: return '#d4a017'
    if 'Prop_Nut' in n: return '#c0c4ca'
    if 'APC' in n: return '#1d1f22'
    if 'Tarot' in n or 'UM2807' in n: return '#4a505a'
    if 'Removable_Plate' in n or 'Adapter' in n: return '#9fb4c8'
    if 'Collar' in n: return '#5b8fd6'
    if 'Boom' in n or 'CFRP' in n: return '#2a2c30'
    return '#e9e7df'
def shot(out, sel, cam, title, clip=None, offsets=(), hide=(), size=(1700,1100), opac={}):
    p=pv.Plotter(off_screen=True, window_size=size); p.set_background('#f4f5f7')
    for n,f in NM.items():
        if not any(k in n for k in sel) or any(h in n for h in hide): continue
        s=cq.Shape.importBrep(f)
        for k,d in offsets:
            if k in n: s=s.translate(cq.Vector(*d))
        m=mesh(s)
        if clip is not None:
            m=m.clip(normal=clip[0], origin=clip[1], invert=False) if not any(k in n for k in ('Screws_M3x4',)) else m
            if m.n_points==0: continue
        p.add_mesh(m, color=col(n), smooth_shading=True, specular=0.35, opacity=opac.get(next((k for k in opac if k in n),None),1.0))
    p.camera_position=cam; p.add_text(title, font_size=13, color='black'); p.screenshot(out); print('wrote', out, flush=True)
w=sys.argv[1]
if w=='section2':
    shot('render/pusher_section.png', ('Shell_','Collar','Removable_Plate','Screws_M3x4','Tarot','Adapter','Prop_Nut_1-4','APC_13x8'),
         [(1112,-210,25),(1112,0,0),(0,0,1)], 'Half-section (y>0 kept): collar (blue), plate (grey-blue), 4x M3x4 SHCS (gold) into the Tarot base',
         clip=((0,1,0),(0,0.01,0)))
if w=='exploded2':
    shot('render/pusher_exploded.png', ('Shell_Right','Collar','Removable_Plate','Screws_M3x4','Tarot'),
         [(1060,-190,95),(1105,0,0),(0,0,1)], 'Exploded along the axis: screws (gold) from the front, through the plate, into the Tarot base',
         clip=((0,1,0),(0,-30,0)), offsets=[('Screws_M3x4',(-22,0,0)),('Removable_Plate',(14,0,0)),('Tarot',(34,0,0))])
if w=='exploded3':
    shot('render/pusher_exploded.png', ('Removable_Plate','Screws_M3x4','Tarot'),
         [(1040,-120,70),(1112,0,0),(0,0,1)], 'Exploded: 4x M3x4 SHCS (gold) go in from the front, through the plate, into the Tarot 19 mm bolt circle',
         offsets=[('Screws_M3x4',(-25,0,0)),('Tarot',(22,0,0))])
if w=='section':
    shot('render/pusher_section.png', ('Shell_','Collar','Removable_Plate','Screws_M3x4','Tarot','Adapter','Prop_Nut_1-4','APC_13x8'),
         [(1118,-260,40),(1112,0,0),(0,0,1)], 'Pusher mount, half-section: Tarot bolted to the plate (4x M3x4 SHCS on the 19 mm circle), plate bonded to collar', clip=((0,-1,0),(0,0,0)))
if w=='exploded':
    shot('render/pusher_exploded.png', ('Shell_','Collar','Removable_Plate','Screws_M3x4','Tarot'),
         [(1060,-170,110),(1100,0,0),(0,0,1)], 'Exploded: screws -> plate -> motor (shell cut away)', clip=((0,-1,0),(0,0,0)),
         offsets=[('Screws_M3x4',(-40,0,0)),('Removable_Plate',(-15,0,0)),('Tarot',(25,0,0))], hide=('Shell_Left',))
if w=='outside':
    shot('render/pusher_outside.png', ('Fuselage','VTail','Tarot','APC_13x8','Adapter','Prop_Nut_1-4'),
         [(1260,330,120),(1110,0,0),(0,0,1)], 'Tarot seated at the plate; wire-tab notch in the right shell', hide=('XPS','Frames','Seam'))
if w=='vtol':
    shot('render/vtol_nut.png', ('UM2807_Front_Boom_R','APC_10x3_LP10030_Front_Boom_R','Prop_Nut_M5_Bullet_Front_Boom_R','Boom_Upper_Half_Boom_R'),
         [(130,215,45),(170,265,14),(0,0,1)], 'UM2807 + APC 10x3 + M5 bullet prop nut (shaft thread +4 mm)')
    shot('render/vtol_nut_section.png', ('UM2807_Front_Boom_R','APC_10x3_LP10030_Front_Boom_R','Prop_Nut_M5_Bullet_Front_Boom_R'),
         [(170,215,20),(170,265,16),(0,0,1)], 'Section: 5.8 mm of M5 thread above the hub, nut bore clears the shaft tip', clip=((0,-1,0),(0,265,0)))
