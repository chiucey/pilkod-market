# -*- coding: utf-8 -*-
"""
Configuration File
Edit this file to customize the post-processing parameters.
"""

# ============================================================================
# ODB Configuration
# ============================================================================

# ODB file name (without .odb extension)
ODB_NAME = 'Job-773-No-Damage-1'

# Instance name in the assembly (None for auto-detection)
# Examples: 'PART-1-1', 'ASSEMBLY'
INSTANCE_NAME = None

# ============================================================================
# Output Configuration
# ============================================================================

# Output filename for results
OUTPUT_FILENAME = 'Energy_Results_Cylindrical.xls'

# Output directory (empty string for current directory)
OUTPUT_DIR = ''

# ============================================================================
# Calculation Configuration
# ============================================================================

# Use plastic strain (PE) instead of total strain (LE)
# Set to True for elastic-plastic analysis
# Set to False for purely elastic analysis
USE_PLASTIC_STRAIN = True

# Coordinate system: 'cylindrical' or 'cartesian'
COORD_SYSTEM = 'cylindrical'

# ============================================================================
# Strain Type Selection
# ============================================================================

# Available strain types in Abaqus:
# 'LE' - Logarithmic strain (total strain in nonlinear analysis)
# 'PE' - Plastic strain (only for elasto-plastic materials)
# 'EE' - Elastic strain
# 'NE' - Nominal strain

STRAIN_TYPE = 'PE' if USE_PLASTIC_STRAIN else 'LE'

# ============================================================================
# Energy Components
# ============================================================================

# Energy components to calculate:
# 'rad' - Radial energy (in cylindrical coords)
# 'cir' - Circumferential/hoop energy
# 'axi' - Axial energy
# 'tan' - Tangential (shear) energy

ENERGY_COMPONENTS = ['rad', 'cir', 'axi', 'tan']

# ============================================================================
# Error Calculation Reference
# ============================================================================

# Reference energy for error calculation:
# 'ALLIE' - Internal energy
# 'ALLKE' - Kinetic energy
# 'ALLWK' - External work
# 'ALLSD' - Strain energy

REFERENCE_ENERGY = 'ALLIE'

# ============================================================================
# Advanced Settings
# ============================================================================

# Use element centroid for coordinate mapping (recommended)
USE_ELEMENT_CENTROID = True

# Integration point position in field output
# ELEMENT_INTEGRATION_POINT - integration point values
# ELEMENT_CENTROID - centroid values (average)
# NODAL - nodal values
POSITION = 'ELEMENT_INTEGRATION_POINT'

# ============================================================================
# Debug Settings
# ============================================================================

# Print detailed debug information
DEBUG_MODE = False

# Maximum frames to process (0 = all frames)
MAX_FRAMES = 0

# Start frame index (0 = first frame)
START_FRAME = 0
