import pydicom
import numpy as np
import os
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
from scipy.interpolate import BSpline, make_interp_spline

def parse_ROINumber(ds, roi_name):
    for roi in ds.StructureSetROISequence:
        if roi.ROIName == roi_name:
            return roi.ROINumber
    return None

def check_if_rtss(dicom_file):
    if not dicom_file.Modality == 'RTSTRUCT':
        raise ValueError('The input file is not a RTSTRUCT file.')

def rtss2ctgr(rtss, roi_name, output_path):

    check_if_rtss(rtss)

    # Create the root element
    format = Element('format')
    format.set('version', '1.0')

    # Create the root of the .ctgr file
    root = Element('contourgroup', path_name='aorta', path_id='1')

    # Create the timestep element
    timestep = SubElement(root, 'timestep')
    timestep.set('id', '0')

    # Add the lofting_parameters element
    lofting_parameters = SubElement(timestep, 'lofting_parameters')
    lofting_parameters.set('sampling', '1')
    lofting_parameters.set('sample_per_seg', '1')
    lofting_parameters.set('use_linear_sample', '1')
    lofting_parameters.set('linear_multiplier', '1')
    lofting_parameters.set('use_fft', '0')
    lofting_parameters.set('num_modes', '1')

    roi_number = parse_ROINumber(rtss, roi_name)
    control_point_path = {}

    # Iterate over each contour in the structure
    for roi in rtss.ROIContourSequence:
        if roi.ReferencedROINumber == roi_number:
            for contour_sequence in roi.ContourSequence:
                # Add the contour element
                contour = SubElement(timestep, 'contour')
                contour.set('id', str(contour_sequence.ContourNumber))
                contour.set('type', 'Contour')
                contour.set('method', 'Manual')
                if contour_sequence.ContourGeometricType == 'CLOSED_PLANAR':
                    contour.set('closed', 'true')
                else:
                    contour.set('closed', 'false')
                contour.set('min_control_number', '0')
                contour.set('max_control_number', '0')
                contour.set('subdivision_type', '0')
                contour.set('subdivision_number', '0')
                contour.set('subdivision_spacing', '0')

                # Add the path_point element
                path_point = SubElement(contour, 'path_point')
                path_point.set('id', '0') # je ne sais pas à quoi correspond cette valeur

                # Add the pos element
                pos = SubElement(path_point, 'pos')
                pos.set('x', '0.0')
                pos.set('y', '0.0')
                pos.set('z', '0.0')

                # Add the tangent element
                tangent = SubElement(path_point, 'tangent')
                tangent.set('x', '0.0')
                tangent.set('y', '0.0')
                tangent.set('z', '0.0')

                # Add the rotation element
                rotation = SubElement(path_point, 'rotation')
                rotation.set('x', '0.0')
                rotation.set('y', '0.0')
                rotation.set('z', '0.0')

                # Add the control_points element (manually delineated points)
                control_points = SubElement(contour, 'control_points')

                # Add the contour_points element (interpolated points from the control points)
                contour_points = SubElement(contour, 'contour_points')

                points = np.array(contour_sequence.ContourData) * 0.1
                reshaped_points = points.reshape(-1, 3)

                centroid = np.mean(reshaped_points, axis=0)
                control_point_path[contour_sequence.ContourNumber] = centroid

                for k, point in enumerate(reshaped_points):
                    SubElement(control_points, 'point', id=str(k), x=str(point[0]), y=str(point[1]), z=str(point[2]))
                    SubElement(contour_points, 'point', id=str(k), x=str(point[0]), y=str(point[1]), z=str(point[2]))

    # Generate  and write the .pth file
    path = generate_pth(control_point_path)

    # Write the .ctgr file
    xml_ctgr = parseString(tostring(root, encoding='UTF-8')).toprettyxml(indent="   ")
    with open(os.path.join(output_path, roi_name + ".ctgr"), 'w') as f:
        f.write(xml_ctgr)

    # Write the .pth file
    xml_pth = parseString(tostring(path, encoding='UTF-8')).toprettyxml(indent="   ")
    with open(os.path.join(output_path, roi_name + ".pth"), 'w') as f:
        f.write(xml_pth)



def generate_pth(control_point_path):

    # Create the root path element
    path = Element('path', id='1', method='0', calculation_number='', spacing='0', version='1.0', reslice_size='1', point_2D_display_size='', point_size='')

    # Create a timestep element and append it to the root
    timestep = SubElement(path, 'timestep', id='0')

    # Create a path_element and append it to timestep
    path_element = SubElement(timestep, 'path_element', method='0', calculation_number='', spacing='0')

    # Create control_points and path_points elements and append them to path_element
    control_points = SubElement(path_element, 'control_points')
    path_points = SubElement(path_element, 'path_points')

    # Create point elements and append them to control_points
    for id, centroid in control_point_path.items():
        SubElement(control_points, 'point', id=str(id), x=str(centroid[0]), y=str(centroid[1]), z=str(centroid[2]))

        # Create a path_point element with pos, tangent, and rotation elements
        path_point = SubElement(path_points, 'path_point', id=str(id))
        SubElement(path_point, 'pos', x='0.0', y='0.0', z='0.0')
        SubElement(path_point, 'tangent', x='0.0', y='0.0', z='0.0')
        SubElement(path_point, 'rotation', x='0.0', y='0.0', z='0.0')
    
    return path




rtss_path = "1.3.12.2.1107.5.1.4.49226.30000019112706455609300000818--1.2.276.0.7230010.3.1.4.296486144.178182.1685377991.264831_rtss.dcm"  
output_path = "C://Users//franc//Documents//Code_python//dcm2ctgr//output"
rtss = pydicom.dcmread(rtss_path)
roi_names = [roi.ROIName for roi in rtss.StructureSetROISequence]
for roi_name in roi_names:
    rtss2ctgr(rtss, roi_name, output_path)