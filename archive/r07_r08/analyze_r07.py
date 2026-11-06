from pathlib import Path
import json,csv,math,numpy as np
base=Path(__file__).resolve().parent;out=base/'r07_study'
m6=json.loads((base/'r06_lightweight/parts.json').read_text());m7=json.loads((out/'parts.json').read_text())
oldm={r['part']:float(r['mass_g']) for r in csv.DictReader((base/'r04_input/mass_items.csv').open())}
def cat(n,d):
 if n.startswith('Arm_'):return 'Arm tubes'
 if d['group'] in ['Front','Rear']:return 'Motor mounts and ESC retention'
 if 'sleeve_X' in n:return 'Internal clamp reinforcement'
 if any(s in n for s in ['CFRP_motor_rib','Bonded_spar_sleeve','rib_doubler','axial_stop']):return 'Rib, sleeve, doublers and stops'
 return 'Wing clamps and fasteners'
rows=[]
for ver,meta in [('R06',m6),('R07',m7)]:
 for n,d in meta.items():
  mass=oldm.get(n) if ver=='R06' and d['group']=='R04' else d.get('mass_g')
  if mass is not None:rows.append(dict(revision=ver,category=cat(n,d),part=n,quantity_both_arms=2,unit_mass_g=mass,total_mass_g=2*mass))
budgets={v:{} for v in ['R06','R07']}
for r in rows:budgets[r['revision']][r['category']]=budgets[r['revision']].get(r['category'],0)+r['total_mass_g']
allowance={'Adhesive and bond fillets':6,'Isolation liners':2,'Local skin edge reinforcement':4,'Band buckles, tails and retention detail':8}
for v in budgets:budgets[v]['Modeled subtotal']=sum(budgets[v].values());budgets[v]['Planning allowance']=sum(allowance.values());budgets[v]['Budget total']=budgets[v]['Modeled subtotal']+sum(allowance.values())
def table(name,rs):
 with (out/(name+'.csv')).open('w',newline='') as f:
  w=csv.DictWriter(f,rs[0].keys());w.writeheader();w.writerows(rs)
table('Complete_Mass_Ledger',rows)
cases=[];sections=[]
for label,b,h,t in [('Rect30x20x1',20,30,1),('Rect25x20x1',20,25,1),('Rect25x15x1',15,25,1),('Round25x1',25,25,1),('Round30x1',30,30,1)]:
 if label.startswith('Round'):
  area=math.pi*(b*b-(b-2*t)**2)/4;Iy=Iz=math.pi*(b**4-(b-2*t)**4)/64;J=2*Iy;Am=math.pi*(b-t)**2/4
 else:
  area=b*h-(b-2*t)*(h-2*t);Iy=(b*h**3-(b-2*t)*(h-2*t)**3)/12;Iz=(h*b**3-(h-2*t)*(b-2*t)**3)/12
  Am=(b-t)*(h-t);J=4*Am**2/(2*(b+h-2*t)/t)
 sections.append(dict(section=label,area_mm2=area,I_vertical_mm4=Iy,I_lateral_mm4=Iz,J_torsion_mm4=J,both_tubes_mass_g=area*350*1.6/1000*2))
 for name,Ff,Fr in [('both',17.3,17.3),('front_only',17.3,0),('rear_only',0,17.3),('front_full_rear_half',17.3,8.65),('front_half_rear_full',8.65,17.3)]:
  rb=(Ff*(235-335)+Fr*(555-335))/70;ra=Ff+Fr-rb
  xx=np.linspace(220,570,1401);loads=[(235,Ff),(335,-ra),(405,-rb),(555,Fr)]
  M=sum(P*np.maximum(xx-a,0) for a,P in loads)
  def raw(x,E):return sum(P*np.maximum(np.asarray(x)-a,0)**3/(6*E*Iy) for a,P in loads)
  def displacement(x,E):
   c1=-(raw(405,E)-raw(335,E))/70;c2=-raw(335,E)-c1*335
   return raw(x,E)+c1*np.asarray(x)+c2
  assert abs(sum(P for a,P in loads))<1e-9
  assert abs(sum(P*a for a,P in loads))<1e-8
  assert max(abs(displacement(np.array([335,405]),70000)))<1e-9
  if name=='rear_only':
   expected=Fr*150**2*(150+70)/(3*70000*Iy)
   assert abs(abs(displacement(555,70000))-expected)<1e-9
  # 10 mm spanwise thrust eccentricity, with torsion fixed at nearest wing clamp.
  twists=[Ff*10*100/(4000*J),Fr*10*150/(4000*J)]
  cases.append(dict(section=label,case=name,Ffront_N=Ff,Frear_N=Fr,RA_N=ra,RB_N=rb,max_M_Nmm=float(max(abs(M))),bending_stress_MPa=float(max(abs(M))*h/2/Iy),max_deflection_mm_E70GPa=float(max(abs(displacement(xx,70000)))),front_deflection_mm_E70GPa=float(displacement(235,70000)),rear_deflection_mm_E70GPa=float(displacement(555,70000)),max_deflection_mm_E40GPa=float(max(abs(displacement(xx,40000)))),twist_deg_G4GPa_e10mm=max(twists)*180/math.pi,torsion_shear_MPa_e10mm=max(Ff,Fr)*10/(2*Am*t)))
