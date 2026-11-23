# RescU R16.9: wing 35 mm aft, ELP camera nose, short landing legs

**Status: current working revision (November 22, 2026).** This is the design in the Final Design Review deck.

| | |
|---|---|
| STEP | `RescU_R16_9_Full_Aircraft.step.zip` |
| STEP SHA-256 (unzipped) | `0d635dac1a23649110cf941b6f57a4ac9bcd2e0e67bdbfa12d4d74f83ebb6c3f` |
| Parts | 177, gear deployed |
| Frame | R16.5 frame: origin at the nose tip, X aft, Y right, Z up, mm. The fuselage axis is at z 0. |

**For Stability & Control:** the data the S&C lead asked for is in [SC_DATA_PACKAGE.md](SC_DATA_PACKAGE.md), with the machine-readable files in `mass_properties/` and `geometry/`.

## Lineage
- **R16.6** ([`../r16_6_landing_gear`](../r16_6_landing_gear/README.md)): added the retractable knee landing gear.
- **R16.7** (60 mm nose plug): dropped by the team, not committed.
- **R16.8**: R16.6 plus the changes below. It was not committed separately.
- **R16.9**: R16.8 with shorter legs.

## Changes vs R16.6

### R16.8: wing aft, smooth nose and ELP camera

**Nose**
- The Z30 gimbal is removed, along with:
  - the cove liner;
  - the camera shelf and camera nutplates;
  - frames NF1 and NF2.
- The smooth R16.2 nose skin is back (L/R shells). The 4-screw removable joint is kept.
- The R16.2 lower D-frame replaces NF3 at x 135. The R16.2 nose seam strips are back.

**Camera**
- `REF_Camera_ELP_5MP_IR_USB` is a placeholder envelope only: a 38 × 38 × 22 mm board stack plus a Ø16 × 16 mm M12 lens.
- It sits at the bottom of the nose tip, x 28–74, with the lens pointing forward and 45° down.
- Mass is **35 g, assumed**. The mount and lens window are not designed yet.

**Wing 35 mm aft.** These moved with it:
- both wing panels;
- both booms, with motors, props and front gear modules;
- the joiner, now at x 339–351, with its receiver sleeves and stop ring;
- the side rails, pin pads and root fairings;
- ring frames F282 and F320, now at x 317 and 355.

The shell holes are filled at the old stations and re-cut at x 345, 380 and 420.

**Rear battery module 35 mm aft** (x 360–435), with its tray, end stop, pads and saddles. Otherwise the joiner and F320 would pass through it. The front module stays at x 200–275.

**ESC deck, pads and ESCs 5 mm aft** (x 440–570).

**Unchanged from R16.6:** the V-tail servos (x 930–960) and the buoy plate (x 325–375).

### R16.9: short legs
- Legs are 180.6 mm (front) and 183.9 mm (tail), measured from the pivot to the foot tip.
- The ground is at z −206. That gives **150 mm clearance under the buoy plate**, the lowest fixed point on the airframe.
- The leg rod is now CFRP OD10/8 (was OD10/6).
- The troughs, boom slots and belly slot are shortened to match, and the boom skin is restored where the old slot ran.
- The tail knee block is re-trimmed to the regenerated belly doubler.
- Gear mass is **158.6 g** with servos (was 229.9 g).
- **Checks:**
  - the full swing is clean (9 positions on the front leg, 5 on the tail);
  - every moved part was checked against the fixed parts with 0.000 mm³ overlap;
  - the only exceptions are the battery-vs-cells reference duplicate and the bond-line slivers.

## Mass and CG

Built bottom-up from this CAD; see `mass_properties/` and the S&C package.

The 350 g "Camera/AI" allocation (the old camera line) was cut on November 22.

| Case | Mass | CG x |
|---|---|---|
| Takeoff, gear down, buoy on, with the 7.5 % bond and finish allowance (**baseline**) | **3.395 kg** | **461.6** (76 % MAC) |
| After the buoy release, gear up | 3.025 kg | 475.7 (+13.7 mm) |
| Before the cut, for reference | 3.745 kg | 424.0 |

