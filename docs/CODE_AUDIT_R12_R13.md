# Existing analysis audit

Reviewed main at 73391e627e078dced2644a18da135a09c447282f. This is the V4/P03 configuration, not the R12 CAD.

| Existing work | What it covers | Limit for R12/R13 |
|---|---|---|
| inputs.json | +3/-1.5 limit n; 1.5 ultimate multiplier; 40N and 69.2N total VTOL scenarios; mass/material estimates | Not derived from a reviewed current mission envelope; old X313/X448 arm supports versus R12 X335/X405 |
| RescU_Structures_V4.py + engine/analytic_v3.py | Idealized wing bending/shear/twist, ply/core/spar screens, asymmetric VTOL, tail loads, mass/CG, positive-n screen boundary | Older continuous core/section assumptions and idealized root; not the current ribbed wing/joints |
| reports/baseline/SUMMARY.md | 3g tip 23.82mm and twist -1.44deg; at 70% stiffness twist -2.06deg fails assumed2deg screen | Historical outputs only. Reported ideal boundary4.327g is NOT aircraft capability |
| Local cad-refinement/analyze_r07.py | Arm supports335/405mm; rectangular/round tube trade; symmetric/asymmetric17.3N cases; preload/bearing demand; assumed0.2Nm torque example | Thrust-only; assumed E/G; no current laminate or complete joint qualification |
| Local cad-refinement/fea_r08.py and saved results | Local aluminum clevis analysis; three meshes; reaction balance54.371N; finest displacement0.000205mm and peak3.399MPa | Local fixture/surrogate only, not whole wing or new composite sockets; not SolidWorks FEA |

The repository's old mass and CG must not be relabeled R12/R13. Four motor+prop allocations of86.08g each conflict with the current108g motor-only reference. Geometry, actual equipment, material and component mass reconciliation are required.

R13 arm_load_screen.py reuses the two-support analytical approach with current geometry, isolates demand comparisons, checks equilibrium and support displacement, and deliberately does not invent material strength or an overall PASS.
