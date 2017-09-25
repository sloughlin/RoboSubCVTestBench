#!/usr/bin/python2.7

import cv2
import numpy

class CVModule:

  image_dimensions = (480, 360)

  def __init__(self, args):
    self.meta = []

  def get_meta(self):
    return self.meta

  def output_dimensions(self):
    return self.image_dimensions

  def thresh(self, img, above, below):
    matched = ((   img[:,:,0] > above[0])  \
                & (img[:,:,0] <= below[0]) \
                & (img[:,:,1] > above[1])  \
                & (img[:,:,1] <= below[1]) \
                & (img[:,:,2] > above[2])  \
                & (img[:,:,2] <= below[2])) 
    return matched

  def sphr_thresh(self, img, center):
    #(b-0)^2 + (g-255)^2 + (r-255)^2 < (255/2)^2
    img = img.astype(float)
    return (2.0*(img[:,:,0])**2 + 0.25*(img[:,:,1]-255.0)**2 + 0.25*(img[:,:,2]-255.0)**2) < ((255.0/2.0)**2)

  def deblue(self, img):
    img[:,:,1] = img[:,:,1]*0.8
    img[:,:,0] = img[:,:,0]*0.6
    return img

  # Processes an image to detect buoys in it
  def process_image(self, img):

    # Resize any input image to the size our algorithm
    # wants to process
    img = cv2.resize(img, self.image_dimensions)

    img_deblue = self.deblue(img.copy())
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img_edges = cv2.Canny(img, 25, 200, apertureSize=3)
    matched_yellow = self.thresh(img_hsv, [40,80,150],[70,130,200])
    #matched_yellow = self.sphr_thresh(img_deblue, [0,255,255])
    #matched_white = self.thresh(img, [180,180,160],[255,255,255])

    #img[numpy.invert(matched_yellow)] = img[numpy.invert(matched_yellow)]/4

    img_match = img.copy()
    img_match[matched_yellow] = 255
    img_match[numpy.invert(matched_yellow)] = 0
    img_match = cv2.cvtColor(img_match, cv2.COLOR_BGR2GRAY)

    #im2, contours, hierarchy = cv2.findContours(img_match,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    #cv2.drawContours(img, contours, -1, (0,255,0), 3)

    lines = cv2.HoughLinesP(img_edges,1,numpy.pi/180,100,50,10)
    if lines is not None:
      for x1,y1,x2,y2 in lines[0]:
        cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)

    # Show the processed image for debugging
    return img





