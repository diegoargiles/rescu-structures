"""Numerical and accounting verification; does not establish physical design validity."""
from pathlib import Path
import math,json,copy
import RescU_Structures_V4 as v
root=Path(__file__).resolve().parent;c=v.read(root/'inputs.json');s=v.read(root/'data/cad_snapshot.json');rows,m=v.mass_ledger(c,s)
def close(a,b,tol=1e-10):assert math.isclose(a,b,rel_tol=tol,abs_tol=tol),(a,b)
for r in rows:
 if r['category']=='CAD_structure':close(r['mass_kg'],r['volume_mm3']*1e-9*c['densities_kg_m3'][r['material']])
close(m['cad_structure_kg'],.6159305596834705)
close(sum(r['mass_kg'] for r in rows),m['accounted_aircraft_kg'])
close(m['structural_budget_kg'],m['cad_structure_kg']+m['structural_allowances_kg']+m['additional_structure_kg'])
for i,k in enumerate(['x_m','y_m','z_m']):close(m['aircraft_cg_m'][i]*m['accounted_aircraft_kg'],sum(r['mass_kg']*r[k] for r in rows))
released=[r for r in rows if r['name']!='Payload'];payload=next(r for r in rows if r['name']=='Payload')
close(sum(r['mass_kg'] for r in released),m['accounted_aircraft_kg']-payload['mass_kg'])
for i,k in enumerate(['x_m','y_m','z_m']):close(v.cg(released)[i]*sum(r['mass_kg'] for r in released),m['aircraft_cg_m'][i]*m['accounted_aircraft_kg']-payload['mass_kg']*payload[k])
c2=copy.deepcopy(c);c2['battery']['measured_complete_pack_mass_kg']=1.;_,m2=v.mass_ledger(c2,s);close(m2['accounted_aircraft_kg']-m['accounted_aircraft_kg'],1.-m['battery_pack_kg'])
c3=copy.deepcopy(c);c3['densities_kg_m3']['GFRP']*=1.1;r3,m3=v.mass_ledger(c3,s)
glass=sum(r['mass_kg'] for r in rows if r.get('material')=='GFRP');close(m3['cad_structure_kg']-m['cad_structure_kg'],glass*.1)
# CAD intrinsic tensor symmetry/positive diagonals; parallel-axis sum around computed CG.
I=[[0.]*3 for _ in range(3)]
for r in rows:
 d=[r[k]-m['aircraft_cg_m'][i] for i,k in enumerate(['x_m','y_m','z_m'])];own=r.get('inertia_centroid_kgm2',[[0.]*3 for _ in range(3)])
 for i in range(3):
  for j in range(3):
   close(own[i][j],own[j][i]);I[i][j]+=own[i][j]+r['mass_kg']*((sum(q*q for q in d) if i==j else 0)-d[i]*d[j])
assert all(I[i][i]>0 for i in range(3))
for i in range(3):
 for j in range(3):close(I[i][j],I[j][i])
# Analytical cantilever comparison: end point force, constant EI, no distributed loads.
y=[i/1000 for i in range(1001)];F=10.;EI=100.;sol=v.beam.cantilever(y,[0.]*len(y),[0.]*len(y),[EI]*len(y),[1e30]*len(y),[1e30]*len(y),points=((1.,F,0.),))
assert abs(sol['bend'][-1]-F/(3*EI))/(F/(3*EI))<1e-5
v.configure(c,s);foam=v.beam.FOAMS['RAVATHERM'];force=m['sizing_aircraft_kg']*v.beam.v2.G*c['loads']['limit_n']/2*c['loads']['wing_force_allowance']
cc=[]
for n in (160,320):cc.append(v.beam.panel_case('Convergence',v.beam.WING_SKIN,foam,force,c['loads']['ultimate_multiplier'],n=n,pitching_cm=v.beam.SCREEN['pitching_cm_bound']))
errs={k:abs(cc[0][k]-cc[1][k])/max(abs(cc[1][k]),1e-12) for k in ['tip_total_limit_mm','tip_twist_limit_deg']+v.UTIL}
assert max(errs.values())<.01,errs
result=dict(status='PASS: accounting and numerical tests only',checks=['CAD volume-density unit conversion','component/structural/aircraft mass conservation','CG moments','payload release moments','measured battery mass sensitivity','material density sensitivity','CAD intrinsic tensor symmetry and parallel-axis assembly','Euler-Bernoulli cantilever point-load solution'],stations=[160,320],relative_changes=errs,physical_validity='UNRESOLVED; not validated by these tests')
(root/'results').mkdir(exist_ok=True);v.dump(root/'results/validation.json',result);print(json.dumps(result,indent=2))
