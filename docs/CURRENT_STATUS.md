# Current development status

Updated November 5, 2026. This checkpoint adds R13/R14 progress to the preserved V4/P03 repository.

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
