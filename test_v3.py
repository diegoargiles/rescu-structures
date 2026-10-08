"""Independent analytical checks and regression guards for numerical screening."""
import unittest
from dataclasses import replace
from math import pi
import RescU_Structures_V3 as model


class BeamChecks(unittest.TestCase):
    def test_uniform_cantilever(self):
        # Closed-form uniform beam: V=qL, M=qL²/2, delta=qL⁴/(8EI)
        # and shear delta=qL²/(2 kGA); constant torsion delta=mL²/(2GJ).
        n,L,q,EI,GA,GJ,m = 1000,2.,10.,400.,200.,300.,3.
        y=[L*i/n for i in range(n+1)]
        r=model.cantilever(y,[q]*(n+1),[m]*(n+1),[EI]*(n+1),[GA]*(n+1),[GJ]*(n+1))
        self.assertAlmostEqual(r["shear"][0],q*L,places=10)
        self.assertAlmostEqual(r["moment"][0],q*L*L/2,places=10)
        self.assertAlmostEqual(r["bend"][-1],q*L**4/(8*EI),places=6)
        self.assertAlmostEqual(r["shear_deflection"][-1],q*L*L/(2*GA),places=10)
        self.assertAlmostEqual(r["twist"][-1],m*L*L/(2*GJ),places=10)

    def test_tip_point(self):
        n,L,F,EI = 1000,1.,10.,100.
        y=[L*i/n for i in range(n+1)]
        r=model.cantilever(y,[0.]*(n+1),[0.]*(n+1),[EI]*(n+1),[1e30]*(n+1),[1e30]*(n+1),[(L,F,0.)])
        self.assertAlmostEqual(r["moment"][0],F*L,places=10)
        self.assertAlmostEqual(r["bend"][-1],F*L**3/(3*EI),places=7)

    def test_invalid_point(self):
        with self.assertRaises(ValueError):
            model.cantilever([0.,1.],[0.,0.],[0.,0.],[1.,1.],[1.,1.],[1.,1.],[(2.,1.,0.)])


class SectionChecks(unittest.TestCase):
    def test_thin_rectangle_torsion(self):
        b,h,t,G=.2,.02,.0005,4e9
        # Classical closed rectangular tube with median dimensions b,h.
        analytical=2*G*t*b*b*h*h/(b+h)
        self.assertAlmostEqual(model.closed_skin_gj(b*h,2*(b+h),G,t),analytical)
    def test_rectangle_moments(self):
        # Independent rectangle area and second moment, not an airfoil snapshot.
        b,h=.2,.02
        a,mz,iz,mx=model.strip_moments([0.,b],[h/2]*2,[-h/2]*2)
        self.assertAlmostEqual(a,b*h)
        self.assertAlmostEqual(mz,0.)
        self.assertAlmostEqual(iz,b*h**3/12)
        self.assertAlmostEqual(mx,b*b*h/2)

    def test_naca_depth_and_closure(self):
        x,u,l=model.profile("NACA0010")
        self.assertLess(abs(max(a-b for a,b in zip(u,l))-.10),.001)
        self.assertAlmostEqual(u[-1]-l[-1],0.,places=12)

    def test_sd_no_extrapolated_negative_thickness(self):
        _,u,l=model.profile("SD7037",1000)
        self.assertGreaterEqual(min(a-b for a,b in zip(u,l)),-1e-12)
        self.assertAlmostEqual(u[0],l[0])

    def test_airfoil_mesh_convergence(self):
        s,f=model.WING_SKIN,model.FOAMS["H60"]
        a=model.section(.165,s,f,n=240)
        b=model.section(.165,s,f,n=960)
        for key in ("EI","GJ","core_area"):
            self.assertLess(abs(a[key]/b[key]-1),.015,key)

    def test_increasing_skin_stiffness(self):
        s,f=model.WING_SKIN,model.FOAMS["H60"]
        thin=model.section(.165,replace(s,angles=(0.,45.,0.)),f)
        thick=model.section(.165,s,f)
        self.assertGreater(thick["EI"],thin["EI"])
        self.assertLess(thick["core_area"],thin["core_area"])


