# RescU structural validation — closure plan

Status at V4/P03: mass accounting and numerical verification have progressed; aircraft structural validity is unresolved. Close requirements individually with evidence and configuration identifiers. Do not turn a global flag to PASS solely because beam cases pass.

## Priority order

| Priority | Open item | Evidence needed to close it |
|---|---|---|
| 1 | Design loads and acceptance criteria | Team/faculty-reviewed maneuver, gust, transition, asymmetric VTOL, landing/handling loads; actual motor/prop/6S thrust data; agreed deflection/twist and limit/ultimate criteria |
| 2 | Wing center connection and arm hardpoints | Dimensioned spar joint, wing/fuselage interfaces, clamps/bolts/inserts, skin doublers, adhesive and local foam; traced load path and joint reactions; bearing, crushing, pull-out and peel checks |
| 3 | CAD and mass baseline | Native FreeCAD reopen/recompute; skin thickness/volume and symmetry audit; real equipment masses, battery retention/interconnects and localized fuselage XPS; refreshed snapshot and CG |
| 4 | Material/process properties | Identified cloth/resin/foam grades, layup and bond process; representative cured thickness/density and stiffness/strength/bond evidence, including relevant environmental effects |
| 5 | Global and local analysis | Beam/FEA comparison using consistent loads/supports; mesh convergence, reaction equilibrium and root flexibility; laminate stress, buckling/wrinkling, core shear/crushing and bond failure checks |
| 6 | Representative ground tests | Faculty-reviewed test plan, fixtures and representative wing/joint/arm specimens; distributed bending and torsion loads; measured deflection/twist/strain and post-test inspection compared with predeclared predictions/acceptance criteria |

Pusher/tail supports, payload retention and servo/control attachments must also close before an aircraft-level structural conclusion. The order above prioritizes the present wing/VTOL load paths, not their exemption.

## Immediate engineering package

Start with the wing/spar/fuselage connection and one motor-arm attachment. Draw section views and dimensions showing exactly how lift and motor thrust pass through the skins/spar into the fuselage. Identify effective bonded area, skin overlap, hardpoint geometry, contact pressure, fastener arrangement and local foam. Until these exist, an ideally clamped beam result cannot establish attachment strength or actual stiffness.

For the first FEA exercise, use the defined half-wing and arm attachments. Establish software access, material/laminate capability, mesh strategy and expected artifacts before starting. Compare displacement, twist and root reactions with hand/beam predictions. Do not automatically fully bond every interface or fully fix a convenient face without justification. A refined mesh cannot validate the wrong support or bond model.

The 70%-stiffness sensitivity predicts about2.06° twist versus the assumed2° criterion. It is a sensitivity flag, not measured behavior. Resolve it by substantiating stiffness and the criterion, or revising skin/bias reinforcement, torsion closure or joint design and rerunning mass/loads. Do not simply raise the criterion to make the result pass.

## Evidence progression

Use states such as OPEN, GEOMETRY DEFINED, ANALYZED, TEST-CORRELATED and REVIEWED, scoped to an identified load case/configuration. Each closed item needs its source inputs, method, result/margin, reviewer and remaining exclusions. An overall conclusion covers only the load envelope, manufacturing condition and environment actually substantiated.

Test small material/bond specimens before expensive full assemblies. Match test fixtures and load distribution in the prediction; predefine comparison tolerances and inspection criteria with the faculty lead. Separate limit-load behavior from potentially damaging ultimate testing on an agreed test article. A single successful test does not establish repeatability or every failure mode.

## Technical guidance

The FAA composite-structure guidance describes material/process control and progressively supported analysis/testing. Its type-certification framework is useful engineering context; this student UAV is not being claimed compliant with it:
https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_20-107B_with_change_1.pdf

NASA's facesheet-wrinkling review emphasizes selecting an applicable failure model for the specific sandwich configuration:
https://ntrs.nasa.gov/citations/19990017863

