"""Current RescU structures baseline: CAD mass/CG + preliminary beam/laminate screens.
Python3.10+, standard library only. Run this file; edit inputs.json for assumptions.
CAD geometry changes require a fresh cad_snapshot.json export. Not a flight release.
"""
from pathlib import Path
import argparse,csv,json,math,sys,html,hashlib
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'engine'))
import analytic_v3 as beam

UTIL=['ply_failure_index_ultimate','core_shear_utilization_ultimate','spar_bending_utilization_ultimate','deflection_screen_utilization','twist_screen_utilization']

def read(path):return json.loads(Path(path).read_text())
def dump(path,value):Path(path).write_text(json.dumps(value,indent=2,allow_nan=False),encoding='utf-8')
def cg(rows):
 m=sum(x['mass_kg'] for x in rows)
 if m<=0:raise ValueError('Mass must be positive')
 return [sum(r['mass_kg']*r.get(k,0.) for r in rows)/m for k in ('x_m','y_m','z_m')]
def mac(span,cr,ct):
 taper=ct/cr
 return 2*cr/3*(1+taper+taper*taper)/(1+taper)
def table(headers,rows):
 return '\n'.join(['| '+' | '.join(map(str,headers))+' |','|'+'|'.join('---' for _ in headers)+'|']+['| '+' | '.join(map(str,row))+' |' for row in rows])
