# P05 motor-arm construction and assembly sequence

Status: detailed review candidate. Mount dimensions are proposed. Motor dimensions come from the linked supplier page and user-supplied dimensional drawing. Neither establishes as-built tolerances beyond those shown, motor screw insertion limits, mounting torque or material/joint allowables.

## Assembly structure

The native document contains a real FreeCAD 1.1 Assembly root with two motor-arm subassemblies. Each arm has one grounded CFRP tube, two separately installed UM2807 motors, two removable clamp mounts, wing saddles and individually separated wing rib solids. Each physical item has its own object and fixed installation joint. These fixed joints represent the installed condition; internal rotor motion is not modeled. Datum connectors avoid dependence on transient generated face numbers. Geometry is reproducible from the build script; the new parts are static boundary representations, not sketch/pad feature histories.

The P04 front saddle contained three disconnected solids. These are now three separately identified pieces: the saddle and two wing rib blanks. Separating them does not establish a qualified rib-to-saddle bond or spar connection. The arm-side saddle top/bottom contact now has explicit 0.2 mm epoxy pockets. Existing side gaps are not treated as bonded area. The wider wing/spar/core interface remains a P04 review item.

## Motor interface

- Motor: Unusual Machines UM2807 1700KV, MPN ENT-UMAC-2807-1700.
- Nominal body diameter 35.4 mm, drawing tolerance ±0.5 mm. Maximum-diameter clearance gauge is 35.9 mm.
- Body length 20 mm, drawing tolerance ±0.1 mm; overall length 33.5 mm. Nominal body and shaft are envelopes rather than detailed rotor/stator CAD.
- Shaft diameter 5 mm, M5×0.8 exposed thread, 9.5 mm threaded portion on the supplied drawing. The 4 mm difference between exposed length13.5 and thread9.5 is used as a provisional prop seat station. Hub, nut and washer stack remain unselected.
- Four M3×0.5 holes on a 19 mm pitch-circle diameter. The mount rotates that pattern45°: hole coordinates ±6.717514 mm in each plate axis. Adjacent-hole distance is13.435029 mm. A19×19 square is incorrect.
- Proposed plate holes are Ø3.4 mm clearance. These are design allowances, not motor drawing tolerances.
- Proposed M3×6 motor screws with a0.5 mm washer and3 mm plate give2.5 mm insertion beyond the motor mounting face. This insertion is **unverified**. The modeled thread-major-diameter recess is an engagement gauge only. Obtain allowable insertion depth/torque or inspect the actual motor before choosing screw length; prevent winding contact and bottoming.
- The base diameter25.5 and base length3 mm are transcribed from the user drawing. Wire exit, underside shaft/clip protrusion, actual screw heads, bearing clearance and internal winding geometry remain unverified.

Supplier link: https://irlock.com/products/unusual-machines-um2807-1700kv-motor

## Mount construction

Each motor mount uses a flat glass/epoxy plate with a44 mm circular center and20 mm wide ears extending toY±30 mm. Thickness3 mm is proposed. Two external M3 clearance holes at(0,±24) take the arm clamp screws. The motor pattern andØ10 center relief are machined into the same plate. G10/glass-epoxy density1850 kg/m³ is assumed; grade, fiber orientation, temperature rating, wet strength and fatigue properties must be selected.

Two28×4×7.6 mm glass-epoxy rails support the plate, with0.2 mm adhesive between rail tops and plate and0.2 mm isolation liners on the carbon contact surfaces. The rails fit within the carbon tube's30 mm width. Their28 mm length fits the15 mm motor-axis distance from each tube end. The lower strap is24×60×4 mm with3 mm corner radii and a0.2 mm liner. All liners are modeled at an assumed1200 kg/m³; actual material must resist creep, moisture and operating temperature.

The proposed two M3×45 clamp screws sit outside the tube, atY±24 mm. Washers spread bearing load into the glass plate; locknuts retain the lower strap. No holes are drilled through the1 mm carbon walls. Hardware is represented with simplified threads/heads and assumed steel density, not verified catalog masses. Deburr/radius machined edges and seal exposed laminate edges; cutting processes need appropriate dust control.

