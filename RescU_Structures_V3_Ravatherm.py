"""RescU foam-core/GFRP candidate: numerical screening, NOT a flight release.

Separate Ravatherm configuration with a bonded tapered tubular wing spar.
V2 and H60 V3 remain unchanged. Unknown fuselage
core/joint masses and unverified load paths prevent an overall structural pass.
Run with Python 3.10+; only the standard library is needed.
"""
from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass, replace
from functools import lru_cache
from math import cos, sin, radians, pi, sqrt, degrees
from pathlib import Path
import csv
import json
import argparse
import RescU_Structures_V2 as v2

ROOT = Path(__file__).resolve().parent
# V3 keeps its own inputs so approved changes never alter the preserved V2.
# Battery mass: revised report, confirmed by Diego on 2026-10-08.
P = {**v2.P, "battery_mass_kg": .900, "fuselage_shell_thickness_m": .00033}


@dataclass(frozen=True)
class Foam:
    name: str
    density: float
    shear_modulus: float
    shear_strength: float
    compression_strength: float


# Diab H Rev19 (2020), minimum strengths AND minimum shear moduli at 23 C.
# No isotropy assumption: core axial stiffness deliberately omitted from EI.
FOAMS = {
    # Ravago TDS v5, 2025-05-09: typical density/G; strength is NOT an aircraft allowable.
    "RAVATHERM": Foam("Ravatherm XPS X H LB", 32., 8e6, .25e6, .30e6),
    "H60": Foam("Divinycell H60", 60., 16e6, .63e6, .70e6),
    "H80": Foam("Divinycell H80", 80., 23e6, .95e6, 1.15e6),
}


@dataclass(frozen=True)
class Skin:
    name: str
    angles: tuple[float, ...]
    ply_thickness: float
    ply_mass: float
    # ASSUMPTIONS for cured nearly balanced woven E-glass/epoxy; NOT vendor
    # allowables. Coupon data must replace these before building to the design.
    E1: float = 15e9
    E2: float = 15e9
    G12: float = 3e9
    nu12: float = .15
    tensile: float = 150e6
    compressive: float = 100e6
    shear: float = 30e6
    strength_knockdown: float = .70

    @property
    def thickness(self):
        return self.ply_thickness * len(self.angles)

    @property
    def areal_mass(self):
        return self.ply_mass * len(self.angles)


# R&G hand lay-up calculated values at 35% fibre volume; actual cure must be
# measured. Each angle describes woven-cloth warp; weft is 90 degrees to warp.
WING_SKIN = Skin("0.33 mm effective woven glass/epoxy", (0., 45., 0.), .000110, .000110*(.291/.000179))
# Equivalent symmetric laminate, not a validated off-the-shelf cloth schedule.
TAIL_SKIN = Skin("80 gsm woven glass", (0., 45., 0.), .000088, .143)

# Engineering assumptions, not team-approved limits or measured properties.
SCREEN = {
    "wing_force_allowance": 1.10,
    "negative_g": -1.50,
    "pitching_cm_bound": -.10,
    "tail_panel_normal_CL": .50,
    "core_strength_knockdown": .70,
    "core_shear_factor": .50,
    "deflection_halfspan_fraction": .05,
    "twist_deg": 2.,
    "soft_stiffness_scale": .70,
    "minimum_sizing_mass_kg": 3.20,
    "unallocated_mass_reserve_kg": .20,
    "proposed_vtol_thrust_weight": 1.50,
}


def integrate(x, f):
    return sum((x[i+1]-x[i])*(f[i+1]+f[i])/2 for i in range(len(x)-1))


def cumulative(x, f):
    out = [0.]
    for i in range(len(x)-1):
        out.append(out[-1] + (x[i+1]-x[i])*(f[i+1]+f[i])/2)
    return out


def matvec(a, b):
    return [sum(x*y for x, y in zip(row, b)) for row in a]


def inverse3(a):
    rows = [list(row)+[float(i == j) for j in range(3)] for i, row in enumerate(a)]
    for j in range(3):
        k = max(range(j, 3), key=lambda i: abs(rows[i][j]))
        rows[j], rows[k] = rows[k], rows[j]
        pivot = rows[j][j]
        if abs(pivot) < 1e-20:
            raise ValueError("Singular laminate stiffness")
        rows[j] = [v/pivot for v in rows[j]]
        for i in range(3):
            if i != j:
                scale = rows[i][j]
                rows[i] = [v-scale*w for v, w in zip(rows[i], rows[j])]
    return [r[3:] for r in rows]


def ply_q(s):
    nu21 = s.nu12*s.E2/s.E1
    den = 1-s.nu12*nu21
    return s.E1/den, s.E2/den, s.nu12*s.E2/den, s.G12


def qbar(s, angle):
    q11, q22, q12, q66 = ply_q(s)
    m, n = cos(radians(angle)), sin(radians(angle))
    a = q11*m**4 + 2*(q12+2*q66)*m*m*n*n + q22*n**4
    b = q11*n**4 + 2*(q12+2*q66)*m*m*n*n + q22*m**4
    c = (q11+q22-4*q66)*m*m*n*n + q12*(m**4+n**4)
    d = (q11-q12-2*q66)*m**3*n - (q22-q12-2*q66)*m*n**3
    e = (q11-q12-2*q66)*m*n**3 - (q22-q12-2*q66)*m**3*n
    f = (q11+q22-2*q12-2*q66)*m*m*n*n + q66*(m**4+n**4)
    return [[a,c,d], [c,b,e], [d,e,f]]


