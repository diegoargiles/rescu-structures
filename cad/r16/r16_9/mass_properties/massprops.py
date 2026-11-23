"""R16.9 mass properties: bottom-up from the R16.9 CAD (rt BREPs) + the equipment list.

Frame: CAD frame, origin at the nose tip, X aft, Y right (starboard), Z up, mm / g.
Structure: R16 BOM mass where the part exists in the BOM (thin skins are unreliable in OCC volume integration),
otherwise OCC volume x density. Centroid and inertia shape always come from the R16.9 geometry (so moved parts
are where they are now). Equipment: masses from the team equipment list, placed on their CAD envelopes.
"""
import sys, json, csv, math, numpy as np, cadquery as cq
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
sys.path.insert(0, '/home/claude/work/fdr'); from vr import NAMES, shape

OCC = json.load(open('occ.json'))
BOM = {r['part']: r for r in csv.DictReader(open('bom16.csv'))}
USE_OCC = {'Fuselage_Seam_Strips_GFRP_Fuselage', 'Boom_Lower_Half_Boom_R', 'Boom_Lower_Half_Boom_L', 'Nose_Shell_Left_GFRP_Fuselage',
           'Nose_Shell_Right_GFRP_Fuselage', 'Nose_Seam_Strips_GFRP_Fuselage', 'Wing_Root_Fairings_ASA_Fuselage'}  # changed since the R16 BOM

def rho(n):  # g/cm^3, same table as the R16.6-R16.9 scripts
    if '_LG_' in n:
        for k, v in [('Knuckle', 2.81), ('Knee_Shaft', 7.85), ('Fork_Pin', 7.85), ('Leg_Rod', 1.6), ('Foot', 1.21), ('Tendon', 2.81),
                     ('Servo_Arm_Pin', 7.85), ('Servo_Arm', 2.81), ('Knee_Block', 2.81), ('Guide_Pin', 7.85), ('Guide_Tab', 1.85),
                     ('Servo_Mount', 1.85), ('Trough', 1.55), ('Belly', 1.55)]:
            if n.startswith(k): return v
    if 'Foam' in n: return 0.10
    if 'XPS' in n: return 0.032
    if any(k in n for k in ['Screw', 'Nutplate', 'Pin_D3', 'Bolts', 'Prop_Nut', 'Rod_Ends']): return 7.85
    if '6061' in n or 'Spar_Root_Plug' in n: return 2.7
    if 'PTFE' in n: return 2.2
    if 'ASA' in n or 'PA-CF' in n: return 1.07
    if 'Fillets' in n: return 0.6
    if 'Brass' in n: return 8.5
    if 'CFRP' in n or 'Boom_' in n or 'Saddle_U' in n or 'Pad_Access' in n: return 1.55
    return 1.85

def group(n):
    if '_LG_' in n: return 'Landing gear'
    for g in ('Wing', 'Boom', 'VTail'):
        if n.endswith(('_' + g + '_R', '_' + g + '_L')) or ('_' + g + '_' in n and not n.endswith('_Fuselage')): return {'Wing': 'Wing', 'Boom': 'Booms', 'VTail': 'V-tail'}[g]
    if n.startswith('Nose_'): return 'Nose module'
    return 'Fuselage'

def props_of(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s.wrapped, g)
    c = g.CentreOfMass(); M = g.MatrixOfInertia()
    return g.Mass(), np.array([c.X(), c.Y(), c.Z()]), np.array([[M.Value(i, j) for j in (1, 2, 3)] for i in (1, 2, 3)])

items = []  # dict(name, group, kind, mass_g, c, I_own (g mm^2, about own CG), source)
def add(name, grp, kind, m, c, I=None, src=''):
    items.append(dict(name=name, group=grp, kind=kind, mass_g=float(m), c=np.array(c, float), I=np.zeros((3, 3)) if I is None else I, source=src))

THIN = ('Skin', 'Shell_', 'Seam_Strips', 'Hatch_Front', 'Hatch_Rear', 'Hatch_Tail')
def surf_props(s):
    g = GProp_GProps(); BRepGProp.SurfaceProperties_s(s.wrapped, g)
    c = g.CentreOfMass(); M = g.MatrixOfInertia()
    return g.Mass(), np.array([c.X(), c.Y(), c.Z()]), np.array([[M.Value(i, j) for j in (1, 2, 3)] for i in (1, 2, 3)])

def add_part(n, s=None, state=''):
    if s is None and any(t in n for t in THIN):
        a, c, I = surf_props(shape(n)); v = OCC[n]['vol']
        if n in BOM and n not in USE_OCC and float(BOM[n]['mass_g'] or 0) > 0: m = float(BOM[n]['mass_g']); src = 'R16 BOM mass, R16.9 surface centroid'
        else: m = v * rho(n) / 1000; src = f'R16.9 CAD volume x {rho(n)} g/cm3, surface centroid'
        add(n + state, group(n), 'structure', m, c, I * (m / a), src); return
    if s is None:
        v = OCC[n]['vol']; c = np.array(OCC[n]['c']); I = np.array(OCC[n]['I'])
    else:
        v, c, I = props_of(s)
    if n in BOM and n not in USE_OCC and float(BOM[n]['mass_g'] or 0) > 0:
        m = float(BOM[n]['mass_g']); src = 'R16 BOM mass, R16.9 position'
    else:
        m = v * rho(n) / 1000; src = f'R16.9 CAD volume x {rho(n)} g/cm3'
    add(n + state, group(n), 'structure', m, c, I * (m / v), src)

