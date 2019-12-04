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

## Load Image using flirimageextractor
# Note: I had to change the path of my exiftool which you may need to also change.
filename = 'C:\\Users\\susanmeerdink\\Documents\\Git\\FLIR_thermal_tools\\Test_Images\\IR_56020.jpg'
flir = flirimageextractor.FlirImageExtractor(exiftool_path="C:\\Users\\susanmeerdink\\.utilities\\exiftool.exe")
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

### Determine manual correction of Thermal and RGB registration 
offset, pts_temp, pts_rgb = u.manual_img_registration(flir)
print('X pixel offset is ' + str(offset[0]) + 'and Y pixel offset is ' + str(offset[1]))

## Fix Thermal and RGB registration with manual correction
# You can see with the manually determined offsets that the images are now aligned.
# By doing this we can use the RGB image to classify the material types in the images.
# This is useful if you are interested in one particular part or class type.
# offset = [-155, -68]  # This i the manual offset I got when running the demo images.
rgb_lowres, rgb_crop = u.extract_coarse_image(flir, offset=offset, plot=1)

#  Build a mask of your area of interest 
mask = np.zeros((rgb_crop.shape[0], rgb_crop.shape[1]))
mask[50:270,210:380] = 1
rgb_mask = u.apply_mask_to_rgb(mask, rgb_crop)

# Classify using K-Means the newly masked rgb image
rgb_class, rgb_qcolor = u.classify_rgb(rgb_mask, 3)

# Pull out just the class for plant material
class_mask = u.create_class_mask(rgb_class, 2)


# Pull out thermal pixels of just plants for single image
temp_mask = u.extract_temp_for_class(flir, class_mask)

# Pull out thermal pixels of just plants for a set of images
dirLoc = 'C:\\Users\\susanmeerdink\\Documents\\Git\\FLIR_thermal_tools\\Test_Images\\'
exiftoolpath = "C:\\Users\\susanmeerdink\\.utilities\\exiftool.exe"
all_temp_mask = u.batch_extract_temp_for_class(dirLoc, class_mask, exiftoolpath=exiftoolpath)
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