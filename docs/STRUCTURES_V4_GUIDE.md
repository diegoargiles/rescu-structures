# P04 study branch update

This branch defaults to inputs.json and data/cad_snapshot_p04.json. Read ATTACHMENT_STUDY.md and reports/p04/REVIEW.md for candidate construction, revised mass, checks and open interfaces. The P03 snapshot and reports/baseline remain preserved. CAD outputs belong to a separate P04 study; they are not a fabrication release. Run verify_v4.py and verify_attachments.py.

The material below documents the preserved P03 method and historical mass checkpoint; its unfinished-attachment descriptions are superseded only to the extent recorded in the P04 review.

# RescU Structures V4 — current analysis entry point

Use **RescU_Structures_V4.py** for this P03 baseline. Earlier V2/V3 versions are preserved; V2 and the older V3 are preserved in archive/v2_v3/.

## Run

1. Clone or pull this repository.
2. Open the folder in VS Code.
3. Run `python RescU_Structures_V4.py` (or `py RescU_Structures_V4.py` on Windows).
4. Open `results/REPORT.html` in a browser. The terminal gives a short summary.

Python3.10+; **no third-party packages needed** for normal runs. Keep engine/, data/ and inputs.json together. Do not run the archived engine files directly.

## What's included

- Current P03 geometry input snapshot, actual saved CAD solid volumes, centroids and intrinsic inertias, re-extracted with OpenCascade. Hidden untrimmed source shapes are excluded. The large CAD assembly is not duplicated in this code package; its filename and SHA-256 are recorded.
- Material mass by part and material; explicit modeled vs allowed vs missing structure.
- Fixed battery position; provisional aircraft CG, structural CG, diagnostic static margin, required battery station for the inherited target, and payload-release CG change. No automatic battery relocation.
- Approximate full-aircraft inertia: exact CAD structural intrinsic tensor + parallel-axis terms; other components/allowances as points. This is not an actual installed-aircraft inertia measurement.
- Positive3g, negative1.5g,70%-stiffness sensitivity, V-tail load, symmetric VTOL and front/rear motor-only wing cases at40N and69.2N total rated thrust scenarios.69.2N is not a verified operating point.
- Skin maximum-stress, core shear, spar bending, deflection and twist screening; arm overhang bending, provisional payload plate bending, tail and pusher design loads.
- Numerically bracketed ideal wing beam positive-n screening boundary. **Not an allowable aircraft load factor.** Local joints, buckling, wrinkling, fatigue and mission loads can govern first.
- Clean browser report, Markdown summary, JSON results and CSV ledgers. FAIL rows highlighted. Read the report's limits alongside the results.

## Mass conventions

`material mass [kg] = CAD solid volume [mm³] × 1e-9 × density [kg/m³]`.

Main wing and tail skins/core/bond are trimmed at the fuselage outer surface. Foam core BREP already excludes the spar/bond envelope; no second cavity deduction. Fuselage currently has only GFRP shell: localized XPS and detailed hardpoints remain undesigned, so their required mass is unknown. The615.931g result is modeled material only, not finished structures.

Previous allowances remain separate: local hardware71.683g, wing bond/finish41.425g, tail bond/finish7.383g. The modeled spar epoxy5.473g is already in the CAD total; the old allowances described other core-seal/finish and local hardware. They are budgeting assumptions, not demonstrated quantities; replace them as joints/manufacturing are detailed.200g unallocated reserve is added to sizing mass, not structural mass or CG.

Battery now defaults to12×74.5g maximum M65A cell mass +50g **assumed** pack hardware =944g. This is an explicit conservative cell-weight budget, not a confirmed pack mass. Set battery.measured_complete_pack_mass_kg to a measured total to override; do not add leads/retention twice. Existing900g assumption can be explored as an override but leaves only6g above maximum cell weight. Current cell/gauge positions remain unchanged.

Two21.9g tail servos use proposed P03 positions.136.2g from the earlier180g aggregate servo budget remains visibly unresolved.150g ESC/wiring and motor/prop placeholders remain estimates; exact AIR40A masses have not been substituted or double-counted. The10×3 choice is geometric/provisional, not propulsion validation.

## Inputs and changes

Edit **inputs.json** for densities, material property assumptions, battery hardware/measurement, component masses/positions, additional structural parts, allowances, loads and reserve. Every additional structural part needs name, mass_kg, x_m, y_m, z_m and source. Densities drive CAD volume mass calculations; geometry does not silently change when densities change.

Edit geometry in FreeCAD, save it, then run **tools/Export_Current_CAD.FCMacro** and select the repository root folder. This updates data/cad_snapshot.json (and backs up the prior snapshot), including native shape volumes/centroids/inertias. New structural solids must have StructuralPart=True, Material and Density_kg_m3. Never tag hidden source wing/tail shapes, gauges, or outer-mold-line tools as physical structure. Add new material densities to inputs.json. Existing raw source internal names are retained.

The supplied snapshot's BREP integrals were computed in OpenCascade; the export macro is supplied for the user's FreeCAD environment and has not been executed here. Native P03 reopening/recompute remains untested. The macro exports the live document; save first so the recorded saved-file hash corresponds to it.

Geometry-driven mass and analytical stiffness are different fidelity levels. Changing tube/skin geometry is reflected in analytical sections via exported parameters, but gross centerline cantilever support and closed intact skin assumptions remain. Current beam root is symmetry plane, not actual wing/fuselage attachment. Nonzero incidence is explicitly rejected rather than silently analyzed in the wrong frame.

## Main remaining work

- Verify CAD skins' normal thickness/volume and small left/right skin mass asymmetry. Underlying full-span analytical shell mass and CAD skin volume differ; CAD integral is authoritative for as-modeled material, not proof of actual manufactured thickness.
- Design/size wing center connection, attachment laminates, local fuselage XPS/hardpoints, arm attachments, tail/pusher supports, servo mounts, payload retention and battery retention.
- Replace assumed laminate modulus/strength and foam directional properties with suitable data. These are not certified aircraft allowables.
- Establish actual motor/KV/prop/voltage thrust-current operating points, full power budget, complete installed masses and CG positions.
- Gust, landing, asymmetric control, fatigue, vibration, skin buckling/wrinkling, bond peel, thermal and water exposure are open. Fuselage pressure/buckling and hardpoint checks are not reported as passed.
- Servo torque and magnet retention require actual hinge moments/linkage geometry and magnet holding-force/installation data; no invented FOS.

## Validation

Run `python verify_v4.py`. It checks mass conservation, volume/density units, CG moment conservation, payload release, battery sensitivity, intrinsic/parallel-axis inertia and the cantilever solver against a closed-form point-load solution. The delivered validation.json also records160/320-station convergence of screening results. Mesh convergence validates numerical stability only, not physical assumptions.

## Source references

- P03 native CAD and its saved BREP members, identified in data/cad_snapshot.json.
- Current V3 Ravatherm beam/laminate and V2 component-screen equations carried into engine/; their material properties and model limits remain assumptions.
- Molicel M65A datasheet v0.1,2025-08-05: https://www.molicel.com/cn/wp-content/uploads/Product-Data-Sheet-of-INR-21700-M65A-80153-0.1_250805.pdf
- Hitec HS-5085MG: https://www.hitecrcd.co.kr/products/hs-5085mg/
- T-Motor AIR40A product identity: https://store.tmotor.com/product/air-40a-6s-esc.html

