# P04 attachment study — preliminary construction and closure record

This branch develops V4/P03 into a **review candidate**, not a manufacturing or flight release. Run `python RescU_Structures_V4.py`, then `python verify_v4.py`. The original P03 snapshot and inputs remain in `data/cad_snapshot.json` and `data/inputs_p03.json`; new analysis defaults to `data/cad_snapshot_p04.json`. The original Desktop CAD is never overwritten. The native study and STEP export are under `cad/` in the delivered package.

## Evidence and geometry fidelity

GitHub parent: `73391e627e078dced2644a18da135a09c447282f`. The Desktop file was found in `RESCU-Current/RescU_CAD_P03`. Its SHA-256 is `5b4ce6b6f7f8afe0953386b3191f858bde2d42926b18e56e2cbed9a3c0d6caa2`; the repository snapshot records `1181ed80a74daf20192822ddcdca741102a3a9c5c58a5736c01abc03975527c3`. All 16 counted saved structural solid volumes match exactly when reopened with FreeCAD 1.1. This establishes volume agreement, not byte identity or feature-history equivalence. Native bounding boxes can be conservative; do not compare their loose spline extrema with the snapshot's optimized bounds as if they were changed dimensions.

Supported P03 inputs: 1,400 mm span; 14-to-8 mm spar OD, 2-to-0.5 mm wall; 350 × 30 × 20 mm arms with 1 mm wall; motor axes X235/555, Y±265 mm; 0.33 mm fuselage skin; 35° tail; 54 mm battery-bank gap. These are snapshot/native design geometry, not as-built measurements. Older Onshape STEP in the workspace is a different design (including a 30° tail), and is not substituted for P03. New parts use exact saved cores/interior mold geometry for trimming. Every new thickness, overlap, material allowable, adhesive quantity, fastener budget and support station is a proposed engineering assumption.

The candidate is static native `Part::Feature` geometry. Rebuild using `tools/build_attachments.py <path-to-P03.FCStd>` under FreeCAD's Python runtime. Do not alter the original source or treat property edits alone as a parametric regeneration. The source companion modules are needed to open its feature objects. CAD outputs are intentionally separate from the original source.

## Proposed construction and load paths

**Lift motor mounts.** Four glass/epoxy shoes: 40 × 44 × 1.5 mm top plate, 1 mm side returns and bottom strap wrapping the existing rectangular CFRP arm. Thrust passes from the selected motor screws into the plate, side returns and bonded arm walls. Glass electrically separates metal hardware from carbon. Do not drill the thin carbon tube based on this study. Motor bolt circle, shaft clearance, screw engagement, antirotation/torque, clamp pressure and prop-plane displacement need the selected motor drawing. The 12 g screw/washer budget is a separate installation estimate. The plate screening span/effective width is 30 mm and is assumed, not measured from a vendor mount.

**Arm-to-wing supports.** Saddles at proposed X356.4 and X410 mm on each arm replace assumed X313/448 mm. The front station is near the P03 spar axis at Y265; the rear station lies in a thicker chord region than the old trailing-edge support. Two 2 mm chordwise glass ribs connect the saddle region to the spar vicinity and inner skins. The load path must carry reversed reactions from one-motor loading, not just upward thrust shared equally. Rib/core pullout, spar attachment, skin bond peel and contact pressure remain open. A saddle touching a surface is not proof of a developed bonded load path.

**Wing center and half-wing attachments.** Default construction is permanently bonded; no detachable pin/socket mechanism is claimed. A 39 × 80 mm center box has 1.5 mm carbon top/bottom caps and webs inside the battery-bank gap, with side webs reaching the root area. Each half-wing receives root cap layers made by 1 mm global-Z offset differences (not verified normal-thickness laminates) over a 100 mm spanwise region and two 2 mm root ribs. Transfer is intended from spar/wing skins through ribs/caps, across the center box and fuselage frames into the opposite half-wing and fuselage. The swept/dihedral spars cannot be assumed to accept a single straight joiner. No bolt-hole weakening of either spar is introduced. Local geometry and bond continuity must be resolved before assigning a root stiffness or joint capacity. The screening assigns the full half-wing bending moment to a proposed cap couple and reports effective-area sensitivity through explicit assumptions, rather than claiming an unverified spar/skin split.

**Pusher support.** A 2 mm glass firewall at X1107, a forward ring at X1040, and four 65 × 8 × 2 mm glass ties support the motor region. Load goes through firewall/ties/frame into the shell. The existing 9.93 N axial demand is derived from cruise thrust and is not maximum/static thrust. Torque, shaft alignment, fastener pattern, gyroscopic load, lateral motor inertia, shell buckling and prop clearance still require closure. There is no invented aft spine stiffness in the analysis.

**V-tail attachments.** Conformal 0.8 mm inner laminate additions near each root plus glass ring frames at X969/1020 and localized foam. Aerodynamic bending is carried by the root skin couple into the reinforced shell/frame region. Bonded fillets and tapered laminate terminations are required; CAD touching surfaces do not establish peel capacity. The 5 mm effective couple depth is a screening assumption and must be replaced by section-specific geometry. Asymmetric control, hinge loads, servo torque and linkage reactions remain absent.

