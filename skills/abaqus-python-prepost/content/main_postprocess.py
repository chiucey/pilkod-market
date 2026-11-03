# -*- coding: utf-8 -*-
"""
Main Post-processing Script
Calculate energy components in cylindrical coordinates from Abaqus ODB results.
Uses modular architecture with separate modules for coordinate transformation,
strain transformation, and energy calculation.
"""

# Import modules
import math
import sys
import os

# Try to import xlwt for Excel output
try:
    import xlwt
    XLWT_AVAILABLE = True
except ImportError:
    XLWT_AVAILABLE = False
    print("Warning: xlwt not available, will use CSV output")

# Import custom modules
from odb_reader import ODBReader
from energy_calculator import EnergyAccumulator, calculate_integration_point_energy_increment


# ============================================================================
# Configuration
# ============================================================================

# ODB file configuration
ODB_NAME = 'Job-773-No-Damage-1'  # Without .odb extension

# Output configuration
OUTPUT_FILENAME = 'Energy_Results_Cylindrical.xls'

# Instance name (set to None for auto-detection)
INSTANCE_NAME = None

# Use plastic strain instead of total strain
USE_PLASTIC_STRAIN = True

# ============================================================================
# Helper Functions
# ============================================================================

def setup_output_file():
    """
    Initialize output file (Excel or CSV).

    Returns:
        tuple: (file_handle, format_string) or None
    """
    if XLWT_AVAILABLE:
        wbk = xlwt.Workbook()
        sheet = wbk.add_sheet('Cylindrical_Energy')

        # Headers
        headers = [
            'Frame', 'Time',
            'ALLKE', 'ALLIE',
            'Calc_E_rad', 'Calc_E_cir', 'Calc_E_axi', 'Calc_E_tan',
            'Total_Calc_Work', 'Total_Reference_Work',
            'Error_Prop'
        ]

        for col, h in enumerate(headers):
            sheet.write(0, col, h)

        return wbk, sheet, 'xls'
    else:
        # CSV output fallback
        csv_file = open(OUTPUT_FILENAME.replace('.xls', '.csv'), 'w')
        headers = [
            'Frame,Time,ALLKE,ALLIE,Calc_E_rad,Calc_E_cir,Calc_E_axi,Calc_E_tan,Total_Calc_Work,Total_Reference_Work,Error_Prop'
        ]
        csv_file.write(','.join(headers) + '\n')
        return csv_file, None, 'csv'


def write_row_xls(sheet, row_idx, data):
    """Write a row to Excel sheet."""
    for col, value in enumerate(data):
        sheet.write(row_idx, col, value)


def write_row_csv(csv_file, data):
    """Write a row to CSV file."""
    csv_file.write(','.join(str(v) for v in data) + '\n')


def get_strain_data(frame_data, use_plastic=True):
    """
    Get strain data from frame.

    Args:
        frame_data: Dictionary from ODBReader
        use_plastic: Use plastic strain instead of total strain

    Returns:
        Strain values list or None
    """
    if use_plastic and frame_data.get('PE') is not None:
        return frame_data['PE']
    elif frame_data.get('LE') is not None:
        return frame_data['LE']
    elif frame_data.get('PE') is not None:
        return frame_data['PE']
    return None


# ============================================================================
# Main Processing Function
# ============================================================================

