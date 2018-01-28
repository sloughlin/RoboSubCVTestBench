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

  def angle_cos(self, p0, p1, p2):
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( numpy.dot(d1, d2) / numpy.sqrt( numpy.dot(d1, d1)*numpy.dot(d2, d2) ) )
  
  def find_squares(self, img):
    img = cv2.GaussianBlur(img, (5, 5), 0)
    squares = []
    for gray in cv2.split(img):
      for thrs in xrange(0, 255, 26):
        if thrs == 0:
          bin = cv2.Canny(gray, 0, 50, apertureSize=5)
          bin = cv2.dilate(bin, None)
        else:
          retval, bin = cv2.threshold(gray, thrs, 255, cv2.THRESH_BINARY)
        bin, contours, hierarchy = cv2.findContours(bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
          cnt_len = cv2.arcLength(cnt, True)
          cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True)
          if len(cnt) == 4 and cv2.contourArea(cnt) > 1000 and cv2.isContourConvex(cnt):
            cnt = cnt.reshape(-1, 2)
            max_cos = numpy.max([self.angle_cos( cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4] ) for i in xrange(4)])
            if max_cos < 0.1:
              squares.append(cnt)
    return squares
  # Processes an image to detect buoys in it
  def process_image(self, img):

    # Resize any input image to the size our algorithm
    # wants to process
    img = cv2.resize(img, self.image_dimensions)
    #img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # im_out = cv2.GaussianBlur(img, (5, 5), 0)
    #circles = cv2.HoughCircles(im_out, cv2.HOUGH_GRADIENT, dp=1, minDist=im_out.shape[0]/8, param1=50.0, param2=25.0, minRadius=0, maxRadius=0)
    # Potential additional tuning parameters:
    #, param1=50, param2=30, minRadius=0, maxRadius=0)
    module = CVModule(2)
    squares = module.find_squares(img)
    # Draw the HoughCircle we detected to the debug image
    buoy_detection = None
    if squares is not None:
      #for i in squares[0,:]:
      cv2.drawContours(img, squares, -1, (255, 255, 255), 3)
      cv2.imshow('squares', img)
      ch = cv2.waitKey(0)
        # if ch == 27:
        #   break

    # if circles is not None:
    #   circles = numpy.uint16(numpy.around(circles))
    #   for i in circles[0,:]:
    #     cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
    #     cv2.circle(img,(i[0],i[1]),2,(0,0,255),3)
    #     buoy_detection = {"pos":(int(i[0]), int(i[1])), "rad":int(i[2]/2)}
    # if buoy_detection is not None:
    #   self.meta.append({"squares":buoy_detection})
    # else:
    #   self.meta.append({})

    # Show the processed image for debugging
    return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)






