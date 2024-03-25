import pydicom
import numpy as np
import csv
import os

def _parse_ROINumber(ds, roi_name):
    for roi in ds.StructureSetROISequence:
        if roi.ROIName == roi_name:
            return roi.ROINumber
    return None

def _check_if_rtss(dicom_file):
    if not dicom_file.Modality == 'RTSTRUCT':
        raise ValueError('The input file is not a RTSTRUCT file.')

def parse_rtss(rtss, roi_name):
    _check_if_rtss(rtss)

    control_point_contour = {}

    roi_number = _parse_ROINumber(rtss, roi_name)
    for roi in rtss.ROIContourSequence:
            if roi.ReferencedROINumber == roi_number:
                    for contour_sequence in roi.ContourSequence:
                            points = np.array(contour_sequence.ContourData)
                            reshaped_points = points.reshape(-1, 3).tolist()
                
                            control_point_contour[int(contour_sequence.ContourNumber)] = reshaped_points

    return control_point_contour


absolute_path = os.path.dirname(__file__)
rtss_path = absolute_path + "//data//AGORL_P66//RTSTRUCT//1.3.12.2.1107.5.1.4.49226.30000019112706455609300000818--1.2.276.0.7230010.3.1.4.296486144.178182.1685377991.264831_rtss.dcm"
rtss_path_2 = absolute_path + "//data//AGORL_P66//RTSTRUCT//1.3.12.2.1107.5.1.4.49226.30000019112706455609300000818--1.2.276.0.7230010.3.1.4.548144204.2639.1685347439.482282_rtss.dcm"
output_path = absolute_path
rtss = pydicom.dcmread(rtss_path_2)
roi_names = [roi.ROIName for roi in rtss.StructureSetROISequence]

contour_data = {}
for roi_name in roi_names:
    control_point_contour = parse_rtss(rtss, roi_name)
    contour_data[roi_name] = control_point_contour

with open('contour_data_2.csv', 'w') as f:
    w = csv.DictWriter(f, contour_data.keys())
    w.writeheader()
    w.writerow(contour_data)

