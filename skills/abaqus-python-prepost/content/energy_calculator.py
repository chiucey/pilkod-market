# -*- coding: utf-8 -*-
"""
Energy Calculator Module
Calculate energy components in cylindrical coordinates from stress and strain data.
"""

import math
from coord_transform import rotate_stress_to_cylindrical, rotate_engineering_strain_to_cylindrical


class EnergyAccumulator:
    """
    Class for accumulating energy components over frames.
    """

    def __init__(self):
        """Initialize energy accumulators."""
        self.acc_rad = 0.0  # Radial energy
        self.acc_cir = 0.0  # Circumferential energy
        self.acc_axi = 0.0  # Axial energy
        self.acc_tan = 0.0  # Tangential (shear) energy

    def get_total(self):
        """
        Get total accumulated energy.

        Returns:
            float: Total energy
        """
        return self.acc_rad + self.acc_cir + self.acc_axi + self.acc_tan

    def get_dict(self):
        """
        Get energy components as dictionary.

        Returns:
            dict: {'rad': ..., 'cir': ..., 'axi': ..., 'tan': ...}
        """
        return {
            'rad': self.acc_rad,
            'cir': self.acc_cir,
            'axi': self.acc_axi,
            'tan': self.acc_tan
        }

    def add_frame_energy(self, frame_energy):
        """
        Add frame energy to accumulators.

        Args:
            frame_energy: dict with 'rad', 'cir', 'axi', 'tan' values
        """
        self.acc_rad += frame_energy.get('rad', 0.0)
        self.acc_cir += frame_energy.get('cir', 0.0)
        self.acc_axi += frame_energy.get('axi', 0.0)
        self.acc_tan += frame_energy.get('tan', 0.0)


def calculate_frame_energy_delta(stress_curr, strain_curr,
                                  stress_prev, strain_prev,
                                  volume, theta):
    """
    Calculate energy increment for one integration point using trapezoidal rule.

    Energy increment = 0.5 * (stress_curr + stress_prev) * (strain_curr - strain_prev) * volume

    Args:
        stress_curr: Current stress in Cartesian [s11, s22, s33, s12, s13, s23]
        strain_curr: Current strain in Cartesian [e11, e22, e33, e12, e13, e23]
        stress_prev: Previous stress in Cartesian
        strain_prev: Previous strain in Cartesian
        volume: Integration point volume
        theta: Rotation angle for cylindrical coordinates

    Returns:
        dict: Energy increments {'rad': ..., 'cir': ..., 'axi': ..., 'tan': ...}
    """
    # Rotate stress to cylindrical
    s_curr = rotate_stress_to_cylindrical(
        stress_curr[0], stress_curr[1], stress_curr[2],
        stress_curr[3], stress_curr[4], stress_curr[5], theta
    )
    s_prev = rotate_stress_to_cylindrical(
        stress_prev[0], stress_prev[1], stress_prev[2],
        stress_prev[3], stress_prev[4], stress_prev[5], theta
    )

    # Rotate strain to cylindrical (handles engineering vs tensor conversion)
    le_curr = rotate_engineering_strain_to_cylindrical(strain_curr, theta)
    le_prev = rotate_engineering_strain_to_cylindrical(strain_prev, theta)

    # Calculate energy increments using trapezoidal rule
    # W = integral(s * dε) ≈ 0.5 * (s_curr + s_prev) * (ε_curr - ε_prev) * V

    e_rad = 0.5 * (s_curr[0] + s_prev[0]) * (le_curr[0] - le_prev[0]) * volume
    e_cir = 0.5 * (s_curr[1] + s_prev[1]) * (le_curr[1] - le_prev[1]) * volume
    e_axi = 0.5 * (s_curr[2] + s_prev[2]) * (le_curr[2] - le_prev[2]) * volume

    # Shear energy (all three shear components)
    e_tan = 0.5 * (
        (s_curr[3] + s_prev[3]) * (le_curr[3] - le_prev[3]) +
        (s_curr[4] + s_prev[4]) * (le_curr[4] - le_prev[4]) +
        (s_curr[5] + s_prev[5]) * (le_curr[5] - le_prev[5])
    ) * volume

    return {
        'rad': e_rad,
        'cir': e_cir,
        'axi': e_axi,
        'tan': e_tan
    }


def calculate_integration_point_energy_increment(s_vals, le_vals, s_last, le_last,
                                                 v_vals, c_vals, ip_index):
    """
    Calculate energy increment for a single integration point.

    This is a wrapper that extracts data from field output values.

    Args:
        s_vals: Current stress values list
        le_vals: Current strain values list
        s_last: Previous stress values list
        le_last: Previous strain values list
        v_vals: Volume values list
        c_vals: Coordinate values list
        ip_index: Integration point index

    Returns:
        dict: Energy increment with centroid position
    """
    # Get stress and strain data
    stress_curr = s_vals[ip_index].data
    strain_curr = le_vals[ip_index].data
    stress_prev = s_last[ip_index].data
    strain_prev = le_last[ip_index].data
    volume = v_vals[ip_index].data

    # Get centroid coordinates and calculate theta
    c_data = c_vals[ip_index].data
    x = c_data[0] if len(c_data) > 0 else 0.0
    y = c_data[1] if len(c_data) > 1 else 0.0
    theta = math.atan2(y, x)

    # Calculate energy
    energy = calculate_frame_energy_delta(
        stress_curr, strain_curr,
        stress_prev, strain_prev,
        volume, theta
    )

    return energy


def sum_frame_energies(frame_energy_list):
    """
    Sum energy contributions from all integration points.

    Args:
        frame_energy_list: List of dicts with energy values

    Returns:
        dict: Total frame energy
    """
    total = {'rad': 0.0, 'cir': 0.0, 'axi': 0.0, 'tan': 0.0}

    for energy in frame_energy_list:
        total['rad'] += energy.get('rad', 0.0)
        total['cir'] += energy.get('cir', 0.0)
        total['axi'] += energy.get('axi', 0.0)
        total['tan'] += energy.get('tan', 0.0)

    return total


def calculate_error(calculated_energy, reference_energy):
    """
    Calculate relative error between calculated and reference energy.

    Args:
        calculated_energy: Calculated energy value
        reference_energy: Reference (Abaqus) energy value

    Returns:
        float: Relative error (absolute value)
    """
    if abs(reference_energy) > 1e-10:
        return abs(calculated_energy - reference_energy) / abs(reference_energy)
    return 0.0
