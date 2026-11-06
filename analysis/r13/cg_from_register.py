"""Compute CG only after every registry row is resolved. No silent blank-to-zero."""
import csv,json,sys
from pathlib import Path
p=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/'reports/connection_study/equipment_mass_location_register.csv'
rows=list(csv.DictReader(p.open()));missing=[];mom=[0.,0.,0.];mass=0.
for r in rows:
 try:
  m=float(r['mass_g']);xyz=[float(r[a+'_mm']) for a in 'xyz']
  assert m>=0
 except (ValueError,AssertionError):missing.append(r['component']);continue
 mass+=m
 for i in range(3):mom[i]+=m*xyz[i]
if missing:print(json.dumps({'status':'INCOMPLETE: no aircraft CG released','missing':missing},indent=2));sys.exit(2)
assert mass>0
print(json.dumps({'mass_g':mass,'cg_mm':[a/mass for a in mom],'warning':'Review mass/position status fields: complete numeric inventory does not turn estimates into measurements.'},indent=2))
