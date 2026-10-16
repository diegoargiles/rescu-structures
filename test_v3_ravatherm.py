"""Independent section/mass checks and integration guards for Ravatherm V3."""
import unittest
from dataclasses import replace
from math import pi
import RescU_Structures_V3 as baseline
import RescU_Structures_V3_Ravatherm as m


class RavathermChecks(unittest.TestCase):
    def setUp(self):
        self.spar=m.SPAR

    def tearDown(self):
        m.SPAR=self.spar

    def test_requested_configuration_and_baseline_isolation(self):
        self.assertAlmostEqual(m.WING_SKIN.thickness,.00033)
        self.assertAlmostEqual(m.P['fuselage_shell_thickness_m'],.00033)
        self.assertEqual(vars(m.TAIL_SKIN), vars(baseline.TAIL_SKIN))
        self.assertEqual(baseline.P['fuselage_shell_thickness_m'],.0004)
        self.assertAlmostEqual(baseline.WING_SKIN.thickness,.000895)
        self.assertEqual(m.FOAMS['RAVATHERM'].shear_strength,.25e6)

    def test_tube_annulus_closed_form(self):
        a,i=m.tube_properties(.014,.002)
        self.assertAlmostEqual(a,pi*(.014**2-.010**2)/4)
        self.assertAlmostEqual(i,pi*(.014**4-.010**4)/64)
        with self.assertRaises(ValueError):
            m.tube_properties(.008,.004)

    def test_uniform_tube_mass_and_cg(self):
        m.SPAR=replace(m.SPAR,root_od=.008,tip_od=.008,wall=.001,tip_wall=.001)
        g=m.spar_geometry()
        r=m.spar_mass(m.FOAMS['RAVATHERM'])
        self.assertAlmostEqual(r['tube_kg'],2*g['tube_length_each_m']*pi*(.008**2-.006**2)/4*1600)
        self.assertAlmostEqual(r['x_m'],(g['root_x_m']+g['tip_x_m'])/2)

    def test_neutral_axis_and_parallel_axis(self):
        c=.165
        f=m.FOAMS['RAVATHERM']
        a=m.section(c,m.WING_SKIN,f)
        r=m.reinforced_section(c,m.WING_SKIN,f,0.,.7)
        area,I=m.tube_properties(.014,.002)
        es=m.laminate(m.WING_SKIN)['E']
        z=(es*a['skin_area']*a['zbar']+m.SPAR.E*area*r['spar_z'])/(es*a['skin_area']+m.SPAR.E*area)
        expected=a['EI']+es*a['skin_area']*(a['zbar']-z)**2+m.SPAR.E*(I+area*(r['spar_z']-z)**2)
        self.assertAlmostEqual(r['EI'],expected)
        self.assertGreater(r['clearance_m'],0)
        self.assertLess(r['core_area'],a['core_area'])
        self.assertEqual(r['GJ'],a['GJ'])  # no unvalidated tube torsion credit

    def test_reject_oversize_tube(self):
        m.SPAR=replace(m.SPAR,root_od=.030)
        with self.assertRaises(ValueError):
            m.reinforced_section(.165,m.WING_SKIN,m.FOAMS['RAVATHERM'],0.,.7)

    def test_no_spar_recovery(self):
        m.SPAR=replace(m.SPAR,enabled=False)
        f=m.FOAMS['RAVATHERM']
        self.assertEqual(m.reinforced_section(.165,m.WING_SKIN,f,0.,.7),m.section(.165,m.WING_SKIN,f))
        self.assertEqual(m.spar_mass(f)['tube_kg'],0)

    def test_mass_accounting_and_mesh_convergence(self):
        mass,cs=m.cases(n=200)
        self.assertAlmostEqual(sum(p['mass_kg'] for p in mass['components']),mass['known_mass_lower_bound_kg'])
        self.assertTrue(all(c['screen_status']=='PASS' for c in cs))
        self.assertLess(cs[0]['deflection_screen_utilization']/.7,1)
        _,fine=m.cases(n=400)
        self.assertLess(abs(fine[0]['tip_total_limit_mm']/cs[0]['tip_total_limit_mm']-1),.005)
        self.assertLess(abs(fine[0]['root_moment_limit_Nm']/cs[0]['root_moment_limit_Nm']-1),.005)


if __name__=='__main__':
    unittest.main()
