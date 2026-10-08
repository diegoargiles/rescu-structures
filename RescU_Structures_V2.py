"""
RescU Structures Analysis V2
============================
Clean conceptual / preliminary structural model for the RescU VTOL fixed-wing UAV.

Coordinate convention
---------------------
    x = longitudinal, positive nose -> tail
    y = spanwise, positive left wing / negative right wing
    z = vertical

Source hierarchy used in this file
----------------------------------
1) Latest CAD measurements supplied by the Structures lead.
2) Team Conceptual Design Presentation.
3) Manufacturer / product data for propulsion masses.
4) Clearly-labelled engineering assumptions where the design is not frozen yet.

IMPORTANT
---------
This is a preliminary design model, not a certification-level structural analysis.
Values tagged ASSUMPTION should be replaced as CAD, materials, joints, and subsystem
locations are finalized. The model intentionally keeps those assumptions visible.

Primary structural questions answered by V2
--------------------------------------------
- What does the current structure weigh?
- Where is the resulting aircraft CG, and where should the battery be placed to hit
  the team's current target CG/static-margin reference?
- What are the first-order wing spar bending stresses and deflections?
- What are the first-order VTOL motor-arm stresses and deflections?
- Can the provisional payload magnet mounting plate carry the payload inertial load?
- What loads are applied to the aft structural spine from tail and pusher cases?
- Which values are still assumptions and therefore need team/CAD confirmation?

No third-party Python packages are required.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import atan, degrees, pi, sqrt
from pathlib import Path
from typing import Dict, List, Tuple
import csv


# =============================================================================
# 1. CONSTANTS / MATERIALS
# =============================================================================

G = 9.80665                 # m/s^2
RHO_AIR = 1.225             # kg/m^3, sea-level standard atmosphere


@dataclass(frozen=True)
class Material:
    name: str
    density_kg_m3: float
    E_Pa: float
    allowable_bending_Pa: float
    yield_Pa: float | None = None


MATERIALS = {
    # Engineering-property assumptions for preliminary sizing.
    # Replace with coupon/vendor laminate properties once material system is selected.
    "CFRP": Material(
        name="CFRP preliminary laminate",
        density_kg_m3=1600.0,
        E_Pa=70.0e9,
        allowable_bending_Pa=300.0e6,
    ),
    "GFRP": Material(
        name="GFRP preliminary laminate",
        density_kg_m3=1850.0,
        E_Pa=25.0e9,
        allowable_bending_Pa=150.0e6,
    ),
    "AL6061T6": Material(
        name="6061-T6 aluminum",
        density_kg_m3=2700.0,
        E_Pa=69.0e9,
        allowable_bending_Pa=276.0e6,
        yield_Pa=276.0e6,
    ),
}


# =============================================================================
# 2. AUTHORITATIVE / CURRENT INPUTS
# =============================================================================

P: Dict[str, float | int | str | bool] = {
    # -------------------------------------------------------------------------
    # Coordinate / aircraft geometry - latest CAD / team presentation
    # -------------------------------------------------------------------------
    "overall_length_m": 1.125,                  # CAD overall aircraft length
    "fuselage_length_m": 1.110,                 # latest CAD
    "fuselage_surface_area_m2": 0.257,          # latest CAD
    "x_main_wing_le_m": 0.260,                  # latest CAD, root LE from nose

    # Main wing - team aerodynamic geometry
    "wing_airfoil": "SD7037",
    "wingspan_m": 1.400,
    "wing_root_chord_m": 0.165,
    "wing_tip_chord_m": 0.100,
    "wing_tip_le_offset_m": 0.140,
    "wing_area_team_m2": 0.185,                 # rounded team reference value
    "wing_spar_chord_fraction": 0.261,           # near max-thickness region

    # V-tail - team aerodynamic geometry
    "vtail_airfoil": "NACA 0010",
    "vtail_root_le_x_m": 0.960,                 # latest CAD measurement
    "vtail_half_span_m": 0.245,
    "vtail_root_chord_m": 0.090,
    "vtail_tip_chord_m": 0.045,
    "vtail_tip_le_offset_m": 0.120,
    "vtail_dihedral_deg": 35.0,

    # Team CG / stability references from presentation
    "np_aft_of_wing_le_m": 0.148,
    "cg_target_aft_of_wing_le_m": 0.1344,
    "static_margin_target": 0.101,

    # Team mass / mission references
    "team_total_mass_ref_kg": 2.669,
    "team_max_vtol_thrust_total_N": 40.0,
    "n_vtol_motors": 4,
    "cruise_speed_mps": 20.0,
    "top_speed_mps": 44.6,
    "pusher_cruise_required_thrust_N": 6.62,
    "wind_design_mph": 30.0,                    # upper end of presentation 20-30 mph

    # -------------------------------------------------------------------------
    # Motor-arm CAD - latest measurements
    # -------------------------------------------------------------------------
    "arm_x_front_m": 0.220,
    "arm_x_rear_m": 0.570,
    "arm_length_m": 0.350,
    "arm_width_y_m": 0.030,                     # spanwise cross-section dimension
    "arm_height_z_m": 0.020,                    # vertical cross-section dimension
    "arm_wall_m": 0.0010,                       # ASSUMPTION: 1.0 mm CFRP baseline
    "arm_y_abs_m": 0.265,
    "arm_z_m": -0.010,                          # ASSUMPTION: tube directly under z=0 plane
    "arm_support_front_x_m": 0.313,
    "arm_support_rear_x_m": 0.448,

    # Four VTOL motor coordinates - CAD
    "front_motor_x_m": 0.235,
    "rear_motor_x_m": 0.555,
    "vtol_motor_z_m": 0.000,

    # -------------------------------------------------------------------------
    # Wing spar baseline - NEW V2 preliminary sizing
    # Tapered CFRP rectangular box spar, one per half-wing.
    # -------------------------------------------------------------------------
    "spar_root_width_m": 0.015,
    "spar_tip_width_m": 0.010,
    "spar_root_height_m": 0.013,
    "spar_tip_height_m": 0.008,
    "spar_wall_m": 0.0015,

    # Wing lightweight construction assumptions
    "wing_covering_areal_density_kg_m2": 0.050,
    "wing_ribs_per_side": 5,
    "wing_rib_thickness_m": 0.003,
    "wing_rib_airfoil_area_factor": 0.060,
    "foam_density_kg_m3": 50.0,

    # -------------------------------------------------------------------------
    # Fuselage baseline - NEW V2 preliminary sizing
    # -------------------------------------------------------------------------
    "fuselage_shell_material": "GFRP",
    "fuselage_shell_thickness_m": 0.00040,

    # -------------------------------------------------------------------------
    # Aft load-path baseline - NEW V2 preliminary sizing
    # Internal CFRP spine; not an external tail boom.
    # -------------------------------------------------------------------------
    "aft_spine_x_front_m": 0.800,
    "aft_spine_x_rear_m": 1.110,
    "aft_spine_width_m": 0.010,
    "aft_spine_height_m": 0.010,
    "aft_spine_wall_m": 0.0010,

    # V-tail lightweight structural assumptions
    "vtail_covering_areal_density_kg_m2": 0.050,
    "vtail_foam_fill_factor": 0.55,
    "vtail_thickness_ratio": 0.10,
    "tail_design_CL": 0.50,                      # ASSUMPTION pending aero tail-load handoff

    # -------------------------------------------------------------------------
    # Payload magnet plate baseline - NEW V2 preliminary sizing
    # -------------------------------------------------------------------------
    "payload_plate_length_x_m": 0.050,
    "payload_plate_width_y_m": 0.040,
    "payload_plate_thickness_m": 0.0015,
    "payload_plate_material": "AL6061T6",
    "payload_plate_span_m": 0.040,

    # -------------------------------------------------------------------------
    # Load-case assumptions pending formal team requirements
    # -------------------------------------------------------------------------
    "limit_load_factor": 3.0,
    "ultimate_load_factor": 4.5,
    "vtol_structural_thrust_factor": 1.50,
    "pusher_structural_thrust_factor": 1.50,

    # -------------------------------------------------------------------------
    # Team non-structural masses
    # -------------------------------------------------------------------------
    "battery_mass_kg": 0.650,
    "payload_mass_kg": 0.360,
    "servos_mass_kg": 0.180,
    "heat_sink_mass_kg": 0.030,
    "esc_wiring_mass_kg": 0.150,
    "camera_ai_mass_kg": 0.350,
    "payload_magnet_mass_kg": 0.010,

    # Manufacturer/product masses
    # UM2807 1700KV: 52.0 g including wires (manufacturer datasheet)
    # APC 10x3: 0.92 oz = 26.08 g
    # T-Motor MT4008-18: 108 g
    # APC 13x8E: 1.09 oz = 30.90 g
    "vtol_motor_mass_each_kg": 0.0520,
    "vtol_prop_mass_each_kg": 0.0260816,
    "pusher_motor_mass_kg": 0.1080,
    "pusher_prop_mass_kg": 0.0309010,

    # Mount allowances - ASSUMPTIONS until CAD mounting hardware is frozen
    "vtol_mount_mass_each_kg": 0.008,
    "pusher_mount_mass_kg": 0.010,

    # -------------------------------------------------------------------------
    # Current / provisional component locations
    # -------------------------------------------------------------------------
    "payload_x_m": 0.350,
    "payload_y_m": 0.000,
    "payload_z_m": -0.055,
    "pusher_x_m": 1.110,
    "pusher_y_m": 0.000,
    "pusher_z_m": 0.000,

    # Internal packaging assumptions: replace after team CAD integration meeting.
    "camera_ai_x_m": 0.060,                      # camera/AI at nose; exact CG TBD
    "camera_ai_y_m": 0.000,
    "camera_ai_z_m": 0.000,
    "servos_x_m": 0.800,                        # ASSUMPTION
    "servos_y_m": 0.000,
    "servos_z_m": 0.000,
    "heat_sink_x_m": 0.200,                     # ASSUMPTION
    "heat_sink_y_m": 0.000,
    "heat_sink_z_m": 0.000,
    "esc_wiring_x_m": 0.350,                    # ASSUMPTION / distributed equivalent
    "esc_wiring_y_m": 0.000,
    "esc_wiring_z_m": 0.000,

    # Battery packaging range used only to flag whether the solved position is plausible.
    "battery_x_min_m": 0.120,                    # ASSUMPTION
    "battery_x_max_m": 0.850,                    # ASSUMPTION
    "battery_y_m": 0.000,
    "battery_z_m": 0.000,

    # Fuselage side-force approximation for 30 mph wind
    "fuselage_projected_side_area_m2": 0.100,    # ASSUMPTION ~ L*d equivalent
    "fuselage_side_Cd": 1.0,                    # ASSUMPTION

    # Explicit conceptual allowance for joints, adhesives, local doublers, fasteners.
    "structural_hardware_fraction": 0.10,
    "structural_hardware_x_m": 0.450,            # ASSUMPTION equivalent mass station
}


# =============================================================================
# 3. DATA TYPES
# =============================================================================


@dataclass
class PointMass:
    name: str
    mass_kg: float
    x_m: float
    y_m: float
    z_m: float
    source: str


# =============================================================================
# 4. BASIC GEOMETRY FUNCTIONS
# =============================================================================


def lerp(a: float, b: float, f: float) -> float:
    return a + (b - a) * f


def trapz(xs: List[float], ys: List[float]) -> float:
    total = 0.0
    for i in range(len(xs) - 1):
        dx = xs[i + 1] - xs[i]
        total += 0.5 * (ys[i] + ys[i + 1]) * dx
    return total


def rectangular_tube_area(width_m: float, height_m: float, wall_m: float) -> float:
    inner_w = max(width_m - 2.0 * wall_m, 0.0)
    inner_h = max(height_m - 2.0 * wall_m, 0.0)
    return width_m * height_m - inner_w * inner_h


def rectangular_tube_I_for_vertical_bending(
    width_y_m: float, height_z_m: float, wall_m: float
) -> float:
    """Second moment about spanwise y-axis for vertical z loading along x."""
    inner_w = max(width_y_m - 2.0 * wall_m, 0.0)
    inner_h = max(height_z_m - 2.0 * wall_m, 0.0)
    return (
        width_y_m * height_z_m**3 - inner_w * inner_h**3
    ) / 12.0


def solid_rect_I(width_m: float, height_m: float) -> float:
    return width_m * height_m**3 / 12.0


def wing_semispan(p=P) -> float:
    return float(p["wingspan_m"]) / 2.0


def wing_local_chord(y_abs_m: float, p=P) -> float:
    L = wing_semispan(p)
    f = min(max(y_abs_m / L, 0.0), 1.0)
    return lerp(float(p["wing_root_chord_m"]), float(p["wing_tip_chord_m"]), f)


def wing_local_le_x(y_abs_m: float, p=P) -> float:
    L = wing_semispan(p)
    f = min(max(y_abs_m / L, 0.0), 1.0)
    return float(p["x_main_wing_le_m"]) + float(p["wing_tip_le_offset_m"]) * f


def wing_spar_width(y_abs_m: float, p=P) -> float:
    L = wing_semispan(p)
    f = min(max(y_abs_m / L, 0.0), 1.0)
    return lerp(float(p["spar_root_width_m"]), float(p["spar_tip_width_m"]), f)


def wing_spar_height(y_abs_m: float, p=P) -> float:
    L = wing_semispan(p)
    f = min(max(y_abs_m / L, 0.0), 1.0)
    return lerp(float(p["spar_root_height_m"]), float(p["spar_tip_height_m"]), f)


def wing_spar_x(y_abs_m: float, p=P) -> float:
    return wing_local_le_x(y_abs_m, p) + float(p["wing_spar_chord_fraction"]) * wing_local_chord(y_abs_m, p)


def derive_wing_geometry(p=P) -> Dict[str, float]:
    b = float(p["wingspan_m"])
    cr = float(p["wing_root_chord_m"])
    ct = float(p["wing_tip_chord_m"])
    tip_offset = float(p["wing_tip_le_offset_m"])
    S_geom = b * (cr + ct) / 2.0
    taper = ct / cr
    AR_geom = b**2 / S_geom
    MAC = (2.0 / 3.0) * cr * (1.0 + taper + taper**2) / (1.0 + taper)
    quarter_chord_offset = tip_offset + 0.25 * ct - 0.25 * cr
    sweep_qc_deg = degrees(atan(quarter_chord_offset / (b / 2.0)))
    return {
        "wing_area_geom_m2": S_geom,
        "taper_ratio": taper,
        "aspect_ratio_geom": AR_geom,
        "mac_m": MAC,
        "quarter_chord_sweep_deg": sweep_qc_deg,
    }


def derive_vtail_geometry(p=P) -> Dict[str, float]:
    s = float(p["vtail_half_span_m"])
    cr = float(p["vtail_root_chord_m"])
    ct = float(p["vtail_tip_chord_m"])
    off = float(p["vtail_tip_le_offset_m"])

    area_one = s * (cr + ct) / 2.0
    area_total = 2.0 * area_one

    # Area centroid x measured aft of root LE, numerically integrating strips.
    n = 1200
    ys = [s * i / n for i in range(n + 1)]
    strip_weights = []
    x_weighted = []
    for y in ys:
        f = y / s if s else 0.0
        c = lerp(cr, ct, f)
        x_le_local = off * f
        x_strip_centroid = x_le_local + 0.5 * c
        strip_weights.append(c)
        x_weighted.append(c * x_strip_centroid)
    x_centroid_from_root_le = trapz(ys, x_weighted) / trapz(ys, strip_weights)

    return {
        "vtail_area_one_m2": area_one,
        "vtail_area_total_m2": area_total,
        "vtail_centroid_from_root_le_m": x_centroid_from_root_le,
        "vtail_centroid_x_m": float(p["vtail_root_le_x_m"]) + x_centroid_from_root_le,
    }


# =============================================================================
# 5. STRUCTURAL MASS MODEL
# =============================================================================


def compute_structural_masses(p=P) -> Tuple[Dict[str, float], List[PointMass]]:
    cfrp = MATERIALS["CFRP"]
    gfrp = MATERIALS["GFRP"]
    al = MATERIALS["AL6061T6"]
    wing_geo = derive_wing_geometry(p)
    tail_geo = derive_vtail_geometry(p)

    masses: Dict[str, float] = {}
    components: List[PointMass] = []

    # --- Fuselage shell -------------------------------------------------------
    shell_mat = MATERIALS[str(p["fuselage_shell_material"])]
    m_fuselage = (
        float(p["fuselage_surface_area_m2"])
        * float(p["fuselage_shell_thickness_m"])
        * shell_mat.density_kg_m3
    )
    masses["fuselage_shell_kg"] = m_fuselage
    components.append(
        PointMass(
            "Fuselage shell",
            m_fuselage,
            0.5 * float(p["fuselage_length_m"]),
            0.0,
            0.0,
            "CAD area + V2 GFRP thickness assumption",
        )
    )

    # --- Wing spars: integrate tapered rectangular tube -----------------------
    L = wing_semispan(p)
    n = 1600
    ys = [L * i / n for i in range(n + 1)]
    area_cs = []
    dm_dx = []
    x_dm = []
    for y in ys:
        w = wing_spar_width(y, p)
        h = wing_spar_height(y, p)
        area = rectangular_tube_area(w, h, float(p["spar_wall_m"]))
        area_cs.append(area)
        linear_mass = area * cfrp.density_kg_m3
        dm_dx.append(linear_mass)
        x_dm.append(linear_mass * wing_spar_x(y, p))
    m_spar_one = trapz(ys, dm_dx)
    x_spar_cg = trapz(ys, x_dm) / m_spar_one
    m_spars = 2.0 * m_spar_one
    masses["wing_spars_kg"] = m_spars
    components.append(PointMass("Wing spars", m_spars, x_spar_cg, 0.0, 0.0, "V2 tapered CFRP box-spar assumption"))

    # --- Wing covering --------------------------------------------------------
    S = wing_geo["wing_area_geom_m2"]
    m_cover = 2.0 * S * float(p["wing_covering_areal_density_kg_m2"])
    masses["wing_covering_kg"] = m_cover

    # Area-weighted covering x-CG; approximate local section centroid at 40% chord.
    chord_weights = []
    x_chord_weight = []
    for y in ys:
        c = wing_local_chord(y, p)
        x_c = wing_local_le_x(y, p) + 0.40 * c
        chord_weights.append(c)
        x_chord_weight.append(c * x_c)
    x_cover = trapz(ys, x_chord_weight) / trapz(ys, chord_weights)
    components.append(PointMass("Wing covering", m_cover, x_cover, 0.0, 0.0, "V2 lightweight-covering assumption"))

    # --- Wing ribs ------------------------------------------------------------
    rib_masses_one_side = []
    rib_x_moments_one_side = []
    n_ribs = int(p["wing_ribs_per_side"])
    for i in range(n_ribs):
        y = 0.0 if n_ribs == 1 else L * i / (n_ribs - 1)
        c = wing_local_chord(y, p)
        rib_planform_area = float(p["wing_rib_airfoil_area_factor"]) * c**2
        m_rib = (
            rib_planform_area
            * float(p["wing_rib_thickness_m"])
            * float(p["foam_density_kg_m3"])
        )
        x_rib = wing_local_le_x(y, p) + 0.40 * c
        rib_masses_one_side.append(m_rib)
        rib_x_moments_one_side.append(m_rib * x_rib)
    m_ribs = 2.0 * sum(rib_masses_one_side)
    x_ribs = sum(rib_x_moments_one_side) / sum(rib_masses_one_side)
    masses["wing_ribs_kg"] = m_ribs
    components.append(PointMass("Wing foam ribs", m_ribs, x_ribs, 0.0, 0.0, "V2 rib geometry assumption"))

    # --- Two motor arms -------------------------------------------------------
    arm_A = rectangular_tube_area(
        float(p["arm_width_y_m"]),
        float(p["arm_height_z_m"]),
        float(p["arm_wall_m"]),
    )
    m_arm_each = arm_A * float(p["arm_length_m"]) * cfrp.density_kg_m3
    masses["motor_arm_each_kg"] = m_arm_each
    masses["motor_arms_total_kg"] = 2.0 * m_arm_each
    x_arm = 0.5 * (float(p["arm_x_front_m"]) + float(p["arm_x_rear_m"]))
    components.append(PointMass("Motor arm R", m_arm_each, x_arm, -float(p["arm_y_abs_m"]), float(p["arm_z_m"]), "CAD + 1 mm CFRP wall assumption"))
    components.append(PointMass("Motor arm L", m_arm_each, x_arm, +float(p["arm_y_abs_m"]), float(p["arm_z_m"]), "CAD + 1 mm CFRP wall assumption"))

    # --- Internal aft CFRP spine ---------------------------------------------
    spine_A = rectangular_tube_area(
        float(p["aft_spine_width_m"]),
        float(p["aft_spine_height_m"]),
        float(p["aft_spine_wall_m"]),
    )
    spine_L = float(p["aft_spine_x_rear_m"]) - float(p["aft_spine_x_front_m"])
    m_spine = spine_A * spine_L * cfrp.density_kg_m3
    masses["aft_spine_kg"] = m_spine
    components.append(
        PointMass(
            "Aft CFRP spine",
            m_spine,
            0.5 * (float(p["aft_spine_x_front_m"]) + float(p["aft_spine_x_rear_m"])),
            0.0,
            0.0,
            "V2 structural load-path assumption",
        )
    )

    # --- V-tail foam + covering ----------------------------------------------
    S_tail = tail_geo["vtail_area_total_m2"]
    m_tail_cover = 2.0 * S_tail * float(p["vtail_covering_areal_density_kg_m2"])
    avg_tail_chord = 0.5 * (float(p["vtail_root_chord_m"]) + float(p["vtail_tip_chord_m"]))
    effective_foam_thickness = (
        float(p["vtail_thickness_ratio"])
        * avg_tail_chord
        * float(p["vtail_foam_fill_factor"])
    )
    m_tail_foam = S_tail * effective_foam_thickness * float(p["foam_density_kg_m3"])
    masses["vtail_covering_kg"] = m_tail_cover
    masses["vtail_foam_kg"] = m_tail_foam
    components.append(
        PointMass(
            "V-tail structure",
            m_tail_cover + m_tail_foam,
            tail_geo["vtail_centroid_x_m"],
            0.0,
            0.040,  # ASSUMPTION; longitudinal CG is much more important at this stage
            "Team V-tail geometry + V2 lightweight structural assumption",
        )
    )

    # --- Payload magnet mounting plate ---------------------------------------
    plate_mat = MATERIALS[str(p["payload_plate_material"])]
    plate_volume = (
        float(p["payload_plate_length_x_m"])
        * float(p["payload_plate_width_y_m"])
        * float(p["payload_plate_thickness_m"])
    )
    m_plate = plate_volume * plate_mat.density_kg_m3
    masses["payload_mount_plate_kg"] = m_plate
    components.append(
        PointMass(
            "Payload mount plate",
            m_plate,
            float(p["payload_x_m"]),
            0.0,
            float(p["payload_z_m"]),
            "V2 6061-T6 plate assumption",
        )
    )

    # --- Joints / adhesive / local hardpoints allowance -----------------------
    structural_subtotal = sum(masses.values()) - masses["motor_arm_each_kg"]
    # The dictionary contains both each-arm and total-arm keys. Remove duplicate 'each'.
    allowance = structural_subtotal * float(p["structural_hardware_fraction"])
    masses["structural_hardware_allowance_kg"] = allowance
    components.append(
        PointMass(
            "Structural hardware allowance",
            allowance,
            float(p["structural_hardware_x_m"]),
            0.0,
            0.0,
            "10% conceptual allowance: joints/adhesive/doublers/fasteners",
        )
    )

    masses["structural_subtotal_before_allowance_kg"] = structural_subtotal
    masses["structural_total_kg"] = structural_subtotal + allowance
    return masses, components


# =============================================================================
# 6. AIRCRAFT MASS PROPERTIES / BATTERY PLACEMENT
# =============================================================================


def propulsion_point_masses(p=P) -> List[PointMass]:
    unit_lift_mass = (
        float(p["vtol_motor_mass_each_kg"])
        + float(p["vtol_prop_mass_each_kg"])
        + float(p["vtol_mount_mass_each_kg"])
    )
    y = float(p["arm_y_abs_m"])
    z = float(p["vtol_motor_z_m"])
    xf = float(p["front_motor_x_m"])
    xr = float(p["rear_motor_x_m"])

    pusher_mass = (
        float(p["pusher_motor_mass_kg"])
        + float(p["pusher_prop_mass_kg"])
        + float(p["pusher_mount_mass_kg"])
    )

    return [
        PointMass("VTOL motor+prop FR", unit_lift_mass, xf, -y, z, "CAD coords + manufacturer mass + mount allowance"),
        PointMass("VTOL motor+prop FL", unit_lift_mass, xf, +y, z, "CAD coords + manufacturer mass + mount allowance"),
        PointMass("VTOL motor+prop RR", unit_lift_mass, xr, -y, z, "CAD coords + manufacturer mass + mount allowance"),
        PointMass("VTOL motor+prop RL", unit_lift_mass, xr, +y, z, "CAD coords + manufacturer mass + mount allowance"),
        PointMass("Rear pusher assembly", pusher_mass, float(p["pusher_x_m"]), float(p["pusher_y_m"]), float(p["pusher_z_m"]), "Team motor/prop selection + manufacturer mass + mount allowance"),
    ]


def nonstructural_nonbattery_point_masses(p=P) -> List[PointMass]:
    return [
        PointMass("Payload", float(p["payload_mass_kg"]), float(p["payload_x_m"]), float(p["payload_y_m"]), float(p["payload_z_m"]), "Team mass + CAD payload center"),
        PointMass("Camera / AI", float(p["camera_ai_mass_kg"]), float(p["camera_ai_x_m"]), float(p["camera_ai_y_m"]), float(p["camera_ai_z_m"]), "Team mass; nose location provisional"),
        PointMass("Servos", float(p["servos_mass_kg"]), float(p["servos_x_m"]), float(p["servos_y_m"]), float(p["servos_z_m"]), "Team mass; location ASSUMPTION"),
        PointMass("Heat sink", float(p["heat_sink_mass_kg"]), float(p["heat_sink_x_m"]), float(p["heat_sink_y_m"]), float(p["heat_sink_z_m"]), "Team mass; location ASSUMPTION"),
        PointMass("ESCs / wiring", float(p["esc_wiring_mass_kg"]), float(p["esc_wiring_x_m"]), float(p["esc_wiring_y_m"]), float(p["esc_wiring_z_m"]), "Team mass; distributed-equivalent location ASSUMPTION"),
        PointMass("Payload magnet", float(p["payload_magnet_mass_kg"]), float(p["payload_x_m"]), 0.0, float(p["payload_z_m"]), "Presentation magnet mass"),
    ]


def solve_battery_x_for_target_cg(other_components: List[PointMass], p=P) -> float:
    target_x = float(p["x_main_wing_le_m"]) + float(p["cg_target_aft_of_wing_le_m"])
    m_b = float(p["battery_mass_kg"])
    m_other = sum(c.mass_kg for c in other_components)
    mx_other = sum(c.mass_kg * c.x_m for c in other_components)
    total_mass = m_other + m_b
    return (target_x * total_mass - mx_other) / m_b


def cg_of_components(components: List[PointMass]) -> Tuple[float, float, float, float]:
    m = sum(c.mass_kg for c in components)
    if m <= 0.0:
        raise ValueError("Total mass must be positive.")
    x = sum(c.mass_kg * c.x_m for c in components) / m
    y = sum(c.mass_kg * c.y_m for c in components) / m
    z = sum(c.mass_kg * c.z_m for c in components) / m
    return m, x, y, z


def mass_moments_of_inertia_point_mass(components: List[PointMass], cg: Tuple[float, float, float]) -> Dict[str, float]:
    xc, yc, zc = cg
    Ixx = Iyy = Izz = 0.0
    for c in components:
        dx = c.x_m - xc
        dy = c.y_m - yc
        dz = c.z_m - zc
        Ixx += c.mass_kg * (dy**2 + dz**2)
        Iyy += c.mass_kg * (dx**2 + dz**2)
        Izz += c.mass_kg * (dx**2 + dy**2)
    return {"Ixx_kgm2": Ixx, "Iyy_kgm2": Iyy, "Izz_kgm2": Izz}


# =============================================================================
# 7. STRUCTURAL LOAD CASES
# =============================================================================


def wing_spar_analysis(total_mass_kg: float, p=P, n_points: int = 1200) -> Dict[str, float]:
    """First-order cantilever half-wing analysis using elliptical distributed lift."""
    mat = MATERIALS["CFRP"]
    L = wing_semispan(p)
    ys = [L * i / n_points for i in range(n_points + 1)]

    # Elliptical distribution shape, normalized to carry one-half of aircraft lift.
    shape = [sqrt(max(0.0, 1.0 - (y / L) ** 2)) for y in ys]
    shape_int = trapz(ys, shape)

    def analyze_at_n(n_factor: float) -> Dict[str, float]:
        half_lift = total_mass_kg * G * n_factor / 2.0
        q = [half_lift * s / shape_int for s in shape]

        # Internal moment M(y) = integral_y^L q(s)*(s-y) ds.
        M = []
        for i, y in enumerate(ys):
            if i == len(ys) - 1:
                M.append(0.0)
                continue
            xs_seg = ys[i:]
            vals = [q[j] * (ys[j] - y) for j in range(i, len(ys))]
            M.append(trapz(xs_seg, vals))

        Is = []
        curv = []
        for y, m in zip(ys, M):
            w = wing_spar_width(y, p)
            h = wing_spar_height(y, p)
            I = rectangular_tube_I_for_vertical_bending(w, h, float(p["spar_wall_m"]))
            Is.append(I)
            curv.append(m / (mat.E_Pa * I))

        # Integrate curvature -> slope -> deflection with root fixed.
        slopes = [0.0]
        deflections = [0.0]
        for i in range(len(ys) - 1):
            dy = ys[i + 1] - ys[i]
            next_slope = slopes[-1] + 0.5 * (curv[i] + curv[i + 1]) * dy
            slopes.append(next_slope)
            next_defl = deflections[-1] + 0.5 * (slopes[-2] + slopes[-1]) * dy
            deflections.append(next_defl)

        I_root = Is[0]
        h_root = wing_spar_height(0.0, p)
        root_stress = M[0] * (h_root / 2.0) / I_root
        return {
            "root_moment_Nm": M[0],
            "root_stress_Pa": root_stress,
            "tip_deflection_m": deflections[-1],
            "root_I_m4": I_root,
            "root_FOS": mat.allowable_bending_Pa / root_stress if root_stress > 0 else float("inf"),
        }

    limit = analyze_at_n(float(p["limit_load_factor"]))
    ultimate = analyze_at_n(float(p["ultimate_load_factor"]))
    return {
        "limit_root_moment_Nm": limit["root_moment_Nm"],
        "limit_root_stress_MPa": limit["root_stress_Pa"] / 1e6,
        "limit_tip_deflection_mm": limit["tip_deflection_m"] * 1000.0,
        "limit_FOS": limit["root_FOS"],
        "ultimate_root_moment_Nm": ultimate["root_moment_Nm"],
        "ultimate_root_stress_MPa": ultimate["root_stress_Pa"] / 1e6,
        "ultimate_tip_deflection_mm": ultimate["tip_deflection_m"] * 1000.0,
        "ultimate_FOS": ultimate["root_FOS"],
        "root_I_m4": limit["root_I_m4"],
    }


def motor_arm_analysis(p=P) -> Dict[str, float]:
    mat = MATERIALS["CFRP"]
    width = float(p["arm_width_y_m"])
    height = float(p["arm_height_z_m"])
    wall = float(p["arm_wall_m"])
    I = rectangular_tube_I_for_vertical_bending(width, height, wall)

    T_max_per_motor = float(p["team_max_vtol_thrust_total_N"]) / int(p["n_vtol_motors"])
    F_design = T_max_per_motor * float(p["vtol_structural_thrust_factor"])

    L_front = float(p["arm_support_front_x_m"]) - float(p["front_motor_x_m"])
    L_rear = float(p["rear_motor_x_m"]) - float(p["arm_support_rear_x_m"])

    def cantilever_case(L: float) -> Tuple[float, float, float]:
        M = F_design * L
        sigma = M * (height / 2.0) / I
        delta = F_design * L**3 / (3.0 * mat.E_Pa * I)
        return M, sigma, delta

    Mf, sf, df = cantilever_case(L_front)
    Mr, sr, dr = cantilever_case(L_rear)
    worst_sigma = max(sf, sr)

    return {
        "max_thrust_per_motor_N": T_max_per_motor,
        "design_thrust_per_motor_N": F_design,
        "front_overhang_m": L_front,
        "rear_overhang_m": L_rear,
        "arm_I_m4": I,
        "front_support_moment_Nm": Mf,
        "rear_support_moment_Nm": Mr,
        "front_stress_MPa": sf / 1e6,
        "rear_stress_MPa": sr / 1e6,
        "front_deflection_mm": df * 1000.0,
        "rear_deflection_mm": dr * 1000.0,
        "worst_FOS": mat.allowable_bending_Pa / worst_sigma if worst_sigma > 0 else float("inf"),
    }


def payload_plate_analysis(p=P) -> Dict[str, float]:
    mat = MATERIALS[str(p["payload_plate_material"])]
    F = float(p["payload_mass_kg"]) * G * float(p["ultimate_load_factor"])
    span = float(p["payload_plate_span_m"])
    b = float(p["payload_plate_length_x_m"])
    t = float(p["payload_plate_thickness_m"])
    I = solid_rect_I(b, t)

    # Conservative simply supported strip with central point load.
    Mmax = F * span / 4.0
    sigma = Mmax * (t / 2.0) / I
    delta = F * span**3 / (48.0 * mat.E_Pa * I)
    avg_shear = F / (b * t)

    return {
        "ultimate_payload_inertial_load_N": F,
        "plate_max_moment_Nm": Mmax,
        "plate_bending_stress_MPa": sigma / 1e6,
        "plate_avg_shear_MPa": avg_shear / 1e6,
        "plate_deflection_mm": delta * 1000.0,
        "plate_FOS": mat.allowable_bending_Pa / sigma if sigma > 0 else float("inf"),
    }


def aft_spine_analysis(p=P) -> Dict[str, float]:
    mat = MATERIALS["CFRP"]
    width = float(p["aft_spine_width_m"])
    height = float(p["aft_spine_height_m"])
    wall = float(p["aft_spine_wall_m"])
    A = rectangular_tube_area(width, height, wall)
    I = rectangular_tube_I_for_vertical_bending(width, height, wall)

    # Pusher axial structural design load.
    F_push = float(p["pusher_cruise_required_thrust_N"]) * float(p["pusher_structural_thrust_factor"])
    axial_stress = F_push / A

    # Provisional tail aerodynamic structural load at top speed.
    tail_geo = derive_vtail_geometry(p)
    q = 0.5 * RHO_AIR * float(p["top_speed_mps"]) ** 2
    F_tail = q * tail_geo["vtail_area_total_m2"] * float(p["tail_design_CL"])
    F_tail_ultimate = 1.5 * F_tail

    # Treat distance from front of spine to V-tail centroid as cantilever lever arm.
    lever = max(tail_geo["vtail_centroid_x_m"] - float(p["aft_spine_x_front_m"]), 0.0)
    M_tail = F_tail_ultimate * lever
    sigma_tail = M_tail * (height / 2.0) / I

    return {
        "pusher_design_axial_load_N": F_push,
        "spine_axial_stress_MPa": axial_stress / 1e6,
        "tail_dynamic_pressure_Pa": q,
        "tail_design_load_N": F_tail,
        "tail_ultimate_load_N": F_tail_ultimate,
        "tail_spine_lever_m": lever,
        "tail_spine_moment_Nm": M_tail,
        "tail_spine_bending_stress_MPa": sigma_tail / 1e6,
        "tail_spine_FOS": mat.allowable_bending_Pa / sigma_tail if sigma_tail > 0 else float("inf"),
    }


def wind_side_load_estimate(p=P) -> Dict[str, float]:
    V = float(p["wind_design_mph"]) * 0.44704
    q = 0.5 * RHO_AIR * V**2
    F = q * float(p["fuselage_projected_side_area_m2"]) * float(p["fuselage_side_Cd"])
    return {"wind_speed_mps": V, "dynamic_pressure_Pa": q, "fuselage_side_force_N": F}


# =============================================================================
# 8. INTEGRATED ANALYSIS
# =============================================================================


def run_analysis(p=P) -> Dict[str, object]:
    wing = derive_wing_geometry(p)
    tail = derive_vtail_geometry(p)
    structural_masses, structural_components = compute_structural_masses(p)

    components_no_battery = (
        structural_components
        + propulsion_point_masses(p)
        + nonstructural_nonbattery_point_masses(p)
    )

    battery_x = solve_battery_x_for_target_cg(components_no_battery, p)
    battery = PointMass(
        "Battery",
        float(p["battery_mass_kg"]),
        battery_x,
        float(p["battery_y_m"]),
        float(p["battery_z_m"]),
        "Solved to hit team target longitudinal CG; final CAD location TBD",
    )
    components = components_no_battery + [battery]

    total_mass, xcg, ycg, zcg = cg_of_components(components)
    inertias = mass_moments_of_inertia_point_mass(components, (xcg, ycg, zcg))

    x_np = float(p["x_main_wing_le_m"]) + float(p["np_aft_of_wing_le_m"])
    mac = wing["mac_m"]
    static_margin = (x_np - xcg) / mac

    wing_struct = wing_spar_analysis(total_mass, p)
    arm_struct = motor_arm_analysis(p)
    plate_struct = payload_plate_analysis(p)
    spine_struct = aft_spine_analysis(p)
    wind = wind_side_load_estimate(p)

    battery_in_range = float(p["battery_x_min_m"]) <= battery_x <= float(p["battery_x_max_m"])

    return {
        "wing": wing,
        "tail": tail,
        "structural_masses": structural_masses,
        "components": components,
        "total_mass_kg": total_mass,
        "cg_m": (xcg, ycg, zcg),
        "inertias": inertias,
        "battery_x_m": battery_x,
        "battery_in_assumed_range": battery_in_range,
        "x_np_m": x_np,
        "static_margin": static_margin,
        "wing_struct": wing_struct,
        "arm_struct": arm_struct,
        "plate_struct": plate_struct,
        "spine_struct": spine_struct,
        "wind": wind,
    }


# =============================================================================
# 9. REPORTING / EXPORT
# =============================================================================


def status(ok: bool) -> str:
    return "PASS" if ok else "CHECK"


def write_component_csv(results: Dict[str, object], path: Path) -> None:
    components: List[PointMass] = results["components"]  # type: ignore[assignment]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Component", "Mass_kg", "x_m", "y_m", "z_m", "Source_or_Status"])
        for c in components:
            w.writerow([c.name, f"{c.mass_kg:.6f}", f"{c.x_m:.6f}", f"{c.y_m:.6f}", f"{c.z_m:.6f}", c.source])


def write_battery_sweep_csv(results: Dict[str, object], p, path: Path, step_m: float = 0.01) -> None:
    components: List[PointMass] = [c for c in results["components"] if c.name != "Battery"]  # type: ignore[index]
    x_min = float(p["battery_x_min_m"])
    x_max = float(p["battery_x_max_m"])
    wing = derive_wing_geometry(p)
    x_np = float(p["x_main_wing_le_m"]) + float(p["np_aft_of_wing_le_m"])
    m_b = float(p["battery_mass_kg"])

    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["battery_x_m", "total_cg_x_m", "static_margin_fraction", "static_margin_percent"])
        x = x_min
        while x <= x_max + 1e-9:
            trial = components + [PointMass("Battery", m_b, x, float(p["battery_y_m"]), float(p["battery_z_m"]), "battery sweep")]
            _, xcg, _, _ = cg_of_components(trial)
            sm = (x_np - xcg) / wing["mac_m"]
            w.writerow([f"{x:.4f}", f"{xcg:.6f}", f"{sm:.6f}", f"{100.0*sm:.3f}"])
            x += step_m


def build_report(results: Dict[str, object], p=P) -> str:
    wing: Dict[str, float] = results["wing"]  # type: ignore[assignment]
    tail: Dict[str, float] = results["tail"]  # type: ignore[assignment]
    smass: Dict[str, float] = results["structural_masses"]  # type: ignore[assignment]
    wing_s: Dict[str, float] = results["wing_struct"]  # type: ignore[assignment]
    arm_s: Dict[str, float] = results["arm_struct"]  # type: ignore[assignment]
    plate_s: Dict[str, float] = results["plate_struct"]  # type: ignore[assignment]
    spine_s: Dict[str, float] = results["spine_struct"]  # type: ignore[assignment]
    wind: Dict[str, float] = results["wind"]  # type: ignore[assignment]
    xcg, ycg, zcg = results["cg_m"]  # type: ignore[misc]

    lines: List[str] = []
    lines.append("RESCU STRUCTURES ANALYSIS V2")
    lines.append("=" * 78)
    lines.append("")
    lines.append("MODEL STATUS")
    lines.append("------------")
    lines.append("Preliminary structural sizing model. Values labelled ASSUMPTION must be")
    lines.append("replaced/validated as CAD packaging, joint details, and subsystem data freeze.")
    lines.append("")

    lines.append("1) GEOMETRY")
    lines.append("-----------")
    lines.append(f"Wing geometric area             : {wing['wing_area_geom_m2']:.6f} m^2")
    lines.append(f"Team rounded wing area          : {float(p['wing_area_team_m2']):.6f} m^2")
    lines.append(f"Taper ratio                     : {wing['taper_ratio']:.4f}")
    lines.append(f"Aspect ratio (geometric area)   : {wing['aspect_ratio_geom']:.4f}")
    lines.append(f"MAC                             : {wing['mac_m']:.6f} m")
    lines.append(f"Quarter-chord sweep             : {wing['quarter_chord_sweep_deg']:.3f} deg")
    lines.append(f"V-tail total planform area      : {tail['vtail_area_total_m2']:.6f} m^2")
    lines.append(f"V-tail structure x-centroid     : {tail['vtail_centroid_x_m']:.6f} m")
    lines.append("")

    lines.append("2) STRUCTURAL MASS")
    lines.append("------------------")
    for key in [
        "fuselage_shell_kg",
        "wing_spars_kg",
        "wing_covering_kg",
        "wing_ribs_kg",
        "motor_arms_total_kg",
        "aft_spine_kg",
        "vtail_covering_kg",
        "vtail_foam_kg",
        "payload_mount_plate_kg",
        "structural_hardware_allowance_kg",
    ]:
        lines.append(f"{key:<35}: {smass[key]:.4f} kg")
    lines.append(f"{'STRUCTURAL TOTAL':<35}: {smass['structural_total_kg']:.4f} kg")
    lines.append(f"{'AIRCRAFT MODEL TOTAL':<35}: {float(results['total_mass_kg']):.4f} kg")
    lines.append(f"{'TEAM TOTAL MASS REFERENCE':<35}: {float(p['team_total_mass_ref_kg']):.4f} kg")
    lines.append(f"{'MODEL - TEAM MASS DIFFERENCE':<35}: {float(results['total_mass_kg'])-float(p['team_total_mass_ref_kg']):+.4f} kg")
    lines.append("")

    lines.append("3) CG / BATTERY PLACEMENT")
    lines.append("--------------------------")
    target_cg = float(p["x_main_wing_le_m"]) + float(p["cg_target_aft_of_wing_le_m"])
    lines.append(f"Team target CG from nose        : {target_cg:.4f} m")
    lines.append(f"Solved battery x                : {float(results['battery_x_m']):.4f} m")
    lines.append(f"Battery assumed allowable range : {float(p['battery_x_min_m']):.3f} to {float(p['battery_x_max_m']):.3f} m")
    lines.append(f"Battery range check             : {status(bool(results['battery_in_assumed_range']))}")
    lines.append(f"Integrated CG (x,y,z)           : ({xcg:.4f}, {ycg:.4f}, {zcg:.4f}) m")
    lines.append(f"Neutral point from nose         : {float(results['x_np_m']):.4f} m")
    lines.append(f"Static margin cross-check       : {100.0*float(results['static_margin']):.2f}% MAC")
    lines.append("NOTE: Final static-margin acceptance belongs to Stability & Control. Here it is")
    lines.append("      used as an integration target/cross-check for mass placement.")
    lines.append("")

    lines.append("4) WING SPAR LOAD CASE")
    lines.append("-----------------------")
    lines.append(f"Limit load factor               : {float(p['limit_load_factor']):.2f} g")
    lines.append(f"Limit root bending moment       : {wing_s['limit_root_moment_Nm']:.3f} N*m")
    lines.append(f"Limit root bending stress       : {wing_s['limit_root_stress_MPa']:.2f} MPa")
    lines.append(f"Limit tip deflection            : {wing_s['limit_tip_deflection_mm']:.2f} mm")
    lines.append(f"Limit-load material FOS         : {wing_s['limit_FOS']:.2f}")
    lines.append(f"Ultimate load factor            : {float(p['ultimate_load_factor']):.2f} g")
    lines.append(f"Ultimate root bending stress    : {wing_s['ultimate_root_stress_MPa']:.2f} MPa")
    lines.append(f"Ultimate tip deflection         : {wing_s['ultimate_tip_deflection_mm']:.2f} mm")
    lines.append(f"Ultimate-load material FOS      : {wing_s['ultimate_FOS']:.2f}")
    lines.append("")

    lines.append("5) VTOL MOTOR ARM LOAD CASE")
    lines.append("----------------------------")
    lines.append(f"Team max VTOL thrust / rotor    : {arm_s['max_thrust_per_motor_N']:.3f} N")
    lines.append(f"Structural design thrust/rotor  : {arm_s['design_thrust_per_motor_N']:.3f} N")
    lines.append(f"Front motor overhang            : {arm_s['front_overhang_m']:.3f} m")
    lines.append(f"Rear motor overhang             : {arm_s['rear_overhang_m']:.3f} m")
    lines.append(f"Front support stress            : {arm_s['front_stress_MPa']:.3f} MPa")
    lines.append(f"Rear support stress             : {arm_s['rear_stress_MPa']:.3f} MPa")
    lines.append(f"Front motor-arm deflection      : {arm_s['front_deflection_mm']:.4f} mm")
    lines.append(f"Rear motor-arm deflection       : {arm_s['rear_deflection_mm']:.4f} mm")
    lines.append(f"Worst arm material FOS          : {arm_s['worst_FOS']:.1f}")
    lines.append("NOTE: Local bracket crushing, holes, fasteners, bondline and delamination are NOT")
    lines.append("      captured by this global beam check and may govern the real joint design.")
    lines.append("")

    lines.append("6) PAYLOAD MAGNET PLATE")
    lines.append("------------------------")
    lines.append(f"Ultimate payload inertial load  : {plate_s['ultimate_payload_inertial_load_N']:.3f} N")
    lines.append(f"Plate bending stress            : {plate_s['plate_bending_stress_MPa']:.3f} MPa")
    lines.append(f"Plate deflection                : {plate_s['plate_deflection_mm']:.4f} mm")
    lines.append(f"Plate bending FOS               : {plate_s['plate_FOS']:.1f}")
    lines.append("NOTE: Magnet pull force, fasteners/bonding and local fuselage reinforcement remain TBD.")
    lines.append("")

    lines.append("7) AFT SPINE / TAIL / PUSHER")
    lines.append("-----------------------------")
    lines.append(f"Pusher structural axial load    : {spine_s['pusher_design_axial_load_N']:.3f} N")
    lines.append(f"Spine axial stress              : {spine_s['spine_axial_stress_MPa']:.4f} MPa")
    lines.append(f"Provisional tail load           : {spine_s['tail_design_load_N']:.3f} N")
    lines.append(f"Tail ultimate load              : {spine_s['tail_ultimate_load_N']:.3f} N")
    lines.append(f"Tail-induced spine stress       : {spine_s['tail_spine_bending_stress_MPa']:.2f} MPa")
    lines.append(f"Tail-spine material FOS         : {spine_s['tail_spine_FOS']:.2f}")
    lines.append("NOTE: Tail CL design value is an explicit V2 assumption pending aerodynamic tail loads.")
    lines.append("")

    lines.append("8) MARITIME WIND REFERENCE")
    lines.append("----------------------------")
    lines.append(f"Wind speed                      : {float(p['wind_design_mph']):.1f} mph ({wind['wind_speed_mps']:.2f} m/s)")
    lines.append(f"Approx fuselage side force      : {wind['fuselage_side_force_N']:.2f} N")
    lines.append("NOTE: This is a simple side-force estimate, not a gust-load certification analysis.")
    lines.append("")

    lines.append("9) OPEN ITEMS / TEAM CONFIRMATIONS")
    lines.append("----------------------------------")
    lines.append("- Freeze actual locations of servos, ESCs/wiring, heat sink and camera/AI CG.")
    lines.append("- Confirm final battery packaging envelope in CAD; the model currently solves x.")
    lines.append("- Confirm motor mounts/bracket geometry, fasteners and material for local joint analysis.")
    lines.append("- Confirm pusher maximum thrust (V2 currently applies 1.5 x cruise-required thrust).")
    lines.append("- Provide aerodynamic V-tail design loads / hinge moments for final aft-structure sizing.")
    lines.append("- Freeze fuselage laminate schedule and local hardpoint/doubler construction.")
    lines.append("- Set an explicit allowable wing-tip deflection / stiffness requirement.")
    lines.append("- Replace preliminary CFRP/GFRP properties with selected vendor laminate properties.")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    results = run_analysis(P)
    report = build_report(results, P)
    print(report)

    out_dir = Path(__file__).resolve().parent
    report_path = out_dir / "RescU_Structures_V2_Report.txt"
    component_path = out_dir / "RescU_Structures_V2_Component_Masses.csv"
    battery_sweep_path = out_dir / "RescU_Structures_V2_Battery_Sweep.csv"

    report_path.write_text(report, encoding="utf-8")
    write_component_csv(results, component_path)
    write_battery_sweep_csv(results, P, battery_sweep_path)

    print("\nGenerated:")
    print(f"  {report_path.name}")
    print(f"  {component_path.name}")
    print(f"  {battery_sweep_path.name}")


if __name__ == "__main__":
    main()
