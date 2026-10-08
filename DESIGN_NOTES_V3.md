# RescU foam-core / GFRP preliminary candidate

**CAD audit update, 2026-10-08:** Current Assembly 2 has a 30-degree V-tail (code: 35 degrees), and the extracted wing profile differs materially from SD7037. Earlier V3 sizing results and skin/core schedules are not validated for this CAD. Read [the measurement audit](CAD_MEASUREMENT_AUDIT.md) before using those results. Analysis inputs remain unchanged pending resolution of profile, chord, area and attachment definitions.

Engineering screening dated 2026-10-07. This is a reproducible candidate for CAD refinement and testing, not an established flightworthy design. V2 is retained unchanged. V3 removes internal wing spars, wing ribs and the aft CFRP spine from the candidate's accounted structure. External CFRP motor arms and the aluminum payload plate remain.

## Proposed wing and tail construction

**Wing:** full-profile Divinycell H60 structural foam, continuously bonded to five plies of 163 g/m² woven E-glass/epoxy on each face. Stack from exterior toward core: **[0, 0, 45, 0, 0]**. Nominal cured thickness **0.895 mm per face**, not combined upper/lower thickness.

**Each V-tail panel:** full-profile H60 foam and three plies of 80 g/m² woven E-glass/epoxy on each face: **[0, 45, 0]**, nominal cured thickness **0.264 mm per face**. This schedule assumes an intact panel; actual ruddervator hinge gaps and servo pockets must be modeled before accepting it.

For the wing, 0 degrees places the cloth warp along the spanwise beam direction; for the tail, along the panel span. Woven cloth also has weft fibers perpendicular to warp: a 0-degree cloth contributes 0/90 fibers, and a 45-degree cloth contributes +45/-45 fibers. These are **woven ply schedules**, not unidirectional tape schedules. The span-aligned plies support bending; the bias ply improves torsional shear stiffness. Symmetric stacks avoid laminate membrane/bending coupling in the idealized model. Actual cloth warp/weft counts differ slightly; equal properties are a screening approximation.

These thicknesses use the supplier's calculated hand-layup values at 35% fiber volume. Cure quality, resin uptake, overlaps and compaction change actual thickness and mass. Do not substitute fabric or bare glass-fiber tensile strength for cured laminate strength. Reference resin candidate: **Gurit Ampreg 31 with a compatible Ampreg 3X hardener**, using the current manufacturer's processing instructions. Its published support for wet layup and vacuum bagging is relevant; its resin/other-laminate properties are not allowables for these cloth stacks. Hardener speed and cure schedule remain manufacturing choices to verify on coupons with the actual foam, equipment and available time. No purchase has been made.

**Fuselage:** retain the current **0.40 mm GFRP exterior assumption**. No final fuselage ply schedule or foam thickness is selected yet: surface area and length cannot establish shell stability or tail/pusher load transfer. The removed aft spine is not secretly credited. Aft shell analysis and its replacement load path are explicit unresolved gates. See [CAD request](CAD_REQUEST_V3.md).

## Why H60, and why five wing plies?

H60 is the baseline because it supplies documented structural core properties at relatively low density and the manufacturer's product family supports low water absorption and machining. It is a reasonable candidate for the maritime mission; this does not establish durability of unsealed joints or suitability of a particular manufactured wing. Use structural foam with traceable grade and sheet orientation, not a generic density-only foam entry.

The model uses Diab Rev19 minimum shear modulus and strength: H60 density 60 kg/m³, shear modulus 16 MPa, shear strength 0.63 MPa, and through-sheet compression strength 0.70 MPa. H80 uses 80 kg/m³, 23 MPa, 0.95 MPa and 1.15 MPa. These are room-temperature data from a dated manufacturer sheet; obtain the current supplied-grade specification before procurement. A separate assumed 0.70 strength factor screens process/environment uncertainty. It is not a statistically qualified hot/wet allowable. Compression properties are recorded for future attachment work, not treated as proof that mounts will resist crushing.

Eight uniform wing candidates were compared, re-calculating aircraft sizing mass for each. Using the reduced-stiffness check, H60 wing deflections are approximately:

- Three 163 gsm plies [0,45,0], 0.537 mm: **50.4 mm**.
- Four [0,45,45,0], 0.716 mm: **44.3 mm**.
- Five [0,0,45,0,0], 0.895 mm: **34.5 mm**.
- Six [0,0,45,45,0,0], 1.074 mm: **32.9 mm**.

