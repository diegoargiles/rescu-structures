import json, math, numpy as np, csv
sec=json.load(open('sections.json')); mp=json.load(open('R16_9_mass_properties.json'))
W=sec['wing_sections_R']; ys=np.array([r['y'] for r in W if r['y']!=265]); 
le=np.array([r['x_le'] for r in W if r['y']!=265]); ch=np.array([r['chord'] for r in W if r['y']!=265])
a_le,b_le=np.polyfit(ys,le,1); a_c,b_c=np.polyfit(ys,ch,1)
b2=700.0; c0=b_c; ct=a_c*b2+b_c; lam=ct/c0; S=2*b2*(c0+ct)/2
mac=2/3*c0*(1+lam+lam**2)/(1+lam); ymac=b2/3*(1+2*lam)/(1+lam); xle_mac=b_le+a_le*ymac
wing=dict(reference='trapezoid extrapolated to the centreline, from CAD sections of the R16.9 skin (y 46-699)',
  span_mm=1400, root_chord_y0_mm=round(c0,1), tip_chord_mm=round(ct,1), taper=round(lam,3), area_m2=round(S/1e6,4), aspect_ratio=round(1400**2/S,2),
  le_x_at_y0_mm=round(b_le,1), le_x_at_tip_mm=round(b_le+a_le*b2,1), le_sweep_deg=round(math.degrees(math.atan(a_le)),2),
  mac_mm=round(mac,1), mac_y_mm=round(ymac,1), mac_le_x_mm=round(xle_mac,1), quarter_mac_x_mm=round(xle_mac+mac/4,1),
  dihedral_deg=0.0, incidence_deg=round(float(np.mean([r['incidence_deg'] for r in W])),2), twist='none measurable (0.1 deg root and tip)',
  airfoil='SD7037', exposed_root_y_mm=44.0, chord_line_z_mm=0.0, ailerons='NONE in the R16.9 CAD (single-piece wing skin)')
V=sec['vtail_sections_L']; s=np.array([r['s'] for r in V]); vle=np.array([r['x_le'] for r in V]); vc=np.array([r['chord'] for r in V]); vh=np.array([r['x_fixed_te'] for r in V])
a1,b1=np.polyfit(s,vle,1); a2,b2c=np.polyfit(s,vc,1); a3,b3=np.polyfit(s,vh,1)
d=np.array([0,-math.cos(math.radians(35)),math.sin(math.radians(35))]); root=np.array([1000,-22,14.0]); stip=221.0
vcr=b2c; vct=a2*stip+b2c; vl=vct/vcr; Sp=stip*(vcr+vct)/2; vmac=2/3*vcr*(1+vl+vl**2)/(1+vl); smac=stip/3*(1+2*vl)/(1+vl); vxle=b1+a1*smac
cg=mp['A_takeoff_gear_down_buoy_on']['cg_mm_cad'][0]
arm=(vxle+vmac/4)-cg
def P(sv): return [round(v,1) for v in (root+d*sv)]
vt=dict(reference='each panel measured in its own plane; s = distance along the panel span from the fuselage-side root (s=0 at y -22, z 14)',
  dihedral_deg=35.0, panel_span_s_mm=stip, root_chord_mm=round(vcr,1), tip_chord_mm=round(vct,1), taper=round(vl,3),
  panel_area_each_m2=round(Sp/1e6,5), total_true_area_m2=round(2*Sp/1e6,5), horizontal_projected_area_m2=round(2*Sp*math.cos(math.radians(35))/1e6,5),
  vertical_projected_area_m2=round(2*Sp*math.sin(math.radians(35))/1e6,5), le_sweep_in_panel_plane_deg=round(math.degrees(math.atan(a1)),2),
  mac_mm=round(vmac,1), mac_s_mm=round(smac,1), mac_le_x_mm=round(vxle,1), quarter_mac_x_mm=round(vxle+vmac/4,1),
  tail_arm_from_cg_case_A_mm=round(arm,1), airfoil='NACA 0010',
  ruddervator=dict(hinge_line_root=[round(b3,1)]+P(0)[1:], hinge_line_tip=[round(a3*stip+b3,1)]+P(stip)[1:],
     chord_root_mm=round(V[0]['ruddervator_chord']+(V[0]['ruddervator_chord']-V[1]['ruddervator_chord'])/(V[1]['s']-V[0]['s'])*V[0]['s'],1), chord_tip_mm=round(V[-1]['ruddervator_chord'],1),
     chord_fraction=round(np.mean([r['ruddervator_chord']/r['chord'] for r in V]),3), span_s_mm='about 2 to 221 (1.0 mm root gap)',
     deflection_clearance_deg=25, note='+-25 deg checked clear in R16.5 (LE bevelled 27 deg). The control throw limit is the S&C choice within this.',
     mirror='L panel given; R panel is the mirror in y'))