@lru_cache(maxsize=32)
def laminate(s):
    if s.angles != tuple(reversed(s.angles)):
        raise ValueError("This beam screening supports symmetric skin stacks only")
    a = [[sum(qbar(s, angle)[i][j]*s.ply_thickness for angle in s.angles)
          for j in range(3)] for i in range(3)]
    compliance = inverse3(a)
    return {"A": a, "compliance": compliance,
            "E": 1/(compliance[0][0]*s.thickness),
            "G": 1/(compliance[2][2]*s.thickness)}


def ply_failure_index(s, axial_stress, torsion_shear):
    """Maximum stress in each woven ply, including simultaneous bending/torsion.

    Free transverse membrane resultant, no local face bending or peel.
    This is not an interaction criterion and does not check wrinkling/debonding.
    """
    eps = matvec(laminate(s)["compliance"],
                 [axial_stress*s.thickness, 0., torsion_shear*s.thickness])
    q11, q22, q12, q66 = ply_q(s)
    worst = 0.
    for angle in s.angles:
        m, n = cos(radians(angle)), sin(radians(angle))
        e1 = m*m*eps[0] + n*n*eps[1] + m*n*eps[2]
        e2 = n*n*eps[0] + m*m*eps[1] - m*n*eps[2]
        g12 = -2*m*n*eps[0] + 2*m*n*eps[1] + (m*m-n*n)*eps[2]
        sig1, sig2, tau = q11*e1+q12*e2, q12*e1+q22*e2, q66*g12
        for sig in (sig1, sig2):
            allowable = s.tensile if sig >= 0 else s.compressive
            worst = max(worst, abs(sig)/(allowable*s.strength_knockdown))
        worst = max(worst, abs(tau)/(s.shear*s.strength_knockdown))
    return worst


def interp(points, x):
    xs = [p[0] for p in points]
    i = max(0, min(len(points)-2, bisect_right(xs, x)-1))
    a, b = points[i], points[i+1]
    return a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0])


@lru_cache(maxsize=8)
def profile(name, n=240):
    xs = [(1-cos(pi*i/n))/2 for i in range(n+1)]
    if name == "SD7037":
        lines = (ROOT/"airfoils"/"sd7037.dat").read_text().splitlines()[1:]
        pts = [tuple(map(float, line.split())) for line in lines
               if line.strip() and not line.lstrip().startswith("#")]
        le = min(range(len(pts)), key=lambda i: pts[i][0])
        # Discrete file's minimum x is .00021, not zero. Normalize x to its
        # sampled chord so interpolation never extrapolates across the nose.
        xmin, xmax = pts[le][0], max(p[0] for p in pts)
        pts = [((x-xmin)/(xmax-xmin),z) for x,z in pts]
        upper, lower = sorted(pts[:le+1]), sorted(pts[le:])
        return xs, [interp(upper, x) for x in xs], [interp(lower, x) for x in xs]
    if name == "NACA0010":
        # Standard 4-digit equation; -.1036 closes TE (explicit design assumption).
        zs = [5*.10*(.2969*sqrt(x)-.1260*x-.3516*x*x+.2843*x**3-.1036*x**4)
              for x in xs]
        return xs, zs, [-z for z in zs]
    raise ValueError(name)


def strip_moments(x, upper, lower):
    """Area, first moment about z=0, second moment about z=0, x first moment."""
    area = integrate(x, [u-l for u,l in zip(upper,lower)])
    first = integrate(x, [(u*u-l*l)/2 for u,l in zip(upper,lower)])
    second = integrate(x, [(u**3-l**3)/3 for u,l in zip(upper,lower)])
    xfirst = integrate(x, [v*(u-l) for v,u,l in zip(x,upper,lower)])
    return area, first, second, xfirst


def perimeter(x, u, l):
    return (sum(sqrt((x[i+1]-x[i])**2+(z[i+1]-z[i])**2)
                for z in (u,l) for i in range(len(x)-1))
            + abs(u[0]-l[0]) + abs(u[-1]-l[-1]))


def closed_skin_gj(enclosed_area, perimeter_m, shear_modulus, skin_thickness):
    """Bredt-Batho single closed cell, constant skin thickness and modulus."""
    return 4*enclosed_area**2*shear_modulus*skin_thickness/perimeter_m


