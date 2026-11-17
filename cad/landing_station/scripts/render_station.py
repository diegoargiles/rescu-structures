import sys, os, numpy as np
sys.path.insert(0, '/home/claude/work'); os.chdir('/home/claude/work'); sys.argv.append('--nostep')
exec(open('assemble_r16.py').read().split("top = cq.Assembly")[0])
import pyvista as pv; pv.OFF_SCREEN = True
def mesh(s, tol=0.3):
    vs, fs = s.tessellate(tol, 0.3)
    return pv.PolyData(np.array([(v.x, v.y, v.z) for v in vs]), np.hstack([[3, *f] for f in fs])).compute_normals(split_vertices=True, feature_angle=35) if fs else None
AC = []
for g in GROUPS:
    for k, s in list(groups[g].items()) + list(extras[g].items()):
        if k.startswith('REF_') and 'Pusher_Prop' not in k: continue
        if 'Prop_Disk' in k: continue
        col, op, met = '#F2F3F5', 1.0, 0.1
        if 'Boom_Upper' in k or 'Boom_Lower' in k or 'Pad_Access' in k: col = '#2B2F36'
        if 'UM2807' in k: col, met = '#3A3F47', 0.7
        if 'Pusher_Prop' in k: col, op = '#D9A441', 0.22
        if not any(t in k for t in ('Skin', 'Shell', 'Boom_', 'UM2807', 'Pusher_Prop', 'Hatch', 'Pad_Access', 'Junction', 'Ruddervator', 'Fixed_Skin', 'Collar')): continue
        m = mesh(s.translate(cq.Vector(0, 0, 300)), 1.0 if 'UM2807' in k else 0.4)
        if m is not None: AC.append((k, m, col, op, met))
SD = '/home/claude/work/station/out'
ST = []
for f in sorted(os.listdir(SD)):
    if not f.endswith('.brep'): continue
    k = f[:-5]; s = cq.Shape.importBrep(f'{SD}/{f}')
    col, met, rough = '#3B4048', 0.6, 0.35
    if 'PETG' in k: col, met, rough = '#F07A2E', 0.0, 0.5
    if 'EVA' in k or 'Feet' in k: col, met, rough = '#17181B', 0.0, 0.9
    if 'Joining' in k: col, met, rough = '#B9BEC5', 0.8, 0.3
    ST.append((k, mesh(s, 0.15), col, met, rough))
def setup(p):
    p.set_background('#EEF1F4', top='#FFFFFF')
    p.add_mesh(pv.Plane(center=(650, 0, -0.5), direction=(0, 0, 1), i_size=3000, j_size=2400), color='#E4E8ED', ambient=0.55, diffuse=0.45)
    p.enable_anti_aliasing('ssaa')
    p.remove_all_lights()
    p.add_light(pv.Light(position=(-800, -1600, 2200), focal_point=(650, 0, 150), intensity=0.75))
    p.add_light(pv.Light(position=(2200, 1400, 900), focal_point=(650, 0, 150), intensity=0.35))
    p.add_light(pv.Light(light_type='headlight', intensity=0.3))
def add_station(p, offs=None):
    for k, m, col, met, rough in ST:
        mm = m.copy()
        if offs:
            for pat, v in offs:
                if pat in k: mm = mm.translate(v); break
        p.add_mesh(mm, color=col, smooth_shading=True, ambient=0.28, diffuse=0.8, specular=0.35 if met > 0.3 else 0.15, specular_power=25)
def add_ac(p, skip=()):
    for k, m, col, op, met in AC:
        if any(s in k for s in skip): continue
        p.add_mesh(m, color=col, opacity=op, smooth_shading=True, ambient=0.3, diffuse=0.75, specular=0.2, specular_power=20)
W = (2200, 1350)
# 3 cradle close-up with boom seated (outboard, low)
p = pv.Plotter(off_screen=True, window_size=W); setup(p); add_station(p); add_ac(p)
p.camera_position = [(560, 620, 175), (395, 265, 255), (0, 0, 1)]; p.camera.zoom(1.0)
p.screenshot('/home/claude/work/station/deliver/S3_boom_cradle.png'); p.close()
# 4 side view with clearance
p = pv.Plotter(off_screen=True, window_size=(2400, 1150)); setup(p); add_station(p); add_ac(p)
p.add_mesh(pv.Line((1185, -400, 134.9), (1185, -400, 0)), color='#C0392B', line_width=8)
p.add_mesh(pv.Line((1150, -400, 134.9), (1220, -400, 134.9)), color='#C0392B', line_width=3)
p.camera_position = [(650, -3000, 230), (650, 0, 230), (0, 0, 1)]; p.enable_parallel_projection(); p.camera.parallel_scale = 330
p.add_text('Side view, aircraft seated: pusher-prop tip 135 mm (5.31 in) above ground', position='upper_left', font_size=16, color='#1f2328')
p.screenshot('/home/claude/work/station/deliver/S4_side_clearance.png'); p.close()
print('ok')
