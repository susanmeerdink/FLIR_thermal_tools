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

rgb_class, rgbqcolor = u.classify_rgb(rgb_crop, 6)

plt.show(block='TRUE') 

# Displaying Results with classes
fig, ax = plt.subplots(figsize=(10,10))
cmap = colors.ListedColormap(['blue','green','orange','red','black','yellow'])
im = ax.imshow(rgb_class, cmap=cmap)
cbar = fig.colorbar(im, ax=ax, shrink = 0.6, ticks=[0.5, 1.25, 2, 2.75, 3.5, 4.5]) #0.8,1.6,2.4,3.2,3.6
cbar.ax.set_yticklabels(['1','2','3','4','5','6']) 
cbar.ax.set_ylabel('Classes')
plt.show(block='TRUE')

# Mask the rgb image to improve kmeans class?
rgb_masked = u.mask_kmeans_classimg(rgb_crop, rgb_class, maskclass=[1,2,3,4,5])

plt.figure(figsize=(10,10))
plt.imshow(rgb_masked)
plt.show(block='TRUE')

# %% 
rgbmask_class, rgbqcolor = u.classify_rgb(rgb_masked, 4)


