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
import matplotlib
matplotlib.use('TKAgg') # Needed to have figures display properly. 
import numpy.ma as ma 

filename = 'C:\\Users\\susanmeerdink\\Dropbox (UFL)\\Analysis\\Thermal Experiment\\Soledad\\IR_55920_Copy.jpg'
flir = flirimageextractor.FlirImageExtractor(exiftool_path="C:\\Users\\susanmeerdink\\.utilities\\exiftool.exe")
flir.process_image(filename, RGB=True)

offset = [-155, -68]
rgb_lowres, rgb_crop = u.extract_coarse_image(flir, offset=offset)

## building mask 
mask = np.zeros((rgb_crop.shape[0], rgb_crop.shape[1]))
mask[50:270,210:380] = 1
plt.figure(figsize=(15,15))
plt.imshow(mask)
plt.show(block='TRUE')

mask_img = rgb_crop
for d in range(0,rgb_crop.shape[2]):
    mask_img[:,:,d] = rgb_crop[:,:,d] * mask
plt.figure(figsize=(15,15))
plt.imshow(mask_img)
plt.show(block='TRUE')

rgb_class, rgbqcolor = u.classify_rgb(mask_img, 3)

# %%
# Pull out just plants
class_of_interest = np.ones((rgb_class.shape[0], rgb_class.shape[1]))
class_of_interest = np.ma.masked_where(rgb_class != 0, class_of_interest)

plt.figure(figsize=(10,10))
plt.imshow(class_of_interest)
plt.show(block='TRUE')


# %% 
therm = flir.get_thermal_np()
therm_masked = np.ma.masked_where(class_of_interest != 1, therm)
plt.figure(figsize=(10,5))
plt.subplot(1,2,1)
plt.imshow(therm)
plt.subplot(1,2,2)
plt.imshow(therm_masked)
plt.show(block='TRUE')
