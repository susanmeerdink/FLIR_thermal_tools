# -*- coding: utf-8 -*-
"""
Now that i have a manually corrected image I would like to use the RGB to 
get classes or just vegetation.

Created on Mon Dec  2 11:43:03 2019

@author: susanmeerdink
"""
import flirimageextractor
import utilities as u
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np

filename = 'C:\\Users\\susanmeerdink\\Dropbox (UFL)\\Analysis\\Thermal Experiment\\Soledad\\IR_55920_Copy.jpg'
flir = flirimageextractor.FlirImageExtractor(exiftool_path="C:\\Users\\susanmeerdink\\.utilities\\exiftool.exe")
flir.process_image(filename, RGB=True)

offset = [-155, -68]
rgb_lowres, rgb_crop = u.extract_coarse_image(flir, offset=offset)

rgb_class, rgb_qcolor = u.classify_rgb(rgb_crop, 6)

idx_x, idx_y = np.where()

plt.show(block='TRUE') 
