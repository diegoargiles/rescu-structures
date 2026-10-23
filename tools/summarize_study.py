import json,html
from pathlib import Path
R=Path(__file__).resolve().parents[1]
r=json.loads((R/'reports/p04/results.json').read_text(encoding='utf-8'))
old=json.loads((R/'reports/reproduced-p03/results.json').read_text(encoding='utf-8'))
build=json.loads((R/'reports/native-audit/build.json').read_text())
audit=json.loads((R/'reports/native-audit/candidate_audit.json').read_text())
groups={}
for p in build['new_parts']:groups[p['attachment_group']]=groups.get(p['attachment_group'],0)+p['mass_kg']*1000
foam=sum(x['removed_mm3'] for x in build['foam_cuts'])*32e-6
refinement=json.loads((R/'reports/native-audit/refinement.json').read_text())
foam+=sum(x['removed_mm3'] for x in refinement['foam_cuts'])*32e-6
m=r['mass'];m0=old['mass']
lines=['# P04 attachment study — result and review gates','', '**Status: preliminary candidate, not finished structural mass or fabrication release.**','', '## Reconciled mass budget','']
for name,key,scale,unit in [('P03 structural budget','structural_budget_kg',1000,'g'),('P03 accounted aircraft','accounted_aircraft_kg',1,'kg'),('P03 sizing aircraft','sizing_aircraft_kg',1,'kg')]:lines.append(f'- {name}: {m0[key]*scale:.4f} {unit}.')
for name,key,scale,unit in [('P04 candidate structural budget','structural_budget_kg',1000,'g'),('P04 accounted aircraft','accounted_aircraft_kg',1,'kg'),('P04 sizing aircraft','sizing_aircraft_kg',1,'kg')]:lines.append(f'- {name}: {m[key]*scale:.4f} {unit}.')
lines += ['',f"Structural increase: {(m['structural_budget_kg']-m0['structural_budget_kg'])*1000:.3f} g. Aircraft increase: {(m['accounted_aircraft_kg']-m0['accounted_aircraft_kg'])*1000:.3f} g. The difference is the 42 g moved out of embedded motor mount allowances.",f'Explicit new installation budgets: 74.000 g. Old local-hardware allowance removed: 71.683 g. Reserve remains 200.000 g outside structure and CG.',f'Exact recorded foam displacement: {foam:.4f} g. These small deductions do not eliminate all geometric overlap risks.','','## New CAD material by attachment group','']
lines += [f'- {name}: {mass:.3f} g.' for name,mass in groups.items()]
lines += ['', 'These are assumed candidate construction dimensions integrated by FreeCAD, not verified manufactured quantities. Retained wing/tail finish budgets total 48.808 g. See the mass ledger for individual parts.','', '## Geometry checks','', f"Native valid: {audit['native_valid']}; STEP valid: {audit['step_valid']}. Native/STEP solid count: {audit['native_solids']}/{audit['step_solids']}. Remaining reported interference pairs: {len(audit['interferences'])}.",'','All positive-volume interferences below require review. Equipment proxies are not vendor-certified geometry. Structural overlaps make the untrimmed candidate subtotal conservative and prevent calling it a net installed mass. The 71.683 g hardware allowance and 200 g reserve are nevertheless reconciled exactly.','']
lines += [f"- {x['part']} / {x['other']}: {x['volume_mm3']:.3f} mm³ ({x['kind']})." for x in audit['interferences']]
lines += ['', '## STEP transfer limitation','', 'The native FCStd is the review authority. The full STEP has an invalid inherited fuselage shell and fails volume agreement. A shell-excluded export has valid solids but still fails the aggregate volume screen (1.171% difference); NURBS conversion also changes shell volume. No STEP is accepted or included in the delivery ZIP. Diagnostic reports are retained. Further transfer diagnosis is required before downstream STEP use.',f"Remaining pairwise duplicate-material upper bound: {audit['pairwise_duplicate_material_upper_bound_g']:.3f} g. This is not a mass correction: triple intersections may be counted repeatedly and pre-existing P03/P03 overlaps were not audited.",'', '## Updated load screens','']
lines += [f"- {x['case']}: {x['screen_status']}, tip deflection {x['tip_total_limit_mm']:.2f} mm, twist {x['tip_twist_limit_deg']:.2f}°." for x in r['load_cases'][:4]]
lines += [f"- Aircraft CG X: {m0['aircraft_cg_m'][0]*1000:.2f} → {m['aircraft_cg_m'][0]*1000:.2f} mm, provisional. Battery held fixed."]
lines += ['', '## Required review','', 'Resolve CAD interfaces and clearance findings; choose bonded versus detachable center wing; confirm motor drawings/torque/max thrust; agree loads and retention requirements; validate layup/adhesive and joints. Payload/servo/control mounts, environmental effects, landing/gust/fatigue and shell buckling remain open. See docs/ATTACHMENT_STUDY.md for assumptions and load paths.']
text='\n'.join(lines)+'\n';(R/'reports/p04/REVIEW.md').write_text(text,encoding='utf-8')
page='<!doctype html><meta charset="utf-8"><title>RescU P04 attachment review</title><style>body{font:16px/1.5 system-ui;max-width:1000px;margin:40px auto;padding:0 20px;color:#20313d}pre{white-space:pre-wrap;font:inherit}img{max-width:100%}</style><h1>RescU P04 attachment review</h1><img src="../../cad/Attachment_Study_Preview.png"><pre>'+html.escape(text)+'</pre>'
(R/'reports/p04/REVIEW.html').write_text(page,encoding='utf-8')
summary=dict(before=m0,after=m,new_CAD_groups_g=groups,foam_removed_g=foam,interference_count=len(audit['interferences']),status='CANDIDATE; NOT NET INSTALLED MASS')
(R/'reports/p04/comparison.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
