import sys; sys.path.insert(0, '.')
from vr import *

def U(v):
    v = np.array(v, float); return v / np.linalg.norm(v)

FUS_STRUCT = ['Battery_End_Stops_GFRP_Fuselage', 'Battery_Insulating_Pads_Foam_Fuselage', 'Battery_Trays_GFRP_Fuselage',
              'ESC_Deck_GFRP_Fuselage', 'ESC_Pads_Foam_Fuselage', 'Frames_Lower_and_Battery_Saddles_GFRP_Fuselage', 'Frames_Ring_GFRP_Fuselage',
              'Joiner_Axial_Stop_Ring_Fuselage', 'Joiner_Receiver_Sleeves_GFRP_Fuselage', 'Wing_Joiner_CFRP_OD12_Fuselage',
              'Wing_Pin_Bushing_Pads_G10_Fuselage', 'Wing_Root_Side_Rails_GFRP_Fuselage', 'Nose_Joiner_Band_GFRP_Fuselage',
              'Nose_Joint_Nutplates_M3_Fuselage', 'VTail_Root_Block_PA-CF_Fuselage', 'VTail_Root_Receivers_GFRP_Fuselage',
              'VTail_Retention_Inserts_M3_Brass_Fuselage', 'Pusher_Bonded_Collar_GFRP_Fuselage',
              'Belly_Doubler_CFRP_LG_Tail', 'Knee_Block_LG_Tail', 'Trough_LG_Tail', 'Servo_Mount_LG_Tail', 'Guide_Tab_LG_Tail']

def step1():
    S = Scene(2400, 1300)
    S.add('Fuselage_Shell_Left_GFRP_Fuselage', off=(0, -80, 0))
    S.add('Fuselage_Shell_Right_GFRP_Fuselage', off=(0, 40, 0))
    S.add('Fuselage_Seam_Strips_GFRP_Fuselage', col=COL['hi'], off=(0, 40, 0))
    for k in ('Hatch_Front_GFRP_Fuselage', 'Hatch_Rear_GFRP_Fuselage', 'Hatch_Tail_GFRP_Fuselage'):
        S.add(k, col=COL['teal'], off=(0, 0, 70))
    S.camera((-350, -1250, 800), (600, 0, 0)); S.fit2(0.94)
    co = [(1, (520, -125, 20), (-60, -150)), (2, (700, 85, 20), (60, -150)), (3, (820, 40, -44), (60, 120)),
          (4, (236, 0, 112), (-60, -110)), (5, (364, 0, 112), (0, -130)), (6, (1005, 0, 98), (-150, -20))]
    S.render('img/s1_shells.png', callouts=co, r=30)

def step2():
    S = Scene(2600, 1300)
    S.add('Fuselage_Shell_Right_GFRP_Fuselage', edges=False)
    for k in FUS_STRUCT: S.add(k)
    S.add('Fuselage_Seam_Strips_GFRP_Fuselage', col=(0.80, 0.78, 0.72))
    S.camera((250, -1300, 650), (640, 0, -15)); S.fit2(0.95)
    co = [(1, (274, 0, -35), (-40, 150)), (2, (317, -30, 0), (-60, -150)), (3, (345, -20, 6), (0, -170)),
          (4, (420, -40, 8), (60, -150)), (5, (505, 0, -16), (40, 140)), (6, (900, 0, -28), (0, 150)),
          (7, (1006, -20, 5), (-30, -150)), (8, (1087, -24, 10), (40, -130)), (9, (180, -30, 30), (-60, -120)),
          (10, (700, -6, -44), (0, 140))]
    S.render('img/s2_internals.png', callouts=co, r=30)

