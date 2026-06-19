"""
shaft_designer.py
Core analytical engine for shaft design based on ASME B106.1M standards.
"""

import math
import numpy as np

# Material database containing yield strength (S_yt), ultimate tensile strength (S_ut), 
# modulus of elasticity (E in GPa), and density (kg/m3).
MATERIAL_DATABASE = {
    "Mild Steel (Structural)": {"S_yt": 250.0, "S_ut": 410.0, "E": 200.0, "density": 7850.0},
    "EN8 (Medium Carbon Steel)": {"S_yt": 280.0, "S_ut": 550.0, "E": 200.0, "density": 7850.0},
    "EN19 (Alloy Steel)": {"S_yt": 520.0, "S_ut": 700.0, "E": 200.0, "density": 7850.0},
    "EN24 (High Tensile Alloy)": {"S_yt": 650.0, "S_ut": 850.0, "E": 200.0, "density": 7850.0},
    "Stainless Steel 304": {"S_yt": 205.0, "S_ut": 515.0, "E": 193.0, "density": 8000.0}
}

# Standard recommended shaft diameters (mm) based on standard engineering practices
STANDARD_DIAMETERS = [
    10, 12, 15, 18, 20, 22, 25, 28, 30, 35, 40, 45, 50, 55, 60, 65, 
    70, 75, 80, 90, 100, 110, 120, 130, 140, 150, 160, 180, 200
]

