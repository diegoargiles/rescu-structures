"""P06 mass replacement identity and reversible-load joint demand screens."""
import sys,json,math,csv,hashlib
from pathlib import Path
import FreeCAD as A,Assembly
R=Path(__file__).resolve().parents[1];P=R.parent/'motor-arm-p05';W=(R.parent/'v4-attachments' if (R.parent/'v4-attachments').exists() else R.parent);sys.path.insert(0,str(W));import RescU_Structures_V4 as v
g=json.loads((R/'reports/geometry_checks.json').read_text());validation=json.loads((R/'reports/validation.json').read_text());before=json.loads((P/'reports/results.json').read_text());c=json.loads((P/'data/inputs_p05.json').read_text());s=json.loads((P/'data/accounting_snapshot_p05.json').read_text());d=A.openDocument(str(R/'cad/RescU_P06_Rib_Saddle_Assembly.FCStd'))
def gs(o):
 q=o.Shape.copy();q.Placement=o.getGlobalPlacement()*o.Placement.inverse()*q.Placement;return q
def integral(name,shape,material,density,source):
 center=sum((q.CenterOfMass*q.Volume for q in shape.Solids),A.Vector())/shape.Volume;I=[[0.]*3 for _ in range(3)]
 for q in shape.Solids:
  matrix=q.MatrixOfInertia;dv=q.CenterOfMass-center;a=[dv.x,dv.y,dv.z]
  for i in range(3):
   for j in range(3):I[i][j]+=(getattr(matrix,'A'+str(i+1)+str(j+1))+q.Volume*((sum(x*x for x in a) if i==j else 0)-a[i]*a[j]))*density*1e-15
 return dict(name=name,material=material,density_kg_m3=density,volume_mm3=shape.Volume,mass_kg=shape.Volume*density*1e-9,x_m=center.x/1000,y_m=center.y/1000,z_m=center.z/1000,inertia_centroid_kgm2=I,valid=shape.isValid(),source=source)
for row in g['added_components']:s['structural_parts'].append(integral(row['name'],gs(d.getObject(row['name'])),row['material'],row['density_kg_m3'],'P06 proposed connection, native solid integral at assumed density'))
foam_credit=0.
for revision in g['wing_material_revisions']:
 if revision['material']!='XPS':continue
 assert revision['quantity_screen_pass'], 'Foam credit requires Boolean volume conservation'
 row=next(q for q in s['structural_parts'] if q['name']==revision['original_part']);assert abs(row['volume_mm3']-revision['original_volume_mm3'])<.001
 shape=d.getObject(revision['context_object']).Shape;new=integral(row['name'],shape,row['material'],row['density_kg_m3'],'P06 explicitly pocketed native foam context; replaces P05 quantity once');s['structural_parts'][s['structural_parts'].index(row)]=new;foam_credit+=revision['removed_mass_kg']
epoxy=sum(row['mass_kg'] for row in g['added_components'] if row['material']=='Epoxy');glass=sum(row['mass_kg'] for row in g['added_components'] if row['material']=='GFRP')
budget=next(q for q in c['structural_allowances'] if q['name']=='Wing saddle/rib adhesive residual above explicit arm bondlines');old_budget=budget['mass_kg'];assert old_budget>epoxy
budget['mass_kg']-=epoxy;budget['name']='Wing saddle/rib adhesive residual above P05/P06 explicit bondlines';budget['source']='P05 remaining adhesive budget less explicit P06 bond layers. No extra adhesive counted twice.'
c['version']='P06 rib-saddle splice candidate';c['additional_requirements']+=['P06 eccentric lap-joint peel/fatigue and saddle wall crippling unqualified','Proposed lower-wing skin entry slots need edge reinforcement and wing load redistribution review; no skin mass credit accepted']
s['source_file']='RescU_P06_Rib_Saddle_Assembly.FCStd plus retained aircraft accounting';s['source_sha256']=g['native_sha256'];s['scope']='Arm assembly and revised wing context only; skin quantity retained from P05 because Boolean volume-conservation screen fails.'
rows,m=v.mass_ledger(c,s);cases,arms,thrust,envelope,plate,support=v.load_screens(c,s,m,160)
expected=glass-foam_credit
assert abs(m['structural_budget_kg']-before['mass']['structural_budget_kg']-expected)<1e-9
assert abs(m['accounted_aircraft_kg']-before['mass']['accounted_aircraft_kg']-expected)<1e-9
assert abs(m['reserve_kg']-.2)<1e-10 and len({r['name'] for r in rows})==len(rows)
assert all(abs(r['mass_kg']-.0780816)<1e-10 for r in rows if r['name'].startswith('VTOL motor+prop'))
F=c['loads']['alternate_total_vtol_thrust_N']/4*c['loads']['vtol_thrust_multiplier'];xf=.3564;xr=.410;reactions=[]
for label,forces in [('both',[F,F]),('front only',[F,0]),('rear only',[0,F])]:
 rear=sum(f*(x-xf) for f,x in zip(forces,[.235,.555]))/(xr-xf);front=sum(forces)-rear
 reactions.append(dict(case=label,front_N=front,rear_N=rear,force_residual_N=front+rear-sum(forces),moment_residual_Nm=rear*(xr-xf)-sum(f*(x-xf) for f,x in zip(forces,[.235,.555]))))
