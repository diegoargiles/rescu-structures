# RescU — attachment loads, R14 socket study and component layout

Prepared November 5, 2026. R13 remains the baseline; R14 is a separate socket-overlap candidate. This package contains engineering demand calculations and fit evidence, not a strength or flight release.

## What changed and what was verified

- Extracted all 250 PartDesign features into `cad_component_locations.csv`: volume, geometric centroid and bounding box in millimetres. Only leaf physical features should be counted for mass; reference disks, equipment envelopes and nested cell/module reservations are not structural material.
- Created `equipment_mass_location_register.csv` with 29 equipment/accounting entries. It distinguishes vendor/team masses, unknowns, CAD positions and proposed positions. Geometric centroid is a placement proxy; actual internal mass distribution and cable routes can move the component CG.
- Checked the right-wing connection interfaces including the intermediate main-spar sleeve and aft collar. The intended sequence is motor/pod → boom → bonded socket → rib bolt → motor rib → bonded main-spar sleeve and aft collar → spars/root adapters → fuselage carry-through. The split between these paths requires a stiffness model; it is not assumed 50/50.
- Main spar-to-sleeve, sleeve-to-rib, aft tube-to-collar and collar-to-rib minimum gaps are approximately 0.15 mm. These are nominal adhesive provisions, not evidence of bond coverage or bond strength. Socket-to-rib clearance is also 0.15 mm, but this is a bolted interface, not an instruction to glue the removable clevis.
- Created full native `RescU_R14_Socket_Overlap_Study.FCStd` and a STEP containing the four revised sockets. Only sleeve overlap changes from 20 to 32 mm; ear and bolt geometry is preserved. All four revised solids are valid; 20 bounding-box candidate pairs against the physical assembly have no overlap above 0.01 mm³. Full loaded clearance and manufacturing/tool access remain open.

## Assumptions and given geometry

Axes: X longitudinal, Y spanwise, Z vertical. Units below are N and mm unless stated. One boom has front motor at X=170, rear at 600, supports A=335 and B=405. Support separation is 70 mm. Boom OD/ID =25/23 mm. Rib bolts are modeled as nominal M3; nominal rib thickness is 2 mm; each clevis ear is 2.35 mm thick. Effective local dimensions, hole quality and bolt thread position require a manufacturing drawing. The broad rib bounding box is not its local bearing thickness.

The existing 17.3 N/motor remains the continuity case. A new 26 N/motor and ±0.45 N·m torque sensitivity case is added separately; it is not a proven maximum for the selected propeller/supply. No aircraft mass is assumed in these local thrust-only free bodies. Wing flexibility, motor/boom inertia, gyroscopic loads, vibration, landing loads and aerodynamic loading are not included.

## Attachment-load calculations

Take upward motor thrust as positive. R_A and R_B below are the forces transmitted **to the wing**; forces on the boom at the supports are their negatives.

R_B = [T_f(170−335) + T_r(600−335)] / (405−335)

R_A = T_f + T_r − R_B

For rear-only at 17.3 N:

R_B = 17.3(265)/70 = 65.493 N; R_A =17.3−65.493=−48.193 N.

For rear-only at the 26 N sensitivity point:

R_B =26(265)/70=98.429 N; R_A=26−98.429=−72.429 N.

| Case | A at 17.3 N max | B at 17.3 N max | A at 26 N max | B at 26 N max |
|---|---:|---:|---:|---:|
| Both full | 9.886 | 24.714 | 14.857 | 37.143 |
| Front only | 58.079 | −40.779 | 87.286 | −61.286 |
| Rear only | −48.193 | 65.493 | −72.429 | 98.429 |

The script also evaluates both full/half differential cases. Force and moment equilibrium assertions pass. Opposite-signed reactions explain why one attachment force exceeds a motor's thrust. These are local demand cases, not assertions that the aircraft can sustain motor-out flight.

With the inherited provisional ultimate multiplier 1.5 applied once:

F_u =1.5(98.429)=147.643 N.

