# RescU Structures V4 — current CAD P03 baseline

UNRESOLVED — preliminary mass budget and structural screening

## Mass summary

| Quantity | Value |
|---|---|
| Modeled structural material | 615.931 g |
| Retained structural allowances | 120.491 g |
| Added user structural parts | 0.000 g |
| Structural budget (incomplete) | 736.422 g |
| Accounted aircraft estimate | 3.2536 kg |
| Sizing aircraft mass | 3.4536 kg |
| Unallocated sizing reserve | 200.0 g |
| Battery pack budget (assumed) | 944.0 g |

CAD material quantities use m=rho×V; hidden untrimmed wing/tail sources and prop/ESC gauges are excluded. No second spar-foam subtraction. Reserve is separate from component mass and has no assigned CG.

## Modeled materials

| Material | Mass g |
|---|---|
| GFRP | 363.835 |
| Ravatherm XPS X H LB | 39.950 |
| Epoxy | 5.473 |
| CFRP | 198.573 |
| Aluminum 6061-T6 | 8.100 |

Wing/tail cores contain the represented XPS. Localized fuselage foam has not been designed or counted.

## CAD structural components

| Part | Material | Mass g | Centroid X mm |
|---|---|---|---|
| Fuselage_GFRP_Shell_0330 | GFRP | 162.873 | 528.92 |
| Wing_PosY_GFRP_Skin_Exposed | GFRP | 87.803 | 401.85 |
| Wing_PosY_Ravatherm_Core_Exposed | Ravatherm XPS X H LB | 18.170 | 379.34 |
| Wing_PosY_EpoxyBond_Exposed | Epoxy | 2.736 | 368.72 |
| VTail_PosY_GFRP_Skin_Exposed | GFRP | 12.948 | 1055.47 |
| VTail_PosY_Ravatherm_Core_Exposed | Ravatherm XPS X H LB | 1.805 | 1044.29 |
| Wing_NegY_GFRP_Skin_Exposed | GFRP | 87.261 | 401.80 |
| Wing_NegY_Ravatherm_Core_Exposed | Ravatherm XPS X H LB | 18.170 | 379.33 |
| Wing_NegY_EpoxyBond_Exposed | Epoxy | 2.736 | 368.72 |
| VTail_NegY_GFRP_Skin_Exposed | GFRP | 12.949 | 1055.47 |
| VTail_NegY_Ravatherm_Core_Exposed | Ravatherm XPS X H LB | 1.805 | 1044.29 |
| Wing_PosY_CFRP_TaperedSpar | CFRP | 45.527 | 353.80 |
| VTOL_Arm_PosY | CFRP | 53.760 | 395.00 |
| Wing_NegY_CFRP_TaperedSpar | CFRP | 45.527 | 353.80 |
| VTOL_Arm_NegY | CFRP | 53.760 | 395.00 |
| Payload_MountPlate_PROVISIONAL | Aluminum 6061-T6 | 8.100 | 350.00 |

## CG and payload release

CAD structural CG: X=456.09, Y=0.48, Z=5.49 mm.
Provisional aircraft CG: X=392.99, Y=0.09, Z=-5.22 mm.
Battery stays at X299.70 mm. Inherited target would require X304.57 mm; fit and stability target are not verified.
Payload release shifts X CG by5.35 mm. This removes payload only; magnet and plate remain.
Installed component locations/allowance centroids remain estimates, so the aircraft CG is not final. Static margin is diagnostic against an inherited neutral point, not stability validation.

## Structural screens

| Case | Screen only | Deflection mm | Twist deg | Max utilization |
|---|---|---|---|---|
| Wing 3g | PASS | 23.82 | -1.44 | 0.720 |
| Wing -1.5g | PASS | -11.91 | -0.77 | 0.385 |
| Wing 3g at70% assumed stiffness | FAIL | 34.03 | -2.06 | 1.029 |
| V-tail at top speed | PASS | 4.31 | -0.11 | 0.352 |
| VTOL 40N total rating: both motors | PASS | 5.03 | 0.31 | 0.346 |
| VTOL 40N total rating: front only | PASS | 2.52 | -0.60 | 0.302 |
| VTOL 40N total rating: rear only | PASS | 2.52 | 0.92 | 0.459 |
| VTOL 69.2N total rating: both motors | PASS | 8.71 | 0.54 | 0.599 |
| VTOL 69.2N total rating: front only | PASS | 4.35 | -1.05 | 0.523 |
| VTOL 69.2N total rating: rear only | PASS | 4.35 | 1.59 | 0.794 |

Ideal wing positive-n screen boundary: 4.32698917388916; governing metric:core_shear_utilization_ultimate. This is not aircraft load-factor capability.

## VTOL arm overhang checks

| Total rating N | Front stress MPa | Rear stress MPa | Worst nominal FOS |
|---|---|---|---|
| 40.0 | 1.83 | 2.51 | 119.48 |
| 69.2 | 3.17 | 4.34 | 69.06 |
Supports X313/X448mm and material properties remain assumptions; no clamp/bearing/crushing check.

## Payload mount and aft support loads

Payload plate bending stress:8.47 MPa; nominal FOS:32.57. Assumed simply-supported strip; fasteners, magnet pull-off and local fuselage support not verified.
Tail ultimate normal load per panel:15.11 N. Pusher design axial load:9.93 N.
UNRESOLVED: no actual pusher/tail support or aft-spine geometry represented; loads only, no invented FOS

## Battery and thrust

6S2P: 21.6 V nominal / 25.2 V fully charged;13.0 Ah;280.8 Wh typical.
Pack budget uses12×74.5g maximum cell mass +50g provisional pack hardware unless inputs override it. This is a budgeting scenario, not measured pack weight.
26A cell rating uses90C surface cutoff; pack thermal/wiring limit unverified

| Total thrust N | T/W at sizing mass | Evidence |
|---|---|---|
| 40.0 | 1.181 | inherited baseline |
| 69.2 | 2.043 | unverified17.30N/motor scenario |

## Open work / limits

- Localized fuselage XPS volume and attachment laminates unknown
- Spar center joint and wing/arm/tail/pusher hardpoints unfinished
- Landing/gust/fatigue/impact/water ingress cases unresolved
- Laminate material data and foam orientation not validated
- Control surface hinge geometry and servo torque load cases missing
- CAD material subtotal includes unresolved spar/shell overlaps; allocation not resolved.
- Left/right main wing skin mass differs0.542g despite symmetric inputs; volume/thickness audit outstanding.
- No localized fuselage XPS represented:0g counted, required quantity unknown; this is not a zero-mass requirement.
- Root beam idealized at aircraft centerline; actual attachment flexibility and trimmed root geometry unresolved.
- Geometric CAD normal-offset skins and analytical section offsets differ; stiffness/stress are screening approximations.
- Motor/prop mass placeholders and6S operating data not verified for selected10x3 prop.
- ESCs are60x30x15mm reservations only; their actual mass remains inside old ESC/wiring allocation.
- No overall structural PASS; no native FreeCAD application reopen verification.

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