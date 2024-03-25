#!/usr/bin/env python
import sv
import csv
import os
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString


# ######################################
# This script is used to calculate the
# angle between the planes of two
# contours. (contour_id1, contour_id2)
# To lauch this code: 
# Start-Process -FilePath "C:\Program Files\SimVascular\SimVascular\2023-03-27\sv.bat"  -NoNewWindow -ArgumentList "--python", "-- C:\Users\franc\Documents\Code_python\dcm2ctgr\main.py"
# ######################################
# https://github.com/SimVascular/SimVascular-Tests/blob/master/new-api-tests/pathplanning/create.py
# use help(sv.pathplanning) to get the list of functions

def load_csv_contour_data(csv_file_path):
    loaded_data = {}
    with open(csv_file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for roi, data in row.items():
                loaded_data[roi] = eval(data)
    return loaded_data

def _get_control_points_id(path):
    """Get the control points of the path that match the contour control points"""

    if path.get_subdivision_method() != "SUBDIVISION":
        raise ValueError("The path must be created with the SUBDIVISION method")
    
    number_of_subdivision = path.get_num_subdivisions()
    number_of_control_points = len(path.get_control_points())
    number_of_curve_points = path.get_num_curve_points()

    if number_of_control_points * number_of_subdivision != number_of_curve_points:
        #raise ValueError("The number of control points and the number of curve points do not match")
        print("")

    cp_id_corres_dict = {}
    for cp_id, _ in enumerate(path.get_control_points()):
        cp_id_corres_dict[cp_id] = cp_id * number_of_subdivision
    
    return cp_id_corres_dict


def generate_contour(cp, id, time_step, path, curve_id, scaling_factor = 1.0):

    # path.get_curve_point(curve_id), path.get_control_point(id) and seg.get_center() should be the same point
    if path.get_curve_point(curve_id) != path.get_control_points()[id]:
        raise ValueError("The path control point does not match the contour control point")

    contour = SubElement(time_step, 'contour')
    contour.set('id', str(id))
    contour.set('type', 'Contour')
    contour.set('method', 'Manual')
    contour.set('closed', 'true')
    contour.set('min_control_number', '0')
    contour.set('max_control_number', '0')
    contour.set('subdivision_type', '0')
    contour.set('subdivision_number', '0')
    contour.set('subdivision_spacing', '0')

    path_point = SubElement(contour, 'path_point')
    path_point.set('id', str(curve_id))
    pos_data = path.get_curve_tangent(curve_id)
    pos = SubElement(path_point, 'pos')
    pos.set('x', str(pos_data[0] * scaling_factor))
    pos.set('y', str(pos_data[1] * scaling_factor))
    pos.set('z', str(pos_data[2] * scaling_factor))

    tangent = SubElement(path_point, 'tangent')
    tangent_data = path.get_curve_tangent(curve_id)
    tangent.set('x', str(tangent_data[0]))
    tangent.set('y', str(tangent_data[1]))
    tangent.set('z', str(tangent_data[2]))
                
    rotation = SubElement(path_point, 'rotation')
    rotation_data = path.get_curve_normal(curve_id)
    rotation.set('x', str(rotation_data[0]))
    rotation.set('y', str(rotation_data[1]))
    rotation.set('z', str(rotation_data[2]))

    control_points = SubElement(contour, 'control_points')
    contour_points = SubElement(contour, 'contour_points')
    for k, point in enumerate(cp):
        x_pos, y_pos, z_pos = str(point[0] * scaling_factor), str(point[1] * scaling_factor), str(point[2] * scaling_factor)
        SubElement(control_points, 'point', id=str(k), x=x_pos, y=y_pos, z=z_pos)
        SubElement(contour_points, 'point', id=str(k), x=x_pos, y=y_pos, z=z_pos)


def rtss2pth(contour_data, roi_name, roi_id, output_path, scaling_factor = 1.0):
    ''' Create a segmentation from a path curve point.
    https://github.com/SimVascular/SimVascular-Tests/blob/master/new-api-tests/segmentation/polygon-path.py
    '''
    number_of_subdivision = 10
    path = sv.pathplanning.Path()
    path.set_subdivision_method("SUBDIVISION", number_of_subdivision) #10 points beween each control points

    path_control_points = []
    for _, control_points in contour_data[roi_name].items():
        seg = sv.segmentation.Contour(control_points)
        path_control_points.append([x * scaling_factor for x in seg.get_center()])

    path.set_control_points(path_control_points)

    path_serie = sv.pathplanning.Series()
    path_serie.set_name("{}_path.pth".format(roi_name))
    path_serie.set_path(path, 0)
    path_serie.set_path_id(roi_id)
    path_serie.write(os.path.join(output_path["pth"], "{}_path.pth".format(roi_name)))

    # Le code suivant ne fonctionne pas. Le Pyhton API de SimVascular est encore en beta et sv.segmentation.Series() 
    #n'a pas encore toutes les fonctions de sv.pathplanning.Series().
    # Pour voir la documentation, utiliser import sv puis help(sv.segmentation.Series()) dans le shell de SimVascular
    # Pour lancer le shell de SimVascular, utilisez Start-Process -WorkingDirectory "C:\Program Files\SimVascular\SimVascular\2023-03-27\" -FilePath "sv.bat" --python                                                                                                           
    # cf https://simtk.org/plugins/phpBB/viewtopicPhpbb.php?f=188&t=17705&p=0&start=0&view=&sid=c6f5ddfd0afc0410cf9084c2dc473622
    """     
    contour_serie = sv.segmentation.Series()
    contour_serie.set_name("{}".format(roi_name))
    contour_serie.set_contour(segmentation, 0)
    contour_serie.set_contour_id(1)
    contour_serie.write(os.path.join(output_path, "{}_contour.ctgr".format(roi_name))) """

    return path


def rtss2ctgr(contour_data, roi_name, roi_id, output_path, scaling_factor = 1.0):

    path = rtss2pth(contour_data, roi_name, roi_id, output_path, scaling_factor)

    # Create a segmentation.
    contour_group = Element("contourgroup")
    contour_group.set("path_name", "{}_path.pth".format(roi_name))
    contour_group.set("path_id", str(roi_id))
    contour_group.set("reslice_size", "5")
    contour_group.set("point_2D_display_size", "")
    contour_group.set("point_size", "")

    time_step = SubElement(contour_group, "timestep")
    time_step.set("id", "0")

    lofting_parameters = SubElement(time_step, "lofting_parameters")
    lofting_parameters.set("method", "nurbs")

    cp_id_corres_dict = _get_control_points_id(path)
    for id, cp in contour_data[roi_name].items():
        curve_id = cp_id_corres_dict[id]
        generate_contour(cp, id, time_step, path, curve_id, scaling_factor = scaling_factor)
        
    #Save as .ctgr file
    xml_ctgr = parseString(tostring(contour_group, encoding='UTF-8')).toprettyxml(indent="   ")
    with open(os.path.join(output_path["ctgr"], roi_name + "_segmentation.ctgr"), 'w') as f:
        f.write(xml_ctgr)


absolute_path = os.path.dirname(__file__)
contour_data_path = os.path.join(absolute_path, "contour_data_2.csv")
output_path = {"pth": os.path.join(absolute_path,"SV_test//Paths"), "ctgr" :  os.path.join(absolute_path, "SV_test\Segmentations")}
contour_data = load_csv_contour_data(contour_data_path)

for roi_id, roi_name in enumerate(contour_data.keys()):
    rtss2ctgr(contour_data, roi_name, roi_id, output_path, scaling_factor=0.1)