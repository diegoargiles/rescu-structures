import sys, itertools, json, pickle, os
sys.path.insert(0, '/home/claude/r15pkg/scripts'); sys.path.insert(0, '/home/claude/work')
sys.argv.append('--nostep')
exec(open('assemble_r16.py').read().split("top = cq.Assembly")[0])
P = {}
for g in GROUPS:
    for k, s in groups[g].items(): P[f'{g}/{k}'] = s
    for k, s in extras[g].items():
        if k.startswith('UM2807'): P[f'{g}/{k}'] = s
changed = [k for k in P if k.startswith('Wing_') or 'Joiner_CFRP' in k or 'Landing' in k or 'Leg_' in k or 'Boom_Lower_Half' in k or 'Fuselage_Shell' in k]
bb = {k: P[k].BoundingBox() for k in P}
def ov(a, b): return not (a.xmax < b.xmin or b.xmax < a.xmin or a.ymax < b.ymin or b.ymax < a.ymin or a.zmax < b.zmin or b.zmax < a.zmin)
res = []; n = 0; seen = set()
for a in changed:
    for b in P:
        if a == b or (b, a) in seen: continue
        seen.add((a, b))
        if a.split('/')[1].startswith('REF') and b.split('/')[1].startswith('REF'): continue
        if not ov(bb[a], bb[b]): continue
        n += 1
        try: i = P[a].intersect(P[b]); v = pvol(i) if i.Solids() else 0.0
        except Exception: v = -1
        if v > 0.05 or v < 0: res.append((a, b, round(v, 3))); print('!!', a, b, round(v, 3)); sys.stdout.flush()
print('pairs checked', n, 'overlaps >0.05 mm3:', len(res))
# every wing tube vs its skin: no tube may need trimming
tubes = ['Wing_Root_Elbow_CFRP', 'Wing_Aft_Elbow_CFRP', 'Wing_Main_Spar_CFRP', 'Wing_Aft_Torque_Tube_CFRP', 'Wing_Spar_Sleeve_GFRP', 'Wing_Aft_Collars_GFRP', 'Wing_Wire_Conduit_PTFE']
from geom import wing_wire, WSKIN, WB2, box
skinchk = {}
for sd, sg in (('R', 1), ('L', -1)):
    g = f'Wing_{sd}'; skin = P[f'{g}/Wing_Skin_GFRP_{g}']
    for t in tubes:
        s = P[f'{g}/{t}_{g}']; i = s.intersect(skin); v = pvol(i) if i.Solids() else 0.0
        skinchk[f'{t}_{g}'] = round(v, 4); print('skin x', t, g, round(v, 4))
json.dump(dict(pairs_checked=n, overlaps=res, tube_vs_skin_mm3=skinchk), open('deliver/interference_r16.json', 'w'), indent=1)
