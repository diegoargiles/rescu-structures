import cadquery as cq, sys, os
sys.argv.append('--nostep')
src=open('/home/claude/full/assemble_full.py').read()
exec(src.split("motor = cq.Shape")[0])
motor = cq.Shape.importBrep('/home/claude/cadwork/motor/um.brep')
top = cq.Assembly(name='RescU')
for g, parts in groups.items():
    for k, s in parts.items():
        m, rho, col = mat(k)
        if k.startswith('REF_Pusher_Prop') or 'Prop_Disk' in k: continue
        top.add(s, name=f'{g}__{k}', color=cq.Color(*col))
for sg, sd in ((1, 'R'), (-1, 'L')):
    for xm in (170, 600):
        top.add(motor, name=f'Boom_{sd}__UM2807_{xm}', loc=cq.Location(cq.Vector(xm, sg*265, -12.8)), color=cq.Color(0.45, 0.47, 0.52))
from cadquery.occ_impl.exporters.assembly import exportGLTF
exportGLTF(top, '/home/claude/render/rescu.glb', binary=True, tolerance=0.25, angularTolerance=0.3)
print('glb', os.path.getsize('/home/claude/render/rescu.glb'))
