## **このレポジトリの動かし方や内容は[こちらのブログ](https://kentapt.hatenablog.com/entry/2022/10/16/152920)にも書かれています。よろしければぜひご覧ください**

# FLIR Thermal Tools
This repository of code processes temperature imagery collected using FLIR cameras (http://flir.com/). Some of the capabilities include:  
  * extracting temperature information as .csv file
  * retrieving RGB imagery associated with thermal imagery
  * correct offset between RGB and thermal imagery 
  * Classify RGB in order to separate image materials
  * Use co-aligned RGB to pull out class's pixels
Note: this may not work for all FLIR cameras and is specifically designed for cameras that have an RGB camera. 

## Dependencies
This repository requires multiple packages to process the imagery including:  
flirimageextractor:   
  * https://pypi.org/project/flirimageextractor/     
  * https://flirimageextractor.readthedocs.io/en/latest/flirimageextractor.html  

exiftools: 
  * https://github.com/exiftool/exiftool  
  * Depending on where exiftools is installed you may have to change the exiftools path for flirimageextractor. An example of this is in the demo.py file. 

## Functions:
These are functions that are included in this repository. The python package flirimageextractor also has a lot of built in functions that users maybe interested in.
  * save_thermal_csv: Extracts the temperature data and exports it as a .csv. A comparison between temperature retrieval using FLIR Tools and this code shows a 0.001 to 0.006 degrees celsius difference.
  * extract_coarse_image: The FLIR imagery contains a high spatial resolution and large field of view RGB imagery. This function scales and crops RGB imagery to match the thermal imagery. If a manual offset value is not provided it will crop the image based on offset values contained in header file. 
  * manual_img_registration: This function helps users determine the manual offset between rgb and thermal imagery. See section below on more details on this function. 
  * classify_rgb: This function classifies the RGB imagery using K-Means to determine the materials in the images. Tip: mask out areas that are not of interest to improve classification. 
  * extract_temp_for_class: This function extracts temperature values for pixels of interest. This is for a single image
  * batch_extract_temp_for_class: This function extracts temperature values for pixels of interest. This is a directory of images. 
  * create_class_mask: This function creates a mask of K-Means classes of interest
  * apply_mask_to_rgb: This function applies the K-Means class mask to the RGB imagery
  * develop_correct_emissivity: This function takes user input and defines the appropriate emissivity for each K-Means class. See section below about assigning emissivities.
  * correct_temp_emiss: This function takes the correct emissivity and runs temperature correction
  * plot_temp_timeseries: this function displays the timeseries data with mean, min, and max temperature.

## Suggested Work Order
This order assumes you have a thermal timeseries where the camera does not move between image collections.
1. Load in first FLIR image of the timeseries. 
2. Examine thermal and full resolution RGB images to ensure everything is correct.
3. Check how well thermal and RGB image registration is without manually correction. If registration is not ideal complete the following steps:  
     1. Determine manual correction of thermal and RGB image registration.  
     2. Apply manually determine x and y offset to the RGB imagery.
4. Build a mask that turns all pixels NOT of interest into zeros. 
5. Classify masked RGB image using K-Means. Determine which class number is of interest.
6. Create mask where all class of interest pixels are 1 while other pixels are 0. 
7. (OPTIONAL) Determine and assign appropriate emissivities to each of the K-Means classes.
8. Using mask, extract pixels from thermal imagery that are only your class of interest. If correct emissivities were developed in step 6, temperature imagery will be corrected. 

## Manually Determing RGB and Temperature Image Offset:
Often, the RGB and Thermal camera lens do not line up accurately. It is possible to change this in the settings, but because the RGB imagery has a larger field of view and is higher resolution the offset between lens can be corrected afterwards. Using the function called manual_img_registration a user can determine tie points between thermal and rgb images used to correct the alignment. The function returns an x and y offset that can be used to determine how much the RGB image should be shifted to match the same distribution of the thermal image. This function pulls up an image with the thermal image on the left and the rgb image on the right. It depends on the matplotlib built in buttons: https://matplotlib.org/3.1.1/users/navigation_toolbar.html. I suggest selecting at a minimum three tie point locations. The average x and y offset will be calculated from these points.   
Important things to note:
  * You MUST select the thermal point first THEN the RGB point.
  * ANY TIME you click (even with zoom and pan) you add a point. Make sure to right click after zooming or panning to remove that point. 
  * The back arrow is nice to get back to the full screen image, then you don't risk accident points using pan feature.  
  
## Correcting Temperature for Appropriate Emissivity 
The FLIR cameras use an assume emissivity of 0.95 (can be changed in settings). However, many materials do not have that emissivity of 0.95. Differences in emissivity changes the temperature retrieved for a pixel. Using the RGB image classified through K-Means, we can assign an emissivity that is more appropriate for a material and correct the temperature. All corrections are done using the stefan-boltzman equation. There are tables available online with materials broadband emissivities. Vegetation is generally 0.98, while white paper is generally 0.86.  
