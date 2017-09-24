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

  def bgr_thresh(self, img, above_bgr, below_bgr):
    matched = ((   img[:,:,0] > above_bgr[0])  \
                & (img[:,:,0] <= below_bgr[0]) \
                & (img[:,:,1] > above_bgr[1])  \
                & (img[:,:,1] <= below_bgr[1]) \
                & (img[:,:,2] > above_bgr[2])  \
                & (img[:,:,2] <= below_bgr[2]))
    return matched

  def deblue(self, img):
    img[:,:,1] = img[:,:,1]*0.4
    img[:,:,0] = img[:,:,0]*0.3
    return img

  # Processes an image to detect buoys in it
  def process_image(self, img):

    # Resize any input image to the size our algorithm
    # wants to process
    img = cv2.resize(img, self.image_dimensions)

    img_deblue = self.deblue(img.copy())
    matched_red = self.bgr_thresh(img_deblue, [0,0,200],[100,100,255])
    matched_white = self.bgr_thresh(img, [180,180,160],[255,255,255])

    # We want things that are RED in deblue, but not BRIGHT WHITE in origional
    matched = matched_red & numpy.invert(matched_white)

    img_match = img.copy()
    img_match[matched] = 255
    img_match[numpy.invert(matched)] = 0
    img_match = cv2.cvtColor(img_match, cv2.COLOR_BGR2GRAY)

    im2, contours, hierarchy = cv2.findContours(img_match,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    largest_cont = None
    largest_area = 0
    for cont in contours:
      area = cv2.contourArea(cont, False)
      if area > largest_area:
        largest_area = area
        largest_cont = cont

    buoy_detection = None

    if largest_cont is not None:

      #cv2.drawContours(img, [largest_cont], -1, (0,255,0), 3)

      bounding_rect = cv2.boundingRect(largest_cont) # x, y, w, h
      rad = int(bounding_rect[2]/2)
      pos = (int(bounding_rect[0]+bounding_rect[2]/2), int(bounding_rect[1]+bounding_rect[3]/2))

      buoy_detection = {"pos":pos, "rad":rad}

      cv2.circle(img, pos, rad, (55, 55, 150), 2)
      cv2.circle(img, pos, rad, (200, 200, 250), 1)

    if buoy_detection is not None:
      self.meta.append({"RedBuoy":buoy_detection})
    else:
      self.meta.append({})

    #img[numpy.invert(matched)] = img[numpy.invert(matched)]/4

    # Show the processed image for debugging
    return img





