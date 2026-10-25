# P06 rib-to-saddle bonded splice study

[Review findings](reports/REVIEW.md) · [Visual report](reports/REVIEW.html) · [Construction guide](docs/CONNECTION_DESIGN.md) · [CAD package](cad/RescU_P06_CAD.zip)

Open `cad/RescU_P06_Rib_Saddle_Assembly.FCStd` in FreeCAD1.1. It retains the two constrained P05 motor arms and adds eight rib/saddle splice connections. Run `cad/Open_Rib_Saddle.FCMacro` for review colors and a carrier close-up. The display macro is separate from validated headless model/solver checks and does not save the file.

Front splice plates are2 mm, rear plates1.5 mm; packers1.8 mm; bond layers0.2 mm. Original ribs and saddles remain separate physical parts. Revised skin/core geometry and proposed slot envelopes are hidden under `WingPocketContext`. Those context objects are held in aircraft coordinates; they are not a completed constrained wing assembly. Static solids are regenerated from scripts and do not carry sketch/pad histories.

Structural budget: **1157.673 g**, up**20.759 g** from P05. New adhesive is reallocated from the existing budget; reserve remains200 g. Skin cutout quantities fail Boolean volume conservation, so **no skin mass credit** is accepted. Slot-edge reinforcement remains future work with unassigned mass.

Native constraints, adhesive contact coverage, arm-only STEP and post-relief fit checks pass. Average shear and plate-strip screens use assumed properties; peel/fatigue and the wing load path remain unqualified. See the report for scope and limitations. Original P05/P04 files are read only.

## Rebuild

Use FreeCAD1.1's Python runtime from this directory, with the sibling `motor-arm-p05` and `v4-attachments` reference folders available:

```text
python tools/build_connections.py
python tools/relieve_wing_context.py
python tools/fit_upper_edges.py
python tools/verify_connections.py
python tools/analyse_connections.py
python tools/render_connections.py
python tools/write_report.py
python tools/package_review.py
```

The render step uses matplotlib. The delivered full ZIP includes the required P04/P05 reference inputs, native source models and unchanged beam solver in those sibling folders. The compact CAD ZIP contains the P06 native, arm-only STEP and display macro.
