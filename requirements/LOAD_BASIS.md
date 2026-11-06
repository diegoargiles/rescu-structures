# Load basis — how we will determine the numbers

R13 is a geometry candidate. No accepted operating envelope has yet been demonstrated. Old V4/P03 defaults are retained only as comparison screens, not asserted team requirements.

## Flight load factor

n=L/(mg) for the chosen lift/normal-load definition. In a steady coordinated level turn, n=1/cos(bank): 30 deg -> 1.155, 45 deg -> 1.414, 60 deg -> 2.0. This is only one maneuver; it does not bound gusts, pull-ups, landing or transition. Aerodynamic capability at a speed is n_aero=q*S*CLmax/(mg), q=0.5*rho*V^2; intersect the aerodynamic envelope with commanded maneuver and structural limits. Wing lift also depends on tail force and other airframe loads. Develop positive/negative and gust cases with Aerodynamics/Controls/Performance; faculty reviews the proposed envelope.

Working comparison: +3 and -1.5 limit n, inherited from inputs.json. These are assumptions, not a computed safe capability. Ultimate load = 1.5 * limit load, once only. Do not multiply thrust by 1.5 and then apply another hidden 1.5 factor. Stiffness/service clearance is evaluated at limit/operating demand, with strength at the explicitly selected factored load.

## Thrust and torque

Symmetric hover T approximately mg/4 only for a level, symmetric idealization without download. Actual trim must balance forces and moments about the current CG. Cases: trim hover; all motors at confirmed maximum; front-only and rear-only local attachment envelopes; differential thrust chosen by Controls. Full-thrust static cases are structural demand cases, not claims of steady flight or motor-out controllability. Include mass/inertial relief consistently in the assembled model.

Qshaft=Pshaft/omega; omega=2*pi*RPM/60. Electrical VI is not shaft power without efficiency/loss information. Ask Propulsion for measured or matched-prop torque. Torque sign follows rotation direction. Do not multiply thrust by prop radius as a torque estimate. Gyroscopic moment needs rotor inertia, RPM and aircraft angular rates.

Wing torque about a chosen spanwise axis includes r cross F and aerodynamic pitching moment. For vertical thrust at a support/shear-center X, magnitude of its pitch/torsion contribution is abs((Xmotor-Xref)*T). Lowering the motor without moving X or Y does not reduce this vertical-thrust bending moment. Shear-center location must be derived or bounded, not silently fixed to an arbitrary chord fraction.

## Allowable displacement and twist

The old scripts use 5% half-span tip deflection and 2 deg twist as preliminary screens. They are NOT demonstrated aerodynamic limits. Final allowable movement must preserve prop/wing/ground clearances after blade flex, structure deflection, tolerances and assembly variability. Controls/Aerodynamics assess the effect of twist on lift, trim and authority. Structures supplies predicted twist/displacement versus load and stiffness uncertainty.

## Strength and safety factors

Margin of safety = allowable / factored demand - 1 for a compatible scalar failure mode. Composite laminate failure needs appropriate directional/ply criteria; generic von Mises stress is not sufficient. Separate bending, shear, torsion, local buckling/ovalization, pin/bolt bearing, pullout, crushing, adhesive shear/peel and fatigue/damage concerns. No margin is released until material/process allowables and the demand envelope are supported.

A 1.5 ultimate multiplier is an inherited project comparison convention pending faculty review, not proof of regulatory compliance and not a replacement for material knockdowns or representative tests. Keep uncertainty/stiffness sensitivity separate from the load factor.

## Evidence plan

Start with free-body diagrams and analytical beams; then a wing/arm/carry-through model with actual support locations. Verify force and moment balance, compare beam displacements and perform mesh convergence. Use explicit joint/contact definitions. Add local bond/bearing models where demand concentrates. Match simple representative ground tests to the analytical fixtures and loads. No flight-ready claim from a CAD interference pass.

References (engineering guidance, not a certification claim):
- FAA Pilot's Handbook, Chapter 5: https://www.faa.gov/sites/faa.gov/files/regulations_policies/handbooks_manuals/aviation/phak/07_phak_ch5.pdf
- FAA AC 20-107B with Change 1: https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_20-107B_with_change_1.pdf
- NASA bonded composite joint design: https://ntrs.nasa.gov/citations/19890016677
