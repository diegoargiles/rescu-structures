"""RescU R16.9 structures screen for the final design presentation.

Analytical screen (beam theory, thin-wall sections, joint hand calcs) on the repo load basis:
+3 / -1.5 g limit, ultimate = 1.5 x limit, 5 g hard landing. Allowables are the preliminary repo values
(GFRP 150/100/30 MPa, CFRP tube 300 MPa, each x 0.7; XPS shear 0.25 x 0.7). Wing stresses and deflections are
calibrated to the R16.5 screen, which itself is calibrated to the R15 SOLIDWORKS LC1 FEA (beam model scaled
by the ratio of section loads). Nothing here is a flight release; coupon tests and FEA close the margins.
Writes out/results.json and out/fig*.png.
"""
import json, math, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = 'out'; os.makedirs(OUT, exist_ok=True)
g = 9.81
# ---------------- configuration (R16.9) ----------------
M = 3.652            # kg, R16.8 (3723 g) - 71 g for the shorter legs
CG_X = 421.0         # mm, gear deployed
NP_X, MAC = 431.0, 135.1   # rough NP for the 35 mm aft wing (Aero to confirm)
M_R165 = 3.768       # mass of the R16.5 screen the wing results are calibrated to
# wing half: root y 45, tip y 700; chord 160 -> 100.6 (CAD)
Y_ROOT, Y_TIP, C_ROOT, C_TIP = 45.0, 700.0, 160.2, 100.6
Y_BOOM = 265.0
M_WING_HALF = 0.1785 # kg structure per panel
M_BOOM_SIDE = 0.0958 + 0.104 + 0.052 + 0.0548   # boom + 2 motors + 2 props + front gear module, kg
# allowables (MPa), knockdown 0.7 already applied where the repo does
ALW = dict(cfrp_tube=210.0, gfrp_t=105.0, gfrp_c=70.0, gfrp_s=21.0, xps_s=0.175, al7075=503.0, steel_shear=300.0,
           g10_bear=150.0, cf_bear=200.0)
UPD = {}

def ms(allow, demand): return allow / demand - 1.0

# ---------------- 1. V-n / load basis ----------------
V_A, V_C, V_MAX, V_D = 28.5, 20.0, 44.6, 55.8
k_gust = 1.92 / (20.0 * 7.6) * (M_R165 / M)          # Pratt slope calibrated to the R16.5 LC3 (n 2.92 at 20 m/s, 7.6 m/s)
def n_gust(V, U): return 1 + k_gust * V * U
rho, CLmax, S = 1.225, 1.3, 2 * (C_ROOT + C_TIP) / 2 * (Y_TIP - Y_ROOT) * 1e-6 + 0.090 * 0.16
V = np.linspace(0, V_D, 200)
n_stall = 0.5 * rho * V ** 2 * S * CLmax / (M * g)
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.plot(V, np.minimum(n_stall, 3), color='#1f77b4', lw=2, label='Manoeuvre envelope (+3 / −1.5 g)')
ax.plot(V, np.maximum(-n_stall * 0.6, -1.5), color='#1f77b4', lw=2)
ax.plot([V_D, V_D], [-1.5, 3], color='#1f77b4', lw=2)
for U, c in [(7.6, '#d62728'), (5.0, '#ff7f0e')]:
    ax.plot(V, n_gust(V, U), '--', color=c, lw=1.4, label=f'Gust line {U} m/s')
    ax.plot(V, 2 - n_gust(V, U), '--', color=c, lw=1.4)
for v, lab in [(V_A, 'V_A 28.5'), (V_MAX, 'V_max 44.6'), (V_D, 'V_D 55.8')]:
    ax.axvline(v, color='0.75', lw=0.8); ax.text(v + 0.4, -1.9, lab, fontsize=8, color='0.35')
ax.axhline(3, color='0.6', lw=0.6, ls=':'); ax.set_xlabel('Equivalent airspeed (m/s)'); ax.set_ylabel('Load factor n')
ax.set_ylim(-2.2, 5.5); ax.set_title('Flight envelope: design limit +3 / −1.5 g (ultimate × 1.5)', loc='left')
ax.legend(loc='upper left', fontsize=8); fig.tight_layout(); fig.savefig(f'{OUT}/fig1_vn.png', dpi=160); plt.close(fig)
UPD['gust'] = {'n_cruise_7p6': n_gust(V_C, 7.6), 'n_vmax_5': n_gust(V_MAX, 5.0), 'n_vmax_7p6': n_gust(V_MAX, 7.6)}

