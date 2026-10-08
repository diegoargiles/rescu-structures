# Foam/GFRP exploration for a 2.76 kg aircraft target

Exploration dated 2026-10-08, updated for Diego's confirmed **900 g battery** from the revised report. V3 uses that mass; the original V2 file remains unchanged at 650 g. No exploratory layup replaces the V3 comparison candidate, and team CAD remains unchanged. This is not a flight approval. Run `explore_mass_target.py` for the recorded calculation; detailed output is `results/mass_target/exploration.json`.

## Budget from the current code

Historical V2 calculates 2.759676 kg with its 650 g battery. Evaluating V2 with the same confirmed 900 g battery, without modifying V2, gives **3.009676 kg**. V3 calculates **3.649600 kg** before its separate 0.200 kg sizing reserve. The foam/GFRP candidate therefore adds 0.639924 kg versus the matched-battery V2 calculation, and exceeds the 2.760 kg target by **0.889600 kg** before missing construction is added.

With the 900 g battery, nonstructural code entries total **2.473227 kg**. At 2.760 kg, the entire accounted structure has only **0.286773 kg** available. Retained fuselage shell, arms and payload plate already consume **0.305800 kg**, exceeding that budget before either wing, tail or hardware is counted. Adding the current tail (0.047473 kg) and retaining V3's 10% structural hardware allowance leaves a mathematically negative wing budget of -0.092571 kg. This means wing-skin optimization alone cannot reach 2.76 kg with those other code inputs fixed. Missing fuselage foam, designed joints and additional equipment would increase mass further. The 200 g reserve is not included in this target budget; removing a reserve is not a physical mass saving.

Current wing/tail foam totals 0.080409 kg. A density-only change from 60 to 48 kg/m3 at the same volume would save 0.016082 kg before hardware-allowance effects. This does not authorize changing foam grade: modulus/strength and bond behavior must be updated. Foam density changes cannot account for the approximately 0.890 kg gap to the target.

## Uniform lighter glass skins explored

All candidates keep H60, the existing tail, assumed laminate properties and mission loads. The existing minimum load-sizing mass of 3.2 kg is retained, even where the calculated known mass is lower. No lower test load was chosen to make a candidate pass.

- Five 163 gsm plies: known aircraft 3.649600 kg, wing 0.716156 kg; wing deflection 25.82 mm nominal / 36.89 mm at 70% stiffness. Nominal screens across six cases pass, but the reduced-stiffness deflection screen fails the proposed 35 mm limit.
- Four 163 gsm plies: known aircraft 3.521034 kg, wing 0.599278 kg; 33.26 / 47.51 mm. Nominal screens pass but the reduced-stiffness deflection screen fails.
- Three 163 gsm plies: known aircraft 3.392543 kg, wing 0.482469 kg; 37.94 / 54.19 mm. Deflection screen fails.
- Three 80 gsm plies: known aircraft 3.196643 kg, wing 0.304378 kg; 67.40 / 96.28 mm. Deflection and assumed maximum-stress ply screen fail (worst index 1.266).
- Two 80 gsm plies: known aircraft 3.133594 kg; fails assumed strength and deflection screens.
- One 80 gsm ply: known aircraft 3.070568 kg; fails assumed strength and deflection screens badly. Such large computed displacements exceed the intended small-deflection regime; this is a rejection diagnostic, not a trustworthy deformed-shape prediction.

The lighter cloth candidates reuse the same provisional cured woven-laminate constants. Different cloth/process properties must be measured. No wrinkling, buckling, bond or attachment pass is issued for any row.

## Candidate development directions

1. Keep the foam core and GFRP as the initial constraints. Study a light continuous skin with localized spanwise glass reinforcement around bending load paths and motor/root attachments, with a defined closed torsion path. Specify fabric orientation, ply drops, bond areas and tapered transitions. V3's uniform skin section cannot currently evaluate such a spatially varying layup; it needs a separate implementation and numerical verification. Savings and adequacy are not established.
2. Control cured fiber/resin content and bond/finish mass using representative manufactured coupons. Do not change modulus upward or laminate weight downward without evidence. Excess resin removal can reduce manufacturing excess; it cannot guarantee the required 890 g saving.
3. Keep the confirmed 900 g battery and reconcile every other equipment entry with actual installed mass, including motors, controllers, wiring, payload and avionics. This is necessary because the current fixed equipment plus retained structure leaves no physical wing budget at 2.76 kg. Endurance must be checked before discussing a smaller battery; it is not an authorized baseline change.
4. Define fuselage foam around equipment cavities as a real shell/core layout rather than automatically filling the complete external fuselage volume. Its volume and load transfer are still unresolved. Do not deduct it from a mass model that has not included it.
5. If the all-glass/foam candidate cannot fit the budget, discuss a change in material or the strict no-spar requirement with the faculty/team. Localized carbon skin reinforcement would change the current all-GFRP exterior constraint; a lightweight spar is a separate departure from the no-internal-spars constraint. Neither is authorized as the baseline by this exploration.

No 2.76 kg structurally acceptable configuration has been demonstrated. The next meaningful comparison should couple a completed mass budget to localized skin/core/joint geometry, agreed stiffness/load criteria, measured materials and representative structural testing.

## Reviewed primary references

- R&G 163 gsm Interglas 92110: https://www.r-g.de/en/art/190120/ — calculated cured ply 0.179 mm / 291 g/m2 at 35% fiber volume; excess resin and manufacturing variation notes.
- R&G 80 gsm glass: https://www.r-g.de/en/art/190110 — calculated cured ply 0.088 mm / 143 g/m2 at 35% fiber volume; exact schedule depends on core, geometry and loading.
- Diab core/sandwich guide: https://www.diabgroup.com/media/q5yldbe4/diab-guideline-to-core-and-sandwich.pdf — skin/core/bond roles, directional properties and minimum-property guidance.
- Diab Divinycell H Rev25, September 2025: https://diab-media.azureedge.net/eyajkrhd/diab-divinycell-h-sep-2025-rev25-si.pdf — H45 nominal density 48 versus H60 60 kg/m3, with lower minimum shear properties. No foam grade was changed in the code.
