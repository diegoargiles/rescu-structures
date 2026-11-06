"""Supplier-backed candidate axial beam screen; does not change baseline inputs."""
import math,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
E=64000;I=math.pi*(25**4-23**4)/64;rows=[]
for T in [17.3,26]:
 a,b,xf,xr=335,405,170,600
 RB=(T*(xf-a)+T*(xr-a))/(b-a);RA=2*T-RB
 loads=[(xf,T),(a,-RA),(b,-RB),(xr,T)]
 assert abs(sum(v for x,v in loads))<1e-9
 assert abs(sum(x*v for x,v in loads))<1e-7
 raw=lambda x:sum(f*max(x-p,0)**3 for p,f in loads)/(6*E*I)
 c1=-(raw(b)-raw(a))/(b-a);c2=-raw(a)-c1*a
 disp=lambda x:raw(x)+c1*x+c2
 assert max(abs(disp(a)),abs(disp(b)))<1e-9
 M=max(abs(sum(f*max(x-p,0) for p,f in loads)) for x,v in loads)
 rows.append({'per_motor_thrust_N':T,'front_displacement_mm':disp(xf),'rear_displacement_mm':disp(xr),'max_bending_stress_limit_MPa':M*12.5/I,'max_bending_stress_ultimate_MPa':M*12.5/I*1.5})
result={'status':'CANDIDATE ONLY; no strength margin or accepted twist limit','tube_product':'CFT-WF-25-23-1','source':'https://www.easycomposites.us/25mm-23mm-woven-finish-carbon-fiber-tube','axial_modulus_GPa':64,'I_mm4':I,'EI_N_mm2':E*I,'two_boom_mass_g':2*.47*113.1,'axial_tensile_strength_vendor_MPa':650,'compression_allowable_MPa':None,'torsional_strength_MPa':None,'laminate_bearing_allowable_MPa':None,'bond_allowable_MPa':None,'accepted_wing_twist_deg':None,'cases':rows,'ideal_2d_twist_sensitivity':[{'twist_deg':d,'delta_section_Cl_2pi_slope':2*math.pi*math.radians(d)} for d in [.5,1,2]]}
(root/'requirements/material_candidate_screen.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