table('Tube_Section_Trade',sections);table('Beam_Load_Cases',cases)
# Explicit sampled preload/contact sensitivity; not a torque specification.
contact=[]
for P in [25,50,100,200]:
 for mu in [.15,.3]:
  N=2*P;area=10*20;p=N/area
  contact.append(dict(preload_per_bolt_N=P,friction_coefficient=mu,normal_force_per_contact_face_N=N,conservative_single_face_axial_friction_N=mu*N,two_face_ideal_axial_friction_N=2*mu*N,mean_contact_pressure_MPa=p,unsupported_face_strip_stress_MPa=.75*p*18**2,unsupported_face_strip_deflection_mm_Etransverse10GPa=5*p*18**4/(32*10000),note='Bare 1 mm face; simply supported strip; sleeve support NOT credited'))
table('Clamp_Preload_Sensitivity',contact)
basecases=[r for r in cases if r['section']=='Rect30x20x1'];worst=max(max(abs(r['RA_N']),abs(r['RB_N'])) for r in basecases)
# Wing clevis bearing, shear, and flange prying demands.
joint=dict(max_wing_reaction_N=worst,clevis_bolt_double_shear_MPa=worst/(2*math.pi*3**2/4),rib_bearing_MPa_t1p7=worst/(3*1.7),aluminum_clevis_bearing_MPa_t2p35=worst/(2*3*2.35),clamp_external_tension_N_per_bolt_equal_share=worst/2,flange_bending_MPa_external_only=6*(worst/2)*(14.5-11.2)/(10*4**2),flange_bending_MPa_with_assumed100N_preload=6*(100+worst/2)*(14.5-11.2)/(10*4**2),axial_slip_assumed_demand_N=10,minimum_per_bolt_preload_N_mu0p15_one_face=10/(2*.15),minimum_per_bolt_preload_N_mu0p3_one_face=10/(2*.3),motor_torque_scenario_Nm=.2,motor_torque_lateral_cantilever_deflection_mm=.2*1000*150**2/(2*70000*sections[0]['I_lateral_mm4']))
oldloads=json.loads((base/'r04_input/analysis_results.json').read_text())['load_cases']
result={'mass_budget_both_arms_g':budgets,'allowances_both_arms_g':allowance,'sections':sections,'beam_cases':cases,'joint_demands':joint,'preload_sensitivity':contact,'inherited_rib_spar_demands':oldloads,'scope':'Linear analytical screens; no laminate allowables, FEA, proof test, modal test or flight qualification. Thrust-only cases use provisional 17.3 N/motor; mass/inertia and landing loads excluded. E=40/70 GPa and G=4 GPa are sensitivity assumptions, not supplier properties.'}
(out/'analysis.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'mass':budgets,'joint':joint,'baseline_beam':basecases,'sections':sections},indent=2))