def step3():
    S = Scene(2400, 1500)
    box = (290, 470, -60, 60, -60, 60)
    S.add(crop_shape('Fuselage_Shell_Right_GFRP_Fuselage', box), col=COL['gfrp'], edges=False)
    S.add(crop_shape('Fuselage_Shell_Left_GFRP_Fuselage', box), col=COL['gfrp'], op=0.13, edges=False)
    for k in ('Wing_Joiner_CFRP_OD12_Fuselage', 'Joiner_Receiver_Sleeves_GFRP_Fuselage', 'Joiner_Axial_Stop_Ring_Fuselage',
              'Wing_Root_Side_Rails_GFRP_Fuselage', 'Wing_Pin_Bushing_Pads_G10_Fuselage'):
        S.add(k)
    S.add(crop_shape('Frames_Ring_GFRP_Fuselage', (300, 370, -60, 60, -60, 60)), col=COL['g10'])
    d = (0, -70, 0)
    for k in ('Wing_Root_Elbow_CFRP_Wing_L', 'Wing_Aft_Elbow_CFRP_Wing_L', 'Wing_AntiRotation_Pin_D3_Wing_L', 'Wing_Retention_Lug_GFRP_Wing_L',
              'Wing_Retention_Screw_M3_Wing_L', 'Wing_Root_Diaphragm_GFRP_Wing_L'):
        S.add(k, off=d)
    for k in ('Wing_Main_Spar_CFRP_Wing_L', 'Wing_Aft_Torque_Tube_CFRP_Wing_L'):
        S.add(crop_shape(k, (300, 480, -230, 0, -20, 30)), col=COL['cfrp'], off=d)
    S.add(crop_shape('Wing_Skin_GFRP_Wing_L', (290, 480, -230, 0, -20, 30)), col=COL['gfrp'], op=0.12, off=d, edges=False)
    S.camera((-150, -650, 420), (385, -60, 0)); S.fit2(0.93)
    co = [(1, (345, -44, 4), (-170, -40)), (2, (345, -30, 12), (-20, -190)), (3, (428, -40, 9), (70, -150)),
          (4, (356, -150, 6), (-110, 90)), (5, (378, -270, 4), (-110, 60)), (6, (428, -230, 3), (90, 90)),
          (7, (420, -120, 3), (100, 40)), (8, (405, -120, 8), (40, -140))]
    S.render('img/s3_wingroot.png', callouts=co, r=30)

def step4():
    S = Scene(2400, 1500)
    box = (930, 1110, -60, 60, -60, 60)
    S.add(crop_shape('Fuselage_Shell_Right_GFRP_Fuselage', box), col=COL['gfrp'], edges=False)
    S.add(crop_shape('Fuselage_Shell_Left_GFRP_Fuselage', box), col=COL['gfrp'], op=0.12, edges=False)
    S.add('Hatch_Tail_GFRP_Fuselage', col=COL['teal'], off=(0, 0, 45))
    for k in ('VTail_Root_Block_PA-CF_Fuselage', 'VTail_Root_Receivers_GFRP_Fuselage', 'VTail_Retention_Inserts_M3_Brass_Fuselage',
              'VTail_Retention_Screws_M3x20_ISO4762_Fuselage', 'Pusher_Bonded_Collar_GFRP_Fuselage'):
        S.add(k)
    S.add(crop_shape('Frames_Ring_GFRP_Fuselage', (980, 1030, -60, 60, -60, 60)), col=COL['g10'])
    S.add('Pusher_Removable_Plate_6061_Fuselage', off=(30, 0, 0))
    S.add('Motor_Screws_M3x4_SHCS_Pusher_Fuselage', off=(48, 0, 0))
    S.add('Tarot_4008_Pusher_Motor_Fuselage', off=(60, 0, 0))
    for k in ('VTail_Spar_CFRP_VTail_L', 'VTail_Spar_CFRP_VTail_R'):
        S.add(crop_shape(k, (970, 1012, -80, 80, -5, 40)), col=COL['cfrp'])
    for k in ('VTail_Spar_Root_Plug_6061_VTail_L', 'VTail_AntiRotation_Pin_D3_VTail_L', 'VTail_Spar_Root_Plug_6061_VTail_R', 'VTail_AntiRotation_Pin_D3_VTail_R'):
        S.add(k)
    S.camera((1550, -800, 520), (1030, -10, 5)); S.fit2(0.93)
    co = [(1, (1028, -27, -5), (120, 170)), (2, (996, -18, 10), (-220, -40)), (3, (991, -10, 19), (-120, -190)),
          (4, (991, -26, -18), (-170, 120)), (5, (1087, -26, 0), (-60, 150)), (6, (1133, -24, 0), (40, 140)),
          (7, (1180, -22, 10), (80, -120)), (8, (1005, 0, 72), (80, -100))]
    S.render('img/s4_tail.png', callouts=co, r=30)