# ---------------- 2. wing spanwise loads (Schrenk, inertia relief) ----------------
y = np.linspace(0, Y_TIP, 1401)
def chord(yy): return np.where(yy < Y_ROOT, C_ROOT, C_ROOT + (C_TIP - C_ROOT) * (yy - Y_ROOT) / (Y_TIP - Y_ROOT))
def wing_loads(n, mass, ell=True):
    c = chord(y); b2 = Y_TIP
    ell_ = np.sqrt(np.clip(1 - (y / b2) ** 2, 0, None))
    area = np.trapezoid(c, y)
    w = 0.5 * (c / area + ell_ * 4 / (math.pi * b2))                 # Schrenk shape, integrates to 1 over the half span
    w = w / np.trapezoid(w, y)
    L_half = 1.1 * n * mass * g / 2                                    # 1.1 = tail download allowance
    lift = w * L_half
    m_w = M_WING_HALF * (c * (y >= Y_ROOT)) / np.trapezoid(c * (y >= Y_ROOT), y)
    q = lift - n * g * m_w                                             # N/mm
    V_ = np.array([np.trapezoid(q[i:], y[i:]) for i in range(len(y))])
    V_ -= n * g * M_BOOM_SIDE * (y <= Y_BOOM)
    Mb = np.array([np.trapezoid(V_[i:], y[i:]) for i in range(len(y))]) / 1000  # N.m
    return V_, Mb
V1, M1 = wing_loads(3.0, M)
V0, M0 = wing_loads(3.0, M_R165)
iy = lambda yy: int(np.argmin(abs(y - yy)))
ratio_root = M1[iy(0)] / M0[iy(0)]
ratio_92 = M1[iy(92)] / M0[iy(92)]
I_j = math.pi * (12 ** 4 - 10 ** 4) / 64
sig_joiner_lc1 = 1.5 * M1[iy(0)] * 1000 * 6 / I_j
UPD['wing'] = {'M_root_y45_limit_Nm': M1[iy(45)], 'M_centre_limit_Nm': M1[iy(0)], 'ratio_vs_R16_5': ratio_root,
               'joiner_OD12_10_ult_MPa_beam': sig_joiner_lc1}
fig, axs = plt.subplots(2, 1, figsize=(9, 6.2), sharex=True)
axs[0].plot(y, 1.5 * V1, color='#2ca02c', lw=2); axs[0].set_ylabel('Shear, ultimate (N)')
axs[1].plot(y, 1.5 * M1, color='#9467bd', lw=2); axs[1].set_ylabel('Bending moment, ult (N·m)')
for a in axs:
    for yy, lab in [(0, 'joiner centre'), (45, 'wing root'), (Y_BOOM, 'boom / saddle')]:
        a.axvline(yy, color='0.7', lw=0.8, ls='--')
    a.grid(alpha=0.25)
axs[1].text(4, 1.5 * M1[0] * 0.9, f'{1.5 * M1[0]:.1f} N·m at the joiner', fontsize=9)
axs[1].text(Y_BOOM + 5, 1.5 * M1[iy(Y_BOOM)] + 1, 'boom + motors + leg\n(inertia relief)', fontsize=8)
axs[1].set_xlabel('Spanwise station y (mm)')
axs[0].set_title('Wing, +3 g pull-up × 1.5 (LC1): spanwise shear and moment', loc='left')
fig.tight_layout(); fig.savefig(f'{OUT}/fig2_wing_loads.png', dpi=160); plt.close(fig)

# calibrated wing results (R16.5 screen values × load ratio)
R165 = {'tip_defl_lc1_mm': 16.2, 'joiner_lc1_MPa': 278.0, 'joiner_lc3b_MPa': 354.0, 'spar_y92_MPa': 115.0,
        'skin_wrinkle_MPa': 30.8, 'skin_shear_lc7_MPa': 12.4, 'xps_shear_MPa': 0.19, 'fus_aft_MPa': 12.9, 'twist_deg': 0.77}
