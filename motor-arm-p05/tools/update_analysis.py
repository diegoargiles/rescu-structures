"""Reconcile the P05 physical BOM with P04; reuse the unchanged beam solver."""
import sys,json,math,csv,copy
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R/'baseline-p04' if (R/'baseline-p04').exists() else R.parent if (R.parent/'RescU_Structures_V4.py').exists() else R.parent/'v4-attachments';sys.path.insert(0,str(P))
import RescU_Structures_V4 as v
a=json.loads((R/'reports/assembly_checks.json').read_text());c=json.loads((P/'inputs.json').read_text());s=json.loads((P/'data/cad_snapshot_p04.json').read_text());previous=json.loads((P/'reports/p04/results.json').read_text())
oldnames=[r['name'] for r in s['structural_parts'] if r['name'].startswith(('MotorShoe_','VTOL_Arm_','ArmSaddle_'))]
removed=[r for r in s['structural_parts'] if r['name'] in oldnames];s['structural_parts']=[r for r in s['structural_parts'] if r['name'] not in oldnames]
# P05 components use exact generated volumes; all hardware density assumptions explicit.
for r in a['components']:
 if r['category']!='structure':continue
 density=r['mass_kg']/r['volume_mm3']*1e9
 c['densities_kg_m3'][r['material']]=density
 # Current mass/beam checks need mass and CG; retain zero intrinsic inertia here.
 # Detailed assembly inertia remains available from native solids if needed.
 s['structural_parts'].append(dict(name=r['name'],material=r['material'],density_kg_m3=density,volume_mm3=r['volume_mm3'],mass_kg=r['mass_kg'],x_m=r['centroid_mm'][0]/1000,y_m=r['centroid_mm'][1]/1000,z_m=r['centroid_mm'][2]/1000,valid=r['valid'],inertia_centroid_kgm2=[[0.]*3 for _ in range(3)],source='P05 assembly solid: '+r['basis'],attachment_group='P05 motor-arm components'))
removed_allowances=[];allowances=[]
for r in c['structural_allowances']:
 if r['name']=='Lift mount screws and washers':removed_allowances.append(r);continue
 if r['name']=='Arm/wing joint adhesive and fillets':
  # Preserve original total12g as a residual above the now explicit arm bond solids.
  r=dict(r);bond=sum(q['mass_kg'] for q in a['components'] if q['name'].startswith('SaddleBond_'))
  r['mass_kg']-=bond;r['name']='Wing saddle/rib adhesive residual above explicit arm bondlines';r['source']='P04 12g adhesive/fillet budget less explicit P05 saddle bond mass; no double count'
 allowances.append(r)
allowances.append(dict(name='P05 rail bond fillets and wire strain relief',mass_kg=.004,x_m=.395,y_m=0,z_m=.005,source='Proposed4g total:2g excess/fillets +2g clips/strain relief; excludes explicit bondline solids and motor leads',category='structural_allowance',status='assumed process/install residual; not weighed'))
c['structural_allowances']=allowances
for r in c['components']:
 if r['name'].startswith('VTOL motor+prop'):
  # 52g motor and existing prop estimate retained, no envelope-density mass.
  r['source']='UM2807 supplier52g including wires + inherited26.0816g prop estimate; mount hardware now in P05 structure'
  r['status']='motor nominal supplied mass verified to listing; prop mass remains estimate';r['z_m']=(11.+10.)/1000
  # Combined installed location: motor body center20.5mm; prop datum35.5mm.
  r['z_m']=(.052*.021+(.0780816-.052)*.036)/.0780816
