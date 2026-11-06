"""Reproducible attachment demand study, no material strength acceptance."""
import csv,json,math
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'reports/connection_study';out.mkdir(exist_ok=True,parents=True)
rows=[]
for T in [17.3,26.0]:
 for name,tf,tr in [('both',T,T),('front_only',T,0),('rear_only',0,T),('front_full_rear_half',T,T/2),('front_half_rear_full',T/2,T)]:
  rb=(tf*(170-335)+tr*(600-335))/70;ra=tf+tr-rb
  assert abs(ra+rb-tf-tr)<1e-10
  assert abs(rb*70-tf*(-165)-tr*265)<1e-8
  rows.append(dict(T_N=T,case=name,front_N=tf,rear_N=tr,force_on_wing_A_N=ra,force_on_wing_B_N=rb,max_abs_support_N=max(abs(ra),abs(rb))))
with (out/'attachment_loads.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,rows[0].keys());w.writeheader();w.writerows(rows)
R=max(r['max_abs_support_N'] for r in rows);U=R*1.5
stress={'limit_vertical_support_N':R,'ultimate_vertical_support_N':U,'nominal_bolt_double_shear_MPa':U/(2*math.pi*3**2/4),'nominal_rib_bearing_MPa':U/(3*2),'nominal_ear_bearing_MPa':U/(2*3*2.35),'ear_net_section_tension_MPa':U/(2*(14-3.2)*2.35),'ear_top_shearout_average_MPa':U/(4*2.35*(4.8-1.6)),'status':'Demand only. Assumed equal sharing, D3 shank and nominal local laminate thickness. No allowable or margin.'}
q=.45
stress.update({'same_rotation_pair_lateral_limit_N':2*q/.07,'same_rotation_pair_lateral_ultimate_N':1.5*2*q/.07,'opposite_rotation_equal_torque_net_lateral_N':0,'motor_pod_19mm_bolt_couple_N':q/.019,'note':'Vertical motor-shaft torque creates horizontal boom bending. Lateral reaction is axial to Y-axis rib bolts; assess retention/ear bending separately. Opposite torque cancellation at supports does not cancel local internal loads.'})
trade=[]
for L in [20,24,28,32,36]:
 trade.append({'overlap_mm':L,'bond_area_mm2':math.pi*25*L,'projected_bearing_pressure_ultimate_MPa':U/(25*L),'mean_surface_traction_scale_MPa':U/(math.pi*25*L),'four_sleeves_added_g':4*math.pi*(14**2-12.65**2)*(L-20)*.0016,'added_bond_gap_epoxy_g_at1200':4*math.pi*(12.65**2-12.5**2)*(L-20)*.0012})
(out/'attachment_results.json').write_text(json.dumps({'loads':rows,'stress_demands':stress,'overlap_trade':trade,'material_allowables':None,'strength_margin':None,'sources':['https://store.tmotor.com/product/at2814-long-shaft-fixed-wing-motor.html','https://ntrs.nasa.gov/citations/19890016677']},indent=2))
# Registry: geometric centroid is a placement proxy, not a measured component CG.
parts={r['name']:r for r in csv.DictReader((out/'cad_component_locations.csv').open())};reg=[]
def add(name,cad,mass=None,mass_status='unknown',xyz=None,location_status='CAD envelope centroid; real installed CG unmeasured'):
 p=parts.get(cad)
 if xyz is None and p:xyz=[float(p['centroid_'+a+'_mm']) for a in 'xyz']
 reg.append({'component':name,'cad_feature':cad or '', 'mass_g':mass if mass is not None else '', 'mass_status':mass_status,'x_mm':xyz[0] if xyz else '', 'y_mm':xyz[1] if xyz else '', 'z_mm':xyz[2] if xyz else '', 'location_status':location_status})
for side in ['PosY','NegY']:
 for tag in ['Front','Rear']:
  add(tag+' lift motor '+side,tag+'_AT2814_1200KV_envelope_'+side,108,'vendor mass including cable; cable CG lumped at motor')
  add(tag+' lift prop '+side,'REFERENCE_R13_'+tag+'_10inch_Disk_'+side)
  add(tag+' lift ESC '+side,tag+'_AIR40A_installation_envelope_'+side)
 for tag in ['tail servo']:
  add(tag+' '+side,'REFERENCE_Servo_Clearance_'+side,21.9,'team board; suffix and linkage excluded')
for tag in ['Front','Rear']:
 add(tag+' six bare M65A cells','REFERENCE_'+tag+'_Six_M65A_Cells',447,'6 x vendor maximum 74.5g; excludes pack hardware')
 add(tag+' module packaging/interconnect','REFERENCE_'+tag+'_Battery_Module_75x68x47')
add('Pusher motor','MT4008_Envelope_44p35x26')
add('Pusher prop/adapter','REFERENCE_Generic_13x8_Visual_Blades')
add('Flight controller + carrier',None,xyz=[152.5,0,10],location_status='PROPOSED above existing avionics deck; footprint/height and fit unverified')
add('Receiver',None,xyz=[175,0,10],location_status='PROPOSED avionics bay; antenna routing and fit unverified')
add('Camera/AI',None,350,'legacy team allowance; not selected hardware',xyz=[60,0,0],location_status='PROPOSED nose station; optical opening, footprint and cooling unverified')
add('Flotation payload',None,360,'legacy team estimate',xyz=[350,0,-55],location_status='PROPOSED external belly position; release envelope and actual CG unverified')
add('Pusher ESC',None,location_status='UNPLACED: reserve fuselage aft bay after envelope/thermal review')
add('Harness/connectors/protection',None,location_status='DISTRIBUTED: route segments required; do not put all wire mass at one point')
add('Other servos/linkages',None,location_status='UNPLACED: control-surface hardware inventory required; do not double count legacy 180g')
add('Heat sink',None,30,'legacy allowance; may already be included in electronics',location_status='UNPLACED: avoid double counting integrated heat sinks')
add('Structure and installation hardware',None,location_status='CAD feature inventory extracted; densities/layups and adhesives not fully reconciled')
with (out/'equipment_mass_location_register.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,reg[0].keys());w.writeheader();w.writerows(reg)
known=[r for r in reg if isinstance(r['mass_g'],(int,float)) and isinstance(r['x_mm'],(int,float))]
# Do not report partial-inventory CG as aircraft CG.
(out/'cg_status.json').write_text(json.dumps({'status':'BLOCKED full-aircraft CG: missing masses, unplaced components and unreconciled structure','rows':len(reg),'unknown_mass_rows':[r['component'] for r in reg if r['mass_g']==''],'unplaced_rows':[r['component'] for r in reg if r['x_mm']==''],'formula':'r_CG=sum(m_i*r_i)/sum(m_i)','battery_trim_formula':'x_battery_required=(M_total*x_target-sum_other(m_i*x_i))/m_battery','hover_trim_formula':'T_front_pair=W*(x_rear-x_CG)/(x_rear-x_front); T_rear_pair=W*(x_CG-x_front)/(x_rear-x_front)','constraints':'No battery travel authorized: fixed trays at X237.5 and362.5. Target CG from aero/controls needed; check loaded and payload-released states.'},indent=2))
print(json.dumps({'stress':stress,'trade32':trade[3],'registry_rows':len(reg)},indent=2))
