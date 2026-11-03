# -*- coding: utf-8 -*-
"""
ODB Reader Module
Extract stress, strain, and coordinate data from Abaqus ODB files.
Handles the critical mapping between integration points and element centroids.
"""

from odbAccess import openOdb
import numpy as np


class ODBReader:
    """
    Class for reading and extracting data from Abaqus ODB files.
    Handles coordinate mapping between different output locations.
    """

    def __init__(self, odb_name):
        """
        Initialize ODB reader.

        Args:
            odb_name: ODB file name (without .odb extension)
        """
        self.odb_name = odb_name
        self.odb = openOdb(path=odb_name + '.odb')
        self.step = self.odb.steps[self.odb.steps.keys()[0]]
        self.num_frames = len(self.step.frames)

        # Cache for element centroid coordinates
        self._element_centroids = {}
        self._integration_point_map = {}

    def get_assembly_history(self, variable_name):
        """
        Get history output at assembly level.

        Args:
            variable_name: Variable name (e.g., 'ALLKE', 'ALLIE', 'ALLWK')

        Returns:
            list: List of (frame_index, value) tuples
        """
        history = self.step.historyRegions['Assembly ASSEMBLY'].historyOutputs
        if variable_name in history:
            return history[variable_name].data
        return []

    def get_step_history_regions(self):
        """
        Get all available history regions.

        Returns:
            dict: History regions dictionary
        """
        return self.step.historyRegions

    def build_element_centroid_map(self, instance_name=None):
        """
        Build a map from element labels to their centroid coordinates.
        This is CRITICAL because integration point data (stress/strain)
        and nodal data (coordinates) have different indexing.

        Args:
            instance_name: Instance name (if None, uses the only/first instance)

        Returns:
            dict: {element_label: (x, y, z)}
        """
        if self._element_centroids:
            return self._element_centroids

        if instance_name is None:
            instance_name = self.odb.rootAssembly.instances.keys()[0]

        inst = self.odb.rootAssembly.instances[instance_name]

        for elem in inst.elements:
            # Calculate centroid from connectivity (average of nodes)
            centroid = np.zeros(3)
            for node_label in elem.connectivity:
                node = inst.getNodeFromLabel(node_label)
                centroid += np.array(node.coordinates)
            centroid /= len(elem.connectivity)
            self._element_centroids[elem.label] = tuple(centroid)

        return self._element_centroids

    def build_integration_point_map(self, frame, instance_name=None):
        """
        Build a map from integration point data index to element centroid.

        This solves the fundamental problem: stress/strain are output at
        integration points, while COORD is output at nodes. When mesh
        doesn't have nodes at integration points, we need to use element
        centroid coordinates instead.

        Args:
            frame: Frame object containing fieldOutputs
            instance_name: Instance name

        Returns:
            dict: {integration_point_index: (x, y, z)}
        """
        if instance_name is None:
            instance_name = self.odb.rootAssembly.instances.keys()[0]

        inst = self.odb.rootAssembly.instances[instance_name]

        # Build element centroid map if not already done
        if not self._element_centroids:
            self.build_element_centroid_map(instance_name)

        # Get stress field to determine number of integration points
        S_field = frame.fieldOutputs.getSubset(position=ELEMENT_INTEGRATION_POINT)
        if S_field is None:
            S_field = frame.fieldOutputs['S']

        ip_map = {}
        current_ip = 0

        for val in S_field.values:
            elem_label = val.elementLabel
            if elem_label in self._element_centroids:
                ip_map[current_ip] = self._element_centroids[elem_label]
            current_ip += 1

        return ip_map

    def get_field_data_at_frame(self, frame_index, instance_name=None):
        """
        Extract all necessary field data at a specific frame.

        Args:
            frame_index: Frame index
            instance_name: Instance name

        Returns:
            dict: Dictionary containing:
                - 'S': Stress values
                - 'LE': Logarithmic strain values (or 'PE' for plastic strain)
                - 'IVOL': Integration point volume
                - 'COORD': Coordinates
                - 'frame': Frame object
        """
        frame = self.step.frames[frame_index]

        if instance_name is None:
            instance_name = self.odb.rootAssembly.instances.keys()[0]

        inst = self.odb.rootAssembly.instances[instance_name]

        # Extract field outputs
        result = {
            'frame': frame,
            'S': None,
            'LE': None,
            'PE': None,
            'IVOL': None,
            'COORD': None
        }

        # Get stress
        S_field = frame.fieldOutputs.getSubset(region=inst, position=ELEMENT_INTEGRATION_POINT)
        if S_field and len(S_field.values) > 0:
            result['S'] = S_field.values

        # Get strain - prefer plastic strain for energy calculation
        PE_field = frame.fieldOutputs.getSubset(region=inst, position=ELEMENT_INTEGRATION_POINT,
                                                technicalName='PE')
        if PE_field and len(PE_field.values) > 0:
            result['PE'] = PE_field.values
        else:
            LE_field = frame.fieldOutputs.getSubset(region=inst, position=ELEMENT_INTEGRATION_POINT,
                                                    technicalName='LE')
            if LE_field and len(LE_field.values) > 0:
                result['LE'] = LE_field.values

        # Get integration point volume
        IVOL_field = frame.fieldOutputs.getSubset(region=inst, position=ELEMENT_INTEGRATION_POINT,
                                                  technicalName='IVOL')
        if IVOL_field and len(IVOL_field.values) > 0:
            result['IVOL'] = IVOL_field.values

        # Get coordinates - use ELEMENT_CENTROID for integration point data
        COORD_field = frame.fieldOutputs.getSubset(region=inst, position=ELEMENT_CENTROID,
                                                   technicalName='COORD')
        if COORD_field and len(COORD_field.values) > 0:
            result['COORD'] = COORD_field.values

        return result

    def get_element_centroid_for_integration_point(self, frame, ip_index, instance_name=None):
        """
        Get the element centroid coordinates for a specific integration point.

        This is the KEY function that solves the node-IP mismatch problem.

        Args:
            frame: Frame object
            ip_index: Integration point index in the field output
            instance_name: Instance name

        Returns:
            tuple: (x, y, z) coordinates
        """
        if instance_name is None:
            instance_name = self.odb.rootAssembly.instances.keys()[0]

        inst = self.odb.rootAssembly.instances[instance_name]

        # Get stress field to find element label
        S_field = frame.fieldOutputs.getSubset(region=inst, position=ELEMENT_INTEGRATION_POINT)
        if S_field is None or len(S_field.values) == 0:
            S_field = frame.fieldOutputs['S']

        if ip_index >= len(S_field.values):
            return None

        elem_label = S_field.values[ip_index].elementLabel

        # Build centroid map if needed
        if not self._element_centroids:
            self.build_element_centroid_map(instance_name)

        return self._element_centroids.get(elem_label)

    def close(self):
        """Close the ODB file."""
        self.odb.close()


# Standalone functions for simple usage
def open_odb(odb_name):
    """
    Open an ODB file.

    Args:
        odb_name: ODB file name (without .odb extension)

    Returns:
        ODB object
    """
    return openOdb(path=odb_name + '.odb')


def get_field_output_by_position(frame, region, position, variable_name):
    """
    Get field output at a specific position.

    Args:
        frame: Frame object
        region: Region object
        position: POSITION_CENTROID, ELEMENT_INTEGRATION_POINT, etc.
        variable_name: Variable name (e.g., 'S', 'LE', 'COORD')

    Returns:
        FieldOutput object
    """
    try:
        field = frame.fieldOutputs.getSubset(region=region, position=position,
                                             technicalName=variable_name)
        return field.values if field else []
    except:
        return []
