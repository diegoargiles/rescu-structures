"""Quick shaded renders (orthographic, painter's algorithm) of the R16.6 gear with matplotlib."""
import sys, json, glob, pickle, math
import numpy as np
import cadquery as cq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import lg

names = [n.split('/')[-1] for n in pickle.load(open('../orig/names.pkl', 'rb'))]
def S(n): return cq.Shape.importBrep(f'../orig/{names.index(n):03d}.brep')

def tess(shape, tol=0.4):
    vs, tris = shape.tessellate(tol, 0.5)
    V = np.array([v.toTuple() for v in vs]); T = np.array(tris, dtype=int)
    return V, T

def basis(view):
    d = np.array(view, float); d /= np.linalg.norm(d)
    up = np.array([0, 0, 1.0])
    if abs(d @ up) > 0.95: up = np.array([1.0, 0, 0])
    r = np.cross(d, up); r /= np.linalg.norm(r); u = np.cross(r, d)
    return d, r, u

def draw(ax, items, view, light=(-0.4, -0.7, 0.6), alpha_map=None):
    d, r, u = basis(view)
    L = np.array(light, float); L /= np.linalg.norm(L)
    polys, cols, depth = [], [], []
    for shape, rgb, a in items:
        V, T = tess(shape)
        if len(T) == 0: continue
        P = V[T]                                   # (n,3,3)
        n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]); nn = np.linalg.norm(n, axis=1) + 1e-12; n /= nn[:, None]
        n[(n @ d) > 0] *= -1                        # face the camera
        sh = 0.45 + 0.55 * np.clip(n @ L, 0, 1)
        X = P @ r; Y = P @ u; Z = (P @ d).mean(axis=1)
        for i in range(len(T)):
            polys.append(np.c_[X[i], Y[i]]); depth.append(Z[i])
            c = np.clip(np.array(rgb) * sh[i], 0, 1); cols.append((*c, a))
    order = np.argsort(depth)[::-1]
    pc = PolyCollection([polys[i] for i in order], facecolors=[cols[i] for i in order], edgecolors='none', antialiased=False)
    ax.add_collection(pc); ax.autoscale_view(); ax.set_aspect('equal'); ax.axis('off')

C = {'gfrp': (0.92, 0.91, 0.87), 'cfrp': (0.16, 0.16, 0.18), 'al': (0.74, 0.76, 0.80), 'steel': (0.45, 0.46, 0.48),
     'tpu': (0.90, 0.40, 0.12), 'plate': (0.22, 0.48, 0.85), 'arm': (0.92, 0.74, 0.12), 'servo': (0.20, 0.36, 0.62),
     'g10': (0.84, 0.64, 0.22), 'motor': (0.30, 0.33, 0.37), 'prop': (0.55, 0.58, 0.62), 'xps': (0.62, 0.78, 0.90)}
def col(n):
    if n.startswith('Foot'): return C['tpu']
    if n.startswith(('Leg_Rod', 'Trough', 'Belly_Doubler')): return C['cfrp']
    if n.startswith(('Tendon',)): return C['plate']
    if n.startswith('Servo_Arm'): return C['arm']
    if n.startswith('REF_Servo'): return C['servo']
    if n.startswith(('Guide_Tab', 'Servo_Mount')): return C['g10']
    if n.startswith(('Knee_Shaft', 'Fork_Pin', 'Guide_Pin')): return C['steel']
    return C['al']

def gear_items(state, tags=('LG_Front_R', 'LG_Front_L', 'LG_Tail')):
    meta = json.load(open(f'out_{state}/meta.json'))['parts']
    return [(cq.Shape.importBrep(f'out_{state}/{n}.brep'), col(n), 1.0) for n, (g, sub) in meta.items() if any(sub.startswith(t) for t in tags)]

