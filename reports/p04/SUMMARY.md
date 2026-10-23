# RescU Structures V4 — P04 attachment study

UNRESOLVED — preliminary mass budget and structural screening

## Mass summary

| Quantity | Value |
|---|---|
| Modeled structural material | 918.220 g |
| Finish and installation budgets | 122.808 g |
| Added user structural parts | 0.000 g |
| Structural budget (incomplete) | 1041.028 g |
| Accounted aircraft estimate | 3.5163 kg |
| Sizing aircraft mass | 3.7163 kg |
| Unallocated sizing reserve | 200.0 g |
| Battery pack budget (assumed) | 944.0 g |

CAD material quantities use m=rho×V; hidden untrimmed wing/tail sources and prop/ESC gauges are excluded. No second spar-foam subtraction. Reserve is separate from component mass and has no assigned CG.

## Modeled materials

| Material | Mass g |
|---|---|
| GFRP | 598.107 |
| Ravatherm XPS X H LB | 40.610 |
| Epoxy | 5.473 |
| CFRP | 265.930 |
| Aluminum 6061-T6 | 8.100 |

Wing/tail cores contain the represented XPS. Candidate localized fuselage foam is counted; final hardpoint closure remains open.

## CAD structural components

| Part | Material | Mass g | Centroid X mm |
|---|---|---|---|
| Fuselage_GFRP_Shell_0330 | GFRP | 162.873 | 528.92 |
| Wing_PosY_GFRP_Skin_Exposed | GFRP | 87.803 | 401.85 |
| Wing_PosY_Ravatherm_Core_Exposed | Ravatherm XPS X H LB | 17.542 | 380.85 |
| Wing_PosY_EpoxyBond_Exposed | Epoxy | 2.736 | 368.72 |
| VTail_PosY_GFRP_Skin_Exposed | GFRP | 12.948 | 1055.47 |
| VTail_PosY_Ravatherm_Core_Exposed | Ravatherm XPS X H LB | 1.620 | 1046.77 |
| Wing_NegY_GFRP_Skin_Exposed | GFRP | 87.261 | 401.80 |
| Wing_NegY_Ravatherm_Core_Exposed | Ravatherm XPS X H LB | 17.542 | 380.85 |
| Wing_NegY_EpoxyBond_Exposed | Epoxy | 2.736 | 368.72 |
| VTail_NegY_GFRP_Skin_Exposed | GFRP | 12.949 | 1055.47 |
| VTail_NegY_Ravatherm_Core_Exposed | Ravatherm XPS X H LB | 1.620 | 1046.77 |
| Wing_PosY_CFRP_TaperedSpar | CFRP | 45.527 | 353.80 |
| VTOL_Arm_PosY | CFRP | 53.760 | 395.00 |
| Wing_NegY_CFRP_TaperedSpar | CFRP | 45.527 | 353.80 |
| VTOL_Arm_NegY | CFRP | 53.760 | 395.00 |
| Payload_MountPlate_PROVISIONAL | Aluminum 6061-T6 | 8.100 | 350.00 |
| MotorShoe_RF | GFRP | 8.880 | 235.00 |
| MotorShoe_RR | GFRP | 8.880 | 555.00 |
| MotorShoe_LF | GFRP | 8.880 | 235.00 |
| MotorShoe_LR | GFRP | 8.880 | 555.00 |
| ArmSaddle_PosY_Spar | GFRP | 13.682 | 365.42 |
| ArmSaddle_PosY_Rear | GFRP | 8.436 | 410.00 |
| ArmSaddle_NegY_Spar | GFRP | 13.682 | 365.42 |
| ArmSaddle_NegY_Rear | GFRP | 8.436 | 410.00 |
| WingCenterBox | CFRP | 23.232 | 305.50 |
| WingCenterSideWeb__1 | GFRP | 12.728 | 320.00 |
| WingCenterSideWeb_1 | GFRP | 12.728 | 320.00 |
| WingRootCaps_PosY | CFRP | 22.062 | 329.88 |
| WingRootRib_PosY_44 | GFRP | 2.751 | 329.43 |
| WingRootRib_PosY_54 | GFRP | 3.925 | 329.25 |
| WingRootCaps_NegY | CFRP | 22.062 | 329.88 |
| WingRootRib_NegY_56 | GFRP | 3.925 | 329.25 |
| WingRootRib_NegY_46 | GFRP | 2.751 | 329.43 |
| WingFrame_280 | GFRP | 11.292 | 281.00 |
| WingFrame_326 | GFRP | 11.292 | 320.00 |
| WingLocalFoam_280 | Ravatherm XPS X H LB | 0.825 | 287.99 |
| WingLocalFoam_321 | Ravatherm XPS X H LB | 0.728 | 312.00 |
| PusherFirewall | GFRP | 7.695 | 1108.00 |
| PusherForwardFrame | GFRP | 4.748 | 1041.00 |
| PusherTie__20_0 | GFRP | 1.924 | 1074.50 |
| PusherTie_20_0 | GFRP | 1.924 | 1074.50 |
| PusherTie_0__20 | GFRP | 1.924 | 1074.50 |
| PusherTie_0_20 | GFRP | 1.924 | 1074.50 |
| TailRootLaminates_PosY | GFRP | 10.701 | 1022.58 |
| TailRootLaminates_NegY | GFRP | 10.701 | 1022.58 |
| TailFrameFront | GFRP | 4.745 | 970.00 |
| TailFrameRear | GFRP | 5.139 | 1021.00 |
| TailLocalFoam_969 | Ravatherm XPS X H LB | 0.406 | 974.77 |
| TailLocalFoam_1014 | Ravatherm XPS X H LB | 0.328 | 1018.46 |
| BatteryTray_Front | GFRP | 11.690 | 237.20 |
| BatteryCradle_Front_206 | GFRP | 4.580 | 208.20 |
| BatteryCradle_Front_261 | GFRP | 4.580 | 263.20 |
| BatteryTray_Rear | GFRP | 11.690 | 362.20 |
| BatteryCradle_Rear_331 | GFRP | 4.580 | 333.20 |
| BatteryCradle_Rear_386 | GFRP | 4.580 | 388.20 |

