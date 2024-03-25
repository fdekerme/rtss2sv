This script converts DICOM RTStrucure (RTSS) files into SimVascular-readable path (.pth) and segmentation (.ctgr) files.

To use it:
1) Use `parse_rtss` from the `parse_rtss.py` file to generate a .csv file `contour_data.csv` containing a dictionary. This dictionary represents the contours of every structure present in the RTSS (only those selected in roi_names).

2) SimVascular's PythonAPI isn't easy to install (with `pip install sv`, for example) and it's not possible (I think, to check) to install a third-party package (like `pydicom`, for example). As a result, you need to run the `main.py` code with the following function (or equivalent under Linux/MacOS, see https://simvascular.github.io/documentation/python_interface.html):

`Start-Process -FilePath "C:\Program Files\SimVascular\SimVascular\2023-03-27\sv.bat" -NoNewWindow -ArgumentList "--python", "-- C:\Users\user_name\Documents\Code_python\dcm2ctgr\main.py"`

A simple prompt can be launched with:

	`Start-Process -FilePath ""C:\Program Files\SimVascular\SimVascular\2023-03-27\sv.bat" --python`

and then get all the methods with
```
	import sv
	help(sv.segmentation.Contour())
```
SimVascular's PythonAPI is in beta. As a result, not all functions are available (see https://simtk.org/plugins/phpBB/viewtopicPhpbb.php?f=188&t=17705&p=49311&start=0&view=). In particular, the code could be greatly simplified if sv.segmentation.Series() had the same functions as sv.pathplanning.Series() (a constructor in particular).

Several resources are available:
- Official documentation: https://simvascular.github.io/documentation/python_interface.html
- Source code: https://github.com/SimVascular/SimVascular/tree/master/Code/Source/PythonAPI
- Tools: https://github.com/ktbolt/cardiovascular/tree/master
- Other tools: https://github.com/neilbalch/SimVascular-pythondemos/tree/master
- SimVascular forum: https://simtk.org/plugins/phpBB/viewtopicPhpbb.php?f=188&t=15296&p=44489&start=0&view=

More things to note:

- maybe check the way I did the scaling (`scaling_factor`), comparing to https://github.com/ktbolt/cardiovascular/tree/master/scale-contours-ctgr/python
- The code part:
```
	number_of_subdivision = 10
    path = sv.pathplanning.Path()
    path.set_subdivision_method("SUBDIVISION", number_of_subdivision)
```
	as well as the

	`_get_control_points_id(path)`

may seem strange. The problem is the following: I generate the path's control points via RTSS contours (`seg.get_center()`). 
I then define the path via `path.set_control_points(path_control_points)`. The API then automatically interpolates between these points to form a "curve". 
So, a Path may have 20 control points, but its Curve is made up of 200 points. Each of these points is characterized by its ID. 
However, once the Path has been generated, there is no method (as far as I know) for tracing the ID of the control points. 
And it's precisely at these control points that the segmentation points are located. 
This code can therefore be used to find out the ID of the control points in the interpolated curve.  