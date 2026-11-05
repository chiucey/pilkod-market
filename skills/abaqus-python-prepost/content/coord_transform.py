# -*- coding: utf-8 -*-
"""
Coordinate Transformation Module
Cartesian to Cylindrical coordinate transformation for stress/strain tensors
"""

import math


def cartesian_to_cylindrical(x, y):
    """
    Convert Cartesian coordinates to cylindrical coordinates (r, theta).

    Args:
        x: X coordinate
        y: Y coordinate

    Returns:
        tuple: (r, theta) where theta is in radians
    """
    r = math.sqrt(x**2 + y**2)
    theta = math.atan2(y, x)
    return r, theta


def rotate_stress_to_cylindrical(s11, s22, s33, s12, s13, s23, theta):
    """
    Rotate stress tensor from Cartesian to cylindrical coordinates.

    Stress components in cylindrical coordinates (r, theta, z):
    - sr: radial stress
    - st: circumferential (hoop) stress
    - sz: axial stress
    - srt: radial-circumferential shear
    - srz: radial-axial shear
    - stz: circumferential-axial shear

    Args:
        s11, s22, s33: Normal stresses (xx, yy, zz)
        s12, s13, s23: Shear stresses (xy, xz, yz)
        theta: Rotation angle in radians

    Returns:
        list: [sr, st, sz, srt, srz, stz]
    """
    c = math.cos(theta)
    s = math.sin(theta)
    c2 = c * c
    s2 = s * s
    cs = c * s

    # Normal stresses transformation
    sr = s11 * c2 + s22 * s2 + 2.0 * s12 * cs
    st = s11 * s2 + s22 * c2 - 2.0 * s12 * cs
    sz = s33

    # Shear stresses transformation
    srt = (s22 - s11) * cs + s12 * (c2 - s2)
    srz = s13 * c + s23 * s
    stz = -s13 * s + s23 * c

    return [sr, st, sz, srt, srz, stz]


def rotate_engineering_strain_to_cylindrical(LE_eng, theta):
    """
    Rotate engineering strain tensor from Cartesian to cylindrical coordinates.

    CRITICAL: Engineering strain must be converted to tensor strain before rotation.
    The LE output from Abaqus is engineering strain, NOT tensor strain.

    Engineering strain: [exx, eyy, ezz, exy, exz, eyz]
    Tensor strain: [exx, eyy, ezz, 2*exy, 2*exz, 2*eyz]

    After rotation in cylindrical coordinates, tensor strain is converted back
    to engineering strain for energy calculation.

    Args:
        LE_eng: Engineering strain [exx, eyy, ezz, exy, exz, eyz]
        theta: Rotation angle in radians

    Returns:
        list: Engineering strain in cylindrical [er, et, ez, ert, erz, etz]
    """
    c = math.cos(theta)
    s = math.sin(theta)
    c2 = c * c
    s2 = s * s
    cs = c * s

    # Convert engineering strain to tensor strain
    exx = LE_eng[0]
    eyy = LE_eng[1]
    ezz = LE_eng[2]
    exy = LE_eng[3] / 2.0
    exz = LE_eng[4] / 2.0
    eyz = LE_eng[5] / 2.0

    # Rotate tensor strain
    er = exx * c2 + eyy * s2 + 2.0 * exy * cs
    et = exx * s2 + eyy * c2 - 2.0 * exy * cs
    ez = ezz

    ert = (eyy - exx) * cs + 2.0 * exy * (c2 - s2)
    erz = exz * c + eyz * s
    etz = -exz * s + eyz * c

    # Convert back to engineering strain
    return [er, et, ez, ert * 2.0, erz * 2.0, etz * 2.0]


def get_element_centroid_rotation(element_centroid):
    """
    Calculate rotation angle for an element at its centroid position.

    Args:
        element_centroid: tuple (x, y, z) or similar coordinate object

    Returns:
        float: Rotation angle theta in radians
    """
    if hasattr(element_centroid, 'data'):
        x = element_centroid.data[0]
        y = element_centroid.data[1]
    else:
        x = element_centroid[0]
        y = element_centroid[1]

    return math.atan2(y, x)