class LaminateChecks(unittest.TestCase):
    def test_isotropic_rotation(self):
        # Isotropic ply invariance verifies strain/shear conventions in Qbar.
        E,nu=20e9,.2
        s=replace(model.WING_SKIN,E1=E,E2=E,G12=E/(2*(1+nu)),nu12=nu,angles=(37.,))
        lam=model.laminate(s)
        self.assertAlmostEqual(lam["E"]/E,1.,places=12)
        self.assertAlmostEqual(lam["G"]/(E/(2*(1+nu))),1.,places=12)

    def test_woven_zero_ninety_equivalence(self):
        a=model.laminate(replace(model.WING_SKIN,angles=(0.,)))
        b=model.laminate(replace(model.WING_SKIN,angles=(90.,)))
        self.assertAlmostEqual(a["E"]/b["E"],1.)

    def test_bias_ply_increases_torsional_stiffness(self):
        a=model.laminate(replace(model.WING_SKIN,angles=(0.,)))
        b=model.laminate(replace(model.WING_SKIN,angles=(45.,)))
        self.assertGreater(b["G"],a["G"])

    def test_asymmetric_stack_rejected(self):
        with self.assertRaises(ValueError):
            model.laminate(replace(model.WING_SKIN,angles=(0.,45.)))


class DesignChecks(unittest.TestCase):
    def test_confirmed_battery_mass_and_independent_cg(self):
        self.assertIsNot(model.P,model.v2.P)
        self.assertEqual(model.P["battery_mass_kg"],.900)
        self.assertEqual(model.v2.P["battery_mass_kg"],.650)
        mass=model.aircraft_mass()
        parts=mass["components"]
        battery=next(p for p in parts if p["name"]=="Battery")
        self.assertEqual(battery["mass_kg"],.900)
        # Direct first moment checks that the helper did not retain V2's 650g.
        cg=sum(p["mass_kg"]*p["x_m"] for p in parts)/sum(p["mass_kg"] for p in parts)
        target=model.P["x_main_wing_le_m"]+model.P["cg_target_aft_of_wing_le_m"]
        self.assertAlmostEqual(cg,target,places=12)

    def test_force_deflection_linearity(self):
        a=model.panel_case("check",model.WING_SKIN,model.FOAMS["H60"],20.,1.5,n=100)
        b=model.panel_case("check",model.WING_SKIN,model.FOAMS["H60"],40.,1.5,n=100)
        for key in ("tip_total_limit_mm","root_moment_limit_Nm","ply_failure_index_ultimate"):
            self.assertAlmostEqual(b[key]/a[key],2.)

    def test_beam_mesh_convergence(self):
        a=model.panel_case("check",model.WING_SKIN,model.FOAMS["H60"],60.,1.5,n=100)
        b=model.panel_case("check",model.WING_SKIN,model.FOAMS["H60"],60.,1.5,n=400)
        for key in ("tip_total_limit_mm","root_moment_limit_Nm"):
            self.assertLess(abs(a[key]/b[key]-1),.005)

    def test_removed_members_and_mass_reserve(self):
        mass=model.aircraft_mass()
        names={p["name"] for p in mass["components"]}
        self.assertFalse(names & {"Wing spars","Wing foam ribs","Aft CFRP spine","Wing covering"})
        self.assertGreaterEqual(mass["sizing_mass_kg"],mass["known_mass_lower_bound_kg"]+.199999)
        self.assertIn("INCOMPLETE",mass["mass_status"])

    def test_screen_does_not_release_aircraft(self):
        _,cs=model.cases(n=100)
        self.assertTrue(all("UNRESOLVED" in c["overall_status"] for c in cs))


if __name__=="__main__":
    unittest.main()
