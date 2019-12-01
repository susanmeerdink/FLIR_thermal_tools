# -*- coding: utf-8 -*-
"""
code to try and develop gui that gathers points that match the two images
Created on Sun Dec  1 09:49:24 2019

@author: susanmeerdink
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TKAgg')
import flirimageextractor
import utilities as u

filename = 'C:\\Users\\susanmeerdink\\Dropbox (UFL)\\Analysis\\Thermal Experiment\\Soledad\\IR_55920_Copy.jpg'
offset, pts_temp, pts_rgb = u.manual_img_registration(filename)

flir = flirimageextractor.FlirImageExtractor(exiftool_path="C:\\Users\\susanmeerdink\\.utilities\\exiftool.exe")
flir.process_image(filename, RGB=True)
lowres_img, crop_img = u.extract_coarse_image(flir, offset=offset)

therm = flir.get_thermal_np()
plt.figure(figsize=(10,10))
plt.subplot(1,2,1)
plt.imshow(therm)
plt.subplot(1,2,2)
plt.imshow(crop_img)
plt.show(block='TRUE')