# P04 attachment study — result and review gates

**Status: preliminary candidate, not finished structural mass or fabrication release.**

## Reconciled mass budget

- P03 structural budget: 736.4218 g.
- P03 accounted aircraft: 3.2536 kg.
- P03 sizing aircraft: 3.4536 kg.
- P04 candidate structural budget: 1041.0282 g.
- P04 accounted aircraft: 3.5163 kg.
- P04 sizing aircraft: 3.7163 kg.

Structural increase: 304.606 g. Aircraft increase: 262.606 g. The difference is the 42 g moved out of embedded motor mount allowances.
Explicit new installation budgets: 74.000 g. Old local-hardware allowance removed: 71.683 g. Reserve remains 200.000 g outside structure and CG.
Exact recorded foam displacement: 1.9238 g. These small deductions do not eliminate all geometric overlap risks.

## New CAD material by attachment group

- Lift motor mounts: 35.520 g.
- Arm-to-wing attachments: 44.236 g.
- Wing center and half-wing joints: 106.165 g.
- Fuselage hardpoints and foam: 24.869 g.
- Pusher support: 20.140 g.
- V-tail attachments: 31.286 g.
- Battery retention: 41.699 g.

These are assumed candidate construction dimensions integrated by FreeCAD, not verified manufactured quantities. Retained wing/tail finish budgets total 48.808 g. See the mass ledger for individual parts.

## Geometry checks

Native valid: True; STEP valid: False. Native/STEP solid count: 71/71. Remaining reported interference pairs: 32.

All positive-volume interferences below require review. Equipment proxies are not vendor-certified geometry. Structural overlaps make the untrimmed candidate subtotal conservative and prevent calling it a net installed mass. The 71.683 g hardware allowance and 200 g reserve are nevertheless reconciled exactly.

- WingCenterBox / REF_Battery_Packaging_Allowance_PROVISIONAL: 2263.290 mm³ (equipment envelope).
- WingCenterSideWeb__1 / Fuselage_GFRP_Shell_0330: 286.984 mm³ (structural overlap).
- WingCenterSideWeb__1 / Wing_NegY_GFRP_Skin_Exposed: 50.795 mm³ (structural overlap).
- WingCenterSideWeb__1 / Wing_NegY_EpoxyBond_Exposed: 6.965 mm³ (structural overlap).
- WingCenterSideWeb__1 / Wing_NegY_CFRP_TaperedSpar: 571.427 mm³ (structural overlap).
- WingCenterSideWeb__1 / WingCenterBox: 64.500 mm³ (structural overlap).
- WingCenterSideWeb_1 / Fuselage_GFRP_Shell_0330: 286.984 mm³ (structural overlap).
- WingCenterSideWeb_1 / Wing_PosY_GFRP_Skin_Exposed: 50.795 mm³ (structural overlap).
- WingCenterSideWeb_1 / Wing_PosY_EpoxyBond_Exposed: 6.965 mm³ (structural overlap).
- WingCenterSideWeb_1 / Wing_PosY_CFRP_TaperedSpar: 571.427 mm³ (structural overlap).
- WingCenterSideWeb_1 / WingCenterBox: 64.500 mm³ (structural overlap).
- WingRootCaps_PosY / WingCenterSideWeb_1: 182.282 mm³ (structural overlap).
- WingRootRib_PosY_44 / WingCenterSideWeb_1: 575.999 mm³ (structural overlap).
- WingRootRib_PosY_44 / WingRootCaps_PosY: 271.750 mm³ (structural overlap).
- WingRootRib_PosY_54 / WingRootCaps_PosY: 287.292 mm³ (structural overlap).
- WingRootCaps_NegY / WingCenterSideWeb__1: 182.282 mm³ (structural overlap).
- WingRootRib_NegY_56 / WingRootCaps_NegY: 287.292 mm³ (structural overlap).
- WingRootRib_NegY_46 / WingCenterSideWeb__1: 575.999 mm³ (structural overlap).
- WingRootRib_NegY_46 / WingRootCaps_NegY: 271.750 mm³ (structural overlap).
- WingFrame_326 / Wing_PosY_CFRP_TaperedSpar: 146.524 mm³ (structural overlap).
- WingFrame_326 / Wing_NegY_CFRP_TaperedSpar: 146.524 mm³ (structural overlap).
- WingFrame_326 / WingCenterBox: 122.869 mm³ (structural overlap).
- WingFrame_326 / WingCenterSideWeb__1: 265.593 mm³ (structural overlap).
- WingFrame_326 / WingCenterSideWeb_1: 265.593 mm³ (structural overlap).
- WingLocalFoam_321 / Wing_PosY_CFRP_TaperedSpar: 120.449 mm³ (structural overlap).
- WingLocalFoam_321 / Wing_NegY_CFRP_TaperedSpar: 120.449 mm³ (structural overlap).
- BatteryTray_Front / REF_Battery_Packaging_Allowance_PROVISIONAL: 709.746 mm³ (equipment envelope).
- BatteryCradle_Front_206 / BatteryTray_Front: 42.600 mm³ (structural overlap).
- BatteryCradle_Front_261 / BatteryTray_Front: 42.600 mm³ (structural overlap).
- BatteryTray_Rear / REF_Battery_Packaging_Allowance_PROVISIONAL: 709.746 mm³ (equipment envelope).
- BatteryCradle_Rear_331 / BatteryTray_Rear: 42.600 mm³ (structural overlap).
- BatteryCradle_Rear_386 / BatteryTray_Rear: 42.600 mm³ (structural overlap).

## STEP transfer limitation

The native FCStd is the review authority. The full STEP has an invalid inherited fuselage shell and fails volume agreement. A shell-excluded export has valid solids but still fails the aggregate volume screen (1.171% difference); NURBS conversion also changes shell volume. No STEP is accepted or included in the delivery ZIP. Diagnostic reports are retained. Further transfer diagnosis is required before downstream STEP use.
Remaining pairwise duplicate-material upper bound: 9.776 g. This is not a mass correction: triple intersections may be counted repeatedly and pre-existing P03/P03 overlaps were not audited.

## Updated load screens

- Wing 3g: PASS, tip deflection 25.63 mm, twist -1.47°.
- Wing -1.5g: PASS, tip deflection -12.82 mm, twist -0.75°.
- Wing 3g at70% assumed stiffness: FAIL, tip deflection 36.62 mm, twist -2.11°.
- V-tail at top speed: PASS, tip deflection 4.31 mm, twist -0.11°.
- Aircraft CG X: 392.99 → 397.56 mm, provisional. Battery held fixed.

## Required review

Resolve CAD interfaces and clearance findings; choose bonded versus detachable center wing; confirm motor drawings/torque/max thrust; agree loads and retention requirements; validate layup/adhesive and joints. Payload/servo/control mounts, environmental effects, landing/gust/fatigue and shell buckling remain open. See docs/ATTACHMENT_STUDY.md for assumptions and load paths.
