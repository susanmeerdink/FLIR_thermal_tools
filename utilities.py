# Importing Functions
import flirimageextractor
from matplotlib import pyplot as plt
from matplotlib import colors
import numpy as np
import subprocess
import cv2
import matplotlib
matplotlib.use('TKAgg') # Needed to have figures display properly. 
import numpy.ma as ma 

def save_thermal_csv(flirobj, filename):
    """
    Function that saves the numpy array as a .csv
    
    INPUTS:
    1) flirobj: the flirimageextractor object.
    2) filename: a string containing the location of the output csv file. 
    
    OUTPUTS:
    Saves a csv of the thermal image where each value is a pixel in the thermal image. 
    """
    data = flirobj.get_thermal_np()
    np.savetxt(filename, data, delimiter=',')

def extract_coarse_image(flirobj, offset=[0]):
    """
    Function that creates the coarse RGB image that matches the resolution of the thermal image.
    
    INPUTS:
        1) flirobj: the flirimageextractor object.
        2) offset: optional variable that shifts the RGB image to match the same field of view as thermal image. 
                If not provided the offset values will be extracted from FLIR file. 
                Use the manual_img_registration function to determine offset.
    OUTPUTS:
        1) lowres: a 3D numpy array of RGB image that matches resolution of thermal image (It has not been cropped) 
        2) crop: a 3D numpy arary of RGB image that matches resolution and field of view of thermal image.
    """
    # Get RGB Image
    visual = flirobj.rgb_image_np
    highres_ht = visual.shape[0]
    highres_wd = visual.shape[1]
    
    # Getting Values for Offset
    if len(offset) < 2:
        offsetx = int(subprocess.check_output([flirobj.exiftool_path, "-OffsetX", "-b", flirobj.flir_img_filename])) 
        offsety = int(subprocess.check_output([flirobj.exiftool_path, "-OffsetY", "-b", flirobj.flir_img_filename])) 
    else:
        offsetx = offset[0]
        offsety = offset[1]
    pipx2 = int(subprocess.check_output([flirobj.exiftool_path, "-PiPX2", "-b", flirobj.flir_img_filename])) # Width
    pipy2 = int(subprocess.check_output([flirobj.exiftool_path, "-PiPY2", "-b", flirobj.flir_img_filename])) # Height
    real2ir = float(subprocess.check_output([flirobj.exiftool_path, "-Real2IR", "-b", flirobj.flir_img_filename])) # conversion of RGB to Temp
    
    # Set up Arrays
    height_range = np.arange(0,highres_ht,real2ir).astype(int)
    width_range = np.arange(0,highres_wd,real2ir).astype(int)
    htv, wdv = np.meshgrid(height_range,width_range)
    
    # Assigning low resolution data
    lowres = np.swapaxes(visual[htv, wdv,  :], 0, 1)
    
    # Cropping low resolution data
    height_range = np.arange(-offsety,-offsety+pipy2).astype(int)
    width_range = np.arange(-offsetx,-offsetx+pipx2).astype(int)
    xv, yv = np.meshgrid(height_range,width_range)
    crop = np.swapaxes(lowres[xv, yv, :],0,1)
    
    return lowres, crop