**The CG is now well aft of any plausible neutral point.** See section 6 of the S&C package for the options.

The structural mass is 1113 g in CAD and 1196 g with the allowance, landing gear included.

## Structures screen

Script: `structures/rescu_r16_9_structures.py`. Results are in `structures/results.json` and the figures are in `structures/`.

| Item | Margin | Fix |
|---|---|---|
| Wing joiner OD12/10 | **−0.21** | OD14/11 gives +0.49 (+3.6 g) |
| Wing skin torsion, 5 g landing on the legs | **−0.34** | One ±45° CF ply on the inner wing gives +0.43 (about +25 g per side) |
| XPS core shear (conservative screen) | −0.04 | Coupon test |
| Skin wrinkling | +0.16 | Coupon test |
| Spar | +0.90 | — |
| Tip deflection | 15.6 mm (+1.25) | — |
| Leg rod OD10/8 | +0.76 | — |
| Knee lock pins and keeper | > +3 | — |
| Aft fuselage shell | +0.30 flight, +0.61 tail-leg landing | — |
| Booms and the other joints | > +3 | — |

**On the ground:** tip-over is at 42° sideways and 48° nose-over.

**Flags:**
- A 5 m/s gust at V_max gives 3.9 g, above the +3 g basis.
- The boom's first bending mode (about 300 Hz) sits in the lift-prop 2P band.

## Files

| Path | Content |
|---|---|
| `RescU_R16_9_Full_Aircraft.step.zip` | Full aircraft STEP, named parts and sub-assemblies. Open with Dissolve/Float in SolidWorks as for R16.6 |
| `SC_DATA_PACKAGE.md` | Answers to the Stability & Control data request, with assumptions and coordinate references |
| `mass_properties/R16_9_mass_properties.json` | Mass, CG and inertia tensor for six cases (gear up/down, buoy on/off, with the structural fixes, without the unresolved allocations) |
| `mass_properties/R16_9_component_masses.csv` | Every item: mass, centroid and source (case A) |
| `mass_properties/massprops.py`, `occ.py` | The mass-properties build (CadQuery/OCP). They need the R16.9 BREPs extracted from the STEP |
| `geometry/R16_9_geometry_reference.json` | Wing and V-tail planform (MAC, areas, sweep, dihedral, incidence), ruddervator hinge line, motors and thrust axes, hover thrust split, pusher thrust line, battery range, buoy, servos, sensors |
| `geometry/sections.json`, `geom.py`, `refdata.py` | Wing and V-tail sections cut from the CAD skins, and the derivation |
| `structures/` | R16.9 structures screen: script, results and figures (V-n, wing loads, margins, gear trade, boom, mass) |
| `renders/` | Side views with the gear deployed and retracted, top/side/front views, hero, interior x-ray, process map |
| `scripts/` | R16.8 and R16.9 builds (`r168.py`, `asm168.py`, `mass168.py`, `r169.py`, `asm169.py`), and the VTK renderer used for the FDR renders (`vr.py`, `steps.py`). Paths are those of the build machine |

## Open items
1. **Neutral point for this wing position.** Aero must compute it (XFLR5). The rough NP of 431 mm puts the post-release CG behind the NP; see the S&C package.
2. **No ailerons in the CAD.** Roll control in wing-borne flight needs a decision; see the S&C package.
3. **Buoy plate.** Re-centre it on the empty CG once the CG is fixed, to remove the release shift (13.7 mm now).
4. **Equipment list** (Luis is checking it in the shared mass list):
   - the 350 g "Camera/AI" line is cut;
   - confirm or cut the 136.2 g "other servo" allocation;
   - add masses for the FC, receiver, pusher ESC and the rest of the missing items;
   - weigh the ELP camera.
5. **CG far aft after the cut.** Restore the margin with nose mass, a wing move or relocated equipment, once Aero gives the NP.
6. **Rear battery access.** The module (x 360–435) runs past the rear hatch (x 322–407).
7. **Structures:**
   - joiner OD14/11;
   - the inner-wing ±45° CF ply;
   - coupon and bend tests;
   - a boom tap test.
8. **V-tail linkage:** pushrods and horns are not modelled.
