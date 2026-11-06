# Development task board

Status refers to R13/R14 development and its stated scope, not the entire aircraft. Latest checkpoint: November 5, 2026.

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

Priority: review candidate geometry with Diego; obtain PROP-01 and mass/control/aero inputs; close CAD-02/03/05 load paths; run FEA-02. No need to wait for all data before layout iteration, but no strength PASS without supported inputs.
