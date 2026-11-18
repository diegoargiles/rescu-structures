import os, sys, cadquery as cq
SD = '/home/claude/work/station/out'; D = '/home/claude/work/station/deliver'; os.makedirs(f'{D}/STL', exist_ok=True)
S = {f[:-5]: cq.Shape.importBrep(f'{SD}/{f}') for f in sorted(os.listdir(SD)) if f.endswith('.brep')}
COL = lambda k: (cq.Color(0.91, 0.45, 0.23) if 'PETG' in k else cq.Color(0.1, 0.1, 0.11) if ('EVA' in k or 'Feet' in k)
                 else cq.Color(0.78, 0.8, 0.83) if 'Joining' in k else cq.Color(0.2, 0.21, 0.23))
A = cq.Assembly(name='RescU_Landing_Station')
for k, s in S.items(): A.add(s, name=k, color=COL(k))
A.save(f'{D}/RescU_Landing_Station.step'); print('station step')
# printable STLs in print orientation: boom cradle (identical L/R) local origin, tail rest flipped onto its flat base
c = S['Cradle_Boom_R_PETG'].translate(cq.Vector(-385, -265, -228))
cq.exporters.export(cq.Workplane().add(c), f'{D}/STL/Cradle_Boom_PETG_print_x2.stl', tolerance=0.02, angularTolerance=0.1)
t = S['Cradle_Tail_PETG'].translate(cq.Vector(-1005, 0, -222))
cq.exporters.export(cq.Workplane().add(t), f'{D}/STL/Cradle_Tail_PETG_print_x1.stl', tolerance=0.02, angularTolerance=0.1)
for k in ('Cradle_Boom_R_PETG', 'Cradle_Tail_PETG'):
    bb = S[k].BoundingBox(); print(k, 'size', round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1))
