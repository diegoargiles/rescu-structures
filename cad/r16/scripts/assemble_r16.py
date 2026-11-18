"""RescU R16 full-aircraft assembly = R15 STEP parts + rebuilt wings (elbow joints) + shortened joiner - TPU landing feet."""
import sys, os, re, csv, json, pickle
sys.path.insert(0, '/home/claude/r15pkg/scripts'); sys.path.insert(0, '/home/claude/work')
import cadquery as cq
from geom import tube_between
from vol import pvol
src = open('/home/claude/r15pkg/scripts/assemble_full.py').read()
exec(src[src.index('MAT = {'):src.index('def load_dir')])          # reuse R15 material table + mat()
names = pickle.load(open('orig/names.pkl', 'rb'))
GROUPS = ['Fuselage', 'Wing_R', 'Wing_L', 'Boom_R', 'Boom_L', 'VTail_R', 'VTail_L']
groups = {g: {} for g in GROUPS}; extras = {g: {} for g in GROUPS}
for i, n in enumerate(names):
    part = n.split('/')[-2]; g = next(g for g in GROUPS if part.endswith('_' + g))
    s = cq.Shape.importBrep(f'orig/{i:03d}.brep')
    if part.startswith('UM2807') or 'Prop_Disk' in part: extras[g][part] = s; continue
    groups[g][part] = s
removed = []
for g in ('Boom_R', 'Boom_L'):
    removed.append(groups[g].pop(f'Landing_Feet_TPU_{g}'))                 # R16: TPU landing feet removed
# R16: joiner shortened to Y +-46 (wing elbow spigots plug into its bore from each side)
groups['Fuselage']['Wing_Joiner_CFRP_OD12_Fuselage'] = tube_between((310, -46.0, 4.2), (310, 46.0, 4.2), 6.0, 5.0).val()
for side in ('R', 'L'):
    g = f'Wing_{side}'; d = f'out/wing_{side}'
    groups[g] = {f'{f[:-5]}_{g}': cq.Shape.importBrep(f'{d}/{f}') for f in sorted(os.listdir(d)) if f.endswith('.brep')}
# R16 landing gear (build_gear.py): adds legs/sockets/doublers/pads, replaces boom lower halves + fuselage shells (leg holes)
GEAR = '/home/claude/work/out/gear'
for g in os.listdir(GEAR) if os.path.isdir(GEAR) else []:
    if not os.path.isdir(f'{GEAR}/{g}'): continue
    for f in sorted(os.listdir(f'{GEAR}/{g}')):
        if f.endswith('.brep'): groups[g][f[:-5]] = cq.Shape.importBrep(f'{GEAR}/{g}/{f}')
top = cq.Assembly(name='RescU_R16_Full_Aircraft'); bom = []
for g in GROUPS:
    sub = cq.Assembly(name=g)
    for nm, s in groups[g].items():
        m, rho, col = mat(nm); alpha = 0.35 if ('Skin' in nm or 'Shell' in nm) else 1.0
        sub.add(s, name=nm, color=cq.Color(*col, alpha) if alpha < 1 else cq.Color(*col))
        v = pvol(s); c = s.Center() if rho > 0 else None; bb = s.BoundingBox()
        bom.append(dict(group=g, part=nm, material=m, density_g_cm3=rho, volume_mm3=round(v, 1), mass_g=round(v*rho/1000, 2),
                        cx=round(c.x, 1) if c else '', cy=round(c.y, 1) if c else '', cz=round(c.z, 1) if c else '',
                        bbox=f'{bb.xmin:.0f}..{bb.xmax:.0f} / {bb.ymin:.0f}..{bb.ymax:.0f} / {bb.zmin:.0f}..{bb.zmax:.0f}'))
    for nm, s in extras[g].items():
        sub.add(s, name=nm, color=cq.Color(0.95, 0.6, 0.3, 0.25) if 'Prop' in nm else cq.Color(0.45, 0.47, 0.52))
    top.add(sub, name=g)
os.makedirs('deliver', exist_ok=True)
with open('deliver/RescU_R16_BOM_CAD_masses.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(bom[0])); w.writeheader(); w.writerows(bom)
json.dump(bom, open('out/bom.json', 'w'), indent=1)
print('parts', len(bom), 'structure g', round(sum(r['mass_g'] for r in bom), 1))
for g in GROUPS: print(g, round(sum(r['mass_g'] for r in bom if r['group'] == g), 1))
pickle.dump({g: {k: None for k in v} for g, v in groups.items()}, open('out/groups.pkl', 'wb'))
if '--nostep' not in sys.argv:
    top.save('deliver/RescU_R16_Full_Aircraft.step'); print('saved step')
