import sys, os, json, itertools
sys.path.insert(0, '/home/claude/work'); os.chdir('/home/claude/work'); sys.argv.append('--nostep')
exec(open('assemble_r16.py').read().split("top = cq.Assembly")[0])
from vol import pvol
A = {}
for g in GROUPS:
    for k, s in list(groups[g].items()) + list(extras[g].items()):
        if k.startswith('REF_') and 'Pusher_Prop' not in k: continue
        A[f'{g}/{k}'] = s.translate(cq.Vector(0, 0, 300))
SD = '/home/claude/work/station/out'
S = {f[:-5]: cq.Shape.importBrep(f'{SD}/{f}') for f in sorted(os.listdir(SD)) if f.endswith('.brep')}
def ov(a, b, g=0.0): return not (a.xmax < b.xmin-g or b.xmax < a.xmin-g or a.ymax < b.ymin-g or b.ymax < a.ymin-g or a.zmax < b.zmin-g or b.zmax < a.zmin-g)
res = {'aircraft_vs_station': [], 'station_internal': [], 'near_misses_lt_2mm': []}
bbA = {k: v.BoundingBox() for k, v in A.items()}; bbS = {k: v.BoundingBox() for k, v in S.items()}
for s, a in itertools.product(S, A):
    if not ov(bbS[s], bbA[a], 2.0): continue
    i = S[s].intersect(A[a]); v = pvol(i) if i.Solids() else 0.0
    if v > 0.01: res['aircraft_vs_station'].append((s, a, round(v, 2))); print('!! AC', s, a, round(v, 2))
    else:
        dd = S[s].distance(A[a])
        if dd < 2.0: res['near_misses_lt_2mm'].append((s, a, round(dd, 2))); print('near', s, a, round(dd, 2))
for a, b in itertools.combinations(S, 2):
    if not ov(bbS[a], bbS[b]): continue
    i = S[a].intersect(S[b]); v = pvol(i) if i.Solids() else 0.0
    if v > 0.05: res['station_internal'].append((a, b, round(v, 2))); print('!! ST', a, b, round(v, 2))
json.dump(res, open(f'{SD}/../interference_station.json', 'w'), indent=1); print('done', {k: len(v) for k, v in res.items()})
