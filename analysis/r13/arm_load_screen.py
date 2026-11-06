"""Thrust-only two-support beam comparison. SI loads; geometry mm, stress MPa.
No joint compliance, motor inertia, laminate failure, strength FOS or aircraft release.
"""
import json, math, csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
cfg=json.loads((ROOT/'requirements/load_assumptions.json').read_text())
out=ROOT/'results/r13';out.mkdir(parents=True,exist_ok=True)
rows=[]
T=cfg['per_motor_thrust_N']
for rev in ['R12','R13']:
 a=cfg[rev+'_arm'];xa,xb=a['support_x_mm'];xf=a['front_motor_x_mm'];xr=a['rear_motor_x_mm']
 if a['section']=='round':
  D=a['outer_diameter_mm'];di=D-2*a['wall_mm'];I=math.pi*(D**4-di**4)/64;c=D/2;area=math.pi*(D**2-di**2)/4
 else:
  b=a['width_mm'];h=a['height_mm'];t=a['wall_mm'];I=(b*h**3-(b-2*t)*(h-2*t)**3)/12;c=h/2;area=b*h-(b-2*t)*(h-2*t)
 for name,Ff,Fr in [('balanced_max',T,T),('front_only',T,0),('rear_only',0,T),('front_full_rear_half',T,T/2),('front_half_rear_full',T/2,T)]:
  RB=(Ff*(xf-xa)+Fr*(xr-xa))/(xb-xa);RA=Ff+Fr-RB
  loads=[(xf,Ff),(xa,-RA),(xb,-RB),(xr,Fr)]
  assert abs(sum(f for x,f in loads))<1e-10
  assert abs(sum(x*f for x,f in loads))<1e-8
  M=lambda x:sum(f*max(x-p,0) for p,f in loads)
  maxM=max(abs(M(x)) for x,f in loads)
  row={'revision':rev,'case':name,'Ffront_limit_N':Ff,'Frear_limit_N':Fr,'RA_limit_N':RA,'RB_limit_N':RB,'max_bending_limit_Nm':maxM/1000,'section_I_mm4':I,'axial_stress_limit_MPa':maxM*c/I,'axial_stress_ultimate_MPa':maxM*c/I*cfg['ultimate_multiplier'],'tube_pair_mass_g_rho1600':2*area*a['length_mm']*.0016}
  for E in cfg['arm_E_sensitivity_GPa']:
   raw=lambda x:sum(f*max(x-p,0)**3 for p,f in loads)/(6*E*1000*I)
   C1=-(raw(xb)-raw(xa))/(xb-xa);C2=-raw(xa)-C1*xa
   disp=lambda x:raw(x)+C1*x+C2
   assert abs(disp(xa))<1e-10 and abs(disp(xb))<1e-10
   row['front_deflection_mm_E'+str(E)]=disp(xf);row['rear_deflection_mm_E'+str(E)]=disp(xr)
  rows.append(row)
with (out/'arm_load_comparison.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,rows[0].keys());w.writeheader();w.writerows(rows)
facts={'status':'THRUST-ONLY DEMAND SCREEN; no strength acceptance','force_and_moment_equilibrium':'PASS for all 10 cases','support_displacement_conditions':'PASS at both supports for both stiffness assumptions','cases':rows,'load_factor_examples':[{'bank_deg':p,'n_level_coordinated_turn':1/math.cos(math.radians(p))} for p in [30,45,60]],'positive_limit_total_lift_N_per_kg':cfg['positive_limit_n']*cfg['g_m_s2'],'positive_ultimate_total_lift_N_per_kg':cfg['positive_limit_n']*cfg['g_m_s2']*cfg['ultimate_multiplier'],'warning':'The lift-per-kg figures omit tail/download allocation; no aircraft mass is silently assumed.'}
(out/'arm_load_screen.json').write_text(json.dumps(facts,indent=2))
print(json.dumps({r: max((x for x in rows if x['revision']==r),key=lambda x:max(abs(x['RA_limit_N']),abs(x['RB_limit_N']))) for r in ['R12','R13']},indent=2))