def step5():
    S = Scene(2400, 1400)
    box = (179, 290, -60, 60, -60, 60)
    S.add(crop_shape('Fuselage_Shell_Right_GFRP_Fuselage', box), col=COL['gfrp'], edges=False)
    S.add(crop_shape('Fuselage_Shell_Left_GFRP_Fuselage', box), col=COL['gfrp'], op=0.13, edges=False)
    S.add('Nose_Joiner_Band_GFRP_Fuselage', col=COL['hi']); S.add('Nose_Joint_Nutplates_M3_Fuselage')
    d = (-110, 0, 0)
    S.add('Nose_Shell_Right_GFRP_Fuselage', off=d, edges=False)
    S.add('Nose_Shell_Left_GFRP_Fuselage', off=d, op=0.12, edges=False)
    for k in ('Nose_Frame_NF3_G10_Fuselage', 'Nose_Frame_NF4_G10_Fuselage', 'Avionics_Deck_GFRP_Fuselage', 'Avionics_Adjust_Strips_Fuselage',
              'REF_Flight_Controller_Cube_Fuselage', 'REF_Receiver_Fuselage', 'REF_Camera_ELP_5MP_IR_USB_Fuselage', 'Nose_Seam_Strips_GFRP_Fuselage',
              'Nose_Joint_Screws_M3x6_ISO7380_Fuselage'):
        S.add(k, off=d)
    S.camera((-450, -900, 450), (100, 0, 0)); S.fit2(0.93)
    co = [(1, (-40, 0, 43), (-60, -150)), (2, (-62, -19, 0), (-140, 110)), (3, (25, -30, -25), (-60, 170)),
          (4, (40, -22, 10), (20, -190)), (5, (53, -30, -25), (60, 170)), (6, (182, -44, 10), (120, -130)),
          (7, (171, -38, -22), (150, 90))]
    S.render('img/s5_nose.png', callouts=co, r=30)

def step6():
    S = Scene(2600, 1300)
    S.add('Wing_Skin_GFRP_Wing_R', op=0.10, edges=False)
    S.add('Wing_XPS_Core_Panels_Wing_R', op=0.30, edges=False)
    for k in ('Wing_Main_Spar_CFRP_Wing_R', 'Wing_Aft_Torque_Tube_CFRP_Wing_R', 'Wing_Aft_Collars_GFRP_Wing_R', 'Wing_Motor_Rib_Extended_Tab_CFRP_Wing_R',
              'Wing_Motor_Rib_Doublers_GFRP_Wing_R', 'Wing_Spar_Sleeve_GFRP_Wing_R', 'Wing_Wire_Conduit_PTFE_Wing_R', 'Wing_Root_Elbow_CFRP_Wing_R',
              'Wing_Aft_Elbow_CFRP_Wing_R', 'Wing_AntiRotation_Pin_D3_Wing_R', 'Wing_Retention_Lug_GFRP_Wing_R', 'Wing_Root_Diaphragm_GFRP_Wing_R'):
        S.add(k, col=COL['hi'] if 'Rib_Extended' in k else None)
    S.add('Boom_Upper_Half_Boom_R', op=0.12, edges=False)
    S.camera((420, 370, 2500), (420, 370, 0), up=(-1, 0, 0), parallel=300); S.fit2(0.95)
    co = [(1, (500, 560, 6), (60, 110)), (2, (432, 500, 4), (40, -120)), (3, (453, 330, 3), (60, 120)),
          (4, (420, 265, 6), (-20, -170)), (5, (356, 90, 4), (-40, -120)), (6, (421, 70, 3), (-40, 130)),
          (7, (395, 170, 3), (40, 130)), (8, (300, 265, 0), (-80, -60))]
    S.render('img/s6_wing.png', callouts=co, r=30)

