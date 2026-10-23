# P05 motor-arm assembly

Two native FreeCAD1.1 Assembly subassemblies, each containing an undrilled CFRP arm, two UM2807 1700KV motor envelopes, separately manufactured mount pieces/fasteners, wing saddles and rib blanks. This is the first detailed assembly study; remaining aircraft structure retains P04 status.

Open `cad/RescU_P05_Motor_Arm_Assembly.FCStd` in FreeCAD1.1. Expand `MotorArmPair`, then either motor-arm and its joints. Installation is constrained with native fixed joints and grounded arm datums. All122 physical objects remain individually selectable. Motor internal rotation is not modeled. Geometry is reproducibly generated static solids; it does not have sketch/pad histories.

For review colors and a view of one arm, run `cad/Open_Motor_Arm.FCMacro` inside FreeCAD. It changes display only and does not save the file. The other arm is hidden by that macro; toggle `MotorArm_NegY` to see it. Reference/tool/prop/wire envelopes are under `ClearanceGauges`, initially hidden. The interactive display macro is provided separately from validated headless geometry/solver checks.

- [Download native CAD, STEP and view macro](cad/RescU_P05_CAD.zip)
- [Review results and mass reconciliation](reports/REVIEW.md)
- [Visual review report](reports/REVIEW.html) — open locally
- [Construction, dimensions and assembly order](docs/CONSTRUCTION.md)
- [Plate profiles and nominal dimensions](cad/Mount_Plates_Review.svg)
- [Native/STEP/constraint validation](reports/native_validation.json)
- [Detailed fit audit](reports/assembly_checks.json)
- [Mass ledger](reports/mass_components.csv)

Mass: P04 structural budget1,041.028 g → P05 provisional gross1,136.914 g (+95.886 g). Accounted aircraft3.6121 kg; sizing3.8121 kg. The200 g reserve is counted once. Replaced P04 shoes/arms/saddles and12 g lift hardware allowance are removed. Explicit saddle bond layers reduce the old adhesive budget, and each motor's52 g includes its leads. Detailed mount hardware mass is estimated from simplified steel solids.

Geometry: no positive-volume physical overlaps detected inside the two arm assemblies. Both assemblies solve after re-opening and recover from deliberate motor displacement. Arm-only STEP passes validity, solid-count, volume and per-component center checks. Other P04 aircraft interfaces are not cleared by these checks.

Remaining gates: motor safe screw insertion/torque; actual propeller/hub and wire exit; carbon clamp crushing/slip; laminate/adhesive/fatigue/environmental tests; saddle-to-wing load path. The1700KV listing is21 V/5S maximum while existing battery inputs are6S/25.2 V full. That supply conflict remains unresolved. Nominal3g beam screen passes;70%-stiffness twist still fails at about2.124°.

## Reproduce

The local ZIP includes `baseline-p04/` with the audited native source and the P04 analysis dependencies. In the repository, analysis can use the existing root baseline; regenerating CAD also requires the separately maintained P04 native whose hash is checked by the builder.

Using FreeCAD1.1's Python runtime:

```text
python tools/build_motor_arm.py
python tools/verify_native.py
python tools/render_review.py
```

The render step uses matplotlib (present in the inspected FreeCAD runtime). Standard Python3.10+ can run:

```text
python tools/update_analysis.py
python tools/write_report.py
```

`cad/ARTIFACT_MANIFEST.json` identifies delivered CAD and report hashes. The original P03/P04 files are not overwritten. No fabrication or operating approval is implied.