class ShaftDesign:
    def __init__(self, power_kw, speed_rpm, bending_moment, kb=1.5, kt=1.0, 
                 fos=1.0, material="EN8 (Medium Carbon Steel)", has_keyway=True,
                 is_hollow=False, inner_outer_ratio=0.0, shaft_length_mm=500.0):
        """
        Initializes the shaft design parameters.
        :param power_kw: Transmitted power in kW
        :param speed_rpm: Rotational speed in RPM
        :param bending_moment: Applied bending moment in N-mm
        :param kb: Shock/Fatigue factor for bending
        :param kt: Shock/Fatigue factor for torsion
        :param fos: User-specified Factor of Safety
        :param material: Material name from database
        :param has_keyway: Boolean indicating presence of keyways
        :param is_hollow: Boolean indicating if the shaft is hollow
        :param inner_outer_ratio: Ratio (di / do) for hollow shaft
        :param shaft_length_mm: Length of the shaft in mm (used for reactions and critical speed)
        """
        self.power_kw = float(power_kw)
        self.speed_rpm = float(speed_rpm)
        self.bending_moment = float(bending_moment)
        self.kb = float(kb)
        self.kt = float(kt)
        self.fos = float(fos)
        self.material_name = material
        self.has_keyway = has_keyway
        self.is_hollow = is_hollow
        self.k = float(inner_outer_ratio)
        self.shaft_length_mm = float(shaft_length_mm)
        
        # Load material properties
        if self.material_name in MATERIAL_DATABASE:
            self.mat_props = MATERIAL_DATABASE[self.material_name]
        else:
            raise ValueError(f"Material '{self.material_name}' not found in the database.")
            
        self.calculate_torque()
        self.calculate_allowable_stress()
        self.calculate_equivalent_twisting_moment()
        self.calculate_diameter()
        self.perform_advanced_checks()

    def calculate_torque(self):
        """
        Calculates transmitted torque based on power and speed.
        Equation: T (N-m) = (9550 * P_kW) / N_rpm
        Then converted to N-mm.
        """
        if self.speed_rpm <= 0:
            raise ValueError("Rotational speed must be greater than zero.")
        self.torque_nm = (9550.0 * self.power_kw) / self.speed_rpm
        self.torque_nmm = self.torque_nm * 1000.0  # Convert to N-mm

    def calculate_allowable_stress(self):
        """
        ASME Code recommendations for commercial steel shafting:
        Allowable Shear Stress (t_allow) is the minimum of:
        - 30% of Yield Strength in Tension (S_yt)
        - 18% of Ultimate Tensile Strength (S_ut)
        If keyways are present, allowable values are reduced by 25%.
        """
        limit_yt = 0.30 * self.mat_props["S_yt"]
        limit_ut = 0.18 * self.mat_props["S_ut"]
        
        # Select base design shear stress
        base_allowable = min(limit_yt, limit_ut)
        
        # Apply Factor of Safety
        self.allowable_stress = base_allowable / self.fos
        
        # Apply Keyway correction if active (ASME recommends 25% reduction)
        if self.has_keyway:
            self.allowable_stress *= 0.75

    def calculate_equivalent_twisting_moment(self):
        """
        Equivalent Twisting Moment Equation (Te):
        Te = sqrt[ (Kb * M)^2 + (Kt * T)^2 ]
        """
        term_bending = (self.kb * self.bending_moment) ** 2
        term_torsion = (self.kt * self.torque_nmm) ** 2
        self.equivalent_torque = math.sqrt(term_bending + term_torsion)

    def calculate_diameter(self):
        """
        Calculates the minimum required shaft outer diameter based on shear design limits.
        Solid Shaft: d^3 = (16 * Te) / (pi * t_allow)
        Hollow Shaft: d_o^3 = (16 * Te) / (pi * t_allow * (1 - k^4))
        """
        pi_factor = math.pi * self.allowable_stress
        
        if not self.is_hollow:
            # Solid shaft design
            self.calculated_diameter = ((16.0 * self.equivalent_torque) / pi_factor) ** (1.0 / 3.0)
            self.calculated_inner_diameter = 0.0
        else:
            # Hollow shaft design
            reduction_factor = 1.0 - (self.k ** 4)
            if reduction_factor <= 0:
                raise ValueError("Inner-to-outer diameter ratio (k) must be strictly less than 1.0.")
            self.calculated_diameter = ((16.0 * self.equivalent_torque) / (pi_factor * reduction_factor)) ** (1.0 / 3.0)
            self.calculated_inner_diameter = self.calculated_diameter * self.k

        # Select standard diameter from list (rounding up)
        self.recommended_diameter = self.get_standard_size(self.calculated_diameter)
        if self.is_hollow:
            self.recommended_inner_diameter = self.recommended_diameter * self.k
        else:
            self.recommended_inner_diameter = 0.0

    @staticmethod
    def get_standard_size(calculated_size):
        """
        Rounds up the calculated diameter to the nearest standard size.
        """
        for size in STANDARD_DIAMETERS:
            if size >= calculated_size:
                return size
        # Return custom rounded up integer if outside standard range
        return int(math.ceil(calculated_size / 5.0) * 5.0)

    def perform_advanced_checks(self):
        """
        Executes structural integrity checks, critical speed calculations, 
        and deflection behavior under assumptions of a simply supported layout.
        """
        d = self.recommended_diameter
        di = self.recommended_inner_diameter
        
        # 1. Area Moment of Inertia (I) and Polar Moment (J)
        if not self.is_hollow:
            self.I_mm4 = (math.pi * (d ** 4)) / 64.0
            self.J_mm4 = (math.pi * (d ** 4)) / 32.0
            self.cross_area_mm2 = (math.pi * (d ** 2)) / 4.0
        else:
            self.I_mm4 = (math.pi * ((d ** 4) - (di ** 4))) / 64.0
            self.J_mm4 = (math.pi * ((d ** 4) - (di ** 4))) / 32.0
            self.cross_area_mm2 = (math.pi * ((d ** 2) - (di ** 2))) / 4.0

        # 2. Maximum induced shear stress check (using recommended diameter)
        # Torque-only maximum shear: tau = T * r / J
        self.induced_shear_stress = (self.equivalent_torque * (d / 2.0)) / self.J_mm4
        self.actual_fos = (self.mat_props["S_yt"] * 0.3) / self.induced_shear_stress if self.induced_shear_stress > 0 else float('inf')

        # 3. Dynamic and deflection modeling:
        # Assuming simple support with point load causing input bending moment at center: M = F * L / 4 -> F = 4 * M / L
        length_m = self.shaft_length_mm / 1000.0
        if length_m > 0:
            self.central_force_n = (4.0 * self.bending_moment) / self.shaft_length_mm
            self.bearing_reaction_n = self.central_force_n / 2.0
        else:
            self.central_force_n = 0.0
            self.bearing_reaction_n = 0.0

        # Deflection due to concentrated center load: delta_p = (F * L^3) / (48 * E * I)
        # E is converted from GPa to MPa (N/mm2)
        E_mpa = self.mat_props["E"] * 1000.0
        if self.I_mm4 > 0 and self.shaft_length_mm > 0:
            self.deflection_load_mm = (self.central_force_n * (self.shaft_length_mm ** 3)) / (48.0 * E_mpa * self.I_mm4)
        else:
            self.deflection_load_mm = 0.0

        # Deflection due to self weight: delta_w = (5 * w * L^4) / (384 * E * I)
        # Self-weight per unit length (N/mm)
        density_g_mm3 = self.mat_props["density"] * 1e-9  # Convert kg/m3 to kg/mm3
        weight_per_mm = self.cross_area_mm2 * density_g_mm3 * 9.81  # N/mm
        
        if self.I_mm4 > 0 and self.shaft_length_mm > 0:
            self.deflection_weight_mm = (5.0 * weight_per_mm * (self.shaft_length_mm ** 4)) / (384.0 * E_mpa * self.I_mm4)
        else:
            self.deflection_weight_mm = 0.0

        self.total_deflection_mm = self.deflection_load_mm + self.deflection_weight_mm

        # 4. Critical Speed using Rayleigh-Dunkerley approach:
        # f_crit = (1 / 2*pi) * sqrt(g_mm_s2 / total_deflection_mm)
        if self.total_deflection_mm > 0:
            g_mm_s2 = 9810.0
            critical_freq_hz = (1.0 / (2.0 * math.pi)) * math.sqrt(g_mm_s2 / self.total_deflection_mm)
            self.critical_speed_rpm = critical_freq_hz * 60.0
        else:
            self.critical_speed_rpm = 0.0