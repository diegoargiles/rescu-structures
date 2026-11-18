# R15 full-aircraft CAD (November 9, 2026)

Rebuilt in CadQuery from this repository's planforms/airfoils and the R13 component positions. Frame = R13 (X aft from nose, Y right, Z up, mm). Superseded by [R16](../r16/README.md) for the wing root joints and landing provisions; kept as the baseline R16 was built from.

| File | Content |
|---|---|
| `RescU_R15_Full_Aircraft.step.zip` | Full assembly STEP (99.8 MB unzipped; zipped for GitHub's file limit). SHA-256 of the STEP: `1cd88f0d40571352f0bec842d256f35b2fcfd859d0a484597aad8e8f84849081` |
| `RescU_R15_BOM_CAD_masses.csv` | 99-part CAD mass BOM |
| `cg.json` | Mass / CG estimate |
| `wing_screen.json` | +3 g × 1.5 wing screen |
| `interference_full.json` | Full-assembly interference (489 pairs, one 0.15 mm³ seam-strip contact) |
| `scripts/` | CadQuery build scripts (`geom.py`, `wing.py`, `fuselage.py`, `build_boom.py`, `tail.py`, `assemble_full.py`, `cg.py`, `wing_screen.py`) |
| `renders/` | Review views |

## Mass and CG

Structure 960.0 g, equipment 2460.9 g, total 3420.9 g. CG x 406.1 mm vs target 394.4 (NP 408.0), static margin ≈ 1.4 % MAC.

## R15 changes vs R13

- Integrated molded booms (rib-tab saddle, 3× M3, molded motor pads, TPU landing feet)
- Wing: full-depth XPS core panels replace 14 foam ribs (skin buckling); telescoped spar OD10/8 → OD8/6.4 → OD6/4.4
- Joiner OD12/10 (was OD8/6); root adapter = 2 sockets + shear plate (was solid block)
- PTFE wire conduit root → boom saddle; tail hatch narrowed for V-tail spar roots

## Wing screen (+3 g × 1.5)

R15 full core + OD10/8 spar: spar 106 MPa, skin 33 MPa, wrinkling ratio ≈ 1.1 with 0.6 knockdown. Joiner OD12/10: 230 MPa (R13 OD8/6 was 588 MPa).

Known issue fixed in R16: the root adapter's joiner socket (OD 14.6) did not fit inside the 14.1 mm wing depth at the root and was trimmed 1.5 mm by the skin.
