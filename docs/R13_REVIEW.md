# R13 layout review — November 5, 2026

Recovered and checked the saved R13 candidate after the previous conversation ended. R12 remains the baseline. R13 is a layout candidate, not a strength-qualified design.

## Open the model

Open `cad/r13/RescU_R13_Layout_Candidate.FCStd` in FreeCAD. The assembly STEP is included for SolidWorks import; the new-parts STEP contains only the added physical parts. Reference propeller disks are in the native model and excluded from the STEP physical assembly. See `R13_Layout_Review.png` for the layout overview.

## Implemented geometry

| Item | R13 candidate |
|---|---|
| Round motor booms | 25 mm OD, 23 mm ID, 470 mm long |
| Front / rear motor X | 170 / 600 mm |
| Motor height | 6 mm lower than R12 |
| Motor attachment | Separate bonded composite pods with screw clearance |
| Wing attachment | Bonded boom sockets connected to motor rib |
| Aft reinforcement | 5 mm OD / 3.5 mm ID tube, ending at absolute Y = 415 mm |
| Aft collars | Stations 265, 310, 360 and 410 mm |
| ESCs | Relocated inside fuselage; deck, pads and cradle provisions |

The aft member extends past the third outboard rib beyond the motor rib. Bond design, retention and load transfer remain open; fitting geometry alone does not establish a sound structural joint.

## Verification completed

The latest native model passed the existing targeted static geometry check: 143 candidate bounding-box pairs tested, no intersection volume above 0.01 mm³, and no invalid checked shapes. The earlier ten aft-member/skin intersections are absent in this rerun.

The checker covers added parts and relocated motors, screws, hubs and ESCs against physical features. It excludes unchanged-to-unchanged pairs and modified-rib-to-inherited-shell pairs. It is not a full-assembly interference certification. Plan-view clearance uses a tessellated wing convex hull and polygonal 254 mm propeller disks, not a measured loaded blade envelope.

| Nominal plan clearance | Both sides |
|---|---:|
| Front propeller disk to wing | 13.223 mm |
| Rear propeller disk to wing | 18.773 mm |

Blade flex, structural deflection, tolerances and ground clearance must still be included. The straight main joiner axis was retained. The checked tail pin axes are recorded as geometry evidence; pin-axis inclination alone does not measure the V-tail surface angle.

## Mass and loads

The modeled changed-part mass is 52.8 g lower than R12 using assumed densities. This excludes added adhesive, ESC retention, changed wiring/connectors and finish. It is not an updated aircraft mass or CG. The round boom pair itself is about 5.9 g heavier; savings come from the combined changed-part set.

The thrust-only beam screen was rerun and its force/moment equilibrium and support-displacement assertions passed for all cases. At provisional 17.3 N per motor, the largest support reaction magnitude rises from 54.37 N in R12 to 65.49 N in R13. These figures exclude assembled wing/joint compliance, inertia and motor torque; they are demand estimates, not joint allowables.

## Next engineering decisions

1. Review this layout and finalize propeller dimensions and motor supply/thrust data with Propulsion.
2. Define the aft-root, collar and main carry-through bond load paths, layups and adhesive/process.
3. Obtain current mass/CG and operating envelope inputs using `requirements/TEAM_DATA_REQUESTS.md`.
4. Apply the load cases in `requirements/LOAD_BASIS.md` to the actual ribbed-wing assembly, including wing twist, joint demands and clearance under load.
5. Select representative structural tests and compare them with calculations before declaring allowable loads.

The inherited +3 / -1.5 load factors, 1.5 ultimate multiplier, 5% half-span deflection and 2-degree twist criteria are provisional comparison assumptions, not established aircraft capability or accepted requirements.

## Package provenance

`cad/r13/summary.json` records the native CAD hash and R12 baseline hash. `reports/r13/verification_record.json` ties this rerun to the native CAD. Build, check, render and load-screen scripts are included. Older interference diagnosis files are historical; use `geometry_checks.json` for the current result.

At recovery, the local development folder was not a Git checkout and remote `r13-layout-load-basis` and `main` both pointed to `73391e627e078dced2644a18da135a09c447282f`. The subsequent GitHub publication adds these development records and scripts to `main`; see [current status](CURRENT_STATUS.md) and the [CAD file manifest](../cad/FILE_MANIFEST.md) for what is committed versus available in the package snapshots.
