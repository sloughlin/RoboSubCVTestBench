#!/usr/bin/python2.7

import cv2

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

    # Show the processed image for debugging
    return img