AIR = ['Fuselage_Shell_Left_GFRP_Fuselage', 'Nose_Shell_Left_GFRP_Fuselage', 'Wing_Skin_GFRP_Wing_L', 'VTail_Fixed_Skin_GFRP_VTail_L',
       'VTail_Ruddervator_Skin_GFRP_VTail_L', 'Boom_Upper_Half_Boom_L', 'Boom_Lower_Half_Boom_L', 'UM2807_Front_Boom_L', 'UM2807_Rear_Boom_L',
       'APC_10x3_LP10030P_Front_Boom_L', 'APC_10x3_LP10030_Rear_Boom_L', 'Tarot_4008_Pusher_Motor_Fuselage', 'APC_13x8_LP13080P_Pusher_Prop_Fuselage',
       'REF_Z30_Camera_Gimbal_Fuselage', 'REF_Payload_Mount_Plate_Fuselage', 'Pusher_Bonded_Collar_GFRP_Fuselage']
def air_items(state):
    out = []
    for n in AIR:
        s = S(n)
        mod = glob.glob(f'out_{state}/MOD__{n}.brep')
        if mod: s = cq.Shape.importBrep(mod[0])
        c = C['cfrp'] if 'Boom' in n and 'UM' not in n and 'APC' not in n else C['motor'] if ('UM2807' in n or 'Tarot' in n) else C['prop'] if 'APC' in n else (0.95, 0.66, 0.30) if 'REF' in n else C['gfrp']
        out.append((s, c, 1.0))
    return out

def side(state, fn, title):
    fig = plt.figure(figsize=(16, 7.2), dpi=130); ax = fig.add_axes([0, 0, 1, 0.93])
    draw(ax, air_items(state) + gear_items(state, ('LG_Front_L', 'LG_Tail')), view=(0, 1, 0))
    ax.axhline(-378.7, color='0.55', lw=1.2)
    fig.suptitle(title, fontsize=15, x=0.02, ha='left'); fig.savefig(fn, facecolor='white'); plt.close(fig)

def iso(state, fn, title):
    fig = plt.figure(figsize=(14, 9), dpi=130); ax = fig.add_axes([0, 0, 1, 0.93])
    items = [(S(n), C['gfrp'], 1.0) for n in ['Fuselage_Shell_Left_GFRP_Fuselage', 'Fuselage_Shell_Right_GFRP_Fuselage', 'Nose_Shell_Left_GFRP_Fuselage', 'Nose_Shell_Right_GFRP_Fuselage',
             'Wing_Skin_GFRP_Wing_L', 'Wing_Skin_GFRP_Wing_R', 'VTail_Fixed_Skin_GFRP_VTail_L', 'VTail_Fixed_Skin_GFRP_VTail_R']]
    for n in ['Fuselage_Shell_Left_GFRP_Fuselage', 'Fuselage_Shell_Right_GFRP_Fuselage']:
        items = [it for it in items]
    for side_ in 'LR':
        for n in [f'Boom_Upper_Half_Boom_{side_}', f'UM2807_Front_Boom_{side_}', f'UM2807_Rear_Boom_{side_}']:
            items.append((S(n), C['cfrp'] if 'Boom' in n else C['motor'], 1.0))
        items.append((cq.Shape.importBrep(f'out_{state}/MOD__Boom_Lower_Half_Boom_{side_}.brep'), C['cfrp'], 1.0))
    items[0] = (cq.Shape.importBrep(f'out_{state}/MOD__Fuselage_Shell_Left_GFRP_Fuselage.brep'), C['gfrp'], 1.0)
    items[1] = (cq.Shape.importBrep(f'out_{state}/MOD__Fuselage_Shell_Right_GFRP_Fuselage.brep'), C['gfrp'], 1.0)
    items += gear_items(state)
    draw(ax, items, view=(0.55, 0.62, 0.42))
    fig.suptitle(title, fontsize=15, x=0.02, ha='left'); fig.savefig(fn, facecolor='white'); plt.close(fig)

