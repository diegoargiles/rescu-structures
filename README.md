# Latest interface study: P06 rib-to-saddle connections

[P06 native CAD, construction and checks](rib-saddle-p06/README.md) adds eight bonded splice plates to the constrained motor-arm assemblies. The current provisional structural budget is **1,157.673 g** (+20.759 g from P05). Lower-wing entry slots are explicit proposals; peel/fatigue, slot-edge reinforcement and rib-to-spar/skin transfer remain open. No skin cutout mass credit is accepted. Earlier studies below are preserved as reference.

# Latest detailed assembly: P05 motor arms

[P05 constrained motor-arm assembly and report](motor-arm-p05/README.md) adds two native FreeCAD assemblies using the UM2807 1700KV interface, removable clamp mounts and a validated arm-only STEP. The provisional aircraft structural budget is **1,136.914 g**; P04 below is the preserved earlier candidate. The supplied motor's21 V/5S limit conflicts with existing6S inputs and remains unresolved.

# RescU V4.1 — P04 attachment study

This branch adds a **preliminary attachment candidate**, not a fabrication or flight release. The P03 baseline remains preserved in `data/cad_snapshot.json`, `data/inputs_p03.json` and `reports/baseline/`.

## Read first

- [Review findings and mass comparison](reports/p04/REVIEW.md)
- [Construction, load paths, assumptions and required decisions](docs/ATTACHMENT_STUDY.md)
- [Generated analysis report](reports/p04/REPORT.html) — download/open locally
- [Native/STEP audit](reports/native-audit/candidate_audit.json)
- [Attachment plan view](cad/Attachment_Study_Preview.png)

## Current candidate mass

- P03 structural budget: **736.422 g**.
- P04 provisional gross structural budget: **1,041.028 g**, including finish and installation budgets. Remaining CAD overlap/fit findings prevent calling this net installed mass.
- Accounted aircraft: **3.5163 kg**; sizing aircraft: **3.7163 kg**.
- Remove **71.683 g** old local hardware and **42 g** embedded motor/pusher mount allowances; keep **200 g** reserve outside structure/CG. New installation budgets total **74 g**.
- Structural increase is **304.606 g**; aircraft increase is **262.606 g** because of the 42 g mount reclassification/replacement.

The nominal 3g wing screen passes; the 70%-stiffness case still exceeds the 2° criterion at about **2.106°**. Overall structural validity remains **UNRESOLVED**. Accounting tests do not qualify joints.

## Run

Python 3.10+, standard library only for analysis:

```powershell
python RescU_Structures_V4.py
python verify_v4.py
python verify_attachments.py
```

The default inputs are `inputs.json` and `data/cad_snapshot_p04.json`. Output goes to `results/`. New CAD dimensions are assumptions; the snapshot stores actual generated solid integrals at assumed densities. Editing screening inputs does not reshape CAD.

## CAD

The delivered local package contains `cad/RescU_P04_Attachment_Study.FCStd` plus a FreeCAD view macro. The native CAD is a separate static-solid study copied from the audited Desktop P03. Original P03 files are untouched. Large CAD binaries follow the repository's existing separately-maintained-CAD convention; their hashes are recorded in the versioned snapshot and artifact manifest.

FreeCAD 1.1 is required to regenerate geometry. Run `tools/build_attachments.py` with the audited P03 native file, then `tools/refine_candidate.py`, `tools/audit_candidate.py` and the analysis. See the detailed guide for the full sequence, runtime and limitations. Native solids reopen successfully; the audit records STEP round-trip results and remaining intersections. The GUI view helper changes visibility only and has not been exercised in the interactive GUI.

Before accepting the design: resolve CAD interfaces, establish motor mounting drawings and operating loads, choose bonded versus detachable wing construction, agree load cases, and substantiate materials/bonds/joints. Payload, servo and control attachments remain gaps.

## STEP delivery limitation

No STEP export is accepted or included in the delivery ZIP. The full export has an invalid inherited fuselage shell and failed volume agreement. The shell-excluded export has valid solids but fails the aggregate volume check by 1.171%. NURBS conversion changed shell volume and was rejected. Use the native FCStd for review; diagnostic reports are retained under `reports/native-audit/`.
