# RescU Structures — current V4 / CAD P03

Current analysis for the Ravatherm XPS / GFRP RescU VTOL UAV. **Run V4 for the current design.** V2 and the older H60 V3 are historical references under [archive/v2_v3](archive/v2_v3/).

## Run

Python 3.10+; no third-party packages required. Open a terminal in this repository folder:

```powershell
python RescU_Structures_V4.py
python verify_v4.py
```

On Windows, `py` can replace `python`. After running, open **results/REPORT.html** for the readable report. Edit **inputs.json** for masses, material assumptions, loads and reserve. Export fresh CAD geometry before treating a changed design as the current baseline.

The committed [baseline report](reports/baseline/SUMMARY.md) and [validation results](reports/baseline/validation.json) record this checkpoint. Download/open [REPORT.html](reports/baseline/REPORT.html) locally for the formatted version; GitHub displays its source.

## Current mass checkpoint

| Quantity | Mass |
|---|---:|
| CAD structural materials | 615.931 g |
| Structural budget including allowances, incomplete | 736.422 g |
| Accounted aircraft estimate | 3.2536 kg |
| Sizing aircraft mass, including reserve | 3.4536 kg |

Battery budget is **944 g**: twelve cells at 74.5 g maximum each plus **50 g assumed** pack hardware, not a measured pack. Localized fuselage XPS, joints, final mounts and installation masses remain unresolved. Do not mistake the CAD material subtotal for finished structural mass.

**Screening status:** the baseline 3g wing case passes its assumed criteria; the 70%-stiffness case exceeds the 2° twist screen. Overall structural validity is **UNRESOLVED**. Numerical tests passing does not qualify the aircraft or its joints.

## Repository layout

| Location | Purpose |
|---|---|
| `RescU_Structures_V4.py` | Current run entry point |
| `inputs.json` | Editable assumptions and component budget |
| `data/cad_snapshot.json` | P03 solid volumes, centroids, inertias and geometry inputs |
| `engine/` | Required numerical and component equations; used by V4 |
| `verify_v4.py` | Accounting and numerical checks |
| `docs/STRUCTURES_V4_GUIDE.md` | Detailed model, sources, assumptions and limits |
| `tools/Export_Current_CAD.FCMacro` | Update the snapshot from saved FreeCAD geometry |
| `reports/baseline/` | Reviewed V4 checkpoint outputs |
| `archive/v2_v3/` | Preserved older models, tests, airfoil references and design notes |
| `results/` | Locally regenerated outputs; excluded from Git |

Read the [V4 guide](docs/STRUCTURES_V4_GUIDE.md) before changing CAD or interpreting strength/CG results. The native CAD assembly is maintained separately; its filename and SHA-256 are recorded in the snapshot. ESC reservations, prop swept disks and duplicated untrimmed source geometry are not counted as structural materials.

## Updating your laptop

In GitHub Desktop, select **rescu-structures**, switch to **main**, then **Fetch origin → Pull origin**. Run the V4 command above from that repository folder.

## Resolving structural validity

Follow the [prioritized structural validation plan](docs/STRUCTURAL_VALIDATION_PLAN.md). Begin with the agreed load envelope, wing center connection and motor-arm hardpoints; close geometry, material, analysis and test evidence separately.
