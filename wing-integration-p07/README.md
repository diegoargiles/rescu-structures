# P07 wing-arm integration candidate

Start with [the review](reports/REVIEW.md) and [construction assumptions](docs/DESIGN_AND_BUILD.md). The native assembly and STEP files are under cad/. Open the carrier-cutaway STEP to see the connection without opaque wing skins or foam. Individual new laminate regions are under cad/parts/.

Provisional structural budget: **1171.807 g (+14.135 g from P06). The 200 g reserve is separate. This is a geometric/sizing candidate, not a fabrication or flight release.

STEP preserves placed separate solids; native FreeCAD constraints do not become SolidWorks mates. See reports/step_validation.json for any thin-shell reference quantity limitations.

Rebuild with FreeCAD 1.1 Python: tools/build_wing.py, tools/refine_layers.py, tools/finish_bonds.py, tools/check_export_account.py --prepare-only, tools/relieve_slot_spar.py, tools/route_wires.py, tools/check_export_account.py --fit-only, tools/run_stage.py export, tools/run_stage.py mass, tools/check_splices.py, tools/audit_patch_extents.py, tools/render_wing.py, tools/write_review.py. Run in that order. The source P04/P06 native documents and P05/P06 accounting files are required in the sibling study folders (P04 may be the repository root). Sources remain unchanged. Inputs document assumptions; geometry dimensions are set in the build script.

**Critical sizing finding:** the conservative all-torque-to-spar radial edge-transfer screen fails. This revision needs a larger developed joint or a substantiated alternative load path before fabrication. See the review; no overall structural pass is claimed.

The FreeCAD display macro cad/Open_P07_Wing.FCMacro shows transparent skins, hidden foam and proposed wire bundle envelopes without saving changes.
