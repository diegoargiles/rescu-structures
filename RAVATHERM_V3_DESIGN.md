# Ravatherm-based V3 configuration — 2026-10-16

## Decision and status

Use **Ravatherm XPS X H LB**, **0.33 mm fuselage and wing GFRP skin**, and two **custom tapered CFRP tubular half-wing spars** at **30% local chord**. Retain the 0.264 mm tail skin, 900 g battery, team geometry, external arms, and payload plate. Replace H60 in both modeled wing and tail cores; fuselage core geometry remains unknown and is not invented.

This is a separate preliminary configuration, not a release to build or fly. Original `RescU_Structures_V3.py` and V2 are unchanged. Based on GitHub `foam-core-gfrp` commit `ac0b68db25fb73b2f4fcf0d7762dc8c4e001767b`. The actual starting skin values are 0.400 mm fuselage and 0.895 mm wing, not 0.44 mm. Diego explicitly selected fuselage and wing for the 0.33 mm change.

## Proposed dimensions

| Item | Root | Tip / total |
|---|---:|---:|
| Tube outside diameter | 14 mm | 8 mm |
| Tube wall thickness | 2.0 mm | 0.5 mm |
| Tube inside diameter | 10 mm | 7 mm |
| Chordwise center | 30% local chord | 30% local chord |
| Distance aft of local leading edge | 49.5 mm | 30.0 mm |
| Aircraft x, nose datum | 309.5 mm | 430.0 mm |
| Spanwise coordinate, each side | 0 | ±700 mm |
| Tube centerline length | — | about 710.3 mm each |
| Pair tube mass | — | 91.0 g |
| Fuselage skin | — | 0.330 mm |
| Wing skin, per face | — | 0.330 mm |
| Tail skin, per face | — | 0.264 mm, retained |

OD and wall thickness both taper linearly with span. The exact annular area and second moment are used; a thin-wall approximation is not used, since the root wall is relatively thick. These dimensions require a custom tapered mandrel/layup and qualified ply transitions; they do not specify an available stock product. Purchased stock tubes would require a separate stepped/jointed design and recalculation.

The two halves sweep aft with the wing. They are not one straight 1.4 m rod. A designed center carry-through must transfer bending into the fuselage and connect both halves. The model uses ideal fixed roots and does not size that joint. In CAD, keep the tube center near the midpoint between the local upper and lower skins; map to actual wing dihedral and coordinates. Modeled section z values are not global CAD z dimensions. Do not cut tubes to the calculated length before accounting for the center joint and root overlap.

## Why CFRP and why position matters

With the same geometry, the assumed CFRP has greater bending stiffness per mass than GFRP. The selected pair is 91.0 g in CFRP versus 105.3 g in GFRP. The assumed CFRP axial modulus/density/strength are 70 GPa / 1600 kg/m³ / 300 MPa; GFRP trade values are 25 GPa / 1850 kg/m³ / 150 MPa. A 0.70 strength knockdown is applied. These are inherited preliminary engineering assumptions, not measured vendor allowables or laminate properties proven for a tapered tube.

A spar is structurally useful here: with the requested thin skins and the same Ravatherm configuration but no spar, the calculated positive-load tip deflection is 58.5 mm against a 35 mm screen. The selected spar reduces that to 23.9 mm, with each configuration's own recalculated sizing mass. It carries part of the bending through compatible deformation with the skin, rather than adding only CAD geometry or mass.

30% chord is near the thick part of the analytical profile, making a larger and more efficient tube possible. Position also affects clearance, mass CG, load introduction, and torsional eccentricity. It is therefore an analysis input, not just a CAD placement. The model's shear center remains a separate unverified 35%-chord assumption, with 25/35/45%-chord sensitivity cases; the spar center is not automatically the shear center.

## Material data and sources

Ravago **XPS X H LB TDS Version 5, 2025-05-09** gives:

| Property | Model input | Qualification |
|---|---:|---|
| Density | 32 kg/m³ | Typical; earlier sheets list 33 |
| Shear modulus | 8 MPa | Typical, depends on in-plane direction |
| Shear strength | 0.250 MPa | Further multiplied by 0.70 screening knockdown |
| Compression | 0.300 MPa | At 10% deformation; stored for reference, **not used as an elastic allowable** |