def step6b():
    S = Scene(1800, 1400)
    box = (404, 426, 225, 305, -50, 20)
    for k, c in (('Wing_Skin_GFRP_Wing_R', None), ('Wing_XPS_Core_Panels_Wing_R', None), ('Wing_Motor_Rib_Extended_Tab_CFRP_Wing_R', COL['hi']),
                 ('Saddle_U_Channel_Boom_R', COL['teal']), ('Compression_Tubes_Boom_R', None), ('Saddle_Bolts_M3_and_Barrel_Nuts_Boom_R', None),
                 ('Boom_Upper_Half_Boom_R', None), ('Boom_Lower_Half_Boom_R', (0.32, 0.33, 0.36)), ('Boom_Junction_Fillets_Boom_R', (0.75, 0.72, 0.62)),
                 ('Trough_LG_Front_R', None), ('Tendon_Bracket_LG_Front_R', None), ('Wing_Motor_Rib_Doublers_GFRP_Wing_R', None),
                 ('Wing_Main_Spar_CFRP_Wing_R', None), ('Wing_Spar_Sleeve_GFRP_Wing_R', None)):
        s = crop_shape(k, box)
        if s.Solids(): S.add(s, col=c or colour(k))
    S.camera((-1500, 265, -12), (415, 265, -12), parallel=60); S.fit2(0.9)
    co = [(1, (404, 290, 8), (90, -90)), (2, (404, 265, -10), (-130, -60)), (3, (404, 262.6, -14), (-140, 50)),
          (4, (404, 255, -9), (-120, 130)), (5, (404, 277.6, -14), (-150, 30)), (6, (404, 276.8, -33), (-150, 40)), (7, (404, 252, -5), (150, -40)),
          (8, (404, 265, -36), (170, 60))]
    S.render('img/s6_ribsection.png', callouts=co, r=30)

def step7():
    S = Scene(2600, 1300)
    S.add('Boom_Upper_Half_Boom_L', op=0.22, edges=False); S.add('Boom_Lower_Half_Boom_L', op=0.22, edges=False)
    for k in ('Motor_Backing_Rings_6061_Boom_L', 'Motor_Screws_M3x10_Boom_L', 'Pad_Access_Covers_Boom_L', 'Compression_Tubes_Boom_L',
              'Saddle_Bolts_M3_and_Barrel_Nuts_Boom_L', 'Saddle_U_Channel_Boom_L', 'UM2807_Front_Boom_L', 'UM2807_Rear_Boom_L'):
        S.add(k)
    S.add('Wing_Motor_Rib_Extended_Tab_CFRP_Wing_L', col=COL['hi'])
    for k in NAMES:
        if k.endswith('LG_Front_L'): S.add(k)
    S.camera((420, -2500, -70), (420, -265, -70), parallel=200); S.fit2(0.95)
    co = [(1, (560, -284, -10), (40, -130)), (2, (560, -284, -36), (60, 120)), (3, (635, -265, -15.6), (90, -110)),
          (4, (414, -277, -9), (20, -150)), (5, (470, -265, 6), (130, -50)), (6, (244, -274, -25), (-120, -110)),
          (7, (322, -274, -17), (-30, -150)), (8, (390, -274, -40), (40, 130)), (9, (220, -270, -120), (-120, 0))]
    S.render('img/s7_boom.png', callouts=co, r=30)

