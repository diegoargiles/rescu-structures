# R16 full-aircraft CAD (November 15, 2026) — current design

R16 = R15 + elbow joints at the wing root + TPU landing feet removed. The aircraft has **no landing gear**; it lands on the [landing station](../landing_station/README.md).

| File | Content |
|---|---|
| `RescU_R16_Full_Aircraft.step.zip` | Full assembly STEP (134.6 MB unzipped; zipped). 105 bodies. SHA-256 of the STEP: `b9ea4e5901d8d7ad16218f7bd0ec080a49800200ad2cc743b9a25a0628570851` |
| `RescU_R16_BOM_CAD_masses.csv` | CAD mass BOM |
| `cg.json` | Mass / CG estimate |
| `interference_r16.json` | 268 changed-part pairs (0 overlaps > 0.05 mm³) plus every wing tube vs its skin (all 0.000 mm³) |
| `R15_vs_R16_root_joints.png` | Root joint comparison |
| `scripts/` | `wing_r16.py` (wing with elbows), `elbow.py` (elbow paths, clearance), `assemble_r16.py`, `check_r16.py`, `cg_r16.py`, `clear.py`, `readstep.py` |

The scripts import the R15 scripts from `../r15/scripts` and the R15 STEP bodies (extracted with `readstep.py`). Paths inside them are the absolute paths of the build machine; adjust before rerunning.

![R15 vs R16 root joints](R15_vs_R16_root_joints.png)

## Changes vs R15

| Change | Detail |
|---|---|
| Root adapter → **root elbow** (CFRP, 10.9 g each, was 13.6 g) | Molded S-bend, OD12 body. Spigot OD9.9 plugs 26 mm into the joiner bore; spigot OD7.9 plugs 30 mm into the OD10/8 spar bore. Tightest bend radius 48 mm. Plugs *into* the tubes, so it is never wider than the joiner. |
| Aft root socket → **aft elbow** (CFRP OD5, 1.69 g) | Single gentle bend; D3 anti-rotation pin bonded in its inboard end; 15 mm spigot into the OD5/3.5 aft torque tube. |
| Joiner | Shortened from ±100 to ±46 mm (wings plug into it). |
| Main spar / aft tube | Start at Y110 / Y100 and butt on the elbow shoulders. Core fills the old shear-plate space. |
| TPU landing feet | Removed (both booms). |

## Checks

- **Nothing trimmed by the skin:** every wing tube has 0.000 mm³ intersection with the skin. Minimum clearance to the inner skin: root elbow 0.66 mm (R15 adapter −1.51, i.e. cut), aft elbow 0.51 mm (was 0.18).
- Interference: 268 pairs involving changed parts, 0 overlaps > 0.05 mm³ (`interference_r16.json`).
- Tight spots unchanged from R15: OD8 spar segment 0.13 mm from the skin at Y560; outboard aft collar 0.17 mm.
- Strength screen (+3 g × 1.5, spar-only, conservative): spar spigot OD7.9/ID4 at Y110 ≈ 317 MPa — make it a solid pultruded CFRP rod or lengthen it.

## Mass and CG

Total 3387.0 g (−33.9 g vs R15). CG x 406.6 mm vs NP 408.0 → static margin +1.0 % MAC. Battery at x ≈ 256 mm reaches the 394.4 mm target CG.

## Landing decision history

1. Removed the TPU feet (this revision).
2. Tried a three-leg gear (raked CFRP legs at mid-boom + tail leg, 135 mm prop clearance): +54.5 g and CG behind the NP (−0.2 % margin). **Dropped.**
3. Folding pusher prop judged not workable by the team.
4. **Adopted: ground landing station** holding the booms and tail — no on-aircraft gear.
