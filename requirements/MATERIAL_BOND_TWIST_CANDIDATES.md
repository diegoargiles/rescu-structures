# RescU material, bond and twist basis — candidate specification

November 5, 2026. Diego confirms no materials purchased/committed and vacuum bagging available. This completes the first supplier-backed candidate selection; material qualification, joint qualification and flight stiffness acceptance remain open. No procurement or changes to baseline CAD/material inputs were made.

## Candidate material system

| Part/process | Candidate | Use and unresolved evidence |
|---|---|---|
| Motor booms | Easy Composites CFT-WF-25-23-1 | Exact nominal25/23 mm stock match; two470 mm pieces fit within one1 m tube before reasonable saw kerf. Confirm delivered length/quality. |
| Motor rib and socket laminate trials | 210 g/m² 2×2 twill carbon cloth + EL2/AT30 Slow epoxy | Vacuum-bagged wet layup; start with flat coupons before curved socket tooling. No cured laminate allowables yet. |
| Secondary bonds between cured composite parts | 3M DP420 Black | Candidate for boom/socket and cured rib/sleeve bonds; qualify actual surfaces and geometry. Not automatically selected for XPS bonding. |
| Existing GFRP sleeves/collars and shell | Preserve current geometry and material labels | Exact glass cloth/epoxy construction still to be selected; do not assign carbon properties to these parts. |

### Published inputs and their limits

**Tube:** supplier lists axial modulus64 GPa, longitudinal tensile strength650 MPa and mass113.1 g/m. Construction is predominantly0/90 reinforcement with a woven exterior and clear coat. Use64 GPa as a candidate axial beam modulus, not an isotropic modulus for every direction. The650 MPa value is not a compression, bearing, torsion or design allowable. Torsional strength is not supplied. Its tabulated dimensional tolerance is0.2 mm; confirm whether that denotes a total or signed tolerance and measure actual stock. Source: https://www.easycomposites.us/25mm-23mm-woven-finish-carbon-fiber-tube

**Cloth:** the linked product is currently210 g/m², despite its200g URL. It lists0.25 mm consolidated thickness and orthogonal yarns. Treat thickness as a planning value only. Source: https://www.easycomposites.us/200g-22-twill-3k-carbon-fiber-cloth

**Laminating epoxy:** EL2 supports wet layup and vacuum bagging. Its specified resin:hardener ratio is100:30 by mass. Manufacturer guidance includes at least14 days at25°C for ambient mechanical-property development, or a suggested24 h room-temperature cure followed by6 h at60°C. Actual temperature history, tools and substrate compatibility must match the selected procedure. Do not use neat-resin mechanical properties as reinforced-laminate properties. Source: https://media.easycomposites.co.uk/datasheets/EC-TDS-EL2-Epoxy-Laminating-Resin.pdf

**Adhesive:** use the DP420 Black V7 datasheet, revised December2025, rather than the older2016 multi-product sheet. It reports an epoxy-FRP lap-shear result39.3 MPa after7 days with specified preparation, and test bondlines0.13–0.20 mm. This is a specimen-specific typical result, not an allowable for our curved socket or a peel limit. Do not calculate a socket safety factor by dividing it by mean force/area. Source: https://multimedia.3m.com/mws/media/2365743O/3m-scotch-weld-epoxy-adhesive-dp420-black.pdf

## Initial laminate coupon plan — engineering proposal

For a flat motor-rib coupon, trial eight woven plies `[0,45,0,45]s`; each angle refers to the fabric warp relative to the rib chordwise datum. A0-degree woven ply includes0/90 yarns; a45-degree woven ply includes±45 yarns. The mirrored stack provides equal fabric counts in those orientations. Eight times the catalog0.25 mm gives an approximately2 mm planning thickness, matching the nominal rib. This is not a released laminate: measure cured thickness, fiber/resin content, voids and bearing performance first. Woven ply property matrices are needed for classical laminate analysis.

The same flat stack is not automatically a socket manufacturing recipe. Curved sockets need continuous fibers around the sleeve and into the ears/deck, supported corners and controlled laps. The current1.35 mm sleeve wall and2.35 mm ears do not correspond to a guaranteed integer number of these plies. Develop a mandrel/mold and ply map after measuring actual ply thickness; then update CAD to the manufacturable section. Do not machine a cosmetic model from a flat plate and assume fiber continuity through the joint.

Bag the solid laminate coupons/parts with controlled resin bleed and a supported tool. Record cloth/resin batch, ply directions, mixed mass, vacuum achieved, leaks, cure temperature/time, final mass and thickness. Vacuum access alone does not establish a fiber fraction or void-free process. Manufacture/post-cure separate composite parts before XPS assembly; do not subject the foam or completed electronics assembly to an assumed oven cycle.

