# R16.9 data package for Stability & Control

This answers the S&C data request (November 22, 2026) for everything the CAD and Structures can supply. Items that only Aero, Propulsion or W&P can provide are listed at the end, so nothing is left implied.

**One baseline:** R16.9 CAD, STEP SHA-256 `0d635dac…6c3f`. Every number here comes from that file.

## 1. Coordinate reference and assumptions

**CAD frame**
- Origin at the nose tip.
- **X aft, Y right (starboard), Z up.**
- The fuselage axis is at z = 0. Units are mm and g.

**Body frame for S&C:** x_b = −X (forward), y_b = Y, z_b = −Z (down). Conversion:
- Ixx, Iyy and Izz are unchanged.
- The products Ixy and Iyz change sign.
- Ixz keeps its sign.

**Product of inertia convention:** `Ixz = Σ m·x·z` (positive form). The inertia tensor element is −Ixz.

**Structure masses**
- Thin skins use the R16 BOM masses, because OCC volume integration is unreliable on 0.33 mm skins.
- Every other part uses the CAD volume × density. Densities are in `mass_properties/massprops.py`.
- Centroids and inertia always come from the R16.9 geometry. Skins use surface-weighted centroids.

**Bond, fillet and finish allowance:** 7.5 % of the CAD structure (83.5 g), spread with the structure's own CG and inertia.

**Equipment**
- Masses come from the team equipment list (`inputs.json`) and catalogues.
- Each item is placed on its CAD envelope, as a solid of uniform density.
- The source of every line is in `mass_properties/R16_9_component_masses.csv`.

**Buoy + release magnet:** a 370 g point mass at (350, 0, −55), the release plate.

**Landing gear:** both states are modelled. The moving parts come from the retracted solution.

## 2. Mass, CG and inertia (Luis's and Owen's items)

| Case | Mass (kg) | CG x, y, z (mm, CAD) | Ixx | Iyy | Izz | Ixz | SM at NP 431 (rough) |
|---|---|---|---|---|---|---|---|
| **A** Takeoff/hover: gear down, buoy on | **3.745** | **424.0**, 0.0, −7.6 | 0.0990 | 0.2846 | 0.3783 | 0.0032 | +5.2 % |
| **B** Cruise: gear up, buoy on | 3.745 | 424.4, 0.0, −6.5 | 0.0983 | 0.2816 | 0.3761 | 0.0033 | +4.9 % |
| **C** After release: gear up, buoy off | 3.375 | **432.6**, 0.0, −1.1 | 0.0973 | 0.2784 | 0.3738 | 0.0018 | **−1.2 %** |
| **D** Return/landing: gear down, buoy off | 3.375 | 432.2, 0.0, −2.4 | 0.0981 | 0.2814 | 0.3761 | 0.0017 | −0.9 % |
| **E** = A + structural fixes (section 6) | 3.803 | 423.5, 0.0, −7.4 | 0.1003 | 0.2847 | 0.3797 | 0.0032 | +5.6 % |
| **F** = A without the two unresolved allocations | 3.259 | 447.4, 0.0, −8.7 | 0.0990 | 0.2171 | 0.3109 | 0.0038 | −12.1 % |

- Inertia values are kg·m², about the CG of each case.
- Static margin = (NP − CG) / MAC, with MAC 135.1 mm.
- **The NP of 431 mm is only a rough wing-share estimate**; Aero must replace it. The point of the column is that **case C lands on or behind the NP**.

**Buoy release:** the CG moves **8.2 mm aft** and the mass drops by 370 g. This matches the "~8 mm" in the request.

**Without the bond allowance,** case A is 3.662 kg at x 422.4. That agrees with the 3.652 kg / 421 mm quoted so far, which had no allowance.

**Compared with the Stability Report (3.607 kg source model: 0.186 / 0.284 / 0.434, Ixz 0.027):**
- Iyy agrees.
- Ixx is about half and Ixz about a tenth of the report's.
- Use the CAD-based set above; it places the wing, booms and motors where they are now.

### Mass by group (case A)

