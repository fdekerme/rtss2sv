import pydicom
import numpy as np
import csv

def parse_ROINumber(ds, roi_name):
    for roi in ds.StructureSetROISequence:
        if roi.ROIName == roi_name:
            return roi.ROINumber
    return None

def check_if_rtss(dicom_file):
    if not dicom_file.Modality == 'RTSTRUCT':
        raise ValueError('The input file is not a RTSTRUCT file.')

def parse_rtss(rtss, roi_name, output_path):
    check_if_rtss(rtss)

    control_point_contour = {}

    roi_number = parse_ROINumber(rtss, roi_name)
    for roi in rtss.ROIContourSequence:
            if roi.ReferencedROINumber == roi_number:
                    for contour_sequence in roi.ContourSequence:
                            points = np.array(contour_sequence.ContourData)
                            reshaped_points = points.reshape(-1, 3).tolist()
                
                            control_point_contour[int(contour_sequence.ContourNumber)] = reshaped_points

    return control_point_contour



rtss_path = "C://Users//franc//Documents//Code_python//dcm2ctgr//data//AGORL_P66//1.3.12.2.1107.5.1.4.49226.30000019112706455609300000818--1.2.276.0.7230010.3.1.4.296486144.178182.1685377991.264831_rtss.dcm"  
output_path = "C://Users//franc//Documents//Code_python//dcm2ctgr//output"
rtss = pydicom.dcmread(rtss_path)
roi_names = [roi.ROIName for roi in rtss.StructureSetROISequence]

contour_data = {}
for roi_name in roi_names:
    control_point_contour = parse_rtss(rtss, roi_name, output_path)
    contour_data[roi_name] = control_point_contour


with open('contour_data.csv', 'w') as f:
    w = csv.DictWriter(f, contour_data.keys())
    w.writeheader()
    w.writerow(contour_data)
    
def load_contour_data(csv_file_path):
    loaded_data = {}
    with open(csv_file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for roi, data in row.items():
                loaded_data[roi] = eval(data)
    return loaded_data
                        

contour_data = load_contour_data("contour_data.csv")
for control_point in contour_data[roi_name].items():
    print(control_point)

