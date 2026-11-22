"""Mass, CG, tip-over and landing-load screen for the R16.6 landing gear. Reads out_deployed/ and out_retracted/."""
import json, math, glob, os
import cadquery as cq

DENS = {  # g/cm3
    'Knuckle': 2.81, 'Knee_Shaft': 7.85, 'Fork_Pin': 7.85, 'Leg_Rod': 1.60, 'Foot': 1.21, 'Tendon_Plate': 2.81,
    'Tendon_Bracket': 2.81, 'Servo_Arm': 2.81, 'Servo_Arm_Pin': 7.85, 'Knee_Block': 2.81, 'Guide_Pin_1': 7.85,
    'Guide_Pin_2': 7.85, 'Guide_Tab': 1.85, 'Servo_Mount': 1.85, 'Trough': 1.55, 'Belly_Doubler_CFRP': 1.55}
MAT = {'Knuckle': '7075-T6', 'Knee_Shaft': 'steel (4140 HT / 17-4)', 'Fork_Pin': 'hardened steel dowel', 'Leg_Rod': 'CFRP tube OD10/ID6',
       'Foot': 'TPU 95A', 'Tendon_Plate': '7075-T6 1.6 mm', 'Tendon_Bracket': '7075-T6 1.0 mm', 'Servo_Arm': '7075-T6',
       'Servo_Arm_Pin': 'steel', 'Knee_Block': '7075-T6 (CNC)', 'Guide_Pin_1': 'hardened steel dowel', 'Guide_Pin_2': 'steel',
       'Guide_Tab': 'G10', 'Servo_Mount': 'G10', 'Trough': 'CFRP 0.5 mm', 'Belly_Doubler_CFRP': 'CFRP 1.0 mm',
       'REF_Servo_KST_X08H': 'KST X08H Plus (9.5 g, spec)'}
SERVO_G = 9.5
REMOVED_DENS = {'Boom_Lower_Half_Boom_R': 1.5, 'Boom_Lower_Half_Boom_L': 1.5, 'Fuselage_Shell_Left_GFRP_Fuselage': 1.85,
                'Fuselage_Shell_Right_GFRP_Fuselage': 1.85, 'Fuselage_Seam_Strips_GFRP_Fuselage': 1.85}
BASE_M, BASE_CG = 3768.0, (382.0, 0.0, -5.9)    # R16.5 snapshot (z from R16 cg.json; R16.5 z not recorded)

def load(state):
    meta = json.load(open(f'out_{state}/meta.json'))
    rows = []
    for n in meta['parts']:
        base = next(k for k in sorted(list(DENS) + ['REF_Servo_KST_X08H'], key=len, reverse=True) if n.startswith(k))
        s = cq.Shape.importBrep(f'out_{state}/{n}.brep')
        vol = s.Volume() / 1000.0
        m = SERVO_G if base == 'REF_Servo_KST_X08H' else vol * DENS[base]
        c = cq.Shape.centerOfMass(s) if hasattr(cq.Shape, 'centerOfMass') else s.Center()
        rows.append((n, base, m, (c.x, c.y, c.z)))
    return meta, rows

def removed():
    import pickle
    names = [n.split('/')[-1] for n in pickle.load(open('../orig/names.pkl', 'rb'))]
    out = []
    for n, rho in REMOVED_DENS.items():
        a = cq.Shape.importBrep(f'../orig/{names.index(n):03d}.brep'); b = cq.Shape.importBrep(f'out_deployed/MOD__{n}.brep')
        va, vb = a.Volume(), b.Volume(); ca, cb = a.Center(), b.Center()
        dv = va - vb
        c = tuple((va * getattr(ca, k) - vb * getattr(cb, k)) / dv for k in 'xyz') if dv > 1e-6 else (0, 0, 0)
        out.append((n, -dv / 1000 * rho, c))
    return out

def cg(rows, extra):
    M = BASE_M; mx = [BASE_M * c for c in BASE_CG]
    for r in rows:
        M += r[2]; mx = [mx[i] + r[2] * r[3][i] for i in range(3)]
    for e in extra:
        M += e[1]; mx = [mx[i] + e[1] * e[2][i] for i in range(3)]
    return M, [v / M for v in mx]

res = {}
rem = removed()
for state in ('deployed', 'retracted'):
    meta, rows = load(state)
    M, C = cg(rows, rem)
    res[state] = {'mass_g': M, 'cg': C}
    if state == 'deployed':
        gear = sum(r[2] for r in rows) + sum(e[1] for e in rem)
        per = {}
        for r in rows:
            mod = r[0].split('_LG_')[-1] if '_LG_' in r[0] else r[0]
            per.setdefault('LG_' + mod, 0.0); per['LG_' + mod] += r[2]
        bypart = {}
        for r in rows:
            bypart.setdefault(r[1], 0.0); bypart[r[1]] += r[2]
        res['gear_mass_g'] = gear; res['per_module_g'] = per; res['by_part_g'] = bypart
        res['removed_g'] = {e[0]: e[1] for e in rem}
        res['meta'] = meta
