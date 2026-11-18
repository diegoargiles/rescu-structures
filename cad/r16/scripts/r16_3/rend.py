import bpy, numpy as np, glob, os, sys, math
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
    if 'Nose_Shell' in n: return mat('nose','#3D7FC1',0.4)
    if 'Shelf' in n: return mat('g10','#D29A2A',0.5)
    if 'Joiner_Band' in n: return mat('band','#4C9F70',0.5)
    if 'Envelope' in n: return mat('env','#D0505A',0.6,alpha=0.12)
    if 'Z30' in n: return mat('cam','#2E3136',0.35,0.3)
    if n.startswith('REF_'): return mat('ref','#E8A33D',0.6,alpha=0.35)
    if 'CFRP' in n or 'Boom' in n: return mat('cf','#1C1D20',0.3)
    return mat('gfrp','#E9E7DF',0.45)
def scene(tag, skip=()):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=40; sc.cycles.use_denoising=True
    sc.view_settings.view_transform='AgX'; sc.render.film_transparent=False
    w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(*srgb('#F3F4F6'),1); w.node_tree.nodes['Background'].inputs[1].default_value=0.5
    for f in glob.glob(f'mesh/{tag}__*.npz'):
        n=os.path.basename(f)[len(tag)+2:-4]
        if any(k in n for k in skip): continue
        d=np.load(f); me=bpy.data.meshes.new(n); me.from_pydata((d['v']*S).tolist(),[],d['t'].tolist()); me.update()
        for p in me.polygons: p.use_smooth=True
        try: me.set_sharp_from_angle(angle=math.radians(35))
        except Exception: pass
        ob=bpy.data.objects.new(n,me); bpy.context.collection.objects.link(ob); ob.data.materials.append(pick(n))
def light(t):
    t=Vector(t)*S
    for nm,loc,e,sz in (('k',(-0.6,-0.8,0.9),120,0.8),('f',(0.8,0.7,0.3),40,1.0),('b',(0.2,-0.3,-0.9),70,0.8)):
        L=bpy.data.lights.new(nm,'AREA'); L.energy=e; L.size=sz; o=bpy.data.objects.new(nm,L); bpy.context.collection.objects.link(o)
        o.location=t+Vector(loc); o.rotation_euler=(t-o.location).to_track_quat('-Z','Y').to_euler()
def cam(loc,tgt,lens=50,ortho=None,res=(1600,1000),out='x'):
    c=bpy.data.cameras.new('c'); c.lens=lens; c.clip_start=0.001
    if ortho: c.type='ORTHO'; c.ortho_scale=ortho*S
    o=bpy.data.objects.new('c',c); bpy.context.collection.objects.link(o); o.location=Vector(loc)*S
    o.rotation_euler=(Vector(tgt)*S-o.location).to_track_quat('-Z','Y').to_euler(); bpy.context.scene.camera=o
    sc=bpy.context.scene; sc.render.resolution_x,sc.render.resolution_y=res; sc.render.filepath=f'/home/claude/out/{out}.png'
    bpy.ops.render.render(write_still=True)
# 1 three-quarter from below/front
scene('full',skip=('Envelope',)); light((120,0,-40)); cam((-230,-330,-260),(115,0,-45),lens=40,out='z30_r1_below_front')
# 2 side, ghost sweep envelope
scene('full'); light((120,0,-40)); cam((100,-900,-40),(100,0,-50),ortho=420,out='z30_r2_side_envelope')
# 3 section at y=0 (half model), Z30 full
scene('half',skip=('Envelope',)); light((110,0,-30)); cam((110,-700,-20),(110,0,-35),ortho=330,out='z30_r3_section')
# 4 bottom view
scene('full',skip=('Envelope',)); light((110,0,-60)); cam((120,0,-900),(120,0,0),ortho=380,out='z30_r4_bottom')