@lru_cache(maxsize=8192)
def section(chord, s, foam, shape="SD7037", n=240):
    """Chordwise strip integration with approximate normal skin offsets.

    Offset intersections at thin LE/TE are clipped. This is not a CAD offset
    surface. EI ignores core axial stiffness. Torsion assumes intact closed skin;
    no stiffness is credited to foam in torsion. Sweep/warping are not resolved.
    """
    xf, uf, lf = profile(shape, n)
    x, u, l = ([v*chord for v in arr] for arr in (xf,uf,lf))
    inner_u, inner_l = [], []
    for i in range(len(x)):
        j, k = max(0,i-1), min(len(x)-1,i+1)
        slope_u = (u[k]-u[j])/(x[k]-x[j])
        slope_l = (l[k]-l[j])/(x[k]-x[j])
        mid = (u[i]+l[i])/2
        inner_u.append(max(mid, u[i]-s.thickness*sqrt(1+slope_u*slope_u)))
        inner_l.append(min(mid, l[i]+s.thickness*sqrt(1+slope_l*slope_l)))
    outer = strip_moments(x,u,l)
    core = strip_moments(x,inner_u,inner_l)
    skin = [o-c for o,c in zip(outer,core)]
    if skin[0] <= 0 or core[0] <= 0:
        raise ValueError("Skin consumes the section; choose a valid skin/core geometry")
    zbar = skin[1]/skin[0]
    Iskin = skin[2]-skin[0]*zbar*zbar
    mid_u = [(a+b)/2 for a,b in zip(u,inner_u)]
    mid_l = [(a+b)/2 for a,b in zip(l,inner_l)]
    Am = strip_moments(x,mid_u,mid_l)[0]
    pm = perimeter(x,mid_u,mid_l)
    E, G = laminate(s)["E"], laminate(s)["G"]
    # Surface mass uses actual outer perimeter, not clipped skin area / t:
    # conservative at thin trailing edge. Surface sweep correction not included.
    pout = perimeter(x,u,l)
    return {"EI": E*Iskin, "GJ": closed_skin_gj(Am,pm,G,s.thickness),
            "core_area": core[0], "skin_area": skin[0], "zbar": zbar,
            "zupper": max(u), "zlower": min(l), "Am": Am,
            "perimeter": pout, "skin_x": skin[3]/skin[0],
            "core_x": core[3]/core[0],
            "skin_linear_mass": pout*s.areal_mass,
            "core_linear_mass": core[0]*foam.density}


@dataclass(frozen=True)
class TubeSpar:
    enabled: bool = True
    material: str = "CFRP"
    root_od: float = .014
    tip_od: float = .008
    wall: float = .002
    tip_wall: float = .0005
    chord_fraction: float = .30
    density: float = 1600.
    E: float = 70e9
    strength: float = 300e6
    knockdown: float = .70
    # Linear OD AND wall taper, custom manufacture; NOT a catalogue tube.
    # Properties are preliminary V2-derived ASSUMPTIONS, not vendor allowables.
    bond_thickness: float = .00010
    bond_density: float = 1200.

SPAR = TubeSpar()


def tube_properties(od, wall):
    if not 0 < 2*wall < od:
        raise ValueError("Tube requires 0 < 2*wall < OD")
    inner = od-2*wall
    return pi*(od**2-inner**2)/4, pi*(od**4-inner**4)/64


def spar_geometry():
    L = float(P["wingspan_m"])/2
    cr,ct = float(P["wing_root_chord_m"]),float(P["wing_tip_chord_m"])
    dx = float(P["wing_tip_le_offset_m"])+SPAR.chord_fraction*(ct-cr)
    # Straight centerline in an unswept section coordinate, with x sweep.
    xf,uf,lf = profile("SD7037")
    zf = (interp(list(zip(xf,uf)),SPAR.chord_fraction)+interp(list(zip(xf,lf)),SPAR.chord_fraction))/2
    dz = zf*(ct-cr)
    length = sqrt(L*L+dx*dx+dz*dz)
    return {"projected_halfspan_m":L,"tube_length_each_m":length,
            "root_x_m":float(P["x_main_wing_le_m"])+SPAR.chord_fraction*cr,
            "tip_x_m":float(P["x_main_wing_le_m"])+float(P["wing_tip_le_offset_m"])+SPAR.chord_fraction*ct,
            "root_z_section_m":zf*cr,"tip_z_section_m":zf*ct,
            "length_per_span":length/L,
            "note":"Two swept half-wing tubes; root carry-through/dihedral joint unresolved. Section z is not CAD global z."}


@lru_cache(maxsize=16384)
def _reinforced_section(chord,s,foam,pos,L,spar):
    a = dict(section(chord,s,foam))
    if not spar.enabled:
        return a
    od = spar.root_od+(spar.tip_od-spar.root_od)*pos/L
    area, inertia = tube_properties(od,spar.wall+(spar.tip_wall-spar.wall)*pos/L)
    xf,uf,lf = profile("SD7037")
    upper,lower = list(zip(xf,uf)),list(zip(xf,lf))
    x0 = spar.chord_fraction*chord
    z0 = chord*(interp(upper,spar.chord_fraction)+interp(lower,spar.chord_fraction))/2
    # Check the entire circular envelope, including skin and bond allowance.
    clearances=[]
    for j in range(181):
        theta=2*pi*j/180
        xx=x0+(od/2+spar.bond_thickness)*cos(theta)
        zz=z0+(od/2+spar.bond_thickness)*sin(theta)
        if not 0 < xx < chord:
            raise ValueError("Spar outside chord")
        clearances += [chord*interp(upper,xx/chord)-s.thickness-zz,
                       zz-(chord*interp(lower,xx/chord)+s.thickness)]
    if min(clearances) < 0:
        raise ValueError(f"Spar does not fit at y={pos:.4f} m (clearance {min(clearances)*1000:.3f} mm)")
    es=laminate(s)["E"]
    oldz=a["zbar"]
    newz=(es*a["skin_area"]*oldz+spar.E*area*z0)/(es*a["skin_area"]+spar.E*area)
    # Perfect axial compatibility; no tube GJ/shear stiffness credit.
    a["EI"] += es*a["skin_area"]*(oldz-newz)**2+spar.E*(inertia+area*(z0-newz)**2)
    a["zbar"]=newz
    a["core_area"] -= pi*(od/2+spar.bond_thickness)**2
    if a["core_area"] <= 0:
        raise ValueError("Spar consumes core")
    a.update(spar_od=od,spar_z=z0,clearance_m=min(clearances))
    return a


