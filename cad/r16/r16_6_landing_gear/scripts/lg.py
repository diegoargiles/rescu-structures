"""RescU R16.6 retractable landing gear: knee module geometry (CadQuery).

Module frame (right front boom): origin at the knee pivot P, X = u (aft), Y = v (outboard, +y for the right boom),
Z = w (up). Units mm, angles deg.
Right boom module: global = (202 + u, 265 + v, -28 + w).  Left boom: mirror v -> -v, global (202 + u, -265 + v, -28 + w).
Tail module: yaw 180 deg (u -> -x, v -> -y), small nose-down tilt, pivot at (915, 0, -25).

Mechanism ("knee"):
  servo (muscle) -> servo arm pin -> vertical slot in the tendon plate (scotch yoke) -> tendon plate slides along X on two
  guide pins -> a ⊥-shaped slot in the plate drives the horn ("kneecap") pin -> horn is keyed to the knee shaft -> knuckle
  -> leg rod -> foot.  The last 4 mm (deploy) / 2 mm (retract) of plate travel is lost motion: the horn pin sits in the
  horizontal bar of the ⊥ slot, so the leg cannot rotate and leg loads go into the plate and guide pins, not the servo.
  Deployed CW (rake-forward) loads go into the heel stop on the knee block.
"""
import math
import cadquery as cq
from cadquery import Vector as V

# ---------------- parameters ----------------
P_R = (202.0, 265.0, -28.0)          # right front knee pivot (global)
P_T = (915.0, 0.0, -25.0)            # tail knee pivot (global)
THETA_DEP = -100.0                   # leg angle deployed (from +u toward +w): 10 deg forward rake
THETA_RET = 0.0
ALPHA = 140.0                        # horn (fork pin) angle relative to leg
R_HORN = 10.0
L_FRONT = 356.0                      # pivot -> foot tip, front legs
FOOT_R = 8.0                         # TPU foot, dia 16
ROD_OD, ROD_ID = 10.0, 6.0
LOCK_DEP, LOCK_RET = 4.0, 2.0        # lost-motion lock travel
HU = R_HORN * math.cos(math.radians(40))      # 7.66
HW0 = R_HORN * math.sin(math.radians(40))     # 6.43 lowest pin centre
D_DEP = HU + LOCK_DEP                # 11.66 plate displacement, deployed + locked
D_RET = -HU - LOCK_RET               # -9.66
D0 = (D_DEP + D_RET) / 2             # 1.0
SERVO_U, SERVO_W = 80.0, 10.5        # servo output shaft (module frame)
R_ARM = (D_DEP - D0) / math.sin(math.radians(60))   # 12.31, servo sweeps +-60 deg
PSI_DEP, PSI_RET = 60.0, -60.0
G1 = (22.0, 10.0)                    # guide pin 1, across the knee block walls (double shear)
G2 = (100.0, 0.0)                    # guide pin 2, in the trough guide tab
KN = 6.5                             # knuckle hub / socket half width
FORK = (0.9, 3.4)                    # fork arm |v| range (plate runs between the arms)
HEEL = (3.6, KN)                     # heel lug |v| range
PLATE = (-0.8, 0.8)                  # tendon plate, centre plane
WALL = (6.8, 8.8)                    # knee block side walls |v|
BRK = (9.5, 10.5)                    # tendon bracket side leg (outboard)
ARM = (8.1, 9.3)                     # servo arm


def pose(psi):
    """servo angle psi (deg, from straight down toward +u) -> (plate displacement d, leg angle theta)."""
    d = D0 + R_ARM * math.sin(math.radians(psi))
    if d >= HU: phi = 40.0
    elif d <= -HU: phi = 140.0
    else: phi = math.degrees(math.acos(d / R_HORN))
    return d, phi - ALPHA


# ---------------- primitives ----------------
def box(u0, u1, v0, v1, w0, w1):
    return cq.Solid.makeBox(u1 - u0, v1 - v0, w1 - w0, V(u0, v0, w0))

def cylY(u, w, r, v0, v1):
    return cq.Solid.makeCylinder(r, v1 - v0, V(u, v0, w), V(0, 1, 0))

