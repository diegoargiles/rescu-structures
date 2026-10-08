"""Compare lightweight glass candidates without changing the baseline V3 design.

Exploration only. Keep existing material assumptions, loads and 3.2 kg minimum
load-sizing floor. Report missing fuselage/core/joints and failed screens.
"""
import json
from dataclasses import replace
from pathlib import Path
import RescU_Structures_V2 as v2
import RescU_Structures_V3 as v3
target=2.76
baseline=v3.aircraft_mass()
original=v2.run_analysis()
matched_v2=v2.run_analysis(p={**v2.P,'battery_mass_kg':v3.P['battery_mass_kg']})
nonstruct=sum(p.mass_kg for p in matched_v2['components'])-matched_v2['structural_masses']['structural_total_kg']
_,old=v2.compute_structural_masses()
retained=sum(p.mass_kg for p in old if p.name in {'Fuselage shell','Motor arm R','Motor arm L','Payload mount plate'})
tail=v3.panel_mass(v3.TAIL_SKIN,v3.FOAMS['H60'],'NACA0010')['total_kg']
wing_budget=(target-nonstruct)/1.1-retained-tail
rows=[]
configs=[('163gsm x5',(0.,0.,45.,0.,0.),.000179,.291),
         ('163gsm x4',(0.,45.,45.,0.),.000179,.291),
         ('163gsm x3',(0.,45.,0.),.000179,.291),
         ('80gsm x3',(0.,45.,0.),.000088,.143),
         ('80gsm x2',(0.,0.),.000088,.143),
         ('80gsm x1',(0.,),.000088,.143)]
for name,angles,t,mass in configs:
    s=replace(v3.WING_SKIN,name=name,angles=angles,ply_thickness=t,ply_mass=mass)
    totals,cases=v3.cases(s)
    row={'candidate':name,'known_aircraft_mass_kg':totals['known_mass_lower_bound_kg'],
         'sizing_mass_kg':totals['sizing_mass_kg'],
         'wing_total_kg':v3.panel_mass(s,v3.FOAMS['H60'])['total_kg'],
         'wing_tip_deflection_nominal_mm':cases[0]['tip_total_limit_mm'],
         'wing_tip_deflection_70pct_stiffness_mm':cases[0]['tip_total_limit_mm']/.7,
         'max_ply_index_all_cases':max(c['ply_failure_index_ultimate'] for c in cases),
         'max_core_shear_index_all_cases':max(c['core_shear_utilization_ultimate'] for c in cases),
         'all_four_screens_all_cases_pass':all(c['screen_status']=='PASS' for c in cases),
         'wing_deflection_70pct_stiffness_pass':cases[0]['tip_total_limit_mm']/.7<=35,
         'overall_status':'UNRESOLVED; not a build recommendation'}
    rows.append(row)
# Density-only bounds do not approve a lower grade or credit hollowed shear paths.
foam_parts=sum(c['mass_kg'] for c in baseline['components'] if c['name'] in {'Wing foam','V-tail foam'})
data={'target_takeoff_mass_kg':target,'v2_calculated_mass_kg':original['total_mass_kg'],
      'confirmed_battery_mass_kg':v3.P['battery_mass_kg'],
      'v2_same_confirmed_battery_mass_kg':matched_v2['total_mass_kg'],
      'v3_calculated_known_mass_kg':baseline['known_mass_lower_bound_kg'],
      'nonstructural_code_mass_kg':nonstruct,'target_structural_budget_kg':target-nonstruct,
      'retained_fuselage_arms_plate_kg':retained,'current_tail_total_kg':tail,
      'remaining_both_wings_budget_kg_with_current_10pct_hardware_allowance':wing_budget,
      'current_accounted_wing_tail_foam_kg':foam_parts,
      'upper_bound_wing_tail_foam_saving_if_all_removed_kg':foam_parts,
      'density_only_saving_H60_to_48kg_m3_kg':foam_parts*(1-48/60),
      'not_yet_allocated':['Fuselage foam','Designed joints/inserts','Unreconciled installed equipment, wiring and battery accessories'],
      'candidate_screens':rows,
      'warnings':['Existing 3.2 kg minimum sizing floor retained; mass target is not used to reduce test loads',
                  'Very thin skins retain the same assumed cured properties and intact closed section',
                  'Buckling/wrinkling, adhesive, root joints and gust/aeroelasticity are unverified',
                  'Current 200g reserve not included in the 2.76kg mass-budget calculation']}
out=Path(__file__).resolve().parent/'results'/'mass_target';out.mkdir(parents=True,exist_ok=True)
(out/'exploration.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
print(json.dumps(data,indent=2))
