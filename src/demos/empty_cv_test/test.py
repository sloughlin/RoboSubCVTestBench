#!/usr/bin/python2.7

import cv2
import numpy

class CVModule:

  image_dimensions = (480, 360)

  def __init__(self, args):
    pass

  def output_dimensions(self):
    return self.image_dimensions

  # Processes an image to detect buoys in it
  def process_image(self, img):

    # Resize any input image to the size our algorithm
    # wants to process
    img = cv2.resize(img, self.image_dimensions)

    #### CV CODE HERE
    above_bgr_thresh = [0,0,200]
    below_bgr_thresh = [150,150,255]
    matched = ((   img[:,:,0] > above_bgr_thresh[0])  \
                & (img[:,:,0] <= below_bgr_thresh[0]) \
                & (img[:,:,1] > above_bgr_thresh[1])  \
                & (img[:,:,1] <= below_bgr_thresh[1]) \
                & (img[:,:,2] > above_bgr_thresh[2])  \
                & (img[:,:,2] <= below_bgr_thresh[2]))
    img[numpy.invert(matched)] = img[numpy.invert(matched)]/4

    # Show the processed image for debugging
    return img