def reinforced_section(chord,s,foam,pos,L):
    return _reinforced_section(chord,s,foam,pos,L,SPAR)


def spar_mass(foam,n=200):
    if not SPAR.enabled:
        return {"tube_kg":0.,"removed_core_kg":0.,"bond_kg":0.,"x_m":0.}
    g=spar_geometry()
    L=g["projected_halfspan_m"]
    y=[L*i/n for i in range(n+1)]
    ods=[SPAR.root_od+(SPAR.tip_od-SPAR.root_od)*v/L for v in y]
    areas=[tube_properties(d,SPAR.wall+(SPAR.tip_wall-SPAR.wall)*v/L)[0] for d,v in zip(ods,y)]
    xs=[g["root_x_m"]+(g["tip_x_m"]-g["root_x_m"])*v/L for v in y]
    factor=2*g["length_per_span"]
    outer=[pi*(d/2+SPAR.bond_thickness)**2 for d in ods]
    bonds=[pi*((d/2+SPAR.bond_thickness)**2-(d/2)**2) for d in ods]
    return {"tube_kg":factor*integrate(y,areas)*SPAR.density,
            "removed_core_kg":factor*integrate(y,outer)*foam.density,
            "bond_kg":factor*integrate(y,bonds)*SPAR.bond_density,
            "x_m":integrate(y,[a*x for a,x in zip(areas,xs)])/integrate(y,areas),
            "removed_x_m":integrate(y,[a*x for a,x in zip(outer,xs)])/integrate(y,outer),
            "bond_x_m":integrate(y,[a*x for a,x in zip(bonds,xs)])/integrate(y,bonds)}


def cantilever(y, q, torque_q, ei, ga, gj, points=()):
    """Integrate equilibrium from free end then curvature/shear/twist from root.

    points: (span station, force, torque). No point may be at free tip outside L.
    Stations containing point loads should be included in the mesh.
    """
    for station, _, _ in points:
        if not 0 <= station <= y[-1]:
            raise ValueError("Point load outside span")
    qint, qyint, tint = cumulative(y,q), cumulative(y,[v*f for v,f in zip(y,q)]), cumulative(y,torque_q)
    shear, moment, torque = [], [], []
    for i, pos in enumerate(y):
        vs, ms, ts = qint[-1]-qint[i], qyint[-1]-qyint[i]-pos*(qint[-1]-qint[i]), tint[-1]-tint[i]
        for station, force, couple in points:
            if pos <= station:
                vs += force
                ms += force*(station-pos)
                ts += couple
        shear.append(vs); moment.append(ms); torque.append(ts)
    slope = cumulative(y,[m/e for m,e in zip(moment,ei)])
    bend = cumulative(y,slope)
    sdef = cumulative(y,[v/g for v,g in zip(shear,ga)])
    twist = cumulative(y,[t/g for t,g in zip(torque,gj)])
    return {"shear": shear, "moment": moment, "torque": torque,
            "bend": bend, "shear_deflection": sdef, "twist": twist}


