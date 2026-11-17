import json, csv
bom = json.load(open('/home/claude/work/out/bom.json'))
S = [(r['part'], r['mass_g'], r['cx'], r['cy'], r['cz']) for r in bom if r['mass_g'] > 0]
EQ = [  # name, g, x, y, z, source
 ('Lift motors UM2807 x4 (52 g w/ leads)', 4*52.0, 385.0, 0, 2.0, 'Unusual Machines page; X avg of 170/600'),
 ('Lift props 10in x4 (ASSUMED 20 g)', 4*20.0, 385.0, 0, 17.0, 'assumption'),
 ('Battery 6S2P M65A (12x74.5 + 50 g)', 944.0, 300.0, 0, 1.25, 'inputs.json conservative; modules at 237.5/362.5'),
 ('Camera / AI', 350.0, 60.0, 0, 0, 'inputs.json; nose location provisional'),
 ('Heat sink', 30.0, 200.0, 0, 0, 'inputs.json'),
 ('ESCs + wiring', 150.0, 500.0, 0, -10.0, 'inputs.json mass; R13 ESC deck position'),
 ('Payload (flotation)', 360.0, 350.0, 0, -55.0, 'inputs.json'),
 ('Payload magnet', 10.0, 350.0, 0, -55.0, 'inputs.json'),
 ('V-tail servos x2', 43.8, 945.0, 0, 1.0, 'HS-5085MG, R13 clearance envelopes'),
 ('Other servo allocation (UNRESOLVED)', 136.2, 800.0, 0, 0, 'inputs.json residual'),
 ('Pusher motor+prop+mount (MT4008, 13x8)', 148.9, 1125.0, 0, 0, 'inputs.json'),
]
M = sum(s[1] for s in S) + sum(e[1] for e in EQ)
def mom(i): return sum(s[1]*s[2+i] for s in S) + sum(e[1]*e[2+i] for e in EQ)
cg = [mom(i)/M for i in range(3)]
ms = sum(s[1] for s in S)
out = dict(structure_g=round(ms, 1), equipment_g=round(sum(e[1] for e in EQ), 1), total_g=round(M, 1),
           cg_mm=[round(c, 1) for c in cg], target_cg_x_mm=260+134.4, neutral_point_x_mm=260+148.0,
           mac_mm=135.1, mac_le_x_mm=324.3)
xb_now = 300.0; mb = 944.0
need = (M*out['target_cg_x_mm'] - (mom(0) - mb*xb_now))/mb
out['battery_x_for_target_mm'] = round(need, 1)
out['static_margin_pct_MAC_at_current_cg'] = round((out['neutral_point_x_mm']-cg[0])/135.1*100, 1)
W = M/1000*9.80665
out['hover_front_pair_N'] = round(W*(600-cg[0])/430, 2); out['hover_rear_pair_N'] = round(W*(cg[0]-170)/430, 2)
out['equipment'] = EQ
json.dump(out, open('/home/claude/work/deliver/cg.json', 'w'), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != 'equipment'}, indent=1))
