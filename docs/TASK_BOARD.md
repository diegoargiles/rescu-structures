# Development task board

Status refers to R13/R14 development and its stated scope, not the entire aircraft. Latest checkpoint: November 17, 2026 (R15/R16, landing station and R16.1/R16.2 rows at the end).

| ID | Task | Owner / inputs | Acceptance evidence | State |
|---|---|---|---|---|
| BASE-01 | Preserve R12 and identify versions | Structures | SHA256 match and source unchanged | DONE |
| LOAD-01 | Audit existing calculations | Structures | Trace old load factors/twist assumptions and configuration mismatch | DONE |
| LOAD-02 | Approve load envelope and criteria | Structures + faculty, Aero, Controls, Performance | Reviewed cases with sources and limits | OPEN |
| PROP-01 | Resolve motor supply and final prop/thrust/RPM/torque | Propulsion | Matched component/voltage data | OPEN |
| CAD-01 | Longer round booms and lower motors | Structures/Geometry | Candidate plus full disk clearance and joint checks | CANDIDATE |
| CAD-02 | Extended aft reinforcement | Structures | Reaches beyond third outboard rib; defined bonds and twist comparison | CANDIDATE |
| CAD-03 | Bonded composite motor/wing sockets | Structures | Separate geometry, bolt access, bond/bearing qualification | CANDIDATE |
| CAD-04 | Internal ESC installation | Propulsion/Geometry/Structures | Envelope fit, thermal/retention/wiring/access | CANDIDATE |
| CAD-05 | Complete main carry-through bonded interfaces | Structures | Defined overlap, bondline, shell reinforcement and retention | OPEN |
| FEA-01 | Confirm SolidWorks Simulation capability and import strategy | Geometry/Structures | Installed add-in, materials/contact capability and named bodies | OPEN |
| FEA-02 | R12 vs R13 wing/arm/carry-through | Structures | Equilibrium, mesh comparison, displacement/twist and joint demands | OPEN |
| MASS-01 | Reconcile aircraft mass and CG | Weights/Performance + all leads | Current measured/vendor parts and installation allowances | OPEN |
| MFG-01 | Select stock, layups, adhesive and tooling | Structures + faculty | Reproducible manufacturing instructions and allowables | OPEN |
| TEST-01 | Representative bond/arm/wing test plan | Structures + faculty | Predeclared loads, fixtures, measurements and acceptance | OPEN |
| LOAD-03 | Attachment force/torque and nominal bearing screens | Structures | Equilibrium checked, 17.3/26 N cases and limits documented | SCREEN COMPLETE |
| CAD-06 | R14 wing-socket overlap 20 to 32 mm | Structures | Four valid changed solids, 20 targeted pairs clear, +8.68 g before adhesive | FIT CANDIDATE |
| MASS-02 | Own equipment placement register | Structures + all leads | 250 geometry features extracted; 29 equipment entries; unknowns explicit | REGISTER COMPLETE; CG OPEN |
| MFG-02 | Supplier-backed material/bond candidates | Structures | Matching tube and vacuum-bag laminate/adhesive trial plan | CANDIDATES DOCUMENTED |
| CAD-07 | R15 full-aircraft CAD rebuilt (CadQuery) | Structures | 489 pairs checked; mass/CG and wing screen | DONE |
| CAD-08 | R16 wing-root elbow joints (no tube trimmed by skin) | Structures | 0.000 mm³ tube/skin intersection; changed-part interference clean | GEOMETRY CANDIDATE |
| CAD-09 | Remove TPU landing feet; landing gear trade | Structures | Tripod gear studied (+54.5 g, SM −0.2 %) and dropped | DONE |
| GSE-01 | Landing station design + manufacturing plan | Structures | Fit-checked vs R16; 135 mm prop clearance; plan in manufacturing/ | DESIGNED |
| GSE-02 | Build and inspect landing station | Structures | 12-point inspection in the manufacturing plan; drop test | OPEN |
| GNC-01 | Precision landing system (±40 mm, ±3.8°) | Controls/Avionics | RTK or beacon selected and demonstrated | OPEN |
| STR-01 | R16 root elbow spar spigot strength | Structures | Solid rod or longer spigot; FEA/test | OPEN |
| MASS-03 | Move battery to x ≈ 256 mm for target CG | Structures + Electrical | Updated CG at target | OPEN |
| CAD-10 | R16.1 smooth nose (exact ellipse, shape unchanged) | Structures | Zero boolean difference aft of x 200.5; tip sag filled | DONE |
| CAD-11 | R16.1 Tarot 4008 pusher + APC 10x3 / 13x8P props in the assembly | Structures | Swept-disk clearances ≥ 11 mm; rotation hands per Quad-X | DONE |
| CAD-12 | R16.2 pusher mount: plate holes on Tarot Ø19 circle, 4× M3 × 4 SHCS, collar bore Ø26, wire-tab notch | Structures | 0 overlaps; screw heads 0.75 mm from collar | GEOMETRY CANDIDATE |
| CAD-13 | R16.2 UM2807 shaft thread +4 mm (model) and bullet prop nuts | Structures | Nut bore clears shaft tip 0.7 mm | DONE (visual) |
| PROP-02 | Confirm real UM2807 shaft length vs 10x3 hub + nut | Propulsion | Measured shaft; nut/spacer chosen | OPEN |
| PROP-03 | Select a real 1/4 in prop adapter for the Tarot 4008 rotor | Propulsion | Part number; replaces REF adapter | OPEN |
| MFG-03 | Plate-to-collar adhesive and pusher wire routing | Structures + Electrical | Adhesive/prep chosen; route through the shell notch to the ESCs | OPEN |
| MASS-04 | Regenerate cg.json with real motor/prop masses | Structures | Updated cg.json | OPEN |

Priority: review candidate geometry with Diego; obtain PROP-01 and mass/control/aero inputs; close CAD-02/03/05 load paths; run FEA-02. No need to wait for all data before layout iteration, but no strength PASS without supported inputs.
