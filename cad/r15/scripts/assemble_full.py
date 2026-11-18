import cadquery as cq, os, json, csv, numpy as np, sys, re
from vol import pvol
OUT = '/home/claude/full/out'; BOOM = '/home/claude/cadwork/out'
MAT = {  # name pattern -> (material, density g/cm3, colour)
 'XPS': ('Ravatherm XPS', 0.032, (0.93, 0.80, 0.55)), 'Foam': ('EVA foam', 0.10, (0.3, 0.3, 0.3)),
 'PTFE': ('PTFE tube', 2.2, (0.95, 0.95, 0.95)), 'TPU': ('TPU 95A printed ~35% gyroid', 0.45, (0.15, 0.15, 0.15)),
 '6061': ('Al 6061-T6', 2.70, (0.80, 0.80, 0.84)), 'M3': ('Steel', 7.85, (0.55, 0.55, 0.60)), 'Bolt': ('Steel', 7.85, (0.55, 0.55, 0.6)),
 'Screw': ('Steel', 7.85, (0.55, 0.55, 0.60)), 'Pin_D3': ('Steel', 7.85, (0.6, 0.6, 0.65)), 'Compression': ('Al 6061-T6', 2.70, (0.8, 0.8, 0.84)),
 'Fillet': ('Microballoon epoxy', 0.60, (0.9, 0.88, 0.8)), 'Hinge': ('Nylon', 1.15, (0.95, 0.95, 0.9)),
 'CFRP': ('CFRP', 1.60, (0.12, 0.12, 0.14)), 'Boom_': ('CFRP wet layup', 1.50, (0.13, 0.15, 0.17)),
 'Channel': ('CFRP', 1.50, (0.85, 0.75, 0.35)), 'Cover': ('CFRP', 1.50, (0.35, 0.37, 0.40)), 'Rib_Extended': ('CFRP', 1.60, (0.3, 0.3, 0.32)),
 'Joiner': ('CFRP', 1.60, (0.12, 0.12, 0.14)), 'Stop': ('GFRP', 1.85, (0.75, 0.85, 0.75)),
 'GFRP': ('GFRP', 1.85, (0.86, 0.90, 0.95)), 'Strips': ('GFRP', 1.85, (0.75, 0.85, 0.75)),
}
def mat(name):
    if name.startswith('REF'): return ('REFERENCE (no structural mass)', 0.0, (0.95, 0.6, 0.3))
    for k in ['XPS', 'Foam', 'PTFE', 'TPU', '6061', 'Compression', 'Fillet', 'Hinge', 'Pin_D3', 'Bolt', 'Screw', 'M3', 'Channel', 'Cover', 'Rib_Extended', 'Boom_', 'Joiner', 'Stop', 'Strips', 'CFRP', 'GFRP']:
        if k in name: return MAT[k]
    return ('GFRP', 1.85, (0.86, 0.9, 0.95))
def load_dir(d):
    return {f[:-5]: cq.Shape.importBrep(f'{d}/{f}') for f in sorted(os.listdir(d)) if f.endswith('.brep')}
groups = {}
groups['Fuselage'] = load_dir(f'{OUT}/fuselage')
for side, s in (('R', 'PosY'), ('L', 'NegY')):
    groups[f'Wing_{side}'] = load_dir(f'{OUT}/wing_{side}')
    b = load_dir(f'{BOOM}/{s}')
    for k in ('REF_Wing_OML', 'REF_Main_Spar_local', 'REF_Aft_Tube_local'): b.pop(k, None)
    b.pop('Motor_Rib_Extended_Tab', None)
    groups[f'Boom_{side}'] = {('Boom_Junction_Fillets' if k == 'Junction_Fillets' else k): v for k, v in b.items()}
    groups[f'VTail_{side}'] = load_dir(f'{OUT}/tail_{side}')
motor = cq.Shape.importBrep('/home/claude/cadwork/motor/um.brep')
MOTOR = cq.Assembly(motor, name='UM2807_Lift_Motor', color=cq.Color(0.45, 0.47, 0.52))
top = cq.Assembly(name='RescU_R15_Full_Aircraft')
bom = []
for g, parts in groups.items():
    sub = cq.Assembly(name=g)
    for k, s in parts.items():
        m, rho, col = mat(k)
        nm = f'{k}_{g}' if not k.endswith(g) else k
        alpha = 0.35 if ('Skin' in k or 'Shell' in k) else 1.0
        sub.add(s, name=nm, color=cq.Color(*col, alpha) if alpha < 1 else cq.Color(*col))
        v = pvol(s); c = s.Center() if rho > 0 else None
        bb = s.BoundingBox()
        bom.append(dict(group=g, part=nm, material=m, density_g_cm3=rho, volume_mm3=round(v, 1), mass_g=round(v*rho/1000, 2),
                        cx=round(c.x, 1) if c else '', cy=round(c.y, 1) if c else '', cz=round(c.z, 1) if c else '',
                        bbox=f'{bb.xmin:.0f}..{bb.xmax:.0f} / {bb.ymin:.0f}..{bb.ymax:.0f} / {bb.zmin:.0f}..{bb.zmax:.0f}'))
    if g.startswith('Boom_'):
        sg = 1 if g.endswith('R') else -1
        for xm, tag in ((170, 'Front'), (600, 'Rear')):
            sub.add(MOTOR, name=f'UM2807_{tag}_{g}', loc=cq.Location(cq.Vector(xm, sg*265, -12.8)))
            disk = cq.Workplane().circle(127).extrude(1).translate((xm, sg*265, -12.8+29.5)).val()
            sub.add(disk, name=f'REF_Prop_Disk_10in_{tag}_{g}', color=cq.Color(0.95, 0.6, 0.3, 0.25))
    top.add(sub, name=g)
os.makedirs(f'{OUT}/deliver', exist_ok=True)
with open(f'{OUT}/deliver/RescU_R15_BOM_CAD_masses.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(bom[0])); w.writeheader(); w.writerows(bom)
json.dump(bom, open(f'{OUT}/bom.json', 'w'), indent=1)
tot = sum(r['mass_g'] for r in bom); print('structural+hardware mass g', round(tot, 1))
for g in groups: print(g, round(sum(r['mass_g'] for r in bom if r['group'] == g), 1))
if '--nostep' not in sys.argv:
    top.save(f'{OUT}/deliver/RescU_R15_Full_Aircraft.step'); print('saved')