wing = {
    'tip_deflection_LC1_mm': R165['tip_defl_lc1_mm'] * ratio_root,
    'joiner_OD12_10_LC1_MPa': R165['joiner_lc1_MPa'] * ratio_root,
    'joiner_OD14_11_LC1_MPa': R165['joiner_lc1_MPa'] * ratio_root * (I_j / 6) / (math.pi * (14 ** 4 - 11 ** 4) / 64 / 7),
    'spar_y92_MPa': R165['spar_y92_MPa'] * ratio_92,
    'skin_wrinkling_MPa': R165['skin_wrinkle_MPa'] * ratio_root,
    'xps_core_shear_MPa': R165['xps_shear_MPa'] * ratio_root,
}

# ---------------- 3. landing gear (R16.9 short legs) ----------------
L_leg, rake = 180.6, math.radians(10)
xf, xt = 207.0, 946.7         # foot contact x (front feet moved 35 mm aft with the booms), tail foot
yf = 265.0
z_ground, cg_z = -206.0, -10.0
W = M * g
tail_share = (CG_X - xf) / (xt - xf); front_share = (1 - tail_share) / 2
def gear_loads(L):
    Nf = 5 * W * front_share; D = 0.25 * Nf
    Mcw = (Nf * (L - 8) * math.sin(rake) + D * (L - 8) * math.cos(rake)) / 1000
    N1 = W * front_share
    Mccw = max(0.8 * N1 * (L - 8) * math.cos(rake) - N1 * (L - 8) * math.sin(rake), D * (L - 8) * math.cos(rake) / 1000 * 1000 - Nf * (L - 8) * math.sin(rake)) / 1000
    return Nf, Mcw, Mccw
def tipover(L):
    h = cg_z - (-28 - (L - 8) * math.cos(rake) - 8)
    xfoot = 237 - (L - 8) * math.sin(rake)
    side = abs((xt - xfoot) * (yf - 0) - (xfoot - CG_X) * (0 - yf)) / math.hypot(xt - xfoot, yf)
    fwd = CG_X - xfoot
    return h, math.degrees(math.atan2(side, h)), math.degrees(math.atan2(fwd, h)), side / h, fwd / h
Nf, Mcw, Mccw = gear_loads(L_leg)
I8 = math.pi * (10 ** 4 - 8 ** 4) / 64; I6 = math.pi * (10 ** 4 - 6 ** 4) / 64
sig_rod = 1.5 * Mcw * 1000 * 5 / I8
F_heel = 1.5 * Mcw * 1000 / 9.3
F_lock = 1.5 * Mccw * 1000 / 7.66
h, tip_side, tip_fwd, mu_side, mu_fwd = tipover(L_leg)
gear = {'foot_share_front_each': front_share, 'foot_share_tail': tail_share, 'N_front_5g_limit_N': Nf,
        'knee_CW_limit_Nm': Mcw, 'knee_CCW_limit_Nm': Mccw, 'rod_OD10_8_ult_MPa': sig_rod, 'heel_stop_ult_N': F_heel,
        'shaft_tau_MPa': F_heel / (2 * math.pi * 2.5 ** 2), 'fork_pin_N': F_lock, 'fork_pin_tau_MPa': F_lock / (2 * math.pi * 1.5 ** 2),
        'keeper_MPa': (F_lock * 7.2 / 8) / (7 * 1.4 ** 2 / 6), 'cg_height_mm': h, 'tip_side_deg': tip_side, 'tip_fwd_deg': tip_fwd,
        'rollover_mu_side': mu_side, 'rollover_mu_fwd': mu_fwd}
# leg-length trade figure
Ls = np.linspace(120, 360, 49)
fig, ax1 = plt.subplots(figsize=(9, 5.2))
msr = [ms(ALW['cfrp_tube'], 1.5 * gear_loads(L)[1] * 1000 * 5 / I8) for L in Ls]
ms6 = [ms(ALW['cfrp_tube'], 1.5 * gear_loads(L)[1] * 1000 * 5 / I6) for L in Ls]
ax1.plot(Ls, msr, color='#1f77b4', lw=2, label='Leg rod OD10/8, margin of safety')
ax1.plot(Ls, ms6, color='#1f77b4', lw=1, ls=':', label='Leg rod OD10/6, margin of safety')
ax1.axhline(0, color='k', lw=0.8); ax1.set_ylabel('Margin of safety (5 g + 0.25 drag)'); ax1.set_xlabel('Leg length, pivot to foot tip (mm)')
ax2 = ax1.twinx()
ax2.plot(Ls, [tipover(L)[1] for L in Ls], color='#d62728', lw=2, label='Side tip-over angle')
ax2.plot(Ls, [tipover(L)[2] for L in Ls], color='#ff7f0e', lw=2, label='Nose-over angle')
ax2.set_ylabel('Static tip-over angle (deg)')
for L, lab in [(356, 'R16.6\n356 mm'), (L_leg, 'R16.9\n181 mm')]:
    ax1.axvline(L, color='0.6', ls='--', lw=0.8); ax1.text(L + 2, max(msr) * 0.85, lab, fontsize=8)
