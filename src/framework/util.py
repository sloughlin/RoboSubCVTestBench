import cv2
import json
import numpy

def load_meta(filename):
  with open(filename, 'r') as infile:
    return json.load(infile)

def save_meta(filename, metadata):
  with open(filename, 'w') as outfile:
    json.dump(metadata, outfile)

def percent_difference(a, b):
  a, b = float(a), float(b)
  return (a - b)/((a + b)/2)*100

def distance(a, b):
  return numpy.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def load_video_images(filename):

  images = []

  vidcap = cv2.VideoCapture(filename)
  success, image = vidcap.read()

  while success:
    images.append(image)
    success, image = vidcap.read()

  return images
