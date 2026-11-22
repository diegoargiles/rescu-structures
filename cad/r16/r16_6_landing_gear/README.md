# RescU R16.6: retractable "knee" landing gear

**Status: proposal (November 21, 2026).** R16.5 stays the current design until the wing-torsion item below is closed. Full-aircraft STEP SHA-256: `7a018ca241d653625541cde510ea6660a46bebd5d543aec2a0593060ac515ecc`. The scripts expect the R16.5 STEP bodies extracted with `../scripts/readstep.py` into `../orig/` beside the working folder; adjust paths before rerunning.

R16.6 is R16.5 with three retractable legs added:
- two front legs, one in each boom, with the knee just aft of the front motor;
- one tail leg in the fuselage belly.

All three use the same knee module. The CAD is in the deployed position. Frame: X aft, Y right, Z up, mm.

## Files

| File | What it is |
|---|---|
| `RescU_R16_6_Full_Aircraft.step.zip` | Full aircraft, 183 parts (R16.5 134 + gear 49). The R16.5 tree is unchanged. The booms' lower halves, the fuselage shells and the seam strip now have the slot. The gear is in `LG_Front_R`, `LG_Front_L` and `LG_Tail`. |
| `RescU_R16_6_LG_Front_R_Module.step.zip` | One front module with the right boom shell, motor and access covers. **Start here to set up the motion.** |
| `RescU_R16_6_LG_Tail_Module.step` | Tail module only. |
| `renders/r_side_deployed.png`, `renders/r_side_retracted.png` | Side views. When retracted, the legs are hidden inside the boom and belly outline. |
| `renders/r_knee_states.png` | Knee mechanism at the centre-plane section in three states, and the full leg swing. |
| `scripts/` | CadQuery source. `lg.py` holds the geometry and parameters, `build_all.py` places the modules, `analysis.py` does the mass and loads, `asm.py` writes the STEP. |

Each module is split into four rigid sub-assemblies: `_Fixed`, `_Leg`, `_Tendon` and `_Servo_Arm`. Only the last three move.

## How the knee works

| Body | Part | Analogy |
|---|---|---|
| Muscle | KST X08H Plus slim servo, 8 mm thick, 9.5 g, ±60° | Quadriceps |
| Tendon | 7075 plate on the centre plane, sliding on 2 guide pins (stroke 21.3 mm). Its bracket takes the servo arm pin in a vertical slot, which works as a scotch yoke. | Patellar tendon |
| Kneecap | Ø3 fork pin on the knuckle, radius 10 mm, running in the plate's ⊥-shaped slot | Patella |
| Tibia | CFRP OD10/ID6 leg rod plus a TPU 95A hemispherical foot (Ø16) | Shin |
| Femur | 7075 knee block bonded into the boom: shaft Ø5 in double shear, heel stop, lock keeper | Thigh |

- **Deploying:** the servo pulls the plate aft, and the leg swings down to 10° forward rake (foot at x ≈ 142, under and just ahead of the front motor). The heel then lands on its stop. The servo travels 4 mm more, which slides the fork pin into the forward pocket of the ⊥ slot. **The knee is now locked.** Fold loads push the pin up into the keeper on the knee block, and forward loads go into the heel stop. Neither load reaches the servo.
- **Retracting:** the servo pushes forward. The first 4 mm unhooks the pin, then the plate drives the leg up into the trough. The last 2 mm hooks the pin into the aft pocket, which locks the leg retracted.
- **Retracted:** the leg lies in a 0.5 mm CFRP trough bonded inside the boom bottom. The trough also closes the boom section around the slot. The foot sits in a pocket that ends at x 558, ahead of the rear access cover.
- **Wiring:** the motor wires pass the knee on the inboard side, in the gap between the block wall and the boom wall.

## Making it move in SolidWorks

