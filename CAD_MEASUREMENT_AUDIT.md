# RescU CAD measurement audit — current Assembly 2

## Status

**Partial verification; not 100% certainty and not structural approval.** The user selected current Assembly 2 as the reference. No source Onshape geometry, mates, features, or team files were edited. V2 and V3 analysis inputs have not been changed by this audit. Earlier V3 numerical results and selected skin/foam schedules remain preliminary and are not validated for this CAD profile.

Source: [team Onshape document](https://cad.onshape.com/documents/9c0191ce087db9938fe55109/w/8c01ddb9176fc18919448d97/e/5f8a25da807435aec98fe36c). The linked document was opened in its anonymous view-only interface. Main is a mutable workspace, not a frozen version.

Assembly 2 STEP AP242 export header timestamp: **2026-10-08T06:57:04Z**. SHA256: `026eaee219b990a2283993cb1202752c7ab20a0f40855b0ea8253e61e0c278a5`. Hidden instances were included; Y-up reorientation was disabled. The export contains 17 solids. STEP declares metres; the OCCT reader reports imported coordinates in millimetres.

The separate Fuselage, Wings, Tail export header timestamp is **2026-10-08T06:46:12Z**; SHA256 `dad3b4b83bef641e670226af07752874166144bc07213b368bcb70e9ec1aa3c88`. Its clean section cuts were checked against Assembly 2 by corresponding solid surface areas and translated vertices. Wing/body, front body, aft body/tail and pusher-body vertex residuals are below 1e-9 mm, with equal surface areas. This establishes correspondence of these exported shapes, not original feature dimensions or manufacturing accuracy.

## Coordinate definition

Native CAD X is vertical, Y is longitudinal, and Z is lateral. For the main wing/front-body datum, convert Assembly 2 coordinates in mm as follows:

```
analysis x = (CAD Y + 164.018617704567) / 1000
analysis y = (CAD Z - 291.063261761907) / 1000
analysis z = (CAD X - 241.329811392558) / 1000
```

Analysis x begins at the front-body nose; y begins at its symmetry plane; z begins at the wing/arm-top datum. The aft body/tail sits 0.215577 mm vertically, 0.124463 mm longitudinally and 0.000694 mm laterally away from its Part Studio position relative to the main-body translation. Current Assembly 2 placement is authoritative for this audit.

## Confirmed agreement, to the precision of the exported geometry

- Wing span: **1,400 mm**, versus code 1.400 m. Both tip coordinates and span bounds agree.
- Main-wing root leading edge: **260 mm** from the nose. Tip leading edge: **400 mm**; leading-edge sweep offset **140 mm**. These agree with the code's 260 and 140 mm entries.
- V-tail panel span measured along the inclined panel: **245 mm**. Leading-edge longitudinal offset: **120 mm**. Both agree. The 212.176 mm horizontal half-span must not be mistaken for the 245 mm panel span.
- Motor-arm geometric extent: **350 mm long × 30 mm wide × 20 mm high**, longitudinal endpoints **220 and 570 mm**, lateral centers **±265 mm**, vertical center **−10 mm**. These agree with the corresponding code entries. This does not establish tube wall thickness or actual attachment stiffness.
- Four mount-platform centers: front **x=235 mm**, rear **x=555 mm**, lateral positions **±265 mm**. Platform top is **z=15 mm**, bottom at z=0. Mount centers are different quantities from motor centers of gravity or propeller axial planes.

## Confirmed discrepancies

**V-tail dihedral: CAD 30°, code 35°.** Tip displacement relative to root is 122.5 mm vertically and 212.176224 mm laterally; atan2 gives 30°. Independent end-face normals agree. Root-leading-edge station in current Assembly 2 is approximately **960.124 mm**, versus nominal code 960 mm, owing to the small assembly translation above.

**One front lift propeller is displaced from its mount.** The negative-lateral front propeller central bore and outer hub cylinders share an axis at **x=231.153922 mm, y=−257.878804 mm**. Its platform center is x=235 mm, y=−265 mm: longitudinal error −3.846078 mm, lateral error +7.121196 mm, combined in-plane distance **8.093 mm** (rounded). The other three lift-propeller axes agree with their platform centers. This is an assembly-placement observation; it does not prove an actual manufactured motor is misplaced. Have the CAD owner inspect the instance/mate. No mate was changed.

**Wing section differs from SD7037.** The clean wing section at lateral station 699.999 mm has surface-projected chord **97.428677 mm**, obtained from refined curve extrema. At common longitudinal coordinates, densely sampled upper-minus-lower thickness reaches approximately **12.318% of this projected chord**. This corrects the earlier roughly 12.5% estimate based on separate upper/lower extrema. The code's SD7037 section is approximately 9.2% thick. These are materially different profiles; the CAD airfoil name cannot be established from thickness alone. Do not infer a NACA designation without the generating definition.

The code's VTOL z=0 entry does not equal the current propeller-hub axial interval, approximately **z=15 to 25.897 mm**. Clarify whether the input is meant to be the motor CG, mount datum or hub plane before changing it.

## Dimensions that require definition or additional evidence

- **Wing chord 165/100 mm:** clean surface sections give 156.233241 mm at span 50, 151.709784 at 100, 129.092500 at 350 and 97.428677 near 700 mm. Linear extrapolation implies surface-projected root chord about **160.756698 mm** and tip chord **97.428587 mm**. The root is extrapolated because the fuselage obscures a clean root section. These do not by themselves disprove nominal 165/100 mm generating parameters. Need the profile-generator/sketch chord definition and airfoil coordinates. A simple bounding box over spline surfaces is not reliable for this comparison.
- **Tail chord 90/45 mm:** clean cuts imply projected root/tip about **87.70095/43.85048 mm**, with root extrapolated. The tip normal-section thickness is approximately **10.263% of projected chord**, consistent with about 10% of the nominal 45 mm chord, but this does not independently identify NACA0010. Obtain its generating definition too.
- **Wing area 0.185 m²:** nominal trapezoid 1.4×(0.165+0.100)/2 is 0.1855 m². Surface-chord extrapolation gives about 0.180730 m² for the ideal full-span projected planform. Neither is a verified selection of the actual exposed planform. Decide whether area includes the region inside the fuselage and uses nominal or trimmed surface boundaries.
- **Fuselage area 0.257 m²:** not verified. Bodies contain wing/arm attachments, internal and cut faces, and shared boundaries. Summing all exported solid areas would be wrong. Need an explicitly selected exterior fuselage face set or an isolated clean exterior shell, with the intended included/excluded faces recorded.
- **Fuselage length 1.110 m / overall 1.125 m:** endpoint definitions are missing. Current pusher propeller axis is about **1.137401 m** from the nose. A lumped pusher CG at 1.110 m is a different quantity. These code entries cannot be marked wrong or confirmed by comparing them indiscriminately with the full assembly envelope.
- **Arm bearing stations 313/448 mm:** the front value resembles wing leading-edge geometry at the arm centerline; the rear varies with which inner/outer intersection is chosen. No distinct pair of load-bearing joints was established. Need actual bonded contact regions, inserts and load paths rather than guessed support points.
- **Wall/skin/core thicknesses, layups and material grades:** not established by these exterior CAD solids. The arm 1 mm wall and fuselage 0.4 mm skin remain analysis assumptions. Battery/equipment CG locations require installed-component data, not an exterior envelope.

## Limitations and actions needed

OCCT 8 marks the front-body solid invalid in both exports (Assembly 2 solid 15). That is an import/topology validation result, not proof the native Onshape model is invalid. The independent OCCT 7.9 reader could not load because Windows Application Control blocked its native DLL. Thus that second-reader check is incomplete. No shape was repaired. Use an alternative allowed reader or native Onshape face/area measurements and a clean re-export to distinguish export/import issues from native geometry defects.

Live Onshape Measure did not populate its entity selector through the available automation. Therefore these results are **STEP-derived checks, not independent live Onshape measurement confirmations**. Team-owner measurements of the explicitly named entities would provide a second route. A frozen Onshape version/export is also needed for a stable design baseline; subsequent changes to Main require a new comparison.

Before accepting the sparless design: obtain wing/tail profile coordinates or generating feature definitions; define chord/area/endpoints; check the displaced propeller instance; provide exterior fuselage sections and face selection; and define wing-root, motor-arm, tail and pusher attachments. Then revise a separate analysis candidate, rerun mass/CG/strength/stiffness checks and validate manufactured laminate/core/joints with suitable coupons and representative load tests. Correct dimensions alone cannot certify the foam-only load path.

## Reproducibility

Local supporting files: both unchanged STEP snapshots, `assembly_inventory.json`, `geometry_inventory.json`, `section_summary.json`, section CSVs, `cross_checks.json`, and `normalized_profiles.csv`. `measure_step.py`, `sections.py`, and `check_profiles.py` record the extraction and cross-check methods. Raw CAD snapshots and CAD-reader packages are kept locally, not uploaded to the code repository by this audit.
