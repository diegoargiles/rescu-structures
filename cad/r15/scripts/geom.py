"""Shared geometry for the RescU R15 full-aircraft model. mm; X aft from nose, Y right, Z up."""
import cadquery as cq, numpy as np
from cadquery import Vector as V
AF = np.loadtxt('/home/claude/rescu-structures/engine/airfoils/sd7037.dat', skiprows=1)
# ---- wing planform (repo cad_snapshot / R13: dihedral 0, incidence 0)
WROOT_LE, WCR, WCT, WSWEEP, WB2 = 260.0, 165.0, 100.0, 140.0, 700.0
def wchord(y): return WCR - (WCR-WCT)*abs(y)/WB2
def wxle(y): return WROOT_LE + WSWEEP*abs(y)/WB2
WSKIN = 0.33
SPAR_FRAC, SPAR_Z = 0.305, 4.0            # R13 swept spar centre line (matches spar sleeve at Y265)
def spar_x(y): return wxle(y) + SPAR_FRAC*wchord(y)
def aft_x(y): return 385.0 + (427.9-385.0)*(abs(y)-85.0)/(415.0-85.0)   # R13 aft torque tube line
AFT_Z = 3.1
CONDUIT_X, CONDUIT_Z = 375.0, 4.0          # conduit runs (345,46)->(375,257.5) in plan
CONDUIT_X_ROOT = 345.0
def box(x0, x1, y0, y1, z0, z1): return cq.Workplane().box(x1-x0, y1-y0, z1-z0, centered=False).translate((x0, y0, z0))
def cylx(y, z, r, x0, x1): return cq.Workplane('YZ').circle(r).extrude(x1-x0).translate((x0, y, z))
def cyly(x, z, r, y0, y1): return cq.Workplane('XZ').circle(r).extrude(-(y1-y0)).translate((x, y0, z))
def cylz(x, y, r, z0, z1): return cq.Workplane().circle(r).extrude(z1-z0).translate((x, y, z0))
def tube_between(p0, p1, ro, ri=0.0):
    p0, p1 = V(*p0), V(*p1); d = p1-p0; L = d.Length
    s = cq.Solid.makeCylinder(ro, L, p0, d.normalized())
    if ri > 0: s = s.cut(cq.Solid.makeCylinder(ri, L, p0, d.normalized()))
    return cq.Workplane().add(s)
def inset_airfoil(pts, t):
    """offset closed airfoil polyline inward by t (point normals); drop TE region thinner than ~2t"""
    P = np.array(pts); n = len(P)
    T = np.roll(P, -1, 0) - np.roll(P, 1, 0); N = np.c_[T[:, 1], -T[:, 0]]
    N /= np.linalg.norm(N, axis=1, keepdims=True)
    # orientation: make normals point inward
    c = P.mean(0)
    if np.mean(np.sum((P - c)*N, 1)) > 0: N = -N
    Q = P + t*N
    return Q
def _updown(coords):
    i = np.argmin(coords[:, 0]); up = coords[:i+1][::-1]; lo = coords[i:]
    return up, lo
def inset_pts(chord, t, coords, n=40):
    up, lo = _updown(coords)
    xs = np.linspace(0, 1, 400)
    th = np.interp(xs, up[:, 0], up[:, 1]) - np.interp(xs, lo[:, 0], lo[:, 1])
    ok = np.where(th*chord - 2*t >= 0.25)[0]; x1 = xs[ok[-1]]
    x0 = 1.2*t/chord
    b = np.linspace(0, np.pi, n); xx = x0 + (x1-x0)*(1-np.cos(b))/2
    u = np.interp(xx, up[:, 0], up[:, 1])*chord - t
    l = np.interp(xx, lo[:, 0], lo[:, 1])*chord + t
    pts = [(x*chord, v) for x, v in zip(xx[::-1], u[::-1])] + [(x*chord, v) for x, v in zip(xx, l)]
    return np.array(pts)
def airfoil_pts(chord, inset=0.0, coords=AF, te_cut=None):
    if inset > 0: return inset_pts(chord, inset, coords)
    P = coords[:-1]*chord
    return P