h1, l1 = ax1.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, fontsize=8, loc='upper right')
ax1.set_title('Landing gear: shorter legs raise both strength margin and tip-over stability', loc='left')
fig.tight_layout(); fig.savefig(f'{OUT}/fig4_gear_trade.png', dpi=160); plt.close(fig)

# ---------------- 4. wing torsion from the forward foot (landing) ----------------
x_ea = 362.0 + 35
T_land = Nf * (x_ea - xf) / 1000 + 0.25 * Nf * (4 - z_ground) / 1000
A_cell, t_skin = 0.66 * 146 * 11.5, 0.33
tau_skin = 1.5 * T_land * 1000 / (2 * A_cell * t_skin)
T_lc6 = 17.3 * (x_ea - (170 + 35)) / 1000
tor = {'T_landing_limit_Nm': T_land, 'skin_tau_ult_MPa': tau_skin, 'T_LC6_limit_Nm': T_lc6,
       'with_one_pm45_CF_ply_tau_MPa': 1.5 * T_land * 1000 / (2 * A_cell) / (0.2 + 0.33 * 4 / 20)}

# ---------------- 5. booms ----------------
def thin_rect_I(b, hh, t): return hh ** 3 * t / 6 + b * t * hh ** 2 / 2
T_max = 17.3
x_sad0, x_sad1 = 317 + 35, 441 + 35
xb = np.linspace(151.5 + 35, 618.5 + 35, 400)
def boom_M(case):
    Mx = np.zeros_like(xb)
    if case == 'thrust':
        for xm in (170 + 35, 600 + 35):
            arm = np.where(xm < x_sad0, np.clip(x_sad0 - xb, 0, None) * (xb < x_sad0) * (xb > xm) * 0 + np.where((xb > xm) & (xb < x_sad0), xb - xm, 0), 0) if False else None
        Mx = np.where(xb < x_sad0, T_max * np.clip(xb - (170 + 35), 0, None), 0) + np.where(xb > x_sad1, T_max * np.clip((600 + 35) - xb, 0, None), 0)
    else:   # 5 g landing on the front foot: vertical + drag at the foot, through the knee at x 237
        xk = 237.0
        Mx = np.where((xb > xk) & (xb < x_sad0), Nf * (xb - xf) / 1 + 0.25 * Nf * (-28 - z_ground), 0)
        Mx = np.where(xb <= xk, 0, Mx)
    return 1.5 * Mx / 1000
fig, ax = plt.subplots(figsize=(9, 4.6))
ax.plot(xb, boom_M('thrust'), lw=2, label='Max VTOL thrust 17.3 N per motor (× 1.5)')
ax.plot(xb, boom_M('landing'), lw=2, label='5 g landing on the front leg + 0.25 drag (× 1.5)')
ax.axvspan(x_sad0, x_sad1, color='0.9'); ax.text(x_sad0 + 5, ax.get_ylim()[1] * 0.85 if ax.get_ylim()[1] > 0 else 1, 'wing saddle', fontsize=8)
ax.set_xlabel('Boom station x (mm)'); ax.set_ylabel('Bending moment, ult (N·m)'); ax.grid(alpha=0.25); ax.legend(fontsize=8)
ax.set_title('Boom bending: the landing leg, not thrust, sizes the boom', loc='left')
fig.tight_layout(); fig.savefig(f'{OUT}/fig5_boom.png', dpi=160); plt.close(fig)
Mb_land = boom_M('landing').max(); Mb_thr = boom_M('thrust').max()
I_sad = thin_rect_I(26, 43, 0.8); I_knee = thin_rect_I(26, 23, 0.8)
M_knee_stn = 1.5 * Mcw
boom = {'M_saddle_front_ult_Nm': Mb_land, 'sigma_saddle_MPa': Mb_land * 1000 * 21.5 / I_sad,
        'M_thrust_ult_Nm': Mb_thr, 'sigma_knee_station_MPa': M_knee_stn * 1000 * 11.5 / I_knee,
        'saddle_bolt_tension_N': Mb_land * 1000 / 100 / 2}

