# -*- coding: utf-8 -*-
"""
This script contains a demonstration of the functions and capabilities of this
repository. It will also give an example work flow for a set of images.

@author: susanmeerdink
December 2019

@updated by: KentaItakura
October 2022
"""

# Importing Functions
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TKAgg') # Needed to have figures display properly. 
import flirimageextractor
import utilities as u
import os

absDirName = os.path.dirname(os.path.abspath(__file__))
print('Abosolute directory name of demo.py: ', absDirName)

## Load Image using flirimageextractor
# Note: I had to change the path of my exiftool which you may need to also change.
# filename = 'C:\\Users\\susanmeerdink\\Documents\\Git\\FLIR_thermal_tools\\Test_Images\\IR_56020.jpg'
filename = os.path.join(absDirName,'Test_Images','IR_56020.jpg')
dirLoc = os.path.join(absDirName,'Test_Images')

# Specify the path of exiftool
# Example1
# exiftoolpath = "C:\\Users\\susanmeerdink\\.utilities\\exiftool.exe"
# Example2
exiftoolpath = "C:\Program Files (x86)\exif\exiftool.exe"

flir = flirimageextractor.FlirImageExtractor(exiftool_path=exiftoolpath)

flir.process_image(filename, RGB=True)

## Examine thermal and full resolution RGB images
# Most FLIR cameras take a thermal image and a corresponding RGB image. 
# The RGB camera is higher resolution and has a larger field of view. 
therm = flir.get_thermal_np()
rgb_fullres = flir.get_rgb_np()
plt.figure(figsize=(10,5))
plt.subplot(1,2,1)
plt.imshow(therm)
plt.title('Thermal Image')
plt.subplot(1,2,2)
plt.imshow(rgb_fullres)
plt.title('RGB Full Resolution Image')
plt.show(block='TRUE') # I needed to have block=TRUE for image to remain displayed

## Check how well thermal and rgb registration is without manually correction
# You can see that the images do not line up and there is an offset even after 
# correcting for offset provided in file header
rgb_lowres, rgb_crop = u.extract_coarse_image(flir)

## Save the thermal information into CSV file
pre, ext = os.path.splitext(filename)
csvNameOut = pre+'.csv'
print('The CSV file is named as follows')
print(csvNameOut)
u.save_thermal_csv(flir, csvNameOut)


### Determine manual correction of Thermal and RGB registration 
offset, pts_temp, pts_rgb = u.manual_img_registration(flir)
print('X pixel offset is ' + str(offset[0]) + ' and Y pixel offset is ' + str(offset[1]))

## Fix Thermal and RGB registration with manual correction
# You can see with the manually determined offsets that the images are now aligned.
# By doing this we can use the RGB image to classify the material types in the images.
# This is useful if you are interested in one particular part or class type.
offset = [-155, -70]  # This i the manual offset I got when running the demo images.
rgb_lowres, rgb_crop = u.extract_coarse_image(flir, offset=offset, plot=1)

#  Build a mask of your area of interest 
mask = np.zeros((rgb_crop.shape[0], rgb_crop.shape[1]))
mask[30:270,220:400] = 1
rgb_mask = u.apply_mask_to_rgb(mask, rgb_crop)

# Classify using K-Means the newly masked rgb image
rgb_class, rgb_qcolor = u.classify_rgb(rgb_mask, 3)

# Pull out just the class for plant material
class_mask = u.create_class_mask(rgb_class, 2)

# Correct temperature imagery for correct emissivity
emiss_img = u.develop_correct_emissivity(rgb_class)

# Pull out thermal pixels of just plants for single image
temp_mask = u.extract_temp_for_class(flir, class_mask, emiss_img)

# Pull out thermal pixels of just plants for a set of images
# dirLoc = 'C:\\Users\\susanmeerdink\\Documents\\Git\\FLIR_thermal_tools\\Test_Images\\'

all_temp_mask = u.batch_extract_temp_for_class(dirLoc, class_mask, emiss_img, exiftoolpath=exiftoolpath)
plt.figure(figsize=(15,5))
plt.subplot(1,3,1)
plt.imshow(all_temp_mask[:,:,0])
plt.subplot(1,3,2)
plt.imshow(all_temp_mask[:,:,1])
plt.subplot(1,3,3)
plt.imshow(all_temp_mask[:,:,2])
plt.show(block='TRUE')

# Plot timeseries
u.plot_temp_timeseries(all_temp_mask)

# END