def panel_case(name, s, foam, half_force, ultimate_factor, shape="SD7037",
               n=200, shear_center=.35, points=(), stiffness_scale=1., pitching_cm=0.):
    wing = shape == "SD7037"
    L = float(P["wingspan_m"])/2 if wing else float(P["vtail_half_span_m"])
    cr = float(P["wing_root_chord_m"] if wing else P["vtail_root_chord_m"])
    ct = float(P["wing_tip_chord_m"] if wing else P["vtail_tip_chord_m"])
    y = sorted(set([L*i/n for i in range(n+1)]+[p[0] for p in points]))
    chords = [cr+(ct-cr)*pos/L for pos in y]
    sec = [reinforced_section(c,s,foam,pos,L) if wing else section(c,s,foam,shape)
           for c,pos in zip(chords,y)]
    weights = [sqrt(max(0.,1-(pos/L)**2)) if wing else c for pos,c in zip(y,chords)]
    norm = integrate(y,weights)
    q = [half_force*w/norm for w in weights]
    pressure = .5*v2.RHO_AIR*float(P["top_speed_mps"])**2
    torque_q = [f*(.25-shear_center)*c + pressure*c*c*pitching_cm
                for f,c in zip(q,chords)]
    # k=.5 is an engineering screening assumption; no validated airfoil k yet.
    ga = [SCREEN["core_shear_factor"]*foam.shear_modulus*stiffness_scale*a["core_area"] for a in sec]
    path_ratio = spar_geometry()["length_per_span"] if wing else 1.
    # Approximate swept-beam path correction; full bending/torsion coupling unresolved.
    ga = [v/path_ratio for v in ga]
    sol = cantilever(y,q,torque_q,[a["EI"]*stiffness_scale/path_ratio**3 for a in sec],ga,
                     [a["GJ"]*stiffness_scale/path_ratio for a in sec],points)
    maxfi, core_util, maxstress, maxtau = 0.,0.,0.,0.
    spar_util = 0.
    for a, m, v, torque in zip(sec,sol["moment"],sol["shear"],sol["torque"]):
        # Ultimate stresses use the SAME factor for distributed and point loads.
        tau = ultimate_factor*torque/(2*a["Am"]*s.thickness)
        # Stress unchanged for uniformly scaled stiffness sensitivity.
        curvature = ultimate_factor*m*path_ratio/a["EI"]
        if wing and SPAR.enabled:
            spar_stress = SPAR.E*abs(curvature)*(a["spar_od"]/2+abs(a["spar_z"]-a["zbar"]))
            spar_util = max(spar_util, spar_stress/(SPAR.strength*SPAR.knockdown))
        for z in (a["zupper"],a["zlower"]):
            # Upward cantilever loading compresses upper skin: epsilon=-z*kappa.
            sig = -laminate(s)["E"]*curvature*(z-a["zbar"])
            maxstress = max(maxstress,abs(sig)); maxtau = max(maxtau,abs(tau))
            for sign in (-1,1):
                maxfi = max(maxfi,ply_failure_index(s,sig,sign*tau))
        # 2 V/A is an assumed peak envelope; local inserts are excluded.
        core_util = max(core_util,2*abs(v)*ultimate_factor/a["core_area"]/(foam.shear_strength*SCREEN["core_strength_knockdown"]))
    defl = sol["bend"][-1]+sol["shear_deflection"][-1]
    defl_util = abs(defl)/(SCREEN["deflection_halfspan_fraction"]*L)
    twist_util = abs(degrees(sol["twist"][-1]))/SCREEN["twist_deg"]
    return {"case": name, "foam": foam.name, "skin_mm": s.thickness*1000,
            "half_force_limit_N": half_force+sum(p[1] for p in points),
            "root_moment_limit_Nm": sol["moment"][0],
            "tip_bend_limit_mm": sol["bend"][-1]*1000,
            "tip_shear_limit_mm": sol["shear_deflection"][-1]*1000,
            "tip_total_limit_mm": defl*1000,
            "tip_twist_limit_deg": degrees(sol["twist"][-1]),
            "max_face_stress_ultimate_MPa": maxstress/1e6,
            "max_torsion_shear_ultimate_MPa": maxtau/1e6,
            "ply_failure_index_ultimate": maxfi,
            "core_shear_utilization_ultimate": core_util,
            "spar_bending_utilization_ultimate": spar_util,
            "deflection_screen_utilization": defl_util,
            "twist_screen_utilization": twist_util,
            "screen_status": "PASS" if max(maxfi,core_util,defl_util,twist_util,spar_util) <= 1 else "FAIL",
            "overall_status": "UNRESOLVED: CAD profile, joints, wrinkling, shell and load envelope"}


@lru_cache(maxsize=64)
def panel_mass(s, foam, shape="SD7037", n=200):
    wing = shape == "SD7037"
    L = float(P["wingspan_m"])/2 if wing else float(P["vtail_half_span_m"])
    cr = float(P["wing_root_chord_m"] if wing else P["vtail_root_chord_m"])
    ct = float(P["wing_tip_chord_m"] if wing else P["vtail_tip_chord_m"])
    sweep = float(P["wing_tip_le_offset_m"] if wing else P["vtail_tip_le_offset_m"])
    xroot = float(P["x_main_wing_le_m"] if wing else P["vtail_root_le_x_m"])
    y = [L*i/n for i in range(n+1)]
    sec = [section(cr+(ct-cr)*pos/L,s,foam,shape) for pos in y]
    sm, cm = [a["skin_linear_mass"] for a in sec], [a["core_linear_mass"] for a in sec]
    # 10% surface mass margin covers omitted sweep surface factor and tip/end
    # skins. Adhesive/finish added separately. Not a tooling procurement quantity.
    skinmass, coremass = 2*integrate(y,sm)*1.10, 2*integrate(y,cm)
    sx = integrate(y,[m*(xroot+sweep*pos/L+a["skin_x"]) for pos,m,a in zip(y,sm,sec)])/integrate(y,sm)
    cx = integrate(y,[m*(xroot+sweep*pos/L+a["core_x"]) for pos,m,a in zip(y,cm,sec)])/integrate(y,cm)
    surface = 2*integrate(y,[a["perimeter"] for a in sec])*1.10
    # ASSUMPTION .100 kg/m2 combined core seal/bond resin/finish, beyond cloth resin.
    extras = .100*surface
    return {"skin_kg": skinmass, "core_kg": coremass, "bond_finish_kg": extras,
            "total_kg": skinmass+coremass+extras, "skin_x_m": sx, "core_x_m": cx,
            "surface_m2_with_margin": surface}


