"""Screening check of the wing root/joiner at +3 g x 1.5 (repo load basis). Not a strength release."""
import numpy as np, json
from geom import wchord, wxle, AF, SPAR_FRAC
W = 3.42*9.80665; n, U = 3.0, 1.5
ys = np.linspace(45, 700, 400); c = np.array([wchord(y) for y in ys])
# lift per half proportional to chord (conservative vs elliptic for root moment), carried by both halves
w_lift = n*W/2*c/np.trapezoid(c, ys)                    # N/mm
m_wing = 0.17 + 0.03                                 # kg per half: CAD wing + core/bond allowance
w_iner = n*m_wing*9.80665*c/np.trapezoid(c, ys)
def M_at(y0, relief=True):
    m = ys >= y0; arm = ys[m]-y0
    M = np.trapezoid((w_lift[m] - (w_iner[m] if relief else 0))*arm, ys[m])
    if relief and y0 < 265: M -= n*0.25*9.80665*(265-y0)          # boom + 2 motors/props per side
    return M*U                                                     # N*mm, ultimate
Mroot = M_at(45.0); Mj = M_at(0.0)
E_cf, E_gf, Ec, Gc = 70e3, 15e3, 15.0, 8.0                        # MPa (repo inputs: skin 15 GPa, spar 70 GPa, foam G 8 MPa)
def tube_I(D, d): return np.pi/64*(D**4-d**4)
cr = wchord(60); i = np.argmin(AF[:, 0]); up, lo = AF[:i+1][::-1], AF[i:]
h = (np.interp(SPAR_FRAC, up[:, 0], up[:, 1]) - np.interp(SPAR_FRAC, lo[:, 0], lo[:, 1]))*cr
b_eff = 0.45*cr; t = 0.33
EI_skin = E_gf*2*(t*b_eff)*(h/2)**2
out = {'ultimate_root_moment_Nm_wing_root_y45': round(Mroot/1e3, 1), 'ultimate_moment_at_joiner_centre_Nm': round(Mj/1e3, 1)}
for name, D, d, core in (('R13 ribs + OD8/6.4 spar', 8, 6.4, False), ('R15 full core + OD10/8 spar', 10, 8, True)):
    EI_sp = E_cf*tube_I(D, d)
    if core:
        k = Mroot/(EI_sp + EI_skin); skin = E_gf*k*h/2; spar = E_cf*k*D/2
        wr = 0.5*(E_gf*Ec*Gc)**(1/3)
        out[name] = dict(spar_stress_MPa=round(spar), skin_stress_MPa=round(skin), skin_wrinkling_theory_MPa=round(wr),
                         wrinkling_ratio_with_0p6_knockdown=round(0.6*wr/skin, 2))
    else:
        R = (cr/2)**2/(2*0.06*cr); sig_cr = 0.3*0.6*E_gf*t/R               # curved panel between ribs, 0.3 knockdown
        spar_alone = Mroot*(D/2)/tube_I(D, d)
        out[name] = dict(upper_skin_panel_buckling_MPa=round(sig_cr, 1), skin_stress_if_effective_MPa=round(E_gf*Mroot/(EI_sp+EI_skin)*h/2),
                         spar_stress_after_skin_buckles_MPa=round(spar_alone))
for name, D, d in (('R13 joiner OD8/6', 8, 6), ('R15 joiner OD12/10', 12, 10)):
    out[name] = dict(bending_stress_MPa=round(Mj*(D/2)/tube_I(D, d)))
json.dump(out, open('/home/claude/full/out/wing_screen.json', 'w'), indent=1); print(json.dumps(out, indent=1))
