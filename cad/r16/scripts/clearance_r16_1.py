import cadquery as cq, pickle, os, json, numpy as np, sys, time
sys.path.insert(0, '/home/claude')
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from matplotlib.path import Path
from scipy.spatial import cKDTree
PC = {}
os.chdir('/home/claude/work')
names = pickle.load(open('orig/names.pkl', 'rb')); nm = [n.split('/')[-1] for n in names]
parts = {n: (f'new/{i:03d}.brep' if os.path.exists(f'new/{i:03d}.brep') else f'orig/{i:03d}.brep') for i, n in enumerate(nm)
         if not any(k in n for k in ('REF_MT4008_Envelope', 'REF_Pusher_Prop_13in_Disk', 'REF_Prop_Disk_10in'))}
add = {f[:-5]: f'add/{f}' for f in os.listdir('add') if f.endswith('.brep')}
allp = {**parts, **add}; S = {}
def sh(n):
    if n not in S: S[n] = cq.Shape.importBrep(allp[n])
    return S[n]
def dist(a, b):
    d = BRepExtrema_DistShapeShape(sh(a).wrapped, sh(b).wrapped); d.Perform(); return d.Value()
def bbgap(a, b):
    A, B = sh(a).BoundingBox(), sh(b).BoundingBox()
    return max(B.xmin-A.xmax, A.xmin-B.xmax, B.ymin-A.ymax, A.ymin-B.ymax, B.zmin-A.zmax, A.zmin-B.zmax)
res = {'static_min_distance_mm': {}, 'swept_min_clearance_mm': {}}
t0 = time.time()
# swept prop envelopes: tessellate others, test points against revolved (r, axial) polygon
pl = json.load(open('add/placement.json'))
def pts(n, tol=0.3):
    if (n, tol) in PC: return PC[(n, tol)]
    PC[(n, tol)] = _pts(n, tol); return PC[(n, tol)]
def _pts(n, tol):
    v, t = sh(n).tessellate(tol, 0.3); v = np.array([p.toTuple() for p in v]); t = np.array(t)
    a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
    return np.vstack([v] + [a + u*(b-a) + w*(c-a) for u, w in ((1/3, 1/3), (.5, 0), (0, .5), (.5, .5))])
# static: each added part vs parts whose bbox is within 5 mm
for an in add:
    for pn in allp:
        if pn == an or bbgap(an, pn) > 5: continue
        d = float(cKDTree(pts(pn, 0.1)).query(pts(an, 0.1))[0].min()); res['static_min_distance_mm'][f'{an} | {pn}'] = round(d, 2)
        print(f'{time.time()-t0:6.0f}s static', an, '|', pn, round(d, 3), flush=True)
for an in add:
    if not an.startswith('APC'): continue
    A = sh(an).BoundingBox()
    o, ax = ((pl['X_PROP'], 0, 0), (1, 0, 0)) if '13x8' in an else (((A.xmin+A.xmax)/2, (A.ymin+A.ymax)/2, 0), (0, 0, 1))
    o, ax = np.array(o, float), np.array(ax, float)
    P = pts(an, 0.1) - o; z = P @ ax; r = np.linalg.norm(P - np.outer(z, ax), axis=1)
    bins = np.arange(0, r.max()+1, 1.0); env = []
    for b0, b1 in zip(bins[:-1], bins[1:]):
        k = (r >= b0) & (r < b1)
        if k.any(): env.append((min(b1, r.max()), z[k].min(), z[k].max()))
    poly = np.array([(0, env[0][1])] + [(e[0], e[1]) for e in env] + [(e[0], e[2]) for e in env[::-1]] + [(0, env[0][2])])
    R = r.max(); zl, zh = z.min(), z.max(); out = []
    for pn in allp:
        if pn == an: continue
        B = sh(pn).BoundingBox()
        lo = np.array([B.xmin, B.ymin, B.zmin]); hi = np.array([B.xmax, B.ymax, B.zmax])
        c = np.clip(o, lo, hi)
        if np.linalg.norm(c - o) > R + 30: continue
        Q = pts(pn) - o; qz = Q @ ax; qr = np.linalg.norm(Q - np.outer(qz, ax), axis=1)
        k = (qr < R + 25) & (qz > zl - 25) & (qz < zh + 25)
        if not k.any(): continue
        Pq = np.c_[qr[k], qz[k]]
        if Path(poly).contains_points(Pq).any(): best = 0.0
        else:
            best = np.inf
            for p0, p1 in zip(poly, np.roll(poly, -1, axis=0)):
                d = p1 - p0; L = (d @ d) or 1e-12; tt = np.clip(((Pq - p0) @ d) / L, 0, 1)
                best = min(best, np.linalg.norm(Pq - (p0 + np.outer(tt, d)), axis=1).min())
        out.append((round(float(best), 1), pn))
    out.sort(); res['swept_min_clearance_mm'][an] = out[:8]
    print(f'{time.time()-t0:6.0f}s swept', an, out[:8], flush=True)
json.dump(res, open('add/clearance.json', 'w'), indent=1)
print('done')