vol_h=vt['horizontal_projected_area_m2']*arm/1000/(wing['area_m2']*wing['mac_mm']/1000)
vol_v=vt['vertical_projected_area_m2']*arm/1000/(wing['area_m2']*1.4)
vt['volume_coeff_horizontal_projected']=round(vol_h,3); vt['volume_coeff_vertical_projected']=round(vol_v,4)
rows={r['item']:r for r in csv.DictReader(open('R16_9_component_masses.csv'))}
def pos(k): r=rows[k]; return [float(r['x_mm']),float(r['y_mm']),float(r['z_mm'])]
lift=[]
for k,lab,spin in [('APC_10x3_LP10030_Front_Boom_R','front right','CCW seen from above (STD prop)'),('APC_10x3_LP10030P_Rear_Boom_R','rear right','CW seen from above (P prop)'),
                   ('APC_10x3_LP10030P_Front_Boom_L','front left','CW seen from above (P prop)'),('APC_10x3_LP10030_Rear_Boom_L','rear left','CCW seen from above (STD prop)')]:
    lift.append(dict(motor=lab, prop_hub_centroid_mm=pos(k), motor_centroid_mm=pos('UM2807_'+('Front' if 'Front' in k else 'Rear')+'_Boom_'+k[-1]), thrust_axis=[0,0,1], cant_deg=0, prop='APC 9x4.5MR per W&P (CAD geometry: APC 10x3, 254 mm)', spin=spin))
xf=np.mean([l['prop_hub_centroid_mm'][0] for l in lift if 'front' in l['motor']]); xr=np.mean([l['prop_hub_centroid_mm'][0] for l in lift if 'rear' in l['motor']])
split={}
for key in ('A_takeoff_gear_down_buoy_on','D_landing_gear_down_buoy_off'):
    m=mp[key]['mass_kg']; x=mp[key]['cg_mm_cad'][0]; Wn=m*9.81; fr=(xr-x)/(xr-xf)
    split[key]=dict(weight_N=round(Wn,2), front_pair_N=round(Wn*fr,2), rear_pair_N=round(Wn*(1-fr),2), per_front_motor_N=round(Wn*fr/2,2), per_rear_motor_N=round(Wn*(1-fr)/2,2))
pusher=dict(prop='APC 12x10 per W&P (CAD geometry: 13x8 LP13080P, 330 mm)', prop_centroid_mm=pos('Pusher prop (APC 12x10 per W&P)'), motor_centroid_mm=pos('Pusher motor (MT4008 per W&P)'), thrust_axis=[-1,0,0],
   thrust_line_z_mm=0.0, thrust_line_offset_above_cg_case_B_mm=round(0-mp['B_cruise_gear_up_buoy_on']['cg_mm_cad'][2],1))
batt=dict(config='6S2P M65A, two 75 x 68 x 47 mm modules, 472 g each (944 g)',
  front_module=dict(now_x_mm=[200,275], range_x_start_mm=[200,242], limits='fwd: flight controller / receiver (x 199.5); aft: ring frame F317 (x 317)'),
  rear_module=dict(now_x_mm=[360,435], range_x_start_mm=[356.5,365], limits='fwd: ring frame F355 (x 356.5); aft: ESC deck (x 440)'),
  cg_trim_authority_mm=dict(front_module_full_aft=round(472*42/(mp['A_takeoff_gear_down_buoy_on']['mass_kg']*1000),1), rear_module_range=[round(-472*3.5/(mp['A_takeoff_gear_down_buoy_on']['mass_kg']*1000),2),round(472*5/(mp['A_takeoff_gear_down_buoy_on']['mass_kg']*1000),2)]),
  note='The saddles are bonded frames, so a new module position must be chosen before step 2 of the build. The battery cannot move the CG forward without moving the flight controller.')
sensors=dict(flight_controller_imu_box_centre_mm=[152.5,0,6.3], lever_arm_from_cg_case_A_mm=[round(152.5-cg,1),0,round(6.3-mp['A_takeoff_gear_down_buoy_on']['cg_mm_cad'][2],1)],
  camera_ELP=dict(centre_mm=pos('ELP 5MP IR USB camera'), boresight='forward and 45 deg down'), gps_compass='not modelled', airspeed_probe='not modelled')
servos=dict(vtail_servos=dict(type='2 x HS-5085MG (REF envelope)', box_x_mm=[930,960], box_y_mm=[-16,16], box_z_mm=[-14.8,17.2]),
   linkage='NOT MODELLED: pushrods run aft through two dia 8 channels in the V-tail root block at y +-12, z -8; horn positions to be defined',
   gear_servos='3 x KST X08H (one per leg), positions in the component CSV')
buoy=dict(release_plate_x_mm=[325,375], plate_z_mm=-55, mass_g=370, cg_shift_on_release_mm=round(mp['C_after_release_gear_up_buoy_off']['cg_mm_cad'][0]-mp['B_cruise_gear_up_buoy_on']['cg_mm_cad'][0],1))
out=dict(frame='CAD frame: origin at the nose tip, X aft, Y right, Z up (fuselage axis at z 0), mm. Body frame for S&C: x_b = -X, y_b = Y, z_b = -Z.',
  wing=wing, vtail=vt, lift_motors=lift, hover_thrust_split=split, pusher=pusher, battery=batt, buoy=buoy, servos=servos, sensors=sensors,
  landing_gear=dict(legs=3, ground_z_mm=-206, clearance_under_buoy_plate_mm=150, tip_over_deg=dict(sideways=42, nose_over=48), mass_g=158.6))
json.dump(out,open('R16_9_geometry_reference.json','w'),indent=1)
print(json.dumps(dict(wing=wing,vt={k:v for k,v in vt.items() if k!='ruddervator'},rud=vt['ruddervator'],split=split,pusher=pusher,batt=batt['cg_trim_authority_mm'],sens=sensors['lever_arm_from_cg_case_A_mm'],buoy=buoy),indent=0))
