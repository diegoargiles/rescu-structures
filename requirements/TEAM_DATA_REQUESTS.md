# RescU inputs needed from subsystem leads

Prepared for Diego; not sent to anyone. Values may be provisional if their source and confidence are included.

| Lead / subsystem | Please provide | Why structures needs it |
|---|---|---|
| Matthew — Propulsion | Final lift prop choice (9 or 10 inch); motor/ESC model; resolved supply voltage; thrust, RPM, current and shaft power/torque versus throttle; CW/CCW assignment; motor/prop/ESC masses and mounting drawings | Actual thrust and torque cases, prop clearance, vibration frequencies, electrical compatibility and motor attachments |
| Raphael — Aerodynamics | Current wing area/profile; cruise, transition and maximum speeds; CLmax; spanwise lift distribution; pitching moment Cm and reference point; preliminary prop/wing interaction guidance | Lift and torsional load distributions, V-n envelope inputs, clearance/layout trade |
| Mooneeza — Stability & Control | Intended maximum bank and maneuver accelerations; transition sequence; permissible front/rear thrust differential; thrust reserve/control limits; acceptable elastic wing twist or a sensitivity study; CG range | Demand envelope, asymmetric thrust, control authority and stiffness acceptance |
| Luis — Weights & Performance | Reconciled current mass table with XYZ locations; sizing mass and reserve; complete battery/harness mass; speed/altitude/density mission envelope; landing/handling assumptions with team | Inertial loads, hover trim, performance constraints, total mass/CG |
| Owen — Geometry & Simulations | Authoritative geometry/datums, wing 0 degree and V-tail 35 degree definitions; motor/prop CAD, prop plane and blade envelope; landing clearances; agreed SolidWorks/FreeCAD workflow | Geometry fidelity, clearances, import/reference alignment and simulations |
| Diego — Structures, with faculty review | Available tube/cloth/resin/adhesive, layup/process, actual cured thickness/density, bond preparation, allowables/test coupons; propose and justify limit/ultimate and deflection criteria | Stiffness, failure modes, manufacturing repeatability and acceptance |

## First requests (do not wait for every detail to start CAD)

1. Propulsion: propeller diameter, supply voltage, thrust/RPM table and installation dimensions.
2. Weights/Performance: current sizing mass and major component locations.
3. Controls + Aerodynamics: maneuver/bank limits, maximum speed and starting lift/Cm information.

Important integration item already recorded in component notes: AT2814 1200KV is listed for 3–4S while the battery is 6S2P. Propulsion must resolve the actual supply architecture before treating any thrust table as representative. The selected ESC voltage rating does not resolve the motor voltage issue.

## Suggested message Diego can send

“I'm updating the wing reinforcement, VTOL arms/mounts, and fuselage connections. I can run the structural calculations, but need each subsystem's current inputs. Please send your items from the table with units, configuration, and whether each is measured, calculated, or assumed. Preliminary estimates are okay if labeled. My first priorities are the final prop size/voltage/thrust data, current sizing mass/CG, and intended maneuver/speed limits.”