# tip-over (deployed, gear on the ground): feet = lowest points of the foot spheres
meta = res['meta']; zg = meta['front_foot_low_z']
fR = meta['front_foot_centre']; fL = (fR[0], -fR[1], fR[2]); fT = meta['tail_foot_centre']
C = res['deployed']['cg']; h = C[2] - zg
def edge(a, b, p):
    ax, ay, bx, by = a[0], a[1], b[0], b[1]
    return abs((bx - ax) * (ay - p[1]) - (ax - p[0]) * (by - ay)) / math.hypot(bx - ax, by - ay)
tip = {'nose-over (front edge)': edge(fR, fL, C), 'side (front-to-tail edge)': edge(fR, fT, C)}
res['cg_height_above_ground_mm'] = h
res['tipover_deg'] = {k: math.degrees(math.atan2(v, h)) for k, v in tip.items()}
res['tipover_edge_distance_mm'] = tip
res['feet'] = {'front_R': fR, 'front_L': fL, 'tail': fT, 'ground_z': zg}
# static and 5 g landing loads per foot
g = 9.81
W = res['deployed']['mass_g'] / 1000 * g
xf, xt = fR[0], fT[0]
tail_share = (C[0] - xf) / (xt - xf); front_share = (1 - tail_share) / 2
res['foot_load_share'] = {'each_front': front_share, 'tail': tail_share}
n = 5.0; mu_hard, mu_slide = 0.25, 0.8
Nf = W * n * front_share
L, rake = 356.0, math.radians(10)
Mv = Nf * L * math.sin(rake) / 1000; Md = mu_hard * Nf * L * math.cos(rake) / 1000
Nf1 = W * front_share
M_slide = (mu_slide * Nf1 * L * math.cos(rake) - Nf1 * L * math.sin(rake)) / 1000
res['knee_loads_front'] = {
    'N_5g_limit_N': Nf, 'drag_0.25_limit_N': mu_hard * Nf,
    'CW_moment_limit_Nm (vertical + forward drag, into heel stop)': Mv + Md,
    'CCW_moment_limit_Nm 5g + 0.25 aft drag (into lock)': Md - Mv,
    'CCW_moment_limit_Nm 1g sliding mu 0.8 (into lock)': M_slide}
Mult_cw = 1.5 * (Mv + Md); Mult_ccw = 1.5 * max(Md - Mv, M_slide)
I = math.pi * (10 ** 4 - 6 ** 4) / 64
res['leg_rod'] = {'M_ult_Nm': Mult_cw, 'sigma_MPa': Mult_cw * 1000 * 5 / I, 'allow_MPa': 210, 'MS': 210 / (Mult_cw * 1000 * 5 / I) - 1}
F_lock = Mult_ccw * 1000 / (10 * math.cos(math.radians(40)))
res['lock'] = {'M_ult_Nm': Mult_ccw, 'fork_pin_force_N': F_lock, 'fork_pin_tau_MPa (dia 3, double shear)': F_lock / (2 * math.pi * 1.5 ** 2),
               'keeper_bending_MPa (7 x 1.4 7075, fixed-fixed span 7.2 between bosses)': (F_lock * 7.2 / 8) / (7 * 1.4 ** 2 / 6),
               'keeper_MS_vs_7075_yield_503': 503 / ((F_lock * 7.2 / 8) / (7 * 1.4 ** 2 / 6)) - 1}
F_heel = Mult_cw * 1000 / 9.3
res['heel_stop'] = {'force_ult_N': F_heel, 'shaft_tau_MPa (dia 5 double shear)': F_heel / (2 * math.pi * 2.5 ** 2),
                    'wall_bearing_MPa (2 x 2 mm x 5)': F_heel / (2 * 2 * 5)}
# wing torsion at the boom station (skin-only closed cell, conservative)
x_ea = 362.0; z_wing = 4.0
T_lim = Nf * (x_ea - fR[0]) / 1000 + mu_hard * Nf * (z_wing - zg) / 1000
A_cell, t_skin = 0.66 * 146 * 11.5, 0.33
tau = 1.5 * T_lim * 1000 / (2 * A_cell * t_skin)
res['wing_torsion'] = {'T_limit_Nm': T_lim, 'skin_tau_ult_MPa': tau, 'allow_MPa': 21.0, 'MS': 21.0 / tau - 1,
                       'compare_LC6_front_motor_T_limit_Nm': 17.3 * (x_ea - 170) / 1000,
                       'with_one_extra_0p33_GFRP_ply_MS': 21.0 / (tau / 2) - 1}
# aft fuselage bending at x 600 from the tail foot (net of aft inertia at 5 g)
Nt = W * n * tail_share
aft = [(141.4, 1130), (45.0, 1050), (43.8, 945), (100.0, 850)]
M600 = Nt * (fT[0] - 600) / 1000 - sum(m / 1000 * g * n * (x - 600) / 1000 for m, x in aft)
res['aft_fuselage'] = {'tail_N_5g_limit': Nt, 'M_x600_limit_Nm': M600,
                       'sigma_ult_MPa (R40.3, t0.33, shell only)': 1.5 * M600 * 1000 / (math.pi * 40.3 ** 2 * 0.33),
                       'allow_buckling_MPa (repo screen)': 16.3}
json.dump(res, open('analysis.json', 'w'), indent=1, default=float)
print(json.dumps({k: v for k, v in res.items() if k != 'meta'}, indent=1, default=lambda x: round(x, 2)))
