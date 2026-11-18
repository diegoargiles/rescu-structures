# Current development status

Updated November 17, 2026. **R16 is the current design** (committed assembly: R16.4). It lands on a ground landing station; it has no landing gear.

| Work | Status | Evidence |
|---|---|---|
| R15 full-aircraft CAD | Baseline for R16 (Nov 9) | [R15 README](../cad/r15/README.md) |
| R16 wing-root elbow joints | Geometry candidate; nothing trimmed by the skin | [R16 README](../cad/r16/README.md), [interference](../cad/r16/interference_r16.json) |
| R16 mass/CG (CAD + inputs.json equipment) | R16 base: 3387.0 g, CG x 406.6, SM +1.0 % MAC. R16.2 estimate: about 3412 g, CG x ≈ 405 (cg.json not regenerated) | [cg.json](../cad/r16/cg.json), [R16.1/R16.2 mass changes](../cad/r16/README.md#mass-changes-r161--r162) |
| R16.1 nose | Faceted strips replaced by the exact elliptical surface; shape unchanged | [R16.1](../cad/r16/README.md#r161--smooth-nose-pusher-motor-and-propellers-november-16) |
| R16.1 propulsion CAD | Tarot 4008 pusher, APC 10x3 (Quad-X hands) and 13x8P props in the assembly; prop adapter provisional | [R16.1](../cad/r16/README.md#r161--smooth-nose-pusher-motor-and-propellers-november-16), [checks](../cad/r16/clearance_r16_1.json) |
| R16.2 pusher mount | Tarot bolted to the plate (Ø19 circle, 4× M3 × 4); plate bonded to collar; collar bore Ø26; wire-tab notch; 0 overlaps | [R16.2](../cad/r16/README.md#r162--pusher-mount-and-prop-nuts-november-17), [checks](../cad/r16/clearance_r16_2.json) |
| R16.3 nose camera | Camera (270 g; Z30 geometry) in a faired cove, full gimbal sweep with ≥ 5 mm; drag about 25–35 % of cruise thrust (estimate) | [R16.3](../cad/r16/README.md#r163--nose-camera-z30-in-a-recessed-cove-november-17), [checks](../cad/r16/clearance_r16_3.json) |
| R16.4 removable nose module | L/R shells, cove liner, NF1–NF4, camera shelf + nutplate mount, 4-screw joint; no unintended overlaps; about 3738 g, CG x ≈ 378 | [R16.4](../cad/r16/README.md#r164--removable-nose-module-november-17), [checks](../cad/r16/clearance_r16_4.json), [manufacturing](../manufacturing/NOSE_MODULE_MANUFACTURING.md) |
| R16.2 prop nuts | UM2807 thread +4 mm (model), M5 bullet nuts; real shaft length to be checked | [R16.2](../cad/r16/README.md#open-items) |
| Landing provisions | TPU feet removed; tripod gear studied and dropped (+54.5 g, CG behind NP); folding pusher judged not workable | [R16 README](../cad/r16/README.md#landing-decision-history) |
| Landing station | Designed, fit-checked against R16, manufacturing plan written; not built | [Station](../cad/landing_station/README.md), [manufacturing plan](../manufacturing/LANDING_STATION_MANUFACTURING.md) |
| Precision landing (±40 mm) | Open — RTK or beacon to be chosen | — |
| R16 root elbow spar spigot | Screen ≈ 317 MPa (conservative, spar-only): use solid rod or lengthen | [R16 README](../cad/r16/README.md#checks) |
| Battery position for target CG | Open — x ≈ 256 mm | [cg.json](../cad/r16/cg.json) |

## Previous checkpoint (November 5, 2026)

This checkpoint added R13/R14 progress to the preserved V4/P03 repository.

| Work | Status | Evidence |
|---|---|---|
| R13 layout | Geometry candidate | [Review](R13_REVIEW.md), [checks](../reports/r13/geometry_checks.json) |
| R14 socket overlap | Fit-tested candidate | [Study result](../cad/r14_socket_study/study_summary.json) |
| Attachment load path and demand | Analytical screen | [Calculations and scope](../reports/connection_study/START_HERE.md) |
| Equipment placement | CAD extraction + proposed positions | [Register](../reports/connection_study/equipment_mass_location_register.csv) |
| Full aircraft mass/CG | Incomplete | [Missing entries](../reports/connection_study/cg_status.json) |
| Material/process selection | Supplier-backed candidates | [Specification](../requirements/MATERIAL_BOND_TWIST_CANDIDATES.md) |
| Laminate/bond strength | Unqualified | Actual material/process data and representative tests required |
| Accepted wing twist | Open | Aero/Controls sensitivity and acceptance required |
| R13/R14 assembled FEA | Not yet performed | Historical archived FEA does not validate this assembly |

## Versioned review packages

- [R13 layout review](https://chatgpt.com/library?file_id=libfile_573f8c70636c8191aa2602bc7ac1c0de&account_id=personal)
- [Attachment loads and R14 study](https://chatgpt.com/library?file_id=libfile_4e62f1a569b08191858788317d0e35ea&account_id=personal)
- [Material, bond and twist basis](https://chatgpt.com/library?file_id=libfile_eb4efc9253088191966d57c1c96d01f9&account_id=personal)

These owner-access package snapshots predate this GitHub publication. Repository documentation may subsequently contain clearer run instructions and status updates. The native CAD source hashes are retained in [the file manifest](../cad/FILE_MANIFEST.md). The packages are not public team download links.

The current native assemblies are distributed through those packages, not committed or stored in Git LFS in this checkpoint. Directly committed smaller STEP exports and review images are listed in the manifest. This distinction prevents treating a documentation link as a stored CAD binary.

## Validation at publication

Reproduced the thrust-only beam, attachment-demand and candidate-material calculations; force/moment equilibrium and support-displacement assertions passed. Confirmed the expected incomplete-inventory exit from the CG script. Checked included Python syntax, current CAD/check hashes and Markdown relative-link targets. Geometry itself is supported by the recorded R13/R14 targeted checks; no new FEA or flight validation is claimed.