Primary manufacturer document hosted by distributor: [Ravago TDS v5](https://www.specifiedby.com/panel-systems-ltd/ravatherm-xps-sheets/ravatherm-xps-x-h-lb-tds-version-5-20250509_2cab80de.pdf). [Earlier Ravago TDS via Proctor](https://files.proctorgroup.com/assets/datasheets/proctors-ravatherm-datasheet.pdf) lists 33 kg/m³. Neither is a qualified aerospace allowable. Confirm the supplied grade, batch, orientation and bonding process.

[Easy Composites roll-wrapped tube construction](https://www.easycomposites.co.uk/12mm-10mm-woven-finish-carbon-fibre-tube) illustrates axial and circumferential reinforcement; [their tube manufacturing tutorial](https://www.easycomposites.co.uk/learning/how-to-make-a-roll-wrapped-carbon-fibre-tube) describes mandrel-based fabrication. Neither validates this proposed tapered tube or its assumed properties. Local hoop reinforcement, ovalization, crushing at clamps, and ply drops remain design tasks.

The 0.33 mm wing skin is modeled as an equivalent symmetric [0/45/0] woven laminate with three 0.110 mm layers. Its areal mass is scaled from the original cured-cloth mass/thickness ratio (about 0.536 kg/m²). This is a target cured thickness, not a claim that a particular cloth schedule achieves it. Tail laminate is unchanged. Fuselage mass retains its inherited density assumption (1850 kg/m³).

## Calculation method

For each tube section, with `d = D - 2t`:

- `A = pi (D² - d²) / 4`
- `I = pi (D⁴ - d⁴) / 64`
- `z_NA = sum(E A z) / sum(E A)` for skin and tube.
- `EI_total = sum[E (I_centroid + A (z - z_NA)²)]`.
- Skin stress uses `E_skin × curvature × distance from combined neutral axis`.
- Tube extreme-fiber stress uses the same curvature and its extreme distance from the combined neutral axis, checked at ultimate load.
- Tube mass integrates `rho A ds` along both swept half-wing centerlines.

Minimum calculated skin-to-bond-envelope clearance is only **0.152 mm**, before manufacturing tolerances. This is a tight analytical fit and must be redesigned if actual CAD, tube tolerances or bond requirements demand more clearance.

The circular envelope plus a 0.1 mm nominal annular bond layer is checked against the analytical airfoil at every beam station, with 0.33 mm skin clearance. The hollow tube envelope displaces foam; the mass calculation removes that foam and adds the tube and bond mass, with their own x centroids. The inherited 10% local-hardware allowance and 0.2 kg unallocated reserve remain; they are not designed joint masses.

Beam bending uses skin plus tube EI, with an approximate swept-path correction. A path/span ratio r gives effective EI/r³, shear stiffness/r and torsional stiffness/r; the stress bending moment is scaled by r. This is an uncoupled beam approximation, not a complete swept-wing bending/torsion model. Core axial EI is omitted. No tube torsion or transverse shear stiffness credit is taken; the original closed-skin torsion calculation is retained and the full shear envelope is conservatively checked against the remaining foam. Bond compliance, local transfer, torsional shear redistribution and warping are unresolved.

Loads retain +3g limit, -1.5g negative screen, 1.5 ultimate multiplier, 10% wing-force allowance, assumed Cm=-0.1, static 40 N VTOL and separate front/rear motor load cases. Tail uses the retained panel-normal load model. The spar affects stiffness, strength, mass, CG and aircraft sizing loads.

## Numerical results

| Result | Selected configuration |
|---|---:|
| Known modeled aircraft mass (incomplete) | 3.262 kg |
| Sizing mass including 0.200 kg reserve | 3.462 kg |
| Tube pair / bond / removed foam | 91.0 / 5.94 / 4.59 g |
| +3g case tip deflection | 23.87 mm |
| 70% stiffness tip deflection | 34.10 mm |
| Proposed deflection limit | 35.00 mm |
| +3g case tip twist | -1.44° |
| Ultimate skin failure index | 0.293 |
| Ultimate core shear utilization | 0.695 |
| Ultimate spar bending utilization | 0.426 |
| 40 N VTOL thrust / sizing weight | 1.178 |

All six modeled cases pass their numerical screens. The reduced-stiffness deflection margin is only about 0.9 mm; do not describe this as a robustly validated design. The thrust ratio remains below the model's proposed 1.5 target. No whole-aircraft maximum load factor or structural approval is inferred from these checks.

Finite trade examples, all with 0.33 mm wing/fuselage skin and recalculated mass:

| Candidate | Tube pair | Nominal tip | 70% stiffness tip | Reduced-stiffness screen |
|---|---:|---:|---:|---|
| No spar | 0 g | 58.53 mm | 83.62 mm | Fail |
| CFRP constant 8 mm OD, 1 mm wall | 50.0 g | 46.27 mm | 66.09 mm | Fail |
| CFRP 14→8 mm OD, 0.75 mm wall | 54.9 g | 31.14 mm | 44.48 mm | Fail |
| CFRP 14→8 mm OD, 1.75→0.5 mm wall | 82.9 g | 24.78 mm | 35.40 mm | Fail |
| **Selected CFRP 14→8 mm OD, 2→0.5 mm wall** | **91.0 g** | **23.87 mm** | **34.10 mm** | **Pass** |
| GFRP, same selected geometry | 105.3 g | 37.96 mm | 54.24 mm | Fail |

This is a finite screening study, not a global minimum-mass optimum. A better actual profile, validated laminate, different limits or a box/cap spar could change the choice.

## Critical remaining work

The repository CAD audit found the actual wing profile differs from analytical SD7037 (about 12.3% projected thickness versus about 9.2%). **Analytical fit does not establish actual CAD fit.** Import the actual profile and confirm chord definitions before freezing dimensions. Do not assume the thicker measured section automatically validates the complete layout.

Design and verify the swept center carry-through, spar-to-skin/core attachment, arm load introduction, adhesive peel, skin wrinkling, tube local buckling/ovalization and ply transitions. Fuselage strength/core, pusher and tail load paths, gusts, landing and aeroelasticity remain unresolved. The 0.33 mm fuselage change updates its modeled mass, not its unmodeled strength. Coupon and representative structural testing are needed before construction approval.

## Reproduce

```powershell
python RescU_Structures_V3_Ravatherm.py
python -m unittest test_v3 test_v3_ravatherm -v
```

Outputs: `results/v3_ravatherm/report.txt`, `screening.json`, `load_cases.csv`, `mass_components.csv`, `wing_candidates.csv` (spar trade), and `sensitivity.csv`. Use `--output PATH` for another destination. Standard library only, Python 3.10+.

Validation covers the existing analytical beam/laminate tests, exact annulus properties, independent uniform-tube mass/CG, transformed neutral axis, foam displacement, invalid fit rejection, no-spar recovery, baseline isolation, mass accounting and 200/400-station convergence.