def step8():
    S = Scene(2400, 1500)
    box = (950, 1060, -60, 60, -60, 60)
    S.add(crop_shape('Fuselage_Shell_Right_GFRP_Fuselage', box), col=COL['gfrp'], edges=False)
    S.add(crop_shape('Fuselage_Shell_Left_GFRP_Fuselage', box), col=COL['gfrp'], op=0.12, edges=False)
    for k in ('VTail_Root_Block_PA-CF_Fuselage', 'VTail_Root_Receivers_GFRP_Fuselage', 'VTail_Retention_Inserts_M3_Brass_Fuselage',
              'VTail_Retention_Screws_M3x20_ISO4762_Fuselage'):
        S.add(k)
    ax = U((105, -193, 137)); dv = ax * 90; D = tuple(dv)
    S.add('VTail_Fixed_Skin_GFRP_VTail_L', op=0.16, off=D, edges=False)
    S.add('VTail_Fixed_Core_XPS_VTail_L', op=0.30, off=D, edges=False)
    S.add('VTail_Ruddervator_Skin_GFRP_VTail_L', col=COL['teal'], op=0.45, off=D, edges=False)
    for k in ('VTail_Spar_CFRP_VTail_L', 'VTail_Spar_Root_Plug_6061_VTail_L', 'VTail_AntiRotation_Pin_D3_VTail_L', 'VTail_Hinge_Pins_REF_VTail_L',
              'VTail_Root_Diaphragm_GFRP_VTail_L'):
        S.add(k, off=D)
    S.camera((1550, -1050, 380), (1040, -90, 60)); S.fit2(0.93)
    a = np.array; P = lambda s_: a((988, -6, 4)) + ax * s_ + dv
    co = [(1, tuple(a((1035, -112, 78)) + dv), (-150, -110)), (2, tuple(a((1088, -112, 80)) + dv), (150, -90)),
          (3, tuple(P(110)), (-170, 30)), (4, tuple(P(6)), (-150, 90)), (5, tuple(a((1023, -17, 12)) + dv), (80, 150)),
          (6, (994, -14, 8), (-130, 140)), (7, (991, -10, 18), (-60, -170))]
    S.render('img/s8_vtail.png', callouts=co, r=30)

PROC = {'hot': (0.30, 0.62, 0.44), 'mold': (0.24, 0.50, 0.76), 'mandrel': (0.44, 0.66, 0.86), 'plate': (0.82, 0.60, 0.16),
        'buy': (0.56, 0.36, 0.71), 'print': (0.82, 0.31, 0.35), 'mach': (0.10, 0.50, 0.50), 'hand': (0.55, 0.55, 0.55), 'eq': (0.86, 0.86, 0.86)}
def process(k):
    if re.search(r'^(UM2807|Tarot|APC|REF_|Prop_Nut)', k): return 'eq'
    if re.search(r'XPS|Wing_Skin|VTail_Fixed_Skin|Ruddervator_Skin', k): return 'hot'
    if re.search(r'Shell|Boom_(Upper|Lower)|Hatch_(Front|Rear|Tail)|Pad_Access', k): return 'mold'
    if re.search(r'Root_Elbow|Aft_Elbow|Receiver|Saddle_U|Pusher_Bonded_Collar|Aft_Collars|Spar_Sleeve|Joiner_Band|Trough|Seam_Strips|Hatch_Rims|Belly_Doubler|Retention_Lug|Stop_Ring', k): return 'mandrel'
    if re.search(r'PA-CF|ASA|Foot', k): return 'print'
    if re.search(r'6061|Knee_Block|Knuckle|Servo_Arm_LG|Tendon_Bracket', k): return 'mach'
    if re.search(r'Fillets|Foam', k): return 'hand'
    if re.search(r'Main_Spar|Torque_Tube|Wing_Joiner|VTail_Spar_CFRP|Leg_Rod|Pin|Screw|Bolts|Nut|Insert|Conduit|Shaft', k): return 'buy'
    return 'plate'

EXT_SKIP = r'^(REF_|Prop_Nut)'
def process_map():
    S = Scene(2600, 1500)
    for k in NAMES:
        if re.search(EXT_SKIP, k) or k in ('Fuselage_Shell_Left_GFRP_Fuselage', 'Nose_Shell_Left_GFRP_Fuselage', 'Wing_Skin_GFRP_Wing_L'): continue
        p = process(k)
        off = (0, 0, 60) if re.search(r'Hatch_(Front|Rear|Tail)', k) else (0, 0, 0)
        op = 0.35 if 'XPS_Core_Panels_Wing_L' in k else 1.0
        S.add(k, col=PROC[p], op=op, off=off, edges=(p != 'eq'))
    S.camera((-700, -1250, 620), (560, 0, -40)); S.fit2(0.95)
    S.render('img/process_map.png')

