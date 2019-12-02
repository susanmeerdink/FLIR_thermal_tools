# -*- coding: utf-8 -*-
"""
This script contains a demonstration of the functions and capabilities of this
repository. It will also give an example work flow for a set of images.

@author: susanmeerdink
December 2019
"""

# Importing Functions
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TKAgg') # Needed to have figures display properly. 
import flirimageextractor
import utilities as u

# Load Image using flirimageextractor
# Note: I had to change the path of my exiftool which you may need to also change.
filename = 'C:\\Users\\susanmeerdink\\Dropbox (UFL)\\Analysis\\Thermal Experiment\\Soledad\\IR_55920_Copy.jpg'
flir = flirimageextractor.FlirImageExtractor(exiftool_path="C:\\Users\\susanmeerdink\\.utilities\\exiftool.exe")
flir.process_image(filename, RGB=True)

# Examine thermal and full resolution RGB images
flir.plot()


#lowres_img, crop_img = u.extract_coarse_image(flir, offset=offset)



#offset, pts_temp, pts_rgb = u.manual_img_registration(filename)