def aircraft_mass(wing_skin=WING_SKIN, tail_skin=TAIL_SKIN, foam=FOAMS["RAVATHERM"]):
    _, old = v2.compute_structural_masses(p=P)
    retained = {"Fuselage shell", "Motor arm R", "Motor arm L", "Payload mount plate"}
    parts = [p for p in old if p.name in retained]
    for name, skin, shape in (("Wing",wing_skin,"SD7037"),("V-tail",tail_skin,"NACA0010")):
        m = panel_mass(skin,foam,shape)
        for suffix, key, xpos in (("skin","skin_kg",m["skin_x_m"]),
                                 ("foam","core_kg",m["core_x_m"]),
                                 ("bond/finish","bond_finish_kg",m["skin_x_m"])):
            parts.append(v2.PointMass(name+" "+suffix,m[key],xpos,0.,0.,"V3 screening"))
    sp = spar_mass(foam)
    if SPAR.enabled:
        parts.append(v2.PointMass("Wing tubular spars",sp["tube_kg"],sp["x_m"],0.,0.,"Ideal bonded tapered tubes"))
        parts.append(v2.PointMass("Spar displaced foam",-sp["removed_core_kg"],sp["removed_x_m"],0.,0.,"Outer tube envelope removed; hollow bore empty"))
        parts.append(v2.PointMass("Spar bond allowance",sp["bond_kg"],sp["bond_x_m"],0.,0.,"0.1 mm equivalent annular epoxy; assumption"))
    hardware = .10*sum(p.mass_kg for p in parts)
    parts.append(v2.PointMass("Provisional local hardware",hardware,.45,0.,0.,"ASSUMPTION 10%; NOT a designed attachment"))
    parts += v2.propulsion_point_masses(p=P)+v2.nonstructural_nonbattery_point_masses(p=P)
    battery_x = v2.solve_battery_x_for_target_cg(parts,p=P)
    parts.append(v2.PointMass("Battery",float(P["battery_mass_kg"]),battery_x,0.,0.,"PROVISIONAL; unknown masses excluded"))
    known = sum(p.mass_kg for p in parts)
    # Explicit reserve, separate from calculated known mass. Does not invent CAD.
    sizing = max(SCREEN["minimum_sizing_mass_kg"],known+SCREEN["unallocated_mass_reserve_kg"])
    return {"known_mass_lower_bound_kg": known, "sizing_mass_kg": sizing,
            "unallocated_reserve_kg": sizing-known, "battery_x_provisional_m": battery_x,
            "battery_in_v2_range": float(P["battery_x_min_m"])<=battery_x<=float(P["battery_x_max_m"]),
            "mass_status": "INCOMPLETE: fuselage foam, actual hardpoints, hinges and finishing",
            "components": [vars(p) for p in parts]}


def cases(s=WING_SKIN, foam=FOAMS["RAVATHERM"], tail_skin=TAIL_SKIN, n=200):
    mass = aircraft_mass(s,tail_skin,foam)
    # Team provisional n=3 limit, 1.5 ultimate. No inertial relief credited.
    # +10% force screen is an assumption for uncertain tail download/distribution.
    limit_n = float(P["limit_load_factor"])
    ultimate_factor = float(P["ultimate_load_factor"])/limit_n
    halfload = mass["sizing_mass_kg"]*v2.G*limit_n/2*SCREEN["wing_force_allowance"]
    label=f"{(SCREEN['wing_force_allowance']-1)*100:g}% force allowance + assumed Cm={SCREEN['pitching_cm_bound']:g}"
    wing = panel_case(f"Wing: {limit_n:g}g + "+label,s,foam,
                      halfload,ultimate_factor,n=n,pitching_cm=SCREEN["pitching_cm_bound"])
    negative = panel_case(f"Wing: {SCREEN['negative_g']:g}g + "+label,s,foam,
                          SCREEN["negative_g"]/limit_n*halfload,ultimate_factor,n=n,
                          pitching_cm=SCREEN["pitching_cm_bound"])
    # Existing external arms retained; two 10 N motors per side. Their net wing
    # load is 20 N at y=.265, with eccentric torque about an ASSUMED .35c SC.
    yarm = float(P["arm_y_abs_m"])
    c = v2.wing_local_chord(yarm,p=P)
    xsc = v2.wing_local_le_x(yarm,p=P)+.35*c
    motorforce = float(P["team_max_vtol_thrust_total_N"])/int(P["n_vtol_motors"])
    thrust_factor = float(P["vtol_structural_thrust_factor"])
    torque = motorforce*(float(P["front_motor_x_m"])+float(P["rear_motor_x_m"])-2*xsc)
    vtol = panel_case("Wing: static VTOL two motors/side",s,foam,0.,thrust_factor,n=n,
                      points=((yarm,2*motorforce,torque),))
    front = panel_case("Wing: front VTOL motor only (attachment envelope)",s,foam,0.,thrust_factor,n=n,
                       points=((yarm,motorforce,motorforce*(float(P["front_motor_x_m"])-xsc)),))
    rear = panel_case("Wing: rear VTOL motor only (attachment envelope)",s,foam,0.,thrust_factor,n=n,
                      points=((yarm,motorforce,motorforce*(float(P["rear_motor_x_m"])-xsc)),))
    # Panel-normal force, two identical tail panels. This does not use V-tail
    # projected horizontal area or divide vertical force by cos(dihedral).
    tailarea = v2.derive_vtail_geometry(p=P)["vtail_area_total_m2"]
    tailforce = .5*v2.RHO_AIR*float(P["top_speed_mps"])**2*tailarea*SCREEN["tail_panel_normal_CL"]/2
    tail = panel_case(f"V-tail: panel-normal CL={SCREEN['tail_panel_normal_CL']:g} at {P['top_speed_mps']:g} m/s",tail_skin,foam,
                      tailforce,ultimate_factor,shape="NACA0010",n=n)
    return mass,[wing,vtol,tail,negative,front,rear]