# ---------------- 6. fuselage ----------------
Nt = 5 * W * tail_share
aft = [(141.4, 1130), (45.0, 1050), (43.8, 945), (100.0, 850)]
M600 = Nt * (xt - 600) / 1000 - sum(m / 1000 * g * 5 * (x - 600) / 1000 for m, x in aft)
fus = {'tail_foot_5g_N': Nt, 'M_x600_limit_Nm': M600, 'sigma_x600_ult_MPa': 1.5 * M600 * 1000 / (math.pi * 40.3 ** 2 * 0.33),
       'flight_aft_shell_MPa': R165['fus_aft_MPa'] * M / M_R165}

# ---------------- 7. mounts / joints ----------------
F_pin = 1.5 * T_land / 0.075            # wing torsion into the root via joiner + D3 pin, 75 mm apart
mounts = {
    'wing_antirotation_pin_D3_tau_MPa': F_pin / (math.pi * 1.5 ** 2),
    'wing_pin_pad_G10_bearing_MPa': F_pin / (3 * 4),
    'boom_saddle_3xM3_bolt_N': boom['saddle_bolt_tension_N'],
    'motor_4xM3_per_motor_N': 1.5 * T_max / 4,
    'knee_block_bond_shear_MPa': 1.5 * Mcw * 1000 / 30 / (2 * 28 * 15),
    'nose_joint_4xM3_shear_N': 1.5 * 5 * (0.1 * g) / 4,
    'tail_knee_doubler_bond_MPa': 1.5 * Nt / (2 * 45 * 12),
    'vtail_root_retention_screw_N': 1.5 * 10.1 * 0.08 / 0.012,
}

# ---------------- 8. margins summary ----------------
MS = [
    ('Wing', 'Joiner OD12/10, +3 g (LC1)', ms(ALW['cfrp_tube'], wing['joiner_OD12_10_LC1_MPa'])),
    ('Wing', 'Joiner OD14/11 (recommended), +3 g', ms(ALW['cfrp_tube'], wing['joiner_OD14_11_LC1_MPa'])),
    ('Wing', 'Spar at y 92, +3 g', ms(ALW['cfrp_tube'], wing['spar_y92_MPa'])),
    ('Wing', 'Skin wrinkling, +3 g', ms(34.2, wing['skin_wrinkling_MPa'])),
    ('Wing', 'XPS core shear (conservative screen)', ms(ALW['xps_s'], wing['xps_core_shear_MPa'])),
    ('Wing', 'Tip deflection vs 35 mm screen', ms(35.0, wing['tip_deflection_LC1_mm'])),
    ('Wing', 'Skin torsion, 5 g landing on the legs', ms(ALW['gfrp_s'], tau_skin)),
    ('Wing', 'Skin torsion with 1 ±45° CF ply (inner wing)', ms(56.0, tor['with_one_pm45_CF_ply_tau_MPa'])),
    ('Boom', 'Section at the saddle, landing', ms(ALW['cfrp_tube'] * 0.7, boom['sigma_saddle_MPa'])),
    ('Boom', 'Section at the knee, landing', ms(ALW['cfrp_tube'] * 0.7, boom['sigma_knee_station_MPa'])),
    ('Landing gear', 'Leg rod OD10/8', ms(ALW['cfrp_tube'], sig_rod)),
    ('Landing gear', 'Knee shaft Ø5, double shear', ms(ALW['steel_shear'], gear['shaft_tau_MPa'])),
    ('Landing gear', 'Fork (lock) pin Ø3', ms(ALW['steel_shear'], gear['fork_pin_tau_MPa'])),
    ('Landing gear', 'Lock keeper, 7075', ms(ALW['al7075'], gear['keeper_MPa'])),
    ('Fuselage', 'Aft shell, +3 g + tail download', ms(16.3, fus['flight_aft_shell_MPa'])),
    ('Fuselage', 'Aft shell, 5 g on the tail leg', ms(16.3, fus['sigma_x600_ult_MPa'])),
    ('Mounts', 'Wing anti-rotation pin D3 (landing torsion)', ms(ALW['steel_shear'], mounts['wing_antirotation_pin_D3_tau_MPa'])),
    ('Mounts', 'Wing pin pad G10 bearing', ms(ALW['g10_bear'], mounts['wing_pin_pad_G10_bearing_MPa'])),
    ('Mounts', 'Boom saddle M3 bolts (tension)', ms(2000 * 0.7, mounts['boom_saddle_3xM3_bolt_N'])),
    ('Mounts', 'Motor M3 screws', ms(2000 * 0.7, mounts['motor_4xM3_per_motor_N'])),
    ('Mounts', 'Knee block bond (epoxy 10 MPa × 0.5)', ms(5.0, mounts['knee_block_bond_shear_MPa'])),
    ('Mounts', 'Tail knee doubler bond', ms(5.0, mounts['tail_knee_doubler_bond_MPa'])),
]
fig, ax = plt.subplots(figsize=(10, 8.6))
labels = [f'{grp}: {lab}' for grp, lab, v in MS]
vals = [max(min(v, 3.0), -1.0) for grp, lab, v in MS]
cols = ['#2ca02c' if v >= 0.25 else '#ffbf00' if v >= 0 else '#d62728' for grp, lab, v in MS]
ax.barh(range(len(MS))[::-1], vals, color=cols)
for i, (grp, lab, v) in enumerate(MS):
    ax.text((min(v, 3.0) if v >= 0 else max(v, -1.0)) + (0.04 if v >= 0 else -0.04), len(MS) - 1 - i, f'{v:+.2f}' if v < 3 else f'>{3:+.0f}',
            va='center', ha='left' if v >= 0 else 'right', fontsize=8)