## CG and payload release

CAD structural CG: X=456.52, Y=0.32, Z=2.98 mm.
Provisional aircraft CG: X=397.56, Y=0.08, Z=-5.01 mm.
Battery stays at X299.70 mm. Inherited target would require X287.93 mm; fit and stability target are not verified.
Payload release shifts X CG by5.42 mm. This removes payload only; magnet and plate remain.
Installed component locations/allowance centroids remain estimates, so the aircraft CG is not final. Static margin is diagnostic against an inherited neutral point, not stability validation.

## Structural screens

| Case | Screen only | Deflection mm | Twist deg | Max utilization |
|---|---|---|---|---|
| Wing 3g | PASS | 25.63 | -1.47 | 0.746 |
| Wing -1.5g | PASS | -12.82 | -0.75 | 0.377 |
| Wing 3g at70% assumed stiffness | FAIL | 36.62 | -2.11 | 1.053 |
| V-tail at top speed | PASS | 4.31 | -0.11 | 0.352 |
| VTOL 40N total rating: both motors | PASS | 5.03 | 0.31 | 0.346 |
| VTOL 40N total rating: front only | PASS | 2.52 | -0.60 | 0.302 |
| VTOL 40N total rating: rear only | PASS | 2.52 | 0.92 | 0.459 |
| VTOL 69.2N total rating: both motors | PASS | 8.71 | 0.54 | 0.599 |
| VTOL 69.2N total rating: front only | PASS | 4.35 | -1.05 | 0.523 |
| VTOL 69.2N total rating: rear only | PASS | 4.35 | 1.59 | 0.794 |

Ideal wing positive-n screen boundary: 4.021225929260254; governing metric:core_shear_utilization_ultimate. This is not aircraft load-factor capability.

## VTOL arm overhang checks

| Total rating N | Front stress MPa | Rear stress MPa | Worst nominal FOS |
|---|---|---|---|
| 40.0 | 2.85 | 3.40 | 88.17 |
| 69.2 | 4.93 | 5.89 | 50.96 |
Proposed supports X356.4/X410mm and material properties remain assumptions; no clamp/bearing/crushing check.

## Payload mount and aft support loads

Payload plate bending stress:8.47 MPa; nominal FOS:32.57. Assumed simply-supported strip; fasteners, magnet pull-off and local fuselage support not verified.
Tail ultimate normal load per panel:15.11 N. Pusher design axial load:9.93 N.
UNRESOLVED: P04 pusher/tail geometry is provisional; load paths, shell transfer and joint strength require closure; no aft-spine stiffness credited

## Battery and thrust

6S2P: 21.6 V nominal / 25.2 V fully charged;13.0 Ah;280.8 Wh typical.
Pack budget uses12×74.5g maximum cell mass +50g provisional pack hardware unless inputs override it. This is a budgeting scenario, not measured pack weight.
26A cell rating uses90C surface cutoff; pack thermal/wiring limit unverified

| Total thrust N | T/W at sizing mass | Evidence |
|---|---|---|
| 40.0 | 1.098 | inherited baseline |
| 69.2 | 1.899 | unverified17.30N/motor scenario |

## Open work / limits