def configure(c,s):
 g=s['parameters']['Global_Parameters'];f=s['parameters']['Fuselage_Profile_Parameters'];p=beam.P;loads=c['loads']
 for k,n,scale in [('wingspan_m','WingHalfSpan',.002),('wing_root_chord_m','WingRootChord',.001),('wing_tip_chord_m','WingTipChord',.001),('wing_tip_le_offset_m','WingSweep',.001),('x_main_wing_le_m','WingRootLE',.001),('vtail_half_span_m','TailSpan',.001),('vtail_root_chord_m','TailRootChord',.001),('vtail_tip_chord_m','TailTipChord',.001),('vtail_tip_le_offset_m','TailSweep',.001),('vtail_root_le_x_m','TailRootLE',.001),('vtail_dihedral_deg','TailDihedral',1),('arm_width_y_m','ArmWidth',.001),('arm_height_z_m','ArmHeight',.001),('arm_wall_m','ArmWall',.001),('arm_y_abs_m','ArmY',.001),('front_motor_x_m','FrontMotorX',.001),('rear_motor_x_m','RearMotorX',.001)]:p[k]=g[n]*scale
 p.update(limit_load_factor=loads['limit_n'],ultimate_load_factor=loads['limit_n']*loads['ultimate_multiplier'],top_speed_mps=loads['top_speed_mps'],team_max_vtol_thrust_total_N=loads['baseline_total_vtol_thrust_N'],vtol_structural_thrust_factor=loads['vtol_thrust_multiplier'],arm_support_front_x_m=loads['arm_support_front_x_m'],arm_support_rear_x_m=loads['arm_support_rear_x_m'])
 # Match actual CAD plate bbox; its supports remain an assumption.
 plate=next(r for r in s['structural_parts'] if r['name']=='Payload_MountPlate_PROVISIONAL');bb=plate['bounds_mm']
 p.update(payload_plate_length_x_m=(bb[1]-bb[0])*.001,payload_plate_span_m=(bb[3]-bb[2])*.001,payload_plate_thickness_m=(bb[5]-bb[4])*.001,payload_mass_kg=next(r['mass_kg'] for r in c['components'] if r['name']=='Payload'))
 beam.WING_SKIN=beam.replace(beam.WING_SKIN,ply_thickness=g['WingSkin']*.001/3,ply_mass=c['densities_kg_m3']['GFRP']*g['WingSkin']*.001/3)
 beam.TAIL_SKIN=beam.replace(beam.TAIL_SKIN,ply_thickness=g['TailSkin']*.001/3,ply_mass=c['densities_kg_m3']['GFRP']*g['TailSkin']*.001/3)
 beam.SPAR=beam.replace(beam.SPAR,root_od=g['SparRootOD']*.001,tip_od=g['SparTipOD']*.001,wall=g['SparRootWall']*.001,tip_wall=g['SparTipWall']*.001,bond_thickness=g['Bond']*.001)
 beam.SCREEN.update(wing_force_allowance=loads['wing_force_allowance'],negative_g=loads['negative_n'],tail_panel_normal_CL=loads['tail_CL'])
 mat=c['structural_material_properties'];sk=mat['skin'];sp=mat['spar'];fm=mat['foam']
 for key in ['WING_SKIN','TAIL_SKIN']:
  setattr(beam,key,beam.replace(getattr(beam,key),E1=sk['E1_Pa'],E2=sk['E2_Pa'],G12=sk['G12_Pa'],nu12=sk['nu12'],tensile=sk['tensile_Pa'],compressive=sk['compressive_Pa'],shear=sk['shear_Pa'],strength_knockdown=sk['strength_knockdown']))
 beam.SPAR=beam.replace(beam.SPAR,E=sp['E_Pa'],strength=sp['strength_Pa'],knockdown=sp['knockdown'])
 beam.SCREEN['core_strength_knockdown']=fm['strength_knockdown']
 beam.FOAMS['RAVATHERM']=beam.replace(beam.FOAMS['RAVATHERM'],shear_modulus=fm['shear_modulus_Pa'],shear_strength=fm['shear_strength_Pa'],compression_strength=fm['compression_strength_Pa'])
 beam.v2.MATERIALS['CFRP']=beam.v2.Material('CFRP preliminary assumption',c['densities_kg_m3']['CFRP'],sp['E_Pa'],sp['strength_Pa'])
 beam.FOAMS['RAVATHERM']=beam.replace(beam.FOAMS['RAVATHERM'],density=c['densities_kg_m3']['Ravatherm XPS X H LB'])
 def spar_geometry():
  L=g['WingHalfSpan']*.001;cr=g['WingRootChord']*.001;ct=g['WingTipChord']*.001;cf=beam.SPAR.chord_fraction
  xx,u,l=beam.profile('SD7037');mid=(beam.interp(list(zip(xx,u)),cf)+beam.interp(list(zip(xx,l)),cf))/2
  dx=g['WingSweep']*.001+cf*(ct-cr);dz=L*math.tan(math.radians(g['WingDihedral']))+mid*(ct-cr)
  length=math.sqrt(L*L+dx*dx+dz*dz)
  return dict(projected_halfspan_m=L,tube_length_each_m=length,length_per_span=length/L,root_x_m=g['WingRootLE']*.001+cf*cr,tip_x_m=(g['WingRootLE']+g['WingSweep'])*.001+cf*ct,root_z_section_m=mid*cr,tip_z_section_m=mid*ct)
 if g['WingIncidence']!=0:raise ValueError('Nonzero wing incidence requires updated beam reference frame.')
 beam.spar_geometry=spar_geometry
 # Free cached values if run twice with a different input file in the same process.
 beam._reinforced_section.cache_clear();beam.panel_mass.cache_clear()
 return p