def spar_trade():
    """Finite candidate set, not a global mass optimization or vendor selection."""
    global SPAR
    selected=SPAR
    rows=[]
    try:
        candidates=[replace(selected,enabled=False)]
        for material,E,rho,strength in (("CFRP",70e9,1600.,300e6),("GFRP",25e9,1850.,150e6)):
            for ro,to,rw,tw in ((8,8,1,1),(14,8,.5,.5),(14,8,.75,.75),
                               (14,8,1.25,1.25),(14,8,1.5,1.5),
                               (14,8,1.5,.5),(14,8,1.75,.5),(14,8,2,.5)):
                candidates.append(replace(selected,material=material,E=E,density=rho,
                    strength=strength,root_od=ro/1000,tip_od=to/1000,wall=rw/1000,tip_wall=tw/1000))
        for candidate in candidates:
            SPAR=candidate
            mass,cs=cases(n=200)
            c=cs[0]
            soft=c["deflection_screen_utilization"]/SCREEN["soft_stiffness_scale"]
            rows.append({"material":candidate.material if candidate.enabled else "no spar",
                "root_od_mm":candidate.root_od*1000,"tip_od_mm":candidate.tip_od*1000,
                "root_wall_mm":candidate.wall*1000,"tip_wall_mm":candidate.tip_wall*1000,
                "tube_pair_g":spar_mass(FOAMS["RAVATHERM"])["tube_kg"]*1000,
                "known_mass_kg":mass["known_mass_lower_bound_kg"],
                "tip_mm":c["tip_total_limit_mm"],"soft_tip_mm":c["tip_total_limit_mm"]/.70,
                "nominal_status":c["screen_status"],"soft_deflection_status":"PASS" if soft<=1 else "FAIL",
                "spar_ultimate_utilization":c["spar_bending_utilization_ultimate"]})
    finally:
        SPAR=selected
    return rows


