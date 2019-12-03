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
filename = 'C:\\Users\\susanmeerdink\\Dropbox (UFL)\\Analysis\\Thermal Experiment\\Soledad\\IR_55920_Copy.jpg'
flir = flirimageextractor.FlirImageExtractor(exiftool_path="C:\\Users\\susanmeerdink\\.utilities\\exiftool.exe")
flir.process_image(filename, RGB=True)

## Examine thermal and full resolution RGB images
# Most FLIR cameras take a thermal image and a corresponding RGB image. 
# The RGB camera is higher resolution and has a larger field of view. 
therm = flir.get_thermal_np()
rgb_fullres = flir.get_rgb_np()
#plt.figure(figsize=(10,5))
#plt.subplot(1,2,1)
#plt.imshow(therm)
#plt.title('Thermal Image')
#plt.subplot(1,2,2)
#plt.imshow(rgb_fullres)
#plt.title('RGB Full Resolution Image')
#plt.show(block='TRUE') # I needed to have block=TRUE for image to remain displayed
#
### Check how well thermal and rgb registration is without manually correction
## You can see that the images do not line up and there is an offset even after 
## correcting for offset provided in file header
#rgb_lowres, rgb_crop = u.extract_coarse_image(flir)
#plt.figure(figsize=(10,5))
#plt.subplot(1,2,1)
#plt.imshow(therm)
#plt.title('Thermal Image')
#plt.subplot(1,2,2)
#plt.imshow(rgb_crop)
#plt.title('RGB Cropped Image (with NO manual adjustment)')
#plt.show(block='TRUE') 
#
### Determine manual correction of Thermal and RGB registration 
#offset, pts_temp, pts_rgb = u.manual_img_registration(filename)
#print('X pixel offset is ' + str(offset[0]) + 'and Y pixel offset is ' + str(offset[1]))

## Fix Thermal and RGB registration with manual correction
# You can see with the manually determined offsets that the images are now aligned.
# By doing this we can use the RGB image to classify the material types in the images.
# This is useful if you are interested in one particular part or class type.
offset = [-155, -68]
rgb_lowres, rgb_crop = u.extract_coarse_image(flir, offset=offset)
plt.figure(figsize=(10,5))
plt.subplot(1,2,1)
plt.imshow(therm)
plt.title('Thermal Image')
plt.subplot(1,2,2)
plt.imshow(rgb_crop)
plt.title('RGB Cropped Image (with manual adjustment)')
plt.show(block='TRUE') 

# Build a mask of your area of interest 
mask = np.zeros((rgb_crop.shape[0], rgb_crop.shape[1]))
mask[50:270,210:380] = 1
rgb_mask = rgb_crop
for d in range(0,rgb_crop.shape[2]):
    rgb_mask[:,:,d] = rgb_crop[:,:,d] * mask   
plt.figure(figsize=(10,5))
plt.imshow(rgb_mask)
plt.show(block='TRUE')

# Classify using K-Means the newly masked rgb image
rgb_class, rgbqcolor = u.classify_rgb(rgb_mask, 3)

# Pull out just the class for plant material
class_of_interest = np.ones((rgb_class.shape[0], rgb_class.shape[1]))
class_of_interest = np.ma.masked_where(rgb_class != 2, class_of_interest)
plt.figure(figsize=(10,10))
plt.imshow(class_of_interest)
plt.show(block='TRUE')

# Pull out thermal pixels of just plants
therm_masked = np.ma.masked_where(class_of_interest != 1, therm)
plt.figure(figsize=(10,5))
plt.subplot(1,2,1)
plt.imshow(therm)
plt.subplot(1,2,2)
plt.imshow(therm_masked)
plt.show(block='TRUE')

## END