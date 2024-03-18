import pydicom
import numpy as np
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString

rtss_path = "1.3.12.2.1107.5.1.4.49226.30000019112706455609300000818--1.2.276.0.7230010.3.1.4.296486144.178182.1685377991.264831_rtss.dcm"
roi_name = "leftexternalcarotidartery"
# Load the DICOM file
ds = pydicom.dcmread(rtss_path)

# Create the root element
root = Element('format')
root.set('version', '1.0')

# Create the contourgroup element
contourgroup = SubElement(root, 'contourgroup')
contourgroup.set('path_name', 'aorta')
contourgroup.set('path_id', '1')

# Create the timestep element
timestep = SubElement(contourgroup, 'timestep')
timestep.set('id', '0')

# Add the lofting_parameters element
lofting_parameters = SubElement(timestep, 'lofting_parameters')
lofting_parameters.set('sampling', '60')
lofting_parameters.set('sample_per_seg', '12')
lofting_parameters.set('use_linear_sample', '1')
lofting_parameters.set('linear_multiplier', '10')
lofting_parameters.set('use_fft', '0')
lofting_parameters.set('num_modes', '20')

# Add the contour element
contour = SubElement(timestep, 'contour')
contour.set('id', '0')
contour.set('type', 'Contour')
contour.set('method', 'LevelSet')
contour.set('closed', 'true')
contour.set('min_control_number', '2')
contour.set('max_control_number', '2')
contour.set('subdivision_type', '0')
contour.set('subdivision_number', '0')
contour.set('subdivision_spacing', '0')

# Add the path_point element
path_point = SubElement(contour, 'path_point')
path_point.set('id', '16')

# Add the pos element
pos = SubElement(path_point, 'pos')
pos.set('x', '-1.89270514490339')
pos.set('y', '-1.72976277330768')
pos.set('z', '12.915622113488325')

# Add the tangent element
tangent = SubElement(path_point, 'tangent')
tangent.set('x', '0.449215644541724')
tangent.set('y', '0.382101372870501')
tangent.set('z', '-0.807591385262029')

# Add the rotation element
tion = SubElement(path_point, 'rotation')
rotation.set('x', '0')
rotation.set('y', '0.90392911036365')
rotation.set('z', '0.42768231602111')

# Add the control_points element
control_points = SubElement(contour, 'control_points')

# Add the contour_points element
contour_points = SubElement(contour, 'contour_points')

# Iterate over the contours in the DICOM file

roi_number = parse_ROINumber(ds, roi_name)

for roi in ds.ROIContourSequence:
    if roi.ReferencedROINumber == roi_number:
        for contour in roi.ContourSequence:
        # Add the points to the control_points and contour_points elements
            points = np.array(contour.ContourData)
            reshaped_points = points.reshape(-1, 3)
            for point in reshaped_points:
                print(point)
                point_element = SubElement(control_points, 'point')
                point_element.set('x', str(point[0]))
                point_element.set('y', str(point[1]))
                point_element.set('z', str(point[2]))
                point_element = SubElement(contour_points, 'point')
                point_element.set('x', str(point[0]))
                point_element.set('y', str(point[1]))
                point_element.set('z', str(point[2]))

# Generate the XML string
xml = parseString(tostring(root)).toprettyxml(indent="   ")

# Write the XML to a .ctgr file
with open('output.ctgr', 'w') as f:
    f.write(xml)


def parse_ROINumber(ds, roi_name):
    for roi in ds.StructureSetROISequence:
        if roi.ROIName == roi_name:
            return roi.ROINumber
    return None