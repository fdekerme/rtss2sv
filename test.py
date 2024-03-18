import pydicom
import numpy as np
import os
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString

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

    # Iterate over each contour in the structure
    for roi in rtss.ROIContourSequence:
        if roi.ReferencedROINumber == roi_number:
            for j, contour_sequence in enumerate(roi.ContourSequence):
                # Add the contour element
                contour = SubElement(timestep, 'contour')
                contour.set('id', '0')
                contour.set('type', 'Contour')
                contour.set('method', 'LevelSet')
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
                pos.set('x', '-1.89270514490339')
                pos.set('y', '-1.72976277330768')
                pos.set('z', '12.915622113488325')

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

                points = np.array(contour_sequence.ContourData)
                reshaped_points = points.reshape(-1, 3)
                for k, point in enumerate(reshaped_points):
                    SubElement(control_points, 'point', id=str(k), x=str(point[0]), y=str(point[1]), z=str(point[2]))
                    SubElement(contour_points, 'point', id=str(k), x=str(point[0]), y=str(point[1]), z=str(point[2]))



    # Write the .ctgr file
    xml = parseString(tostring(root, encoding='UTF-8')).toprettyxml(indent="   ")
    with open(os.path.join(output_path,roi_name + ".ctgr"), 'w') as f:
        f.write(xml)

rtss_path = "1.3.12.2.1107.5.1.4.49226.30000019112706455609300000818--1.2.276.0.7230010.3.1.4.296486144.178182.1685377991.264831_rtss.dcm"  
output_path = "C://Users//franc//Documents//Code_python//dcm2ctgr//output"
rtss = pydicom.dcmread(rtss_path)
roi_names = [roi.ROIName for roi in rtss.StructureSetROISequence]
for roi_name in roi_names:
    rtss2ctgr(rtss, roi_name, output_path)