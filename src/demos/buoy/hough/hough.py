#!/usr/bin/python2.7

import cv2
import numpy

class CVModule:

  image_dimensions = (480, 360)

  def __init__(self, args):
    self.meta = []

  def output_dimensions(self):
    return self.image_dimensions

  def get_meta(self):
    return self.meta

  # Processes an image to detect buoys in it
  def process_image(self, img):

    # Resize any input image to the size our algorithm
    # wants to process
    img = cv2.resize(img, self.image_dimensions)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    im_out = cv2.GaussianBlur(img, (5, 5), 0)
    circles = cv2.HoughCircles(im_out, cv2.HOUGH_GRADIENT, dp=1, minDist=im_out.shape[0]/4, param1=50.0, param2=25.0, minRadius=im_out.shape[0]/16, maxRadius=0)
    # Potential additional tuning parameters:
    #, param1=50, param2=30, minRadius=0, maxRadius=0)

    # Draw the HoughCircle we detected to the debug image
    buoy_detection = None
    if circles is not None:
      circles = numpy.uint16(numpy.around(circles))
      for i in circles[0,:]:
        cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
        cv2.circle(img,(i[0],i[1]),2,(0,0,255),3)
        buoy_detection = {"pos":(int(i[0]), int(i[1])), "rad":int(i[2]/2)}
    if buoy_detection is not None:
      self.meta.append({"RedBuoy":buoy_detection})
    else:
      self.meta.append({})

    # Show the processed image for debugging
    return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)