STAGES = [
    ('st1', r'_Fuselage$|_LG_Tail$', r'^(Nose_|REF_Camera|REF_Flight|REF_Receiver|Avionics|Tarot|APC|Prop_Nut|REF_Prop|Motor_Screws_M3x4|Pusher_Removable|VTail_Root_Fairings|VTail_Retention_Screws)'),
    ('st2', r'_Wing_[LR]$', None), ('st3', r'_Boom_[LR]$|_LG_Front_[LR]$', r'^(APC|Prop_Nut)'), ('st4', r'_VTail_[LR]$|VTail_Root_Fairings|VTail_Retention_Screws', None),
    ('st5', r'^(Nose_Shell|Nose_Frame|Nose_Seam|Nose_Joint_Screws|REF_Camera|REF_Flight|REF_Receiver|Avionics)', None),
    ('st6', r'^(Tarot|APC|Prop_Nut|REF_Prop|Motor_Screws_M3x4|Pusher_Removable)', None)]
def stage_of(k):
    for i, (nm, inc, exc) in enumerate(STAGES):
        if re.search(inc, k) and not (exc and re.search(exc, k)): return i
    for i in (4, 5):
        if re.search(STAGES[i][1], k): return i
    return 0
def stages():
    st = {k: stage_of(k) for k in NAMES}
    for k in NAMES:
        if re.search(r'^(Nose_Shell|Nose_Frame|Nose_Seam|Nose_Joint_Screws|REF_Camera|REF_Flight|REF_Receiver|Avionics)', k): st[k] = 4
        if re.search(r'^(Tarot|APC_13|Prop_Nut_1-4|REF_Prop|Motor_Screws_M3x4|Pusher_Removable)', k): st[k] = 5
        if re.search(r'^(APC_10|Prop_Nut_M5)', k): st[k] = 5
    json.dump(st, open('img/stages.json', 'w'), indent=0)
    for i in range(6):
        S = Scene(1500, 950)
        for k in NAMES:
            if st[k] > i or re.search(r'^REF_(Battery|M65A|ESC|VTail_Servos|Payload)', k): continue
            if re.search(r'XPS|Main_Spar|Torque|Aft_Collars|Doublers|Spar_Sleeve|Conduit|Diaphragm|VTail_Spar|Root_Plug|Frames|Battery|ESC_|Joiner_|Side_Rails|Pin_Bushing|Hatch_Rims|Seam_Strips|Inserts', k): continue
            col = COL['hi'] if st[k] == i else (0.80, 0.80, 0.78) if material(k) in ('gfrp', 'g10') else (0.45, 0.46, 0.49)
            S.add(k, col=col, edges=True)
        S.camera((-950, -650, 1150), (560, 0, -40)); S.fit2(0.95)
        S.render(f'img/stage{i + 1}.png')

def hero():
    S = Scene(2600, 1500, transparent=True)
    skip = r'XPS|Main_Spar|Torque|Aft_Elbow|Aft_Collars|Doublers|Spar_Sleeve|Conduit|Root_Elbow|Diaphragm|AntiRotation|Retention|VTail_Spar|Root_Plug|Compression|Backing|Motor_Screws|Saddle_Bolts|Tendon|Guide|Servo|Knee_Shaft|Fork_Pin|Trough|Belly|Frames|Battery|ESC_|Avionics|Joiner|Side_Rails|Pin_Bushing|Hatch_Rims|Seam_Strips|Nose_Frame|Nose_Joint|Root_Block|Root_Receivers|Inserts|Knee_Block|Tendon'
    for k in NAMES:
        if (re.search(EXT_SKIP, k) and 'Camera' not in k) or re.search(skip, k): continue
        S.add(k)
    S.camera((-950, -650, 1150), (560, 0, -40)); S.fit2(0.97)
    S.render('img/hero_iso.png')

import json
if __name__ == '__main__':
    for f in sys.argv[1:]:
        globals()[f]()
        print('done', f, flush=True)