| Group | Mass (g) | x (mm) |
|---|---|---|
| Battery (2 × 472 g modules) | 944.0 | 317.5 |
| Avionics and sensor (includes both unresolved allocations) | 745.0 | 342.2 |
| Propulsion (4 × UM2807 52 g, 4 × APC 10×3 26.1 g, pusher 148.9 g) | 461.3 | 646.6 |
| Payload (buoy 360 g + magnet 10 g) | 370.0 | 350.0 |
| Wing (2 panels) | 364.2 | 418.1 |
| Fuselage structure | 330.1 | 604.0 |
| Booms (2) | 187.3 | 422.4 |
| Landing gear (structure 138.6 g + 3 servos 28.5 g) | 167.1 | 481.7 |
| Allowance (bonds, fillets, finish) | 83.5 | 494.6 |
| Nose module structure | 47.8 | 130.4 |
| V-tail (2 panels) | 44.8 | 1045.6 |
| **Total** | **3745.1** | **424.0** |

### Equipment lines that need an owner's decision

These move the CG a lot.

| Line | Mass | Where | Effect |
|---|---|---|---|
| "Camera/AI" allocation | 350 g | x 60 | Probably the old camera line, now that the ELP (35 g) is modelled separately. Cutting it alone moves the CG about **37 mm aft**; cutting both allocations (case F) moves it 23 mm aft |
| "Other servo" allocation | 136.2 g | x 800 | `inputs.json` residual. The gear and V-tail servos are now explicit |
| Flight controller + receiver | **0 g** | x 106–200 | No mass yet. Add real values |
| ELP camera | 35 g | x 28–74 | Assumed. Weigh it |

## 3. Geometry (Owen's items, for Raphael's XFLR5 model)

All values are in `geometry/R16_9_geometry_reference.json`. They were measured by cutting sections through the R16.9 skins.

### Wing
- **Reference trapezoid** (extrapolated to the centreline):
  - span 1400 mm;
  - root chord **165.0** and tip chord **100.0** mm, taper 0.606;
  - **S = 0.1855 m²**, AR 10.57.
- **Leading edge:** x 295.0 at the centreline and 435.0 at the tip, a sweep of 11.3°.
- **MAC 135.1 mm** at y 321.4. **MAC LE x 359.3**, quarter-MAC x 393.1.
- **Dihedral 0°**, incidence 0.1° (effectively 0°), no twist. The chord line is at z 0.
- SD7037. The exposed wing starts at y ±44.
- **There are no ailerons or flaps in the R16.9 CAD** (see section 6).

### V-tail
Each panel is measured in its own plane; s is the distance along the panel from the fuselage side.

- **Dihedral 35°**, NACA 0010. Panel span 221 mm.
- Root chord 85.2 and tip chord 44.6 mm (taper 0.524). The LE sweep in the panel plane is 26.1°.
- **Areas:**
  - true area 0.0287 m² for both panels;
  - horizontal projection 0.0235 m²;
  - vertical projection 0.0165 m².
- **Tail MAC 67.0 mm**, with its quarter-chord at x 1038.0. The **tail arm from the case-A CG is 614 mm**.
- **Volume coefficients (projected areas):** horizontal 0.576, vertical 0.039.

### Buoy
- Release plate at x 325–375, z −55. The 370 g release shifts the CG **+8.2 mm**.
- A suggested move to x ≈ 397–447 (centred near the CG) would remove most of the shift. That is an S&C/Mission decision.

### Battery relocation range
- **Pack:** 6S2P M65A, two modules (75 × 68 × 47 mm, 472 g each).
- **Front module** (now x 200–275):
  - its start can move from x 200 to x 242;
  - forward it is limited by the flight controller and receiver (x 199.5), aft by ring frame F317.
- **Rear module** (now x 360–435):
  - its start can move from x 356.5 to x 365;
  - it is limited by ring frame F355 forward and the ESC deck (x 440) aft.
- **CG trim authority:**
  - **+5.3 mm aft** with the front module fully aft;
  - −0.4 to +0.6 mm from the rear module.
  - **The battery cannot move the CG forward** unless the flight controller moves.
- The saddles are bonded frames, so the final position must be fixed before the internals are bonded (build step 2).

### Sensors
- **Flight controller / IMU** envelope centre: (152.5, 0, 6.3). Lever arm from the case-A CG: **(−271.5, 0, +13.9) mm**, CAD axes.
- **ELP camera** at (51, 0, −2.5), looking forward and 45° down.
- GPS, compass and airspeed probe are not modelled yet.

## 4. Motors and thrust lines (for Matthew; positions only)

