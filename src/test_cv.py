#!/usr/bin/python2.7

import argparse
import cv2
import sys
import imp

def main(sys_args):

  parser = argparse.ArgumentParser()
  parser.add_argument('--test-script')
  parser.add_argument('--test-video')
  parser.add_argument('--output-video')
  args = parser.parse_known_args(sys_args)[0]

  test_script = imp.load_source('CVModule', args.test_script)
  cv_test = test_script.CVModule(sys_args)

  debug_video = False
  if args.output_video is not None:
    debug_video = True
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    out = cv2.VideoWriter(args.output_video,fourcc, 30.0, cv_test.output_dimensions())

  vidcap = cv2.VideoCapture(args.test_video)
  success, image = vidcap.read()
  while success:

    debug_image = cv_test.process_image(image)

    # Note: when this code is integrating with the sub we will
    # publish frames to a topic instead of showing debug images
    if debug_video:
      # write debug image to file
      out.write(debug_image)
    else:
      # Show user debug image
      cv2.imshow('debug_image', debug_image)
      cv2.waitKey(0)

    success, image = vidcap.read()


  if debug_video:
    cap.release()
    out.release()

if __name__ == "__main__":
  main(sys.argv[1:])