def section_wire(pts2d, place):
    """pts2d (u=chordwise, v=thickness) -> 3D via place(u,v) -> V; closed spline"""
    vs = [place(u, v) for u, v in pts2d]
    return cq.Wire.assembleEdges([cq.Edge.makeSpline(vs + [vs[0]])])
def wing_wire(y, inset=0.0, te_cut=None):
    c = wchord(y); x0 = wxle(y)
    return section_wire(airfoil_pts(c, inset, te_cut=te_cut), lambda u, v: V(x0+u, y, v))
def wing_zlo(x, y):
    c = wchord(y); s = (x-wxle(y))/c; i = np.argmin(AF[:, 0]); lo = AF[i:]
    return float(np.interp(s, lo[:, 0], lo[:, 1])*c)
def wing_zup(x, y):
    c = wchord(y); s = (x-wxle(y))/c; i = np.argmin(AF[:, 0]); up = AF[:i+1][::-1]
    return float(np.interp(s, up[:, 0], up[:, 1])*c)
# ---- fuselage profile (repo Fuselage_Profile_Parameters)
FL, FR, FNOSE, FTAPER, FTAILX, FTAILR, FREARR, FWALL = 1110.0, 45.0, 200.0, 425.0, 960.0, 30.5, 26.0, 0.33
def fus_r(x):
    if x <= FNOSE: return FR*np.sqrt(max(0.0, 1-((FNOSE-x)/FNOSE)**2))
    if x <= FTAPER: return FR
    if x <= FTAILX: return FR + (FTAILR-FR)*(x-FTAPER)/(FTAILX-FTAPER)
    return FTAILR + (FREARR-FTAILR)*(x-FTAILX)/(FL-FTAILX)
def fus_solid(offset=0.0, x0=0.0, x1=FL):
    xs = np.r_[np.linspace(max(x0, 0.0), min(x1, FNOSE), 40), [FTAPER, FTAILX, FL]]
    xs = xs[(xs >= x0) & (xs <= x1)]
    if x1 > xs[-1]: xs = np.r_[xs, x1]
    pts = [(x, max(fus_r(x)-offset, 0.0)) for x in xs]
    if pts[0][1] > 0: pts = [(pts[0][0], 0.0)] + pts
    pts = pts + [(pts[-1][0], 0.0)]
    # profile in XZ plane (x, r) then revolve about X axis
    w = cq.Workplane('XZ').polyline([(p[0], p[1]) for p in pts]).close()
    return w.revolve(360, (0, 0, 0), (1, 0, 0))
# ---- V-tail (NACA0010, 35 deg dihedral, root LE 960, root c 90, tip c 45, span 245, sweep 120)
TLE, TCR, TCT, TSPAN, TSWEEP, TDIH, TSKIN = 960.0, 90.0, 45.0, 245.0, 120.0, 35.0, 0.264
HINGE_FRAC = 0.69
def naca00(t=0.10, n=60):
    b = np.linspace(0, np.pi, n); x = (1-np.cos(b))/2
    yt = 5*t*(0.2969*np.sqrt(x)-0.1260*x-0.3516*x**2+0.2843*x**3-0.1036*x**4)
    up = np.c_[x[::-1], yt[::-1]]; lo = np.c_[x[1:], -yt[1:]]
    return np.vstack([up, lo])
NACA = naca00()
def tchord(s): return TCR - (TCR-TCT)*s/TSPAN
def txle(s): return TLE + TSWEEP*s/TSPAN
def tail_place(sg, s):
    a = np.radians(TDIH); ey = V(0, sg*np.cos(a), np.sin(a)); en = V(0, -sg*np.sin(a), np.cos(a))
    def f(u, v): return V(txle(s)+u, 0, 0) + ey*s + en*v
    return f
def tail_wire(sg, s, inset=0.0, u0=None, u1=None):
    c = tchord(s); P = inset_pts(c, inset, NACA) if inset > 0 else NACA[:-1]*c
    return section_wire(P, tail_place(sg, s))
