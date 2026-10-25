# P06 rib-to-saddle connection review

**Detailed geometry candidate. Peel/fatigue and wing-slot reinforcement remain unresolved.**

## Connection modeled

Eight external glass/epoxy splice plates bridge the P05 rib/saddle gaps. Front plates are2 mm thick, rear plates1.5 mm. Each overlaps24 mm along the arm, bonds to the saddle wall below and to a fitted1.8 mm rib packer above. Three explicit0.2 mm bond layers per connection make the lap interfaces visible and measurable. The rib-to-spar/skin connection remains a wing-group task.

Added 40 separately identified pieces/layers; arm-only STEP contains 162 solids. Existing P05 motors, motor mounts and carbon arms are retained. Native fixed joints attach ribs through the new front splice, with a nonredundant constraint tree. Rear physical bond paths are checked geometrically without adding redundant fixed-joint loops.

Original P05 minimum rib/saddle gaps:0.997/1.454 mm at the front and2.964/3.336 mm at the rear on the positive-Y arm. Flat plates bridge those spaces; the design does not depend on edge contact.

## Verified geometry and explicit wing changes

- Internal new-part interference pairs: 0.
- Native reopen/solver and face coverage: PASS: geometric coverage, native reopen/solver and explicit slot/spar compatibility checks.
- 24 bond groups, with48 adherend-side contact checks. Minimum face coverage / mean slab area: 94.54%. Joint screens use the smaller measured contact area, then an assumed50% effective-area factor.
- Arm-only STEP passes geometry, solid count and component-center checks; maximum component-center error 0.000455043 mm.
- Spar outside-surface clearance:0.4 mm. Native conical outer surface is filled and offset, including the inner bore region; no spar material is removed.
- Proposed lower-skin entry slots: four per arm, eight total. Length24.6 mm, width4.8 mm front/4.3 mm rear. The skin cutter stops atZ7 mm. Upper plate contours are trimmed to the actual core envelope with0.3 mm vertical margin; upper-skin interference is checked separately.
- Post-relief skin clearance:0.3 mm nominal, with no detected remaining physical intersection. Foam context includes installation clearance. These are proposed skin/foam cutouts, not a released wing modification.

## Skin quantity limitation

The relieved wing-skin shapes are valid and pass the geometric clearance test, but their Boolean volumes fail conservation. The raw differences include an unphysical apparent volume increase on one side. **No skin cutout mass credit is accepted.** The original P05 skin quantities stay in the budget. Diagnostic quantities remain in geometry_checks.json; valid BREP alone is not accepted as mass validation.

Foam removed volumes pass the separate conservation check (within1% of the removed volume). Only that foam credit is used. Skin-slot reinforcement/sealing mass is not designed or credited yet.

## Mass reconciliation

- P05 structural budget: 1136.914 g.
- P06 provisional gross structural budget: 1157.673 g.
- Increase: 20.759 g.
- New glass laminate: 20.931 g; explicit new epoxy: 1.440 g.
- Epoxy is reallocated from the existing saddle/rib adhesive budget: 10.618 → 9.177 g residual. It is not counted twice.
- Foam credit: 0.1716 g. Skin credit:0.000 g.
- Accounted / sizing aircraft: 3.6329 / 3.8329 kg. Reserve remains200 g, separate and counted once.
- Aircraft CG X: 397.40 mm, provisional.
- Earlier71.683 g generic hardware and42 g embedded mount allowances remain removed. Motor/prop mass rows and battery budget remain unchanged. Future wing-slot reinforcement and other existing P04/P05 gaps are not included.

## Preliminary demand checks

- Inherited hypothetical17.3 N/motor ×1.5 gives25.95 N/motor. Front-only/rear-only cases reverse the saddle reactions; peak absolute front/rear reaction is84.725/96.151 N.
- Both equal rib sharing and a full station reaction carried by one splice are evaluated. Strength values, load sharing and effective-area reduction remain assumptions.
- Front plate net width is sampled across the actual spar-relief section atZ5–11 mm in0.25 mm increments. Full one-splice force is conservatively applied across the smallest sampled section. Rear full-width bridge section is used. This is a strip approximation, not a laminate/3D stress solution.
- Worst average-shear utilization: 0.772 against an assumed2 MPa value.
- Worst combined plate-strip utilization: 0.740 against an assumed70 MPa value.
- Maximum adhesive peel-demand proxy: 3.524 MPa. No qualified peel capacity is available, so this remains UNRESOLVED.
- Eccentricity, spar-relief load distribution, laminate interlaminar failure, saddle-wall crippling, bond end effects, hot/wet exposure and fatigue require refined analysis and representative joint tests. Passing the two preliminary averages does not qualify the connection.

## Global wing screens

- Wing 3g: PASS, twist -1.489°, tip displacement 26.44 mm.
- Wing -1.5g: PASS, twist -0.746°, tip displacement -13.22 mm.
- Wing 3g at70% assumed stiffness: FAIL, twist -2.128°, tip displacement 37.76 mm.

No favorable stiffness credit is added for these splice plates, and the skin-slot effects are not represented by the ideal wing beam. The beam screen is not conservative proof of the slotted wing.

## Next wing-group work

Detail rib-to-spar/skin load transfer, slot-edge reinforcement/sealing, spar installation access and skin closure. Validate eccentric bonded laps, saddle/carbon interface and load sharing with tests before manufacture. The current concept is a permanently bonded arm carrier. Existing P05 motor screw-depth and electrical-supply issues retain their previous status.

See docs/CONNECTION_DESIGN.md for fabrication, assembly order and assumptions.
