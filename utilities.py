# Importing Functions
import flirimageextractor
from matplotlib import pyplot as plt
from matplotlib import colors
import numpy as np
import subprocess
import cv2
import glob
import matplotlib
matplotlib.use('TKAgg') # Needed to have figures display properly. 

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

def extract_coarse_image(flirobj, offset=[0], plot=1):
    """
    Function that creates the coarse RGB image that matches the resolution of the thermal image.
    
    INPUTS:
        1) flirobj: the flirimageextractor object.
        2) offset: optional variable that shifts the RGB image to match the same field of view as thermal image. 
                If not provided the offset values will be extracted from FLIR file. 
                Use the manual_img_registration function to determine offset.
        3) plot: a flag that determine if a figure of thermal and coarse cropped RGB is displayed. 
                1 = plot displayed, 0 = no plot is displayed
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
    
    if plot == 1:
        therm = flirobj.get_thermal_np()
        plt.figure(figsize=(10,5))
        plt.subplot(1,2,1)
        plt.imshow(therm, cmap='jet')
        plt.title('Thermal Image')
        plt.subplot(1,2,2)
        plt.imshow(crop)
        plt.title('RGB Cropped Image')
        plt.show(block='TRUE') 
        
    return lowres, crop

def manual_img_registration(flirobj):
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
        1) flirobj: the flirimageextractor object.
    OUTPUTS:
        1) offset: a numpy array with [x pixel offset, y pixel offset] between thermal and rgb image
        2) pts_therm: a numpy array containing the image registration points for the thermal image. 
        3) pts_rgb: a numpy array containing the coordinates of RGB image matching the thermal image.
    """
    # Getting Images
    therm = flirobj.get_thermal_np()
    rgb, junk = extract_coarse_image(flirobj)
    
    # Plot Images
    fig = plt.figure(figsize=(10,5))
    ax1 = fig.add_subplot(1,2,1)
    ax1.imshow(therm, cmap='jet')
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