def cylX(u0, u1, r, v=0.0, w=0.0):
    return cq.Solid.makeCylinder(r, u1 - u0, V(u0, v, w), V(1, 0, 0))

def prism(pts, v0, v1):
    wire = cq.Wire.makePolygon([V(p[0], v0, p[1]) for p in pts], close=True)
    return cq.Solid.extrudeLinear(cq.Face.makeFromWires(wire), V(0, v1 - v0, 0))

def stadium(p0, p1, r, v0, v1):
    """slot between centres p0, p1 (u,w) with radius r, through v0..v1"""
    (a, b), (c, d) = p0, p1
    L = math.hypot(c - a, d - b)
    s = cylY(a, b, r, v0, v1).fuse(cylY(c, d, r, v0, v1))
    if L > 1e-6:
        nu, nw = (c - a) / L, (d - b) / L
        pu, pw = -nw * r, nu * r
        s = s.fuse(prism([(a + pu, b + pw), (c + pu, d + pw), (c - pu, d - pw), (a - pu, b - pw)], v0, v1))
    return s

def U(*s):
    out = s[0]
    for x in s[1:]: out = out.fuse(x)
    return out.clean()

def rotY(shape, theta):      # rotate leg-group parts from the theta=0 frame to theta (deg, +u toward +w)
    return shape.rotate(V(0, 0, 0), V(0, 1, 0), -theta)


# ---------------- moving parts (leg group built at theta = 0, i.e. retracted) ----------------
def _sym(s, rng):            # solid at v in +rng and mirrored at -rng
    return s(rng[0], rng[1]).fuse(s(-rng[1], -rng[0]))

def knuckle():
    hub = cylY(0, 0, KN, -KN, KN)
    sock = cylX(0, 21, KN)
    a = math.radians(ALPHA); hu, hw = R_HORN * math.cos(a), R_HORN * math.sin(a)
    fork = _sym(lambda v0, v1: U(stadium((0, 0), (hu, hw), 2.6, v0, v1), cylY(hu, hw, 2.6, v0, v1)), FORK)
    heel = _sym(lambda v0, v1: box(-10.5, 0, v0, v1, -3.5, 3.5).intersect(cylY(0, 0, 10.5, v0 - 1, v1 + 1)), HEEL)
    k = U(hub, sock, fork, heel)
    k = k.cut(cylX(5, 22, ROD_OD / 2 + 0.05))
    k = k.cut(cylY(0, 0, 2.5, -10, 10))                                   # knee shaft (keyed by roll pin)
    k = k.cut(cylY(hu, hw, 1.5, -5, 5))                                   # fork (kneecap) pin
    gap = box(-20, 20, -FORK[0], FORK[0], 3.0, 20).fuse(box(-20, 1.0, -FORK[0], FORK[0], -20, 20))
    k = k.cut(gap.intersect(cylY(0, 0, 14, -2, 2)).cut(cylY(0, 0, 3.6, -2, 2)))   # centre-plane gap for the tendon plate
    k = k.cut(cq.Solid.makeCylinder(0.75, 30, V(-1.2, 0, -15), V(0, 0, 1)).intersect(box(-3, 3, -KN, KN, -15, 15)))
    return k

def shaft():
    s = cylY(0, 0, 2.5, -WALL[1], WALL[1])
    return s.cut(cq.Solid.makeCylinder(0.75, 30, V(-1.2, 0, -15), V(0, 0, 1)).intersect(box(-3, 3, -KN, KN, -15, 15)))

def fork_pin():
    a = math.radians(ALPHA)
    return cylY(R_HORN * math.cos(a), R_HORN * math.sin(a), 1.5, -FORK[1], FORK[1])

def rod(L=L_FRONT):
    return cylX(5, L - 11, ROD_OD / 2).cut(cylX(4, L, ROD_ID / 2))

def foot(L=L_FRONT):
    c = L - FOOT_R
    f = U(cylX(c - 14, c, FOOT_R), cq.Solid.makeSphere(FOOT_R, V(c, 0, 0), angleDegrees1=-90, angleDegrees2=90))
    return f.cut(cylX(c - 15, L - 11, ROD_OD / 2))