c['version']='P05 motor-arm detailed review study 2026-10-23'
c['additional_requirements']+=['UM2807 1700KV supplier maximum21V/5S conflicts with existing6S supply25.2V full; no approved operating point','Motor screw insertion2.5mm and mount torque unverified; clamp preload/crushing/slip/thermal/fatigue tests required']
s['source_file']='RescU_P05_Motor_Arm_Assembly.FCStd + retained P04 geometry';s['source_sha256']=a['native_sha256'];s['scope']='Composite accounting snapshot: retained P04 parts + replacement P05 assembly. No single full-aircraft native is implied.'
(R/'data/inputs_p05.json').write_text(json.dumps(c,indent=2));(R/'data/accounting_snapshot_p05.json').write_text(json.dumps(s,indent=2))
rows,m=v.mass_ledger(c,s);cases,arms,thrust,envelope,plate,support=v.load_screens(c,s,m,160)
# Motor joint screens: deliberately separate demands from assumed capacity.
F=c['loads']['alternate_total_vtol_thrust_N']/4*c['loads']['vtol_thrust_multiplier'];Q=60/(2*math.pi*1700)*62
rbolt=.0095;shear=Q/(4*rbolt);tensile=F/4;As=5.03
preload_each=100.;preload_max_each=150.;mu=.2;rail_area=2*28*4;normal=2*preload_each
torque_capacity=mu*(max(normal-F,0)*.013+normal*.010) # top/bottom contact effective radii13/10 mm, assumes full preload
stress_strip=1.5*F*22/(20*3.**2)
capacity70=70.
screens=dict(thrust_scenario_N=F,torque_scenario_Nm=Q,torque_scenario_basis='Kt*62A: phase-current/drive convention unknown; supplier62A is3s limit. Not verified operating torque.',motor_screw_axial_each_N=tensile,motor_screw_torque_shear_each_N=shear,motor_screw_nominal_tensile_stress_MPa=tensile/As,motor_screw_nominal_shear_stress_MPa=shear/As,thread_engagement_mm=2.5,thread_pullout_status='UNKNOWN: safe depth, base material, thread quality and preload unspecified',plate_strip_bending_MPa=stress_strip,glass_bending_assumption_MPa=capacity70,plate_strip_utilization=stress_strip/capacity70,top_plate_clamp_preload_bending_MPa=6*preload_max_each*11/(20*3**2),lower_strap_clamp_preload_bending_MPa=6*preload_max_each*16.5/(24*4**2),clamp_bending_method="Maximum150N per clamp screw: upper11mm cantilever/20mm strip/3mm thickness; lower16.5mm cantilever/24mm strip/4mm thickness. No local prying or laminate failure analysis.",plate_strip_method='Simply supported22mm inner-rail span,20mm effective strip, central thrust; concentrated screw/washer and clamp prying omitted',rail_bond_avg_shear_from_torque_MPa=(Q*1000/26)/(28*4),rail_bond_shear_assumption_MPa=2.,clamp_preload_per_screw_assumption_N=preload_each,clamp_total_normal_assumption_N=normal,clamp_max_preload_each_assumption_N=preload_max_each,friction_coefficient_assumption=mu,friction_torque_capacity_assumption_Nm=torque_capacity,friction_torque_utilization=Q/torque_capacity,upper_contact_pressure_assumption_MPa=2*preload_max_each/rail_area,lower_contact_pressure_assumption_MPa=2*preload_max_each/(24*30),CFRP_crush_status='No qualified transverse/edge compression capacity; clamp preload cannot be specified from this screen',saddle_effective_area_mm2=720.,saddle_effective_area_basis='24x30 top +24x30 bottom,50% effective area factor; peel/reversed load sharing not qualified')
xf=.3564;xr=.410;reactions=[]
for label,forces in [('both',[F,F]),('front only',[F,0]),('rear only',[0,F])]:
 rear=sum(f*(x-xf) for f,x in zip(forces,[.235,.555]))/(xr-xf);front=sum(forces)-rear
 reactions.append(dict(case=label,front_N=front,rear_N=rear,force_residual_N=front+rear-sum(forces),moment_residual_Nm=rear*(xr-xf)-sum(f*(x-xf) for f,x in zip(forces,[.235,.555]))))
screens['arm_reactions']=reactions;screens['saddle_avg_bond_shear_MPa']=max(abs(r[k]) for r in reactions for k in ['front_N','rear_N'])/720.
# Hardware totals and explicit subtraction identities guard reserve/allowance duplication.
newphysical=sum(r['mass_kg'] for r in a['components'] if r['category']=='structure');oldphysical=sum(r['mass_kg'] for r in removed)
newbond=sum(r['mass_kg'] for r in a['components'] if r['name'].startswith('SaddleBond_'))
expected=newphysical-oldphysical-.012-newbond+.004
assert abs(m['structural_budget_kg']-previous['mass']['structural_budget_kg']-expected)<1e-10
assert abs(m['accounted_aircraft_kg']-previous['mass']['accounted_aircraft_kg']-expected)<1e-10
assert abs(m['reserve_kg']-.2)<1e-10
assert len({r['name'] for r in rows})==len(rows)
assert sum(r['name'].startswith('VTOL motor+prop') for r in rows)==4
assert all(abs(r['mass_kg']-.0780816)<1e-10 for r in rows if r['name'].startswith('VTOL motor+prop'))
result=dict(version=c['version'],overall_status='REVIEW CANDIDATE; no qualified operational release',mass=m,before_P04=previous['mass'],removed_P04_parts=oldnames,removed_P04_solid_mass_kg=oldphysical,added_P05_solid_mass_kg=newphysical,removed_lift_hardware_allowance_kg=.012,saddle_adhesive_reclassification_kg=newbond,new_process_residual_kg=.004,structural_delta_kg=expected,components=rows,load_cases=cases,arm_cases=arms,thrust_scenarios=thrust,joint_screens=screens,accounting_tests='PASS: replacement identity, aircraft delta, unique names, four motor/prop rows unchanged, reserve counted once',inertia_status='P05 snapshot stores zero intrinsic tensors for new parts; this report does not claim an updated aircraft inertia tensor.',electrical_status='UNRESOLVED:6S full25.2V exceeds supplied1700KV21V maximum',retained_P04_limits='Other P04 interfaces/overlaps and ideal beam assumptions remain. No new stiffness credit from motor mounts.')
(R/'reports/results.json').write_text(json.dumps(result,indent=2))
with (R/'reports/mass_components.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['name','category','material','mass_kg','x_m','y_m','z_m'],extrasaction='ignore');w.writeheader();w.writerows(rows)
print(json.dumps(dict(mass=m,structural_delta_g=expected*1000,joint_screens=screens),indent=2))