def knee(fn):
    """right front knee, section at the centre plane (outboard half removed), seen from outboard."""
    secs = pickle.load(open('boom_inner_R.pkl', 'rb'))
    xs = sorted(secs); top = [max(p[1] for p in secs[x]) + 0.8 for x in xs]; bot = [min(p[1] for p in secs[x]) - 0.8 for x in xs]
    fx = {f[3:-5]: cq.Shape.importBrep(f) for f in glob.glob('fx_*.brep')}
    keep = lg.box(-50, 450, -20, 0.85, -60, 40)
    def sec(s):
        r = s.intersect(keep)
        return r if r.Solids() else None
    fixed = [(fx['Knee_Block'], C['al']), (fx['Trough'], (0.45, 0.45, 0.48)), (fx['REF_Servo_KST_X08H'], C['servo']),
             (fx['Servo_Mount'], C['g10']), (fx['Guide_Pin_1'], C['steel'])]
    fixed = [(sec(s), c, 1.0) for s, c in fixed]
    fixed = [f for f in fixed if f[0] is not None]
    P = cq.Vector(*lg.P_R)
    fig = plt.figure(figsize=(16, 13), dpi=130)
    states = [(lg.PSI_DEP, 'Deployed + locked (servo +60°)'), (0.0, 'Mid-swing (servo 0°)'), (lg.PSI_RET, 'Retracted + locked (servo −60°)')]
    for i, (psi, t) in enumerate(states):
        ax = fig.add_axes([0.01 + i * 0.33, 0.56, 0.32, 0.38])
        m, d, th = lg.moving_parts(psi)
        mv = [(sec(m[k]), col(k), 1.0) for k in ('Knuckle', 'Knee_Shaft', 'Fork_Pin', 'Leg_Rod', 'Foot', 'Tendon_Plate')]
        mv = [x for x in mv if x[0] is not None]
        draw(ax, [(s.translate(P), c, a) for s, c, a in fixed + mv], view=(0, -1, 0))
        ax.plot([-x for x in xs], top, color='0.3', lw=1.3); ax.plot([-x for x in xs], bot, color='0.3', lw=1.3)
        ax.set_xlim(-262, -180); ax.set_ylim(-62, -8); ax.invert_xaxis()
        ax.set_title(f'{t}\nleg {abs(th):.0f}° below the boom axis, tendon plate at {d:+.1f} mm', fontsize=11, loc='left')
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.50])
    items = [(s, c, a) for s, c, a in fixed]
    for psi in [lg.PSI_DEP, 20, 0, -20, lg.PSI_RET]:
        m, d, th = lg.moving_parts(psi)
        items += [(m[k], col(k), 1.0) for k in ('Knuckle', 'Leg_Rod', 'Foot')]
    draw(ax, [(s.translate(P), c, a) for s, c, a in items], view=(0, -1, 0))
    ax.plot([-x for x in xs], top, color='0.3', lw=1.3); ax.plot([-x for x in xs], bot, color='0.3', lw=1.3)
    ax.axhline(-378.7, color='0.6', lw=1)
    ax.set_xlim(-600, -110); ax.set_ylim(-395, 10); ax.invert_xaxis()
    ax.set_title('Right front leg swing: deployed, three intermediate positions, retracted (boom outline in grey; ground line at the bottom)', fontsize=11, loc='left')
    fig.savefig(fn, facecolor='white'); plt.close(fig)

if __name__ == '__main__':
    what = sys.argv[1]
    if what == 'side':
        side('deployed', 'r_side_deployed.png', 'R16.6 landing gear deployed — left side (ground line 379 mm below the boom pivot)')
        side('retracted', 'r_side_retracted.png', 'R16.6 landing gear retracted — left side: the front leg is hidden inside the boom, the tail leg inside the belly')
    if what == 'iso':
        iso('deployed', 'r_iso_deployed.png', 'R16.6 — gear deployed (3 knee modules)')
    if what == 'knee':
        knee('r_knee_states.png')