demands={'Spar':max(abs(r['front_N']) for r in reactions),'Rear':max(abs(r['rear_N']) for r in reactions)}
joint=[]
for side in ['PosY','NegY']:
 for station in ['Spar','Rear']:
  for ri in [1,2]:
   patches=[p for p in g['bond_interfaces'] if p['side']==side and p['station']==station and p['rib_index']==ri]
   area=min(min(c['area_mm2'] for c in p['contacts']) for p in patches);lower=min(min(c['area_mm2'] for c in p['contacts']) for p in patches if p['bond_parts'][0].startswith('SaddleSpliceBond'))
   length=area/24.;thickness=2.0 if station=='Spar' else 1.5;eccentricity=3.2+thickness/2.
   net_width=24.
   if station=='Spar':
    shape=gs(d.getObject('SplicePlate_'+side+'_'+station+'_Rib'+str(ri)));widths=[]
    for zi in range(25):
     plane=__import__('Part').makePlane(150,100,A.Vector(300,220 if side=='PosY' else -320,5+zi*.25));widths.append(shape.common(plane).Area/thickness)
    net_width=min(widths)
   for share,label in [(.5,'equal split between ribs'),(1.,'one splice carries full station reaction')]:
    force=demands[station]*share;effective=.5*area;tau=force/effective;axial=force/(net_width*thickness);bending=6*force*eccentricity/(net_width*thickness**2);peel=6*force*eccentricity/(24*length**2)
    joint.append(dict(side=side,station=station,rib_index=ri,load_case=label,force_N=force,plate_thickness_mm=thickness,sampled_net_width_mm=net_width,eccentricity_mm=eccentricity,minimum_geometric_contact_area_mm2=area,effective_area_factor_assumption=.5,average_shear_MPa=tau,bond_shear_assumption_MPa=2.,shear_utilization=tau/2.,plate_axial_MPa=axial,plate_eccentric_bending_MPa=bending,combined_plate_strip_MPa=axial+bending,plate_bending_assumption_MPa=70.,plate_utilization=(axial+bending)/70.,peel_demand_proxy_MPa=peel,peel_allowable_MPa=None,peel_status='UNRESOLVED: linear rectangular-lap normal-stress proxy only; variable spar-relief patch, adherend flexibility and edge singularities need refined analysis/tests',lower_lap_contact_area_mm2=lower))
result=dict(version=c['version'],status='DETAILED GEOMETRY CANDIDATE; joint strength and skin-slot reinforcement unresolved',before_P05_mass=before['mass'],mass=m,new_glass_kg=glass,new_epoxy_kg=epoxy,foam_mass_credit_kg=foam_credit,skin_mass_credit_kg=0.,adhesive_residual_before_kg=old_budget,adhesive_residual_after_kg=budget['mass_kg'],structural_delta_kg=expected,accounting_checks='PASS: glass-minus-foam identity, adhesive reallocation, unchanged motor rows, unique names, reserve once',components=rows,load_cases=cases,arm_reactions=reactions,joint_screens=joint,geometry_status=validation['status'],skin_quantity_status=g['skin_mass_credit_policy'],unallocated_future_work='Wing-slot edge reinforcement/sealing and rib-to-spar/skin attachment not modeled or credited. Other P04/P05 open items unchanged.')
(R/'reports/results.json').write_text(json.dumps(result,indent=2));(R/'data/inputs_p06.json').write_text(json.dumps(c,indent=2));(R/'data/accounting_snapshot_p06.json').write_text(json.dumps(s,indent=2))
with (R/'reports/mass_components.csv').open('w',newline='') as f:
 out=csv.DictWriter(f,fieldnames=['name','category','material','mass_kg','x_m','y_m','z_m'],extrasaction='ignore');out.writeheader();out.writerows(rows)
print(json.dumps(dict(mass=m,delta_g=expected*1000,glass_g=glass*1000,epoxy_reallocated_g=epoxy*1000,max_shear_utilization=max(r['shear_utilization'] for r in joint),max_plate_utilization=max(r['plate_utilization'] for r in joint),max_peel_demand_proxy_MPa=max(r['peel_demand_proxy_MPa'] for r in joint),peel='UNQUALIFIED'),indent=2))
