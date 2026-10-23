"""Independent ledger deltas, equilibrium and limiting behavior tests."""
import copy,json,math,unittest
from pathlib import Path
import RescU_Structures_V4 as v
from attachment_checks import evaluate
R=Path(__file__).resolve().parent
class Attachments(unittest.TestCase):
 def setUp(self):
  self.c=v.read(R/'inputs.json');self.s=v.read(R/'data/cad_snapshot_p04.json')
  self.rows,self.m=v.mass_ledger(self.c,self.s)
 def test_mass_reconciliation(self):
  old=v.read(R/'data/inputs_p03.json');snap=v.read(R/'data/cad_snapshot.json');_,m0=v.mass_ledger(old,snap)
  delta_cad=self.m['cad_structure_kg']-m0['cad_structure_kg']
  delta_allowances=.074-.07168293725120682
  self.assertAlmostEqual(self.m['structural_budget_kg']-m0['structural_budget_kg'],delta_cad+delta_allowances)
  self.assertAlmostEqual(self.m['accounted_aircraft_kg']-m0['accounted_aircraft_kg'],delta_cad+delta_allowances-.042)
  self.assertAlmostEqual(self.m['sizing_aircraft_kg']-self.m['accounted_aircraft_kg'],.2)
 def test_reactions_and_scaling(self):
  cases=[dict(case='V-tail at top speed',root_moment_limit_Nm=1),dict(case='wing',root_moment_limit_Nm=10)]
  a=evaluate(self.c,self.s,self.m,cases)
  for r in a['arm_reactions']:
   self.assertAlmostEqual(r['force_residual_N'],0);self.assertAlmostEqual(r['moment_residual_Nm'],0)
  self.assertTrue(any(r['front_N']<0 or r['rear_N']<0 for r in a['arm_reactions']))
  c2=copy.deepcopy(self.c);c2['attachment_design']['motor_plate_thickness_mm']*=2
  b=evaluate(c2,self.s,self.m,cases)
  self.assertAlmostEqual(b['checks'][0]['demand'],a['checks'][0]['demand']/4)
 def test_cad_and_installation_ids(self):
  ids=[r['name'] for r in self.rows];self.assertEqual(len(ids),len(set(ids)))
  self.assertFalse(any(r['name']=='Provisional local hardware' for r in self.rows))
  self.assertAlmostEqual(sum(r.get('removed_mount_allowance_kg',0) for r in self.c['components']),.042)
  for r in self.s['structural_parts']:
   self.assertTrue(r['valid']);self.assertGreater(r['volume_mm3'],0)
if __name__=='__main__':
 import sys
 result=unittest.main(exit=False).result
 out=R/'reports/p04';out.mkdir(parents=True,exist_ok=True)
 (out/'attachment_validation.json').write_text(json.dumps(dict(tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),passed=result.wasSuccessful(),scope='Mass reconciliation, allowance uniqueness, reaction equilibrium and plate-thickness scaling; not physical qualification'),indent=2))
 sys.exit(0 if result.wasSuccessful() else 1)
