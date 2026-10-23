"""Reopen, solve and compare STEP component centers, not just volumes."""
import sys,json,math
from pathlib import Path
import FreeCAD as A,Part,Assembly
sys.path.append(str(Path(A.getHomePath())/'Mod/Assembly'))
import JointObject
R=Path(__file__).resolve().parents[1];r=json.loads((R/'reports/assembly_checks.json').read_text());d=A.openDocument(str(R/'cad/RescU_P05_Motor_Arm_Assembly.FCStd'))
solves=[]
for name in ['MotorArm_PosY','MotorArm_NegY','MotorArmPair']:
 o=d.getObject(name);solves.append(dict(assembly=name,solve_code=int(o.solve())))
assert all(x['solve_code']==0 for x in solves)
q=Part.Shape();q.read(str(R/'cad/RescU_P05_Motor_Arm_Pair.step'))
left=[dict(volume=s.Volume,center=s.CenterOfMass,valid=s.isValid()) for s in q.Solids];matched=[]
for row in r['components']:
 center=A.Vector(*row['centroid_mm']);volume=row['volume_mm3']
 candidate=min(left,key=lambda s:(s['center']-center).Length+abs(s['volume']-volume)/max(volume,1))
 err=(candidate['center']-center).Length;ve=abs(candidate['volume']-volume)/max(volume,1)
 matched.append(dict(name=row['name'],center_error_mm=err,volume_relative_error=ve));left.remove(candidate)
assert not left
assert max(x['center_error_mm'] for x in matched)<.001,sorted(matched,key=lambda x:-x['center_error_mm'])[:3]
assert max(x['volume_relative_error'] for x in matched)<.001
# Both arms individually respond to constraint solve after an intentional disturbance.
follow=[]
for side in ['PosY','NegY']:
 o=d.getObject('UM2807_'+side+'_Front');before=o.Placement;o.Placement=A.Placement(A.Vector(before.Base.x+2,before.Base.y+3,before.Base.z+1),A.Rotation(5,0,0))
 code=d.getObject('MotorArm_'+side).solve();error=(o.Placement.Base-before.Base).Length;angle=(o.Placement.Rotation.inverted()*before.Rotation).Angle
 assert code==0 and error<1e-5 and angle<1e-5
 follow.append(dict(arm=side,solve_code=int(code),translation_error_mm=error,rotation_error_rad=angle))
valid=all(d.getObject(x['name']).Shape.isValid() for x in r['components']);assert valid
result=dict(status='PASS: native reopen/solver, both-arm perturbation recovery, STEP volume and component positions',reopen_solves=solves,perturbation_tests=follow,native_parts=len(r['components']),fixed_joints=len(r['joints']),ground_constraints=3,STEP_max_component_center_error_mm=max(x['center_error_mm'] for x in matched),STEP_max_component_volume_relative_error=max(x['volume_relative_error'] for x in matched),STEP_all_solids_valid=all(s.isValid() for s in q.Solids),all_native_valid=valid,limits='Tolerance-free fit study; screw-depth, materials, preload, dynamics and actual prop geometry not qualified')
(R/'reports/native_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