The proposed preliminary screen is 5% of the 0.700 m half-span, or 35 mm, plus 2 degrees tip twist at limit load. These are engineering screening criteria, not approved team requirements. Five plies are the lightest tested stack that meets both nominal and 30%-reduced stiffness checks. Margin against 35 mm is small; further load/property changes can reject this choice. Six plies add approximately 117 g to the wing for limited extra bending benefit. Other fabrics, mixed stacks or localized reinforcement have not been optimized.

H80 lowers five-ply reduced-stiffness deflection to about 33.8 mm, adding about 24 g of wing core mass. It improves core shear margin but does not resolve the main skin-bending or propulsion-budget constraints. Local H80 or denser inserts may be useful at mounts only after the load path and contact geometry are known. There is no direct evidence here that another similar UAV's foam grade validates this RescU construction.

## Model and property assumptions

Wing geometry remains span 1.400 m, root/tip chords 0.165/0.100 m, tip leading-edge offset 0.140 m, SD7037. Total planform area is 0.1855 m². Each tail panel remains span 0.245 m, chords 0.090/0.045 m, leading-edge offset 0.120 m and NACA 0010. Total tail panel area is 0.033075 m². The tail load is panel-normal, not a vertical force derived from projected horizontal area.

Published UIUC SD7037 coordinates provide a preliminary profile. The NACA 0010 equation uses a closed trailing edge; confirm both against CAD. Chordwise integration subtracts approximate normally offset skins from the external profile; overlapping offsets at thin edges are clipped. This is not an exact CAD shell. Foam volume is full core volume after skin subtraction, without crediting unknown pockets or hollow areas. Surface mass includes a 10% margin for omitted sweep surface effects/end caps and an additional assumed 100 g/m² for core sealing/bond resin/finish. Core orientation must match the supplier's tested directions.

Plane-stress laminate extensional stiffness is transformed by ply angle; ply stresses are recovered under combined axial bending and skin torsion. The cured woven-ply constants are **assumptions**: E1=E2=15 GPa, G12=3 GPa, nu12=0.15; tensile/compressive/in-plane shear strengths 150/100/30 MPa, each reduced by 0.70. These have not been measured for the selected cloth/resin. The 15 GPa modulus is a restrained initial value for the modest fiber fraction and woven fiber split, not a published material guarantee. Sensitivity scales structural elastic stiffness to 70%; strengths remain separate assumptions.

Beam EI credits the skins only, avoiding unsupported core axial-isotropy assumptions. Cantilever equilibrium includes elliptical wing lift, bending and core shear deflection. Core shear uses assumed k=0.5 and a peak 2V/A envelope. Closed-skin torsion uses the Bredt-Batho single-cell model; foam torsional stiffness is not credited. The root is ideally clamped. Connection rotation, sweep/warping, composite shear coupling, detailed local stresses and joint flexibility are not resolved. Actual root compliance can increase deflection.

Loads include provisional +3g limit/+4.5g ultimate, assumed -1.5g limit with 1.5 ultimate multiplier, a 10% wing force allowance, and an assumed Cm=-0.10 aerodynamic pitching moment at 44.6 m/s. This pitching-moment bound requires aerodynamics confirmation. VTOL uses the team's 40 N total thrust, two motors per side and front-only/rear-only cases, with the existing 1.5 structural factor. Tail load uses assumed panel-normal CL=0.5 at 44.6 m/s, multiplied by 1.5 for ultimate. Negative tail loads on the symmetric intact section have equivalent extrema; actual combined pitch/yaw and hinge loads remain unverified.

## Current calculated results and mission conflict

Under the selected five-ply H60 candidate:

- Wing +3g limit tip deflection **24.14 mm**, tip twist **0.68 degrees** in magnitude. With reduced stiffness and shear center varied from 25% to 45% chord, maxima are **34.49 mm** and **1.29 degrees**.
- Ultimate global maximum face stress **27.56 MPa**, maximum ply stress utilization **0.418**, core shear utilization **0.291**. Utilization <=1 passes the stated assumed material screen, not every failure mode.
- Tail limit tip deflection **3.89 mm** under the stated assumed tail load.
- Six load cases pass the four computed screens: ply maximum stress, core shear, limit deflection and limit twist. **Overall aircraft status remains UNRESOLVED.**

Accounted aircraft mass is **3.400 kg**, a lower bound because actual fuselage foam and connection construction are unknown. A separate provisional **0.200 kg** reserve produces **3.600 kg** load sizing mass. This is not a complete takeoff mass. A sensitivity with +20% cured skin areal mass and +10% foam density raises the sizing mass to **3.748 kg**; the reserve is not a validated uncertainty allowance.

