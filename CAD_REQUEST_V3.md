# CAD information needed for RescU V3

The span and chords already exist in V2. The missing information is the detailed shape, construction, and attachment load paths. Area alone does not determine bending or torsional stiffness.

## First export: complete assembly

Send a STEP (.step/.stp) assembly with separately identifiable wing, left/right V-tail, fuselage, motor arms, attachment fittings, and equipment bodies. Include the native CAD assembly if convenient, with its dependent part files. Declare units and the coordinate origin. The current model uses x from nose toward tail, y across the wing, and z upward. An STL can help visualization but is insufficient for precise inner/outer surfaces and engineering dimensions.

Include a dimensioned drawing or PDF if the export loses component names. Identify which surfaces are the finished exterior and which are the machined foam. The core should be offset inward from the finished exterior to make room for the glass skin; adding glass to an unmodified full-size foam profile changes the aerodynamic shape.

## Wing and tail geometry

- Confirm wing span 1.400 m, root/tip chords 0.165/0.100 m, and tip leading-edge offset 0.140 m. Confirm whether span includes the fuselage and identify the actual root restraint station.
- Confirm each V-tail panel span 0.245 m, root/tip chords 0.090/0.045 m, leading-edge offset 0.120 m, and 35-degree dihedral. Confirm that 0.245 m is distance along the panel, not horizontal projection.
- Supply wing section curves at the root, motor-arm station y=0.265 m, mid-half-span y=0.350 m, and tip y=0.700 m. Supply tail sections at panel stations 0, 0.1225, and 0.245 m. Give extra sections at any discontinuity.
- Airfoil points can be .dat, CSV (x,z), DXF section curves, or curves in the STEP. State whether coordinates are normalized x/c,z/c or actual millimetres, and whether they describe the exterior or foam. Keep upper/lower curves and section closure identifiable.
- Show twist, incidence, dihedral, any profile changes and fillets. Confirm the wing really matches published SD7037 and the tail matches NACA 0010, including trailing-edge thickness.
- Show every aileron/ruddervator hinge line, control-surface chord/span, gap, hinge cutout, servo pocket, wire channel, access opening and hollow region. V3 currently treats the complete airfoil as an intact bonded closed section; a hinge gap can invalidate that assumption.
- Show leading/trailing-edge skin continuity, bond overlaps, panel seams and root/tip closure. Full-span continuous plies are assumed; butt joints are not analyzed.

## Attachments: highest priority for removing spars/spine

- Wing-to-fuselage and V-tail-to-fuselage connections: bonded contact areas, flange/overlap dimensions, bolt patterns/diameters, insert sizes/materials, local foam grades, skin doublers, adhesive thickness, and removable vs permanent joints.
- Motor-arm supports at x=0.313 and 0.448 m: actual contact footprint, clamp/bolt details, local skin/core thickness and how each reaction reaches the wing skins. Identify the motor-arm station and exact rotor coordinates.
- Tail root, pusher motor mount, battery restraint, payload/magnet plate, landing contacts and hinge attachments: the same dimensions and material details. Foam-only interior does not mean that bolts can be fastened directly into low-density foam without an engineered connection.
- Specify any acceptable local reinforced inserts or denser foam blocks. The present 10% hardware mass allowance is not a connection design.

## Fuselage: required to remove the aft spine responsibly

Supply exterior AND interior sections near x=0.220, 0.260, 0.313, 0.448, 0.570, 0.800, 0.960 and 1.110 m, plus sections where the shape changes. Give width, height, corner radii, shell thickness, foam thickness, local laminate changes and all hatches/cutouts. Show the continuous load path between tail, pusher mount and wing.

Identify occupied equipment volume, voids and which regions actually contain foam. A full solid fuselage cannot be assumed where batteries/electronics need space. The existing 0.257 m² surface area supports a shell mass estimate but cannot establish section stiffness, shell stability or foam volume.

## Mass and mission information outside CAD

- CAD volumes/centroids by material and actual hardware list, plus measured equipment masses and positions. Provide usable battery bay dimensions, not just the battery centre point.
- Selected cloth/resin products and manufacturing process; measured cured thickness, areal mass, fibre content and coupons. Confirm machining access for the chosen foam and material sheet orientation.
- Actual four-motor thrust curves at the flight battery voltage, including low-voltage/end-of-mission and temperature conditions; battery endurance and final takeoff mass target.
- Team-approved maneuver/gust envelope, vertical gust model, load distributions and airfoil pitching moments, tail forces in pitch/yaw, transition/asymmetric VTOL cases, landing/handling loads, flight life, and hot/wet operating conditions.

Start with the complete STEP assembly and attachment details. Published airfoil points already support preliminary wing/tail sections; exporting the actual sections establishes whether those assumptions match what will be built.