EQUIP = 'REF_|UM2807|APC_|Tarot'
def structure(gear='deployed'):
    for n in NAMES:
        if __import__('re').match(EQUIP, n) or n.startswith('Prop_Nut') or n.startswith('Motor_Screws_M3x4'):
            continue
        if '_LG_' in n and gear == 'retracted' and not n.startswith(('Knee_Block', 'Trough', 'Belly', 'Servo_Mount', 'Guide_')):
            s = cq.Shape.importBrep(f'/home/claude/work/gear2/out_retracted/{n}.brep')
            if '_LG_Front_' in n: s = s.translate(cq.Vector(35, 0, 0))
            add_part(n, s)
        else:
            add_part(n)
    # pusher hardware kept as structure (small)
    for n in ('Motor_Screws_M3x4_SHCS_Pusher_Fuselage', 'Prop_Nut_1-4in_Bullet_Pusher_Fuselage', 'Prop_Nut_M5_Bullet_Front_Boom_R',
              'Prop_Nut_M5_Bullet_Rear_Boom_R', 'Prop_Nut_M5_Bullet_Front_Boom_L', 'Prop_Nut_M5_Bullet_Rear_Boom_L'):
        add_part(n)

def solid_mass(n, m, src, grp='Equipment', solid=None):
    s = shape(n)
    sols = s.Solids() if solid is None else [s.Solids()[solid]]
    vs = [props_of(x) for x in sols]; V = sum(v for v, _, _ in vs)
    c = sum(v * cc for v, cc, _ in vs) / V
    I = sum(Ii * (m / V) + (m * v / V) * ((cc - c) @ (cc - c) * np.eye(3) - np.outer(cc - c, cc - c)) for v, cc, Ii in vs)
    return c, I

def equipment(buoy=True, unresolved=True):
    for n in [k for k in NAMES if k.startswith('UM2807')]:
        c, I = solid_mass(n, 52.0, ''); add(n, 'Propulsion', 'equipment', 52.0, c, I, 'UM2807 52 g with leads (Unusual Machines)')
    for n in [k for k in NAMES if k.startswith('APC_10x3')]:
        c, I = solid_mass(n, 26.1, ''); add(n, 'Propulsion', 'equipment', 26.1, c, I, 'APC 10x3 LP10030, 0.92 oz catalog')
    c, I = solid_mass('APC_13x8_LP13080P_Pusher_Prop_Fuselage', 49.0, ''); add('APC 13x8 pusher prop', 'Propulsion', 'equipment', 49.0, c, I, 'APC LP13080, 1.73 oz catalog')
    c, I = solid_mass('Tarot_4008_Pusher_Motor_Fuselage', 99.9, ''); add('Tarot 4008 pusher motor + adapter', 'Propulsion', 'equipment', 99.9, c, I, '148.9 g pusher allocation (inputs.json) minus prop')
    s = shape('REF_Battery_Modules_75x68x47_Fuselage').Solids()
    for i, so in enumerate(sorted(s, key=lambda x: x.Center().x)):
        v, cc, Ii = props_of(so); add(f'Battery 6S module {"front" if i == 0 else "rear"} (half of 6S2P)', 'Battery', 'equipment', 472.0, cc, Ii * 472.0 / v, 'M65A 6S2P 944 g (12 x 74.5 + 50), inputs.json')
    c, I = solid_mass('REF_ESC_AIR40A_x4_Fuselage', 150.0, ''); add('4 x AIR40A ESCs + wiring', 'Avionics', 'equipment', 150.0, c, I, 'inputs.json')
    c, I = solid_mass('REF_Camera_ELP_5MP_IR_USB_Fuselage', 35.0, ''); add('ELP 5MP IR USB camera', 'Avionics', 'equipment', 35.0, c, I, 'ASSUMED 35 g, weigh the unit')
    c, I = solid_mass('REF_VTail_Servos_Fuselage', 43.8, ''); add('V-tail servos x2 (HS-5085MG)', 'Avionics', 'equipment', 43.8, c, I, 'R13 equipment list')
    for n in [k for k in NAMES if k.startswith('REF_Servo_KST')]:
        c, I = solid_mass(n, 9.5, ''); add(n, 'Landing gear', 'equipment', 9.5, c, I, 'KST X08H Plus 9.5 g')
    add('Heat sink', 'Avionics', 'equipment', 30.0, (200, 0, 0), None, 'inputs.json, position provisional')
    add('Flight controller (Cube) + receiver', 'Avionics', 'equipment', 0.0, (152, 0, 8), None, 'NO MASS YET - add real values')
    if unresolved:
        add('Camera/AI allocation (UNRESOLVED)', 'Avionics', 'equipment', 350.0, (60, 0, 0), None, 'inputs.json 350 g, probably the old camera line: confirm or cut')
        add('Other servo allocation (UNRESOLVED)', 'Avionics', 'equipment', 136.2, (800, 0, 0), None, 'inputs.json residual: confirm or cut')
    if buoy:
        add('Buoy (flotation) + beacon', 'Payload', 'payload', 360.0, (350, 0, -55), None, 'inputs.json; point mass at the release plate')
        add('Payload release magnet', 'Payload', 'payload', 10.0, (350, 0, -55), None, 'inputs.json')

