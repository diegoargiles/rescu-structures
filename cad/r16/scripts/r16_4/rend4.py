import bpy, numpy as np, glob, os, math, sys
from mathutils import Vector
S=0.001
def srgb(h):
    h=h.lstrip('#'); c=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(((x+0.055)/1.055)**2.4 if x>0.04045 else x/12.92 for x in c)
def mat(name,hexc,rough=0.5,metal=0,alpha=1.0):
    m=bpy.data.materials.get(name)
    if m: return m
    m=bpy.data.materials.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*srgb(hexc),1); b.inputs['Roughness'].default_value=rough
    b.inputs['Metallic'].default_value=metal; b.inputs['Alpha'].default_value=alpha
    return m
def pick(n):
    if 'Nose_Shell' in n: return mat('shell','#3D7FC1',0.4)
    if 'Cove_Liner' in n: return mat('liner','#6FB3E0',0.45)
    if 'Nose_Frame' in n or 'Shelf' in n: return mat('g10','#D29A2A',0.5)
    if 'Joiner_Band' in n: return mat('band','#4C9F70',0.5)
    if 'Nose_Seam' in n: return mat('seam','#8E5BB5',0.5)
    if 'Nutplates' in n: return mat('np','#C9CDD2',0.3,1.0)
    if 'Screws' in n: return mat('scr','#2A2C30',0.3,0.8)
    if 'Z30' in n: return mat('cam','#2E3136',0.35,0.3)
    if n.startswith('REF_'): return mat('ref','#E8A33D',0.6,alpha=0.35)
    if 'CFRP' in n or 'Boom' in n: return mat('cf','#1C1D20',0.3)
    return mat('gfrp','#E9E7DF',0.45)
def scene(tag, skip=(), only=None, offs=()):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=40; sc.cycles.use_denoising=True
    sc.view_settings.view_transform='AgX'
    w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(*srgb('#F3F4F6'),1); w.node_tree.nodes['Background'].inputs[1].default_value=0.6
    for f in glob.glob(f'mesh4/{tag}__*.npz'):
        n=os.path.basename(f)[len(tag)+2:-4]
        if any(k in n for k in skip): continue
        if only and not any(k in n for k in only): continue
        d=np.load(f); me=bpy.data.meshes.new(n); me.from_pydata((d['v']*S).tolist(),[],d['t'].tolist()); me.update()
        for p in me.polygons: p.use_smooth=True
        try: me.set_sharp_from_angle(angle=math.radians(35))
        except Exception: pass
        ob=bpy.data.objects.new(n,me); bpy.context.collection.objects.link(ob); ob.data.materials.append(pick(n))
        for k,v in offs:
            if k in n: ob.location=Vector(v)*S; break
def light(t,s=1.0):
    t=Vector(t)*S
    for nm,loc,e,sz in (('k',(-0.6,-0.8,0.9),120,0.8),('f',(0.8,0.7,0.3),45,1.0),('b',(0.2,-0.3,-0.9),70,0.8)):
        L=bpy.data.lights.new(nm,'AREA'); L.energy=e*s; L.size=sz; o=bpy.data.objects.new(nm,L); bpy.context.collection.objects.link(o)
        o.location=t+Vector(loc); o.rotation_euler=(t-o.location).to_track_quat('-Z','Y').to_euler()
def cam(loc,tgt,lens=50,ortho=None,res=(1600,1000),out='x'):
    c=bpy.data.cameras.new('c'); c.lens=lens; c.clip_start=0.001
    if ortho: c.type='ORTHO'; c.ortho_scale=ortho*S
    o=bpy.data.objects.new('c',c); bpy.context.collection.objects.link(o); o.location=Vector(loc)*S
    o.rotation_euler=(Vector(tgt)*S-o.location).to_track_quat('-Z','Y').to_euler(); bpy.context.scene.camera=o
    sc=bpy.context.scene; sc.render.resolution_x,sc.render.resolution_y=res; sc.render.filepath=f'/home/claude/out164/render/{out}.png'
    bpy.ops.render.render(write_still=True)
NOSE=('Nose_','Camera_Shelf','Camera_Mount')
shot=sys.argv[-1]
if shot in ('all','exploded'):
    offs=[('Nose_Shell_Right',(-90,90,0)),('Nose_Shell_Left',(-90,-90,0)),('Nose_Cove_Liner',(-90,0,-75)),('Camera_Shelf',(-90,0,55)),('Camera_Mount',(-90,0,70)),
          ('Nose_Seam',(-90,0,35)),('Nose_Frame',(-90,0,0)),('Avionics',(-90,0,0)),('Nose_Joint_Screws',(-20,0,0)),('Nose_Joint_Nutplates',(0,0,0)),('Nose_Joiner_Band',(0,0,0))]
    scene('full',skip=('Z30','Envelope','REF_','Wing','Boom','Hatch','Battery','ESC','Joiner_Rec','Joiner_Axial','Wing_Joiner','Frames_Ring','Side_Rails'),offs=offs)
    for o in bpy.data.objects:
        if o.type=='MESH' and o.location.length==0 and not any(k in o.name for k in NOSE+('Avionics',)):
            o.hide_render = not ('Fuselage_Shell' in o.name or 'Seam_Strips' in o.name)
    light((60,0,0),1.1); cam((-420,-520,330),(70,0,-10),lens=38,out='r16_4_01_nose_exploded')
if shot in ('all','section'):
    scene('half',skip=('Envelope',)); light((110,0,-30)); cam((110,-700,-20),(110,0,-35),ortho=330,out='r16_4_02_section')
if shot in ('all','mount'):
    scene('full',skip=('Z30','Envelope','REF_')); light((84,0,-60),1.2); cam((84,0,-420),(84,0,0),ortho=170,out='r16_4_03_cove_from_below')
if shot in ('all','joint'):
    scene('full',skip=('Z30','Envelope','REF_','Wing','Boom')); light((172,-40,0),0.8); cam((120,-200,30),(172,-38,-5),lens=50,out='r16_4_04_joint')
