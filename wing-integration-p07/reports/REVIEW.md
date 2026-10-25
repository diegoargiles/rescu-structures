# P07 wing-arm integration review

**Preliminary CAD candidate. Joint strength, fatigue and the final laminate/process remain unqualified.**

**Critical open sizing result:** the spar-to-rib radial edge-transfer case demands 12.255 MPa versus the inherited assumed 2 MPa screen. It fails that conservative case. A larger developed face flange/molded connection or another substantiated load path is required before release. The favorable skin-cap end case does not establish actual sharing.

## What is modeled

Both wing halves retain their own native surfaces and tapered spars. New skin cap strips, web-face tapes, open fore/aft spar cheeks, collar doublers, lower-skin slot reinforcement, edge potting and explicit adhesive layers connect the existing carrier into the local wing structure. The original local ribs become separate forward/aft web segments after the spar and flange reliefs.

The outer wing profile and spar geometry come from saved CAD. New laminate thicknesses, widths and bond dimensions are design assumptions. The foam has explicit web bays and cap/coupler channels. It is not credited as the primary motor attachment. The outer wing skins and original thin wing bond quantity retain their previous mass budget; no cutout credit is taken.

## Current mass

- P06 structural budget: 1157.673 g.
- P07 structural budget: 1171.807 g.
- Change: +14.135 g.
- Accounted aircraft: 3.647035 kg.
- Sizing aircraft including the separate reserve: 3.847035 kg.
- Reserve: 200.0 g, unchanged and counted once.
- Net explicit epoxy reallocated from the prior adhesive allowance: 5.668 g.

New material additions: Epoxy 5.874 g, GFRP 23.907 g.
Removed/replaced material: GFRP 9.151 g, Epoxy 0.206 g, XPS 0.621 g.

Modified parts and cores replace prior rows once. Exported skins, spars and original wing bond layers are retained quantities rather than additional mass. The earlier generic hardware and embedded motor-mount allowances remain removed. Cured laminate density includes its matrix resin; adhesive is separately modeled only at joints.

## Geometry and interchange checks

- 448 separate modeled material solids (including adhesive volumes; not 448 manufactured stock pieces) in the placed wing-arm pair.
- Hard-part interference findings: 0.
- Both native arm/wing assemblies solve; deliberately displaced/rotated rib datums recover to the constrained position.
- STEP exports are reopened and checked for valid solids, component counts and placed component quantities. They do not contain SolidWorks mates.

- `RescU_P07_Wing_Arm_Pair.step`: 448 valid solids; all quantity checks pass: False.
- `RescU_P07_SolidWorks_Review.step`: 260 valid solids; all quantity checks pass: False.
- `RescU_P07_PosY_Wing_Arm.step`: 224 valid solids; all quantity checks pass: False.
- `RescU_P07_PosY_Carrier_Cutaway.step`: 216 valid solids; all quantity checks pass: True.
- `RescU_P07_NegY_Wing_Arm.step`: 224 valid solids; all quantity checks pass: False.
- `RescU_P07_NegY_Carrier_Cutaway.step`: 216 valid solids; all quantity checks pass: True.

Thin-shell reference quantities show STEP/native deviations. Those files retain the affected reference geometry for viewing, not accepted mass properties. Native budgeting remains authoritative; use the carrier and individual-part exports for the checked hardware interfaces. See step_validation.json for every component.

## Updated joint demand screens

- Revised P06 splice average-shear utilization against the assumed 2 MPa screen: 0.975.
- Revised plate-strip utilization against the assumed 70 MPa screen: 0.831.
- All these assumed splice screens below one: True.
- PosY spar cheek: mean developed bond area 438.8 mm² per cheek; CAD cheek centroid separation 12.324 mm; full local torsion scenario 5.154 Nm; average shear demand 1.965 MPa with 50% effective area.
- NegY spar cheek: mean developed bond area 438.8 mm² per cheek; CAD cheek centroid separation 12.324 mm; full local torsion scenario 5.154 Nm; average shear demand 1.965 MPa with 50% effective area.

These are preliminary demand/strip screens, not validated capacities. Peel, carbon interlaminar failure, collar/tape transfer, skin buckling, discontinuous skin shear flow, local torsion, adhesive process and fatigue are unresolved. No favorable sharing between skins and spar is assumed in the separate cheek torsion scenario. Corner radii, fillets, continuous ply drape and ply terminations must be developed before manufacturing drawings are released. No new global wing stiffness credit is taken.

## Build and service sequence

Install the carrier and reinforcement while the wing is open, in a fixture referenced to the spar and motor axes. Form the skin cap strips to the native contour; cut the flat web/collar pieces; form the spar cheeks on a matching split tool. Prepare and bond the composite interfaces with a selected, qualified adhesive process. Complete the corner tapes/fillets and slot edge closure before skin closure. Keep inspection access during bonding. The arm carrier is permanently bonded; the motor/clamp service approach is retained from P05, including bench installation of the motor screws.

See docs/DESIGN_AND_BUILD.md for construction assumptions, load path and source guidance. The P04 center/root joint is retained rather than qualified by this local integration. Motor screw engagement and the21 V motor versus6S battery issue remain open.

## Files

- `cad/RescU_P07_Wing_Arm_Integration.FCStd`: native constrained assembly.
- `cad/RescU_P07_Wing_Arm_Pair.step`: both wing/arm groups.
- `cad/RescU_P07_PosY_Wing_Arm.step` and negative-Y equivalent: one side.
- `cad/RescU_P07_PosY_Carrier_Cutaway.step` and negative-Y equivalent: reinforcement and carrier, without opaque wing skin/core context.
- `cad/parts/`: individual new glass/epoxy laminate regions, in installed coordinates.
- `reports/mass_components.csv`, `results.json`, `fit_checks.json`, `splice_checks.json`, `step_validation.json`: accounting and checks.
- `data/`: assumptions and replacement accounting snapshot.

## Fit scope and remaining geometry decisions

There are no reported hard-part clashes after final relief. 15 nominal wet-bond volume intersections below 0.02 mm³ are retained as construction-layer ambiguity. Their summed epoxy-equivalent mass upper bound is 0.000114 g, within the unchanged adhesive allocation. They are not rigid-part interference or extra reserve mass.
Foam compatibility uses the defined pocket construction and removed-volume conservation; a full compound/foam Boolean was deferred. Skin/bond checks cover the outer bedding interfaces. See fit_checks.json for the exact full/incremental method and exclusions.
Slot doubler blanks have 8 mm nominal expansion before trimming. Actual bounding-outline extensions are 6.1 mm at the front edge of the spar slots and 5.7 mm aft of the rear slots; other outline extensions are 8 mm. Reliefs interrupt the perimeter, so these are bounding dimensions, not a verified continuous bonded lap. Patch extent/skin shear-flow restoration requires further design.
The wire gauges are proposed 8 mm bundle envelopes routed outside the arm and below the wing, starting at a free-air point outside the motor body. All four clear the modeled physical parts. Actual motor lead exit, bend radius, clips/strain relief and ESC termination remain unverified; the 52 g motor-with-wires allocation is unchanged.
New laminate layers use vertical-thickness geometry surrogates, not an exact normal-offset ply schedule. Select cloth, cure process, corner radii and fillets before manufacturing release.
