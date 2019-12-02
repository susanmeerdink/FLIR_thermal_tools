# FLIR-Temp_Retrieval
Code that processes FLIR imagery.

## Dependencies
flirimageextractor:   
	https://pypi.org/project/flirimageextractor/     
	https://flirimageextractor.readthedocs.io/en/latest/flirimageextractor.html
exiftools:   
	Depending on where exiftools is installed you may have to change the exiftools path for flirimageextractor. An example of this is in the demo. 


## Functionality I want:
Convert FLIR temperature imagery into csv (need to check that it is the same temperature returned as FLIR software)
	Completed - the temperatures don't EXACTLY match, but are some where between 0.001 to 0.006 degrees celisus difference.
Convert FLIR RGB imagery into png - both full resolution and resolution that matches temperature image
	Completed 
Match FLIR temperature and RGB imagery 
	Completed
Classify RGB imagery into groups for emissivity assignments 
Correct FLIR temperature with new emissivity values
Grab FLIR temperature for a specific class 

## Manually Determing RGB and Temperature Image Offset
This uses the function manual_img_registration to determine tie points between thermal and rgb images. It will be used to determine how much the RGB image should be shifted to match the same distribution of the thermal image. This function pulls up an image with the thermal image on the left and the rgb image on the right. It depends on the matplotlib built in buttons: https://matplotlib.org/3.1.1/users/navigation_toolbar.html. I would select at least three tie point locations. The average x and y offset will be calculated from these points. 
Important things to note:
* You MUST select the thermal point first THEN the RGB point.
* ANY TIME you click (even with zoom and pan) you add a point. Make sure to right click after zooming or panning to remove that point. 
* The back arrow is nice to get back to the full screen image, then you don't risk accident points using pan feature.  