ax.set_yticks(range(len(MS))[::-1]); ax.set_yticklabels(labels, fontsize=8)
ax.axvline(0, color='k', lw=1); ax.set_xlim(-1.1, 3.4); ax.set_xlabel('Margin of safety (allowable / ultimate demand − 1), capped at 3')
ax.set_title('R16.9 structural margins — green ≥ +0.25, amber 0 to +0.25, red negative', loc='left')
fig.tight_layout(); fig.savefig(f'{OUT}/fig3_margins.png', dpi=160); plt.close(fig)

# ---------------- 9. structural mass ----------------
mass_parts = {'Fuselage + nose': 415 - 39.5 + 4, 'Wing (2 panels)': 357, 'Booms (2)': 188 - 5.8, 'V-tail': 45,
              'Landing gear (3 legs, no servos)': 158.6 - 28.5 + 5.6}
fig, ax = plt.subplots(figsize=(8, 4.2))
ks = list(mass_parts); vs = [mass_parts[k] for k in ks]
ax.barh(ks[::-1], vs[::-1], color='#4c72b0')
for i, v in enumerate(vs[::-1]): ax.text(v + 4, i, f'{v:.0f} g', va='center', fontsize=9)
ax.set_xlabel('CAD structural mass (g)'); ax.set_xlim(0, max(vs) * 1.2)
tot = sum(vs)
ax.set_title(f'Structure ≈ {tot:.0f} g in CAD (+≈ 85 g bond/finish) = {100 * (tot + 85) / (M * 1000):.0f} % of {M * 1000:.0f} g', loc='left')
fig.tight_layout(); fig.savefig(f'{OUT}/fig6_mass.png', dpi=160); plt.close(fig)

res = {'config': {'mass_kg': M, 'cg_x': CG_X, 'np_x_rough': NP_X, 'static_margin_pct': (NP_X - CG_X) / MAC * 100},
       'load_basis': UPD, 'wing': wing, 'wing_torsion_landing': tor, 'boom': boom, 'landing_gear': gear, 'fuselage': fus,
       'mounts': mounts, 'margins': [(a, b, round(c, 3)) for a, b, c in MS], 'structural_mass_g': mass_parts}
json.dump(res, open(f'{OUT}/results.json', 'w'), indent=1, default=float)
for a, b, c in MS: print(f'{a:13s} {b:48s} {c:+.2f}')
print(json.dumps({k: res[k] for k in ['config', 'load_basis', 'landing_gear', 'boom', 'fuselage', 'wing_torsion_landing']}, indent=1, default=lambda v: round(v, 2)))