def run(output):
    output.mkdir(parents=True,exist_ok=True)
    mass, basecases = cases()
    sweep = spar_trade()
    sens = []
    load = basecases[0]["half_force_limit_N"]
    for sc in (.25,.35,.45):
        for stiffness in (SCREEN["soft_stiffness_scale"],1.):
            sens.append({**panel_case("Wing sensitivity",WING_SKIN,FOAMS["RAVATHERM"],load,
                                     float(P["ultimate_load_factor"])/float(P["limit_load_factor"]),
                                     shear_center=sc,stiffness_scale=stiffness,pitching_cm=SCREEN["pitching_cm_bound"]),
                         "shear_center_chord_fraction":sc,"stiffness_scale":stiffness})
    process_skin=replace(WING_SKIN,ply_mass=WING_SKIN.ply_mass*1.20)
    process_tail=replace(TAIL_SKIN,ply_mass=TAIL_SKIN.ply_mass*1.20)
    process_foam=replace(FOAMS["RAVATHERM"],density=FOAMS["RAVATHERM"].density*1.10)
    process_mass=aircraft_mass(process_skin,process_tail,process_foam)
    worst_soft_tip=max(abs(c["tip_total_limit_mm"]) for c in sens
                       if c["stiffness_scale"]==SCREEN["soft_stiffness_scale"])
    wing_deflection_limit_mm=SCREEN["deflection_halfspan_fraction"]*float(P["wingspan_m"])/2*1000
    soft_status="PASS" if worst_soft_tip<=wing_deflection_limit_mm else "FAIL"
    result = {"overall_status":"UNRESOLVED - preliminary candidate only", "assumptions":SCREEN,
              "source_base_commit":"ac0b68db25fb73b2f4fcf0d7762dc8c4e001767b",
              "foam_data_source":"https://www.specifiedby.com/panel-systems-ltd/ravatherm-xps-sheets/ravatherm-xps-x-h-lb-tds-version-5-20250509_2cab80de.pdf",
              "foam_data_notes":"Ravago TDS v5 2025-05-09; density and G typical; G direction-dependent. 300 kPa compression at 10% strain is not an elastic design allowable and is not used as one.",
              "minimum_analytical_spar_clearance_mm":1000*min(reinforced_section(
                    float(P["wing_root_chord_m"])+(float(P["wing_tip_chord_m"])-float(P["wing_root_chord_m"]))*i/200,
                    WING_SKIN,FOAMS["RAVATHERM"],float(P["wingspan_m"])*i/400,float(P["wingspan_m"])/2)["clearance_m"] for i in range(201)),
              "spar": vars(SPAR), "spar_mass": spar_mass(FOAMS["RAVATHERM"]),
              "spar_geometry": spar_geometry(),
              "confirmed_battery_mass_kg":float(P["battery_mass_kg"]),
              "reduced_stiffness_wing_deflection":{"status":soft_status,
                    "worst_tip_mm":worst_soft_tip,"limit_mm":wing_deflection_limit_mm},
              "wing_skin":vars(WING_SKIN),"tail_skin":vars(TAIL_SKIN),
              "foam":vars(FOAMS["RAVATHERM"]),"mass":mass,"cases":basecases,
              "vtol_thrust_to_sizing_weight":float(P["team_max_vtol_thrust_total_N"])/(mass["sizing_mass_kg"]*v2.G),
              "process_mass_sensitivity":process_mass,
              "thrust_for_proposed_margin_N":mass["sizing_mass_kg"]*v2.G*SCREEN["proposed_vtol_thrust_weight"],
              "sweep":sweep,"sensitivity":sens,
              "external_arm_screen":v2.motor_arm_analysis(p=P),
              "payload_plate_screen":v2.payload_plate_analysis(p=P),
              "gates":["CAD differs from SD7037: obtain actual profile before accepting tube fit or sizing",
                       "Custom tapered tube procurement/layup, local ovalization and ply-drop transitions",
                       "Spar-to-skin bonds, load transfer, swept center carry-through and dihedral joint",
                       "CAD sweep/twist and intact torsion closure",
                       "Measured laminate modulus/strength and foam orientation",
                       "Skin wrinkling/local buckling and adhesive peel/debonding",
                       "Wing/tail roots, motor supports, hinges, pusher and payload hardpoints",
                       "Fuselage section/core layout and replacement of removed aft spine",
                       "Gust, landing, asymmetric VTOL, aeroelasticity and full mission loads",
                       "Final mass, CG, VTOL thrust margin and ground structural tests"]}
    (output/"screening.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    for filename,rows in (("load_cases.csv",basecases),("wing_candidates.csv",sweep),
                          ("sensitivity.csv",sens),("mass_components.csv",mass["components"])):
        with (output/filename).open("w",newline="",encoding="utf-8") as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader();writer.writerows(rows)
    lines=["RescU V3 - RAVATHERM / 0.33 mm GFRP / TUBULAR SPAR",result["overall_status"],"",
           f"Wing: {WING_SKIN.angles}, {WING_SKIN.thickness*1000:.3f} mm per face",
           f"Tail: {TAIL_SKIN.angles}, {TAIL_SKIN.thickness*1000:.3f} mm per face",
           "Foam: Ravatherm XPS X H LB; fuselage exterior 0.330 mm GFRP",
           f"Spar: {SPAR.material}, OD root/tip {SPAR.root_od*1000:g}/{SPAR.tip_od*1000:g} mm, wall root/tip {SPAR.wall*1000:g}/{SPAR.tip_wall*1000:g} mm",
           f"Tube pair mass: {spar_mass(FOAMS['RAVATHERM'])['tube_kg']*1000:.1f} g; position {SPAR.chord_fraction*100:g}% local chord",
           f"Battery: {float(P['battery_mass_kg'])*1000:.0f} g (confirmed revised report)",
           f"Known mass lower bound: {mass['known_mass_lower_bound_kg']:.3f} kg",
           f"Load sizing mass: {mass['sizing_mass_kg']:.3f} kg",
           f"Unallocated reserve: {mass['unallocated_reserve_kg']:.3f} kg",
           f"40 N VTOL thrust / sizing weight: {result['vtol_thrust_to_sizing_weight']:.3f}",
           f"Battery x (incomplete mass only): {mass['battery_x_provisional_m']:.3f} m",
           "", "LIMIT deflections / ULTIMATE utilization (<=1 for numerical screen):"]
    for c in basecases:
        lines += [c["case"],f"  {c['screen_status']}: tip {c['tip_total_limit_mm']:.2f} mm; twist {c['tip_twist_limit_deg']:.2f} deg; "
                  f"ply FI {c['ply_failure_index_ultimate']:.3f}; core shear {c['core_shear_utilization_ultimate']:.3f}; spar {c['spar_bending_utilization_ultimate']:.3f}"]
    lines += ["", f"Wing at {SCREEN['soft_stiffness_scale']*100:g}% assumed stiffness: {soft_status}; worst tip {worst_soft_tip:.2f} mm / {wing_deflection_limit_mm:.2f} mm limit.",
              f"{SCREEN['deflection_halfspan_fraction']*100:g}% half-span deflection and {SCREEN['twist_deg']:g} deg twist are proposed engineering screens, not team requirements.",
              "PASS refers only to five calculated screens. No overall structural pass is issued.",
              "Included: ideal bonded wing tubes. Excluded: ribs/aft spine. Retained: external CFRP arms and payload plate.",
              "Fuselage foam and actual joints are not modeled; known mass is a lower bound.",
              "", "Before release:"] + ["- "+g for g in result["gates"]]
    (output/"report.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("\n".join(lines))
    return result


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=ROOT/"results"/"v3_ravatherm")
    run(parser.parse_args().output)