def classify_rgb(img, K=3, plot=1):
    """
    This classifies an RGB image using K-Means clustering.
    Note: only 10 colors are specified, so will have plotting error with K > 10
    INPUTS:
        1) img: a 3D numpy array of rgb image
        2) K: optional, the number of K-Means Clusters
        3) plot: a flag that determine if multiple figures of classified is displayed. 
                1 = plot displayed, 0 = no plot is displayed
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

    if plot == 1:
        # Plotting Results
        coloroptions = ['b','g','r','c','m','y','k','orange','navy','gray']
        fig = plt.figure(figsize=(10,5))
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
        fig, ax = plt.subplots(figsize=(5,5))
        im = ax.imshow(label_image, cmap=cmap)
        cbar = fig.colorbar(im, ax=ax, shrink = 0.6, ticks=np.arange(0,K)) 
        cbar.ax.set_yticklabels(ticklabels[0:K]) 
        cbar.ax.set_ylabel('Classes')
        plt.show(block='TRUE')

    return label_image, result_image

def apply_mask_to_rgb(mask, rgbimg, plot=1):
    """
    Function that applies mask to provided RGB image and returns RGB image with 
    only pixels where mask is 1 and all other pixels are black. This function
    is useful to use BEFORE K-Means classification. 
    INPUTS:
        1) mask: a numpy binary mask that same shape as rgbimg variable. 
                0's are pixels NOT of interest and will be masked out.
                1's are pixels of interest and will be returned.
        2) rgbimg: a 3D numpy array that contains RGB image.
        3) plot: a flag that determine if a figure of masked image is displayed. 
                1 = plot displayed, 0 = no plot is displayed
    OUTPUTS:
        1) masked_rgb: a 3D numpy array that contains RGB image with all pixels 
                designated as 0 in the mask are black. 
    """         
    masked_rgb = np.zeros((rgbimg.shape[0], rgbimg.shape[1], rgbimg.shape[2]),int)
    for d in range(0,rgbimg.shape[2]):
        masked_rgb[:,:,d] = rgbimg[:,:,d] * mask 
    
    if plot == 1:
        plt.figure(figsize=(10,5))
        plt.subplot(1,2,1)
        plt.imshow(rgbimg)
        plt.title('Original Image')
        plt.subplot(1,2,2)
        plt.imshow(masked_rgb)
        plt.title('Masked Image')
        plt.show(block='TRUE')
        
    return masked_rgb

def create_class_mask(classimg, classinterest, plot=1):
    """
    This function creates a mask that turns all K-Means classes NOT of interest 
    as 0 and all classes of interest to 1. This can be used to extract temperatures
    only for classes of interest. 
    INPUTS:
        1) classinterest: a array containing the class or classes of interest. 
                All other classes will be masked out
        2) classimg: the K-Means class image which is (2D) numpy array
        3) plot: a flag that determine if a figure of masked K-Means class image is displayed. 
                1 = plot displayed, 0 = no plot is displayed
    OUTPUTS:
        1) mask: a 2D numpy binary mask that same shape as the first two dimensions of rgbimg variable. 
                0's are pixels NOT of interest and will be masked out.
                1's are pixels of interest and will be returned.
    """
    mask = np.zeros((classimg.shape[0], classimg.shape[1]))
    if isinstance(classinterest,int):
        endrange = 1
    else:
        endrange = len(classinterest)
    
    for c in range(0,endrange):
        idx_x, idx_y = np.where(classimg == c)
        mask[idx_x, idx_y] = 1
    
    if plot == 1:
        plt.figure(figsize=(10,5))
        plt.subplot(1,2,1)
        plt.imshow(classimg)
        plt.title('Original K-Means Classes')
        plt.subplot(1,2,2)
        plt.imshow(mask, cmap='gray')
        plt.title('Masked Classes')
        plt.show(block='TRUE')
    
    return mask

def extract_temp_for_class(flirobj, mask, plot=1):
    """
    This function creates a numpy array thermal image that ONLY contains pixels for class
    of interest with all other pixels set to 0. This is for a SINGLE image
    INPUTS:
        1) flirobj: the flirimageextractor object
        2) mask: a binary mask with class pixels set as 1. 
        3) plot: a flag that determine if a figure of tempeature image is displayed. 
                1 = plot displayed, 0 = no plot is displayed
    OUTPUTS:
        1) therm_masked: a 2D numpy array of temperature values for a class of interest
    """       
    therm = flirobj.get_thermal_np()
#    therm_masked = np.copy(therm)
#    idx_x, idx_y = np.where(mask == 0)
#    therm_masked[idx_x,idx_y] = 0
    therm_masked = np.ma.masked_where(mask != 1, therm)
    
    if plot == 1:
        plt.figure(figsize=(10,5))
        plt.subplot(1,2,1)
        plt.imshow(therm, cmap='jet')
        plt.subplot(1,2,2)
        plt.imshow(therm_masked, cmap='jet')
        plt.show(block='TRUE')
        
    return therm_masked

def batch_extract_temp_for_class(dirLoc, mask, exiftoolpath=''):
    """
    This function creates a 3D numpy array thermal image that ONLY contains pixels for class
    of interest with all other pixels set to 0. This is for a directory of images.
    INPUTS:
        1) dirLoc: a string containing the directory of FLIR images.
        2) mask: a binary mask with class pixels set as 1. 
        3) exiftoolpath = OPTIONAL a string containing the location of exiftools.
                Only use if the exiftool path is different than the python path.
    OUTPUTS:
        1) all_temp: a 3D numpy array of temperature values for a class of interest
                The first two dimensions will match the dimensions of a single temperature image.
                The third dimension size will match the number of files in directory.
    """  
    filelist = glob.glob(dirLoc + '*')
    print('Found ' + str(len(filelist)) + ' files.')
    all_temp = np.ma.empty((mask.shape[0], mask.shape[1], len(filelist)))
    
    for f in range(0,len(filelist)):
        # Get individual file
        if not exiftoolpath:
            flir = flirimageextractor.FlirImageExtractor()
        else:
            flir = flirimageextractor.FlirImageExtractor(exiftool_path=exiftoolpath)

        flir.process_image(filelist[f], RGB=True)
        
        all_temp[:,:,f] = extract_temp_for_class(flir, mask, plot=0)
        
    return all_temp

def plot_temp_timeseries(temp):
    """
    Function that plots the mean, min, and max temperature for a temperature timeseries.
    INPUTS:
        1) temp: a 3D numpy array of temperature values for a class of interest
                The first two dimensions will match the dimensions of a single temperature image.
                The third dimension size will match the number of files in directory. 
    OUTPUTS:
        figure of mean, min, and maximum temperature across timeseries
    """
    # Setting up Variables
    minmaxtemp = np.zeros((2,temp.shape[2]))
    meantemp = np.zeros(temp.shape[2])
    
    # Loop through time steps
    for d in range(0, temp.shape[2]):
        minmaxtemp[0,d] = np.nanmin(temp[:,:,d])
        meantemp[d] = np.nanmean(temp[:,:,d])
        minmaxtemp[1,d] = np.nanmax(temp[:,:,d])
    
    difftemp = abs(minmaxtemp - meantemp)
    plt.figure(figsize=(10,7))
    plt.errorbar(np.arange(1, temp.shape[2]+1), meantemp, yerr=difftemp, linewidth=2, color='black')
    plt.gca().yaxis.grid(True)
    plt.title('Temperature through Timeseries')
    plt.xlabel('Time Steps')
    plt.ylabel('Temperature (Celsius))')
    plt.show(block='true')
    
def develop_correct_emissivity(class_img):
    """
    The thermal camera has an assume emissivity of 0.95, but many materials do 
    not have that emissivity which changes the temperature retrieved. This code
    assigned the appropriate emissivity value for a pixel (user provided) 
    using the K-Means classes.
    INPUTS:
        1) class_img: the K-Means class image
    OUTPUTS:
        1) emiss_img: a numpy array with same dimensions as K-Means class image,
                but every pixel has an emissivity value.
    """
    K = np.unique(class_img)
    
    # Plotting just K-Means with label
    coloroptions = ['b','g','r','c','m','y','k','orange','navy','gray']
    ticklabels = ['1','2','3','4','5','6','7','8','9','10']
    fig, ax = plt.subplots(figsize=(5,5))
    cmap = colors.ListedColormap(coloroptions[0:K])
    im = ax.imshow(class_img, cmap=cmap)
    cbar = fig.colorbar(im, ax=ax, shrink = 0.6, ticks=np.arange(0,K)) 
    cbar.ax.set_yticklabels(ticklabels[0:K]) 
    cbar.ax.set_ylabel('Classes')
    plt.show(block='TRUE')
    
    print('Input the emissivity for each class. If unknown put 0.95')
    emiss = np.zeros((K.shape[0]))
    for c in range(0,K):
        strout = 'Class ' + str(c) + 'Emissivity: '
        emiss[c] = input(strout)
        
    emiss_img = np.zeros((class_img.shape[0], class_img.shape[1]))    
    for e in range(0, K):
        idx_x, idx_y = np.where(class_img == e)
        emiss_img[idx_x, idx_y] = emiss[e]
        
    return emiss_img
    