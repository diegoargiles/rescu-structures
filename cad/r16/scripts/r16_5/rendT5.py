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
    b.inputs['Base Color'].default_value=(*srgb(hexc),1); b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal; b.inputs['Alpha'].default_value=alpha
    return m
def pick(n):
    if 'Root_Block' in n: return mat('blk','#2E3136',0.55)
    if 'Fairings' in n: return mat('fair','#4C9F70',0.5)
    if 'Retention' in n: return mat('scr','#C9A227',0.3,1.0)
    if 'Plug' in n: return mat('plug','#8E5BB5',0.4,0.6)
    if 'Receivers' in n: return mat('rec','#D0505A',0.4)
    if 'Spar' in n: return mat('spar','#1C1D20',0.3)
    if 'AntiRotation' in n: return mat('pin','#C9CDD2',0.3,1.0)
    if 'Frames_Ring' in n: return mat('fr','#D29A2A',0.5)
    if 'Diaphragm' in n: return mat('dia','#4C9F70',0.5)
    if 'VTail' in n and ('Skin' in n): return mat('tskin','#9FC7E6',0.5,alpha=0.25)
    if 'VTail' in n and 'Core' in n: return mat('tcore','#9FC7E6',0.8,alpha=0.12)
    if n.startswith('REF_'): return mat('ref','#E8A33D',0.6,alpha=0.35)
    if 'Shell' in n or 'Hatch' in n or 'Seam' in n: return mat('sh','#E9E7DF',0.45,alpha=0.10)
    return mat('g','#E9E7DF',0.45)
def scene(skip=()):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=24; sc.cycles.use_denoising=True; sc.view_settings.view_transform='AgX'
    w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(*srgb('#F3F4F6'),1); w.node_tree.nodes['Background'].inputs[1].default_value=0.7
    for f in glob.glob('meshT/*.npz'):
        n=os.path.basename(f)[:-4]
        if any(k in n for k in skip): continue
        d=np.load(f); me=bpy.data.meshes.new(n); me.from_pydata((d['v']*S).tolist(),[],d['t'].tolist()); me.update()
        for p in me.polygons: p.use_smooth=True
        try: me.set_sharp_from_angle(angle=math.radians(35))
        except Exception: pass
        ob=bpy.data.objects.new(n,me); bpy.context.collection.objects.link(ob); ob.data.materials.append(pick(n))
def light(t):
    t=Vector(t)*S
    for nm,loc,e,sz in (('k',(-0.4,-0.6,0.7),70,0.6),('f',(0.6,0.5,0.3),30,0.8),('b',(0.2,-0.3,-0.7),40,0.6)):
        L=bpy.data.lights.new(nm,'AREA'); L.energy=e; L.size=sz; o=bpy.data.objects.new(nm,L); bpy.context.collection.objects.link(o)
        o.location=t+Vector(loc); o.rotation_euler=(t-o.location).to_track_quat('-Z','Y').to_euler()
def cam(loc,tgt,lens=50,ortho=None,out='x'):
    c=bpy.data.cameras.new('c'); c.lens=lens; c.clip_start=0.001
    if ortho: c.type='ORTHO'; c.ortho_scale=ortho*S
    o=bpy.data.objects.new('c',c); bpy.context.collection.objects.link(o); o.location=Vector(loc)*S
    o.rotation_euler=(Vector(tgt)*S-o.location).to_track_quat('-Z','Y').to_euler(); bpy.context.scene.camera=o
    sc=bpy.context.scene; sc.render.resolution_x,sc.render.resolution_y=(1600,1000); sc.render.filepath=f'/home/claude/out165/render/{out}.png'; bpy.ops.render.render(write_still=True)
scene(skip=('Shell','Hatch','Seam','Core','Ruddervator','Hinge')); light((1005,0,5)); cam((900,-170,150),(1005,0,5),lens=50,out='r16_5_vtail_root_block_3d')