def process_energy_calculation():
    """
    Main function to process ODB and calculate energy in cylindrical coordinates.
    """
    print("=" * 60)
    print("Abaqus Energy Post-processing - Cylindrical Coordinates")
    print("=" * 60)

    # Open ODB
    print("\n1. Opening ODB file: {}.odb".format(ODB_NAME))
    reader = ODBReader(ODB_NAME)
    print("   Number of frames: {}".format(reader.num_frames))

    # Get reference energy from history
    print("\n2. Extracting reference energy from history...")
    allke_data = reader.get_assembly_history('ALLKE')
    allie_data = reader.get_assembly_history('ALLIE')

    if not allke_data:
        print("   Warning: ALLKE not found in history outputs")
    if not allie_data:
        print("   Warning: ALLIE not found in history outputs")

    # Setup output
    print("\n3. Setting up output file: {}".format(OUTPUT_FILENAME))
    output_handle, sheet, output_type = setup_output_file()

    # Initialize energy accumulator
    accumulator = EnergyAccumulator()

    # Process each frame
    print("\n4. Processing frames...")
    print("-" * 60)

    for kf in range(reader.num_frames):
        print("   Processing frame {}...".format(kf))

        # Get current frame data
        curr_data = reader.get_field_data_at_frame(kf, INSTANCE_NAME)

        # Check required data
        S_curr = curr_data.get('S')
        strain_curr = get_strain_data(curr_data, USE_PLASTIC_STRAIN)
        V_curr = curr_data.get('IVOL')
        C_curr = curr_data.get('COORD')

        if S_curr is None or strain_curr is None or V_curr is None or C_curr is None:
            print("      Warning: Missing data at frame {}, skipping...".format(kf))
            continue

        # Get previous frame data for delta calculation
        curr_frame_sum = {'rad': 0.0, 'cir': 0.0, 'axi': 0.0, 'tan': 0.0}

        if kf > 0:
            prev_data = reader.get_field_data_at_frame(kf - 1, INSTANCE_NAME)

            S_prev = prev_data.get('S')
            strain_prev = get_strain_data(prev_data, USE_PLASTIC_STRAIN)

            if S_prev is None or strain_prev is None:
                print("      Warning: Previous frame missing data, skipping delta...")
            else:
                # Get previous COORD if current doesn't have it
                C_prev = prev_data.get('COORD')
                if C_curr is None:
                    C_curr = C_prev

                # Calculate energy increment for each integration point
                num_ips = min(len(V_curr), len(S_curr), len(strain_curr))

                for i in range(num_ips):
                    # Get centroid coordinates for this integration point
                    elem_centroid = reader.get_element_centroid_for_integration_point(
                        curr_data['frame'], i, INSTANCE_NAME
                    )

                    if elem_centroid is None:
                        # Fallback: use COORD field data
                        if i < len(C_curr):
                            c_data = C_curr[i].data
                            x = c_data[0] if len(c_data) > 0 else 0.0
                            y = c_data[1] if len(c_data) > 1 else 0.0
                        else:
                            x, y = 0.0, 0.0
                    else:
                        x, y, _ = elem_centroid

                    theta = math.atan2(y, x)

                    # Get stress and strain data
                    stress_curr = S_curr[i].data
                    strain_curr_i = strain_curr[i].data
                    stress_prev = S_prev[i].data
                    strain_prev_i = strain_prev[i].data
                    volume = V_curr[i].data

                    # Calculate energy increment
                    from energy_calculator import calculate_frame_energy_delta

                    delta = calculate_frame_energy_delta(
                        stress_curr, strain_curr_i,
                        stress_prev, strain_prev_i,
                        volume, theta
                    )

                    curr_frame_sum['rad'] += delta['rad']
                    curr_frame_sum['cir'] += delta['cir']
                    curr_frame_sum['axi'] += delta['axi']
                    curr_frame_sum['tan'] += delta['tan']

        # Accumulate energy
        accumulator.add_frame_energy(curr_frame_sum)

        # Get reference values
        allke_val = allke_data[kf][1] if kf < len(allke_data) else 0.0
        allie_val = allie_data[kf][1] if kf < len(allie_data) else 0.0

        # Calculate total and error
        total_calc = accumulator.get_total()
        total_ref = allie_val

        if abs(total_ref) > 1e-10:
            error = abs(total_calc - total_ref) / total_ref
        else:
            error = 0.0

        # Get frame time
        frame_time = reader.step.frames[kf].frameValue

        # Write output
        if output_type == 'xls':
            row_data = [
                kf, frame_time,
                round(allke_val, 5),
                round(allie_val, 5),
                round(accumulator.acc_rad, 5),
                round(accumulator.acc_cir, 5),
                round(accumulator.acc_axi, 5),
                round(accumulator.acc_tan, 5),
                round(total_calc, 5),
                round(total_ref, 5),
                round(error, 5)
            ]
            write_row_xls(sheet, kf + 1, row_data)
        else:
            row_data = [
                kf, frame_time,
                allke_val, allie_val,
                accumulator.acc_rad, accumulator.acc_cir,
                accumulator.acc_axi, accumulator.acc_tan,
                total_calc, total_ref, error
            ]
            write_row_csv(output_handle, row_data)

        print("      Frame {}: Total = {:.5f}, Ref = {:.5f}, Error = {:.2%}".format(
            kf, total_calc, total_ref, error
        ))

    # Save output file
    print("-" * 60)

    if output_type == 'xls':
        output_handle.save(OUTPUT_FILENAME)
        print("\n5. Results saved to: {}".format(OUTPUT_FILENAME))
    else:
        output_handle.close()
        print("\n5. Results saved to: {}".format(OUTPUT_FILENAME.replace('.xls', '.csv')))

    # Close ODB
    reader.close()

    print("\n" + "=" * 60)
    print("Processing complete!")
    print("=" * 60)


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == '__main__':
    # Allow custom ODB name via command line
    if len(sys.argv) > 1:
        ODB_NAME = sys.argv[1]

    if len(sys.argv) > 2:
        OUTPUT_FILENAME = sys.argv[2]

    process_energy_calculation()
