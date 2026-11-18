# Nose module (R16.4): manufacturing and assembly plan

November 17, 2026. Covers the removable nose module, x 0–179: L/R GFRP shells, cove liner, G10 frames NF1–NF4, camera shelf with nutplate mount, and the 4-screw joint to the fuselage. Geometry, masses and checks are in [`cad/r16/README.md`](../cad/r16/README.md#r164--removable-nose-module-november-17).

## 1. Forward-flight loads (hand check)

All loads are small; the mount is sized by stiffness and handling, not strength. Inputs: cruise 20 m/s and top speed 44.6 m/s (`inputs.json`). Exposed frontal area of the camera is 4,980 mm² facing forward and 7,340 mm² yawed 90°. Assumed Cd 1.0 × 1.25 for interference with the cove. Not tested.

| Load case | Drag on camera (N) | Moment at mount face (N·m) | Vertical (N) |
|---|---|---|---|
| Cruise 20 m/s (forward → yawed) | 1.5 → 2.3 | 0.14 → 0.22 | 2.6 (1 g) |
| Top speed 44.6 m/s, limit | 7.6 → 11.2 | 0.72 → 1.06 | 2.6 |
| Top speed, ultimate (×1.5) | 16.8 | 1.6 | 4.0 |
| Hard landing on station, 5 g limit / ×1.5 ultimate | ~0 | ~0 | 13.2 / 19.9 |

| Item | Ultimate load | Capacity / stress |
|---|---|---|
| Mount screws (4 × M3, Ø32 PCD) | about 40 N tension per screw | Pull-through > 1 kN (2 mm G10 + 0.99 mm roof) |
| Shelf → NF1/NF2 | about 35 N couple per frame | Bond shear about 0.06 MPa |
| Nose joint, x 179 | about 3 N·m | About 1.5 MPa in the skin ring; carried by the band spigot |
| Cove skin under q = 1.2 kPa | — | 0.66 mm liner + NF3 arch: about 0.16 mm deflection (0.33 mm would drum) |

**Not covered by strength:**
- The camera adds about 25–35 % to cruise drag (pusher cruise thrust 6.62 N).
- It gives about 0.12–0.18 N·m nose-down at cruise.
- The camera's own gimbal must be rated for 20–45 m/s airflow.

## 2. Tooling

| Tool | Description |
|---|---|
| T1 – Nose female mold, L and R | Printed half-cups split on the XZ plane, 15 mm bolt flanges with dowels, trim line scribed at x 179. Seal, sand to 600, wax + PVA |
| T2 – Cove liner plug (male) | Printed solid of the cove cavity + R8 lip + flush skin strip + 10 mm flange surface. **Print in two halves split at y = 0** so it releases from the slight undercut at the side lips |
| T3a – Opening trim template | One per shell half; opening edge = cove offset 4.5–13.5 mm |
| T3b – Station comb | Bar across the mold flange with slots at x 55.5, 104, 135, 162.5; holds the frames square |
| T3c – Joint cradle | V-blocks for nose + fuselage alignment |
| T3d – Mount drill template | 4 × Ø3.4 on a Ø32 PCD at 45° + Ø12 centre |
| Flat parts | NF1–NF4, shelf (2 mm), deck: G10 DXFs from CAD sections, 0.3–0.5 mm undersize for the bond line |

## 3. Layups

Room-temperature epoxy, same system as the fuselage. Peel ply on every surface that will be bonded later. Vacuum bag the open layups.

1. **Shell halves (T1):** 2 plies GFRP 0/45 (0.33 mm), plus 2 extra plies in a 15 mm band round the opening and at the aft 20 mm. Cure, and keep the halves **in their molds**. Trim the opening with T3a while in the mold.
2. **Cove liner (T2):** 4 plies (0.66 mm), plus 2 plies on the roof (doubler). Trim the flange to 10 mm with a template, then demold.
3. **G10 parts:** cut, deburr, and scuff the bond edges (80 grit).

## 4. Assembly sequence

Everything inside the nose goes in while the **left half is open in its mold**. The right half then closes like a lid.

1. **Liner into the left half.** Dry fit. Bond the left side of the 10 mm flange with flocked epoxy. The right side stays dry for now.
2. **Frames.** Place NF1, NF2, NF3 and NF4 in the station comb. Bond the left edges to the skin and NF1/NF2/NF3 to the liner. After gel, add a 15 mm glass-tape fillet on both faces.
3. **Shelf: nutplate installation (secondary bonding).**
   - (a) On the bench, drill the shelf with T3d: 4 × Ø3.4 on a Ø32 PCD at 45°, plus Ø12.
   - (b) Fit 4 self-locking 2-lug M3 nutplates (MS21069/NAS1068 style, or Click Bond bonded nutplates) on the shelf top. Rivet through the lugs (2 mm / 3/32 in) plus epoxy, or bond only. Run waxed M3 alignment screws up from below into each nutplate while it cures, so they stay on-axis and no epoxy reaches the threads. Keep fillets out of the Ø12 hole.
   - (c) Flock the shelf onto the liner roof, bond its ends to NF1/NF2, and fillet the left side edge.
   - (d) Back-drill the roof and doubler from below through the shelf holes.

   Once the nose is closed, these nutplates are sealed in and are not serviceable. The camera screws thread in from below.
4. **Close the right half.** Apply flocked epoxy to every right-side edge (liner flange, frames, shelf side) and seam strips on the left flanges. Close the right mold on its dowels and bolt it. Press the top seam from inside (balloon or foam). Cure.
5. **Demold.** Split the molds sideways. Trim the aft edge at x 179. Fill the outer lip joint with microballoon, sand it to R8, and prime.
6. **Deck and FC.** Through the open Ø89 aft end, bond the deck and adjust strips onto NF3/NF4. Fit and wire the FC. Route the camera cable up through the Ø12 hole, then aft through the NF2 lightening hole (grommet strip on its edge).
7. **Joiner band (fuselage side).** Fit the 4 joint nutplates on the band's inner face (riveted or bonded, waxed alignment screws), then bond the band into the fuselage shells at x 179–186. These nutplates stay serviceable: with the nose off, the front of the band is open.
8. **Fit the nose.** Using the cradle, slide the nose over the band spigot (x 164–179) until it seats on NF4. Fit 4 × ISO 7380 M3 × 6 button-head screws (blue threadlocker, snug). To remove the nose, unplug the harness and take out the 4 screws.
9. **Camera.** Bolt the camera mount plate to the 4 shelf nutplates from below (for example ISO 4762 M3 × 8 with threadlocker).

## 5. Open items

1. FC and camera harness disconnect at the joint.
2. Real camera mount pattern (nutplates can move up to about Ø38 PCD).
3. Real FC length vs NF2 (REF Cube starts at x 105.5).
4. Camera gimbal airspeed rating.
5. Lap-shear coupon of the chosen epoxy on G10.
6. Export T1–T3 tooling from the CAD.