def mass_ledger(c,s):
 rows=[]
 for part in s['structural_parts']:
  row=dict(part,category='CAD_structure',status='CAD solid volume; assumed density; as-modeled geometry')
  rho=c['densities_kg_m3'][part['material']];row['mass_kg']=part['volume_mm3']*1e-9*rho
  # Snapshot inertia used below is rescaled when density changes.
  row['inertia_centroid_kgm2']=[[v*rho/part['density_kg_m3'] for v in line] for line in part['inertia_centroid_kgm2']]
  rows.append(row)
 rows += [dict(x,category='structural_allowance') for x in c['structural_allowances']]
 for x in c['additional_structural_parts']:
  if not all(k in x for k in ['name','mass_kg','x_m','y_m','z_m','source']):raise ValueError('Additional structural parts require mass, centroid and source.')
  rows.append(dict(x,category='additional_structure',status='user-entered structural part; verify source'))
 rows += [dict(x) for x in c['components']]
 bp=s['parameters']['Battery_Parameters_PROVISIONAL'];b=c['battery']
 cell_count=b['series']*b['parallel']
 if cell_count!=12:raise ValueError('Different cell count requires updated CAD packaging.')
 pack=b['measured_complete_pack_mass_kg']
 if pack is None:pack=cell_count*b['cell_max_mass_kg']+b['pack_hardware_allowance_kg'];status='maximum cell-mass budget plus assumed hardware allowance; not measured'
 else:status='user-entered complete pack mass; verify measured source'
 rows.append(dict(name='Battery complete pack budget',mass_kg=pack,x_m=bp['CGX']*.001,y_m=bp['CGY']*.001,z_m=bp['CGZ']*.001,category='nonstructural',source='Molicel M65A + inputs.json',status=status))
 for r in rows:
  if r['mass_kg']<0 or not math.isfinite(r['mass_kg']):raise ValueError('Invalid component mass')
 accounted=sum(r['mass_kg'] for r in rows);sizing=max(c['minimum_sizing_mass_kg'],accounted+c['unallocated_reserve_kg'])
 structural=[r for r in rows if r['category'] in ['CAD_structure','structural_allowance','additional_structure']]
 return rows,dict(cad_structure_kg=sum(r['mass_kg'] for r in rows if r['category']=='CAD_structure'),structural_allowances_kg=sum(r['mass_kg'] for r in rows if r['category']=='structural_allowance'),additional_structure_kg=sum(r['mass_kg'] for r in rows if r['category']=='additional_structure'),structural_budget_kg=sum(r['mass_kg'] for r in structural),accounted_aircraft_kg=accounted,sizing_aircraft_kg=sizing,reserve_kg=sizing-accounted,structural_budget_cg_m=cg(structural),cad_structure_cg_m=cg([r for r in rows if r['category']=='CAD_structure']),aircraft_cg_m=cg(rows),aircraft_cg_status='provisional: actual CAD structural centroids plus estimated installed nonstructural/allowance locations',battery_pack_kg=pack)

def load_screens(c,s,m,nstations):
 p=configure(c,s);foam=beam.FOAMS['RAVATHERM'];loads=c['loads'];mass=m['sizing_aircraft_kg'];G=beam.v2.G
 def wing(n,scale=1.):
  return beam.panel_case(f'Wing {n:g}g',beam.WING_SKIN,foam,mass*G*n/2*loads['wing_force_allowance'],loads['ultimate_multiplier'],n=nstations,pitching_cm=beam.SCREEN['pitching_cm_bound'],stiffness_scale=scale)
 cases=[wing(loads['limit_n']),wing(loads['negative_n']),wing(loads['limit_n'],.7)]
 cases[-1]['case']+=' at70% assumed stiffness'
 tail_area=2*p['vtail_half_span_m']*(p['vtail_root_chord_m']+p['vtail_tip_chord_m'])/2
 q=.5*beam.v2.RHO_AIR*loads['top_speed_mps']**2
 cases.append(beam.panel_case('V-tail at top speed',beam.TAIL_SKIN,foam,q*tail_area*loads['tail_CL']/2,loads['ultimate_multiplier'],shape='NACA0010',n=nstations))
 arms=[];thrust=[]
 for total,label in [(loads['baseline_total_vtol_thrust_N'],'inherited baseline'),(loads['alternate_total_vtol_thrust_N'],'unverified17.30N/motor scenario')]:
  per=total/4;y=p['arm_y_abs_m'];chord=beam.v2.wing_local_chord(y,p=p);xsc=beam.v2.wing_local_le_x(y,p=p)+.35*chord
  for pattern,points in [('both motors',((y,2*per,per*(p['front_motor_x_m']+p['rear_motor_x_m']-2*xsc)),)),('front only',((y,per,per*(p['front_motor_x_m']-xsc)),)),('rear only',((y,per,per*(p['rear_motor_x_m']-xsc)),))]:
   cases.append(beam.panel_case(f'VTOL {total:g}N total rating: {pattern}',beam.WING_SKIN,foam,0.,loads['vtol_thrust_multiplier'],n=nstations,points=points))
  p['team_max_vtol_thrust_total_N']=total
  arm=beam.v2.motor_arm_analysis(p=p);arms.append(dict(total_rating_N=total,**arm,status='beam overhang only; assumed support stations; no hardpoint/crushing qualification'))
  thrust.append(dict(thrust_N=total,status=label,thrust_to_sizing_weight=total/(mass*G),hover_thrust_each_N=mass*G/4))
 p['team_max_vtol_thrust_total_N']=loads['baseline_total_vtol_thrust_N']
 # Numerically bracket the first observed positive-n screen crossing, fixed top-speed Cm.
 # This is a modeled screening boundary, not an allowable aircraft load factor.
 def utilization(n):return max(wing(n)[k] for k in UTIL)
 prev=.25;lo=None;hi=None
 if utilization(prev)<=1:
  for j in range(1,49):
   v=.25+j*.25
   if utilization(v)>1:lo=prev;hi=v;break
   prev=v
  if lo is not None:
   for _ in range(18):
    mid=(lo+hi)/2
    if utilization(mid)<=1:lo=mid
    else:hi=mid
  boundary=lo
 else:boundary=None
 if boundary is not None:
  bc=wing(boundary);governing=max(UTIL,key=lambda k:bc[k])
 else:governing='not bracketed within0.25–12.25g, or low-n screen already fails'
 envelope=dict(positive_n_screen_boundary=boundary,governing=governing,status='IDEAL WING BEAM SCREEN ONLY; not aircraft load-factor capability',searched_upper_n=12.25)
 return cases,arms,thrust,envelope,beam.v2.payload_plate_analysis(p=p),dict(tail_panel_limit_normal_force_N=q*tail_area*loads['tail_CL']/2,tail_panel_ultimate_normal_force_N=q*tail_area*loads['tail_CL']/2*loads['ultimate_multiplier'],pusher_design_axial_load_N=loads['pusher_cruise_thrust_N']*loads['pusher_thrust_multiplier'],support_status='UNRESOLVED: P04 pusher/tail geometry is provisional; load paths, shell transfer and joint strength require closure; no aft-spine stiffness credited')