def totals(its, bond=0.0):
    its = [dict(i) for i in its]
    if bond:
        S = [i for i in its if i['kind'] == 'structure']; ms = sum(i['mass_g'] for i in S)
        cs = sum(i['mass_g'] * i['c'] for i in S) / ms
        Is = sum(i['I'] + i['mass_g'] * ((i['c'] - cs) @ (i['c'] - cs) * np.eye(3) - np.outer(i['c'] - cs, i['c'] - cs)) for i in S)
        its.append(dict(name='Bond, fillet and finish allowance', group='Allowance', kind='structure', mass_g=bond * ms, c=cs, I=Is * bond, source=f'{bond * 100:.1f} % of CAD structure'))
    M = sum(i['mass_g'] for i in its); C = sum(i['mass_g'] * i['c'] for i in its) / M
    I = sum(i['I'] + i['mass_g'] * ((i['c'] - C) @ (i['c'] - C) * np.eye(3) - np.outer(i['c'] - C, i['c'] - C)) for i in its)
    return its, M, C, I * 1e-9  # g mm^2 -> kg m^2

BOND = 0.075
def case(gear, buoy, unresolved=True, extra=()):
    global items; items = []
    structure(gear); equipment(buoy, unresolved)
    for e in extra: add(*e)
    return totals(items, BOND)

def tensor_report(M, C, I):
    # CAD frame tensor -> body frame (x fwd, y right, z down): xb=-x, yb=y, zb=-z  => T = diag(-1,1,-1)
    T = np.diag([-1, 1, -1]); Ib = T @ I @ T
    return dict(mass_kg=round(M / 1000, 4), cg_mm_cad=[round(v, 1) for v in C],
                Ixx=round(I[0, 0], 5), Iyy=round(I[1, 1], 5), Izz=round(I[2, 2], 5),
                Ixz_product_cad=round(-I[0, 2], 5), Ixy_product_cad=round(-I[0, 1], 5), Iyz_product_cad=round(-I[1, 2], 5),
                Ixz_product_body=round(-Ib[0, 2], 5))

if __name__ == '__main__':
    fixes = [('Joiner OD14/11 upgrade (delta)', 'Fuselage', 'structure', 3.6, (345, 0, 4.2), None, 'R16.9 structures fix'),
             ('Inner-wing +-45 CF ply R (delta)', 'Wing', 'structure', 25.0, (395, 155, 4.5), None, 'R16.9 structures fix'),
             ('Inner-wing +-45 CF ply L (delta)', 'Wing', 'structure', 25.0, (395, -155, 4.5), None, 'R16.9 structures fix')]
    res = {}
    for key, gear, buoy, unres, ex in [('A_takeoff_gear_down_buoy_on', 'deployed', True, True, ()),
                                       ('B_cruise_gear_up_buoy_on', 'retracted', True, True, ()),
                                       ('C_after_release_gear_up_buoy_off', 'retracted', False, True, ()),
                                       ('D_landing_gear_down_buoy_off', 'deployed', False, True, ()),
                                       ('E_A_with_structural_fixes', 'deployed', True, True, fixes),
                                       ('F_A_without_unresolved_allocations', 'deployed', True, False, ())]:
        its, M, C, I = case(gear, buoy, unres, ex)
        res[key] = tensor_report(M, C, I)
        print(key, res[key], flush=True)
        if key == 'A_takeoff_gear_down_buoy_on':
            with open('R16_9_component_masses.csv', 'w', newline='') as f:
                w = csv.writer(f); w.writerow(['item', 'group', 'kind', 'mass_g', 'x_mm', 'y_mm', 'z_mm', 'source'])
                for i in sorted(its, key=lambda i: (i['group'], -i['mass_g'])):
                    w.writerow([i['name'], i['group'], i['kind'], round(i['mass_g'], 2), *[round(v, 1) for v in i['c']], i['source']])
            grp = {}
            for i in its:
                g = grp.setdefault(i['group'], [0, np.zeros(3)]); g[0] += i['mass_g']; g[1] = g[1] + i['mass_g'] * i['c']
            res['groups_case_A'] = {g: dict(mass_g=round(v[0], 1), x_mm=round((v[1] / v[0])[0], 1) if v[0] else None) for g, v in grp.items()}
            res['structure_g_case_A'] = round(sum(i['mass_g'] for i in its if i['kind'] == 'structure'), 1)
    json.dump(res, open('R16_9_mass_properties.json', 'w'), indent=1)
