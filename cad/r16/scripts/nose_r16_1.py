"""R16 nose smoothing: replace the 39-facet cone nose (x 0..200) with the exact elliptical surface the facets were
sampled from, r(x)=45*sqrt(1-(1-x/200)^2) (verified: every facet vertex lies on it). Skin 0.33 thick (radial),
seam strips 0.30 under the skin. New pieces are rebuilt out to x=290 (plain cylinder) and joined there."""
import cadquery as cq, math, numpy as np, pickle, sys
sys.path.insert(0, '/home/claude'); from vol import tv
A, B, XS = 200.0, 45.0, 290.0
V = cq.Vector
def curve(off, x0, x1):
    """edges along r = r_e(x) - off from x0 to x1 (x1 > 200 adds the straight cylinder line)."""
    xe = min(x1, A); edges = []
    if off == 0 and x0 == 0:
        edges.append(cq.Edge.makeEllipse(A, B, V(A,0,0), V(0,0,1), V(1,0,0), 90, 180).reversed() if False else
                     cq.Edge.makeEllipse(A, B, V(A,0,0), V(0,0,1), V(1,0,0), 90, 180))
    else:
        th0 = max(math.acos(1-x0/A), math.asin(off/B)) if x0 > 0 else math.asin(off/B)
        th1 = math.acos(1-xe/A)
        th = th0 + (th1-th0)*np.concatenate([[0], np.sort(1-np.cos(np.linspace(0, math.pi/2, 150)))[1:]])
        pts = [V(A-A*math.cos(t), B*math.sin(t)-off, 0) for t in th]
        tg = [V(A*math.sin(t), B*math.cos(t), 0).normalized() for t in (th[0], th[-1])]
        edges.append(cq.Edge.makeSpline(pts, tangents=tg, scale=True))
    if x1 > A + 1e-6:
        edges.append(cq.Edge.makeLine(V(A, B-off, 0), V(x1, B-off, 0)))
    return edges
def ends(edges):
    ps = [e.startPoint() for e in edges] + [e.endPoint() for e in edges]
    return min(ps, key=lambda p: p.x), max(ps, key=lambda p: p.x)
def band(off_out, off_in, x0, x1):
    eo, ei = curve(off_out, x0, x1), curve(off_in, x0, x1)
    (o0, o1), (i0, i1) = ends(eo), ends(ei)
    es = eo + ei + [cq.Edge.makeLine(o1, i1)]
    if (o0 - i0).Length > 1e-9: es.append(cq.Edge.makeLine(i0, o0))
    w = cq.Wire.assembleEdges(es)
    return cq.Solid.revolve(cq.Face.makeFromWires(w), 360, V(0,0,0), V(1,0,0))
def box(x0,x1,y0,y1,z0,z1):
    return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, V(x0,y0,z0))
names = pickle.load(open('orig/names.pkl','rb'))
idx = {n.split('/')[-1]: i for i, n in enumerate(names)}
ld = lambda n: cq.Shape.importBrep(f'orig/{idx[n]:03d}.brep')
BIG = 3000
skin = band(0, 0.33, 0, XS)
print('skin valid', skin.isValid())
out = {}
noseL = skin.intersect(box(-1, XS, -60, 0, -60, 60)).cut(box(192, 280, -33, 33, 0, 60))
for nm, y0, y1 in (('Fuselage_Shell_Right_GFRP_Fuselage', 0, 60), ('Fuselage_Shell_Left_GFRP_Fuselage', -60, 0)):
    s = ld(nm)
    rest = s.intersect(box(XS, BIG, -60, 60, -60, 60))
    nose = noseL if y0 < 0 else noseL.mirror('XZ')
    new = rest.fuse(nose); c = new.clean(); new = c if c.isValid() else new
    out[nm] = new
    print(nm, 'valid', new.isValid(), 'solids', len(new.Solids()), 'faces', len(s.Faces()), '->', len(new.Faces()))
nm = 'Hatch_Front_GFRP_Fuselage'; s = ld(nm); bb = s.BoundingBox()
new = skin.intersect(box(bb.xmin, bb.xmax, bb.ymin, bb.ymax, 0, 60))
out[nm] = new; print(nm, new.isValid(), len(new.Solids()), len(s.Faces()), '->', len(new.Faces()), 'bbox', [round(v,2) for v in (bb.xmin,bb.xmax,bb.ymin,bb.ymax)])
nm = 'Fuselage_Seam_Strips_GFRP_Fuselage'; s = ld(nm); sols = []
for so in s.Solids():
    bb = so.BoundingBox()
    if bb.xmin > 199: sols.append(so); continue
    zsl = (0, 60) if bb.zmin > 0 else (-60, 0)
    if bb.xmax < A:
        sols.append(band(0.33, 0.63, bb.xmin, A).intersect(box(bb.xmin-1, bb.xmax, -6, 6, *zsl))); continue
    nose = band(0.33, 0.63, bb.xmin, XS).intersect(box(bb.xmin-1, XS, -6, 6, *zsl))
    sols += so.intersect(box(XS, BIG, -60, 60, -60, 60)).fuse(nose).clean().Solids()
new = cq.Compound.makeCompound(sols); out[nm] = new
print(nm, all(x.isValid() for x in sols), len(s.Solids()), '->', len(sols), len(s.Faces()), '->', len(new.Faces()))
import os; os.makedirs('new', exist_ok=True)
for k, v in out.items(): v.exportBrep(f'new/{idx[k]:03d}.brep')