def run(inputs=ROOT/'inputs.json',snapshot=ROOT/'data/cad_snapshot_p04.json',output=ROOT/'results',nstations=None):
 c=read(inputs);s=read(snapshot)
 if c['unallocated_reserve_kg']<0 or c['battery']['pack_hardware_allowance_kg']<0:raise ValueError('Reserve and battery hardware allowance must be nonnegative.')
 if not all(v>0 for v in c['densities_kg_m3'].values()):raise ValueError('Densities must be positive.')
 output=Path(output);output.mkdir(parents=True,exist_ok=True)
 rows,m=mass_ledger(c,s);n=nstations or c['beam_station_count']
 if n<20:raise ValueError('At least20 beam stations required.')
 cases,arms,thrust,env,plate,support=load_screens(c,s,m,n)
 from attachment_checks import evaluate
 attachment=evaluate(c,s,m,cases) if 'attachment_design' in c else None
 g=s['parameters']['Global_Parameters'];MAC=mac(g['WingHalfSpan']*.002,g['WingRootChord']*.001,g['WingTipChord']*.001);wing_LE=g['WingRootLE']*.001
 target=wing_LE+c['target_cg_aft_wing_LE_m'];np=wing_LE+c['neutral_point_aft_wing_LE_m'];battery=next(r for r in rows if r['name']=='Battery complete pack budget')
 other=[r for r in rows if r is not battery];required=(target*sum(r['mass_kg'] for r in rows)-sum(r['mass_kg']*r['x_m'] for r in other))/battery['mass_kg']
 released=[r for r in rows if r['name']!='Payload'];release_cg=cg(released)
 b=c['battery'];electrical=dict(cells=b['series']*b['parallel'],nominal_voltage_V=b['series']*b['cell_nominal_voltage_V'],full_voltage_V=b['series']*b['cell_full_voltage_V'],capacity_Ah=b['parallel']*b['cell_capacity_Ah'],nominal_energy_Wh=b['series']*b['cell_nominal_voltage_V']*b['parallel']*b['cell_capacity_Ah'],ideal_cell_current_sum_A=b['parallel']*b['cell_continuous_current_A'],current_status=b['current_note'])
 # Intrinsic CAD inertia plus parallel-axis terms; nonstructural/allowance rows are point masses.
 center=m['aircraft_cg_m'];inertia=[[0.]*3 for _ in range(3)]
 for r in rows:
  d=[r[k]-center[i] for i,k in enumerate(['x_m','y_m','z_m'])];intrinsic=r.get('inertia_centroid_kgm2',[[0.]*3 for _ in range(3)])
  for i in range(3):
   for j in range(3):inertia[i][j]+=intrinsic[i][j]+r['mass_kg']*((sum(v*v for v in d) if i==j else 0)-d[i]*d[j])
 bymat={}
 for r in rows:
  if r['category']=='CAD_structure':bymat[r['material']]=bymat.get(r['material'],0)+r['mass_kg']
 warnings=list(c['additional_requirements'])+['CAD material subtotal includes unresolved spar/shell overlaps; allocation not resolved.', 'Left/right main wing skin mass differs0.542g despite symmetric inputs; volume/thickness audit outstanding.', 'P04 localized foam is counted; complete hardpoint and shell qualification remains open.', 'Root beam idealized at aircraft centerline; actual attachment flexibility and trimmed root geometry unresolved.', 'Geometric CAD normal-offset skins and analytical section offsets differ; stiffness/stress are screening approximations.', 'Motor/prop mass placeholders and6S operating data not verified for selected10x3 prop.', 'ESCs are60x30x15mm reservations only; their actual mass remains inside old ESC/wiring allocation.', 'No overall structural PASS. Native P04 reopen/geometry checks do not qualify joints.']
 audit_path=ROOT/'reports/native-audit/candidate_audit.json'
 geometry_audit=read(audit_path) if audit_path.exists() else {}
 audit_current=geometry_audit.get('native_sha256')==s['source_sha256']
 if not audit_current:warnings.append('CAD fit audit missing or stale for this snapshot; rerun audit before accepting geometry.')
 if geometry_audit.get('interferences'):warnings.append(f"P04 fit audit reports {len(geometry_audit['interferences'])} positive-volume intersections; candidate mass is gross, not net installed mass. See reports/p04/REVIEW.md.")
 results=dict(geometry_audit_current=audit_current,geometry_audit=geometry_audit,mass_status='Gross candidate budget; fit/overlap and missing attachments remain unresolved',attachment_checks=attachment,material_property_assumptions=c['structural_material_properties'],version=c['version'],overall_status='UNRESOLVED — preliminary mass budget and structural screening',cad_source=s['source_file'],cad_source_sha256=s['source_sha256'],input_sha256=hashlib.sha256(Path(inputs).read_bytes()).hexdigest(),mass=m,materials_kg=bymat,components=rows,stability=dict(MAC_m=MAC,target_cg_x_m=target,provisional_static_margin=(np-m['aircraft_cg_m'][0])/MAC,battery_current_x_m=battery['x_m'],battery_required_x_for_inherited_target_m=required,battery_relocated=False,status=c['stability_status'],payload_released_cg_m=release_cg,payload_release_shift_mm=[(x-y)*1000 for x,y in zip(release_cg,center)]),inertia_kgm2=inertia,inertia_status='CAD intrinsic structural inertias + point approximations elsewhere; reserve not placed',electrical=electrical,load_cases=cases,arm_cases=arms,payload_plate=plate,tail_pusher_loads=support,wing_screen_boundary=env,thrust_scenarios=thrust,warnings=warnings)
 dump(output/'results.json',results)
 flat=[{k:r.get(k,'') for k in ['name','category','material','volume_mm3','mass_kg','x_m','y_m','z_m','status','source']} for r in rows]
 for name,data in [('mass_components.csv',flat),('load_cases.csv',cases)]:
  with (output/name).open('w',newline='',encoding='utf-8') as f:
   w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
 md=['# RescU Structures V4 — P04 attachment study','',results['overall_status'],'', '## Mass summary', '',table(['Quantity','Value'],[
 ['Modeled structural material',f"{m['cad_structure_kg']*1000:.3f} g"],['Finish and installation budgets',f"{m['structural_allowances_kg']*1000:.3f} g"],['Added user structural parts',f"{m['additional_structure_kg']*1000:.3f} g"],['Structural budget (incomplete)',f"{m['structural_budget_kg']*1000:.3f} g"],['Accounted aircraft estimate',f"{m['accounted_aircraft_kg']:.4f} kg"],['Sizing aircraft mass',f"{m['sizing_aircraft_kg']:.4f} kg"],['Unallocated sizing reserve',f"{m['reserve_kg']*1000:.1f} g"],['Battery pack budget (assumed)',f"{m['battery_pack_kg']*1000:.1f} g"]]),'', 'CAD material quantities use m=rho×V; hidden untrimmed wing/tail sources and prop/ESC gauges are excluded. No second spar-foam subtraction. Reserve is separate from component mass and has no assigned CG.','', '## Modeled materials','',table(['Material','Mass g'],[(k,f'{v*1000:.3f}') for k,v in bymat.items()]),'', 'Wing/tail cores contain the represented XPS. Candidate localized fuselage foam is counted; final hardpoint closure remains open.','', '## CAD structural components','',table(['Part','Material','Mass g','Centroid X mm'],[(r['name'],r['material'],f"{r['mass_kg']*1000:.3f}",f"{r['x_m']*1000:.2f}") for r in rows if r['category']=='CAD_structure']), '', '## CG and payload release','', f"CAD structural CG: X={m['cad_structure_cg_m'][0]*1000:.2f}, Y={m['cad_structure_cg_m'][1]*1000:.2f}, Z={m['cad_structure_cg_m'][2]*1000:.2f} mm.",f"Provisional aircraft CG: X={center[0]*1000:.2f}, Y={center[1]*1000:.2f}, Z={center[2]*1000:.2f} mm.",f"Battery stays at X{battery['x_m']*1000:.2f} mm. Inherited target would require X{required*1000:.2f} mm; fit and stability target are not verified.",f"Payload release shifts X CG by{(release_cg[0]-center[0])*1000:.2f} mm. This removes payload only; magnet and plate remain.",'Installed component locations/allowance centroids remain estimates, so the aircraft CG is not final. Static margin is diagnostic against an inherited neutral point, not stability validation.','', '## Structural screens','',table(['Case','Screen only','Deflection mm','Twist deg','Max utilization'],[(x['case'],x['screen_status'],f"{x['tip_total_limit_mm']:.2f}",f"{x['tip_twist_limit_deg']:.2f}",f"{max(x[k] for k in UTIL):.3f}") for x in cases]),'', f"Ideal wing positive-n screen boundary: {env['positive_n_screen_boundary'] if env['positive_n_screen_boundary'] is not None else 'not bracketed'}; governing metric:{env['governing']}. This is not aircraft load-factor capability.", '', '## VTOL arm overhang checks','',table(['Total rating N','Front stress MPa','Rear stress MPa','Worst nominal FOS'],[(a['total_rating_N'],f"{a['front_stress_MPa']:.2f}",f"{a['rear_stress_MPa']:.2f}",f"{a['worst_FOS']:.2f}") for a in arms]),'Proposed supports X356.4/X410mm and material properties remain assumptions; no clamp/bearing/crushing check.','', '## Payload mount and aft support loads','',f"Payload plate bending stress:{plate['plate_bending_stress_MPa']:.2f} MPa; nominal FOS:{plate['plate_FOS']:.2f}. Assumed simply-supported strip; fasteners, magnet pull-off and local fuselage support not verified.",f"Tail ultimate normal load per panel:{support['tail_panel_ultimate_normal_force_N']:.2f} N. Pusher design axial load:{support['pusher_design_axial_load_N']:.2f} N.",support['support_status'],'','## Battery and thrust','',f"6S2P: {electrical['nominal_voltage_V']:.1f} V nominal / {electrical['full_voltage_V']:.1f} V fully charged;{electrical['capacity_Ah']:.1f} Ah;{electrical['nominal_energy_Wh']:.1f} Wh typical.",f"Pack budget uses12×74.5g maximum cell mass +50g provisional pack hardware unless inputs override it. This is a budgeting scenario, not measured pack weight.",electrical['current_status'],'',table(['Total thrust N','T/W at sizing mass','Evidence'],[(t['thrust_N'],f"{t['thrust_to_sizing_weight']:.3f}",t['status']) for t in thrust]),'', '## Open work / limits','']+['- '+w for w in warnings]
 md += ['', '## Geometry and material inputs', '', table(['Input','Current value / status'], [('Fuselage OD / shell', f"{s['parameters']['Fuselage_Profile_Parameters']['MainDiameter']:.2f} / {s['parameters']['Fuselage_Profile_Parameters']['Wall']:.3f} mm"),('Wing projected span / root / tip chord',f"{2*g['WingHalfSpan']:.1f} / {g['WingRootChord']:.1f} / {g['WingTipChord']:.1f} mm"),('Wing / tail skins',f"{g['WingSkin']:.3f} / {g['TailSkin']:.3f} mm"),('Spar OD root / tip; wall root / tip',f"{g['SparRootOD']:.2f} / {g['SparTipOD']:.2f}; {g['SparRootWall']:.2f} / {g['SparTipWall']:.2f} mm"),('Arm Y width / Z height / wall',f"{g['ArmWidth']:.1f} / {g['ArmHeight']:.1f} / {g['ArmWall']:.1f} mm"),('GFRP E1 / E2 / G12',f"{c['structural_material_properties']['skin']['E1_Pa']/1e9:g} / {c['structural_material_properties']['skin']['E2_Pa']/1e9:g} / {c['structural_material_properties']['skin']['G12_Pa']/1e9:g} GPa; assumed laminate"),('Foam shear modulus / shear strength',f"{c['structural_material_properties']['foam']['shear_modulus_Pa']/1e6:g} / {c['structural_material_properties']['foam']['shear_strength_Pa']/1e6:g} MPa; not qualified allowables"),('CFRP spar E / strength',f"{c['structural_material_properties']['spar']['E_Pa']/1e9:g} GPa / {c['structural_material_properties']['spar']['strength_Pa']/1e6:g} MPa; assumed"),('Force screening factors',f"limit n={c['loads']['limit_n']}; ultimate multiplier={c['loads']['ultimate_multiplier']}; wing force allowance={c['loads']['wing_force_allowance']}")]), '', '## Governing equations and interpretation', '', '- Material mass: m = density × CAD solid volume. All CAD lengths converted from mm to m.', '- Center of gravity: r_CG = sum(m_i × r_i) / sum(m_i). Battery held fixed; reserve has no assigned location.', '- Inertia: I_total = sum(I_intrinsic + m × [(d dot d) identity - d outer d]). Nonstructural components treated as points.', '- Wing screening force per side: F = sizing_mass × g × n × wing_force_allowance / 2. Elliptical span load; no inertial relief.', '- Beam equilibrium: V(y) = integral(q ds) + point forces; M(y) = integral(q × lever ds) + point-force moments.', '- Bending/shear deflection from integration of M/EI and V/kGA. Closed-section torsion from T/GJ. Material/connection assumptions limit physical accuracy.', '- Arm overhang: M=F L; stress=M c/I; tip deflection=F L^3/(3 E I). Nominal FOS uses assumed bending strength.', '- Payload plate: simply supported strip, central inertial force; M=F L/4; deflection=F L^3/(48 E I). Fasteners and magnet are separate unresolved checks.', '- Tail panel limit force: 0.5 × air_density × V^2 × panel_area × assumed_CL. Pusher load is required thrust × design multiplier.', '- Utilization above1 means the associated modeled criterion fails. PASS applies only to the listed screen, never the whole aircraft.']
 if attachment:
  md += ['## P04 attachment demand and sizing screens', 'All dimensions/effective areas/strengths below are assumptions; see docs/ATTACHMENT_STUDY.md. Geometry connections, peel, fatigue and tests remain open.',table(['Check','Demand','Capacity assumption','Units','Status'],[[r['name'],f"{r['demand']:.3f}",f"{r['capacity']:.3f}" if r['capacity'] else 'not established',r['units'],r['status']] for r in attachment['checks']])]
 md += ['## CAD fit acceptance gate',f"Audit matches snapshot: {audit_current}. Positive-volume intersections: {len(geometry_audit.get('interferences',[]))}. This is a gross candidate budget, not a net installed or finished structural mass. See reports/p04/REVIEW.md for fit findings."]
 text='\n'.join(md);(output/'SUMMARY.md').write_text(text,encoding='utf-8')
 # Self-contained report with real HTML tables and accessible color coding.
 pieces=[];in_table=False;in_list=False
 for line in text.splitlines():
  if line.startswith('|'):
   if set(line.replace('|','').strip())<=set('- '):continue
   if not in_table:pieces.append('<div class="scroll"><table>');in_table=True;tag='th'
   else:tag='td'
   pieces.append(('<tr class="fail">' if '| FAIL |' in line else '<tr>')+''.join(f'<{tag}>{html.escape(x.strip())}</{tag}>' for x in line.strip('|').split('|'))+'</tr>');continue
  if in_table:pieces.append('</table></div>');in_table=False
  if line.startswith('- '):
   if not in_list:pieces.append('<ul>');in_list=True
   pieces.append('<li>'+html.escape(line[2:])+'</li>');continue
  if in_list:pieces.append('</ul>');in_list=False
  if line.startswith('# '):pieces.append('<h1>'+html.escape(line[2:])+'</h1>')
  elif line.startswith('## '):pieces.append('<h2>'+html.escape(line[3:])+'</h2>')
  elif line:pieces.append('<p>'+html.escape(line)+'</p>')
 if in_table:pieces.append('</table></div>')
 if in_list:pieces.append('</ul>')
 page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>RescU Structures V4</title><style>body{font:16px/1.55 system-ui,sans-serif;max-width:1200px;margin:40px auto;padding:0 24px;color:#183044;background:#f5f7fa}h1{font-size:32px}h2{margin-top:36px;border-bottom:2px solid #14a3a0;padding-bottom:8px}table{border-collapse:collapse;width:100%;font-size:14px;background:white}td,th{text-align:left;padding:10px 12px;border-bottom:1px solid #dce5eb}th{background:#183044;color:white}tr:nth-child(even){background:#edf3f6}tr.fail{background:#ffe1dc;color:#7b2419;font-weight:600}.scroll{overflow-x:auto}p{max-width:100ch}li{margin:6px 0}@media print{body{background:white;margin:0}table{font-size:10px}h2{break-after:avoid}}</style><main>'+''.join(pieces)+'</main></html>'
 (output/'REPORT.html').write_text(page,encoding='utf-8')
 print('\n'.join(['RESCU STRUCTURES V4.1 | P04 ATTACHMENT STUDY','--------------------------------------------',f"Modeled structural materials : {m['cad_structure_kg']*1000:9.3f} g",f"Structural budget, incomplete: {m['structural_budget_kg']*1000:9.3f} g",f"Aircraft estimate / sizing  : {m['accounted_aircraft_kg']:.4f} / {m['sizing_aircraft_kg']:.4f} kg",f"Aircraft CG X, provisional  : {center[0]*1000:.2f} mm",f"Screens passing             : {sum(x['screen_status']=='PASS' for x in cases)}/{len(cases)}",'Overall structural status   : UNRESOLVED',f'Read report: {output/"REPORT.html"}']))
 return results

if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--inputs',type=Path,default=ROOT/'inputs.json');ap.add_argument('--snapshot',type=Path,default=ROOT/'data/cad_snapshot_p04.json');ap.add_argument('--output',type=Path,default=ROOT/'results');ap.add_argument('--stations',type=int)
 a=ap.parse_args()
 if a.stations is not None and a.stations<20:ap.error('--stations must be at least20')
 run(a.inputs,a.snapshot,a.output,a.stations)

