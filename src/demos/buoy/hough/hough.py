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

    edges = cv2.Canny(img, 100, 200)
    im_out = edges
    im_out = cv2.GaussianBlur(im_out, (5, 5), 0)
    circles = cv2.HoughCircles(im_out, cv2.HOUGH_GRADIENT, 2, 32.0)
    # Potential additional tuning parameters:
    #, param1=50, param2=30, minRadius=0, maxRadius=0)

    # Draw the HoughCircle we detected to the debug image
    if circles is not None:
      circles = numpy.uint16(numpy.around(circles))
      for i in circles[0,:]:
        cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
        cv2.circle(img,(i[0],i[1]),2,(0,0,255),3)

    # Show the processed image for debugging
    return img