def manual_img_registration(filename):
    """
    Function that displays the thermal and RGB image so that similar locations 
    can be selected in both images. It is recommended that at least three tied-points
    are collected. Using the tie points the average x and y pixel offset will be determined.
    
    HOW TO:
    Left click adds points, right click removes points (necessary after a pan or zoom),
    and middle click stops point collection. 
    The keyboard can also be used to select points in case your mouse does not have one or 
    more of the buttons. The delete and backspace keys act like right clicking 
    (i.e., remove last point), the enter key terminates input and any other key 
    (not already used by the window manager) selects a point. 
    ESC will delete all points - do not use. 
    
    INPUTS:
        1) filename: a string with the thermal image location. 
    OUTPUTS:
        1) offset: a numpy array with [x pixel offset, y pixel offset] between thermal and rgb image
        2) pts_therm: a numpy array containing the image registration points for the thermal image. 
        3) pts_rgb: a numpy array containing the coordinates of RGB image matching the thermal image.
    """
    # Getting Images
    flir = flirimageextractor.FlirImageExtractor(exiftool_path="C:\\Users\\susanmeerdink\\.utilities\\exiftool.exe")
    flir.process_image(filename, RGB=True)
    therm = flir.get_thermal_np()
    rgb, junk = extract_coarse_image(flir)
    
    # Plot Images
    fig = plt.figure(figsize=(10,5))
    ax1 = fig.add_subplot(1,2,1)
    ax1.imshow(therm)
    ax1.set_title('Thermal')
    ax1.text(0,-100,'Collect points matching features between images. Select location on thermal then RGB image.')
    ax1.text(0,-75,'Right click adds a point. Left click removes most recently added point. Middle click (or enter) stops point collection.')
    ax1.text(0,-50,'Zoom/Pan add a point, but you can remove with left click. Or use back arrow to get back to original view.')
    ax2 = fig.add_subplot(1,2,2)
    ax2.imshow(rgb)
    ax2.set_title('RGB')
    fig.subplots_adjust(left=0.05, top = 0.8, bottom=0.01,right=0.95)
    
    # Getting points
    pts = np.asarray(fig.ginput(-1, timeout=-1))    
    idx_therm = np.arange(0,pts.shape[0],2)
    pts_therm = pts[idx_therm,:]
    idx_rgb = np.arange(1,pts.shape[0],2)
    pts_rgb = pts[idx_rgb,:]
    
    # Getting Difference between images to determine offset
    size_therm = pts_therm.shape[0]
    size_rgb = pts_rgb.shape[0]
    offset = [0,0]
    if size_therm == size_rgb:
        pts_diff = pts_therm - pts_rgb  
        offset = np.around(np.mean(pts_diff, axis=0))
    else:
        print('Number of points do not match between images')
        
    plt.close()
    return offset, pts_therm, pts_rgb

def classify_rgb(img, K=3):
    """
    This classifies an RGB image using K-Means clustering.
    Note: only 10 colors are specified, so will have plotting error with K > 10
    INPUTS:
        1) img: a 3D numpy array of rgb image
        2) K: optional, the number of K-Means Clusters
    OUTPUTS:
        1) label_image: a 2D numpy array the same x an y dimensions as input rgb image, 
            but each pixel is a k-means class.
        2) result_image: a 3D numpy array the same dimensions as input rgb image, 
            but having undergone Color Quantization which is the process of 
            reducing number of colors in an image.
    """
    # Preparing RGB Image
    vectorized = img.reshape((-1,3))
    vectorized = np.float32(vectorized)
    
    # K-Means
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    attempts = 10
    ret,label,center=cv2.kmeans(vectorized,K,None,criteria,attempts,cv2.KMEANS_RANDOM_CENTERS)
    
    # Use if you want to have quantized imaged
    center = np.uint8(center)
    res = center[label.flatten()]
    result_image = res.reshape((img.shape))
    
    # Labeled class image
    label_image = label.reshape((img.shape[0], img.shape[1]))

    # Plotting Results
    coloroptions = ['b','g','r','c','m','y','k','orange','navy','gray']
    fig = plt.figure(figsize=(15,10))
    ax1 = fig.add_subplot(1,2,1)
    ax1.imshow(img)
    ax1.set_title('Original Image') 
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax2 = fig.add_subplot(1,2,2)
    cmap = colors.ListedColormap(coloroptions[0:K])
    ax2.imshow(label_image, cmap=cmap)
    ax2.set_title('K-Means Classes') 
    ax2.set_xticks([]) 
    ax2.set_yticks([])
    fig.subplots_adjust(left=0.05, top = 0.8, bottom=0.01, wspace=0.05)
    plt.show(block='TRUE')
    
    # Plotting just K-Means with label
    ticklabels = ['1','2','3','4','5','6','7','8','9','10']
    fig, ax = plt.subplots(figsize=(10,10))
    im = ax.imshow(label_image, cmap=cmap)
    cbar = fig.colorbar(im, ax=ax, shrink = 0.6, ticks=np.arange(0,K)) 
    cbar.ax.set_yticklabels(ticklabels[0:K]) 
    cbar.ax.set_ylabel('Classes')
    plt.show(block='TRUE')

    return label_image, result_image
        