| Motor | Prop hub (x, y, z) mm | Thrust axis | Prop | Spin (seen from above) |
|---|---|---|---|---|
| Front right | 205, +265, 14.3 | +Z, no cant | APC 10×3 LP10030 | CCW |
| Rear right | 635, +265, 14.3 | +Z | APC 10×3 LP10030P | CW |
| Front left | 205, −265, 14.3 | +Z | APC 10×3 LP10030P | CW |
| Rear left | 635, −265, 14.3 | +Z | APC 10×3 LP10030 | CCW |
| Pusher (Tarot 4008) | prop at 1139, 0, 0 | −X (forward thrust) | APC 13×8 LP13080P | — |

- The diagonal pairs spin the same way (FR and RL CCW; FL and RR CW).
- **Pusher thrust line:** z = 0, which is 6.5 mm above the cruise CG (case B). Thrust therefore gives a small nose-down moment.
- **Hover thrust split** (geometric, at the CG):

| Case | Front pair | Rear pair | Per front motor | Per rear motor |
|---|---|---|---|---|
| A, 36.74 N | 18.03 N | 18.71 N | 9.01 N | 9.36 N |
| D, 33.11 N | 15.62 N | 17.49 N | 7.81 N | 8.75 N |

## 5. Structures answers (Diego's items)

| Request | Answer |
|---|---|
| Final wing dihedral | **0° in R16.9.** Structures can build 3° or 5° by molding the root elbows at that angle; the joiner stays straight. With dihedral, the boom stations rise and the **lift-motor axes tilt inboard by the dihedral angle** unless the saddle is re-angled. Tell us which you want, and whether the motors should stay vertical. |
| V-tail servo and linkage geometry | Two HS-5085MG servos (envelope x 930–960, y ±16, z −14.8…17.2). The pushrods run aft through two Ø8 channels in the root block at y ±12, z −8. **Horns and pushrods are not modelled.** Ruddervator hinge line (L panel; R is the mirror in y): root (1031.1, −22.0, 14.0) to tip (1111.3, −203.0, 140.8). Ruddervator chord 26.9 → 14.7 mm, about 32 % of the chord, over the full panel span (1.0 mm root gap). |
| Maximum control-surface deflection | **Ruddervators: ±25° clear of the fixed skin and the shell** (R16.5 motion check; the LE is bevelled 27°). Your control-throw limit should sit inside this. There are no other aerodynamic control surfaces. |
| Mass changes from structural modifications | Joiner OD12/10 → OD14/11: **+3.6 g** at x 345. One ±45° CF ply on each inner wing: **+25 g per side** (x ≈ 395, y ±155). Total **+53.6 g**; the CG moves 0.5 mm forward (case E). The 7.5 % bond allowance is already in cases A–F. |

## 6. Findings that matter for S&C

1. **Static margin after the buoy release.** With the rough NP of 431 mm:
   - the CG at x 432.6 gives **−1.2 % MAC** (gear up, buoy off);
   - before the release it is +5 %.
   - The NP has to come from XFLR5 at this wing position before any margin is quoted.
   - Moving the buoy plate to the CG removes most of the 8 mm shift. The battery cannot fix it.
2. **No ailerons.**
   - Roll control in wing-borne flight currently comes only from the ruddervators, through yaw-roll coupling, which is weak at 0° dihedral. Near hover, the lift motors also give roll control.
   - The dihedral comparison should include roll authority.
   - The alternative is to add ailerons, which Structures can cut into the panels behind the aft tube.
3. **The equipment list.** The 350 g and 136.2 g allocations decide whether the CG is 424 or 447 mm. Confirm or cut them before freezing S&C.
4. **Gust load factor.** A 5 m/s gust at V_max gives 3.9 g, above the +3 g structural basis. The speed envelope in turbulence should be limited to about V_B (≈ 30 m/s).

## 7. Not from Structures/CAD (owners)

| Item | Owner |
|---|---|
| Neutral point, stability derivatives, control effectiveness, 0°/3°/5° dihedral comparison | Raphael (XFLR5, using the geometry in section 3) |
| Thrust vs RPM/throttle, thrust limits, final pack confirmation | Matthew (positions in section 4) |
| Flight-performance conditions at the new mass | Luis (mass properties in section 2) |
| FC/receiver masses, final camera/AI hardware | Avionics / mission |
