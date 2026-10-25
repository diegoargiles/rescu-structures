# P06 rib-to-saddle connection candidate

The P05 arm-side saddles and two rib blanks were geometrically separated. Measured native CAD minimum gaps on the positive-Y arm were0.997/1.454 mm at the front saddle and2.964/3.336 mm at the rear saddle. These are saved-design geometry measurements, not measurements of manufactured parts.

## Proposed construction

Each rib receives one flat external glass/epoxy splice plate at each saddle station: four plates per arm, eight for the pair. Each plate overlaps the outside saddle wall and the outside rib face above it. Proposed plate thickness is2.0 mm at the spar/front station and1.5 mm at the rear station and chordwise overlap width24 mm. The lower overlap runs fromZ−18 toZ+1 mm. Front plates reachZ14 mm; rear plates reachZ10 mm. The plates bridge the open vertical space between rib and saddle. They do not rely on the rib's bottom edge touching the saddle.

The rib outer face sits2 mm inward from the saddle outer face. A proposed1.8 mm glass/epoxy packer plus0.2 mm adhesive aligns those faces. Another0.2 mm adhesive layer connects the packer to the plate. The plate-to-saddle adhesive is also0.2 mm nominal. Existing P05 saddle-to-arm bondlines are retained.

Packers follow the actual saved rib face within each station. If the spar relief divides a packer into disconnected islands, each island is modeled and counted as a separate cut piece. The front plates, packers and bondlines are relieved against the filled **native conical spar outside surface plus0.4 mm**. This is clearance for future assembly, not a designed spar bearing or attachment. No spar wall is removed.

The upper bonded profile is derived from the native rib face shifted down0.3 mm to leave an upper-edge installation margin. It is checked against the native wing skin and spar. The shift and clearances are proposed design allowances; manufacturing tolerances and actual bond quality remain unverified.

## Wing entry slots

The new continuous plate must enter the wing from the external saddle below it. Explicit local lower-skin/foam relief slots are included as a separate proposed wing-interface revision. Those openings are shown in revised wing context solids and their removed material is reconciled in the aircraft mass ledger. Both the original intersections and the post-relief checks are retained.

These slots interrupt local skin material. Their edge reinforcement, sealing, skin shear redistribution and connection to the ribs/spar must be developed with the wing group. No strength credit is taken for a future doubler. The geometry is a review candidate, not a release to cut a wing. The current arm-group design establishes where the wing needs to accommodate the carrier.

## Load path and checks

Thrust and reversed arm support reactions pass through the arm-to-saddle bond, saddle walls, plate-to-saddle lap, splice plate, packer bonds and rib. The subsequent rib-to-spar/skin transfer remains a wing-group task.

Joint calculations use the inherited hypothetical17.3 N per motor multiplied by1.5. Front-only and rear-only cases reverse support reactions; the largest station reaction is about96.15 N. A nominal50/50 split between ribs and a conservative100% of station reaction applied to one splice are both shown. These are load-sharing assumptions, not results from a detailed shell/joint model.

Bond areas are derived from generated adhesive volumes divided by the0.2 mm thickness, with actual contact areas and gaps also checked at both adherends. A50% effective-area factor and2 MPa bond shear value are preliminary assumptions. Local end shear, peel, adherend flexibility, laminate interlaminar failure and fatigue are not represented by the average-shear screen.

The flat lap is eccentric. Plate bending includes a sampled reduced net width through the front spar relief; all station load is conservatively applied to one splice as a separate case. Plate bending and a simple linear adhesive peel-demand proxy are reported explicitly. No qualified peel allowable is available, so the connection is **not strength-qualified**, even if average shear and plate-strip stresses are below assumed values. Coupon/subassembly tests and refined analysis are required before assigning a capacity.

Glass density1850 kg/m³, epoxy density1200 kg/m³ and70 MPa plate bending strength are inherited screening assumptions. They do not specify a purchased laminate/adhesive or qualified wet/hot allowables.

## Fabrication and assembly order

1. Dry-fit both saddles on the actual undrilled carbon arm at the existing stations. Use a fixture to hold arm and rib alignment. Current concept is a permanently bonded arm carrier.
2. Produce flat splice plates and fitted packer blanks from the selected glass/epoxy laminate. Confirm actual sheet thickness; target the2.0 mm packer-plus-inner-bond stack rather than assuming stock sheet is exactly1.8 mm. Deburr, radius and seal exposed edges. Match the spar-relief templates to the actual spar with the planned clearance.
3. Prepare cured laminate surfaces using the selected adhesive manufacturer's instructions. Establish a controlled bondline and process inspection method. Do not sand through the arm's thin structural fibers.
4. Bond saddles to the arm using the retained P05 interface. Bond packers and splice plates in the fixture. Inspect both ends of each overlap before closing the wing. The accessible external faces permit temporary clamping; they are not permanent fastener locations.
5. Dry-fit the carrier into the proposed wing slots before skin closure or final skin bonding. Confirm clearance around the actual tapered spar. Resolve slot-edge reinforcement and rib-to-spar/skin connections with the wing assembly before closing that structure.
6. Cure, inspect and weigh the assembly. Test representative bond/plate/carbon interfaces under positive, reversed and cyclic loads. Establish repair and replacement procedures for this bonded carrier.

General process reference: [WEST SYSTEM bonding and clamping](https://www.westsystem.com/instruction/epoxy-basics/bonding-and-clamping/) describes surface preparation, avoiding adhesive-starved joints, fillets and overlap. It does not provide aircraft-specific allowables or qualify this selected construction. Final adhesive choice, cure, surface preparation and environmental limits remain to be specified.

## Mass allocation

New glass pieces are explicit solid volumes. New adhesive solid mass is moved out of the remaining P05 saddle/rib adhesive budget, so it is not counted twice. The200 g sizing reserve remains separate. Foam credit is accepted only after checking removed-volume conservation. No skin mass credit is accepted: the spline-skin Boolean quantities fail volume conservation even though the resulting shapes are valid. The full original skin budget is retained. Other P04 mass/fit uncertainty, the P05 motor fastener-depth limit and the21 V motor versus6S supply conflict retain their previous status.