1. Open `RescU_R16_6_LG_Front_R_Module.step.zip`. If a component shows (f), right-click it and choose **Float**, then **Fix** only `LG_Front_R_Fixed` and `LG_Front_R_Airframe_Context`. Keep the three moving sub-assemblies **rigid** (the default).
2. **Planar motion** (all motion is in the XZ plane). Add **Coincident**: *Top Plane* of `LG_Front_R_Leg` ↔ *Top Plane* of the assembly. Do the same for `_Tendon` and `_Servo_Arm`.
3. **Knee:** **Concentric**: `Knee_Shaft` cylinder ↔ the Ø5.1 bore in `Knee_Block`.
4. **Servo:** **Concentric**: the `Servo_Arm` hub bore ↔ the output-shaft cylinder of `REF_Servo_KST_X08H`.
5. **Tendon guides:** **Slot** mate (Free): `Guide_Pin_1` ↔ the long horizontal slot in `Tendon_Plate`. Add another **Slot** mate: `Guide_Pin_2` ↔ the horizontal slot at the aft end of `Tendon_Bracket`.
6. **Servo to tendon:** **Slot** mate: `Servo_Arm_Pin` ↔ the short vertical slot in `Tendon_Bracket`.
7. **Kneecap:** **Tangent**: `Fork_Pin` cylinder ↔ the *forward* flat face of the vertical stem of the ⊥ slot in `Tendon_Plate`. A slot mate won't work here because the ⊥ shape isn't a plain slot.
8. **Limits:** Advanced → **Angle** limit on the servo arm, measured from straight down, **−44° … +31°**. Inside this range the pin rides in the stem.
9. Drag `Servo_Arm`. The plate slides and the leg swings 0–100°.

To show the lock travel, suppress mate 7 and set the arm limit to ±60°.

For the full aircraft, repeat steps 2–8 under each `LG_*` folder. On the left boom the parts are mirrored, so the arm limit signs swap. In the tail the module is turned 180°, so the leg folds forward.

## Key numbers

All loads are on the repo basis: 5 g landing, ultimate = 1.5 × limit, 7075 / CFRP 210 MPa allowables.

| Item | Value |
|---|---|
| Leg length, pivot to foot tip | Front 356 mm, tail 359.5 mm |
| Ground below the boom pivot | 351 mm (z −378.7) |
| Payload plate clearance | ≈ 323 mm |
| Gear mass | **230 g** (81 / 81 / 84 g), 6 % of MTOW. Largest items: rods 82 g, troughs 37 g, knee blocks 36 g, servos 28.5 g |
| CG x (R16.5 was 382) | Deployed 386.1, retracted 387.9; target 394.4, NP 408 |
| Tip-over | Nose-over 33.7°, sideways 26.0° (CG 367 mm above ground) |
| Foot load share | Each front 35 %, tail 29 % |
| Leg rod OD10/6 at the knee | 15.6 N·m ult → 182 MPa, **MS +0.15** |
| Heel stop (fwd loads) | 1.67 kN ult. Shaft τ 43 MPa; wall bearing 84 MPa |
| Lock (fold loads), 1 g sliding μ 0.8 | 4.6 N·m ult. Fork pin 594 N, τ 42 MPa; keeper 234 MPa (**MS +1.15**) |
| Servo margin | Knee torque ≥ 0.235 N·m at 6 V against ~0.15 N·m needed (leg weight + downwash) |
| **Wing torsion at the boom station** | **21.9 N·m limit**; LC6 was 3.3 N·m. Skin-only screen **MS −0.53** |
| Aft fuselage at x 600 (tail foot) | 13.4 / 16.3 MPa, MS +0.22 (the existing +3 g case is +0.26) |

## Open items (must close before build)

1. **Wing torsion (critical).** A forward foot puts about 6.6× the existing torque into the inner wing. One extra 0.33 GFRP ply still leaves MS −0.07. One or two ±45° CF plies on the inner wing between root and boom (about +25 g per side) would clear it on this screen.
   - Run an FEA LC8: three-leg landing at 5 g plus 0.25 drag.
   - Separately, ask whether 5 g is the right landing basis for a VTOL with gear.
2. Joiner: the tail now takes 29 %, so the LC7-type joiner load drops about 24 %. The current OD12/10 tube is still near MS 0; the OD14/11 change stays recommended.
3. Fail-safe: with the servo dead in the retracted position, the gear stays up. If the team wants gear-down on failure, add a torsion spring on the knee shaft and re-check servo torque.
4. Check the servo dimensions against the KST drawing. The CAD uses a 23.5 × 8 × 17 mm body, output 6 mm from the front edge.
5. Lightening, about −50 g:
   - pocket the knee blocks;
   - OD10/8 rods if a coupon shows pultruded strength above ~400 MPa (the screen used 210);
   - 0.3 mm troughs.
6. Shorter legs would raise the tip-over margin and cut every knee load in proportion. 250 mm legs give about 34° sideways. Maximum length was the requirement for this revision.
7. The Controls lead needs the CG shift and the three servo channels.
