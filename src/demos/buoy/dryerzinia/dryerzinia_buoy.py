#!/usr/bin/python2.7

import argparse
import numpy
import cv2

import keras
from keras.models import model_from_json

class Feature():

  def __init__(self, s, p):
    self.size = s
    self.pt = p

  def set_image(self, img):
    self.img = img

  def __repr__(self):
    return str(self.size) + " " + str(self.pt)

class CVModule:

  HOUGH_ON = False
  NN_PREDICTION = True
  COLOR_DETECT = True

  FEATURE_LIMIT = 150

  MIN_FEATURE_SIZE = 12.0

  depth = 20

  SAVE_FEATURES = False
  feature_counter = 0
  feature_filename = 'features/feature_%06u.png'

  d_blue = (150, 55, 55)
  l_blue = (250, 200, 200)

  d_green = (55, 150, 55)
  l_green = (200, 250, 200)

  d_yellow = (55, 150, 150)
  l_yellow = (200, 250, 250)

  d_red = (55, 55, 150)
  l_red = (200, 200, 250)

  BUOY_NN_THRESHOLD = 0.8

  feature_list = []
  input_img_buffer = []
  edge_detect_img_buffer = []

  loaded_model = None

  def __init__(self, args):

    parser = argparse.ArgumentParser()
    parser.add_argument('--neural-net-model')
    parser.add_argument('--neural-net-weights')
    args = parser.parse_known_args(args)[0]

    # Load the neural net
    if self.NN_PREDICTION:
      # load json and create model
      json_file = open(args.neural_net_model, 'r')#'buoy_feature_model.json', 'r')
      loaded_model_json = json_file.read()
      json_file.close()
      self.loaded_model = model_from_json(loaded_model_json)
      # load weights into new model
      self.loaded_model.load_weights(args.neural_net_weights)#"buoy_feature_model.h5")
      print("Loaded model from disk")

      self.loaded_model.compile(loss=keras.losses.categorical_crossentropy,
              optimizer=keras.optimizers.Adadelta(),
              metrics=['accuracy'])

  # Do frame by frame filtering to make sure
  # the features are persistent through depth
  # frames
  def match_features(self):
    # For every feature in new list
    # if any in old list are with in 20 of it
    # and size change less than 10% keep it
    # replace old list with trimmed list
    for j in range(self.depth-2, 0, -1):
      matches = [False]*len(self.feature_list[j])
      for f1 in self.feature_list[j+1]:
        for i in xrange(len(self.feature_list[j])):
          f2 = self.feature_list[j][i]
          if(f2.size < f1.size*1.1 and f2.size > f1.size*0.9):
            dst = numpy.sqrt((f2.pt[0]-f1.pt[0])**2 + (f2.pt[1]-f1.pt[1])**2)
            if(dst < 100):
              matches[i] = True
      fl = []
      for i in xrange(len(self.feature_list[j])):
        if matches[i]:
          fl.append(self.feature_list[j][i])
      self.feature_list[j] = fl

  # Extract a feature from the image
  def get_feature(self, f, img):

    # To make sure we get the whole feature grab a secion +4 pixels or 10% larger
    size = f.size + max(int(f.size*0.15), 6)

    x1 = int(f.pt[0]-size/2)
    x2 = int(x1 + size)
    y1 = int(f.pt[1]-size/2)
    y2 = int(y1+size)

    crop_img = img[y1:y2, x1:x2]

    # Make sure our feature dosn't excede the dimentions of our image
    if y1 >= 360 or y2 >= 360 or x1 >= 480 or x2 >= 480 or y1 < 0 or y2 < 0 or x1 < 0 or x2 < 0:
      return None

    if len(crop_img) == 0:
      return None

    # Standardize blot size to 32x32
    crop_img = cv2.resize(crop_img, (32, 32))

    return crop_img

  # saves a feature to train a neural net with
  def save_feature(self, feat):

    if(self.SAVE_FEATURES):
      cv2.imwrite(self.feature_filename % self.feature_counter, feat)
      self.feature_counter = self.feature_counter + 1

  # Remove duplicates
  def supress(x, fs):
    for f in fs:
      distx = f.pt[0] - x.pt[0]
      disty = f.pt[1] - x.pt[1]
      dist = math.sqrt(distx*distx + disty*disty)
      if (f.size > x.size) and (dist<f.size/2):
        return True

  # Draws the detected features
  def draw_debug_features(self, feature_set, img):

    for feature in feature_set:

      feature_img = feature.img

      # Set default color of blue to draw debug features
      # if we are not sure what color the buoy is
      d_col = self.d_blue
      l_col = self.l_blue

      if self.COLOR_DETECT:

        # Detect color from HSV
        feat_cen = feature_img.copy()[16:24, 8:24] # look at lower center This assumes upright orientation
        feat_cen[:,:,0] = 0 # Zero out blue channel
        feat_cen[:,:,1] = feat_cen[:,:,1]/3 # Cut down on green it transmits well though water
                            # Water absorbs 10x more red light than green
                            # TODO use distance estimate based on size and depth to tune this
        feat_cen_hsv = cv2.cvtColor(feat_cen,cv2.COLOR_BGR2HSV)
        feat_cen_h = feat_cen_hsv[:,:,0]
        h = numpy.mean(feat_cen_h) # Hue value

        # Magic hue numbers for estimating buoy color
        if h < 10:
          d_col = self.d_red
          l_col = self.l_red
        elif h > 26 and h < 33:
          d_col = self.d_yellow
          l_col = self.l_yellow
        elif h > 45 and h < 75:
          d_col = self.d_green
          l_col = self.l_green

      # Draw a debug circle around the feature
      cv2.circle(img, (int(feature.pt[0]), int(feature.pt[1])), int(feature.size/2), d_col, 2)
      cv2.circle(img, (int(feature.pt[0]), int(feature.pt[1])), int(feature.size/2), l_col, 1)

  # Converts black and white image to RGB
  def to_rgb1(self, im):
    # I think this will be slow
    w, h = im.shape
    ret = numpy.empty((w, h, 3), dtype=numpy.uint8)
    ret[:, :, 0] = im
    ret[:, :, 1] = im
    ret[:, :, 2] = im
    return ret

  def remove_similar(self, fl, size, dist):
    fl2 = []
    while len(fl) > 0:
      f1 = fl.pop(0)
      fl2.append(f1)
      for f2 in fl[:]:
        if(f2.size < f1.size*(1.0+size) and f2.size > f1.size*(1.0-size)):
          dst = numpy.sqrt((f2.pt[0]-f1.pt[0])**2 + (f2.pt[1]-f1.pt[1])**2)
          if(dst < dist):
            # make sure we keep the largest feature size
            if(f2.size > f1.size):
              f1.size = f2.size
            fl.remove(f2)
    return fl2

  def output_dimensions(self):
    return (480*2,360)

  # Processes an image to detect buoys in it
  def process_image(self, img):

    # Resize any input image to the size our algorithm
    # wants to process
    img = cv2.resize(img, (480, 360))

    # Do an edge detection to make the image simpler for MSER
    # and HOUGH
    edges = cv2.Canny(img, 100, 200)
    # Bluring helps with feature & circle detection
    im_out = edges
    im_out = cv2.GaussianBlur(im_out, (5, 5), 0)

    # Do HoughCircles opencv detection
    # Note: Works better than MSER when buoy is close
    if self.HOUGH_ON:
      # TODO make this render when we know there is a buoy in the area for more accuracy
      circles = cv2.HoughCircles(im_out, cv2.HOUGH_GRADIENT, 2, 32.0)
      # Potential additional tuning parameters:
      #, param1=50, param2=30, minRadius=0, maxRadius=0)

      # When we save features we can't draw
      # because the features wil be altered if we do
      if not self.SAVE_FEATURES:
        # Draw the HoughCircle we detected to the debug image
        if circles is not None:
          circles = numpy.uint16(numpy.around(circles))
          for i in circles[0,:]:
            cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
            cv2.circle(img,(i[0],i[1]),2,(0,0,255),3)

    # Detects feature that contains buoy well when bouy is distant
    # but also detects everything else bloby
    detector = cv2.MSER_create()
    fs = detector.detect(im_out)
    fs.sort(key = lambda x: -x.size)

    # We are running real time so drop frames with tons of features
    # we depend on buoys not having a lot between them and the background
    # being largley just the deep blue water
    if len(fs) > self.FEATURE_LIMIT:
      fs = []

    # Transform detected features to our custom
    # feature class for convinence
    fl = []
    for f in fs:
      # Filter small features
      if f.size > self.MIN_FEATURE_SIZE:
        fl.append(Feature(f.size, f.pt))

    # Remove duplicate features
    fl2 = self.remove_similar(fl, 0.2, 8)

    # Remove features that fail NN
    for f in fl2[:]:
      feat = self.get_feature(f, img)
      f.set_image(feat)
      self.save_feature(feat)
      if feat is not None:
        gs_feat = cv2.cvtColor(feat, cv2.COLOR_BGR2GRAY)
        feat_x = numpy.empty((1,32,32))
        feat_x[0] = gs_feat
        feat_x = feat_x.reshape(feat_x.shape[0], 32, 32, 1)
        prediction = self.loaded_model.predict(feat_x)
        if prediction[0][1] < self.BUOY_NN_THRESHOLD:
          fl2.remove(f)

    # Only look at features consistent across self.depth frames
    # Feature matching and traceability of specific frames though
    # camera motion would be better.  Also integration with the subs
    # internal referece frame to ignore rotations.
    self.feature_list.append(fl2)
    if len(self.feature_list) > self.depth:
      self.feature_list.pop(0)
      self.match_features()

    # Maintain image buffers so we can only draw confident features
    # after filtering for consistency across self.depth frames
    self.edge_detect_img_buffer.append(im_out)
    if len(self.edge_detect_img_buffer) > self.depth:
      self.edge_detect_img_buffer.pop(0)
    self.input_img_buffer.append(img)
    if len(self.input_img_buffer) > self.depth:
      self.input_img_buffer.pop(0)
      feature_set = self.remove_similar(self.feature_list[0], 0.5, 30)
      self.draw_debug_features(feature_set, self.input_img_buffer[0])
      img, im_out = self.input_img_buffer[0], self.edge_detect_img_buffer[0]

    # Show the processed image for debugging
    return numpy.hstack((img, self.to_rgb1(im_out)))