## Bond specification development

1. Measure boom OD/ovality at each bond station and socket ID after manufacture. Target nominal radial gap0.15 mm for the first comparison specimens, but qualify the achievable range. Actual gap is `(socket ID − boom OD)/2`; the nominal25.3 mm socket cannot guarantee that gap on every25 mm tube.
2. Establish a coating-removal and surface-preparation procedure with the tube/adhesive supplier. The glossy outer finish is not an established structural bonding surface. Avoid cutting load-bearing fibers. Keep release agent and preparation debris away from bonding surfaces.
3. Use the selected product's mixing system and current instructions. Qualify the fixture, adhesive application/insertion method, gap control, bond coverage and fillets on sacrificial samples. Do not assume squeezing until tight improves a bond.
4. Prepare representative20 and32 mm overlap joints using actual stock and actual socket laminate. Inspect coverage by sectioning a sacrificial specimen. The R14 length is a comparison candidate, not accepted optimum.
5. Measure joint slip/compliance and failure behavior under both vertical reaction directions and lateral/retention loading. Include the actual rib, bolt and ears in the final fixture, not only a lap-shear coupon. Evaluate wet-conditioned samples for the maritime mission; define exposure conditions before testing and report them without claiming service-life equivalence.

For each screening condition, propose at least three specimens to reveal obvious scatter, with untested controls where conditioning is compared. This small sample is not a statistical material allowable. Faculty/lab supervision should establish test fixture capacity, exclusion zones and acceptance criteria. Tests must distinguish adhesive separation, laminate delamination, bolt bearing, ear bending and tube crushing. NASA joint guidance: https://ntrs.nasa.gov/citations/19890016677

## Candidate tube calculations

Calculations are saved in `material_candidate_screen.json` and reproduced by `analysis/r13/material_candidate_screen.py`. They use the existing ideal two-support beam model and supplied nominal tube geometry. They do not include wing/support/joint compliance, transverse shear, local shell deformation or motor inertia.

- I=π(25⁴−23⁴)/64=5438.10 mm⁴.
- EI=64000×5438.10=348.04×10⁶ N·mm².
- Two470 mm tubes:2×0.470×113.1=106.314 g, using catalog linear mass.
- At17.3 N at both motors, predicted rear motor displacement is approximately0.1856 mm using64 GPa.
- At26 N at both motors, it is approximately0.2790 mm. Maximum nominal bending stress is11.65 MPa at limit and17.48 MPa with the inherited1.5 multiplier. Compression, local buckling, fatigue and joint acceptance remain unresolved; no safety margin is released.

Catalog linear mass is used directly instead of forcing it to match the earlier assumed1600 kg/m³ density. This side study does not revise aircraft mass/CG or remove manufacturing allowances.

## Acceptable wing twist — analysis plan and interim status

The inherited2-degree criterion remains unapproved. Define local elastic twist as section-chord rotation relative to the root reference after subtracting rigid-body motion. Report twist versus span and load, including asymmetry; tip deflection alone cannot determine it. Do not calculate wing torsional stiffness from the round boom or aft spar alone. The skin, rib bonds, main spar, aft tube, root connections and load distribution all contribute.

Run geometry-preserving aero sensitivity cases at±0.5°,±1° and±2° using explicit spanwise twist shapes, plus symmetric and asymmetric structural predictions. These are study points, not permitted values. Compare lift redistribution, stall margin, trim, pitching/rolling moments and control authority at cruise, transition and high-demand conditions. Raphael and Mooneeza must define acceptable changes and operating conditions; Structures can supply twist/load curves.

As a scale illustration only, thin-airfoil slope2π/rad gives ΔC_l≈0.055,0.110 and0.219 for local changes0.5°,1° and2°. This is an ideal two-dimensional attached-flow estimate, not the SD7037 finite-wing response or an allowable. Use the actual airfoil/wing analysis to replace it.

Until those limits exist, report predicted twist without PASS/FAIL. Propeller, ground and control-surface clearance budgets remain independent checks. A higher ultimate factor cannot substitute for a stiffness requirement.

## Information still needed from Diego/team

Nothing else is needed to finish this candidate-research stage. Before manufacturing, confirm lab-controlled post-cure access (or choose/document the ambient-cure route), available load/displacement measurement equipment, and any teacher-mandated process. From Aero/Controls, request allowed lift/trim/control changes and operating cases rather than asking them to guess one twist number. No purchases are implied by this specification.

## Stage status

Supplier candidates and usable property inputs identified; one axial-stiffness/mass screen completed. Still open: delivered tube verification, compression/shear/bearing properties, cured laminate characterization, actual bond tests, and aerodynamic twist acceptance. Keep these distinctions in reports and the project register.