**Battery retention.** Two 77 × 71 × 1 mm glass trays, 6 mm end stops and two clipped 3 mm cradle webs per tray sit beneath the existing two-bank envelope. Two straps, insulating pads and anchors have a 16 g budget. Load path: pack → straps/end stops/trays → cradle webs → shell/frames. Pack interconnects and leads are not retention members. The proposed retention screen is 6g limit × 1.5 ultimate; this is a proposed requirement, not an agreed crash or landing case. Verify each bank and all three axes; equally shared straps are not redundant unless each can retain the full pack load. Ensure access, insulation, terminals, cable bend radii and cooling clearances. Do not relocate the battery automatically to recover CG.

**Fuselage hardpoints and foam.** Interior rings follow P03 saved mold geometry. Local XPS fills support skin shape and distribute contact; glass frames and laminate paths carry concentrated loads. Do not thread fasteners into XPS or infer allowable bolt preload from its nominal compressive strength. Shell doublers/tapered frame tabs and the payload/servo mounting details remain unfinished. Local foam and adhesive volumes are distinct quantities.

## Mass boundaries and double-count prevention

- Original P03 structural budget: 615.930560 g CAD + 41.425416 g wing finish + 7.382879 g tail finish + 71.682937 g local hardware = 736.421792 g.
- Remove the full 71.682937 g local-hardware allowance when introducing the explicit candidate parts and installation budgets. The replacement covers the listed candidate only; unresolved servo/payload hardware is still a gap.
- Remove four 8 g lift-mount allowances and one 10 g pusher-mount allowance from **nonstructural motor/prop rows**: 42 g total. The motor/prop estimates remain otherwise unchanged and are not reverified vendor masses.
- Retain 41.425416 g and 7.382879 g as **surface sealing/finish only**, excluding the modeled spar bond and new joint fillets/adhesive. These quantities still require process-level verification.
- New installation budgets are 12 g lift screws, 12 g arm bonds, 12 g root bonds, 8 g pusher screws/bonds, 6 g tail bonds, 16 g battery straps/pads/anchors, and 8 g frame/foam bonds: **74 g**, all provisional.
- The 944 g battery budget remains 894 g maximum cells + 50 g pack-only hardware. Airframe trays/straps are counted separately. If a future weighed pack includes straps or trays, remove the corresponding separate rows.
- The **200 g unallocated reserve stays outside structural mass and CG**, and is added once to aircraft sizing mass. No attachment mass is hidden in or deducted from reserve.
- Foam displaced by new inserts is subtracted from the relevant existing core; the CAD audit records each subtraction. New/new and equipment interference must be checked and resolved or explicitly identified before claiming a net installed CAD mass. A gross candidate subtotal is not a finished aircraft weight.

## Analysis scope

Global beam screens are rerun at the revised sizing mass and support stations. Added local parts do **not** automatically increase ideal-wing stiffness: the analytical model still uses the P03 skin/spar sections. No favorable stiffness credit is taken for an unqualified joint. Local foam removal and replacement are also not resolved in the beam sections, so this approximation is not guaranteed conservative; joint flexibility and local damage may govern. Attachment screens use assumed 70 MPa glass bending, 210 MPa carbon axial and 2 MPa effective bond shear. These are sensitivity inputs, not manufacturer, coupon or certified allowables. Average bond shear omits peel/end concentration. A passing strip calculation does not close local buckling, crushing, delamination or fatigue. Negative support reactions are retained with signs, and equilibrium residuals are tested.

## Decisions and missing evidence

1. Accept a permanent bonded center wing, or request a separable transport joint (a different design and mass).
2. Confirm lift/pusher motor drawing, prop/voltage operating point, maximum thrust and torque; confirm mount-plane clearance.
3. Agree maneuver, gust, transition, asymmetric VTOL, landing and battery retention loads with the faculty lead.
4. Select cloth/layup, resin, adhesive, surface preparation, foam orientation and cure process; obtain representative joint/laminate tests.
5. Resolve candidate interface gaps/overlaps and equipment interference, then refresh CAD and mass. Include payload plate attachment, servo mounts and control mechanisms before declaring finished structural weight.

Engineering guidance: [FAA AC 20-107B](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_20-107B_with_change_1.pdf) discusses composite material/process and bonded-joint substantiation. [WEST SYSTEM bonding guidance](https://www.westsystem.com/instruction/epoxy-basics/bonding-and-clamping/) supports overlap/fillet/reinforcing-fiber construction and controlled bond processing. Neither source supplies allowables for this candidate or establishes aircraft compliance.

## Rebuilding the delivered candidate

Run build_attachments.py with the audited native source, then refine_candidate.py, audit_candidate.py, export_preview.py and render_preview.py. The refinement moves WingFrame_326 to X319, WingLocalFoam_321 to X306, and WingLocalFoam_280 to X282 mm; internal names retain their original identity. It removes new dense-part occupancy from local XPS. Run the analysis and both verification scripts after regenerating the snapshot. The new study has static solids and does not replace P03 feature history.

The attachment_design block controls hand-screen assumptions only; it does not reshape CAD. Physical dimensions are explicit in tools/build_attachments.py. If changing thickness or geometry, rebuild and re-audit the candidate and regenerate its snapshot before using the updated mass. The assumed 2,000 mm² effective root bond area is 100 mm overlap × 40 mm gross width × 0.5 effective-area factor; actual wet-out, taper and peel behavior are not demonstrated.

## Final transfer check

The native study reopens with all structural solids valid. Full STEP transfer fails: the inherited fuselage shell becomes invalid with substantially changed volume. A shell-excluded export is valid but differs in aggregate volume by 1.171%, so it is also unaccepted. NURBS conversion changes shell volume and is rejected. No accepted STEP is delivered. Native FCStd is authoritative for this preliminary review; see saved diagnostic reports.