| Idealized demand | Calculation | Result |
|---|---|---:|
| M3 bolt, equal double shear | F_u / [2π(3²)/4] | 10.44 MPa |
| Nominal 2 mm motor-rib bearing | F_u / (3×2) | 24.61 MPa |
| Two nominal 2.35 mm ear bearings | F_u / (2×3×2.35) | 10.47 MPa |
| Ear net-section tension, width14, hole3.2 | F_u / [2(14−3.2)2.35] | 2.91 MPa |
| Ear top shear-out average, center-to-edge4.8 | F_u / [4×2.35×(4.8−1.6)] | 4.91 MPa |

These values are **required stress capacity**, not safety margins. They assume equal ear sharing and full nominal shank section, ignore contact concentration/bolt bending/preload, and are not composite failure predictions. Rib shear-out and pull-through remain unsized. Check bolt threads, locking, galvanic isolation, ear bending, laminate bearing/bypass and representative coupons before acceptance.

## Torque: correct axis and demand

Motor reaction torque is about Z. It produces boom bending in the horizontal plane. With no other lateral forces and ideal two-point supports, the support-force couple is |R_y|=|Q_f+Q_r|/0.070. For same-sign 0.45 N·m at both motors, |R_y|=0.90/0.070=12.86 N (19.29 N after the provisional 1.5 multiplier). This acts along the Y-oriented rib bolt and requires axial retention and ear/pull-through assessment in addition to vertical shear.

Equal opposite torque signs cancel the net support couple in this idealization; they do not remove internal boom/pod loads. The independent 26 N and 0.45 N·m extrema form a sensitivity envelope, not a matched operating point. A simple 19 mm motor-bolt couple gives 0.45/0.019=23.68 N at each side of the couple; actual four-bolt distribution needs a bolt-group model. Shaft torque Q=P_shaft/ω, ω=2πRPM/60. Electrical VI is not shaft power.

## Proposed R14 CAD trade

For overlap L and boom D=25 mm, A_bond=πDL. R13 has 1,570.8 mm²; R14 has 2,513.3 mm², a 60% increase. At the same force, nominal force/area decreases 37.5%.

The vertical force is transverse to a cylindrical socket. F/(πDL) is only a mean surface-traction scale, **not a pure adhesive shear solution**. F/(DL) is a projected bearing-pressure scale: at ultimate demand it falls from0.2953 to0.1846 MPa. Edge peel, local normal stress, ovalization and flexible-adherend effects remain uncalculated. Increasing overlap need not increase actual strength proportionally.

Four sleeves add 8.680 g at assumed cured density1600 kg/m³. Filling only the incremental 0.15 mm radial gaps adds about0.683 g at assumed adhesive density1200 kg/m³, before fillets and waste. Combined incremental estimate ≈9.36 g. The native CAD delta excludes adhesive. Compared with the earlier modeled R13 changed-part saving of52.8 g, the socket change retains approximately44.1 g of that geometric saving before adhesive/other exclusions. This is not a whole-aircraft mass update.

Choose32 mm as a fit-tested trade point with substantial added area and a small mass cost, not an optimized final dimension. It leaves38 mm between sleeves and preserves motor/prop positions, bolt spacing and the existing clevis. It does not reduce reactions or rib bearing demands. A larger bolt or thicker ear is not yet justified without material allowables; thickening ears would also require checking grip length and nut seating.

## Missing values: what we can estimate responsibly

| Input | Current approach | Confidence / remaining need |
|---|---|---|
| Component X/Y/Z | Extract CAD; place unmodeled equipment in a register | High for geometry; real component CG needs mass distribution/measurement |
| Motor and bare-cell mass | Vendor values × quantity | Useful starting basis; cables and pack hardware need separate accounting |
| Max thrust / torque | 17.3 N continuity; 26 N / 0.45 N·m sensitivity | Proxy envelope from motor-maker tests with different props; not matched performance |
| Hover thrust split | Compute from mass, CG and front/rear motor stations | Deterministic once inventory is complete; include rotor download later |
| Maneuver load factor | n=1/cos(bank) in coordinated level turn | 45° gives1.414;60° gives2.0; excludes gust/pull-up/landing |
| Positive/negative envelope | Keep inherited +3/−1.5 as comparison only | Team operating limits and aero/gust inputs required |
| Tube bending stiffness | Existing40/70 GPa sensitivity | Supplier layup and coupon/beam-test stiffness needed |
| Joint/laminate strength | Calculate required bearing/shear/peel demand | Cannot accurately invent process-dependent allowables |
| Twist / deflection acceptance | Derive from clearance and aero/control sensitivity | Existing2° and5% half-span are unapproved screens |
| Ultimate factor | Retain provisional1.5 once | Faculty/team acceptance required; not material uncertainty compensation |