def plate():
    """tendon plate in its own frame (xi = u - d), centre plane."""
    v0, v1 = PLATE
    head = prism([(-7.4, 3.95), (5.4, 3.95), (5.4, 12.8), (-3.0, 12.8), (-7.4, 9.0)], v0, v1)
    arm1 = box(-2, 48, v0, v1, 7.2, 12.8)
    p = U(head, arm1)
    for dd in (D_DEP, D_RET):                                   # clear the knuckle hub at both ends of travel
        p = p.cut(cylY(-dd, 0, 7.0, v0 - 1, v1 + 1))
    hb = 1.55
    stem = stadium((0, HW0), (0, R_HORN), hb, v0 - 1, v1 + 1)
    bar = stadium((-LOCK_DEP, HW0), (LOCK_RET, HW0), hb, v0 - 1, v1 + 1)
    s1 = stadium((G1[0] - D_DEP, G1[1]), (G1[0] - D_RET, G1[1]), 1.6, v0 - 1, v1 + 1)
    rv = cylY(40.0, 10.0, 1.0, v0 - 1, v1 + 1).fuse(cylY(45.5, 10.0, 1.0, v0 - 1, v1 + 1))   # rivet holes
    return p.cut(U(stem, bar, s1, rv))

def bracket():
    """tendon bracket (riveted to the plate, same rigid body): crosses outboard and carries the servo + guide-2 slots."""
    fl = box(37, 48, PLATE[1], PLATE[1] + 1.0, 7.2, 12.8)                 # flange on the plate
    web = box(46, 48, PLATE[1], BRK[1], 7.2, 9.0)                        # cross web above the trough
    side = box(46, 70, BRK[0], BRK[1], 2.0, 9.0).fuse(box(68, 112, BRK[0], BRK[1], -4.4, 9.0))
    b = U(fl, web, side)
    xs = SERVO_U - D0
    ss = stadium((xs, SERVO_W - R_ARM), (xs, SERVO_W - R_ARM * 0.5), 1.55, BRK[0] - 1, BRK[1] + 1)
    s2 = stadium((G2[0] - D_DEP, G2[1]), (G2[0] - D_RET, G2[1]), 1.6, BRK[0] - 1, BRK[1] + 1)
    rv = cylY(40.0, 10.0, 1.0, 0, 3).fuse(cylY(45.5, 10.0, 1.0, 0, 3))
    return b.cut(U(ss, s2, rv))

def servo_arm(psi):
    a = math.radians(psi); pu, pw = SERVO_U + R_ARM * math.sin(a), SERVO_W - R_ARM * math.cos(a)
    arm = U(cylY(SERVO_U, SERVO_W, 3.5, *ARM), cylY(pu, pw, 2.8, *ARM), stadium((SERVO_U, SERVO_W), (pu, pw), 2.2, *ARM))
    arm = arm.cut(cylY(SERVO_U, SERVO_W, 1.4, ARM[0] - 1, ARM[1] + 1)).cut(cylY(pu, pw, 1.5, ARM[0] - 1, ARM[1] + 1))
    pin = cylY(pu, pw, 1.5, ARM[0], BRK[1] + 0.4)
    return arm, pin


# ---------------- fixed parts ----------------
def knee_block():
    top, bot = 17.0, -9.0                                   # raw, trimmed to the boom later
    walls = _sym(lambda v0, v1: box(-12.6, 26, v0, v1, bot, top), WALL)
    front = box(-12.6, -10.6, -WALL[1], WALL[1], bot, top).cut(box(-13, -10, -1.1, 1.1, 2.8, 20))   # plate passes
    boss = _sym(lambda v0, v1: prism([(4.84, 7.27), (5.9, 13.2), (9.5, 13.2), (9.5, 6.95), (6.81, 6.92)], v0, v1), (HEEL[0], WALL[0] + 0.01))
    keeper = box(4.0, 11.0, -HEEL[1] - 0.3, HEEL[1] + 0.3, 12.9, 15.5)           # lock keeper over the plate head
    boss2 = _sym(lambda v0, v1: box(5.9, 11.0, v0, v1, 11.6, 15.5), (HEEL[0], WALL[0] + 0.01))
    b = U(walls, front, boss, boss2, keeper)
    b = b.cut(box(21, 30, -6.4, 6.4, -20, 6.3))              # trough runs in under the aft end
    b = b.cut(cylY(0, 0, 2.55, -WALL[1] - 1, WALL[1] + 1))       # shaft bores
    b = b.cut(cylY(G1[0], G1[1], 1.5, -WALL[1] - 1, WALL[1] + 1))  # guide pin 1
    return b