The rails are bonded to the plate on a flat fixture. Their adhesive pocket has an explicit0.2 mm layer; fillet and process excess have a separate budget. The lower strap stays removable. No permanent adhesive between the removable mount and carbon arm is credited. This is a reviewable fabrication concept, pending clamp and fatigue tests.

## Load path and preliminary checks

Thrust travels through the motor screws into the upper plate, then the external clamp screws/lower strap into the carbon tube. The rails keep the assembly aligned and distribute compression. Motor torque travels from the four motor bolts into the plate, then through friction at the lined upper/lower tube contacts. The clamp has no positive axial key, so vibration and slip tests are necessary. Wing saddles transfer arm bending and reversed support reactions into the wing; the rib/skin/spar joint still needs detailed development.

The check sheet uses the inherited hypothetical17.3 N per motor ×1.5 =25.95 N axial demand. The torque screen uses Q≈60/(2πKV)×62 A≈0.348 N·m. This treats the supplier's62 A/3 s limit as a torque scenario; controller phase-current conventions, acceleration torque and the real prop operating point are unknown. It is not a verified torque rating or continuous operating point.

Screw loads are evaluated on the19 mm bolt circle. Plate strip bending, rail bond averages, clamp preload/friction, carbon contact pressure and saddle bond averages are preliminary screens. G10 strengths, friction coefficient, preload and CFRP compression allowables are assumptions. Geometry constraints and interference checks do not validate these physical load paths.

## Installation and service

1. Machine the plates/rails and verify hole locations, flatness and fit against a motor sample. Verify safe motor screw length before assembly.
2. Bond the two rails under each upper plate with controlled bondline thickness; cure using the selected adhesive process. Fit isolation liners.
3. On the bench, insert the four motor screws and washers from beneath the plate, locate the motor, and tighten using a motor-approved method. The tube blocks straight driver access after clamping; this is an intentional installation sequence.
4. Place the motor/plate unit on the undrilled carbon arm atX235 or555 mm, align the lower strap and insert the two external clamp bolts. Set preload by a validated procedure, not a guessed torque. Record torque/preload only after laminate crush and slip tests.
5. Route all three motor wires inward toward the wing/ESC, protect edges and add strain relief. The CAD route is a2.2 mm wire envelope with assumed exit/bend geometry, and represents only part of the supplied200 mm lead length. Wire mass remains within each52 g motor allowance. Connector, clip and route-excess budgets are separate only where explicitly stated in the ledger.
6. Check propeller, hub, locknut and tool clearances using the selected physical parts. The254 mm sweep is inherited10-inch packaging, not propulsion approval. Remove propellers for motor servicing.
7. To remove a motor, undo the external clamp hardware and lift the motor/plate unit from the tube before accessing its four motor screws. Clamp tool envelopes are evaluated separately from the bench-only motor screwdriver envelopes.

## System decision that remains open

The supplied1700KV listing specifies3S–5S and21.0 V maximum. Existing aircraft inputs use6S:21.6 V nominal and25.2 V full. Direct connection exceeds the listed maximum. The motor, supply architecture or battery choice must be resolved before operation; changing cell count also changes packaging, mass and propulsion performance. This study retains the battery budget solely for mass comparison and does not silently choose a replacement motor.

The initial5 mm rail width collided slightly with the motor washers. Final4 mm rails leave0.782 mm nominal radial washer-to-rail clearance; combined fabrication and hardware tolerances must stay below this margin. Motor screws are excluded from the external rotating-bell distance because their engagement lies inside the motor envelope; winding/rotor screw-tip clearance remains unverified.

The final upper plate is3 mm and lower strap4 mm thick. A proposed100 N nominal/150 N maximum preload per clamp screw is a screening assumption, not an installation specification. At the150 N maximum, simple cantilever-strip screens give55 MPa in the upper plate and38.7 MPa in the lower strap against an assumed70 MPa bending value. Upper/lower lever arms are11/16.5 mm, effective widths20/24 mm. No tightening torque is prescribed because preload scatter and carbon tube crushing are unqualified.
