"""Demand and preliminary sizing screens, not joint qualification."""
import math

def evaluate(c,s,m,cases):
    a=c['attachment_design'];L=c['loads'];g=9.80665
    rows=[]
    def check(name,demand,capacity,units,method,limits):
        rows.append(dict(name=name,demand=demand,capacity=capacity,units=units,
                         utilization=demand/capacity if capacity else None,
                         status=('SCREEN EXCEEDED' if capacity and demand>capacity else 'PRELIMINARY SCREEN ONLY'),
                         method=method,unresolved=limits))
    F=max(L['baseline_total_vtol_thrust_N'],L['alternate_total_vtol_thrust_N'])/4*L['vtol_thrust_multiplier']
    check('Lift motor shoe strip bending',1.5*F*a['motor_plate_span_mm']/(a['motor_plate_effective_width_mm']*a['motor_plate_thickness_mm']**2),a['glass_bending_assumption_MPa'],'MPa','Simply supported central point load: 6(FL/4)/(bt^2). No torque credited.','Motor bolt pattern, local plate action, fatigue and clamp preload absent; 69.2 N thrust is hypothetical.')
    xf=L['arm_support_front_x_m'];xr=L['arm_support_rear_x_m'];p=s['parameters']['Global_Parameters'];motorx=[p['FrontMotorX']/1000,p['RearMotorX']/1000]
    if xr<=xf:raise ValueError('Rear arm support must be aft of front support.')
    reactions=[]
    for pattern,forces in [('both',[F,F]),('front only',[F,0]),('rear only',[0,F])]:
        rear=sum(f*(x-xf) for x,f in zip(motorx,forces))/(xr-xf);front=sum(forces)-rear
        reactions.append(dict(pattern=pattern,front_N=front,rear_N=rear,force_residual_N=front+rear-sum(forces),moment_residual_Nm=rear*(xr-xf)-sum(f*(x-xf) for x,f in zip(motorx,forces))))
    R=max(abs(r[k]) for r in reactions for k in ['front_N','rear_N'])
    check('Arm saddle average bond shear',R/a['arm_effective_bond_mm2'],a['bond_shear_assumption_MPa'],'MPa','Maximum absolute support reaction / effective bond area.','Reversed support reactions require tension-capable connection; peel, core pullout, rib buckling and vibration open.')
    # Entire half-wing bending moment assigned to candidate root caps, deliberately
    # avoiding credit for an unsupported stiffness split between spar and skins.
    M=max(abs(r['root_moment_limit_Nm'])*L['ultimate_multiplier'] for r in cases)
    cap_force=M*1000/a['root_cap_separation_mm']
    check('Wing root cap axial stress',cap_force/(a['root_cap_effective_width_mm']*a['root_cap_thickness_mm']),a['carbon_axial_assumption_MPa'],'MPa','N=M/h, sigma=N/(bt); entire bending moment on one cap pair.','Actual effective width, minimum separation, compression buckling and center-box connection not substantiated.')
    check('Wing root transfer bond shear',cap_force/a['root_effective_bond_mm2'],a['bond_shear_assumption_MPa'],'MPa','N=M/h; tau=N/A_effective.','Nonuniform end shear and peel omitted; actual spar/cap/rib load sharing unknown.')
    battery=m['battery_pack_kg']*g*a['battery_retention_limit_g']*L['ultimate_multiplier']
    check('Battery retention per strap',battery/a['battery_strap_count'],a['battery_strap_required_rating_N'],'N','Pack mass * assumed 6g retention envelope * 1.5, equally shared by two straps.','6g is a proposed requirement, not agreed landing/crash envelope. Each strap should independently retain full load if redundancy is required; latch rating unknown.')
    tail=next(r for r in cases if r['case']=='V-tail at top speed')
    check('Tail root couple force',abs(tail['root_moment_limit_Nm'])*L['ultimate_multiplier']*1000/a['tail_effective_depth_mm'],None,'N','Tail panel moment / proposed effective root depth.','Tail attachment peel, laminate crippling, skin-shell transfer and asymmetric control loads unresolved.')
    check('Pusher axial demand',L['pusher_cruise_thrust_N']*L['pusher_thrust_multiplier'],None,'N','Inherited cruise thrust * 1.5 only.','Maximum/static thrust, motor torque, gyroscopic and lateral inertia cases missing; not a governing verified design load.')
    return dict(status='UNRESOLVED',assumption_status='Every attachment allowable and effective dimension is preliminary, not test-derived.',checks=rows,arm_reactions=reactions,wing_root_ultimate_moment_Nm=M,battery_ultimate_N=battery)