T-Motor's KV1200/APC10×5.5 test gives2169 g thrust (21.27 N),0.355 N·m at38.94 A; its full-throttle point gives2616 g (25.65 N),0.436 N·m at54.64 A. This motivates rounded26 N/0.45 N·m for a structural sensitivity study. It does not authorize that operating point with a40 A ESC, a different propeller or the6S battery. The selected motor is rated3–4S; Propulsion must resolve the supply architecture. Motor mass is108 g including cable. Source: https://store.tmotor.com/product/at2814-long-shaft-fixed-wing-motor.html

For the exact APC propeller variant, manufacturer performance coefficients can support T=C_T ρ n²D⁴ and Q=C_P ρ n²D⁵/(2π), where n=RPM/60. Match variant, RPM, advance ratio and voltage-dependent motor operating point first; prop diameter and pitch alone do not uniquely specify the coefficients. Source: https://www.apcprop.com/technical-information/performance-data/

## We now own component placement

Retain modeled battery-module centers at(237.5,0,1.25) and(362.5,0,1.25) mm, motors atX170/600,Y±265, geometric Z≈4.50 mm, and lift ESC centers atX465/535,Y±15,Z−9.85 mm. These are candidate layout positions, not proof of actual component CG or thermal suitability.

Propose controller/carrier near(152.5,0,10) above the existing deck; receiver near(175,0,10); camera/AI near(60,0,0); flotation payload near(350,0,−55). Their fit, lens field, antennas, service access and retention remain open. These proposed electronics positions are recorded only; no fictitious component solids were added. Keep the pusher ESC and distributed wiring unplaced until envelopes and routes are available.

Compute r_CG=Σ(m_i r_i)/Σm_i. For a desired X_CG, required battery position is x_b=[M X_CG−Σ_other(m_i x_i)]/m_b. Existing fixed trays provide no assumed trim travel: solve feasibility first, then change hardware if needed. For ideal level hover, total front-pair thrust=W(600−X_CG)/430 and rear-pair thrust=W(X_CG−170)/430, with X in mm. Check payload-present and payload-released CG. The acceptable target range belongs to aerodynamic stability/control analysis; we should not choose it just to fit the battery.

`cg_from_register.py` refuses to output aircraft CG while mass or location entries are blank. A 0.95 kg battery moved10 mm would shift a hypothetical3 kg aircraft CG by3.17 mm; this illustrates sensitivity only, not current aircraft mass. We will prioritize weighing the battery, verifying camera/AI mass, and reconciling structural materials before tuning placement.

## Next work and remaining gates

Completed now: load path mapping, thrust reaction calculations, torque sensitivity, nominal bolt/rib/ear demand, overlap trade, separate CAD candidate, targeted fit checks and component-location inventory. Still open: bond stress/peel model, full rib load distribution, laminate allowables, current aircraft mass/CG, aero twist limits, FEA and physical tests. Do not interpret progress as a percent of flight readiness.

For FEA, model tube/sleeve/rib compliance and explicit bonded interfaces; constrain the root through its actual carry-through stiffness rather than fixing the motor rib. Compare reactions and displacement with beam calculations; verify mesh convergence before local contact/bearing interpretation. Test a representative tube/socket/rib joint in both reaction directions with the actual layup and adhesive. A test load must be chosen after defining limit/ultimate basis and fixture/load path; this study is not an instruction to load a flight article.

NASA guidance treats adhesive peak shear, peel, environment and cyclic loading separately: https://ntrs.nasa.gov/citations/19890016677

Open `Attachment_Annotated.png` for the free body and socket section. Open the native R14 file in FreeCAD for the full assembly, or import the four-socket STEP into SolidWorks as a parts-only study. Scripts require FreeCAD Python for CAD extraction/build, ordinary Python for calculations/CG, and Matplotlib for the drawing. The R13 native SHA is recorded in the interface and R14 study results; the source was not overwritten.
