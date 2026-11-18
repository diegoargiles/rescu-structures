"""
Parametric APC-style 'Sport' propeller models for RescU (10x3 LP10030, 13x8 LP13080).

Frame (both props):
  +Z = rotation axis = thrust direction (front of prop, toward incoming air)
  Hub centered at origin, hub faces at z = +/- hub_thk/2
  Blades along +/-X.  Flat (pressure) side faces -Z (motor side), cambered side faces +Z.
  'STD' = standard tractor prop, CCW viewed from the front (+Z).
  'P'   = mirror image (pusher / opposite-rotation), CW viewed from the front.

Blade pitch angle beta(r) = atan(P / (2*pi*r)) applied to the airfoil flat bottom.
Blade thickness is scaled so that solid mass at rho_nylon_gf matches the catalog weight.
"""
import math, json, sys
import numpy as np
import cadquery as cq

IN = 25.4
RHO = 1.35e-3  # g/mm^3, glass-filled nylon (APC material)

# Planform (APC sport-like): r/R -> chord/R
CHORD = [(0.07, 0.115), (0.12, 0.125), (0.20, 0.150), (0.30, 0.172), (0.40, 0.182),
         (0.50, 0.180), (0.60, 0.168), (0.70, 0.150), (0.80, 0.124), (0.88, 0.098),
         (0.94, 0.072), (0.975, 0.050), (1.00, 0.022)]
# Thickness/chord distribution (before mass scaling)
TC = [(0.07, 0.60), (0.12, 0.42), (0.20, 0.26), (0.30, 0.18), (0.50, 0.13), (0.80, 0.10), (1.00, 0.09)]

PROPS = {
    "10x3": dict(code="LP10030", D=10, P=3, hub_d=1.00, hub_t=0.46, shaft=0.25, oz=0.92),
    "13x8": dict(code="LP13080", D=13, P=8, hub_d=1.00, hub_t=0.48, shaft=0.25, oz=1.73),
}


def interp(tab, x):
    xs, ys = zip(*tab)
    return float(np.interp(x, xs, ys))


def airfoil(n=28):
    """Flat-bottom (Clark-Y-like) section, unit chord. Returns upper TE->LE then lower LE->TE."""
    beta = np.linspace(0, math.pi, n)
    x = 0.5 * (1 - np.cos(beta))  # cosine spacing, 0 = LE
    yt = 5 * 0.12 * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x**2 + 0.2843 * x**3 - 0.1015 * x**4)
    yt = yt / 0.06  # normalize so max half-thickness ~= 1.0 * (t/2) unit; scaled later
    up = 0.85 * yt   # most thickness on cambered (front) side
    lo = -0.15 * yt  # nearly flat back, rounded LE
    upper = list(zip(x[::-1], up[::-1]))
    lower = list(zip(x[1:], lo[1:]))
    return upper, lower


def section_wire(r, R, Pmm, tscale, hub_t):
    c = interp(CHORD, r / R) * R
    tc = interp(TC, r / R) * tscale
    t = tc * c
    beta = math.atan2(Pmm, 2 * math.pi * r)
    # keep root sections inside the hub thickness envelope (axial extent ~ c*(sin b + t/c*cos b))
    env = float(np.interp(r, [0.0, 0.5 * IN, 0.20 * R, 0.35 * R], [0.95 * hub_t, 0.95 * hub_t, 1.7 * hub_t, 3.0 * hub_t]))
    c = min(c, env / (math.sin(beta) + tc * math.cos(beta)))
    t = tc * c
    upper, lower = airfoil()
    piv = interp([(0.07, 0.50), (0.30, 0.45), (1.0, 0.36)], r / R)  # pitch axis, centered at root
    cb, sb = math.cos(beta), math.sin(beta)
    zoff = -0.5 * t  # center section thickness about the pitch axis
    def to3d(u, v):
        uu = (u - piv) * c
        vv = v * t + zoff  # airfoil v is in units of total thickness
        # chord dir LE->TE = (-cb, -sb) in (y,z); normal toward front = (-sb, cb)
        y = -uu * cb - vv * sb
        z = -uu * sb + vv * cb
        return cq.Vector(r, y, z)
    pts = [to3d(u, v) for u, v in upper] + [to3d(u, v) for u, v in lower]
    zc = 0.5 * (max(p.z for p in pts) + min(p.z for p in pts))  # center section axially on hub mid-plane
    pts = [cq.Vector(p.x, p.y, p.z - zc) for p in pts]
    spl = cq.Edge.makeSpline(pts)
    te = cq.Edge.makeLine(pts[-1], pts[0])
    return cq.Wire.assembleEdges([spl, te])


def blade(R, Pmm, tscale, hub_t, r0):
    rs = [r0] + [f * R for f, _ in CHORD if f * R > r0 + 1.0]
    wires = [section_wire(r, R, Pmm, tscale, hub_t) for r in rs]
    return cq.Solid.makeLoft(wires, ruled=False)


def build(spec, tscale):
    R = spec["D"] * IN / 2
    Pmm = spec["P"] * IN
    hub_r = spec["hub_d"] * IN / 2
    hub_t = spec["hub_t"] * IN
    b1 = blade(R, Pmm, tscale, hub_t, r0=0.07 * R)
    b2 = b1.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 180)
    hub = cq.Workplane("XY").workplane(offset=-hub_t / 2).circle(hub_r).extrude(hub_t)
    body = hub.union(cq.Workplane().add(b1)).union(cq.Workplane().add(b2))
    body = body.cut(cq.Workplane("XY").workplane(offset=-hub_t).circle(spec["shaft"] * IN / 2).extrude(2 * hub_t))
    body = body.intersect(cq.Workplane("XY").box(2 * R, 4 * R, 100))  # exact diameter
    return body.val()


def target_g(spec):
    return spec["oz"] * 28.3495


def main(outdir):
    report = {}
    for name, spec in PROPS.items():
        tgt = target_g(spec)
        # secant iteration on thickness scale to hit catalog mass
        s0, s1 = 1.0, 1.3
        m0 = build(spec, s0).Volume() * RHO
        m1 = build(spec, s1).Volume() * RHO
        for _ in range(6):
            if abs(m1 - tgt) < 0.05:
                break
            s2 = s1 + (tgt - m1) * (s1 - s0) / (m1 - m0)
            s2 = max(0.6, min(s2, 3.0))
            s0, m0 = s1, m1
            s1 = s2
            m1 = build(spec, s1).Volume() * RHO
        solid = build(spec, s1)
        mirrored = solid.mirror("YZ")  # mirror across plane containing axis -> opposite hand
        base = f"APC_Sport_{name}_{spec['code']}"
        solid.exportBrep(f"{outdir}/{base}_STD.brep")
        mirrored.exportBrep(f"{outdir}/{base}_P.brep")
        bb = solid.BoundingBox()
        report[name] = dict(code=spec["code"], target_mass_g=round(tgt, 2), model_mass_g=round(solid.Volume() * RHO, 2),
                            thickness_scale=round(s1, 3), bbox_mm=[round(bb.xlen, 2), round(bb.ylen, 2), round(bb.zlen, 2)],
                            valid=solid.isValid())
        print(name, report[name], flush=True)
    json.dump(report, open(f"{outdir}/prop_mass_props.json", "w"), indent=2)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