def guide_pin_1():
    return cylY(G1[0], G1[1], 1.5, -WALL[1], WALL[1])

def guide_pin_2():
    return cylY(G2[0], G2[1], 1.5, 6.0, BRK[1] + 0.4)

def guide_tab():
    t = box(G2[0] - 3.5, G2[0] + 3.5, 6.0, ARM[1], -9.0, 4.0)
    return t.cut(cylY(G2[0], G2[1], 1.5, 5, 12))

def servo_ref():
    body = box(SERVO_U - 6, SERVO_U + 17.5, -10.6, 6.4, SERVO_W - 4, SERVO_W + 4)
    boss = cylY(SERVO_U, SERVO_W, 3.5, 6.4, 8.0)
    sh = cylY(SERVO_U, SERVO_W, 1.4, 8.0, ARM[1])
    return U(body, boss, sh)

def servo_mount():
    a = box(SERVO_U - 8, SERVO_U - 6, -12.0, 6.4, 6.05, 17.0)
    b = box(SERVO_U + 17.5, SERVO_U + 19.5, -12.0, 6.4, 6.05, 17.0)
    return U(a, b)

def trough(L=L_FRONT, bottom=-17.0):
    """CFRP channel, open at the bottom (the boom/belly slot); rod section then foot pocket."""
    t = 0.5
    up = L - 2 * FOOT_R - 8
    ue = L + 2.6
    rod_in, pk_in = 5.5, 8.5
    outer = U(box(22.5, up, -rod_in - t, rod_in + t, bottom, rod_in + t),
              box(up - t, ue + t, -pk_in - t, pk_in + t, bottom, pk_in + t))
    inner = U(box(20, up + 0.01, -rod_in, rod_in, bottom - 1, rod_in),
              box(up, ue, -pk_in, pk_in, bottom - 1, pk_in))
    return outer.cut(inner)

def slot_cutter(L=L_FRONT, w0=-22.0, w1=-3.0):
    up = L - 2 * FOOT_R - 8
    return U(box(-9.0, 22.5, -7.0, 7.0, w0, w1), box(22.5, up, -5.5, 5.5, w0, w1), box(up, L + 2.6, -8.5, 8.5, w0, w1))


# ---------------- assembly in module frame ----------------
LEG = ['Knuckle', 'Knee_Shaft', 'Fork_Pin', 'Leg_Rod', 'Foot']
TENDON = ['Tendon_Plate', 'Tendon_Bracket']
ARMG = ['Servo_Arm', 'Servo_Arm_Pin']
MOVING = LEG + TENDON + ARMG

def leg_group(theta, L=L_FRONT):
    parts = {'Knuckle': knuckle(), 'Knee_Shaft': shaft(), 'Fork_Pin': fork_pin(), 'Leg_Rod': rod(L), 'Foot': foot(L)}
    return {k: rotY(s, theta) for k, s in parts.items()}

def fixed_parts(L=L_FRONT):
    return {'Knee_Block': knee_block(), 'Guide_Pin_1': guide_pin_1(), 'Guide_Pin_2': guide_pin_2(),
            'Guide_Tab': guide_tab(), 'REF_Servo_KST_X08H': servo_ref(), 'Servo_Mount': servo_mount(), 'Trough': trough(L)}

def moving_parts(psi, L=L_FRONT):
    d, theta = pose(psi)
    m = leg_group(theta, L)
    m['Tendon_Plate'] = plate().translate(V(d, 0, 0))
    m['Tendon_Bracket'] = bracket().translate(V(d, 0, 0))
    m['Servo_Arm'], m['Servo_Arm_Pin'] = servo_arm(psi)
    return m, d, theta