At 3.600 kg, 40 N total VTOL thrust gives **thrust/weight=1.133**. The old 2.669 kg team target and propulsion budget are inconsistent with this uniformly reinforced sparless candidate. A proposed 1.5 thrust/weight screen would require about **53.0 N**, or mass <=2.72 kg at 40 N. That ratio is an engineering comparison, not a regulatory requirement. This model does not validate end-of-battery thrust, control authority, endurance or transition. A stronger propulsion option would also require updating motor loads and masses. Do not release the current candidate for manufacture/flight until the team resolves this conflict.

Provisional battery centre is x=0.248 m from the nose using accounted components alone. Missing masses and actual compartment fit can change it; it is not a finalized CG or battery installation.

## What validation has and has not been done

Seventeen automated checks cover independent uniform-load and point-load beam solutions, shear deflection and torsion integration, rectangular area/inertia and closed-tube torsion, isotropic laminate rotation, woven orientation behavior, profile closure, section/span mesh convergence, load linearity, and removal of old member mass. These verify the numerical implementation. They do not measure materials or validate the aircraft.

NASA's wrinkling survey explains that orthotropic laminate wrinkling requires laminate **bending** stiffness and applicable core/facesheet assumptions. V3 deliberately does not claim a wrinkling pass by inserting extensional effective modulus into an isotropic formula. Skin wrinkling, local buckling, debond/peel, inserts/crushing/pull-out, control-surface interruptions, aft shell, gust/landing cases and aeroelasticity remain unresolved.

Next validation sequence:

1. Import/reconcile CAD and actual mass budget; decide with the team whether the no-spar constraint and existing propulsion can coexist. Locate joints, voids and hinge gaps before optimizing the skin schedule further.
2. Make representative glass/epoxy and skin/core coupons using the intended process. Measure cured mass/thickness, stiffness and tensile/compressive/shear properties; assess core bond/peel and relevant hot/wet exposure. Replace assumptions with appropriately conservative test-based values.
3. Analyze roots, motor supports, tail/pusher attachments, shell stability and representative local panels with detailed CAD and laminate bending stiffness. Check manufacturing temperature and vacuum compatibility with supplied core.
4. Agree the maneuver/gust/VTOL/landing envelope and stiffness limits with the faculty lead. Re-run sizing and propulsion/endurance/CG checks.
5. Conduct a faculty-reviewed representative wing/tail and attachment ground-test program with distributed bending and torsion loads, measured deflections, and inspections for damage. Ultimate tests may damage the specimen; use an agreed sacrificial test article and test plan, not an improvised load on the flight aircraft.

## Primary sources reviewed

- [R&G 163 gsm Interglas 92110](https://www.r-g.de/en/art/190120/): cloth construction; 0.179 mm and 291 g/m² calculated cured ply at 35% fiber volume. No exact finished-part strength approval.
- [R&G 80 gsm woven cloth](https://www.r-g.de/en/art/190110): 0.088 mm and 143 g/m² calculated cured ply at 35% fiber volume.
- [Diab Divinycell H product information](https://www.diabgroup.com/products-services/divinycell-pvc/divinycell-h/) and [Rev19 minimum-property sheet](https://www.diabgroup.com/media/mfamadrz/diab-divinycell-h-june-2020-rev19-si-cn.pdf): grade properties and manufacturing/environment context. The available numerical sheet is in Chinese; units/minimum rows were checked.
- [Diab sandwich guide](https://www.diabgroup.com/media/q5yldbe4/diab-guideline-to-core-and-sandwich.pdf): skin/core/bond roles and preference for minimum properties; not a finished-wing design method.
- [UIUC SD7037 coordinates](https://m-selig.ae.illinois.edu/ads/coord/sd7037.dat) and [NASA TM-4741](https://ntrs.nasa.gov/api/citations/19970008124/downloads/19970008124.pdf): profile references.
- [Gurit Ampreg range](https://www.gurit.com/ampreg-2/): candidate wet-laminating epoxy and processing context. Verify current product/hardener instructions before use.
- [NASA/CR-1999-208994, Facesheet Wrinkling in Sandwich Structures](https://ntrs.nasa.gov/citations/19990017863): failure-mode applicability and why a simplistic isotropic wrinkling pass is insufficient.

Reproduce with `python RescU_Structures_V3.py` and `python -m unittest test_v3 -v` in the repository. Generated numerical data are in `results/v3/`; these notes record the reviewed candidate and should be updated when assumptions change.