- P04 is a geometry and sizing study, not an accepted attachment design
- Local foam is now modeled; final shell doublers, insert geometry and interface closure remain open
- Wing root bonded center box is provisional; detachable joint not designed
- Motor bolt pattern/torque, pusher maximum thrust and strap ratings require selected hardware
- Landing/gust/fatigue/impact/water ingress cases unresolved
- Laminate, adhesive, foam and joint properties are assumptions
- Servo mounts, payload plate-to-fuselage connection and control linkage/hinges remain incomplete
- CAD material subtotal includes unresolved spar/shell overlaps; allocation not resolved.
- Left/right main wing skin mass differs0.542g despite symmetric inputs; volume/thickness audit outstanding.
- P04 localized foam is counted; complete hardpoint and shell qualification remains open.
- Root beam idealized at aircraft centerline; actual attachment flexibility and trimmed root geometry unresolved.
- Geometric CAD normal-offset skins and analytical section offsets differ; stiffness/stress are screening approximations.
- Motor/prop mass placeholders and6S operating data not verified for selected10x3 prop.
- ESCs are60x30x15mm reservations only; their actual mass remains inside old ESC/wiring allocation.
- No overall structural PASS. Native P04 reopen/geometry checks do not qualify joints.
- P04 fit audit reports 32 positive-volume intersections; candidate mass is gross, not net installed mass. See reports/p04/REVIEW.md.

## Geometry and material inputs

| Input | Current value / status |
|---|---|
| Fuselage OD / shell | 90.00 / 0.330 mm |
| Wing projected span / root / tip chord | 1400.0 / 165.0 / 100.0 mm |
| Wing / tail skins | 0.330 / 0.264 mm |
| Spar OD root / tip; wall root / tip | 14.00 / 8.00; 2.00 / 0.50 mm |
| Arm Y width / Z height / wall | 30.0 / 20.0 / 1.0 mm |
| GFRP E1 / E2 / G12 | 15 / 15 / 3 GPa; assumed laminate |
| Foam shear modulus / shear strength | 8 / 0.25 MPa; not qualified allowables |
| CFRP spar E / strength | 70 GPa / 300 MPa; assumed |
| Force screening factors | limit n=3.0; ultimate multiplier=1.5; wing force allowance=1.1 |

## Governing equations and interpretation

- Material mass: m = density × CAD solid volume. All CAD lengths converted from mm to m.
- Center of gravity: r_CG = sum(m_i × r_i) / sum(m_i). Battery held fixed; reserve has no assigned location.
- Inertia: I_total = sum(I_intrinsic + m × [(d dot d) identity - d outer d]). Nonstructural components treated as points.
- Wing screening force per side: F = sizing_mass × g × n × wing_force_allowance / 2. Elliptical span load; no inertial relief.
- Beam equilibrium: V(y) = integral(q ds) + point forces; M(y) = integral(q × lever ds) + point-force moments.
- Bending/shear deflection from integration of M/EI and V/kGA. Closed-section torsion from T/GJ. Material/connection assumptions limit physical accuracy.
- Arm overhang: M=F L; stress=M c/I; tip deflection=F L^3/(3 E I). Nominal FOS uses assumed bending strength.
- Payload plate: simply supported strip, central inertial force; M=F L/4; deflection=F L^3/(48 E I). Fasteners and magnet are separate unresolved checks.
- Tail panel limit force: 0.5 × air_density × V^2 × panel_area × assumed_CL. Pusher load is required thrust × design multiplier.
- Utilization above1 means the associated modeled criterion fails. PASS applies only to the listed screen, never the whole aircraft.
## P04 attachment demand and sizing screens
All dimensions/effective areas/strengths below are assumptions; see docs/ATTACHMENT_STUDY.md. Geometry connections, peel, fatigue and tests remain open.
| Check | Demand | Capacity assumption | Units | Status |
|---|---|---|---|---|
| Lift motor shoe strip bending | 17.300 | 70.000 | MPa | PRELIMINARY SCREEN ONLY |
| Arm saddle average bond shear | 0.200 | 2.000 | MPa | PRELIMINARY SCREEN ONLY |
| Wing root cap axial stress | 107.161 | 210.000 | MPa | PRELIMINARY SCREEN ONLY |
| Wing root transfer bond shear | 1.340 | 2.000 | MPa | PRELIMINARY SCREEN ONLY |
| Battery retention per strap | 41.659 | 100.000 | N | PRELIMINARY SCREEN ONLY |
| Tail root couple force | 329.091 | not established | N | PRELIMINARY SCREEN ONLY |
| Pusher axial demand | 9.930 | not established | N | PRELIMINARY SCREEN ONLY |
## CAD fit acceptance gate
Audit matches snapshot: True. Positive-volume intersections: 32. This is a gross candidate budget, not a net installed or finished structural mass. See reports/p04/REVIEW.md for fit findings.