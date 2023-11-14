# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 12:57:38 2023

@author: Olivier-Rukundo
"""

import os   # OR added this to find the openslide DLL file
os.add_dll_directory(r'C:\Users\Olivier-Rukundo\Desktop\RUKUNDO\FFGPROJECT\AUTOPATHSTAGEDATA\MoNuSAC\openslide-win64-20231011\openslide-win64-20231011\bin')

#Process whole slide images
# import os
import openslide
# from xml.dom import minidom
import numpy as np
# import openslide
# from openslide import open_slide  
from glob import glob
import cv2
# import matplotlib.pyplot as plt
# import scipy.io as sio
# from PIL import Image
# import scipy
# import scipy.ndimage
from shapely.geometry import Polygon
from skimage import draw
import xml.etree.ElementTree as ET

# Read svs files from the desired path
count = 0
data_path = r'C:\Users\Olivier-Rukundo\Desktop\RUKUNDO\FFGPROJECT\AUTOPATHSTAGEDATA\MoNuSAC\TestingData\MoNuSAC Testing Data and Annotations' #Path to read data from
destination_path = r'C:\Users\Olivier-Rukundo\Desktop\RUKUNDO\FFGPROJECT\AUTOPATHSTAGEDATA\MoNuSAC\BinaryMaskTestData' # Path to save binary masks corresponding to xml files
os.chdir(destination_path)

try:
    os.mkdir(destination_path+'\MoNuSAC_masks')
except OSError:
    print ("Creation of the mask directory %s failed" % destination_path)
    
os.chdir(destination_path+'\MoNuSAC_masks')#Create folder named as MoNuSAC_masks
patients = [x[0] for x in os.walk(data_path)]#Total patients in the data_path
len(patients)

for patient_loc in patients:
    patient_name = patient_loc[len(data_path)+1:]#Patient name
    print(patient_name)
    
    ## To make patient's name directory in the destination folder
    try:
        os.mkdir(patient_name)
    except OSError:
        print ("\n Creation of the patient's directory %s failed" % patient_name)
        
    ## Read sub-images of each patient in the data path        
    sub_images = glob(patient_loc+'/*.svs')
    for sub_image_loc in sub_images:
        sub_image_name = sub_image_loc[len(data_path)+len(patient_name)+1:-4]        
        print(sub_image_name)
        
        ## To make sub_image directory under the patient's folder
        sub_image = './'+patient_name+'/'+sub_image_name #Destination path
        try:
            os.mkdir(sub_image)
        except OSError:
            print ("\n Creation of the patient's directory %s failed" % sub_image)
            
        image_name = sub_image_loc
        img = openslide.OpenSlide(image_name)
                                  
        # If svs image needs to save in tif
        cv2.imwrite(sub_image_loc[:-4]+'.png', np.array(img.read_region((0,0),0,img.level_dimensions[0])))      
   
        # Read xml file
        xml_file_name  = image_name[:-4]
        xml_file_name = xml_file_name+'.xml'
        tree = ET.parse(xml_file_name)
        root = tree.getroot()
        
        #Generate binary mask for each cell-type                         
        for k in range(len(root)):
            label = [x.attrib['Name'] for x in root[k][0]]
            label = label[0]
            
            for child in root[k]:
                for x in child:
                    r = x.tag
                    if r == 'Attribute':
                        count = count+1
                        print(count)
                        label = x.attrib['Name']
                        binary_mask = np.transpose(np.zeros((img.read_region((0,0),0,img.level_dimensions[0]).size))) 
                        print(label)
                        
                        # Create directory for each label
                        sub_path = sub_image+'/'+label
                        
                        try:
                            os.mkdir(sub_path)
                        except OSError:
                            print ("Creation of the directory %s failed" % label)
                        else:
                            print ("Successfully created the directory %s " % label) 
                                          
                        
                    if r == 'Region':
                        regions = []
                        vertices = x[1]
                        coords = np.zeros((len(vertices), 2))
                        for i, vertex in enumerate(vertices):
                            coords[i][0] = vertex.attrib['X']
                            coords[i][1] = vertex.attrib['Y']        
                        regions.append(coords)
                        # poly = Polygon(regions[0])  
                        
                        if len(regions[0]) >= 4:       # OR added this condition to check if there are fewer than 4 coordinates or else to print a skipping message
                           poly = Polygon(regions[0]) 
                        
                           vertex_row_coords = regions[0][:,0]
                           vertex_col_coords = regions[0][:,1]
                           fill_row_coords, fill_col_coords = draw.polygon(vertex_col_coords, vertex_row_coords, binary_mask.shape)
                           binary_mask[fill_row_coords, fill_col_coords] = 255
                           mask_path = sub_path+'/'+str(count)+'_mask.png'
                           cv2.imwrite(mask_path, binary_mask) 
                        
                        else:
                           print("Skipping creation of Polygon. Insufficient coordinates.")