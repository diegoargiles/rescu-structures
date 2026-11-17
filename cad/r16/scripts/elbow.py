import sys; sys.path.insert(0,'/home/claude/r15pkg/scripts')
import numpy as np, cadquery as cq
from cadquery import Vector as V
from geom import *
SPAR_D = np.array([spar_x(700)-spar_x(0), 700.0, 0.0]); SPAR_D /= np.linalg.norm(SPAR_D)
AFT_D = np.array([427.9-385.0, 330.0, 0.0]); AFT_D /= np.linalg.norm(AFT_D)
def hermite(P0, T0, P1, T1, k=None):
    P0, T0, P1, T1 = map(lambda a: np.array(a, float), (P0, T0, P1, T1))
    if k is None: k = np.linalg.norm(P1-P0)
    def f(u):
        h00, h10, h01, h11 = 2*u**3-3*u**2+1, u**3-2*u**2+u, -2*u**3+3*u**2, u**3-u**2
        return h00*P0 + h10*k*T0 + h01*P1 + h11*k*T1
    def df(u):
        return (6*u**2-6*u)*P0 + (3*u**2-4*u+1)*k*T0 + (-6*u**2+6*u)*P1 + (3*u**2-2*u)*k*T1
    return f, df
# ---- root elbow: joiner (x310, z4.2, along Y) -> main spar line
J_X, J_Z, Y_ROOT = 310.0, 4.2, 46.2           # elbow shoulder sits 0.2 mm outboard of joiner end (joiner ends Y +-46)
def root_path(ye):
    P1 = (spar_x(ye), ye, SPAR_Z)
    return hermite((J_X, Y_ROOT, J_Z), (0, 1, 0), P1, SPAR_D)
def path_stats(f, df, n=400):
    u = np.linspace(0, 1, n); P = np.array([f(x) for x in u]); D = np.array([df(x) for x in u])
    T = D/np.linalg.norm(D, axis=1)[:, None]
    ang = np.degrees(np.arctan2(T[:, 0], T[:, 1]))
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    dth = np.abs(np.diff(np.radians(ang))); ds = np.diff(s)
    Rmin = np.min(ds/np.maximum(dth, 1e-12))
    return P, T, ang, s, Rmin
def frame(t):
    a = np.cross(t, [0, 0, 1]); a /= np.linalg.norm(a); b = np.cross(a, t); return a, b
def path_clear(f, df, rfun, ymin=46.0, n=120, m=48):
    worst = (1e9, None)
    for u in np.linspace(0, 1, n):
        c = f(u); t = df(u); t = t/np.linalg.norm(t); a, b = frame(t); r = rfun(u)
        for th in np.linspace(0, 2*np.pi, m, endpoint=False):
            p = c + r*(np.cos(th)*a + np.sin(th)*b)
            if abs(p[1]) < ymin: continue
            zu, zl = wing_zup(p[0], abs(p[1]))-WSKIN, wing_zlo(p[0], abs(p[1]))+WSKIN
            cl = min(zu-p[2], p[2]-zl)
            if cl < worst[0]: worst = (cl, tuple(np.round(p, 1)))
    return worst
def r_root(u): return 6.0 if u < 0.75 else 6.0 - (u-0.75)/0.25          # OD12 -> OD10 at the spar shoulder
# ---- aft elbow: pin leg (x385, z3.0, along Y) -> aft torque tube line (vertex at Y85)
A_Y0, A_Y1, A_YB = 46.0, 70.0, 100.0
def aft_line_x(y): return 385.0 + AFT_D[0]/AFT_D[1]*(y-85.0)
def aft_path():
    return hermite((385.0, A_Y1, 3.0), (0, 1, 0), (aft_line_x(A_YB), A_YB, AFT_Z), AFT_D)
if __name__ == '__main__':
    for ye in (100, 110, 120, 130, 140):
        f, df = root_path(ye); P, T, ang, s, Rmin = path_stats(f, df)
        print(f'root ye {ye}: path len {s[-1]:.1f} max sweep {ang.max():.1f} deg, Rmin {Rmin:.1f} mm, x range {P[:,0].min():.1f}-{P[:,0].max():.1f}, clear {path_clear(f, df, r_root)}')
    f, df = aft_path(); P, T, ang, s, Rmin = path_stats(f, df)
    print(f'aft: len {s[-1]:.1f} max {ang.max():.1f} Rmin {Rmin:.0f} clear {path_clear(f, df, lambda u: 2.5)}')
